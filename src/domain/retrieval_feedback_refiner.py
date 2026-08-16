"""
Persistent Retrieval Feedback & Chunk Affinity Refiner Engine.
Logs user interaction signals (click, copy, dwell, ignore) to dynamically adjust document chunk relevance multipliers
persisted directly in the SQLite knowledge base.
Standard: Pure Python standard library (sqlite3, unicodedata, typing).
"""
import sqlite3
import unicodedata
from typing import Dict, Any, Optional

SIGNAL_DELTAS = {
    "click": +0.05,
    "copy": +0.10,
    "dwell": +0.02,
    "ignore": -0.05
}

# Fallback in-memory ledger if database connection is unavailable
_FALLBACK_LEDGER: Dict[str, float] = {}


def _init_feedback_table(conn: sqlite3.Connection) -> None:
    """Ensures chunk feedback persistence table exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunk_feedback (
            chunk_id TEXT PRIMARY KEY,
            affinity_score REAL DEFAULT 1.0,
            interaction_count INTEGER DEFAULT 0,
            last_signal TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def get_chunk_affinity(chunk_id: str, db_path: Optional[str] = None) -> float:
    """Retrieves current affinity multiplier for a chunk ID."""
    norm_chunk_id = unicodedata.normalize("NFC", str(chunk_id or "")).strip()
    if not norm_chunk_id:
        return 1.0

    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_feedback_table(conn)
            row = conn.execute("SELECT affinity_score FROM chunk_feedback WHERE chunk_id = ?", (norm_chunk_id,)).fetchone()
            if row:
                return float(row["affinity_score"] if isinstance(row, sqlite3.Row) else row[0])
    except Exception:
        pass

    return _FALLBACK_LEDGER.get(norm_chunk_id, 1.0)


def log_feedback_and_refine(
    chunk_id: str,
    feedback_signal: str = "click",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adjusts and persists affinity multiplier for a chunk based on user interaction signals.
    """
    norm_chunk_id = unicodedata.normalize("NFC", str(chunk_id or "")).strip()
    if not norm_chunk_id:
        return {"status": "error", "message": "empty_chunk_id"}

    current_weight = get_chunk_affinity(norm_chunk_id, db_path)
    delta = SIGNAL_DELTAS.get(feedback_signal, 0.0)
    new_weight = round(max(0.1, min(2.0, current_weight + delta)), 4)

    # Persist in SQLite
    persisted = False
    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_feedback_table(conn)
            conn.execute("""
                INSERT INTO chunk_feedback (chunk_id, affinity_score, interaction_count, last_signal, updated_at)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(chunk_id) DO UPDATE SET
                    affinity_score = ?,
                    interaction_count = interaction_count + 1,
                    last_signal = ?,
                    updated_at = CURRENT_TIMESTAMP
            """, (norm_chunk_id, new_weight, feedback_signal, new_weight, feedback_signal))
            conn.commit()
            persisted = True
    except Exception:
        _FALLBACK_LEDGER[norm_chunk_id] = new_weight

    return {
        "chunk_id": norm_chunk_id,
        "signal": feedback_signal,
        "previous_affinity": current_weight,
        "updated_affinity": new_weight,
        "persisted_to_db": persisted,
        "status": "success"
    }
