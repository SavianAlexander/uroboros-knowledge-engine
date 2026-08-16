"""
Deterministic Lexical Context Coverage & Refusal Gating Engine.
Evaluates query term representation across candidate passages and triggers refusal when evidence coverage is deficient.
Standard: Pure Python standard library (re, unicodedata, typing).
"""
import re
import unicodedata
from typing import Dict, Any, List

MIN_CONFIDENCE_THRESHOLD = 0.65
RE_QUERY_TERMS = re.compile(r'\b[\w-]{3,}\b')


def evaluate_hallucination_risk(query: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates deterministic token coverage and flags hallucination risk when coverage is below threshold.
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
            "matched_terms": [],
            "missing_terms": [],
            "status": "success"
        }

    matched_words = set()
    total_length = 0

    for p in valid_passages:
        content = str(p.get("content") or p.get("text") or p.get("snippet") or "").lower()
        total_length += len(content)
        for w in query_words:
            if w in content:
                matched_words.add(w)

    coverage_ratio = len(matched_words) / float(len(query_words))
    # Grounding confidence: proportional to token coverage with minimum length floor
    length_bonus = 0.10 if total_length >= 80 else (total_length / 800.0)
    confidence_score = round(min(1.0, (coverage_ratio * 0.90) + length_bonus), 2)

    should_refuse = confidence_score < MIN_CONFIDENCE_THRESHOLD

    return {
        "query": str_query,
        "matched_terms": sorted(list(matched_words)),
        "missing_terms": sorted(list(query_words - matched_words)),
        "confidence_score": confidence_score,
        "should_refuse": should_refuse,
        "refusal_reason": (
            f"Query term coverage ({int(coverage_ratio * 100)}%) is below required threshold ({int(MIN_CONFIDENCE_THRESHOLD * 100)}%)."
            if should_refuse else ""
        ),
        "status": "refused" if should_refuse else "success"
    }
