"""
Source Document Credibility & Authority Weighting Engine.
Computes document authority scores based on document type and applies authority multipliers to search rankings.
Zero-dependency, stdlib implementation.
"""

from typing import List, Dict, Any

AUTHORITY_MULTIPLIERS = {
    "policy_spec": 1.50,
    "official_doc": 1.30,
    "verified_pdf": 1.20,
    "general": 1.00,
    "draft": 0.80,
    "scratchpad": 0.60
}


def apply_source_credibility_weighting(
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Applies authority weighting multipliers to candidate search results.
    """
    if not candidates or not isinstance(candidates, list):
        return []

    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    if not valid_candidates:
        return []

    weighted_results = []
    for cand in valid_candidates:
        cand_copy = dict(cand)
        doc_type = (cand.get("doc_type") or "general").lower()
        multiplier = AUTHORITY_MULTIPLIERS.get(doc_type, 1.00)
        
        base_score = float(cand.get("score", 0.5))
        final_credibility_score = round(base_score * multiplier, 4)

        cand_copy["doc_type"] = doc_type
        cand_copy["authority_multiplier"] = multiplier
        cand_copy["final_credibility_score"] = final_credibility_score
        weighted_results.append(cand_copy)

    weighted_results.sort(key=lambda x: x["final_credibility_score"], reverse=True)
    return weighted_results
