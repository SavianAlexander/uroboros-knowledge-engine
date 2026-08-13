import os
import time
import glob
import shutil
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from src.infrastructure.database import get_db, get_db_connection, reset_db_connections, DB_FILE

logger = logging.getLogger(__name__)

def create_db_snapshot() -> int:
    """Create atomic database snapshot using native SQLite backup API with closed connection."""
    try:
        with get_db_connection(DB_FILE, timeout=10.0) as conn:
            with conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning(f"Swallowed error in database.py: {e}")
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
        logger.exception(f"Swallowed error in database.py: {e}")
        try:
            if c_dst: c_dst.close()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning(f"Swallowed error in database.py: {e}")
        try:
            if c_src: c_src.close()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning(f"Swallowed error in database.py: {e}")
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
            logger.exception(f"Swallowed error in database.py: {e}")
            try:
                if c_dst: c_dst.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                logger.warning(f"Swallowed error in database.py: {e}")
            try:
                if c_src: c_src.close()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                logger.warning(f"Swallowed error in database.py: {e}")
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
            logger.warning(f"Swallowed error in database.py: {e}")
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
            logger.warning(f"Swallowed error in database.py: {e}")
    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    return snapshots