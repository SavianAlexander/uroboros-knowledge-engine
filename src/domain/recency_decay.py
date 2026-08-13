"""
Zero-dependency Adaptive Recency Time-Decay Reranking Engine.
Applies exponential decay scoring to prioritize recently updated vault documents over legacy records.
Formula: Score_final = Score_initial * exp(-decay_lambda * delta_days)
"""

import math
import time
from typing import Dict, Any, List


def apply_recency_decay(candidates: List[Dict[str, Any]], decay_half_life_days: float = 30.0) -> List[Dict[str, Any]]:
    """
    Applies exponential recency decay to candidate search scores based on document mtime.
    Zero-dependency stdlib implementation.
    """
    if not candidates or not isinstance(candidates, list):
        return []

    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    if not valid_candidates:
        return []

    now = time.time()
    decay_lambda = math.log(2) / float(max(1.0, decay_half_life_days))

    reranked = []
    for cand in valid_candidates:
        mtime = cand.get("mtime") or cand.get("updated_at") or now
        if isinstance(mtime, (int, float)):
            delta_sec = max(0.0, now - float(mtime))
        elif isinstance(mtime, str):
            try:
                from datetime import datetime, timezone
                clean_str = mtime.replace("Z", "+00:00")
                dt = datetime.fromisoformat(clean_str)
                ts = dt.timestamp()
                delta_sec = max(0.0, now - ts)
            except Exception:
                delta_sec = 0.0
        else:
            delta_sec = 0.0

        delta_days = delta_sec / 86400.0
        recency_multiplier = round(math.exp(-decay_lambda * delta_days), 6)

        initial_score = cand.get("rrf_score") or cand.get("score") or 1.0
        final_score = round(initial_score * recency_multiplier, 6)

        cand_copy = dict(cand)
        cand_copy["initial_score"] = initial_score
        cand_copy["recency_multiplier"] = recency_multiplier
        cand_copy["final_score"] = final_score
        cand_copy["age_days"] = round(delta_days, 2)

        reranked.append(cand_copy)

    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked
