"""
Filesystem watchdog and active directory monitoring thread.
"""
import os
import time
import shutil
import threading
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

def start_active_folder_watcher(directory: str, callback: Optional[Callable[[], None]] = None):
    """Start background directory watcher thread."""
    start_active_folder_watcher.active = True

    def watch_loop():
        from src.infrastructure.database import get_db, DB_FILE
        from src.infrastructure.vector_engine import index_directory
        last_checked = {}
        pending_stable = {}

        while getattr(start_active_folder_watcher, "active", True):
            if not os.path.exists(directory):
                time.sleep(2)
                continue

            try:
                _, _, free = shutil.disk_usage(directory)
                if free < 10 * 1024 * 1024:
                    time.sleep(5)
                    continue
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in watcher.py: {e}")
                logger.warning(f"Error checking disk usage: {e}")

            current_files = {}
            ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                for f in files:
                    if f == DB_FILE:
                        continue
                    fp = os.path.join(root, f)
                    try:
                        mtime = os.path.getmtime(fp)
                        size = os.path.getsize(fp)
                        current_files[fp] = (mtime, size)
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception as e:
                        import logging; logging.getLogger(__name__).exception(f"Swallowed error in watcher.py: {e}")
                        logger.warning(f"Error checking file {fp}: {e}")

            stable_files = {}
            for fp, stamp in current_files.items():
                if fp not in last_checked or last_checked[fp] != stamp:
                    if fp in pending_stable and pending_stable[fp] == stamp:
                        stable_files[fp] = stamp
                    else:
                        pending_stable[fp] = stamp

            for fp in list(pending_stable.keys()):
                if fp not in current_files or fp in stable_files:
                    del pending_stable[fp]

            has_changes = len(stable_files) > 0
            deleted_files = []
            for fp in last_checked:
                if fp not in current_files:
                    deleted_files.append(fp)
                    has_changes = True

            if deleted_files:
                try:
                    conn = get_db()
                    cursor = conn.cursor()
                    with conn:
                        placeholders = ",".join("?" for _ in deleted_files)
                        cursor.execute(f"SELECT id, filepath FROM files WHERE filepath IN ({placeholders})", deleted_files)
                        rows = cursor.fetchall()
                        if rows:
                            del_ids = [r[0] for r in rows]
                            del_fps = [r[1] for r in rows]
                            id_ph = ",".join("?" for _ in del_ids)
                            fp_ph = ",".join("?" for _ in del_fps)
                            cursor.execute(f"DELETE FROM files WHERE id IN ({id_ph})", del_ids)
                            cursor.execute(f"DELETE FROM fts_files WHERE filepath IN ({fp_ph})", del_fps)
                            cursor.execute(f"DELETE FROM fts_file_chunks WHERE file_id IN ({id_ph})", del_ids)
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception as e:
                    import logging; logging.getLogger(__name__).exception(f"Swallowed error in watcher.py: {e}")
                    logger.warning(f"Error deleting from DB: {e}")

            if has_changes:
                index_directory(directory)
                if callback:
                    callback()

                for fp, stamp in stable_files.items():
                    last_checked[fp] = stamp
                for fp in deleted_files:
                    if fp in last_checked:
                        del last_checked[fp]

            if not last_checked and current_files:
                index_directory(directory)
                if callback:
                    callback()
                last_checked = dict(current_files)

            time.sleep(2)

    t = threading.Thread(target=watch_loop, name="WatcherThread", daemon=True)
    t.start()

real_start_active_folder_watcher = start_active_folder_watcher
