import os
import sys
import time
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, init_db, reset_db_connections
from src.infrastructure.repositories.snapshots import (
    create_db_snapshot,
    restore_db_snapshot,
    delete_db_snapshot,
    list_db_snapshots,
    prune_db_snapshots,
    get_snapshot_path,
    MAX_SNAPSHOT_RETENTION
)

class TestSnapshotRetentionPolicy(unittest.TestCase):
    """Regression test suite for DB Snapshot Retention, Deduplication & Safe Restoration."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="snapshot_test_")
        self.db_path = os.path.join(self.test_dir, "test_know.db")
        self.orig_db_file = db_module.DB_FILE
        db_module.DB_FILE = self.db_path

        # Initialize schema
        init_db()

    def tearDown(self):
        reset_db_connections()
        db_module.DB_FILE = self.orig_db_file
        if os.path.exists(self.test_dir):
            for _ in range(5):
                try:
                    shutil.rmtree(self.test_dir)
                    break
                except PermissionError:
                    reset_db_connections()
                    time.sleep(0.1)

    def test_01_retention_policy_strictly_bounded_at_max_retention(self):
        """Verify that creating 10 consecutive distinct snapshots strictly enforces MAX_SNAPSHOT_RETENTION <= 3 files on disk."""
        snapshot_timestamps = []

        for i in range(10):
            # Mutate database so each snapshot is distinct
            with db_module.get_db_connection(self.db_path) as conn:
                with conn:
                    conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                                 (f"user_{i}_{time.time()}", "hash", "user"))

            ts = create_db_snapshot(self.db_path, max_retention=MAX_SNAPSHOT_RETENTION)
            self.assertIsInstance(ts, int)
            snapshot_timestamps.append(ts)

            # Check snapshot count on disk
            snapshots_on_disk = list_db_snapshots(self.db_path)
            self.assertLessEqual(
                len(snapshots_on_disk),
                MAX_SNAPSHOT_RETENTION,
                f"Snapshot count {len(snapshots_on_disk)} exceeded MAX_SNAPSHOT_RETENTION {MAX_SNAPSHOT_RETENTION} at step {i}"
            )
            # Short sleep to guarantee distinct timestamps if clock resolution requires it
            time.sleep(0.01)

        final_snapshots = list_db_snapshots(self.db_path)
        self.assertEqual(len(final_snapshots), MAX_SNAPSHOT_RETENTION)

        # Ensure the remaining snapshots correspond to the most recent ones
        recent_timestamps = set(snapshot_timestamps[-MAX_SNAPSHOT_RETENTION:])
        found_timestamps = {s["timestamp"] for s in final_snapshots}
        self.assertEqual(found_timestamps, recent_timestamps)

    def test_02_sha256_deduplication_on_identical_database(self):
        """Verify that creating a snapshot on an unchanged database reuses existing timestamp without duplicating disk space."""
        with db_module.get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                             ("dedup_user", "dedup_hash", "admin"))

        ts1 = create_db_snapshot(self.db_path)
        snapshots_after_first = list_db_snapshots(self.db_path)
        self.assertEqual(len(snapshots_after_first), 1)

        # Attempt to create snapshot again without modifying database
        ts2 = create_db_snapshot(self.db_path)
        snapshots_after_second = list_db_snapshots(self.db_path)

        self.assertEqual(ts1, ts2, "Deduplication failed: new timestamp generated for identical DB content")
        self.assertEqual(len(snapshots_after_second), 1, "Deduplication failed: redundant file written to disk")

    def test_03_point_in_time_restore_integrity(self):
        """Verify that point-in-time snapshot restore recovers exact historical state and passes integrity check."""
        with db_module.get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                             ("state_alpha", "hash_alpha", "admin"))

        ts_alpha = create_db_snapshot(self.db_path)

        # Mutate database state (state beta)
        with db_module.get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                             ("state_beta", "hash_beta", "user"))

        time.sleep(0.02)
        ts_beta = create_db_snapshot(self.db_path)
        self.assertNotEqual(ts_alpha, ts_beta)

        # Verify state beta has 2 users
        with db_module.get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            self.assertEqual(cursor.fetchone()[0], 2)

        # Restore state alpha
        restore_success = restore_db_snapshot(ts_alpha, self.db_path)
        self.assertTrue(restore_success)

        # Verify state alpha is restored: only 1 user ('state_alpha') exists
        with db_module.get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "state_alpha")

            # Run SQLite integrity check
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            self.assertEqual(integrity, "ok")

    def test_04_delete_and_list_snapshots(self):
        """Verify listing metadata and explicit deletion of snapshots."""
        with db_module.get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                             ("delete_user", "hash", "user"))

        ts = create_db_snapshot(self.db_path)
        snaps = list_db_snapshots(self.db_path)
        self.assertTrue(any(s["timestamp"] == ts for s in snaps))

        # Delete snapshot
        deleted = delete_db_snapshot(ts, self.db_path)
        self.assertTrue(deleted)

        # Confirm removed from list
        snaps_after = list_db_snapshots(self.db_path)
        self.assertFalse(any(s["timestamp"] == ts for s in snaps_after))

    def test_05_legacy_snapshot_discovery_and_restore(self):
        """Verify backward-compatible discovery and restoration from legacy paths."""
        # Create a legacy-style snapshot file next to the database
        legacy_ts = int(time.time()) - 100
        legacy_path = f"{self.db_path}.snapshot-{legacy_ts}"
        
        # Populate legacy db snapshot
        db_module.DB_FILE = legacy_path
        init_db()
        with db_module.get_db_connection(legacy_path) as c_dst:
            with c_dst:
                c_dst.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                              ("legacy_user", "legacy_hash", "admin"))
        reset_db_connections()
        db_module.DB_FILE = self.db_path

        # Discover via list_db_snapshots
        snaps = list_db_snapshots(self.db_path)
        self.assertTrue(any(s["timestamp"] == legacy_ts for s in snaps))

        # Restore from legacy snapshot
        restored = restore_db_snapshot(legacy_ts, self.db_path)
        self.assertTrue(restored)

        # Verify content restored
        with db_module.get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = 'legacy_user'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "legacy_user")

        # Cleanup legacy file
        delete_db_snapshot(legacy_ts, self.db_path)

if __name__ == "__main__":
    unittest.main()
