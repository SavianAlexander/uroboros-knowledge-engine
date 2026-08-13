"""
Self-Supervised Retrieval Feedback Auto-Refiner Engine.
Logs user interaction signals to continuously adjust document chunk affinity vectors.
Zero-dependency, stdlib implementation.
"""
import unicodedata

from typing import Dict, Any, List


# Global persistent affinity ledger in memory
_AFFINITY_LEDGER: Dict[str, float] = {}


def log_feedback_and_refine(
    chunk_id: str,
    feedback_signal: str = "click"
) -> Dict[str, Any]:
    """
    Adjusts affinity boost multiplier based on feedback signal (click, copy, dwell, ignore).
    """
    global _AFFINITY_LEDGER
    norm_chunk_id = unicodedata.normalize("NFC", str(chunk_id or ""))
    current_weight = _AFFINITY_LEDGER.get(norm_chunk_id, 1.0)

    signal_deltas = {
        "click": +0.05,
        "copy": +0.10,
        "dwell": +0.02,
        "ignore": -0.05
    }

    delta = signal_deltas.get(feedback_signal, 0.0)
    new_weight = max(0.1, min(2.0, current_weight + delta))
    _AFFINITY_LEDGER[chunk_id] = round(new_weight, 4)

    return {
        "chunk_id": chunk_id,
        "signal": feedback_signal,
        "previous_affinity": current_weight,
        "updated_affinity": new_weight,
        "status": "success"
    }
