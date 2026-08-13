"""
Zero-dependency Rerank Search Score Deconstruction Explainer Engine.
Provides human-readable breakdowns explaining WHY candidate documents ranked at specific positions.
"""
import unicodedata

from typing import Dict, Any, List


def explain_candidate_score(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deconstructs candidate search score into component weights and explanations.
    Zero-dependency stdlib implementation.
    """
    if not candidate or not isinstance(candidate, dict):
        candidate = {}
    raw_name = str(candidate.get("filename") or "document.md")
    filename = unicodedata.normalize("NFC", raw_name)
    try:
        fts_rank = int(candidate.get("fts_rank", 1))
    except (ValueError, TypeError):
        fts_rank = 1

    try:
        pagerank_score = float(candidate.get("pagerank_score", 0.001))
    except (ValueError, TypeError):
        pagerank_score = 0.001

    try:
        recency_multiplier = float(candidate.get("recency_multiplier", 1.0))
    except (ValueError, TypeError):
        recency_multiplier = 1.0

    try:
        final_score = float(candidate.get("final_score") or candidate.get("rrf_score") or 0.05)
    except (ValueError, TypeError):
        final_score = 0.05

    bm25_weight = round(1.0 / (60.0 + fts_rank), 6)
    pr_boost = round(pagerank_score * 10.0, 6)

    explanation = (
        f"Document '{filename}' achieved a Final Score of {final_score:.6f}.\n"
        f"• Keyword FTS5 BM25 Rank #{fts_rank} contributed {bm25_weight:.6f} points.\n"
        f"• Knowledge Graph PageRank Centrality ({pagerank_score:.6f}) contributed a boost of {pr_boost:.6f} points.\n"
        f"• Recency Time-Decay Multiplier applied: {recency_multiplier:.4f}x."
    )

    return {
        "filename": filename,
        "final_score": final_score,
        "score_components": {
            "bm25_weight": bm25_weight,
            "pagerank_boost": pr_boost,
            "recency_multiplier": recency_multiplier
        },
        "explanation": explanation,
        "status": "success"
    }
