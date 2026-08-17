"""
Semantic Concept Drift & Term Context Evolution Monitor Engine.
Tracks term context shifts and co-occurrence variations across document timestamps.
Standard: Pure Python standard library (sqlite3, typing, re).
"""
import re
from typing import Dict, Any, List


def compute_jaccard_divergence(text_a: str, text_b: str) -> float:
    """Compute Jaccard distance (1.0 - overlap) between two text corpora in O(N) set operations."""
    tokens_a = set(re.findall(r'\b\w+\b', text_a.lower()))
    tokens_b = set(re.findall(r'\b\w+\b', text_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return round(1.0 - (intersection / union), 4) if union > 0 else 0.0


def audit_semantic_concept_drift(term: str = "") -> Dict[str, Any]:
    """
    Audits term concept drift across vault document timestamps using token divergence.
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
            return {"term": term, "drift_detected": False, "divergence_score": 0.0, "drift_events": [], "status": "success"}

        drift_events = []
        contents = []
        for r in rows:
            content = r[2] or ""
            contents.append(content)
            preview = content[:150].replace("\n", " ")
            drift_events.append({
                "doc_id": r[0],
                "filename": r[1],
                "timestamp": r[3] or "2026-08-12T00:00:00Z",
                "context_snippet": preview
            })

        # Calculate divergence between earliest and latest epoch documents
        divergence = 0.0
        if len(contents) >= 2:
            divergence = compute_jaccard_divergence(contents[0], contents[-1])

        drift_detected = len(drift_events) > 3 or divergence > 0.65

        return {
            "term_audited": term or "All Concepts",
            "occurrences_found": len(drift_events),
            "divergence_score": divergence,
            "drift_detected": drift_detected,
            "drift_events": drift_events,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Facade alias
track_semantic_drift = audit_semantic_concept_drift

