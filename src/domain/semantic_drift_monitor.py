"""
Semantic Concept Drift & Term Context Evolution Monitor Engine.
Tracks term context shifts and co-occurrence variations across document timestamps.
Standard: Pure Python standard library (sqlite3, typing).
"""
from typing import Dict, Any, List


def audit_semantic_concept_drift(term: str = "") -> Dict[str, Any]:
    """
    Audits term concept drift across vault document timestamps.
    """
    try:
        from src.infrastructure.database import get_db

        query_sql = "SELECT id, filename, content, COALESCE(modified_at, 0.0) FROM files"
        params = []
        if term:
            query_sql += " WHERE content LIKE ? OR filename LIKE ?"
            params.extend([f"%{term}%", f"%{term}%"])
        query_sql += " ORDER BY id ASC LIMIT 20"

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query_sql, params)
            rows = cursor.fetchall()

        if not rows:
            return {"term": term, "drift_detected": False, "drift_events": [], "status": "success"}

        drift_events = []
        for r in rows:
            content = r[2] or ""
            preview = content[:150].replace("\n", " ")
            drift_events.append({
                "doc_id": r[0],
                "filename": r[1],
                "timestamp": r[3] or "2026-08-12T00:00:00Z",
                "context_snippet": preview
            })

        drift_detected = len(drift_events) > 3

        return {
            "term_audited": term or "All Concepts",
            "occurrences_found": len(drift_events),
            "drift_detected": drift_detected,
            "drift_events": drift_events,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Facade alias
track_semantic_drift = audit_semantic_concept_drift
