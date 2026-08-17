import sys
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
                    conn.execute("PRAGMA busy_timeout = 30000")
                    conn.execute("PRAGMA synchronous = NORMAL")
                    conn.execute("PRAGMA temp_store = MEMORY")
                    conn.execute("PRAGMA cache_size = -262144")
                    conn.execute("PRAGMA mmap_size = 4294967296")
                    conn.execute("PRAGMA threads = 4")
                    conn.execute("PRAGMA wal_autocheckpoint = 2000")
                    conn.execute("PRAGMA journal_size_limit = 67108864")
                    return conn

            # Block until a connection is available if we are at max
            return self.pool.get()

    def return_connection(self, conn):
        try:
            if conn and getattr(conn, "in_transaction", False):
                try:
                    conn.rollback()
                except Exception:
                    pass
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
    """Clear the connection pools and close all thread-local connections. Useful during init_db and teardown."""
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
        for entry in _local_connections.values():
            try:
                c = entry.get("conn") if isinstance(entry, dict) else entry
                if c:
                    c.close()
            except Exception:
                pass
        _local_connections.clear()
    
    if hasattr(_local, "connection"):
        _local.connection = None
    _local.connection_path = None
    global _initialized_dbs
    _initialized_dbs.clear()


_db_write_lock = threading.Lock()

def with_sqlite_retry(fn: Callable, max_retries: int = 5, initial_delay: float = 0.05, backoff_factor: float = 2.0) -> Any:
    """Execute callable with exponential backoff on transient SQLite write locks / busy states."""
    import random
    last_err = None
    for attempt in range(max_retries):
        try:
            return fn()
        except sqlite3.OperationalError as e:
            last_err = e
            err_str = str(e).lower()
            if ("locked" in err_str or "busy" in err_str) and attempt < max_retries - 1:
                sleep_time = (initial_delay * (backoff_factor ** attempt)) + random.uniform(0.01, 0.05)
                time.sleep(sleep_time)
                continue
            raise
    if last_err:
        raise last_err

@contextlib.contextmanager
def get_db_write_connection(db_path: str, timeout: float = DB_TIMEOUT):
    """Acquires a global lock to serialize SQLite writes at Python level with exponential retry backoff."""
    pool = get_pool(db_path)
    with _db_write_lock:
        conn = pool.get_connection()
        try:
            yield conn
            if getattr(conn, "in_transaction", False):
                with_sqlite_retry(lambda: conn.commit())
        except Exception:
            if getattr(conn, "in_transaction", False):
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            pool.return_connection(conn)

@contextlib.contextmanager
def get_db_connection(db_path: str, timeout: float = DB_TIMEOUT):
    """Centralized database connection manager that uses a thread-safe connection pool with commit retry."""
    pool = get_pool(db_path)
    conn = pool.get_connection()
    try:
        yield conn
        if getattr(conn, "in_transaction", False):
            with_sqlite_retry(lambda: conn.commit())
    except Exception:
        if getattr(conn, "in_transaction", False):
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        pool.return_connection(conn)

DB_FILE = os.environ.get("DB_FILE", "knowledge.db")

_local = threading.local()

_db_version = 0

def get_active_dir() -> str:
    """Return active sandbox or working directory."""
    try:
        if "main" in sys.modules:
            m_dir = getattr(sys.modules["main"], "ACTIVE_DIR", None)
            if m_dir:
                return m_dir
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning(f"Swallowed error in database.py: {e}")
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

_local_connections: Dict[int, Dict[str, Any]] = {}
_local_connections_lock = threading.Lock()


def reap_zombie_connections(idle_timeout_seconds: float = 1800.0) -> Dict[str, Any]:
    """
    Scans all registered thread-local SQLite connections.
    Forcefully closes and cleans up:
    1. Connections originating from dead/terminated Python threads.
    2. Connections idle for longer than idle_timeout_seconds (excluding current thread).
    Returns count and metadata of reaped zombie connections.
    """
    now = time.time()
    current_ident = threading.get_ident()
    alive_idents = set(t.ident for t in threading.enumerate() if t.ident)
    reaped = []

    with _local_connections_lock:
        stale_idents = []
        for ident, entry in list(_local_connections.items()):
            conn = entry.get("conn")
            created_at = entry.get("created_at", now)
            last_used = entry.get("last_used", now)
            is_dead_thread = ident not in alive_idents
            is_idle_stale = (now - last_used > idle_timeout_seconds) and (ident != current_ident)

            if is_dead_thread or is_idle_stale:
                stale_idents.append(ident)
                reason = "dead_thread" if is_dead_thread else "idle_timeout"
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                reaped.append({
                    "thread_ident": ident,
                    "reason": reason,
                    "idle_seconds": round(now - last_used, 1)
                })

        for ident in stale_idents:
            if ident in _local_connections:
                del _local_connections[ident]

    return {
        "status": "success",
        "reaped_count": len(reaped),
        "reaped_connections": reaped
    }


def get_database_connection_stats() -> Dict[str, Any]:
    """Returns real-time connection pool, thread-local registry, and WAL status."""
    now = time.time()
    with _local_connections_lock:
        thread_conn_count = len(_local_connections)
        connections_detail = [
            {
                "thread_ident": ident,
                "idle_seconds": round(now - entry.get("last_used", now), 1)
            }
            for ident, entry in _local_connections.items()
        ]
    with _pool_lock:
        pool_stats = {
            p_path: {"created": pool.created, "available": pool.pool.qsize()}
            for p_path, pool in _db_pools.items()
        }

    wal_size_bytes = 0
    wal_path = f"{DB_FILE}-wal"
    if os.path.exists(wal_path):
        try:
            wal_size_bytes = os.path.getsize(wal_path)
        except Exception:
            pass

    return {
        "db_file": DB_FILE,
        "thread_local_connections_count": thread_conn_count,
        "thread_connections": connections_detail,
        "connection_pools": pool_stats,
        "wal_size_bytes": wal_size_bytes
    }


def get_db():
    """Get or establish thread-local SQLite database connection."""
    conn = getattr(_local, "connection", None)
    cached_path = getattr(_local, "connection_path", None)
    current_path = os.path.abspath(DB_FILE)
    current_ident = threading.get_ident()
    now = time.time()

    if conn is not None:
        if cached_path != current_path:
            try:
                conn.close()
            except Exception:
                pass
            conn = None
            _local.connection = None
            _local.connection_path = None
        else:
            try:
                conn.cursor().execute("SELECT 1")
                # Update last used timestamp
                with _local_connections_lock:
                    if current_ident in _local_connections:
                        _local_connections[current_ident]["last_used"] = now
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
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
                conn.execute("PRAGMA busy_timeout = 5000")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA temp_store = MEMORY")
                conn.execute("PRAGMA cache_size = -262144")
                conn.execute("PRAGMA mmap_size = 4294967296")
                conn.execute("PRAGMA threads = 4")
                conn.execute("PRAGMA wal_autocheckpoint = 2000")
                conn.execute("PRAGMA foreign_keys = ON")
                _local.connection = conn

                _local.connection_path = current_path
                with _local_connections_lock:
                    _local_connections[current_ident] = {
                        "conn": conn,
                        "created_at": now,
                        "last_used": now
                    }
                break

            except (KeyboardInterrupt, MemoryError, SystemExit):
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                raise
            except Exception as e:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    conn = None
                if isinstance(e, sqlite3.OperationalError):
                    attempts += 1
                    if attempts >= 5:
                        raise e
                    time.sleep(0.05 * (2 ** attempts))
                else:
                    raise e
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

def _ensure_column(cursor, table: str, column: str, type_def: str):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")

_initialized_dbs = set()

