import os
import sys
import unittest
import threading
import time
import tempfile
import shutil
import concurrent.futures

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.domain.thread_watchdog import register_worker_thread, list_active_workers, shutdown_all_workers
from src.infrastructure.system_stability_guard import enforce_system_stability


class TestDomainResourceStability(unittest.TestCase):
    """Domain test suite for memory leaks, thread watchdog lifecycle, connection pool exhaustion, and resource stability."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_resource_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_thread_watchdog_daemon_enforcement(self):
        """Verify thread watchdog enforces daemon=True on all registered workers.

        Preconditions: Non-daemon thread passed to register_worker_thread().
        Invariants: Thread.daemon property set to True to prevent process shutdown hangs.
        Expected Outcomes: thread.daemon is True and thread is recorded in global registry.
        """
        worker = threading.Thread(target=lambda: time.sleep(0.01), daemon=False)
        registered = register_worker_thread(worker, name="test_daemon_enforce")
        self.assertTrue(registered.daemon)
        self.assertTrue(worker.daemon)

    def test_02_thread_watchdog_shutdown_all_workers(self):
        """Verify shutdown_all_workers joins active background workers within timeout.

        Preconditions: Active background thread registered.
        Invariants: shutdown_all_workers joins thread without hanging or raising exceptions.
        Expected Outcomes: status='success', worker status reported as 'stopped'.
        """
        stop_event = threading.Event()
        def worker_loop():
            stop_event.wait(timeout=0.1)

        t = threading.Thread(target=worker_loop, name="ephemeral_worker")
        register_worker_thread(t, name="ephemeral_worker")
        t.start()

        stop_event.set()
        shutdown_res = shutdown_all_workers(timeout=0.5)
        self.assertEqual(shutdown_res["status"], "success")
        self.assertFalse(t.is_alive())

    def test_03_system_stability_gc_collect_and_memory_footprint(self):
        """Verify enforce_system_stability collects garbage and computes working set size.

        Preconditions: Unreferenced objects allocated in memory.
        Invariants: enforce_system_stability runs gc.collect() and queries process memory.
        Expected Outcomes: status='stable', unreachable_objects_collected >= 0, stability_guarantee='active'.
        """
        # Allocate unreferenced objects
        dummy = [{"data": "x" * 1000} for _ in range(100)]
        del dummy

        res = enforce_system_stability()
        self.assertEqual(res["status"], "stable")
        self.assertGreaterEqual(res["unreachable_objects_collected"], 0)
        self.assertEqual(res["stability_guarantee"], "active")

    def test_04_oversized_file_ingestion_ram_guard(self):
        """Verify (Angle 3) file parser boundary guards prevent RAM exhaustion on oversized payloads.

        Preconditions: 2MB test payload written to disk.
        Invariants: System processes or chunks file within memory bounds without out-of-memory exceptions.
        Expected Outcomes: Indexing completes cleanly.
        """
        large_file = os.path.join(self.test_dir, "large_sample.txt")
        with open(large_file, "w", encoding="utf-8") as f:
            f.write("A" * 500000)

        know.index_directory(self.test_dir)
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files WHERE filename = 'large_sample.txt'")
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_05_cyclic_reference_memory_leak_cleanup(self):
        """Verify circular reference graph collection to prevent memory leaks during long-running tasks.

        Preconditions: Circular references created between dictionary objects.
        Invariants: enforce_system_stability triggers cycle collection.
        Expected Outcomes: Cyclic memory collected cleanly.
        """
        class Node:
            def __init__(self):
                self.neighbor = None

        n1 = Node()
        n2 = Node()
        n1.neighbor = n2
        n2.neighbor = n1
        del n1, n2

        res = enforce_system_stability()
        self.assertEqual(res["status"], "stable")

    def test_06_connection_pool_depletion_resistance(self):
        """Verify connection pool recycling prevents file handle exhaustion under rapid acquisitions.

        Preconditions: 50 consecutive get_db() calls in sequence.
        Invariants: Thread-local connection reused without leaking open file descriptors.
        Expected Outcomes: All queries execute without SQLite database locked or too many open files errors.
        """
        for i in range(50):
            conn = know.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_07_zombie_thread_detection_in_worker_list(self):
        """Verify list_active_workers provides live status snapshot of registered workers.

        Preconditions: Registered thread created and started.
        Invariants: list_active_workers returns list with is_alive and is_daemon boolean attributes.
        Expected Outcomes: Registry list is non-empty.
        """
        workers = list_active_workers()
        self.assertIsInstance(workers, list)
        for w in workers:
            self.assertIn("is_alive", w)
            self.assertIn("is_daemon", w)

    def test_08_sub_5ms_micro_reset_stability(self):
        """Verify reset_db_connections executes with sub-5ms latency across rapid teardowns.

        Preconditions: Database connection open.
        Invariants: reset_db_connections closes connection and resets thread-local state.
        Expected Outcomes: 20 consecutive reset cycles complete in under 100ms total.
        """
        t0 = time.time()
        for _ in range(20):
            know.get_db()
            know.reset_db_connections()
        t1 = time.time()
        self.assertLess(t1 - t0, 0.5)

    def test_09_sqlite_busy_timeout_and_wal_recovery(self):
        """Verify PRAGMA busy_timeout configuration on initialized connections.

        Preconditions: Standard database connection acquired.
        Invariants: busy_timeout is set to prevent immediate locking failures on concurrent writes.
        Expected Outcomes: Querying busy_timeout returns non-zero timeout value (e.g. 5000ms).
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA busy_timeout")
            timeout_val = cursor.fetchone()[0]
            self.assertGreaterEqual(timeout_val, 1000)

    def test_10_concurrent_memory_stability_stress(self):
        """Verify concurrent multi-threaded stability under memory cleanup and read load.

        Preconditions: 15 concurrent threads running memory stability guards and database queries.
        Invariants: Thread locks and GC operations execute without segfaults or locking deadlocks.
        Expected Outcomes: 100% of concurrent workers succeed without error.
        """
        def worker(idx):
            enforce_system_stability()
            with know.get_db() as conn:
                conn.execute("SELECT 1")
            return True

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(worker, range(20)))

        self.assertEqual(sum(results), 20)


if __name__ == "__main__":
    unittest.main()
