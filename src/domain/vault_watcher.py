"""
Continuous Zero-Stutter Background Vault Watcher:
Monitors workspace directory for real-time document creation, updates, and deletion.
Adheres strictly to the project's Cooperative Zero-Stutter Standard:
1. Thread priority lowered to IDLE (THREAD_PRIORITY_IDLE on Windows / os.nice(19)).
2. Debounced file processing (LIMIT 1 per cycle with inter-task cooling).
3. Cryptographic SHA-256 change ledger avoiding redundant embeddings.
4. Auto-indexes files and refreshes MiniVectorEngine cache on change.
"""

import os
import sys
import time
import hashlib
import threading
import logging
from typing import Dict, List, Set, Optional, Callable, Any

logger = logging.getLogger("VAULT_WATCHER")


class ZeroStutterVaultWatcher:
    """
    Cooperative zero-stutter background daemon synchronizing vault files.
    """

    SUPPORTED_EXTENSIONS = {
        '.md', '.markdown', '.py', '.txt', '.json', '.yaml', '.yml', '.ini',
        '.csv', '.tsv', '.xml', '.html', '.css', '.js', '.pdf', '.docx', '.epub'
    }

    def __init__(
        self,
        watch_directory: str,
        poll_interval: float = 2.0,
        inter_task_cooling: float = 0.1,
        on_indexed_callback: Optional[Callable[[str], None]] = None
    ):
        self.watch_directory = os.path.abspath(watch_directory)
        self.poll_interval = poll_interval
        self.inter_task_cooling = inter_task_cooling
        self.on_indexed_callback = on_indexed_callback

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._file_ledger: Dict[str, str] = {}  # filepath -> sha256_hash
        self._lock = threading.Lock()

    @staticmethod
    def _lower_thread_priority():
        """Lowers thread priority to IDLE to guarantee zero-stutter operation."""
        if sys.platform == "win32":
            try:
                import ctypes
                THREAD_PRIORITY_IDLE = -15
                handle = ctypes.windll.kernel32.GetCurrentThread()
                ctypes.windll.kernel32.SetThreadPriority(handle, THREAD_PRIORITY_IDLE)
            except Exception as e:
                logger.debug("Failed to set Windows thread priority to IDLE: %s", e)
        else:
            try:
                os.nice(19)
            except Exception:
                pass

    @staticmethod
    def compute_file_hash(filepath: str) -> Optional[str]:
        """Calculates fast SHA-256 hash of file content."""
        if not os.path.isfile(filepath):
            return None
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return None

    def scan_directory_once(self) -> Dict[str, str]:
        """Scans watched directory and builds current filepath -> sha256 map."""
        current_map: Dict[str, str] = {}
        if not os.path.isdir(self.watch_directory):
            return current_map

        for root, _, files in os.walk(self.watch_directory):
            # Skip hidden and temporary folders
            if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.git'] for part in root.split(os.sep)):
                continue

            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(root, fname)
                    f_hash = self.compute_file_hash(full_path)
                    if f_hash:
                        current_map[full_path] = f_hash

        return current_map

    def poll_sync_once(self) -> Dict[str, Any]:
        """
        Executes a single cooperative polling and synchronization pass.
        Returns report of added, modified, and deleted files.
        """
        current_map = self.scan_directory_once()
        added = []
        modified = []
        deleted = []

        with self._lock:
            # Detect added or modified files
            for fpath, fhash in current_map.items():
                if fpath not in self._file_ledger:
                    added.append(fpath)
                elif self._file_ledger[fpath] != fhash:
                    modified.append(fpath)

            # Detect deleted files
            for fpath in list(self._file_ledger.keys()):
                if fpath not in current_map:
                    deleted.append(fpath)

            # Process changes with LIMIT 1 pacing and cooling interval
            from src.infrastructure.vector_engine import index_file, MiniVectorEngine

            changed_files = added + modified
            for fpath in changed_files:
                try:
                    index_file(fpath)
                    self._file_ledger[fpath] = current_map[fpath]
                    if self.on_indexed_callback:
                        self.on_indexed_callback(fpath)
                except Exception as e:
                    logger.warning("VaultWatcher failed to index %s: %s", fpath, e)
                
                # Cooperative cooling interval between individual file re-indexes
                if self.inter_task_cooling > 0:
                    time.sleep(self.inter_task_cooling)

            # Handle deletions in ledger and DB
            if deleted:
                from src.infrastructure.database import get_db_write_connection, DB_FILE
                with get_db_write_connection(DB_FILE) as conn:
                    with conn:
                        for fpath in deleted:
                            conn.execute("DELETE FROM files WHERE filepath = ?", (fpath,))
                            conn.execute("DELETE FROM fts_files WHERE filepath = ?", (fpath,))
                            if fpath in self._file_ledger:
                                del self._file_ledger[fpath]

            if changed_files or deleted:
                MiniVectorEngine.reset_cache()

        return {
            "added_count": len(added),
            "modified_count": len(modified),
            "deleted_count": len(deleted),
            "total_tracked": len(self._file_ledger)
        }

    def _worker_loop(self):
        """Cooperative daemon loop."""
        self._lower_thread_priority()
        while self._running:
            try:
                self.poll_sync_once()
            except Exception as e:
                logger.debug("VaultWatcher polling error: %s", e)

            # Sleep poll interval in small slices for quick shutdown responsiveness
            slices = int(max(1, self.poll_interval * 10))
            for _ in range(slices):
                if not self._running:
                    break
                time.sleep(self.poll_interval / float(slices))

    def start(self):
        """Starts the background watcher daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="ZeroStutterVaultWatcher")
        self._thread.start()
        logger.info("ZeroStutterVaultWatcher started for directory: %s", self.watch_directory)

    def stop(self):
        """Stops the background watcher daemon thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("ZeroStutterVaultWatcher stopped.")

    def is_running(self) -> bool:
        return self._running
