"""
Reciprocal Rank Fusion (RRF) & Multi-Channel Reranker Engine.
Delegates to unified src.domain.reranking engine.
"""
from typing import List, Dict, Any
from src.domain.reranking import compute_rrf_scores, rerank_sparse_dense_fusion

# Backward compatibility aliases
reciprocal_rank_fusion = compute_rrf_scores


def score_rerank_candidates(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 10,
    dense_weight: float = 0.5
) -> List[Dict[str, Any]]:
    """Score and rerank search candidates using sparse-dense fusion."""
    return rerank_sparse_dense_fusion(query, candidates, top_k=top_k, dense_weight=dense_weight)
