"""
Source Document Credibility & Authority Weighting Engine.
Computes document authority scores based on document type and applies authority multipliers to search rankings.
Zero-dependency, stdlib implementation.
"""
import unicodedata
from typing import List, Dict, Any

AUTHORITY_MULTIPLIERS = {
    "policy_spec": 1.50,
    "official_doc": 1.30,
    "verified_pdf": 1.20,
    "general": 1.00,
    "draft": 0.80,
    "scratchpad": 0.60
}


def _infer_doc_type_from_metadata(candidate: Dict[str, Any]) -> str:
    """Dynamically infers document authority type from candidate metadata, filepath, title, and tags."""
    explicit_type = str(candidate.get("doc_type") or "").strip().lower()
    if explicit_type and explicit_type in AUTHORITY_MULTIPLIERS and explicit_type != "general":
        return explicit_type

    filepath = str(candidate.get("filepath") or "").lower()
    title = str(candidate.get("title") or candidate.get("filename") or "").lower()
    tags = [str(t).lower() for t in candidate.get("tags", [])] if isinstance(candidate.get("tags"), (list, tuple, set)) else []
    combined_meta = f"{filepath} {title} {' '.join(tags)}"

    if any(k in combined_meta for k in ("policy", "standard", "rfc", "specification", "compliance", "security_controls")):
        return "policy_spec"
    if any(k in combined_meta for k in ("official", "handbook", "guide", "manual", "readme", "architecture", "overview")):
        return "official_doc"
    if filepath.endswith(".pdf") or "pdf" in tags or "verified" in combined_meta:
        return "verified_pdf"
    if any(k in combined_meta for k in ("draft", "wip", "proposal", "rfc-draft", "unverified")):
        return "draft"
    if any(k in combined_meta for k in ("scratch", "tmp", "temp", "memo", "note", "meeting", "transcript")):
        return "scratchpad"

    return "general"


def apply_source_credibility_weighting(
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Applies authority weighting multipliers to candidate search results.
    Zero-dependency stdlib implementation.
    """
    if not candidates or not isinstance(candidates, list):
        return []

    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    if not valid_candidates:
        return []

    weighted_results = []
    for cand in valid_candidates:
        cand_copy = dict(cand)
        doc_type = _infer_doc_type_from_metadata(cand)
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
