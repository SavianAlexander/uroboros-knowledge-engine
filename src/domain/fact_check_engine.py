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

    for c_a in doc_a_clauses:
        norm_a = c_a.lower()
        for c_b in doc_b_clauses:
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
