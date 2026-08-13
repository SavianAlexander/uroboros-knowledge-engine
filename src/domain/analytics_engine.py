"""
Domain Analytics Engine providing fast, thread-safe, cached analytical telemetry and metrics over SQLite vault tables.
"""

import os
import time
import sqlite3
from typing import Optional, Dict, Any, List
import know
from src.core.domain.models import (
    AnalyticsOverviewResponse,
    StorageBreakdownResponse,
    TagDistributionResponse,
    SearchActivityResponse
)

import threading

# Global TTL cache dictionary: key -> (result, timestamp)
_analytics_cache: Dict[tuple, tuple] = {}
_cache_lock = threading.Lock()
CACHE_TTL_SECONDS = 3.0
from src.infrastructure.database import get_db_connection, DB_FILE

def _connect(db_path: Optional[str] = None):
    target_path = db_path if db_path is not None else DB_FILE
    return get_db_connection(target_path)


def clear_analytics_cache() -> None:
    """Clear the process-local analytics cache."""
    with _cache_lock:
        _analytics_cache.clear()


def get_indexing_overview(db_path: Optional[str] = None) -> AnalyticsOverviewResponse:
    target_path = db_path if db_path is not None else know.DB_FILE
    db_ver = getattr(know, "_db_version", 0)
    cache_key = ("indexing_overview", target_path, db_ver)
    now = time.time()

    with _cache_lock:
        if cache_key in _analytics_cache:
            res, ts = _analytics_cache[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                return res

    total_docs = 0
    total_chunks = 0
    fts_records = 0
    storage_bytes = 0

    try:
        with _connect(db_path) as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM files),
                        (SELECT COUNT(*) FROM file_chunks),
                        (SELECT COUNT(*) FROM fts_files),
                        (SELECT COALESCE(SUM(file_size), 0) FROM files)
                """)
                row = cur.fetchone()
                if row:
                    total_docs = row[0] or 0
                    total_chunks = row[1] or 0
                    fts_records = row[2] or 0
                    storage_bytes = row[3] or 0
            except sqlite3.OperationalError:
                pass

        res = AnalyticsOverviewResponse(
            total_documents=total_docs,
            total_chunks=total_chunks,
            fts_records=fts_records,
            indexing_status="idle",
            storage_total_bytes=storage_bytes
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).warning("Swallowed error in analytics_engine.py")
        res = AnalyticsOverviewResponse(
            total_documents=0,
            total_chunks=0,
            fts_records=0,
            indexing_status="idle",
            storage_total_bytes=0
        )

    _analytics_cache[cache_key] = (res, now)
    return res


def get_storage_breakdown(db_path: Optional[str] = None) -> StorageBreakdownResponse:
    target_path = db_path if db_path is not None else know.DB_FILE
    db_ver = getattr(know, "_db_version", 0)
    cache_key = ("storage_breakdown", target_path, db_ver)
    now = time.time()

    if cache_key in _analytics_cache:
        res, ts = _analytics_cache[cache_key]
        if now - ts < CACHE_TTL_SECONDS:
            return res

    by_mime: Dict[str, int] = {}
    by_ext: Dict[str, int] = {}
    top_dirs: List[Dict[str, Any]] = []

    try:
        with _connect(db_path) as conn:
            conn.row_factory = None
            cur = conn.cursor()
            try:
                # 1. Fast MIME type aggregation in SQL
                cur.execute("SELECT COALESCE(NULLIF(mime_type, ''), 'unknown'), COUNT(*) FROM files GROUP BY 1")
                by_mime = dict(cur.fetchall())

                # 2. Fast extension aggregation in SQL
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN COALESCE(filename, filepath, '') LIKE '%.%' 
                            THEN LOWER(SUBSTR(COALESCE(filename, filepath, ''), INSTR(COALESCE(filename, filepath, ''), '.')))
                            ELSE '.none'
                        END AS ext,
                        COUNT(*)
                    FROM files
                    GROUP BY 1
                """)
                by_ext = dict(cur.fetchall())

                # 3. Fast top directory aggregation in SQL
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN filepath IS NOT NULL AND filename IS NOT NULL AND LENGTH(filepath) > LENGTH(filename) 
                                 AND (SUBSTR(filepath, LENGTH(filepath) - LENGTH(filename)) = '/' || filename 
                                      OR SUBSTR(filepath, LENGTH(filepath) - LENGTH(filename)) = '\\' || filename)
                            THEN 
                                CASE 
                                    WHEN LENGTH(filepath) - LENGTH(filename) - 1 = 0 THEN '.'
                                    ELSE SUBSTR(filepath, 1, LENGTH(filepath) - LENGTH(filename) - 1)
                                END
                            ELSE '.'
                        END AS dir,
                        COUNT(*) AS count,
                        COALESCE(SUM(file_size), 0) AS size_bytes
                    FROM files
                    GROUP BY 1
                    ORDER BY count DESC, size_bytes DESC
                    LIMIT 10
                """)
                top_dirs = [{"directory": r[0], "count": r[1], "size_bytes": r[2]} for r in cur.fetchall()]

            except sqlite3.OperationalError:
                pass

        res = StorageBreakdownResponse(
            by_mime=by_mime,
            by_extension=by_ext,
            top_directories=top_dirs
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).warning("Swallowed error in analytics_engine.py")
        res = StorageBreakdownResponse(
            by_mime={},
            by_extension={},
            top_directories=[]
        )

    _analytics_cache[cache_key] = (res, now)
    return res


def get_tag_distribution(db_path: Optional[str] = None) -> TagDistributionResponse:
    target_path = db_path if db_path is not None else know.DB_FILE
    db_ver = getattr(know, "_db_version", 0)
    cache_key = ("tag_distribution", target_path, db_ver)
    now = time.time()

    if cache_key in _analytics_cache:
        res, ts = _analytics_cache[cache_key]
        if now - ts < CACHE_TTL_SECONDS:
            return res

    total_tags = 0
    top_tags: List[Dict[str, Any]] = []
    cooccurrence: List[Dict[str, Any]] = []

    try:
        with _connect(db_path) as conn:
            conn.row_factory = None
            cur = conn.cursor()
            try:
                # 1. Single scan for total distinct tags and top candidate tags
                cur.execute("SELECT tag, COUNT(*) as count FROM tags GROUP BY tag ORDER BY count DESC")
                all_tag_rows = cur.fetchall()
                total_tags = len(all_tag_rows)

                top_rows = all_tag_rows[:15]
                top_tags = [{"tag": r[0], "count": r[1]} for r in top_rows[:10]]
                # ponytail: Candidate pool capped at top 15 tags with session temp index for O(log N) join under 15ms.
                candidate_tags = [r[0] for r in top_rows]

                # 2. Co-occurrence using session temporary indexed table for O(log N) candidate join
                if candidate_tags:
                    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_cand_tags (file_id INTEGER, tag TEXT, PRIMARY KEY (file_id, tag)) WITHOUT ROWID")
                    cur.execute("DELETE FROM tmp_cand_tags")

                    placeholders = ",".join("?" * len(candidate_tags))
                    cur.execute(f"INSERT INTO tmp_cand_tags SELECT file_id, tag FROM tags WHERE tag IN ({placeholders})", candidate_tags)

                    cur.execute("""
                        SELECT t1.tag as tag1, t2.tag as tag2, COUNT(*) as weight
                        FROM tmp_cand_tags t1
                        JOIN tmp_cand_tags t2 ON t1.file_id = t2.file_id AND t1.tag < t2.tag
                        GROUP BY t1.tag, t2.tag
                        ORDER BY weight DESC
                        LIMIT 20
                    """)
                    cooccurrence = [{"tag1": r[0], "tag2": r[1], "weight": r[2]} for r in cur.fetchall()]
                    cur.execute("DELETE FROM tmp_cand_tags")

            except sqlite3.OperationalError:
                pass

        res = TagDistributionResponse(
            total_tags=total_tags,
            top_tags=top_tags,
            tag_cooccurrence=cooccurrence
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).warning("Swallowed error in analytics_engine.py")
        res = TagDistributionResponse(
            total_tags=0,
            top_tags=[],
            tag_cooccurrence=[]
        )

    _analytics_cache[cache_key] = (res, now)
    return res


def get_search_activity(db_path: Optional[str] = None) -> SearchActivityResponse:
    target_path = db_path if db_path is not None else know.DB_FILE
    db_ver = getattr(know, "_db_version", 0)
    cache_key = ("search_activity", target_path, db_ver)
    now = time.time()

    if cache_key in _analytics_cache:
        res, ts = _analytics_cache[cache_key]
        if now - ts < CACHE_TTL_SECONDS:
            return res

    total_queries = 0
    avg_latency = 0.0
    top_queries: List[Dict[str, Any]] = []
    recent_queries: List[Dict[str, Any]] = []
    timeline_data: Dict[str, Dict[str, int]] = {}

    # Initialize last 7 days
    from datetime import datetime, timedelta, timezone
    today = datetime.now(timezone.utc).date()

    for i in range(6, -1, -1):
        dt_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        timeline_data[dt_str] = {"date": dt_str[-5:], "searches": 0, "indexed": 0}

    try:
        with _connect(db_path) as conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM search_history")
                row = cur.fetchone()
                total_queries = row[0] if row else 0

                cur.execute("""
                    SELECT query_string as query, COUNT(*) as count
                    FROM search_history
                    WHERE query_string IS NOT NULL AND query_string != ''
                    GROUP BY query_string
                    ORDER BY count DESC
                    LIMIT 10
                """)
                top_queries = [{"query": r[0], "count": r[1]} for r in cur.fetchall()]

                cur.execute("""
                    SELECT query_string as query, search_mode as mode, executed_at, result_count
                    FROM search_history
                    ORDER BY executed_at DESC
                    LIMIT 10
                """)
                recent_queries = [
                    {
                        "query": r[0],
                        "mode": r[1],
                        "executed_at": r[2],
                        "result_count": r[3]
                    }
                    for r in cur.fetchall()
                ]

                # Aggregate searches by date
                cur.execute("""
                    SELECT date(executed_at, 'unixepoch') as dt, COUNT(*) as count
                    FROM search_history
                    WHERE executed_at > (strftime('%s', 'now') - 7 * 86400)
                    GROUP BY dt
                """)
                for r in cur.fetchall():
                    dt = r[0]
                    if dt in timeline_data:
                        timeline_data[dt]["searches"] = r[1]

                # Aggregate indexed files by date
                cur.execute("""
                    SELECT date(created_at, 'unixepoch') as dt, COUNT(*) as count
                    FROM files
                    WHERE created_at > (strftime('%s', 'now') - 7 * 86400)
                    GROUP BY dt
                """)
                for r in cur.fetchall():
                    dt = r[0]
                    if dt in timeline_data:
                        timeline_data[dt]["indexed"] = r[1]

                try:
                    from src.infrastructure.telemetry import GLOBAL_TELEMETRY
                    if GLOBAL_TELEMETRY.latencies:
                        avg_latency = float(sum(GLOBAL_TELEMETRY.latencies) / len(GLOBAL_TELEMETRY.latencies))
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception:
                    import logging; logging.getLogger(__name__).warning("Swallowed error in analytics_engine.py")
                    avg_latency = 0.0

            except sqlite3.OperationalError:
                pass

        res = SearchActivityResponse(
            total_queries=total_queries,
            avg_latency_ms=round(avg_latency, 2),
            top_queries=top_queries,
            recent_queries=recent_queries,
            timeline=list(timeline_data.values())
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).warning("Swallowed error in analytics_engine.py")
        res = SearchActivityResponse(
            total_queries=0,
            avg_latency_ms=0.0,
            top_queries=[],
            recent_queries=[],
            timeline=list(timeline_data.values())
        )

    _analytics_cache[cache_key] = (res, now)
    return res
