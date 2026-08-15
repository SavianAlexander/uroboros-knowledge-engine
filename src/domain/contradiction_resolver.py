"""
Autonomous Vault Contradiction & Fact Discrepancy Resolver.
Scans SQLite document vault and in-memory text passages to identify contradictory claims, numerical mismatches, date discrepancies, and negation collisions.
Zero-dependency, stdlib implementation.
"""
import re
import sqlite3
import unicodedata
from typing import Dict, Any, List, Tuple, Optional
from src.infrastructure.database import get_db_connection, DB_FILE

RE_NEGATION = re.compile(r'\b(not|never|no|deprecated|disabled|removed|unsupported|false|prohibited|disallowed)\b', re.IGNORECASE)
RE_NUMBERS = re.compile(r'(\$?\d+(?:\.\d+)?(?:\s*(?:ms|s|gb|mb|kb|tb|%|users|req/s|rps|rpm|ghz|mhz|usd|eur|dollars))?)', re.IGNORECASE)
RE_YEARS = re.compile(r'\b(20\d{2}|19\d{2})\b')


def detect_text_pair_contradictions(
    content_a: str,
    content_b: str,
    doc_name_a: str = "doc_a",
    doc_name_b: str = "doc_b"
) -> List[Dict[str, Any]]:
    """
    Evaluates a pair of texts for negation conflicts, numerical collisions, and temporal discrepancies.
    """
    if not content_a or not content_b:
        return []

    norm_a = unicodedata.normalize("NFC", str(content_a))
    norm_b = unicodedata.normalize("NFC", str(content_b))

    words_a = set(w.lower() for w in re.findall(r'\b[\w]{4,}\b', norm_a))
    words_b = set(w.lower() for w in re.findall(r'\b[\w]{4,}\b', norm_b))
    shared_terms = words_a.intersection(words_b)

    if len(shared_terms) < 2:
        return []

    discrepancies = []

    # 1. Negation Conflict Check
    neg_a = bool(RE_NEGATION.search(norm_a))
    neg_b = bool(RE_NEGATION.search(norm_b))
    if neg_a != neg_b:
        discrepancies.append({
            "doc_a": doc_name_a,
            "doc_b": doc_name_b,
            "shared_terms": list(shared_terms)[:5],
            "discrepancy_type": "negation_conflict",
            "confidence": 0.80,
            "detail": f"One document asserts a negation ({'doc_a' if neg_a else 'doc_b'}) while the other does not."
        })

    # 2. Numerical Mismatch on Shared Context
    nums_a = set(RE_NUMBERS.findall(norm_a.lower()))
    nums_b = set(RE_NUMBERS.findall(norm_b.lower()))
    if nums_a and nums_b and not (nums_a & nums_b):
        # Different numbers claimed on shared semantic terms
        discrepancies.append({
            "doc_a": doc_name_a,
            "doc_b": doc_name_b,
            "shared_terms": list(shared_terms)[:5],
            "discrepancy_type": "numerical_mismatch",
            "confidence": 0.70,
            "detail": f"Distinct numerical assertions: doc_a={list(nums_a)[:3]} vs doc_b={list(nums_b)[:3]}"
        })

    # 3. Temporal Year Mismatch
    years_a = set(RE_YEARS.findall(norm_a))
    years_b = set(RE_YEARS.findall(norm_b))
    if years_a and years_b and not (years_a & years_b):
        discrepancies.append({
            "doc_a": doc_name_a,
            "doc_b": doc_name_b,
            "shared_terms": list(shared_terms)[:5],
            "discrepancy_type": "temporal_discrepancy",
            "confidence": 0.75,
            "detail": f"Divergent timeline years: doc_a={list(years_a)} vs doc_b={list(years_b)}"
        })

    return discrepancies


def detect_vault_contradictions(db_path: str = DB_FILE, limit: int = 50) -> Dict[str, Any]:
    """
    Scans the files table for potential factual contradictions between documents.
    # ponytail: multi-criteria discrepancy scan across SQLite chunks; ceiling: O(N^2) pairwise n-gram comparison; upgrade: use cross-encoder NLI model if deep factual verification is required
    """
    safe_limit = max(1, int(limit)) if limit is not None and isinstance(limit, (int, float)) else 50
    try:
        with get_db_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files WHERE content IS NOT NULL LIMIT ?", (safe_limit,))
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

                doc_discrepancies = detect_text_pair_contradictions(
                    content_a,
                    content_b,
                    doc_name_a=doc_a["filename"] or f"file_{doc_a['id']}",
                    doc_name_b=doc_b["filename"] or f"file_{doc_b['id']}"
                )
                contradictions.extend(doc_discrepancies)

        return {
            "contradictions": contradictions,
            "total_scanned": len(rows),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "contradictions": []}

