"""
Agent Episodic Memory & Dynamic Scratchpad Engine.
Standard: Pure Python Standard Library (sqlite3, json, time, typing).
Provides persistent, low-latency key-value memory, episodic execution traces, and context scratchpads for AI agents.
"""

import json
import time
from typing import Dict, Any, List, Optional
from collections import OrderedDict
from src.infrastructure.database import get_db

_MEM_LRU_CACHE: OrderedDict[str, Dict[str, Any]] = OrderedDict()
_MAX_MEM_CACHE_SIZE = 256


def _init_memory_table() -> None:
    """Ensures the agent episodic memory table exists."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                tags TEXT,
                created_at REAL NOT NULL,
                expires_at REAL,
                UNIQUE(session_id, memory_key)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_mem_session ON agent_episodic_memory(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_mem_key ON agent_episodic_memory(session_id, memory_key)")
        conn.commit()


def store_memory(
    session_id: str,
    key: str,
    value: Any,
    tags: Optional[List[str]] = None,
    ttl_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """Stores an episodic memory entry with optional tags and TTL."""
    _init_memory_table()
    now = time.time()
    expires_at = now + ttl_seconds if ttl_seconds is not None else None
    val_json = json.dumps(value) if not isinstance(value, str) else value
    tags_str = ",".join(tags) if tags else ""

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_episodic_memory (session_id, memory_key, memory_value, tags, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id, memory_key) DO UPDATE SET
                memory_value = excluded.memory_value,
                tags = excluded.tags,
                created_at = excluded.created_at,
                expires_at = excluded.expires_at
        """, (session_id, key, val_json, tags_str, now, expires_at))
        conn.commit()

    cache_key = f"{session_id}:{key}"
    _MEM_LRU_CACHE[cache_key] = {"value": value, "tags": tags or [], "created_at": now, "expires_at": expires_at}
    if len(_MEM_LRU_CACHE) > _MAX_MEM_CACHE_SIZE:
        _MEM_LRU_CACHE.popitem(last=False)

    return {"status": "success", "session_id": session_id, "key": key}


def recall_memory(session_id: str, key: str) -> Optional[Any]:
    """Retrieves an episodic memory entry, verifying expiration."""
    _init_memory_table()
    now = time.time()
    cache_key = f"{session_id}:{key}"

    if cache_key in _MEM_LRU_CACHE:
        entry = _MEM_LRU_CACHE[cache_key]
        if entry["expires_at"] is None or entry["expires_at"] > now:
            _MEM_LRU_CACHE.move_to_end(cache_key)
            return entry["value"]
        else:
            del _MEM_LRU_CACHE[cache_key]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT memory_value, expires_at FROM agent_episodic_memory
            WHERE session_id = ? AND memory_key = ?
        """, (session_id, key))
        row = cursor.fetchone()

    if not row:
        return None

    val_raw, expires_at = row[0], row[1]
    if expires_at is not None and expires_at <= now:
        return None

    try:
        val = json.loads(val_raw)
    except Exception:
        val = val_raw

    _MEM_LRU_CACHE[cache_key] = {"value": val, "expires_at": expires_at, "created_at": now}
    return val


def list_session_memories(session_id: str) -> List[Dict[str, Any]]:
    """Lists all active memories for a given session."""
    _init_memory_table()
    now = time.time()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT memory_key, memory_value, tags, created_at, expires_at
            FROM agent_episodic_memory
            WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY created_at DESC
        """, (session_id, now))
        rows = cursor.fetchall()

    results = []
    for r in rows:
        try:
            val = json.loads(r[1])
        except Exception:
            val = r[1]
        results.append({
            "key": r[0],
            "value": val,
            "tags": r[2].split(",") if r[2] else [],
            "created_at": r[3]
        })
    return results
