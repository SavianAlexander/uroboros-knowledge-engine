import unittest
import os
import shutil
import tempfile
import time
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainPerformance(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_perf_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        conn = know.get_db()
        conn.close()

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_db_read_latency_guard(self):
        """Verify database read query latency remains under 5.0ms threshold.

        Preconditions: Active database connection initialized.
        Invariants: Execute SELECT COUNT(*) query on files table and measure wall-clock duration.
        Expected Outcomes: Query execution latency is strictly less than 5.0ms.
        """
        t0 = time.time()
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        _ = cursor.fetchone()
        conn.close()
        t1 = time.time()
        duration_ms = (t1 - t0) * 1000
        self.assertLess(duration_ms, 5.0, f"DB read latency regression: {duration_ms:.2f}ms > 5.0ms")

    def test_02_fts_search_latency_guard(self):
        """Verify FTS full-text search query latency remains under 5.0ms threshold.

        Preconditions: Database FTS index initialized.
        Invariants: Perform search_files call and measure execution time.
        Expected Outcomes: Search latency is strictly less than 5.0ms.
        """
        t0 = time.time()
        res = know.search_files("quantum")
        t1 = time.time()
        duration_ms = (t1 - t0) * 1000
        self.assertLess(duration_ms, 5.0, f"FTS search latency regression: {duration_ms:.2f}ms > 5.0ms")

    def test_03_query_sanitizer_throughput_guard(self):
        """Verify query sanitizer throughput for 1,000 complex FTS query sanitizations.

        Preconditions: Complex FTS query string with operators provided.
        Invariants: Loop 1,000 iterations of sanitise_fts_query and measure elapsed time.
        Expected Outcomes: Total duration for 1,000 operations is strictly less than 2.0ms.
        """
        t0 = time.time()
        for _ in range(1000):
            _ = main.sanitise_fts_query("quantum OR physics NOT mechanics NEAR(test, 5)")
        t1 = time.time()
        duration_ms = (t1 - t0) * 1000
        self.assertLess(duration_ms, 2.0, f"Sanitizer throughput regression: {duration_ms:.2f}ms > 2.0ms")

    def test_04_lru_cache_memoization_benchmarks(self):
        """Verify @lru_cache hit and miss performance counters across core services.

        Preconditions: Clear tag suggestion function LRU cache.
        Invariants: First call produces 1 cache miss; 100 subsequent identical calls hit cache.
        Expected Outcomes: Final cache info reports exactly 1 miss and 100 hits.
        """
        sample_text = "The Uroboros Knowledge Engine provides high-performance document parsing and indexing." * 5
        know.suggest_tags_from_text.cache_clear()

        _ = know.suggest_tags_from_text(sample_text)
        info1 = know.suggest_tags_from_text.cache_info()
        self.assertEqual(info1.misses, 1)

        for _ in range(100):
            _ = know.suggest_tags_from_text(sample_text)

        info2 = know.suggest_tags_from_text.cache_info()
        self.assertEqual(info2.hits, 100)
        self.assertEqual(info2.misses, 1)

if __name__ == "__main__":
    unittest.main()

