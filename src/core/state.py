import os
import json
import time
import sqlite3
import threading
from contextlib import contextmanager
import math
from src.infrastructure.database import DB_FILE, get_db_connection

@contextmanager
def db_conn():
    with get_db_connection(DB_FILE) as conn:
        yield conn

def cosine_similarity(vec1: list, vec2: list) -> float:
    """Compute cosine similarity between two float vectors using pure standard library."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1)
    norm2 = sum(b * b for b in vec2)
    if norm1 <= 0.0 or norm2 <= 0.0:
        return 0.0
    return dot / (math.sqrt(norm1) * math.sqrt(norm2))

class QueryCache:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        self.mem_cache = {}
        self.semantic_mem_cache = {}
        self.cache = self.mem_cache
        try:
            with db_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS query_cache (query_key TEXT PRIMARY KEY, response_json TEXT, cached_at REAL)")
                conn.commit()
        except Exception:
            pass

    def get(self, key):
        with self.lock:
            if key in self.mem_cache:
                self.hits += 1
                val = self.mem_cache.pop(key)
                self.mem_cache[key] = val
                return val
            try:
                with db_conn() as conn:
                    cursor = conn.cursor()
                    # ponytail: evict stale cache entries older than 1 hour on read
                    cursor.execute("DELETE FROM query_cache WHERE cached_at < ?", (time.time() - 3600,))
                    cursor.execute("SELECT response_json FROM query_cache WHERE query_key = ?", (key,))
                    row = cursor.fetchone()
                    if row:
                        val = json.loads(row[0])
                        self.mem_cache[key] = val
                        self.hits += 1
                        conn.commit()
                        return val
                    conn.commit()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in state.py: {e}")
            self.misses += 1
            return None

    def get_semantic(self, query_text: str, query_embedding: list = None, threshold: float = 0.95):
        """Retrieve cached response via exact key or embedding cosine similarity threshold."""
        exact_res = self.get(query_text)
        if exact_res is not None:
            return exact_res, 1.0

        if not query_embedding:
            try:
                from src.core.embeddings import generate_embedding
                query_embedding = generate_embedding(query_text)
            except Exception:
                query_embedding = None

        if not query_embedding:
            return None, 0.0

        with self.lock:
            best_val = None
            best_sim = 0.0
            for key, entry in self.semantic_mem_cache.items():
                cached_vec = entry.get("embedding")
                if cached_vec:
                    sim = cosine_similarity(query_embedding, cached_vec)
                    if sim > best_sim and sim >= threshold:
                        best_sim = sim
                        best_val = entry.get("value")

            if best_val is not None:
                self.hits += 1
                return best_val, best_sim

        return None, 0.0

    def set_semantic(self, query_text: str, value: any, query_embedding: list = None):
        """Cache response with vector embedding for future semantic lookups."""
        self.set(query_text, value)
        if not query_embedding:
            try:
                from src.core.embeddings import generate_embedding
                query_embedding = generate_embedding(query_text)
            except Exception:
                query_embedding = None

        if query_embedding:
            with self.lock:
                self.semantic_mem_cache[query_text] = {
                    "value": value,
                    "embedding": query_embedding,
                    "cached_at": time.time()
                }
                if len(self.semantic_mem_cache) > self.capacity:
                    self.semantic_mem_cache.pop(next(iter(self.semantic_mem_cache)))

    def set(self, key, value):
        with self.lock:
            self.mem_cache[key] = value
            if len(self.mem_cache) > self.capacity:
                self.mem_cache.pop(next(iter(self.mem_cache)))
            try:
                with db_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM query_cache")
                    count = cursor.fetchone()[0]
                    if count >= self.capacity:
                        cursor.execute("DELETE FROM query_cache WHERE cached_at = (SELECT MIN(cached_at) FROM query_cache)")

                    cursor.execute(
                        "INSERT OR REPLACE INTO query_cache (query_key, response_json, cached_at) VALUES (?, ?, ?)",
                        (key, json.dumps(value), time.time())
                    )
                    cursor.execute("DELETE FROM query_cache WHERE cached_at < ?", (time.time() - 3600,))
                    conn.commit()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in state.py: {e}")

    def invalidate(self):
        with self.lock:
            self.mem_cache.clear()
            self.semantic_mem_cache.clear()
            for attempt in range(5):
                try:
                    with db_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM query_cache")
                        conn.commit()
                        break
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception as e:
                    if attempt == 4:
                        import logging; logging.warning(f"Swallowed error in state.py: {e}")
                    time.sleep(0.1 * (attempt + 1))

    clear = invalidate

    def get_stats(self):
        with self.lock:
            total_requests = self.hits + self.misses
            hit_ratio = (
                round((self.hits / total_requests) * 100, 2)
                if total_requests > 0
                else 0.0
            )
            size = 0
            try:
                with db_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM query_cache")
                    size = cursor.fetchone()[0]
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in state.py: {e}")
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio": hit_ratio,
                "cache_size": size,
            }

    stats = get_stats

GLOBAL_QUERY_CACHE = QueryCache()

from src.core.model_manager import (
    ModelManager,
    _lock as _llm_lock,
    Llama,
    get_llm,
    get_fallback_llm,
    expand_query_with_llm
)
