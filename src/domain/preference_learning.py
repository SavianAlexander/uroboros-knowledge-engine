"""
Document Preference Learning & Direct Feedback Optimization Engine.
Persists explicit and implicit user document feedback to SQLite and calculates
Bayesian Laplace-smoothed preference boost weights for hybrid search ranking.
Standard: Pure Python standard library (sqlite3, time, typing).
"""
import time
import sqlite3
from typing import Dict, Any, Optional

_MEMORY_CACHE: Dict[str, float] = {}


def _init_preference_table(conn: sqlite3.Connection):
    """Initializes the persistent document preference feedback table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_preference_feedback (
            doc_id TEXT PRIMARY KEY,
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            weight REAL DEFAULT 1.0,
            last_query TEXT,
            updated_at REAL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_pref_weight ON document_preference_feedback(weight)")


def log_user_feedback(
    document_id: str,
    query: str = "",
    rating: int = 1  # +1 for positive/click/bookmark, -1 for negative/dislike
) -> Dict[str, Any]:
    """
    Persists document feedback to SQLite and computes updated Bayesian Laplace weight.
    Formula: weight = 1.0 + ((positive - negative) / (positive + negative + 2.0)) * 0.60
    """
    if not document_id:
        return {"status": "error", "message": "document_id is required"}

    doc_str = str(document_id).strip()
    is_positive = int(rating) > 0
    now = time.time()

    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_preference_table(conn)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT positive_count, negative_count, weight FROM document_preference_feedback WHERE doc_id = ?",
                (doc_str,)
            )
            row = cursor.fetchone()

            if row:
                pos = row[0] + (1 if is_positive else 0)
                neg = row[1] + (0 if is_positive else 1)
                prev_w = row[2]
            else:
                pos = 1 if is_positive else 0
                neg = 0 if is_positive else 1
                prev_w = 1.0

            # Bayesian Laplace smoothing
            smoothed_score = (pos - neg) / float(pos + neg + 2.0)
            new_weight = round(max(0.40, min(1.60, 1.0 + (smoothed_score * 0.60))), 4)

            cursor.execute("""
                INSERT INTO document_preference_feedback (doc_id, positive_count, negative_count, weight, last_query, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    positive_count = excluded.positive_count,
                    negative_count = excluded.negative_count,
                    weight = excluded.weight,
                    last_query = excluded.last_query,
                    updated_at = excluded.updated_at
            """, (doc_str, pos, neg, new_weight, query or "", now))
            conn.commit()

        _MEMORY_CACHE[doc_str] = new_weight

        return {
            "document_id": doc_str,
            "previous_weight": prev_w,
            "new_weight": new_weight,
            "positive_count": pos,
            "negative_count": neg,
            "rating": rating,
            "status": "success"
        }
    except Exception as e:
        # Fallback to local memory cache if database is locked
        current = _MEMORY_CACHE.get(doc_str, 1.0)
        delta = 0.10 if is_positive else -0.15
        new_w = max(0.40, min(1.60, round(current + delta, 4)))
        _MEMORY_CACHE[doc_str] = new_w
        return {
            "document_id": doc_str,
            "previous_weight": current,
            "new_weight": new_w,
            "rating": rating,
            "status": "fallback_cached",
            "error": str(e)
        }


def get_document_preference_weight(document_id: str) -> float:
    """
    Retrieves stored Bayesian preference weight for document_id from SQLite.
    Returns 1.0 default if no prior feedback is recorded.
    """
    if not document_id:
        return 1.0

    doc_str = str(document_id).strip()
    if doc_str in _MEMORY_CACHE:
        return _MEMORY_CACHE[doc_str]

    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_preference_table(conn)
            cursor = conn.cursor()
            cursor.execute("SELECT weight FROM document_preference_feedback WHERE doc_id = ?", (doc_str,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                w = float(row[0])
                _MEMORY_CACHE[doc_str] = w
                return w
    except Exception:
        pass

    return 1.0


class DocumentPreferenceEngine:
    """Facade for document preference learning and ranking feedback."""

    @staticmethod
    def log_feedback(document_id: str, query: str = "", rating: int = 1) -> Dict[str, Any]:
        return log_user_feedback(document_id, query, rating)

    @staticmethod
    def get_weight(document_id: str) -> float:
        return get_document_preference_weight(document_id)
