"""
Zero-dependency automated background scheduled database backups and snapshot lifecycle manager.
"""
import os
import glob
import time
import sqlite3
import threading
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backups")
RETENTION_MAX_FILES = 10
RETENTION_SECONDS = 7 * 86400  # 7 days


def ensure_backup_dir() -> str:
    """Ensure the backups directory exists and returns its absolute path."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR


def create_database_backup(db_file_path: str) -> Dict[str, Any]:
    """
    Creates an atomic SQLite database online snapshot using SQLite VACUUM INTO / backup API.
    Zero-dependency stdlib implementation.
    """
    if not os.path.exists(db_file_path):
        return {"status": "error", "message": f"Database file not found: {db_file_path}"}

    ensure_backup_dir()
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"db_snapshot_{timestamp_str}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    t0 = time.time()
    try:
        source_conn = sqlite3.connect(db_file_path, timeout=30.0)
        target_conn = sqlite3.connect(backup_path)
        with target_conn:
            source_conn.backup(target_conn)
        source_conn.close()
        target_conn.close()

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        file_size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

        # Prune old backups
        prune_count = prune_old_backups()

        return {
            "status": "success",
            "backup_file": backup_filename,
            "backup_path": backup_path,
            "size_bytes": file_size,
            "elapsed_ms": elapsed_ms,
            "pruned_files_count": prune_count
        }
    except Exception as e:
        logger.exception("Failed to create database backup")
        return {"status": "error", "message": str(e)}


def prune_old_backups(max_files: int = RETENTION_MAX_FILES) -> int:
    """
    Prunes old backup snapshot files based on retention count and age limit.
    """
    ensure_backup_dir()
    pattern = os.path.join(BACKUP_DIR, "db_snapshot_*.db")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    pruned = 0
    now = time.time()

    for idx, filepath in enumerate(files):
        age_seconds = now - os.path.getmtime(filepath)
        # Prune if exceeds max retention count OR exceeds retention period
        if idx >= max_files or age_seconds > RETENTION_SECONDS:
            try:
                os.remove(filepath)
                pruned += 1
            except OSError:
                pass

    return pruned


def list_backups() -> List[Dict[str, Any]]:
    """List all available database snapshot files ordered by timestamp descending."""
    ensure_backup_dir()
    pattern = os.path.join(BACKUP_DIR, "db_snapshot_*.db")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    result = []
    for filepath in files:
        stat = os.stat(filepath)
        result.append({
            "filename": os.path.basename(filepath),
            "filepath": filepath,
            "size_bytes": stat.st_size,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
            "mtime": stat.st_mtime
        })
    return result


class BackupScheduler:
    """Background thread scheduler for automated periodic database backups."""
    def __init__(self, db_file_path: str, interval_seconds: int = 3600):
        self.db_file_path = db_file_path
        self.interval_seconds = interval_seconds
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="BackupSchedulerThread")
        self._thread.start()
        logger.info(f"BackupScheduler started with interval {self.interval_seconds}s")

    def stop(self):
        self._running = False

    def _run_loop(self):
        while self._running:
            try:
                create_database_backup(self.db_file_path)
            except Exception as e:
                logger.exception("Error in BackupScheduler thread loop")

            # Sleep in short increments for responsive stop
            for _ in range(self.interval_seconds):
                if not self._running:
                    break
                time.sleep(1)
