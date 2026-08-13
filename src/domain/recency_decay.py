"""
Zero-dependency Adaptive Recency Time-Decay Reranking Engine.
Applies exponential decay scoring to prioritize recently updated vault documents over legacy records.
Formula: Score_final = Score_initial * exp(-decay_lambda * delta_days)
"""
import math
import time
from datetime import datetime
from typing import Dict, Any, List

from functools import lru_cache

_LN_2 = 0.6931471805599453

@lru_cache(maxsize=2048)
def _parse_iso_timestamp(mtime_str: str) -> float:
    try:
        clean_str = mtime_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        return dt.timestamp()
    except Exception:
        return 0.0


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
    decay_lambda = _LN_2 / float(max(1.0, decay_half_life_days))

    reranked = []
    for cand in valid_candidates:
        mtime = cand.get("mtime") or cand.get("updated_at") or now
        if isinstance(mtime, (int, float)):
            delta_sec = max(0.0, now - float(mtime))
        elif isinstance(mtime, str):
            ts = _parse_iso_timestamp(mtime)
            delta_sec = max(0.0, now - ts) if ts > 0 else 0.0
        else:
            delta_sec = 0.0

        delta_days = delta_sec / 86400.0
        recency_multiplier = round(math.exp(-decay_lambda * delta_days), 6)

        raw_score = cand.get("rrf_score") if cand.get("rrf_score") is not None else cand.get("score")
        try:
            initial_score = float(raw_score) if raw_score is not None else 1.0
        except (ValueError, TypeError):
            initial_score = 1.0

        final_score = round(initial_score * recency_multiplier, 6)

        cand_copy = dict(cand)
        cand_copy["initial_score"] = initial_score
        cand_copy["recency_multiplier"] = recency_multiplier
        cand_copy["final_score"] = final_score
        cand_copy["age_days"] = round(delta_days, 2)

        reranked.append(cand_copy)

    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked
