"""
Zero-dependency live system health & OS resource telemetry engine.
Gathers Python GC stats, process memory allocations, and SQLite DB page metrics.
"""

import gc
import sys
import os
import time
import sqlite3
from typing import Dict, Any


from functools import lru_cache

@lru_cache(maxsize=2)
def _get_cached_db_counts(cache_epoch: int) -> tuple:
    from src.infrastructure.database import get_db
    f_cnt, c_cnt, t_cnt = 0, 0, 0
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            row_f = cursor.fetchone()
            f_cnt = row_f[0] if row_f else 0

            try:
                cursor.execute("SELECT COUNT(*) FROM file_chunks")
                row_c = cursor.fetchone()
                c_cnt = row_c[0] if row_c else 0
            except Exception:
                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                row_c = cursor.fetchone()
                c_cnt = row_c[0] if row_c else 0

            cursor.execute("SELECT COUNT(*) FROM tags")
            row_t = cursor.fetchone()
            t_cnt = row_t[0] if row_t else 0
    except Exception:
        pass
    return f_cnt, c_cnt, t_cnt

def gather_system_telemetry() -> Dict[str, Any]:
    """
    Returns real-time OS, Python runtime, and SQLite connection pool telemetry.
    Zero-dependency stdlib implementation.
    """
    try:
        from src.infrastructure.database import DB_FILE, get_db

        # 1. Python GC Telemetry
        gc_stats = gc.get_stats()
        gc_counts = gc.get_count()
        allocated_blocks = sys.getallocatedblocks() if hasattr(sys, "getallocatedblocks") else 0

        # 2. SQLite Database File Telemetry
        db_size_bytes = 0
        wal_size_bytes = 0
        if DB_FILE and os.path.exists(DB_FILE):
            db_size_bytes = os.path.getsize(DB_FILE)
            wal_file = DB_FILE + "-wal"
            if os.path.exists(wal_file):
                wal_size_bytes = os.path.getsize(wal_file)

        # 3. Database Record Counts (Cached 15s)
        cache_epoch = int(time.time() // 15)
        files_count, chunks_count, tags_count = _get_cached_db_counts(cache_epoch)

        # 4. Engine & State Telemetry
        import threading
        active_threads = threading.active_count()
        cache_stats = {}
        try:
            from src.core.state import GLOBAL_QUERY_CACHE
            cache_stats = {
                "exact_cache_entries": len(GLOBAL_QUERY_CACHE.cache),
                "semantic_cache_entries": len(GLOBAL_QUERY_CACHE.semantic_cache)
            }
        except Exception:
            pass

        return {
            "runtime": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
                "uptime_timestamp": time.time(),
                "allocated_memory_blocks": allocated_blocks,
                "active_threads": active_threads
            },
            "garbage_collector": {
                "generation_counts": gc_counts,
                "collections_stats": gc_stats
            },
            "cache": cache_stats,
            "database": {
                "db_file": DB_FILE,
                "db_size_bytes": db_size_bytes,
                "db_size_mb": round(db_size_bytes / (1024.0 * 1024.0), 2),
                "wal_size_bytes": wal_size_bytes,
                "wal_size_mb": round(wal_size_bytes / (1024.0 * 1024.0), 2),
                "files_count": files_count,
                "chunks_count": chunks_count,
                "tags_count": tags_count
            },
            "status": "healthy"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Backward-compatible alias
get_system_telemetry = gather_system_telemetry
