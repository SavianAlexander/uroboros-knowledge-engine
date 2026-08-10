"""
Challenger 4 Empirical Benchmark Verification Script.
Empirically benchmarks all 4 REST endpoints:
- /api/analytics/overview
- /api/analytics/storage
- /api/analytics/tags
- /api/analytics/search-activity

States:
1. Empty SQLite DB state.
2. Large synthetic dataset (10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs).

Measures both REST TestClient Endpoint Latency and Direct Engine Latency (p50, p95, p99, max).
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import math
import tempfile
import sqlite3

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


def calculate_percentiles(latencies_ms):
    if not latencies_ms:
        return {"min": 0.0, "mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0}
    sorted_l = sorted(latencies_ms)
    n = len(sorted_l)
    def percentile(p):
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


def populate_large_dataset(db_file):
    print("\n[CHALLENGER-4] Populating 10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs...")
    start_time = time.time()
    know.reset_db_connections()

    with get_db_connection(db_file, timeout=30.0) as conn:
        cur = conn.cursor()

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
            sha256 = f"sha256_mock_hash_{i}"
            mod_time = 1700000000.0 + i
            content = f"Synthetic content for document {i} in directory dir_{dir_idx}"
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

        chunks_data = []
        for i in range(1, 50001):
            file_id = (i % 10000) + 1
            chunk_index = i // 10000
            content = f"Synthetic chunk {i} content text sample for file {file_id}"
            chunks_data.append((i, file_id, chunk_index, content))

        cur.executemany("""
            INSERT INTO file_chunks (id, file_id, chunk_index, content)
            VALUES (?, ?, ?, ?)
        """, chunks_data)

        tags_data = []
        for file_id in range(1, 10001):
            for t_idx in range(10):
                tag_num = ((file_id * 7) + (t_idx * 13)) % 300
                tag_str = f"tag_{tag_num}"
                tags_data.append((file_id, tag_str))

        cur.executemany("""
            INSERT OR IGNORE INTO tags (file_id, tag)
            VALUES (?, ?)
        """, tags_data)

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
    print(f"[CHALLENGER-4] Populated synthetic dataset in {duration:.2f}s.")


def run_benchmark(client, db_file, state_label, num_iterations=50):
    endpoints = {
        "/api/analytics/overview": lambda: get_indexing_overview(db_file),
        "/api/analytics/storage": lambda: get_storage_breakdown(db_file),
        "/api/analytics/tags": lambda: get_tag_distribution(db_file),
        "/api/analytics/search-activity": lambda: get_search_activity(db_file)
    }

    report_data = {}

    for url, func in endpoints.items():
        # REST Endpoint Uncached
        api_uncached = []
        for _ in range(num_iterations):
            clear_analytics_cache()
            t0 = time.perf_counter()
            resp = client.get(url)
            t1 = time.perf_counter()
            assert resp.status_code == 200, f"Endpoint {url} returned status {resp.status_code}"
            api_uncached.append((t1 - t0) * 1000.0)

        # REST Endpoint Cached
        api_cached = []
        client.get(url) # Prime
        for _ in range(num_iterations):
            t0 = time.perf_counter()
            resp = client.get(url)
            t1 = time.perf_counter()
            assert resp.status_code == 200
            api_cached.append((t1 - t0) * 1000.0)

        # Direct Engine Uncached
        engine_uncached = []
        for _ in range(num_iterations):
            clear_analytics_cache()
            t0 = time.perf_counter()
            func()
            t1 = time.perf_counter()
            engine_uncached.append((t1 - t0) * 1000.0)

        # Direct Engine Cached
        engine_cached = []
        func() # Prime
        for _ in range(num_iterations):
            t0 = time.perf_counter()
            func()
            t1 = time.perf_counter()
            engine_cached.append((t1 - t0) * 1000.0)

        report_data[url] = {
            "api_uncached": calculate_percentiles(api_uncached),
            "api_cached": calculate_percentiles(api_cached),
            "engine_uncached": calculate_percentiles(engine_uncached),
            "engine_cached": calculate_percentiles(engine_cached)
        }

    return report_data


def main():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "challenger_knowledge.db")
    original_db = know.DB_FILE
    know.DB_FILE = db_file
    know.init_db()
    clear_analytics_cache()
    client = TestClient(app)

    try:
        print("\n=======================================================")
        print("BENCHMARK STATE 1: EMPTY DATABASE")
        print("=======================================================")
        empty_results = run_benchmark(client, db_file, "EMPTY_DB", num_iterations=50)

        print("\n=======================================================")
        print("BENCHMARK STATE 2: LARGE SYNTHETIC DATASET")
        print("=======================================================")
        populate_large_dataset(db_file)
        large_results = run_benchmark(client, db_file, "LARGE_DB", num_iterations=50)

        print("\nSUMMARY RESULTS:")
        print("--- Empty Database State ---")
        for url, data in empty_results.items():
            u = data["api_uncached"]
            c = data["api_cached"]
            eu = data["engine_uncached"]
            ec = data["engine_cached"]
            print(f"REST {url} | Uncached: p50={u['p50']}ms, p95={u['p95']}ms, p99={u['p99']}ms | Cached: p50={c['p50']}ms, p95={c['p95']}ms, p99={c['p99']}ms")
            print(f"Engine {url} | Uncached: p50={eu['p50']}ms, p95={eu['p95']}ms, p99={eu['p99']}ms | Cached: p50={ec['p50']}ms, p95={ec['p95']}ms, p99={ec['p99']}ms")

        print("\n--- Large Synthetic Dataset State ---")
        for url, data in large_results.items():
            u = data["api_uncached"]
            c = data["api_cached"]
            eu = data["engine_uncached"]
            ec = data["engine_cached"]
            print(f"REST {url} | Uncached: p50={u['p50']}ms, p95={u['p95']}ms, p99={u['p99']}ms | Cached: p50={c['p50']}ms, p95={c['p95']}ms, p99={c['p99']}ms")
            print(f"Engine {url} | Uncached: p50={eu['p50']}ms, p95={eu['p95']}ms, p99={eu['p99']}ms | Cached: p50={ec['p50']}ms, p95={ec['p95']}ms, p99={ec['p99']}ms")

    finally:
        know.reset_db_connections()
        know.DB_FILE = original_db
        clear_analytics_cache()

if __name__ == "__main__":
    main()
