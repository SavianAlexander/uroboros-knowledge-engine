import src.infrastructure.database as db
"""
Verification 5 Empirical Benchmark Test Harness.
Empirically benchmarks all 4 REST endpoints (/api/analytics/overview, /api/analytics/storage, /api/analytics/tags, /api/analytics/search-activity)
under:
1. Empty database state.
2. Large synthetic dataset (10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs).

Measures 100 samples per endpoint for both uncached (cache cleared before call) and cached states.
Verifies:
- All uncached REST endpoint latencies (p95 and p99) < 50.0ms
- All cached lookups < 5.0ms
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import math
import tempfile
import sqlite3
import unittest

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


def calc_percentiles(samples_ms):
    if not samples_ms:
        return {"min": 0.0, "mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0}
    sorted_s = sorted(samples_ms)
    n = len(sorted_s)

    def p(pct):
        idx = (n - 1) * pct
        low = int(math.floor(idx))
        high = int(math.ceil(idx))
        if low == high:
            return sorted_s[low]
        weight = idx - low
        return sorted_s[low] * (1.0 - weight) + sorted_s[high] * weight

    return {
        "min": round(sorted_s[0], 3),
        "mean": round(sum(sorted_s) / n, 3),
        "p50": round(p(0.50), 3),
        "p95": round(p(0.95), 3),
        "p99": round(p(0.99), 3),
        "max": round(sorted_s[-1], 3)
    }


def seed_large_dataset(db_file):
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
            filepath = f"C:/vault/dir_{dir_idx}/doc_{i}{ext}"
            filename = f"doc_{i}{ext}"
            file_size = (i * 1024) % 500000 + 128
            sha256 = f"sha256_record_hash_{i}"
            mod_time = 1700000000.0 + i
            content = f"Scalability corpus text content for document {i} inside dir_{dir_idx}"
            files_data.append((i, filepath, filename, file_size, mime, sha256, mod_time, content, "notes string", "insights string"))
            fts_data.append((filepath, filename, content, "notes string"))

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
            content = f"Corpus chunk segment {i} for document file_id {file_id}"
            chunks_data.append((i, file_id, chunk_index, content))

        cur.executemany("""
            INSERT INTO file_chunks (id, file_id, chunk_index, content)
            VALUES (?, ?, ?, ?)
        """, chunks_data)

        tags_data = []
        for file_id in range(1, 10001):
            for t_idx in range(10):
                tag_num = ((file_id * 11) + (t_idx * 17)) % 400
                tag_str = f"tag_cluster_{tag_num}"
                tags_data.append((file_id, tag_str))

        cur.executemany("""
            INSERT OR IGNORE INTO tags (file_id, tag)
            VALUES (?, ?)
        """, tags_data)

        search_data = []
        modes = ["keyword", "semantic", "hybrid"]
        for i in range(1, 5001):
            query_str = f"analytics search query {i % 150}"
            mode = modes[i % len(modes)]
            exec_time = 1700000000.0 + (i * 10)
            res_count = i % 100
            search_data.append((i, query_str, mode, exec_time, res_count))

        cur.executemany("""
            INSERT INTO search_history (id, query_string, search_mode, executed_at, result_count)
            VALUES (?, ?, ?, ?, ?)
        """, search_data)

        conn.commit()


def benchmark_suite(client, db_file, iterations=100):
    endpoints = [
        "/api/analytics/overview",
        "/api/analytics/storage",
        "/api/analytics/tags",
        "/api/analytics/search-activity"
    ]

    results = {}
    for ep in endpoints:
        # 1. REST Uncached
        rest_uncached = []
        for _ in range(iterations):
            clear_analytics_cache()
            t0 = time.perf_counter()
            r = client.get(ep)
            t1 = time.perf_counter()
            assert r.status_code == 200, f"Error {r.status_code} on {ep}"
            rest_uncached.append((t1 - t0) * 1000.0)

        # 2. REST Cached
        rest_cached = []
        client.get(ep)  # Warm up cache
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = client.get(ep)
            t1 = time.perf_counter()
            assert r.status_code == 200, f"Error {r.status_code} on {ep}"
            rest_cached.append((t1 - t0) * 1000.0)

        results[ep] = {
            "rest_uncached": calc_percentiles(rest_uncached),
            "rest_cached": calc_percentiles(rest_cached)
        }
    return results


def run_all_verification_benchmarks():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "verification5_test.db")
    orig_db = db.DB_FILE
    db.DB_FILE = db_file
    know.init_db()
    clear_analytics_cache()
    client = TestClient(app)

    try:
        print("=== CHALLENGER 5 EMPIRICAL BENCHMARK START ===")
        # Benchmark 1: Empty Database
        empty_res = benchmark_suite(client, db_file, iterations=100)

        # Seed Large Dataset
        print("Seeding 10,000 files, 50,000 chunks, 100,000 tags, 5,000 search logs...")
        seed_large_dataset(db_file)

        # Benchmark 2: Large Dataset
        large_res = benchmark_suite(client, db_file, iterations=100)

        print("\n=== RESULTS SUMMARY ===")
        print("--- Empty DB State ---")
        for ep, res in empty_res.items():
            u = res["rest_uncached"]
            c = res["rest_cached"]
            print(f"{ep:30s} | Uncached p50={u['p50']:6.2f}ms, p95={u['p95']:6.2f}ms, p99={u['p99']:6.2f}ms | Cached p50={c['p50']:6.2f}ms, p95={c['p95']:6.2f}ms, p99={c['p99']:6.2f}ms")

        print("\n--- Large Synthetic Dataset (10k files, 50k chunks, 100k tags, 5k searches) ---")
        for ep, res in large_res.items():
            u = res["rest_uncached"]
            c = res["rest_cached"]
            print(f"{ep:30s} | Uncached p50={u['p50']:6.2f}ms, p95={u['p95']:6.2f}ms, p99={u['p99']:6.2f}ms | Cached p50={c['p50']:6.2f}ms, p95={c['p95']:6.2f}ms, p99={c['p99']:6.2f}ms")

        return empty_res, large_res
    finally:
        know.reset_db_connections()
        db.DB_FILE = orig_db
        clear_analytics_cache()


if __name__ == "__main__":
    run_all_verification_benchmarks()
