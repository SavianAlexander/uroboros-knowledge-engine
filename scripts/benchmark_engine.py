import sys
import os

# Add root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import time
import know
import main

def run_benchmark():
    print("==========================================")
    print("  UROBOROS SYSTEM BENCHMARK SUITE")
    print("==========================================")

    # 1. Database Read Speed Benchmark
    t0 = time.time()
    conn = know.get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM files")
    count = c.fetchone()[0]
    conn.close()
    t1 = time.time()
    print(f"[1] Database Connection & Count ({count} files): {(t1 - t0) * 1000:.2f} ms")

    # 2. FTS Keyword Search Latency
    t0 = time.time()
    res_fts = know.search_files("science")
    t1 = time.time()
    items = res_fts.get("results", []) if isinstance(res_fts, dict) else (res_fts or [])
    print(f"[2] FTS5 Keyword Search ('science'): {(t1 - t0) * 1000:.2f} ms | Matches: {len(items)}")

    # 3. MiniVectorEngine Semantic Search Latency
    t0 = time.time()
    res_sem1 = know.MiniVectorEngine.search_semantic("quantum physics")
    t1 = time.time()
    res_sem2 = know.MiniVectorEngine.search_semantic("quantum physics")
    t2 = time.time()
    print(f"[3] Semantic Vector Search ('quantum physics'):")
    print(f"    - Cold Run: {(t1 - t0) * 1000:.2f} ms | Matches: {len(res_sem1)}")
    print(f"    - Warm/Cached Run: {(t2 - t1) * 1000:.2f} ms | Matches: {len(res_sem2)}")

    # 4. FTS Query Sanitizer (10,000 Ops)
    t0 = time.time()
    for _ in range(10000):
        main.sanitise_fts_query("quantum OR science NOT physics NEAR(test, 5)")
    t1 = time.time()
    print(f"[4] FTS Query Sanitizer (10,000 ops): {(t1 - t0) * 1000:.2f} ms ({(t1 - t0) / 10000 * 1000:.4f} ms/op)")

    print("==========================================")
    print("  BENCHMARK COMPLETE - ALL SYSTEMS OK")
    print("==========================================")

if __name__ == "__main__":
    run_benchmark()
