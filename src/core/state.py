import os
import json
import time
import sqlite3
import threading
from contextlib import contextmanager
from src.infrastructure.database import DB_FILE, get_db_connection

@contextmanager
def db_conn():
    with get_db_connection(DB_FILE) as conn:
        yield conn

class QueryCache:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        self.mem_cache = {}
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
