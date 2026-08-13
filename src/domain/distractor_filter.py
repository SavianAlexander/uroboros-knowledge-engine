"""
Adversarial Noise & Distractor Filter Engine.
Filters out candidate chunks with high superficial keyword matches but low core semantic similarity.
Zero-dependency, stdlib implementation.
"""

from typing import List, Dict, Any
from src.domain.rag_grounding_guard import compute_ngram_overlap


def filter_distractor_chunks(
    query: str,
    candidates: List[Dict[str, Any]],
    min_intent_overlap: float = 0.15
) -> Dict[str, Any]:
    """
    Filters candidate chunks by computing core intent overlap score.
    Removes distractor chunks that fall below min_intent_overlap threshold.
    """
    if not candidates or not isinstance(candidates, list):
        return {"filtered_candidates": [], "distractor_count": 0, "status": "success"}

    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    if not valid_candidates:
        return {"filtered_candidates": [], "distractor_count": 0, "status": "success"}

    filtered = []
    distractors = []

    for cand in valid_candidates:
        content = cand.get("content") or cand.get("text") or ""
        score = compute_ngram_overlap(query, content)
        cand_copy = dict(cand)
        cand_copy["intent_overlap_score"] = score
        
        if score >= min_intent_overlap or cand.get("score", 0.0) >= 0.70:
            filtered.append(cand_copy)
        else:
            distractors.append(cand_copy)

    return {
        "filtered_candidates": filtered,
        "distractors_removed": len(distractors),
        "total_candidates": len(candidates),
        "distractors": distractors,
        "status": "success"
    }
