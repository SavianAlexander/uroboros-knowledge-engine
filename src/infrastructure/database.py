"""
SQLite database manager: Connection lifecycle, schema creation, WAL pragmas, snapshot management, and repository operations.
"""

import os
import re
import time
import glob
import shutil
import sqlite3
import hashlib
import threading
from typing import Dict, List, Any, Tuple, Optional, Callable
import mimetypes
import concurrent.futures
import uuid
import json
import contextlib
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

import queue

DB_TIMEOUT = 30.0

class SQLiteConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 15, timeout: float = DB_TIMEOUT):
        self.db_path = db_path
        self.timeout = timeout
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.created = 0

    def get_connection(self):
        try:
            return self.pool.get_nowait()
        except queue.Empty:
            with self.lock:
                if self.created < self.max_connections:
                    self.created += 1
                    conn = sqlite3.connect(self.db_path, timeout=self.timeout, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    # Enable WAL mode per-connection defensively
                    conn.execute("PRAGMA journal_mode = WAL")
                    return conn
            # Block until a connection is available if we are at max
            return self.pool.get()

    def return_connection(self, conn):
        try:
            # We don't want a connection with a broken transaction state to go back to the pool
            # but sqlite rollback handles it. 
            self.pool.put_nowait(conn)
        except queue.Full:
            try:
                conn.close()
            except Exception:
                pass

_db_pools: Dict[str, SQLiteConnectionPool] = {}
_pool_lock = threading.Lock()

def get_pool(db_path: str) -> SQLiteConnectionPool:
    with _pool_lock:
        if db_path not in _db_pools:
            _db_pools[db_path] = SQLiteConnectionPool(db_path)
        return _db_pools[db_path]

def reset_db_connections():
    """Clear the connection pools. Useful during init_db."""
    with _pool_lock:
        for pool in _db_pools.values():
            while not pool.pool.empty():
                try:
                    conn = pool.pool.get_nowait()
                    conn.close()
                except Exception:
                    pass
            pool.created = 0
        _db_pools.clear()
    
    # Close thread-local connection for the CURRENT thread
    if hasattr(_local, "connection") and _local.connection is not None:
        try:
            _local.connection.close()
        except Exception:
            pass
        _local.connection = None
    _local.connection_path = None

    # Close ALL other thread-local connections we've tracked globally
    with _local_connections_lock:
        for conn in _local_connections:
            try:
                conn.close()
            except Exception:
                pass
        _local_connections.clear()


_db_write_lock = threading.Lock()

@contextlib.contextmanager
def get_db_write_connection(db_path: str, timeout: float = DB_TIMEOUT):
    """Acquires a global lock to serialize SQLite writes at the Python level, preventing database is locked errors."""
    pool = get_pool(db_path)
    with _db_write_lock:
        conn = pool.get_connection()
        try:
            yield conn
        finally:
            pool.return_connection(conn)

@contextlib.contextmanager
def get_db_connection(db_path: str, timeout: float = DB_TIMEOUT):
    """Centralized database connection manager that uses a thread-safe connection pool."""
    pool = get_pool(db_path)
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.return_connection(conn)

from datetime import datetime, timezone
from pathlib import Path
from src.shared.security import get_file_acl
from src.core.domain.services import (
    extract_ai_tags,
    chunk_text,
)
from src.infrastructure.parsers import extract_content, parse_audio_metadata, calculate_sha256, calculate_sha256_cached

DB_FILE = os.environ.get("DB_FILE", "knowledge.db")
_local = threading.local()
_db_version = 0



def get_active_dir() -> str:
    """Return active sandbox or working directory."""
    try:
        import sys
        if "main" in sys.modules:
            m_dir = getattr(sys.modules["main"], "ACTIVE_DIR", None)
            if m_dir:
                return m_dir
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in database.py: {e}")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM files LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                return os.path.dirname(os.path.abspath(row[0]))
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in database.py: {e}")
    try:
        if DB_FILE:
            return os.path.dirname(os.path.abspath(DB_FILE))
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in database.py: {e}")
    return os.getcwd()

_local_connections = []
_local_connections_lock = threading.Lock()

def get_db():
    """Get or establish thread-local SQLite database connection."""
    conn = getattr(_local, "connection", None)
    cached_path = getattr(_local, "connection_path", None)
    current_path = os.path.abspath(DB_FILE)
    if conn is not None:
        if cached_path != current_path:
            try:
                conn.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in database.py: {e}")
            conn = None
            _local.connection = None
            _local.connection_path = None
        else:
            try:
                conn.execute("SELECT 1")
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
                conn = None
                _local.connection = None
                _local.connection_path = None

    if conn is None:
        attempts = 0
        while attempts < 5:
            try:
                conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=DB_TIMEOUT)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA temp_store = MEMORY")
                conn.execute("PRAGMA cache_size = -64000")
                conn.execute("PRAGMA mmap_size = 268435456")
                conn.execute("PRAGMA foreign_keys = ON")
                _local.connection = conn
                _local.connection_path = current_path
                with _local_connections_lock:
                    _local_connections.append(conn)
                break
            except sqlite3.OperationalError as e:
                attempts += 1
                if attempts >= 5:
                    raise e
                time.sleep(0.05 * (2 ** attempts))
    return conn

