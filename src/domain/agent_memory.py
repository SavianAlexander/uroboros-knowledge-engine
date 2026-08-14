"""
Agentic Long-Term Memory & Episodic Store.
Provides persistent SQLite key-value and semantic preference memory for multi-session continuity.
"""
import unicodedata
import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.infrastructure.database import get_db, get_db_connection, DB_FILE


def init_memory_db(db_path: str = DB_FILE):
    """Initializes agent_memory schema."""
    with get_db() as conn:
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_memory_key ON agent_memory(memory_key)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_memory_category ON agent_memory(category)")
        conn.commit()


def remember(key: str, value: Any, category: str = "preference", confidence: float = 1.0, db_path: str = DB_FILE) -> Dict[str, Any]:
    """Stores or updates a memory key in the persistent SQLite database."""
    init_memory_db(db_path)
    norm_key = unicodedata.normalize("NFC", str(key).strip())
    norm_cat = unicodedata.normalize("NFC", str(category or "preference").strip())
    now = datetime.now(timezone.utc).isoformat()
    str_val = json.dumps(value) if not isinstance(value, str) else value

    with get_db() as conn:
        conn.execute("""
            INSERT INTO agent_memory (category, memory_key, memory_value, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(memory_key) DO UPDATE SET
                category = excluded.category,
                memory_value = excluded.memory_value,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at
        """, (norm_cat, norm_key, str_val, confidence, now, now))
        conn.commit()

    return {"status": "success", "key": norm_key, "category": norm_cat, "updated_at": now}


def recall(key: str, category: Optional[str] = None, db_path: str = DB_FILE) -> Optional[Any]:
    """Retrieves a memory value by key."""
    init_memory_db(db_path)
    norm_key = unicodedata.normalize("NFC", str(key).strip())
    norm_cat = unicodedata.normalize("NFC", str(category).strip()) if category else None

    with get_db() as conn:
        cursor = conn.cursor()
        if norm_cat:
            cursor.execute("SELECT memory_value FROM agent_memory WHERE memory_key = ? AND category = ?", (norm_key, norm_cat))
        else:
            cursor.execute("SELECT memory_value FROM agent_memory WHERE memory_key = ?", (norm_key,))
        row = cursor.fetchone()
        if not row:
            return None
        raw_val = row[0]
        try:
            return json.loads(raw_val)
        except Exception:
            return raw_val


def delete_memory(key: str, db_path: str = DB_FILE) -> Dict[str, Any]:
    """Deletes a memory entry by key."""
    init_memory_db(db_path)
    norm_key = unicodedata.normalize("NFC", str(key).strip())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agent_memory WHERE memory_key = ?", (norm_key,))
        deleted = cursor.rowcount > 0
        conn.commit()
    return {"status": "success" if deleted else "not_found", "key": norm_key, "deleted": deleted}


def forget_category(category: str, db_path: str = DB_FILE) -> Dict[str, Any]:
    """Purges all memories associated with a given category."""
    init_memory_db(db_path)
    norm_cat = unicodedata.normalize("NFC", str(category).strip())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agent_memory WHERE category = ?", (norm_cat,))
        count = cursor.rowcount
        conn.commit()
    return {"status": "success", "category": norm_cat, "deleted_count": count}


def list_memories(category: Optional[str] = None, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Lists stored memories."""
    init_memory_db(db_path)
    norm_cat = unicodedata.normalize("NFC", str(category).strip()) if category else None

    with get_db() as conn:
        cursor = conn.cursor()
        if norm_cat:
            cursor.execute("SELECT id, category, memory_key, memory_value, confidence, updated_at FROM agent_memory WHERE category = ?", (norm_cat,))
        else:
            cursor.execute("SELECT id, category, memory_key, memory_value, confidence, updated_at FROM agent_memory")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            val = r[3]
            try:
                parsed_val = json.loads(val)
            except Exception:
                parsed_val = val
            results.append({
                "id": r[0],
                "category": r[1],
                "key": r[2],
                "value": parsed_val,
                "confidence": r[4],
                "updated_at": r[5]
            })
        return results
