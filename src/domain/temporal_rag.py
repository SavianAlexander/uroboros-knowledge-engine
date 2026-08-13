"""
Temporal Decay & Recency-Weighted Scoring Engine.
Applies exponential time-decay scoring (S_final = S_vec * e^(-lambda * delta_t_days)) to favor recent documents over obsolete revisions.
Zero-dependency, stdlib implementation.
"""

import math
import time
from typing import List, Dict, Any


def apply_temporal_decay_scoring(
    candidates: List[Dict[str, Any]],
    half_life_days: float = 90.0
) -> List[Dict[str, Any]]:
    """
    Applies exponential time-decay weighting to candidate search results based on updated_at timestamp.
    half_life_days controls decay rate (default 90 days).
    """
    if not candidates or not isinstance(candidates, list):
        return []

    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    if not valid_candidates:
        return []

    now = time.time()
    decay_lambda = math.log(2.0) / half_life_days

    scored_results = []
    for cand in valid_candidates:
        cand_copy = dict(cand)
        try:
            base_score = float(cand.get("score", 0.5))
        except (ValueError, TypeError):
            base_score = 0.5

        try:
            timestamp = float(cand.get("timestamp", now))
        except (ValueError, TypeError):
            timestamp = now
        
        age_days = max(0.0, (now - timestamp) / 86400.0)
        decay_factor = math.exp(-decay_lambda * age_days)
        final_score = round(base_score * decay_factor, 4)

        cand_copy["base_score"] = base_score
        cand_copy["age_days"] = round(age_days, 1)
        cand_copy["decay_factor"] = round(decay_factor, 4)
        cand_copy["final_temporal_score"] = final_score

        scored_results.append(cand_copy)

    scored_results.sort(key=lambda x: x["final_temporal_score"], reverse=True)
    return scored_results
