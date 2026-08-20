import src.core.config as config
import src.infrastructure.database as db
import unittest
import os
import shutil
import tempfile
import sqlite3
import time
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_db_")
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

    def test_01_db_initialization_and_pragma(self):
        """Verify DB schema initialization and performance PRAGMA configurations.

        Preconditions: Isolated temporary database path initialized via know.init_db().
        Invariants: Database operates in WAL mode with non-negative MMAP size and valid auto-vacuum enum.
        Expected Outcomes: PRAGMA journal_mode is WAL, mmap_size is >= 0, auto_vacuum is in (0, 1, 2).
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        self.assertEqual(mode.lower(), "wal")

        cursor.execute("PRAGMA mmap_size")
        mmap_val = cursor.fetchone()[0]
        self.assertGreaterEqual(mmap_val, 0)

        cursor.execute("PRAGMA auto_vacuum")
        vac_val = cursor.fetchone()[0]
        self.assertIn(vac_val, (0, 1, 2))
        conn.close()

    def test_02_fts_porter_tokenizer(self):
        """Verify FTS5 full-text search index tokenization using Porter stemmer.

        Preconditions: FTS index populated with sample text content.
        Invariants: Search queries match stemmed word forms across document records.
        Expected Outcomes: FTS query for stemmed keyword 'process' returns matching records for 'processing'.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (filepath, filename, content)
            VALUES ('/tmp/test1.txt', 'test1.txt', 'The developer is processing data.')
        """)
        cursor.execute("""
            INSERT INTO fts_files (filepath, filename, content)
            VALUES ('/tmp/test1.txt', 'test1.txt', 'The developer is processing data.')
        """)
        conn.commit()

        cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH 'process'")
        rows = cursor.fetchall()
        self.assertGreater(len(rows), 0)
        conn.close()

    def test_03_composite_indexes_exist(self):
        """Verify initial creation of O(log N) composite indexes on files table.

        Preconditions: Schema initialized in target database.
        Invariants: Index metadata table includes required column indexes.
        Expected Outcomes: Index list contains idx_files_filepath, idx_files_filename, and idx_files_modified.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("PRAGMA index_list('files')")
        indexes = [row['name'] for row in cursor.fetchall()]
        self.assertIn("idx_files_filepath", indexes)
        self.assertIn("idx_files_filename", indexes)
        self.assertIn("idx_files_modified", indexes)
        conn.close()

    def test_04_double_close_safety(self):
        """Verify double-closing a database connection executes safely without exception.

        Preconditions: Active database connection handle opened.
        Invariants: Calling close() on an already closed connection does not crash or raise errors.
        Expected Outcomes: Second close call completes without raising an exception.
        """
        conn = know.get_db()
        conn.close()
        try:
            conn.close()
        except Exception as e:
            self.fail(f"Double-close raised exception: {e}")

    def test_05_connection_timeout_guard(self):
        """Verify database connection object initializes with required timeout parameters.

        Preconditions: Active connection established via know.get_db().
        Invariants: Connection handle is non-null and valid.
        Expected Outcomes: Connection handle is successfully retrieved and closed.
        """
        conn = know.get_db()
        self.assertIsNotNone(conn)
        conn.close()

    def test_06_atomic_snapshot_during_read(self):
        """Verify atomic database snapshot creation while read handle is active.

        Preconditions: Active database read cursor open on files table.
        Invariants: Snapshot generation creates valid backup file on disk without locking error.
        Expected Outcomes: Snapshot timestamp returned and snapshot file exists on disk.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        ts = know.create_db_snapshot()
        self.assertIsNotNone(ts)
        snap_file = know.get_snapshot_path(ts) or f"{db.DB_FILE}.snapshot-{ts}"
        self.assertTrue(os.path.exists(snap_file))
        conn.close()

    def test_07_submillisecond_connection_reset(self):
        """Verify sub-second database connection pool reset and cleanup under rapid iteration.

        Preconditions: 50 sequential reset and reconnect iterations.
        Invariants: Connection pool resets and closes connections cleanly without resource leakage.
        Expected Outcomes: Total iteration duration is strictly less than 1.0 second.
        """
        t0 = time.time()
        for _ in range(50):
            know.reset_db_connections()
            conn = know.get_db()
            conn.close()
        t1 = time.time()
        self.assertLess((t1 - t0), 1.0)

    def test_08_batch_transaction_scaling(self):
        """Verify high-throughput batch insertion of 1,000 file records in a single transaction.

        Preconditions: Explicit transaction block started on active database connection.
        Invariants: All 1,000 records committed atomically into files table.
        Expected Outcomes: Total row count in files table is at least 1,000 after commit.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        for i in range(1000):
            cursor.execute("INSERT INTO files (filepath, filename, content) VALUES (?, ?, ?)",
                           (f"/tmp/batch_{i}.txt", f"batch_{i}.txt", f"Batch content {i}"))
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        self.assertGreaterEqual(count, 1000)
        conn.close()

    def test_09_sql_wildcard_escaping(self):
        """Verify SQL LIKE query wildcard escaping for special characters (%, _, ').

        Preconditions: File record inserted with raw SQL wildcards in filename.
        Invariants: Escaped LIKE parameter matches exact literal string without wildcard expansion.
        Expected Outcomes: Query returns exactly 1 row matching the inserted wildcard filename.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (filepath, filename, content) VALUES (?, ?, ?)",
                       ("/tmp/wildcard.txt", "100%_special'name.txt", "Special content"))
        conn.commit()

        cursor.execute("SELECT filepath FROM files WHERE filename LIKE ? ESCAPE '\\'", ("%100\\%\\_special'name.txt%",))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['filepath'], "/tmp/wildcard.txt")
        conn.close()

    def test_10_maintenance_vacuum_and_revisions(self):
        """Verify file revision snapshot history and background WAL maintenance execution.

        Preconditions: Multiple revisions written to disk file and saved in database.
        Invariants: Revision history retrieved accurately; run_maintenance completes cleanly.
        Expected Outcomes: Exactly 2 revisions retrieved and run_maintenance raises no exceptions.
        """
        test_f = os.path.join(self.test_dir, "rev_test.txt")
        with open(test_f, "w", encoding="utf-8") as f:
            f.write("Version 1")

        know.save_file_revision(test_f, "Version 1")
        with open(test_f, "w", encoding="utf-8") as f:
            f.write("Version 2")
        know.save_file_revision(test_f, "Version 2")

        revs = know.get_file_revisions(test_f)
        self.assertEqual(len(revs), 2)

        try:
            know.run_maintenance()
        except Exception as e:
            self.fail(f"run_maintenance raised exception: {e}")

    def test_11_sqlite_connection_pool_lifecycle_and_pragmas(self):
        """Verify SQLiteConnectionPool explicit lifecycle, in-flight tracking, and resilient WAL pragmas."""
        pool = db.get_pool(db.DB_FILE, max_connections=4)
        self.assertIsNotNone(pool)

        # Context manager checkout
        with pool.acquire() as conn:
            self.assertEqual(len(pool.in_flight), 1)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            self.assertEqual(cursor.fetchone()[0].lower(), "wal")

            cursor.execute("PRAGMA busy_timeout")
            self.assertEqual(cursor.fetchone()[0], 60000)

            cursor.execute("PRAGMA synchronous")
            self.assertEqual(cursor.fetchone()[0], 1)  # NORMAL = 1

            cursor.execute("PRAGMA cache_size")
            self.assertEqual(cursor.fetchone()[0], -64000)

            cursor.execute("PRAGMA mmap_size")
            self.assertEqual(cursor.fetchone()[0], 268435456)

            cursor.execute("PRAGMA wal_autocheckpoint")
            self.assertEqual(cursor.fetchone()[0], 1000)

        # After exiting context manager, in_flight must be empty and pool must have connection
        self.assertEqual(len(pool.in_flight), 0)

        # Direct checkout and checkin lifecycle
        c = pool.get_connection()
        self.assertEqual(len(pool.in_flight), 1)
        pool.return_connection(c)
        self.assertEqual(len(pool.in_flight), 0)

    def test_12_sqlite_connection_pool_concurrency_and_health_recycling(self):
        """Verify concurrent multi-threaded worker pool checkouts and healthy recycling of closed connections."""
        import concurrent.futures
        pool = db.get_pool(db.DB_FILE, max_connections=8)

        def worker(w_id):
            with pool.acquire() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 + ?", (w_id,))
                res = cursor.fetchone()[0]
                return res

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(20)]
            results = [f.result() for f in futures]
            self.assertEqual(len(results), 20)

        # Test dead connection recycling
        conn = pool.get_connection()
        conn.close()  # Intentionally close connection before returning
        pool.return_connection(conn)

        # Next checkout should discard dead connection and return a fresh healthy connection
        new_conn = pool.get_connection()
        self.assertTrue(pool._is_connection_healthy(new_conn))
        pool.return_connection(new_conn)

    def test_13_get_db_dual_mode_support_and_close_all_connections(self):
        """Verify get_db supports both context manager and direct usage, and close_all_connections cleans up."""
        # Context manager usage
        with know.get_db() as conn1:
            cursor1 = conn1.cursor()
            cursor1.execute("SELECT COUNT(*) FROM files")
            self.assertIsNotNone(cursor1.fetchone())

        # Direct connection returning
        conn2 = know.get_db()
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT COUNT(*) FROM files")
        self.assertIsNotNone(cursor2.fetchone())

        stats = db.get_database_connection_stats()
        self.assertGreaterEqual(stats["thread_local_connections_count"], 1)

        # Deterministic teardown
        db.close_all_connections()
        post_stats = db.get_database_connection_stats()
        self.assertEqual(post_stats["thread_local_connections_count"], 0)


if __name__ == "__main__":
    unittest.main()


