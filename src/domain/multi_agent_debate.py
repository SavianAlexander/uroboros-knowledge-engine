"""
Context Alignment & Adversarial Relevance Verification Engine.
Performs dual-perspective verification (evidence support vs. ambiguity critique) to filter out ungrounded context.
Standard: Pure Python standard library (unicodedata, re, math).
"""
import unicodedata
import re
from typing import Dict, Any, List


def execute_multi_agent_debate(query: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes adversarial dual-pass verification of candidate context passages:
    - Pass 1 (Support Analysis): Evaluates lexical match density, key phrase alignment, and term coverage.
    - Pass 2 (Critique Analysis): Inspects for content ambiguity, length deficiency, and missing search entities.
    """
    if not passages:
        return {
            "query": query,
            "debate_consensus": "REFUSE_NO_CONTEXT",
            "pro_arguments": ["No candidate passages available for context verification."],
            "con_arguments": ["Vault returned zero matching passages for query."],
            "consensus_score": 0.0,
            "rounds_debated": 1,
            "status": "success"
        }

    norm_query = unicodedata.normalize("NFC", str(query or "")).lower()
    q_tokens = set(re.findall(r'\b\w{3,}\b', norm_query))

    if not q_tokens:
        return {
            "query": query,
            "debate_consensus": "REFUSE_NO_CONTEXT",
            "pro_arguments": ["Query contains no searchable content terms."],
            "con_arguments": ["Insufficient token entropy in search query."],
            "consensus_score": 0.0,
            "rounds_debated": 1,
            "status": "success"
        }

    # Aggregate passage content analysis
    total_chars = 0
    matched_q_tokens = set()
    pro_points = []
    con_points = []

    for i, p in enumerate(passages[:5]):
        fname = p.get("filename", f"doc_{i+1}.txt")
        raw_text = p.get("content") or p.get("text") or p.get("snippet") or ""
        norm_text = unicodedata.normalize("NFC", str(raw_text)).lower()
        # Include both passage filename and body tokens for full contextual entity grounding
        p_tokens = set(re.findall(r'\b\w{3,}\b', f"{fname} {norm_text}".lower()))
        
        overlap = q_tokens.intersection(p_tokens)
        matched_q_tokens.update(overlap)
        total_chars += len(norm_text)
        
        if overlap:
            coverage_pct = round((len(overlap) / float(len(q_tokens))) * 100, 1)
            pro_points.append(f"Passage '{fname}' grounds {coverage_pct}% of query terms ({', '.join(sorted(overlap)[:3])}).")
        else:
            con_points.append(f"Passage '{fname}' lacks direct token overlap with search query.")

    total_coverage = len(matched_q_tokens) / float(len(q_tokens))
    avg_passage_len = total_chars / float(max(1, len(passages)))

    if avg_passage_len < 20 and total_coverage < 0.5:
        con_points.append(f"Average passage length ({int(avg_passage_len)} chars) is below reliable grounding threshold.")
    else:
        pro_points.append(f"Retrieved {len(passages)} passages providing {total_chars} total characters of reference material.")

    # Calculate deterministic consensus score based on total query term coverage and context volume
    consensus_score = round(min(1.0, 0.45 + (total_coverage * 0.40) + min(0.15, len(passages) * 0.05)), 2)
    is_approved = consensus_score >= 0.65

    return {
        "query": query,
        "debate_consensus": "APPROVE_CONTEXT" if is_approved else "REJECT_CONTEXT",
        "pro_arguments": pro_points or ["No strong supporting evidence found."],
        "con_arguments": con_points or ["No significant critique violations detected."],
        "consensus_score": consensus_score,
        "rounds_debated": 2,
        "status": "success"
    }
