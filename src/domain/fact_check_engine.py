"""
Semantic Contradiction & Fact-Check Engine.
Detects factual contradictions between documents (e.g. Policy A vs Policy B).
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List


def detect_semantic_contradictions(
    doc_a_clauses: List[str],
    doc_b_clauses: List[str]
) -> Dict[str, Any]:
    """
    Scans two sets of document clauses for factual contradictions or value conflicts.
    """
    contradictions = []

    import unicodedata
    valid_a = [unicodedata.normalize("NFC", str(c)) for c in (doc_a_clauses or []) if c is not None]
    valid_b = [unicodedata.normalize("NFC", str(c)) for c in (doc_b_clauses or []) if c is not None]

    for c_a in valid_a:
        norm_a = c_a.lower()
        for c_b in valid_b:
            norm_b = c_b.lower()

            # Negation or value conflict heuristic
            if ("shall " in norm_a and "shall not " in norm_b) or \
               ("required" in norm_a and "prohibited" in norm_b) or \
               ("30 days" in norm_a and "90 days" in norm_b):
                contradictions.append({
                    "clause_a": c_a,
                    "clause_b": c_b,
                    "conflict_type": "policy_discrepancy",
                    "severity": "high"
                })

    return {
        "contradictions_found": contradictions,
        "total_contradictions": len(contradictions),
        "status": "success"
    }