def backup_db_online(backup_target_path: str) -> bool:
    """Perform a non-blocking online SQLite database backup using connection backup API."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(backup_target_path)), exist_ok=True)
        with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as src_conn:
            with get_db_connection(backup_target_path, timeout=DB_TIMEOUT) as dst_conn:
                src_conn.backup(dst_conn, pages=100, sleep=0.01)
        return True
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
        return False

def init_db():
    """Initialize database tables, pragmas, indices, and schema migrations."""
    reset_db_connections()
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA cache_size = -64000;")
            cursor.execute("PRAGMA mmap_size = 268435456;")
            cursor.execute("PRAGMA auto_vacuum = INCREMENTAL;")
            cursor.execute("PRAGMA threads = 4;")
        
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding_json TEXT,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_chunks_file_id ON file_chunks(file_id)')

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tf_idf_index (
                    term TEXT NOT NULL,
                    file_id INTEGER NOT NULL,
                    term_freq INTEGER NOT NULL,
                    PRIMARY KEY (term, file_id),
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tf_idf_term ON tf_idf_index(term)')
        
            # Core metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 0,
                    filepath TEXT UNIQUE,
                    filename TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    sha256 TEXT,
                    modified_at REAL,
                    content TEXT,
                    tags TEXT,
                    created_at REAL DEFAULT 0.0,
                    notes TEXT,
                    insights TEXT,
                    acl_permissions TEXT
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)')

            cursor.execute("PRAGMA table_info(files)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute("ALTER TABLE files ADD COLUMN user_id INTEGER DEFAULT 0")
            if 'notes' not in columns:
                cursor.execute("ALTER TABLE files ADD COLUMN notes TEXT")
            if 'insights' not in columns:
                cursor.execute("ALTER TABLE files ADD COLUMN insights TEXT")
            if 'acl_permissions' not in columns:
                cursor.execute("ALTER TABLE files ADD COLUMN acl_permissions TEXT")

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id)')

            cursor.execute("PRAGMA table_info(fts_files)")
            cursor.execute("DROP TABLE IF EXISTS fts_files")
            cursor.execute("""
                CREATE VIRTUAL TABLE fts_files USING fts5(
                    filepath UNINDEXED,
                    filename,
                    content,
                    notes,
                    tokenize="porter unicode61"
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    file_id INTEGER,
                    tag TEXT,
                    PRIMARY KEY(file_id, tag),
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auto_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT UNIQUE,
                    tag TEXT,
                    priority INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT,
                    content TEXT,
                    sha256 TEXT,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_revisions_filepath ON file_revisions(filepath)")

            cursor.execute("PRAGMA table_info(auto_rules)")
            rule_cols = [row[1] for row in cursor.fetchall()]
            if 'priority' not in rule_cols:
                cursor.execute("ALTER TABLE auto_rules ADD COLUMN priority INTEGER DEFAULT 0")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_peers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE,
                    name TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocr_coords (
                    file_id INTEGER,
                    word TEXT,
                    x REAL,
                    y REAL,
                    w REAL,
                    h REAL,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag_metadata (
                    tag TEXT PRIMARY KEY,
                    color TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_macros (
                    name TEXT PRIMARY KEY,
                    expansion TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag_aliases (
                    alias TEXT PRIMARY KEY,
                    target TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS synonyms (
                    word TEXT PRIMARY KEY,
                    substitutes TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_string TEXT,
                    search_mode TEXT,
                    executed_at REAL,
                    result_count INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    query_string TEXT,
                    search_mode TEXT,
                    created_at REAL
                )
            """)


            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_file_chunks USING fts5(
                    chunk_id UNINDEXED,
                    file_id UNINDEXED,
                    content,
                    tokenize="porter unicode61"
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    query_key TEXT PRIMARY KEY,
                    response_json TEXT,
                    cached_at REAL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER DEFAULT 0,
                    title TEXT,
                    created_at REAL,
                    updated_at REAL,
                    model_path TEXT,
                    temperature REAL,
                    context_window INTEGER,
                    metadata_json TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    citations_json TEXT,
                    web_sources_json TEXT,
                    tokens_used INTEGER,
                    created_at TEXT,
                    metadata_json TEXT,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    condition_pattern TEXT,
                    webhook_url TEXT NOT NULL,
                    secret_header TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_id INTEGER,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_status_code INTEGER,
                    response_body TEXT,
                    execution_time_ms REAL DEFAULT 0.0,
                    retry_count INTEGER DEFAULT 0,
                    executed_at TEXT NOT NULL,
                    FOREIGN KEY(trigger_id) REFERENCES workflow_triggers(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_modified_desc ON files(modified_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_filepath ON files(filepath)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_file_id ON tags(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_composite ON tags(tag, file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_exec ON search_history(executed_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ocr_coords_file_id ON ocr_coords(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_chunks_file_id ON file_chunks(file_id)")
            
            cursor.execute("PRAGMA table_info(chat_sessions)")
            columns_chat = [row[1] for row in cursor.fetchall()]
            if 'user_id' not in columns_chat:
                cursor.execute("ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER DEFAULT 0")

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC)')
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at ASC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_triggers_event_type ON workflow_triggers(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_triggers_active ON workflow_triggers(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_logs_trigger_id ON workflow_logs(trigger_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_logs_event_type ON workflow_logs(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_logs_status ON workflow_logs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_logs_executed_at ON workflow_logs(executed_at DESC)")

            conn.commit()
            cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
    print("Database initialized successfully.")

def save_file_revision(filepath: str, content: str):
    """Save a snapshot of file content into file_revisions with safe connection management."""
    norm_path = os.path.abspath(filepath)
    content_hash = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO file_revisions (filepath, content, sha256)
            VALUES (?, ?, ?)
        """, (norm_path, content, content_hash))
        
        cursor.execute("""
            DELETE FROM file_revisions
            WHERE filepath = ? AND id NOT IN (
                SELECT id FROM file_revisions WHERE filepath = ? ORDER BY id DESC LIMIT 5
            )
        """, (norm_path, norm_path))
        conn.commit()

def get_file_revisions(filepath: str) -> List[Dict[str, Any]]:
    """Retrieve last 5 revision snapshots for a file with safe connection management."""
    norm_path = os.path.abspath(filepath)
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filepath, sha256, saved_at, LENGTH(content) as content_length
            FROM file_revisions
            WHERE filepath = ?
            ORDER BY id DESC LIMIT 5
        """, (norm_path,))
        return [dict(row) for row in cursor.fetchall()]

def revert_file_revision(filepath: str, revision_id: int) -> bool:
    """Revert a file to a specific revision ID with correct column name (modified_at)."""
    norm_path = os.path.abspath(filepath)
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM file_revisions WHERE id = ? AND filepath = ?", (revision_id, norm_path))
        row = cursor.fetchone()
        if not row:
            return False
        
        rev_content = row["content"]
        with open(norm_path, "w", encoding="utf-8") as f:
            f.write(rev_content)
        
        sha256 = hashlib.sha256(rev_content.encode("utf-8")).hexdigest()
        cursor.execute("UPDATE files SET content = ?, sha256 = ?, modified_at = ? WHERE filepath = ?", (rev_content, sha256, os.path.getmtime(norm_path), norm_path))
        cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (norm_path,))
        cursor.execute("INSERT INTO fts_files (filepath, filename, content) VALUES (?, ?, ?)", (norm_path, os.path.basename(norm_path), rev_content))
        conn.commit()
        return True

def run_maintenance():
    """Execute WAL checkpoint and incremental vacuum maintenance with safe connection management."""
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            cursor = conn.cursor()
        cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
        cursor.execute("PRAGMA incremental_vacuum(100)")
        cursor.execute("PRAGMA optimize")
        conn.commit()

def create_db_snapshot() -> int:
    """Create atomic database snapshot using native SQLite backup API with closed connection."""
    try:
        with get_db_connection(DB_FILE, timeout=10.0) as conn:
            with conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in database.py: {e}")
    timestamp = int(time.time())
    dest = f"{DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(dest):
        timestamp = int(time.time() * 1000)
        dest = f"{DB_FILE}.snapshot-{timestamp}"
    c_src = None
    c_dst = None
    try:
        c_src = sqlite3.connect(DB_FILE)
        c_dst = sqlite3.connect(dest)
        c_src.backup(c_dst)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
        try:
            if c_dst: c_dst.close()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")
        try:
            if c_src: c_src.close()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")
        c_dst = None
        c_src = None
        shutil.copy2(DB_FILE, dest)
    finally:
        if c_dst: c_dst.close()
        if c_src: c_src.close()
    return timestamp

def restore_db_snapshot(timestamp: int) -> bool:
    """Restore database from snapshot timestamp."""
    src = f"{DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(src):
        reset_db_connections()
        c_src = None
        c_dst = None
        try:
            c_src = sqlite3.connect(src)
            c_dst = sqlite3.connect(DB_FILE)
            c_src.backup(c_dst)
            return True
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
            try:
                if c_dst: c_dst.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in database.py: {e}")
            try:
                if c_src: c_src.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in database.py: {e}")
            c_dst = None
            c_src = None
            shutil.copy2(src, DB_FILE)
            return True
        finally:
            if c_dst: c_dst.close()
            if c_src: c_src.close()
    return False

def delete_db_snapshot(timestamp: int) -> bool:
    """Delete a database snapshot by timestamp."""
    src = f"{DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(src):
        try:
            os.remove(src)
            return True
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")
    return False

def list_db_snapshots() -> List[Dict[str, Any]]:
    """List available database snapshots."""
    snapshots = []
    for f in glob.glob(f"{DB_FILE}.snapshot-*"):
        try:
            ts = f.split("-")[-1]
            size = os.path.getsize(f)
            snapshots.append({"timestamp": ts, "filename": f, "size": size})
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")
    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    return snapshots

def db_status() -> Dict[str, Any]:
    """Retrieve database metrics, page count, freelist, and table stats."""
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        cursor.execute("PRAGMA freelist_count")
        freelist_count = cursor.fetchone()[0]
        return {
            "file_count": file_count,
            "db_size_bytes": page_count * page_size,
            "freelist_pages": freelist_count,
            "snapshots_count": len(list_db_snapshots())
        }

def search_files(query: str) -> List[Dict[str, Any]]:
    """Execute FTS5 keyword search across files with Unicode NFC normalization."""
    if not query or not str(query).strip():
        return []
    import unicodedata
    norm_query = unicodedata.normalize("NFC", str(query).strip())
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT files.id, files.filepath, files.filename, files.file_size, files.mime_type, files.modified_at, files.content
                FROM fts_files JOIN files ON fts_files.filepath = files.filepath
                WHERE fts_files MATCH ? LIMIT 100
            """, (norm_query,))
            rows = cursor.fetchall()
            if rows:
                return [dict(r) for r in rows]
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")

        if "NEAR(" in norm_query:
            import re
            m = re.search(r'NEAR\((.*?),\s*(\d+)\)', norm_query, re.IGNORECASE)
            if m:
                words = m.group(1).split()
                dist = m.group(2)
                quoted_words = " ".join([f'"{w}"' for w in words])
                fts_near = f'NEAR({quoted_words}, {dist})'
                try:
                    cursor.execute("""
                        SELECT files.id, files.filepath, files.filename, files.file_size, files.mime_type, files.modified_at, files.content
                        FROM fts_files JOIN files ON fts_files.filepath = files.filepath
                        WHERE fts_files MATCH ? LIMIT 100
                    """, (fts_near,))
                    rows = cursor.fetchall()
                    if rows:
                        return [dict(r) for r in rows]
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in database.py: {e}")

        import re
        words = re.findall(r'\w+', norm_query)
        words = [w for w in words if w.lower() not in ('near', 'and', 'or', 'not') and not w.isdigit()]
        if words:
            where_clause = " AND ".join(["(content LIKE ? OR filename LIKE ?)" for _ in words])
            params = []
            for w in words:
                params.extend([f"%{w}%", f"%{w}%"])
            try:
                cursor.execute(f"SELECT id, filepath, filename, file_size, mime_type, modified_at, content FROM files WHERE {where_clause} LIMIT 100", params)
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in database.py: {e}")
        return []

def index_directory(dir_path: str, progress_callback: Optional[Callable[[str, int, int], None]] = None, on_complete_callback: Optional[Callable[[], None]] = None, job_id: Optional[str] = None):
    """
    Crawls dir_path, parses supported files, updates files/FTS/Tags,
    and manages chunks + vector embeddings.
    """
    if not os.path.exists(dir_path):
        if on_complete_callback:
            on_complete_callback()
        return

    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0

    print(f"Indexing directory: {dir_path} for user: {user_id}")
    """
    Index directory files with decoupled post-processing:
    Auto-tagging and search index rules are evaluated for ALL matching files (including unmodified ones).
    """
    global _db_version
    _db_version += 1

    try:
        from src.core.state import GLOBAL_QUERY_CACHE
        if GLOBAL_QUERY_CACHE is not None:
            GLOBAL_QUERY_CACHE.invalidate()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in database.py: {e}")

    path = Path(dir_path).resolve()
    if not path.is_dir():
        print(f"Error: {dir_path} is not a directory.")
        return

    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, filepath, modified_at, file_size, sha256, content FROM files")
            existing_files = {
                row['filepath']: {
                    'id': row['id'],
                    'modified_at': row['modified_at'],
                    'file_size': row['file_size'],
                    'sha256': row['sha256'],
                    'content': row['content']
                }
                for row in cursor.fetchall()
            }
        except sqlite3.OperationalError:
            print(f"Skipping index_directory due to uninitialized database table.")
            return

    text_extensions = {
        '.md', '.py', '.txt', '.json', '.yaml', '.yml', '.ini', '.csv', '.xml',
        '.html', '.css', '.js', '.pdf', '.docx', '.rtf', '.xlsx',
        '.png', '.jpg', '.jpeg', '.bmp'
    }
    ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}

    all_files = []
    for p in path.rglob('*'):
        if p.is_file() and p.name != DB_FILE and not p.name.startswith('.') and p.name not in ['desktop.ini', 'Thumbs.db']:
            if not any(part in ignored_dirs for part in p.parts):
                all_files.append(p)

    total_files = len(all_files)
    if total_files == 0:
        print("Indexing completed. Indexed: 0, Updated: 0")
        if on_complete_callback:
            try:
                on_complete_callback()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in database.py: {e}")
        return

    if total_files > 100 and len(all_files) > 50:
        try:
            create_db_snapshot()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")

    modified_tasks = []
    unmodified_tasks = []
    print(f"[DEBUG_INDEXER] Indexing directory '{dir_path}' | Total files: {total_files}")

    for p in all_files:
        filepath = str(p)
        filename = p.name
        suffix = p.suffix.lower()
        try:
            stat = p.stat()
            file_size = stat.st_size
            modified_at = stat.st_mtime
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
            continue

        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'
        cached = existing_files.get(filepath)

        task = {
            'filepath': filepath,
            'filename': filename,
            'suffix': suffix,
            'file_size': file_size,
            'modified_at': modified_at,
            'mime_type': mime_type,
            'is_modified': False,
            'id': cached['id'] if cached else None,
            'content': cached['content'] if cached else "",
            'coords': []
        }

        curr_sha = calculate_sha256(filepath)
        if cached and cached['modified_at'] == modified_at and cached['file_size'] == file_size and cached.get('sha256') == curr_sha:
            unmodified_tasks.append(task)
        else:
            task['is_modified'] = True
            modified_tasks.append(task)

    completed_count = 0
    progress_lock = threading.Lock()

    def update_progress(fn):
        nonlocal completed_count
        if progress_callback:
            with progress_lock:
                completed_count += 1
                progress_callback(fn, completed_count, total_files)

    def parse_single_file(task):
        fp = task['filepath']
        suf = task['suffix']
        mime = task['mime_type']
        fsize = task.get('file_size', 0)
        mt = task.get('modified_at', 0)

        if fsize > 100 * 1024 * 1024:
            task['sha256'] = calculate_sha256_cached(fp, mt)
            task['content'] = f"[File size ({fsize / (1024*1024):.1f}MB) exceeds 100MB safety limit.]"
            task['coords'] = []
            return task

        sha256 = calculate_sha256_cached(fp, mt)
        cnt = ""
        coords = []
        if mime.startswith('text/') or suf in text_extensions:
            cnt, coords = extract_content(fp, suf)
        elif suf in {'.wav', '.mp3'}:
            meta = parse_audio_metadata(fp)
            cnt = f"[Audio Metadata] samplerate:{meta.get('samplerate', 0)} channels:{meta.get('channels', 0)}"

        task['sha256'] = sha256
        task['content'] = cnt
        task['coords'] = coords
        task['acl_permissions'] = get_file_acl(fp)
        return task

    batch_size = 200
    if modified_tasks:
        for i in range(0, len(modified_tasks), batch_size):
            batch = modified_tasks[i:i + batch_size]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(parse_single_file, t): t for t in batch}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res_task = future.result()
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception as e:
                        import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
                        t = futures[future]
                        t['content'] = f"[ThreadPool Error: {str(e)}]"
                        t['acl_permissions'] = get_file_acl(t['filepath'])
                        res_task = t
                    update_progress(res_task['filename'])
            time.sleep(0.005)

    for task in unmodified_tasks:
        task['acl_permissions'] = get_file_acl(task['filepath'])
        update_progress(task['filename'])

    # DECOUPLED POST-PROCESSING: Extract AI tags for ALL tasks (both modified & unmodified)
    rule_matches = []
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pattern, tag FROM auto_rules")
            rule_matches = [(r[0], r[1]) for r in cursor.fetchall()]
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
        rule_matches = []

    all_tasks = modified_tasks + unmodified_tasks
    for task in all_tasks:
        task['matched_tags'] = extract_ai_tags(task['content'], task['filename'], rule_matches=rule_matches)

    indexed_count = 0
    updated_count = 0

    with get_db() as conn:
        with conn:
            cursor = conn.cursor()
            for task in modified_tasks:
                filepath = task['filepath']
                filename = task['filename']
                file_size = task['file_size']
                modified_at = task['modified_at']
                content = task['content']
                matched_tags = task['matched_tags']
                acl_permissions = task.get('acl_permissions') or get_file_acl(filepath)
                sha256 = task.get('sha256')
                mime_type = task['mime_type']
                coords = task['coords']
                file_id = task['id']

                if file_id is not None:
                    cursor.execute("""
                        UPDATE files
                        SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?, acl_permissions = ?, insights = NULL
                        WHERE filepath = ?
                    """, (filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, filepath))

                    cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
                    cursor.execute("""
                        INSERT INTO fts_files (filepath, filename, content, notes)
                        VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))
                    """, (filepath, filename, content, filepath))

                    cursor.execute("DELETE FROM ocr_coords WHERE file_id = ?", (file_id,))
                    if coords:
                        cursor.executemany("""
                            INSERT INTO ocr_coords (file_id, word, x, y, w, h)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [(file_id, c['word'], c['x'], c['y'], c['w'], c['h']) for c in coords])

                    cursor.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM fts_file_chunks WHERE file_id = ?", (file_id,))
                    updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO files (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                    """, (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions))
                    file_id = cursor.lastrowid
                    task['id'] = file_id

                    cursor.execute("""
                        INSERT INTO fts_files (filepath, filename, content, notes)
                        VALUES (?, ?, ?, NULL)
                    """, (filepath, filename, content))

                    if coords:
                        cursor.executemany("""
                            INSERT INTO ocr_coords (file_id, word, x, y, w, h)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [(file_id, c['word'], c['x'], c['y'], c['w'], c['h']) for c in coords])
                    indexed_count += 1

            for task in all_tasks:
                file_id = task['id']
                task_content = task.get('content') or ""
                matched_tags = task.get('matched_tags', [])
                if file_id is not None:
                    if matched_tags:
                        cursor.executemany("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", [(file_id, tag) for tag in matched_tags])

                    # Generate Dense Embeddings and Chunks
                    from src.core.embeddings import generate_embedding
                    from src.core.domain.services import chunk_text
                    
                    chunks = chunk_text(task_content, chunk_size=1024)
                    for chunk_idx, chunk in enumerate(chunks):
                        emb = generate_embedding(chunk)
                        emb_json = json.dumps(emb) if emb else None
                        cursor.execute('''
                            INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json)
                            VALUES (?, ?, ?, ?)
                        ''', (file_id, chunk_idx, chunk, emb_json))
                        
                        chunk_id = cursor.lastrowid
                        try:
                            cursor.execute(
                                "INSERT INTO fts_file_chunks (chunk_id, file_id, content) VALUES (?, ?, ?)",
                                (chunk_id, file_id, chunk)
                            )
                        except (KeyboardInterrupt, MemoryError, SystemExit):
                            raise
                        except Exception as e:
                            import logging; logging.error(f"Swallowed error in database.py: {e}")

            # Decoupled tag sync for unmodified tasks
            for task in unmodified_tasks:
                file_id = task['id']
                matched_tags = task['matched_tags']
                if file_id is not None and matched_tags:
                    cursor.executemany("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", [(file_id, tag) for tag in matched_tags])

            cursor.execute("DELETE FROM fts_files WHERE filepath NOT IN (SELECT filepath FROM files)")

    if on_complete_callback:
        try:
            on_complete_callback()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in database.py: {e}")

    print(f"Indexing completed. Indexed: {indexed_count}, Updated: {updated_count}")

def migrate_folder_path(old_dir: str, new_dir: str):
    """Migrate indexed file records when working directory moves."""
    old_prefix = os.path.abspath(old_dir)
    new_prefix = os.path.abspath(new_dir)
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filepath FROM files WHERE filepath LIKE ?", (f"{old_prefix}%",))
        rows = cursor.fetchall()
        for fid, fpath in rows:
            rel = os.path.relpath(fpath, old_prefix)
            updated_path = os.path.join(new_prefix, rel)
            cursor.execute("UPDATE files SET filepath = ? WHERE id = ?", (updated_path, fid))
            cursor.execute("UPDATE fts_files SET filepath = ? WHERE filepath = ?", (updated_path, fpath))
        conn.commit()

class MiniVectorEngine:
    @staticmethod
    def search_semantic(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Native Vector Search using file_chunks and cosine similarity.
        Zero dependency fallback to Ollama embeddings.
        """
        if not query or not query.strip():
            return []
            
        from src.core.embeddings import generate_embedding, cosine_similarity
        query_emb = generate_embedding(query.strip())
        if not query_emb:
            return []
            
        try:
            conn = get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch all chunks that have embeddings
            cursor.execute('''
                SELECT c.id, c.file_id, c.chunk_index, c.text_content as content, c.embedding_json, 
                       f.filepath, f.filename, f.modified_at
                FROM file_chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.embedding_json IS NOT NULL
            ''')
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                try:
                    chunk_emb = json.loads(r['embedding_json'])
                    score = cosine_similarity(query_emb, chunk_emb)
                    if score > 0.3: # Threshold
                        
                        # Find matching tags
                        tags = []
                        try:
                            cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (r['file_id'],))
                            for tr in cursor.fetchall():
                                tags.append(tr['tag'])
                        except (KeyboardInterrupt, MemoryError, SystemExit):
                            raise
                        except Exception as e:
                            import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
                            
                        # Build snippet
                        content = r['content'] or ""
                        snippet_text = content[:150] + "..."
                        
                        results.append({
                            "id": r['file_id'],
                            "chunk_id": r['id'],
                            "filepath": r['filepath'],
                            "filename": r['filename'],
                            "content": content,
                            "snippet": snippet_text,
                            "modified_at": r['modified_at'],
                            "tags": tags,
                            "score": round(score, 4),
                            "rrf_score": round(score, 6),
                            "vector_score": round(score, 6),
                            "bm25_score": round(score, 6)
                        })
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception:
                    import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
                    continue
                    
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Semantic search error: {e}")
            return []

def extract_rag_context(query: str, max_chunks: int = 5):
    """RAG context extractor delegating to domain RAG engine."""
    from src.domain.rag_engine import extract_advanced_rag_context
    return extract_advanced_rag_context(query, max_chunks=max_chunks, jaccard_threshold=0.70)


# ---------------------------------------------------------------------------
# Chat Sessions & Messages CRUD Helpers (Milestone 1)
# ---------------------------------------------------------------------------

def create_chat_session(
    title: Optional[str] = None,
    model_path: Optional[str] = None,
    temperature: float = 0.7,
    context_window: int = 4096,
    metadata_json: Optional[Any] = None
) -> Dict[str, Any]:
    """Create a new chat session in SQLite database."""
    session_id = uuid.uuid4().hex
    now_iso = datetime.now(timezone.utc).isoformat()
    session_title = title if title is not None else "New Chat"
    meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json
    
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at, model_path, temperature, context_window, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, session_title, time.time(), time.time(), model_path, temperature, context_window, meta_str))
        conn.commit()

    return {
        "id": session_id,
        "user_id": user_id,
        "title": session_title,
        "created_at": now_iso,
        "updated_at": now_iso,
        "model_path": model_path,
        "temperature": temperature,
        "context_window": context_window,
        "metadata_json": metadata_json
    }

