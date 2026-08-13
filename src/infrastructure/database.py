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
import queue
from datetime import datetime, timezone
from pathlib import Path
from src.shared.security import get_file_acl
from src.core.domain.services import (
    extract_ai_tags,
    chunk_text,
)
from src.infrastructure.parsers import extract_content, parse_audio_metadata, calculate_sha256, calculate_sha256_cached

"""
SQLite database manager: Connection lifecycle, schema creation, WAL pragmas, snapshot management, and repository operations.
"""

logger = logging.getLogger(__name__)

DB_TIMEOUT = 30.0

class SQLiteConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 8, timeout: float = DB_TIMEOUT):
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
                    if self.db_path and os.path.dirname(self.db_path):
                        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
                    conn = sqlite3.connect(self.db_path, timeout=self.timeout, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    # Enable WAL mode and lightweight memory-mapped I/O per-connection
                    conn.execute("PRAGMA journal_mode = WAL")
                    conn.execute("PRAGMA synchronous = NORMAL")
                    conn.execute("PRAGMA mmap_size = 67108864")
                    conn.execute("PRAGMA cache_size = -4000")
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
    
    # Close ALL thread-local connections
    with _local_connections_lock:
        for c in _local_connections:
            try:
                c.close()
            except Exception:
                pass
        _local_connections.clear()
    
    if hasattr(_local, "connection"):
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
        import logging; logging.warning(f"Swallowed error in database.py: {e}")
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
        import logging; logging.warning(f"Swallowed error in database.py: {e}")
    try:
        if DB_FILE:
            return os.path.dirname(os.path.abspath(DB_FILE))
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in database.py: {e}")
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
                import logging; logging.warning(f"Swallowed error in database.py: {e}")
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
                os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
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
                    chunk_hash TEXT,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_chunks_file_id ON file_chunks(file_id)')

            cursor.execute("PRAGMA table_info(file_chunks)")
            fc_cols = [row[1] for row in cursor.fetchall()]
            if 'chunk_hash' not in fc_cols:
                cursor.execute("ALTER TABLE file_chunks ADD COLUMN chunk_hash TEXT")
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_chunks_hash ON file_chunks(chunk_hash)')

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
                CREATE TABLE IF NOT EXISTS system_audit_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    description TEXT,
                    timestamp REAL,
                    metadata_json TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_ledger_timestamp ON system_audit_ledger(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_ledger_event_type ON system_audit_ledger(event_type)")


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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_logs_trigger_executed ON workflow_logs(trigger_id, executed_at DESC, id DESC)")

            conn.commit()
            cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
    print("Database initialized successfully.")

def run_maintenance():
    """Execute WAL checkpoint and incremental vacuum maintenance with safe connection management."""
    if DB_FILE and os.path.dirname(DB_FILE):
        os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            cursor = conn.cursor()
        cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
        cursor.execute("PRAGMA incremental_vacuum(100)")
        cursor.execute("PRAGMA optimize")
        conn.commit()

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
        from src.infrastructure.repositories.snapshots import list_db_snapshots
        return {
            "file_count": file_count,
            "db_size_bytes": page_count * page_size,
            "freelist_pages": freelist_count,
            "snapshots_count": len(list_db_snapshots())
        }

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


def log_audit_event(event_type: str, description: str, metadata: dict = None):
    """Log an audit event entry into system_audit_ledger."""
    try:
        import json
        init_db()
        metadata_str = json.dumps(metadata) if metadata else "{}"
        with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_audit_ledger (event_type, description, timestamp, metadata_json)
                    VALUES (?, ?, ?, ?)
                """, (event_type, description, time.time(), metadata_str))
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error logging audit event: {e}")


def get_audit_ledger(limit: int = 50) -> list:
    """Retrieve recent system audit ledger entries."""
    try:
        import json
        init_db()
        with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, event_type, description, timestamp, metadata_json FROM system_audit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                try:
                    item["metadata"] = json.loads(item.get("metadata_json") or "{}")
                except Exception:
                    item["metadata"] = {}
                results.append(item)
            return results
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error getting audit ledger: {e}")
        return []