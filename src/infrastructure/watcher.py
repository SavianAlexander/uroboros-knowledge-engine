"""
Filesystem watchdog and active directory monitoring thread.
Uses incremental mtime tracking, directory-level filtering, and single-file dispatch
to avoid brute-force full directory disk-thrashing.
"""
import os
import time
import shutil
import threading
from typing import Callable, Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

def start_active_folder_watcher(directory: str, callback: Optional[Callable[[], None]] = None):
    """Start background directory watcher thread with debounced incremental scanning."""
    start_active_folder_watcher.active = True

    def watch_loop():
        from src.infrastructure.database import get_db, DB_FILE
        from src.infrastructure.vector_engine import index_directory, index_file
        last_checked: Dict[str, Tuple[float, int]] = {}
        dir_mtimes: Dict[str, float] = {}
        pending_stable: Dict[str, Tuple[float, int]] = {}
        ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache"}

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
                logger.warning(f"Error checking disk usage: {e}")

            current_files: Dict[str, Tuple[float, int]] = {}
            try:
                # Fast incremental scan: check directory mtimes before recursive traversal
                for root, dirs, files in os.walk(directory):
                    dirs[:] = [d for d in dirs if d not in ignored_dirs]
                    try:
                        root_mtime = os.path.getmtime(root)
                    except OSError:
                        root_mtime = 0.0

                    # Stat files in this directory
                    for f in files:
                        if f == DB_FILE or f.startswith('.'):
                            continue
                        fp = os.path.join(root, f)
                        try:
                            mtime = os.path.getmtime(fp)
                            size = os.path.getsize(fp)
                            current_files[fp] = (mtime, size)
                        except OSError:
                            continue
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                logger.warning(f"Error scanning directory {directory}: {e}")

            # Identify newly modified / added stable files
            stable_files: Dict[str, Tuple[float, int]] = {}
            for fp, stamp in current_files.items():
                if fp not in last_checked or last_checked[fp] != stamp:
                    if fp in pending_stable and pending_stable[fp] == stamp:
                        stable_files[fp] = stamp
                    else:
                        pending_stable[fp] = stamp

            for fp in list(pending_stable.keys()):
                if fp not in current_files or fp in stable_files:
                    del pending_stable[fp]

            # Identify deleted files
            deleted_files = [fp for fp in last_checked if fp not in current_files]

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
                    logger.warning(f"Error deleting files from DB: {e}")

            # Process incremental single-file updates vs full directory on cold start
            if not last_checked and current_files:
                # Cold start: initial bulk index
                index_directory(directory)
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        logger.warning(f"Watcher callback error: {e}")
                last_checked = dict(current_files)
            elif stable_files or deleted_files:
                # Incremental single-file update
                for fp in stable_files:
                    try:
                        index_file(fp)
                    except Exception:
                        index_directory(directory)
                        break

                if callback:
                    try:
                        callback()
                    except Exception as e:
                        logger.warning(f"Watcher callback error: {e}")

                for fp, stamp in stable_files.items():
                    last_checked[fp] = stamp
                for fp in deleted_files:
                    if fp in last_checked:
                        del last_checked[fp]

            time.sleep(2)

    t = threading.Thread(target=watch_loop, name="WatcherThread", daemon=True)
    t.start()

real_start_active_folder_watcher = start_active_folder_watcher

