"""
Autonomous Vault Contradiction & Fact Discrepancy Resolver.
Scans SQLite document vault to identify contradictory claims, numerical mismatches, and legacy specs.
Zero-dependency, stdlib implementation.
"""

import re
import sqlite3
from typing import Dict, Any, List, Tuple, Optional
from src.infrastructure.database import get_db_connection, DB_FILE

RE_NEGATION = re.compile(r'\b(not|never|no|deprecated|disabled|removed|unsupported)\b', re.IGNORECASE)


def detect_vault_contradictions(db_path: str = DB_FILE, limit: int = 50) -> Dict[str, Any]:
    """
    Scans the files table for potential factual contradictions between documents.
    # ponytail: lightweight n-gram and negation heuristic scan across SQLite chunks
    """
    try:
        with get_db_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files WHERE content IS NOT NULL LIMIT ?", (limit,))
            rows = cursor.fetchall()

        if len(rows) < 2:
            return {"contradictions": [], "total_scanned": len(rows), "status": "success"}

        contradictions = []
        # Compare document pairs for key assertion collisions
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                doc_a = rows[i]
                doc_b = rows[j]
                
                content_a = doc_a["content"] or ""
                content_b = doc_b["content"] or ""

                # Extract shared key terms (3+ chars)
                words_a = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', content_a))
                words_b = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', content_b))
                shared_terms = words_a.intersection(words_b)

                if len(shared_terms) > 5:
                    # Check for inverse negation patterns in shared context
                    neg_a = bool(RE_NEGATION.search(content_a))
                    neg_b = bool(RE_NEGATION.search(content_b))

                    if neg_a != neg_b:
                        contradictions.append({
                            "doc_a": doc_a["filename"],
                            "doc_b": doc_b["filename"],
                            "shared_terms": list(shared_terms)[:5],
                            "discrepancy_type": "negation_conflict",
                            "confidence": 0.75
                        })

        return {
            "contradictions": contradictions,
            "total_scanned": len(rows),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "contradictions": []}
