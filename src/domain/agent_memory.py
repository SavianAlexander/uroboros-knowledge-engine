"""
Agentic Long-Term Memory & Episodic Store.
Provides persistent SQLite key-value and semantic preference memory for multi-session continuity.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.infrastructure.database import get_db_connection, DB_FILE


_initialized_dbs = set()


def init_memory_db(db_path: str = DB_FILE):
    """Initializes agent_memory schema."""
    if db_path in _initialized_dbs:
        return
    with get_db_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL DEFAULT 'preference',
                memory_key TEXT UNIQUE NOT NULL,
                memory_value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
    _initialized_dbs.add(db_path)


def remember(key: str, value: Any, category: str = "preference", confidence: float = 1.0, db_path: str = DB_FILE) -> Dict[str, Any]:
    """Stores or updates a memory key in the persistent SQLite database."""
    init_memory_db(db_path)
    import unicodedata
    norm_key = unicodedata.normalize("NFC", str(key))
    norm_cat = unicodedata.normalize("NFC", str(category or "preference"))
    now = datetime.now(timezone.utc).isoformat()
    str_val = json.dumps(value) if not isinstance(value, str) else value

    with get_db_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO agent_memory (category, memory_key, memory_value, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(memory_key) DO UPDATE SET
                memory_value = excluded.memory_value,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at
        """, (category, key, str_val, confidence, now, now))
        conn.commit()

    return {"status": "success", "key": key, "category": category, "updated_at": now}


def recall(key: str, category: Optional[str] = None, db_path: str = DB_FILE) -> Optional[Any]:
    """Retrieves a memory value by key."""
    init_memory_db(db_path)
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT memory_value FROM agent_memory WHERE memory_key = ? AND category = ?", (key, category))
        else:
            cursor.execute("SELECT memory_value FROM agent_memory WHERE memory_key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return None
        raw_val = row["memory_value"]
        try:
            return json.loads(raw_val)
        except Exception:
            return raw_val


def list_memories(category: Optional[str] = None, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Lists stored memories."""
    init_memory_db(db_path)
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT id, category, memory_key, memory_value, confidence, updated_at FROM agent_memory WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT id, category, memory_key, memory_value, confidence, updated_at FROM agent_memory")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            val = r["memory_value"]
            try:
                parsed_val = json.loads(val)
            except Exception:
                parsed_val = val
            results.append({
                "id": r["id"],
                "category": r["category"],
                "key": r["memory_key"],
                "value": parsed_val,
                "confidence": r["confidence"],
                "updated_at": r["updated_at"]
            })
        return results
