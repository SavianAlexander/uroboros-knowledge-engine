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
        import unicodedata
        cand_copy = dict(cand)
        raw_type = str(cand.get("doc_type") or "general")
        doc_type = unicodedata.normalize("NFC", raw_type).strip().lower()
        multiplier = AUTHORITY_MULTIPLIERS.get(doc_type, 1.00)
        
        raw_score = cand.get("score")
        try:
            base_score = float(raw_score) if raw_score is not None else 0.5
        except (ValueError, TypeError):
            base_score = 0.5

        final_credibility_score = round(base_score * multiplier, 4)

        cand_copy["doc_type"] = doc_type
        cand_copy["authority_multiplier"] = multiplier
        cand_copy["final_credibility_score"] = final_credibility_score
        weighted_results.append(cand_copy)

    weighted_results.sort(key=lambda x: x["final_credibility_score"], reverse=True)
    return weighted_results