def list_chat_sessions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """List most recent chat sessions."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at, model_path, temperature, context_window, metadata_json
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        rows = cursor.fetchall()
        
    sessions = []
    for r in rows:
        d = dict(r)
        d["metadata_json"] = json.loads(d["metadata_json"]) if d["metadata_json"] else None
        sessions.append(d)
    return sessions

def get_chat_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get full chat session including ordered messages."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None
        session_dict = dict(row)
        session_dict["messages"] = get_chat_messages(session_id)
        return session_dict

def update_chat_session(
    session_id: str,
    title: Optional[str] = None,
    model_path: Optional[str] = None,
    temperature: Optional[float] = None,
    context_window: Optional[int] = None,
    metadata_json: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """Update metadata and parameters for a chat session."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        if not cursor.fetchone():
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        updates = ["updated_at = ?"]
        params: List[Any] = [now_iso]

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if model_path is not None:
            updates.append("model_path = ?")
            params.append(model_path)
        if temperature is not None:
            updates.append("temperature = ?")
            params.append(temperature)
        if context_window is not None:
            updates.append("context_window = ?")
            params.append(context_window)
        if metadata_json is not None:
            meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json
            updates.append("metadata_json = ?")
            params.append(meta_str)

        params.extend([session_id, user_id])
        sql = f"UPDATE chat_sessions SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        cursor.execute(sql, params)
        conn.commit()

    return get_chat_session(session_id)

