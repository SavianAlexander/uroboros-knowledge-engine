"""
Zero-dependency Hallucination-Guarded Refusal & Confidence Engine.
Calculates mathematical Context Confidence Scores (0.00 - 1.00) and refuses low-confidence queries to prevent false info.
"""
import re
import unicodedata
from typing import Dict, Any, List

MIN_CONFIDENCE_THRESHOLD = 0.65
RE_QUERY_TERMS = re.compile(r'\b[\w-]{3,}\b')


def evaluate_hallucination_risk(query: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates context coverage and calculates confidence score. Refuses if confidence < 0.65.
    Zero-dependency stdlib implementation.
    """
    str_query = str(query or "").strip()
    valid_passages = [p for p in passages if isinstance(p, dict)] if isinstance(passages, list) else []

    if not valid_passages:
        return {
            "query": str_query,
            "confidence_score": 0.0,
            "should_refuse": True,
            "refusal_reason": "Zero relevant passages retrieved from knowledge vault.",
            "status": "refused"
        }

    norm_query = unicodedata.normalize("NFC", str_query)
    query_words = set(RE_QUERY_TERMS.findall(norm_query.lower()))
    if not query_words:
        return {
            "query": str_query,
            "confidence_score": 1.0,
            "should_refuse": False,
            "status": "success"
        }

    matched_words = set()
    total_length = 0

    for p in valid_passages:
        content = (p.get("content") or p.get("text") or "").lower()
        total_length += len(content)
        for w in query_words:
            if w in content:
                matched_words.add(w)

    coverage_ratio = len(matched_words) / float(len(query_words))
    confidence_score = round(min(1.0, coverage_ratio * 0.90 + (0.10 if total_length > 100 else 0.0)), 2)

    should_refuse = confidence_score < MIN_CONFIDENCE_THRESHOLD

    return {
        "query": str_query,
        "matched_terms": list(matched_words),
        "missing_terms": list(query_words - matched_words),
        "confidence_score": confidence_score,
        "should_refuse": should_refuse,
        "refusal_reason": f"Context coverage ({confidence_score:.2f}) below threshold ({MIN_CONFIDENCE_THRESHOLD})" if should_refuse else None,
        "status": "refused" if should_refuse else "success"
    }
