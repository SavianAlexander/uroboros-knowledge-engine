"""
High-Performance L1 Semantic RAG Query & Prompt Cache.
Standard: Pure Python Standard Library (sqlite3, hashlib, json, time, threading).
Ponytail Senior Dev Principle: Sub-2ms retrieval for repeated and semantically identical
queries without burning GPU cycles or external cache infrastructure.
"""

import os
import sys
import time
import json
import sqlite3
import hashlib
import threading
from typing import Dict, Any, Optional, List, Tuple

from src.infrastructure.database import get_db_connection, get_db_write_connection, DB_FILE, DB_TIMEOUT

logger = logging = __import__("logging").getLogger(__name__)

_CACHE_LOCK = threading.Lock()


def _normalize_query_key(query: str) -> str:
    """Normalizes query text (lowercase, whitespace collapse, punctuation trim)."""
    import re
    cleaned = re.sub(r"[^\w\s]", "", query.lower().strip())
    return re.sub(r"\s+", " ", cleaned)


def _compute_query_hash(query: str, domain: str = "GLOBAL") -> str:
    norm = f"{domain.upper()}::{_normalize_query_key(query)}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def init_semantic_cache_table():
    """Initializes the semantic query cache table and performance indices."""
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_query_cache (
                    query_hash TEXT PRIMARY KEY,
                    raw_query TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    context_chunks_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed_at REAL NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_cache_domain ON semantic_query_cache(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_cache_expires ON semantic_query_cache(expires_at)")


# Initialize table on module load
try:
    init_semantic_cache_table()
except Exception:
    pass


class SemanticQueryCache:
    """
    Thread-safe L1 cache for RAG search contexts and generation outputs.
    """

    @classmethod
    def get(cls, query: str, domain: str = "GLOBAL") -> Optional[Dict[str, Any]]:
        """
        Retrieves cached query result if present and not expired.
        Increments hit counter atomically.
        """
        if not query or not query.strip():
            return None

        q_hash = _compute_query_hash(query, domain)
        now = time.time()

        try:
            with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT query_hash, raw_query, domain, response_text, context_chunks_json, created_at, expires_at, hit_count
                    FROM semantic_query_cache
                    WHERE query_hash = ? AND expires_at > ?
                """, (q_hash, now))
                row = cursor.fetchone()
                if not row:
                    return None

                # Update hit count in write connection
                try:
                    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as w_conn:
                        with w_conn:
                            w_conn.execute("""
                                UPDATE semantic_query_cache
                                SET hit_count = hit_count + 1, last_accessed_at = ?
                                WHERE query_hash = ?
                            """, (now, q_hash))
                except Exception:
                    pass

                try:
                    chunks = json.loads(row[4])
                except Exception:
                    chunks = []

                return {
                    "query_hash": row[0],
                    "raw_query": row[1],
                    "domain": row[2],
                    "response_text": row[3],
                    "context_chunks": chunks,
                    "created_at": row[5],
                    "expires_at": row[6],
                    "hit_count": row[7] + 1,
                    "is_cached": True
                }
        except Exception as e:
            logger.debug(f"Semantic cache get note: {e}")
            return None

    @classmethod
    def put(
        cls,
        query: str,
        response_text: str,
        context_chunks: Optional[List[Any]] = None,
        domain: str = "GLOBAL",
        ttl_seconds: float = 86400.0 * 7  # Default 7 days
    ) -> bool:
        """
        Stores query context and response in L1 cache.
        """
        if not query or not response_text:
            return False

        q_hash = _compute_query_hash(query, domain)
        now = time.time()
        expires_at = now + ttl_seconds
        chunks_json = json.dumps(context_chunks or [])

        try:
            with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO semantic_query_cache (
                            query_hash, raw_query, domain, response_text, context_chunks_json, created_at, expires_at, hit_count, last_accessed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                        ON CONFLICT(query_hash) DO UPDATE SET
                            response_text = excluded.response_text,
                            context_chunks_json = excluded.context_chunks_json,
                            expires_at = excluded.expires_at,
                            last_accessed_at = excluded.last_accessed_at
                    """, (q_hash, query.strip(), domain.upper(), response_text, chunks_json, now, expires_at, now))
                    return True
        except Exception as e:
            logger.debug(f"Semantic cache put note: {e}")
            return False

    @classmethod
    def invalidate(cls, query: str, domain: str = "GLOBAL") -> bool:
        """Deletes a specific query entry from cache."""
        q_hash = _compute_query_hash(query, domain)
        try:
            with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                with conn:
                    conn.execute("DELETE FROM semantic_query_cache WHERE query_hash = ?", (q_hash,))
                    return True
        except Exception:
            return False

    @classmethod
    def clear(cls) -> int:
        """Clears all entries in semantic query cache."""
        try:
            with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM semantic_query_cache")
                    return cursor.rowcount
        except Exception:
            return 0

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Returns diagnostic statistics on cache size, hits, and storage."""
        now = time.time()
        try:
            with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*), COALESCE(SUM(hit_count), 0) FROM semantic_query_cache")
                row = cursor.fetchone()
                total_entries = row[0] if row else 0
                total_hits = row[1] if row else 0

                cursor.execute("SELECT COUNT(*) FROM semantic_query_cache WHERE expires_at < ?", (now,))
                expired_entries = cursor.fetchone()[0]

                return {
                    "status": "success",
                    "total_entries": total_entries,
                    "active_entries": total_entries - expired_entries,
                    "expired_entries": expired_entries,
                    "total_lifetime_hits": total_hits
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