def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session and cascade delete all associated messages."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def add_chat_message(
    session_id: str,
    role: str,
    content: str,
    citations_json: Optional[Any] = None,
    web_sources_json: Optional[Any] = None,
    tokens_used: int = 0,
    metadata_json: Optional[Any] = None
) -> Dict[str, Any]:
    """Add a message turn to a chat session."""
    msg_id = uuid.uuid4().hex
    now_iso = datetime.now(timezone.utc).isoformat()
    cit_str = json.dumps(citations_json) if isinstance(citations_json, (dict, list)) else citations_json
    web_str = json.dumps(web_sources_json) if isinstance(web_sources_json, (dict, list)) else web_sources_json
    meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, content, cit_str, web_str, tokens_used or 0, now_iso, meta_str))
        cursor.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now_iso, session_id))
        conn.commit()

    return {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "citations_json": cit_str,
        "web_sources_json": web_str,
        "tokens_used": tokens_used or 0,
        "created_at": now_iso,
        "metadata_json": meta_str
    }

def get_chat_messages(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all messages for a session ordered by created_at ASC."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def create_workflow_trigger(
    name: str,
    event_type: str,
    webhook_url: str,
    condition_pattern: Optional[str] = "",
    secret_header: Optional[str] = "",
    is_active: bool = True
) -> Dict[str, Any]:
    """Create a new workflow trigger rule."""
    now = datetime.now(timezone.utc).isoformat()
    active_int = 1 if is_active else 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO workflow_triggers (name, event_type, condition_pattern, webhook_url, secret_header, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, event_type, condition_pattern or "", webhook_url, secret_header or "", active_int, now, now)
        )
        conn.commit()
        trigger_id = cursor.lastrowid
        return get_workflow_trigger(trigger_id)


