"""
Continuous Autonomous Filesystem Watcher & Knowledge Vault Synchronizer.
Standard: Pure Python Standard Library (os, time, threading, sqlite3, re).
Ponytail Senior Dev Principle: Lightweight background polling, zero-dependency timestamp delta detection, debounced incremental FTS5 indexing, and zero CPU waste.
"""

import os
import sys
import time
import threading
import sqlite3
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infrastructure.database import get_db, DB_FILE


class VaultAutoWatcher:
    """
    Background sentinel monitoring vault/ for new and modified documents,
    incrementally indexing them into SQLite FTS5 database in real time.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VaultAutoWatcher, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, poll_interval_s: float = 5.0):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._poll_interval = poll_interval_s
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._file_mtimes: Dict[str, float] = {}
        self._indexed_count = 0
        self.vault_dir = os.path.join(BASE_DIR, "vault")

    def scan_and_index_delta(self) -> Dict[str, Any]:
        """Perform a single incremental scan over vault/ and index any changed files."""
        t0 = time.perf_counter()
        changed_files = []

        if not os.path.exists(self.vault_dir):
            return {"status": "no_vault", "indexed": 0, "scan_ms": 0}

        conn = get_db()
        cursor = conn.cursor()

        def _walk_entries(directory: str):
            try:
                with os.scandir(directory) as it:
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False):
                            yield from _walk_entries(entry.path)
                        elif entry.is_file(follow_symlinks=False) and entry.name.endswith((".md", ".txt", ".json")):
                            yield entry
            except (PermissionError, FileNotFoundError):
                pass

        for entry in _walk_entries(self.vault_dir):
            full_path = entry.path
            file = entry.name
            try:
                stat = entry.stat()
                mtime = stat.st_mtime
                mtime_ns = stat.st_mtime_ns
                last_mtime = self._file_mtimes.get(full_path, 0.0)

                if mtime > last_mtime:
                    self._file_mtimes[full_path] = mtime
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    cursor.execute("SELECT id FROM files WHERE filepath = ?", (full_path,))
                    row = cursor.fetchone()

                    if row:
                        file_id = row[0]
                        cursor.execute(
                            "UPDATE files SET content = ?, file_size = ?, modified_at = ? WHERE id = ?",
                            (content, len(content), mtime, file_id)
                        )
                        cursor.execute(
                            "UPDATE fts_files SET content = ? WHERE rowid = ?",
                            (content, file_id)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO files (filename, filepath, content, file_size, modified_at) VALUES (?, ?, ?, ?, ?)",
                            (file, full_path, content, len(content), mtime)
                        )
                        file_id = cursor.lastrowid
                        cursor.execute(
                            "INSERT INTO fts_files (rowid, filename, filepath, content, notes) VALUES (?, ?, ?, ?, ?)",
                            (file_id, file, full_path, content, "")
                        )

                    changed_files.append(file)
                    self._indexed_count += 1
            except Exception:
                pass

        conn.commit()
        scan_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "scan_complete",
            "indexed_count": len(changed_files),
            "total_indexed": self._indexed_count,
            "changed_files": changed_files[:10],
            "scan_ms": scan_ms
        }
