"""
Zero-dependency Autonomous Claim & Fact Conflict Resolver Engine.
Detects contradictory assertions across vault document pairs (e.g. conflicting dates, numbers, or status claims).
"""
import unicodedata
import re
import sqlite3
from typing import Dict, Any, List

DATE_REGEX = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?|\b\d{4}-\d{2}-\d{2}\b', re.IGNORECASE)
NUMBER_REGEX = re.compile(r'\b\$?\d+(?:\.\d+)?\s*(?:million|billion|thousand|USD|EUR|GB|TB|percent|%)\b', re.IGNORECASE)


def detect_and_resolve_conflicts(topic: str = "") -> Dict[str, Any]:
    """
    Scans knowledge base documents for contradictory dates, numbers, or assertions on matching topics.
    Zero-dependency stdlib implementation.
    """
    conn = None
    try:
        from src.infrastructure.database import get_db_connection, DB_FILE, init_db

        init_db()
        norm_topic = unicodedata.normalize("NFC", str(topic)) if topic else ""

        with get_db_connection(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query_sql = "SELECT id, filename, filepath, content FROM files"
            params = []
            if norm_topic:
                query_sql += " WHERE content LIKE ? OR filename LIKE ?"
                params.extend([f"%{norm_topic}%", f"%{norm_topic}%"])
            query_sql += " LIMIT 15"

            cursor.execute(query_sql, params)
            rows = cursor.fetchall()

        if len(rows) < 2:
            return {
                "conflicts_found": 0,
                "conflicts": [],
                "reconciliation_summary": "Insufficient document pairs to evaluate conflicts.",
                "status": "success"
            }

        # Pre-extract dates and numbers per doc once O(N)
        doc_claims = []
        for r in rows:
            content = r["content"] or ""
            doc_claims.append({
                "filename": r["filename"],
                "dates": set(DATE_REGEX.findall(content)),
                "numbers": set(NUMBER_REGEX.findall(content))
            })

        conflicts = []
        for i in range(len(doc_claims)):
            for j in range(i + 1, len(doc_claims)):
                doc1, doc2 = doc_claims[i], doc_claims[j]
                dates1, dates2 = doc1["dates"], doc2["dates"]
                nums1, nums2 = doc1["numbers"], doc2["numbers"]

                if dates1 and dates2 and dates1 != dates2:
                    conflicts.append({
                        "type": "DATE_CONTRADICTION",
                        "doc_a": doc1["filename"],
                        "doc_b": doc2["filename"],
                        "claims_a": list(dates1),
                        "claims_b": list(dates2),
                        "recommended_truth": f"Flagged date discrepancy between '{doc1['filename']}' and '{doc2['filename']}'"
                    })

                if nums1 and nums2 and nums1 != nums2:
                    conflicts.append({
                        "type": "NUMERICAL_CONTRADICTION",
                        "doc_a": doc1["filename"],
                        "doc_b": doc2["filename"],
                        "claims_a": list(nums1),
                        "claims_b": list(nums2),
                        "recommended_truth": f"Flagged numerical discrepancy between '{doc1['filename']}' and '{doc2['filename']}'"
                    })

        conflicts = conflicts[:10]

        return {
            "topic_evaluated": topic or "All Vault Documents",
            "documents_scanned": len(rows),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "reconciliation_summary": f"Detected {len(conflicts)} potential claim discrepancies across {len(rows)} documents.",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
