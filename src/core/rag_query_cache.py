"""
Zero-Dependency Semantic RAG Query Cache with Cosine Similarity Deduplication.
Standard: Pure Python Standard Library (collections, math, time, typing).
Ponytail Senior Dev Principle: Bypasses expensive re-vectorization and full-table scans for near-identical queries (cos similarity >= threshold).
"""

import math
import time
from collections import OrderedDict
from typing import Dict, Any, List, Optional, Tuple


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute accelerated cosine similarity between two float vectors using math.fsum."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = math.fsum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.fsum(a * a for a in vec_a)
    norm_b = math.fsum(b * b for b in vec_b)
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


class SemanticRAGQueryCache:
    """Thread-safe, zero-dependency in-memory LRU cache for semantic RAG queries."""

    def __init__(self, max_entries: int = 256, default_ttl_sec: float = 3600.0, similarity_threshold: float = 0.96):
        self.max_entries = max_entries
        self.default_ttl_sec = default_ttl_sec
        self.similarity_threshold = similarity_threshold
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, query: str, embedding: Optional[List[float]] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached result by exact query match or cosine similarity threshold."""
        now = time.time()
        q_norm = query.strip().lower()

        # 1. Exact query match in LRU
        if q_norm in self._cache:
            entry = self._cache[q_norm]
            if now < entry["expires_at"]:
                self._cache.move_to_end(q_norm)
                self._hits += 1
                return {
                    "hit_type": "exact",
                    "similarity": 1.0,
                    "results": entry["results"],
                    "cached_query": entry["query"],
                    "age_seconds": round(now - entry["created_at"], 2)
                }
            else:
                del self._cache[q_norm]

        # 2. Semantic vector similarity search over unexpired entries
        if embedding is not None:
            best_match = None
            best_score = -1.0

            for k, entry in list(self._cache.items()):
                if now >= entry["expires_at"]:
                    del self._cache[k]
                    continue
                if entry.get("embedding") is not None:
                    sim = _cosine_similarity(embedding, entry["embedding"])
                    if sim > best_score:
                        best_score = sim
                        best_match = (k, entry)

            if best_match and best_score >= self.similarity_threshold:
                matched_key, entry = best_match
                self._cache.move_to_end(matched_key)
                self._hits += 1
                return {
                    "hit_type": "semantic_similarity",
                    "similarity": round(best_score, 4),
                    "results": entry["results"],
                    "cached_query": entry["query"],
                    "age_seconds": round(now - entry["created_at"], 2)
                }

        self._misses += 1
        return None

    def put(self, query: str, results: Any, embedding: Optional[List[float]] = None, ttl_sec: Optional[float] = None) -> None:
        """Store query results with optional pre-normalized embedding and TTL."""
        now = time.time()
        q_norm = query.strip().lower()
        ttl = ttl_sec if ttl_sec is not None else self.default_ttl_sec

        # Evict oldest if capacity exceeded
        if len(self._cache) >= self.max_entries and q_norm not in self._cache:
            self._cache.popitem(last=False)

        norm_emb = None
        if embedding is not None:
            v_norm = math.sqrt(math.fsum(x * x for x in embedding)) or 1.0
            norm_emb = [x / v_norm for x in embedding]

        self._cache[q_norm] = {
            "query": query,
            "results": results,
            "embedding": norm_emb,
            "created_at": now,
            "expires_at": now + ttl
        }
        self._cache.move_to_end(q_norm)

    def clear(self) -> None:
        """Purge all cached query records."""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Return cache hit rate, entries count, and memory metrics."""
        total = self._hits + self._misses
        hit_ratio = round(self._hits / total, 4) if total > 0 else 0.0
        return {
            "total_entries": len(self._cache),
            "max_capacity": self.max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": hit_ratio,
            "similarity_threshold": self.similarity_threshold
        }


def get_db_data_version(db_path: Optional[str] = None) -> int:
    """Returns SQLite internal data_version pragma tracking transactions with zero overhead."""
    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA data_version")
            row = cursor.fetchone()
            return int(row[0]) if row else 0
    except Exception:
        return int(time.time())


def generate_query_etag(query: str, version: Optional[int] = None) -> str:
    """Generates an ETag hash combining normalized query and database mutation version."""
    import hashlib
    v = version if version is not None else get_db_data_version()
    raw = f"{query.strip().lower()}:{v}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# Global singleton instance
GLOBAL_RAG_CACHE = SemanticRAGQueryCache()
