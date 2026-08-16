"""
Vector Distribution Drift & Re-Balancing Evaluation Engine.
Monitors vector embedding centroid shift distance as new documents are ingested to determine when re-indexing is warranted.
Standard: Pure Python standard library (math, typing).
"""
import math
from typing import Dict, Any, List


def audit_vector_index_drift(
    current_centroids: List[List[float]],
    new_embeddings: List[List[float]],
    drift_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Computes Euclidean centroid shift distance between baseline centroids and newly ingested vector embeddings.
    """
    if not current_centroids or not isinstance(current_centroids, list):
        return {"drift_score": 0.0, "rebalance_needed": False, "status": "insufficient_vectors"}
    if not new_embeddings or not isinstance(new_embeddings, list):
        return {"drift_score": 0.0, "rebalance_needed": False, "status": "insufficient_vectors"}

    valid_new = [e for e in new_embeddings if isinstance(e, list) and len(e) > 0]
    valid_curr = [c for c in current_centroids if isinstance(c, list) and len(c) > 0]
    if not valid_new or not valid_curr:
        return {"drift_score": 0.0, "rebalance_needed": False, "status": "insufficient_vectors"}

    dim = min(len(valid_new[0]), len(valid_curr[0]))
    if dim == 0:
        return {"drift_score": 0.0, "rebalance_needed": False, "status": "zero_dimension"}

    # Compute mean centroid vectors
    mean_new = [sum(emb[i] for emb in valid_new if len(emb) > i) / float(len(valid_new)) for i in range(dim)]
    mean_curr = [sum(cent[i] for cent in valid_curr if len(cent) > i) / float(len(valid_curr)) for i in range(dim)]

    # Euclidean distance between centroids
    euclidean_dist = math.sqrt(sum((mean_new[i] - mean_curr[i]) ** 2 for i in range(dim)))
    drift_score = round(euclidean_dist, 4)
    rebalance_needed = drift_score >= drift_threshold

    return {
        "drift_score": drift_score,
        "euclidean_shift": drift_score,
        "drift_threshold": drift_threshold,
        "dimension": dim,
        "sample_count": len(valid_new),
        "rebalance_needed": rebalance_needed,
        "recommended_action": "trigger_background_rebalance" if rebalance_needed else "index_optimal",
        "status": "success"
    }
