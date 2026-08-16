"""
Reciprocal Rank Fusion (RRF) & Multi-Channel Reranker Engine.
Combines dense vector ranks, FTS5 BM25 keyword ranks, exponential time-decay scoring,
and learned Bayesian preference weights from user interactions.
Standard: Pure Python standard library (math, time, typing).
"""
import math
import time
from typing import List, Dict, Any


def compute_rrf_scores(
    vector_results: List[Dict[str, Any]],
    fts_results: List[Dict[str, Any]],
    k: int = 60,
    w_vector: float = 1.0,
    w_fts: float = 1.0,
    time_decay_lambda: float = 0.00001,
    apply_preference_weights: bool = True
) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion (RRF) reranker with exponential time-decay scoring
    and learned Bayesian document preference multipliers.
    """
    doc_map: Dict[str, Dict[str, Any]] = {}
    now = time.time()

    # 1. Process Vector Search Rank Positions
    for rank, doc in enumerate(vector_results or [], start=1):
        doc_id = str(doc.get("id") or doc.get("filename") or doc.get("path"))
        if not doc_id:
            continue
        if doc_id not in doc_map:
            doc_map[doc_id] = {**doc, "rrf_score": 0.0, "vector_rank": rank, "fts_rank": None}
        else:
            doc_map[doc_id]["vector_rank"] = rank
        
        doc_map[doc_id]["rrf_score"] += w_vector / (k + rank)

    # 2. Process FTS5 BM25 Keyword Search Rank Positions
    for rank, doc in enumerate(fts_results or [], start=1):
        doc_id = str(doc.get("id") or doc.get("filename") or doc.get("path"))
        if not doc_id:
            continue
        if doc_id not in doc_map:
            doc_map[doc_id] = {**doc, "rrf_score": 0.0, "vector_rank": None, "fts_rank": rank}
        else:
            doc_map[doc_id]["fts_rank"] = rank
            
        doc_map[doc_id]["rrf_score"] += w_fts / (k + rank)

    # 3. Apply Recency Modification & Learned Preference Weights
    combined_results = list(doc_map.values())
    
    pref_getter = None
    if apply_preference_weights:
        try:
            from src.domain.preference_learning import get_document_preference_weight
            pref_getter = get_document_preference_weight
        except Exception:
            pref_getter = None

    for doc in combined_results:
        mtime = doc.get("mtime") or doc.get("timestamp") or now
        if isinstance(mtime, (int, float)):
            delta_days = (now - mtime) / 86400.0
            recency_decay = math.exp(-time_decay_lambda * max(0.0, delta_days))
            doc["rrf_score"] *= recency_decay

        if pref_getter:
            doc_key = str(doc.get("filename") or doc.get("id") or "")
            if doc_key:
                pref_mult = pref_getter(doc_key)
                if pref_mult != 1.0:
                    doc["rrf_score"] *= pref_mult
                    doc["preference_weight"] = pref_mult

    # 4. Sort by RRF score descending
    combined_results.sort(key=lambda x: x["rrf_score"], reverse=True)
    return combined_results


# Aliases for domain facade compatibility
reciprocal_rank_fusion = compute_rrf_scores
score_rerank_candidates = compute_rrf_scores
