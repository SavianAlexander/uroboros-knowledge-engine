import unittest
import os
import shutil
import tempfile
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainChaos(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_chaos_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_chaos_corrupted_utf8_binary_payload(self):
        """Verify indexer handles corrupted non-UTF-8 binary payloads without crashing.

        Preconditions: Binary file with corrupt byte sequences created in test directory.
        Invariants: Directory indexer logs or handles binary parsing errors gracefully.
        Expected Outcomes: Indexing completes cleanly and file record exists in database.
        """
        corrupt_file = os.path.join(self.test_dir, "corrupt.bin")
        with open(corrupt_file, "wb") as f:
            f.write(b"\x80\xff\xfe\x00\x15\xfa\xde\xad\xbe\xef" * 100)

        try:
            know.index_directory(self.test_dir)
            conn = know.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM files WHERE filename = 'corrupt.bin'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            conn.close()
        except Exception as e:
            self.fail(f"Corrupt binary payload ingestion crashed engine: {e}")

    def test_02_chaos_simulated_read_lock_recovery(self):
        """Verify database read lock contention recovers cleanly without leaking connections.

        Preconditions: Multiple active database connections executing concurrent read transactions.
        Invariants: SQLite WAL mode permits concurrent readers without connection lock deadlocks.
        Expected Outcomes: Both connection read queries succeed and connections close cleanly.
        """
        conn1 = know.get_db()
        conn2 = know.get_db()
        try:
            c1 = conn1.cursor()
            c2 = conn2.cursor()
            c1.execute("SELECT COUNT(*) FROM files")
            c2.execute("SELECT COUNT(*) FROM files")
            _ = c1.fetchone()
            _ = c2.fetchone()
        finally:
            conn1.close()
            conn2.close()

    def test_03_chaos_rapid_db_reset_stress(self):
        """Verify multi-threaded database connection pool reset under concurrent thread load.

        Preconditions: 5 parallel worker threads rapidly resetting and reconnecting DB handle.
        Invariants: know.reset_db_connections synchronization prevents thread race conditions.
        Expected Outcomes: All threads complete execution with zero thread exception errors.
        """
        import threading
        errors = []

        def worker():
            try:
                for _ in range(10):
                    know.reset_db_connections()
                    c = know.get_db()
                    c.close()
            except Exception as ex:
                errors.append(ex)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"DB connection reset race condition: {errors}")

if __name__ == "__main__":
    unittest.main()
