"""
Self-Improving Search Weight & Chunk Tuner Engine.
Simulates feedback loops on search metrics to dynamically adjust search weights and chunk sizes.
Zero-dependency, stdlib implementation.
"""
import unicodedata

from typing import Dict, Any, List


def optimize_search_parameters(
    historical_feedback: List[Dict[str, Any]],
    current_weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Optimizes search weights (vector_weight, keyword_weight, colbert_weight, chunk_size) based on interaction scores.
    """
    weights = current_weights or {"vector_weight": 0.50, "keyword_weight": 0.30, "colbert_weight": 0.20, "chunk_size": 512}

    if not historical_feedback or not isinstance(historical_feedback, list):
        return {"optimized_weights": weights, "status": "no_feedback_data", "adjustment_applied": False}

    valid_feedback = [f for f in historical_feedback if isinstance(f, dict)]
    if not valid_feedback:
        return {"optimized_weights": weights, "status": "no_feedback_data", "adjustment_applied": False}

    def _safe_score(f):
        s = f.get("score")
        if s is None:
            return 0.5
        try:
            return float(s)
        except (ValueError, TypeError):
            return 0.5

    avg_satisfaction = sum(_safe_score(f) for f in valid_feedback) / float(len(valid_feedback))

    if avg_satisfaction < 0.60:
        # Boost ColBERT rerank and decrease chunk size for higher precision
        weights["colbert_weight"] = round(min(0.50, weights["colbert_weight"] + 0.10), 2)
        weights["vector_weight"] = round(max(0.30, weights["vector_weight"] - 0.05), 2)
        weights["chunk_size"] = 256
    elif avg_satisfaction > 0.85:
        # Stable performance
        pass

    return {
        "optimized_weights": weights,
        "historical_sample_size": len(historical_feedback),
        "avg_user_satisfaction": round(avg_satisfaction, 4),
        "adjustment_applied": True,
        "status": "success"
    }