def init_db():
    """Initialize database tables, pragmas, indices, and schema migrations."""
    global _initialized_dbs
    if DB_FILE in _initialized_dbs:
        return
        
    reset_db_connections()
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA busy_timeout = 5000;")
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

            _ensure_column(cursor, "file_chunks", "chunk_hash", "TEXT")
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_mime_type ON files(mime_type)')

            _ensure_column(cursor, "files", "user_id", "INTEGER DEFAULT 0")
            _ensure_column(cursor, "files", "notes", "TEXT")
            _ensure_column(cursor, "files", "insights", "TEXT")
            _ensure_column(cursor, "files", "acl_permissions", "TEXT")

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id)')

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)')

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

            _ensure_column(cursor, "auto_rules", "priority", "INTEGER DEFAULT 0")

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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ocr_coords_file_id ON ocr_coords(file_id)')

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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_history_executed ON search_history(executed_at DESC)')

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
                    metadata_json TEXT,
                    prev_hash TEXT,
                    block_hash TEXT
                )
            """)
            _ensure_column(cursor, "system_audit_ledger", "prev_hash", "TEXT")
            _ensure_column(cursor, "system_audit_ledger", "block_hash", "TEXT")
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
    
    _initialized_dbs.add(DB_FILE)
    print("Database initialized successfully.")

def run_maintenance(truncate_wal: bool = False) -> Dict[str, Any]:
    """Execute WAL checkpoint (PASSIVE or TRUNCATE), incremental vacuum, and reap zombie connections."""
    reap_report = reap_zombie_connections()
    if DB_FILE and os.path.dirname(DB_FILE):
        os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            cursor = conn.cursor()
            mode = "TRUNCATE" if truncate_wal else "PASSIVE"
            cursor.execute(f"PRAGMA wal_checkpoint({mode})")
            cursor.execute("PRAGMA incremental_vacuum(100)")
            cursor.execute("PRAGMA optimize")
    return {
        "status": "success",
        "checkpoint_mode": mode,
        "zombie_reap": reap_report
    }


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
        metadata_str = json.dumps(metadata) if metadata else "{}"
        try:
            with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO system_audit_ledger (event_type, description, timestamp, metadata_json)
                        VALUES (?, ?, ?, ?)
                    """, (event_type, description, time.time(), metadata_str))
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO system_audit_ledger (event_type, description, timestamp, metadata_json)
                        VALUES (?, ?, ?, ?)
                    """, (event_type, description, time.time(), metadata_str))
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error logging audit event: {e}")


def _parse_audit_metadata(r: sqlite3.Row) -> dict:
    item = dict(r)
    try:
        item["metadata"] = json.loads(item.get("metadata_json") or "{}")
    except Exception:
        item["metadata"] = {}
    return item

def get_audit_ledger(limit: int = 50) -> list:
    """Retrieve recent system audit ledger entries."""
    try:
        try:
            with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, event_type, description, timestamp, metadata_json FROM system_audit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [_parse_audit_metadata(r) for r in cursor.fetchall()]
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, event_type, description, timestamp, metadata_json FROM system_audit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [_parse_audit_metadata(r) for r in cursor.fetchall()]
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error getting audit ledger: {e}")
        return []


def validate_and_repair_indexes(conn=None) -> dict:
    """
    Validates and auto-repairs all core performance B-Tree indices.
    Zero-dependency stdlib implementation.
    """
    required_indexes = [
        ("idx_files_modified", "files", "files(modified_at)"),
        ("idx_files_filename", "files", "files(filename)"),
        ("idx_files_sha256", "files", "files(sha256)"),
        ("idx_files_mime_type", "files", "files(mime_type)"),
        ("idx_files_user_id", "files", "files(user_id)"),
        ("idx_file_chunks_file_id", "file_chunks", "file_chunks(file_id)"),
        ("idx_file_chunks_hash", "file_chunks", "file_chunks(chunk_hash)"),
        ("idx_tags_tag", "tags", "tags(tag)"),
        ("idx_ocr_coords_file_id", "ocr_coords", "ocr_coords(file_id)"),
        ("idx_system_audit_timestamp", "system_audit_ledger", "system_audit_ledger(timestamp)")
    ]

    verified = []
    repaired = []

    def _check_on_cursor(cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing = {r[0] for r in cursor.fetchall() if r[0]}
        for idx_name, tbl, defn in required_indexes:
            if idx_name in existing:
                verified.append(idx_name)
            else:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {defn}")
                    repaired.append(idx_name)
                except Exception:
                    pass

    if conn is not None:
        cursor = conn.cursor()
        _check_on_cursor(cursor)
    else:
        with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as local_conn:
            with local_conn:
                cursor = local_conn.cursor()
                _check_on_cursor(cursor)

    return {
        "status": "success",
        "total_required": len(required_indexes),
        "verified_count": len(verified),
        "repaired_count": len(repaired),
        "verified_indexes": verified,
        "repaired_indexes": repaired
    }
