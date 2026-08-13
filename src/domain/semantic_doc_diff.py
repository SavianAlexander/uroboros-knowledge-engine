"""
Multi-Document Semantic Diff & Evolution Tracker.
Computes semantic claim diffs between document versions over time.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any, List


def _extract_sentences(text: str) -> List[str]:
    """Extracts non-empty sentences from text, falling back to line/sentence split."""
    if not text.strip():
        return []
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sents:
        sents = [text.strip()]
    return sents


def compute_semantic_doc_diff(doc_text_a: str, doc_text_b: str) -> Dict[str, Any]:
    """
    Computes sentence-level semantic claim diffs between doc_text_a (old) and doc_text_b (new).
    # ponytail: zero-dependency semantic claim diff engine
    """
    sents_a = set(_extract_sentences(doc_text_a))
    sents_b = set(_extract_sentences(doc_text_b))

    added_claims = list(sents_b - sents_a)
    removed_claims = list(sents_a - sents_b)
    retained_claims = list(sents_a.intersection(sents_b))
    union_claims = sents_a.union(sents_b)
    sim_ratio = round(len(retained_claims) / max(len(union_claims), 1), 4)

    return {
        "status": "success",
        "doc_a_claim_count": len(sents_a),
        "doc_b_claim_count": len(sents_b),
        "added_claims_count": len(added_claims),
        "removed_claims_count": len(removed_claims),
        "retained_claims_count": len(retained_claims),
        "total_added": len(added_claims),
        "total_removed": len(removed_claims),
        "similarity_ratio": sim_ratio,
        "added_claims": added_claims,
        "removed_claims": removed_claims
    }


compare_semantic_doc_diff = compute_semantic_doc_diff
