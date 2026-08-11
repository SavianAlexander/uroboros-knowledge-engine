from src.infrastructure.database import get_db, get_db_connection, get_db_write_connection, get_pool, reset_db_connections
import src.infrastructure.database as db
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

def create_db_snapshot() -> int:
    """Create atomic database snapshot using native SQLite backup API with closed connection."""
    try:
        with get_db_connection(db.DB_FILE, timeout=10.0) as conn:
            with conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in database.py: {e}")
    timestamp = int(time.time())
    dest = f"{db.DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(dest):
        timestamp = int(time.time() * 1000)
        dest = f"{db.DB_FILE}.snapshot-{timestamp}"
    c_src = None
    c_dst = None
    try:
        c_src = sqlite3.connect(db.DB_FILE)
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
            import logging; logging.warning(f"Swallowed error in database.py: {e}")
        try:
            if c_src: c_src.close()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")
        c_dst = None
        c_src = None
        shutil.copy2(db.DB_FILE, dest)
    finally:
        if c_dst: c_dst.close()
        if c_src: c_src.close()
    return timestamp

def restore_db_snapshot(timestamp: int) -> bool:
    """Restore database from snapshot timestamp."""
    src = f"{db.DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(src):
        reset_db_connections()
        c_src = None
        c_dst = None
        try:
            c_src = sqlite3.connect(src)
            c_dst = sqlite3.connect(db.DB_FILE)
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
                import logging; logging.warning(f"Swallowed error in database.py: {e}")
            try:
                if c_src: c_src.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in database.py: {e}")
            c_dst = None
            c_src = None
            shutil.copy2(src, db.DB_FILE)
            return True
        finally:
            if c_dst: c_dst.close()
            if c_src: c_src.close()
    return False

def delete_db_snapshot(timestamp: int) -> bool:
    """Delete a database snapshot by timestamp."""
    src = f"{db.DB_FILE}.snapshot-{timestamp}"
    if os.path.exists(src):
        try:
            os.remove(src)
            return True
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")
    return False

def list_db_snapshots() -> List[Dict[str, Any]]:
    """List available database snapshots."""
    snapshots = []
    for f in glob.glob(f"{db.DB_FILE}.snapshot-*"):
        try:
            ts = f.split("-")[-1]
            size = os.path.getsize(f)
            snapshots.append({"timestamp": ts, "filename": f, "size": size})
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")
    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    return snapshots