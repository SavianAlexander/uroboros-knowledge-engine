"""
Instant Local RLHF Preference Optimization Engine.
Logs positive/negative implicit feedback to dynamically boost preference weights for top-performing documents.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any

# In-memory preference feedback weights dictionary
_PREFERENCE_WEIGHTS: Dict[str, float] = {}


def log_user_feedback(
    document_id: str,
    query: str,
    rating: int  # +1 for positive/click, -1 for negative/dislike
) -> Dict[str, Any]:
    """
    Updates local document preference weight based on user explicit/implicit feedback.
    """
    global _PREFERENCE_WEIGHTS
    current = _PREFERENCE_WEIGHTS.get(document_id, 1.0)
    
    delta = 0.10 if rating > 0 else -0.15
    new_weight = max(0.20, min(2.0, round(current + delta, 4)))
    _PREFERENCE_WEIGHTS[document_id] = new_weight

    return {
        "document_id": document_id,
        "previous_weight": current,
        "new_weight": new_weight,
        "rating": rating,
        "status": "success"
    }


def get_document_preference_weight(document_id: str) -> float:
    """Returns stored preference weight for document_id."""
    if document_id in _PREFERENCE_WEIGHTS:
        return _PREFERENCE_WEIGHTS[document_id]

    import os
    import sqlite3
    from src.infrastructure.database import DB_FILE, get_db_connection
    if os.path.exists(DB_FILE):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM query_bookmarks WHERE title LIKE ? OR query LIKE ? LIMIT 1", (f"%{document_id}%", f"%{document_id}%"))
                if cursor.fetchone():
                    return 1.25
        except Exception:
            pass

    return 1.0
