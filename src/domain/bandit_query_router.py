"""
Zero-dependency Multi-Armed Bandit Query Router Engine.
Learns which retrieval strategy (FTS5, Vector, HyDE, GraphRAG) yields the highest Self-RAG reflection scores.
"""

import random
from typing import Dict, Any, List

# Bandit arms state
_BANDIT_ARMS = {
    "hybrid_rrf_pagerank": {"successes": 15, "trials": 18, "weight": 0.83},
    "multihop_graph_bfs": {"successes": 12, "trials": 15, "weight": 0.80},
    "contextual_hyde": {"successes": 10, "trials": 14, "weight": 0.71},
    "parent_child_expand": {"successes": 14, "trials": 16, "weight": 0.875}
}


def bandit_select_pipeline(intent: str = "FACTUAL") -> Dict[str, Any]:
    """
    Selects the optimal retrieval pipeline using Thompson Sampling / Epsilon-Greedy bandit learning.
    Zero-dependency stdlib implementation.
    """
    global _BANDIT_ARMS

    # Thompson Sampling sampling from Beta distribution approximation
    best_arm = None
    best_score = -1.0

    for arm_name, stats in _BANDIT_ARMS.items():
        # Beta(alpha, beta) sample approximation using stdlib random
        alpha = stats["successes"] + 1
        beta = (stats["trials"] - stats["successes"]) + 1
        sample = random.betavariate(alpha, beta)

        if sample > best_score:
            best_score = sample
            best_arm = arm_name

    return {
        "intent": intent,
        "selected_pipeline": best_arm,
        "bandit_confidence": round(best_score, 4),
        "arms_state": _BANDIT_ARMS,
        "status": "success"
    }


def record_bandit_feedback(pipeline_name: str, is_successful: bool) -> Dict[str, Any]:
    """
    Records reward feedback ([IsSup] = 1.0 vs 0.0) to update bandit arm weights.
    """
    global _BANDIT_ARMS
    if pipeline_name in _BANDIT_ARMS:
        _BANDIT_ARMS[pipeline_name]["trials"] += 1
        if is_successful:
            _BANDIT_ARMS[pipeline_name]["successes"] += 1
        s = _BANDIT_ARMS[pipeline_name]["successes"]
        t = _BANDIT_ARMS[pipeline_name]["trials"]
        _BANDIT_ARMS[pipeline_name]["weight"] = round(s / float(t), 4)

    return {"pipeline": pipeline_name, "updated_stats": _BANDIT_ARMS.get(pipeline_name), "status": "success"}
