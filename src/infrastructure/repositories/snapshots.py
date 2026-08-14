import os
import time
import glob
import shutil
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, get_db_connection, reset_db_connections

logger = logging.getLogger(__name__)

def create_db_snapshot() -> int:
    """Create atomic database snapshot using native SQLite backup API with closed connection."""
    target_db = db_module.DB_FILE
    try:
        with get_db_connection(target_db, timeout=10.0) as conn:
            with conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in database.py: {e}")
    timestamp = int(time.time())
    dest = f"{target_db}.snapshot-{timestamp}"
    if os.path.exists(dest):
        timestamp = int(time.time() * 1000)
        dest = f"{target_db}.snapshot-{timestamp}"
    c_src = None
    c_dst = None
    try:
        c_src = sqlite3.connect(target_db)
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
        shutil.copy2(target_db, dest)
    finally:
        if c_dst: c_dst.close()
        if c_src: c_src.close()
    return timestamp

def restore_db_snapshot(timestamp: int) -> bool:
    """Restore database from snapshot timestamp."""
    target_db = db_module.DB_FILE
    src = f"{target_db}.snapshot-{timestamp}"
    if os.path.exists(src):
        reset_db_connections()

        # Purge lingering WAL / SHM files to prevent ghost pages
        for ext in ["-wal", "-shm"]:
            wal_file = target_db + ext
            if os.path.exists(wal_file):
                try:
                    os.remove(wal_file)
                except Exception as e:
                    logger.debug(f"Snapshot restore WAL purge notice: {e}")

        c_src = None
        c_dst = None
        restored = False
        try:
            c_src = sqlite3.connect(src)
            c_dst = sqlite3.connect(target_db)
            c_src.backup(c_dst)
            restored = True
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.debug(f"Snapshot backup API fallback notice: {e}")
            try:
                if c_dst: c_dst.close()
            except Exception:
                pass
            try:
                if c_src: c_src.close()
            except Exception:
                pass
            c_dst = None
            c_src = None
            shutil.copy2(src, target_db)
            restored = True
        finally:
            if c_dst:
                try: c_dst.close()
                except Exception: pass
            if c_src:
                try: c_src.close()
                except Exception: pass

        if restored:
            try:
                with get_db_connection(target_db, timeout=10.0) as conn:
                    with conn:
                        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except Exception as e:
                logger.debug(f"Snapshot post-restore checkpoint notice: {e}")

        return restored
    return False

def delete_db_snapshot(timestamp: int) -> bool:
    """Delete a database snapshot by timestamp."""
    target_db = db_module.DB_FILE
    src = f"{target_db}.snapshot-{timestamp}"
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
    target_db = db_module.DB_FILE
    snapshots = []
    for f in glob.glob(f"{target_db}.snapshot-*"):
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