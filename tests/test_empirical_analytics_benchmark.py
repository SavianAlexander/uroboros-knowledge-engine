import src.infrastructure.database as db
"""
Empirical Performance Benchmark for Milestone 1 Analytics Endpoints.
Evaluates response latency (p50, p95, p99) under:
1. Empty SQLite DB state.
2. Large synthetic dataset (10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs).
Measures both Direct Engine Function Latency and FastAPI TestClient Endpoint Latency.
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import math
import tempfile
import sqlite3
import unittest
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
import know
from src.app.server import app
from src.domain.analytics_engine import (
    clear_analytics_cache,
    get_indexing_overview,
    get_storage_breakdown,
    get_tag_distribution,
    get_search_activity
)


def calculate_percentiles(latencies_ms: List[float]) -> Dict[str, float]:
    if not latencies_ms:
        return {"min": 0.0, "mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0}
    sorted_l = sorted(latencies_ms)
    n = len(sorted_l)
    def percentile(p: float) -> float:
        idx = (n - 1) * p
        lower = int(math.floor(idx))
        upper = int(math.ceil(idx))
        if lower == upper:
            return sorted_l[lower]
        weight = idx - lower
        return sorted_l[lower] * (1.0 - weight) + sorted_l[upper] * weight

    return {
        "min": round(sorted_l[0], 3),
        "mean": round(sum(sorted_l) / n, 3),
        "p50": round(percentile(0.50), 3),
        "p95": round(percentile(0.95), 3),
        "p99": round(percentile(0.99), 3),
        "max": round(sorted_l[-1], 3)
    }


class TestEmpiricalAnalyticsBenchmark(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "benchmark_knowledge.db")
        self.original_db = db.DB_FILE
        db.DB_FILE = self.db_file
        know.init_db()
        clear_analytics_cache()
        self.client = TestClient(app)

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.original_db
        clear_analytics_cache()

    def populate_large_dataset(self):
        """Populate database with 10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs."""
        print("\n[BENCHMARK] Populating 10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs...")
        start_time = time.time()
        know.reset_db_connections()

        with get_db_connection(self.db_file, timeout=30.0) as conn:
            cur = conn.cursor()

            # 1. Insert 10,000 files
            exts = [".pdf", ".md", ".txt", ".docx", ".png", ".json", ".csv", ".py", ".html", ".xml"]
            mimes = [
                "application/pdf", "text/markdown", "text/plain",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "image/png", "application/json", "text/csv", "text/x-python", "text/html", "application/xml"
            ]

            files_data = []
            fts_data = []
            for i in range(1, 10001):
                idx = i % len(exts)
                ext = exts[idx]
                mime = mimes[idx]
                dir_idx = i % 50
                filepath = f"C:/data/dir_{dir_idx}/file_{i}{ext}"
                filename = f"file_{i}{ext}"
                file_size = (i * 1024) % 500000 + 128
                sha256 = f"sha256_record_hash_{i}"
                mod_time = 1700000000.0 + i
                content = f"Corpus text content for record {i} in directory dir_{dir_idx}"
                files_data.append((i, filepath, filename, file_size, mime, sha256, mod_time, content, "notes sample", "insights sample"))
                fts_data.append((filepath, filename, content, "notes sample"))

            cur.executemany("""
                INSERT INTO files (id, filepath, filename, file_size, mime_type, sha256, modified_at, content, notes, insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, files_data)

            cur.executemany("""
                INSERT INTO fts_files (filepath, filename, content, notes)
                VALUES (?, ?, ?, ?)
            """, fts_data)

            # 2. Insert 50,000 file_chunks
            chunks_data = []
            for i in range(1, 50001):
                file_id = (i % 10000) + 1
                chunk_index = i // 10000
                content = f"Indexed chunk {i} text segment for file {file_id}"
                chunks_data.append((i, file_id, chunk_index, content))

            cur.executemany("""
                INSERT INTO file_chunks (id, file_id, chunk_index, content)
                VALUES (?, ?, ?, ?)
            """, chunks_data)

            # 3. Insert 100,000 tags across 10,000 files
            tags_data = []
            for file_id in range(1, 10001):
                # Assign 10 distinct tags per file from a pool of 300 tags
                for t_idx in range(10):
                    tag_num = ((file_id * 7) + (t_idx * 13)) % 300
                    tag_str = f"tag_{tag_num}"
                    tags_data.append((file_id, tag_str))

            cur.executemany("""
                INSERT OR IGNORE INTO tags (file_id, tag)
                VALUES (?, ?)
            """, tags_data)

            # 4. Insert 5,000 search_history logs
            search_data = []
            modes = ["keyword", "semantic", "hybrid"]
            for i in range(1, 5001):
                query_str = f"search query term {i % 120}"
                mode = modes[i % len(modes)]
                exec_time = 1700000000.0 + (i * 10)
                res_count = i % 50
                search_data.append((i, query_str, mode, exec_time, res_count))

            cur.executemany("""
                INSERT INTO search_history (id, query_string, search_mode, executed_at, result_count)
                VALUES (?, ?, ?, ?, ?)
            """, search_data)

            conn.commit()

        duration = time.time() - start_time
        print(f"[BENCHMARK] Scalability corpus dataset populated in {duration:.2f}s.")

    def run_benchmark_for_state(self, state_label: str, num_iterations: int = 50) -> Dict[str, Dict[str, Any]]:
        endpoints = {
            "overview": ("/api/analytics/overview", lambda: get_indexing_overview(self.db_file)),
            "storage": ("/api/analytics/storage", lambda: get_storage_breakdown(self.db_file)),
            "tags": ("/api/analytics/tags", lambda: get_tag_distribution(self.db_file)),
            "search-activity": ("/api/analytics/search-activity", lambda: get_search_activity(self.db_file))
        }

        results = {}

        for name, (url, func) in endpoints.items():
            # 1. Direct Engine Function Performance
            engine_uncached = []
            for _ in range(num_iterations):
                clear_analytics_cache()
                t0 = time.perf_counter()
                func()
                t1 = time.perf_counter()
                engine_uncached.append((t1 - t0) * 1000.0)

            engine_cached = []
            func() # Prime cache
            for _ in range(num_iterations):
                t0 = time.perf_counter()
                func()
                t1 = time.perf_counter()
                engine_cached.append((t1 - t0) * 1000.0)

            # 2. REST API TestClient Endpoint Performance
            api_uncached = []
            for _ in range(num_iterations):
                clear_analytics_cache()
                t0 = time.perf_counter()
                resp = self.client.get(url)
                t1 = time.perf_counter()
                self.assertEqual(resp.status_code, 200, f"Failed endpoint {url}: {resp.text}")
                api_uncached.append((t1 - t0) * 1000.0)

            api_cached = []
            self.client.get(url) # Prime cache
            for _ in range(num_iterations):
                t0 = time.perf_counter()
                resp = self.client.get(url)
                t1 = time.perf_counter()
                self.assertEqual(resp.status_code, 200)
                api_cached.append((t1 - t0) * 1000.0)

            eng_u_stats = calculate_percentiles(engine_uncached)
            eng_c_stats = calculate_percentiles(engine_cached)
            api_u_stats = calculate_percentiles(api_uncached)
            api_c_stats = calculate_percentiles(api_cached)

            results[name] = {
                "engine_uncached": eng_u_stats,
                "engine_cached": eng_c_stats,
                "api_uncached": api_u_stats,
                "api_cached": api_c_stats
            }

            print(f"\n--- State: {state_label} | Endpoint: GET {url} ---")
            print(f"  [Direct Engine] Uncached: p50={eng_u_stats['p50']}ms | p95={eng_u_stats['p95']}ms | p99={eng_u_stats['p99']}ms | max={eng_u_stats['max']}ms")
            print(f"  [Direct Engine] Cached:   p50={eng_c_stats['p50']}ms | p95={eng_c_stats['p95']}ms | p99={eng_c_stats['p99']}ms | max={eng_c_stats['max']}ms")
            print(f"  [REST Client]   Uncached: p50={api_u_stats['p50']}ms | p95={api_u_stats['p95']}ms | p99={api_u_stats['p99']}ms | max={api_u_stats['max']}ms")
            print(f"  [REST Client]   Cached:   p50={api_c_stats['p50']}ms | p95={api_c_stats['p95']}ms | p99={api_c_stats['p99']}ms | max={api_c_stats['max']}ms")

        return results

    def test_empirical_performance_empty_db(self):
        """Benchmark 1: Empty SQLite Database state."""
        print("\n=======================================================")
        print("RUNNING BENCHMARK 1: EMPTY DATABASE STATE")
        print("=======================================================")
        results = self.run_benchmark_for_state("EMPTY_DB", num_iterations=50)

        # SLA Assertions for Empty DB (Engine level)
        for ep, metrics in results.items():
            p95_uncached = metrics["engine_uncached"]["p95"]
            p99_uncached = metrics["engine_uncached"]["p99"]
            p95_cached = metrics["engine_cached"]["p95"]

            self.assertLess(p95_uncached, 50.0, f"[{ep}] Empty DB engine uncached p95 ({p95_uncached}ms) exceeded 50ms SLA!")
            self.assertLess(p99_uncached, 50.0, f"[{ep}] Empty DB engine uncached p99 ({p99_uncached}ms) exceeded 50ms SLA!")
            self.assertLess(p95_cached, 5.0, f"[{ep}] Empty DB engine cached p95 ({p95_cached}ms) exceeded 5ms SLA!")

    def test_empirical_performance_large_db(self):
        """Benchmark 2: Large Scalability Corpus Dataset state (10k files, 50k chunks, 100k tags, 5k search logs)."""
        print("\n=======================================================")
        print("RUNNING BENCHMARK 2: LARGE 10K CORPUS DATASET STATE")
        print("=======================================================")
        self.populate_large_dataset()
        results = self.run_benchmark_for_state("LARGE_DB", num_iterations=50)

        # SLA Assertions for Large DB (Engine level)
        for ep, metrics in results.items():
            p95_uncached = metrics["engine_uncached"]["p95"]
            p99_uncached = metrics["engine_uncached"]["p99"]
            p95_cached = metrics["engine_cached"]["p95"]

            self.assertLess(p95_uncached, 50.0, f"[{ep}] Large DB engine uncached p95 ({p95_uncached}ms) exceeded 50ms SLA!")
            self.assertLess(p99_uncached, 50.0, f"[{ep}] Large DB engine uncached p99 ({p99_uncached}ms) exceeded 50ms SLA!")
            self.assertLess(p95_cached, 5.0, f"[{ep}] Large DB engine cached p95 ({p95_cached}ms) exceeded 5ms SLA!")


if __name__ == "__main__":
    unittest.main()
