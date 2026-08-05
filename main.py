"""
Backward-compatibility root entrypoint shim for FastAPI server and test suite re-exports.
"""

import os
import sys
import time
import json
import sqlite3
import threading
from contextlib import contextmanager

from src.app.server import app
from src.infrastructure.database import get_db
import src.infrastructure.database as _infra_db
from src.shared.security import verify_path_containment, get_file_acl
from src.shared.regex import RE_NEAR_SYNTAX, RE_TOKEN_SPLIT, RE_SIZE_OP, RE_FTS_CLEAN, RE_WIKILINKS
from src.core.domain.services import (
    parse_query_operators,
    suggest_tags_from_text,
    generate_summary,
    generate_key_takeaways,
    extract_ai_tags,
    reciprocal_rank_fusion,
    generate_hyde_expansion,
    sanitise_fts_query,
)

class _MainModule(sys.modules[__name__].__class__):
    @property
    def DB_FILE(self):
        return _infra_db.DB_FILE

    @DB_FILE.setter
    def DB_FILE(self, value):
        _infra_db.DB_FILE = value

    @property
    def _db_version(self):
        return _infra_db._db_version

    @_db_version.setter
    def _db_version(self, value):
        _infra_db._db_version = value

sys.modules[__name__].__class__ = _MainModule

ACTIVE_DIR = "dumps"
is_testing = True

_llm_lock = threading.Lock()
try:
    import llama_cpp
    Llama = llama_cpp.Llama
except Exception:
    Llama = None

@contextmanager
def db_conn():
    conn = sqlite3.connect(_infra_db.DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class QueryCache:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        self.mem_cache = {}
        self.cache = self.mem_cache

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
                    cursor.execute("SELECT response_json FROM query_cache WHERE query_key = ?", (key,))
                    row = cursor.fetchone()
                    if row:
                        val = json.loads(row[0])
                        self.mem_cache[key] = val
                        self.hits += 1
                        return val
            except Exception:
                pass
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
                    conn.commit()
            except Exception:
                pass

    def invalidate(self):
        with self.lock:
            self.mem_cache.clear()
            try:
                with db_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM query_cache")
                    conn.commit()
            except Exception:
                pass

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
            except Exception:
                pass
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio": hit_ratio,
                "cache_size": size,
            }

    stats = get_stats

GLOBAL_QUERY_CACHE = QueryCache()

def get_llm():
    if Llama is None:
        return None
    try:
        model_path = os.environ.get("LLM_MODEL_PATH", "models/llama-2-7b.Q4_K_M.gguf")
        if os.path.exists(model_path):
            return Llama(model_path=model_path, n_ctx=2048, verbose=False)
        return Llama(model_path=model_path, verbose=False)
    except Exception:
        pass
    return None

def get_fallback_llm():
    return get_llm()

def expand_query_with_llm(query: str) -> str:
    return query

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    start_port = int(os.environ.get("PORT", 8085))
    for p in range(start_port, start_port + 10):
        try:
            print(f"Starting Uroboros server on http://{host}:{p}")
            uvicorn.run(app, host=host, port=p)
            break
        except OSError as e:
            if getattr(e, 'errno', None) in (10048, 98):
                print(f"Port {p} in use, retrying on port {p + 1}...")
                continue
            raise
