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

        for root, _, files in os.walk(self.vault_dir):
            for file in files:
                if file.endswith((".md", ".txt", ".json")):
                    full_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(full_path)
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
                                    "UPDATE files SET content = ?, size = ?, mtime = ? WHERE id = ?",
                                    (content, len(content), mtime, file_id)
                                )
                                cursor.execute(
                                    "UPDATE fts_files SET content = ? WHERE rowid = ?",
                                    (content, file_id)
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO files (filename, filepath, content, size, mtime) VALUES (?, ?, ?, ?, ?)",
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