def list_workflow_triggers(
    event_type: Optional[str] = None,
    active_only: bool = False
) -> List[Dict[str, Any]]:
    """List registered workflow trigger rules."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM workflow_triggers WHERE 1=1"
        params = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_workflow_trigger(trigger_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single workflow trigger by ID."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflow_triggers WHERE id = ?", (trigger_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_workflow_trigger(trigger_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update fields of an existing workflow trigger rule."""
    allowed_fields = {"name", "event_type", "condition_pattern", "webhook_url", "secret_header", "is_active"}
    updates = []
    params = []
    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            if key == "is_active":
                value = 1 if value else 0
            updates.append(f"{key} = ?")
            params.append(value)
    if not updates:
        return get_workflow_trigger(trigger_id)
    
    now = datetime.now(timezone.utc).isoformat()
    updates.append("updated_at = ?")
    params.append(now)
    params.append(trigger_id)
    
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE workflow_triggers SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
    return get_workflow_trigger(trigger_id)


def delete_workflow_trigger(trigger_id: int) -> bool:
    """Delete a workflow trigger rule by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workflow_triggers WHERE id = ?", (trigger_id,))
        conn.commit()
        return cursor.rowcount > 0


def log_workflow_execution(
    trigger_id: Optional[int],
    event_type: str,
    payload_json: str,
    status: str,
    response_status_code: Optional[int] = None,
    response_body: str = "",
    execution_time_ms: float = 0.0,
    retry_count: int = 0
) -> int:
    """Log an evaluation or HTTP POST delivery attempt to workflow_logs."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        real_trigger_id = trigger_id
        if real_trigger_id is not None:
            cursor.execute("SELECT 1 FROM workflow_triggers WHERE id = ?", (real_trigger_id,))
            if not cursor.fetchone():
                real_trigger_id = None
        cursor.execute(
            """
            INSERT INTO workflow_logs (
                trigger_id, event_type, payload_json, status,
                response_status_code, response_body, execution_time_ms,
                retry_count, executed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                real_trigger_id, event_type, payload_json, status,
                response_status_code, response_body[:2000] if response_body else "", execution_time_ms,
                retry_count, now
            )
        )
        conn.commit()
        return cursor.lastrowid


def list_workflow_logs(
    trigger_id: Optional[int] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """List recent workflow execution logs."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if trigger_id is not None:
            cursor.execute(
                "SELECT * FROM workflow_logs WHERE trigger_id = ? ORDER BY executed_at DESC, id DESC LIMIT ?",
                (trigger_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM workflow_logs ORDER BY executed_at DESC, id DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


