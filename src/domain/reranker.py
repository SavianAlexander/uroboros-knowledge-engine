import math
import time
from typing import List, Dict, Any

def compute_rrf_scores(
    vector_results: List[Dict[str, Any]],
    fts_results: List[Dict[str, Any]],
    k: int = 60,
    w_vector: float = 1.0,
    w_fts: float = 1.0,
    time_decay_lambda: float = 0.00001
) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion (RRF) reranker with exponential time-decay scoring.
    Combines dense vector rank and BM25 keyword rank position with recency decay.
    """
    doc_map: Dict[str, Dict[str, Any]] = {}
    now = time.time()

    # 1. Process Vector Search Rank Positions
    for rank, doc in enumerate(vector_results, start=1):
        doc_id = str(doc.get("id") or doc.get("filename") or doc.get("path"))
        if not doc_id:
            continue
        if doc_id not in doc_map:
            doc_map[doc_id] = {**doc, "rrf_score": 0.0, "vector_rank": rank, "fts_rank": None}
        else:
            doc_map[doc_id]["vector_rank"] = rank
        
        doc_map[doc_id]["rrf_score"] += w_vector / (k + rank)

    # 2. Process FTS5 BM25 Keyword Search Rank Positions
    for rank, doc in enumerate(fts_results, start=1):
        doc_id = str(doc.get("id") or doc.get("filename") or doc.get("path"))
        if not doc_id:
            continue
        if doc_id not in doc_map:
            doc_map[doc_id] = {**doc, "rrf_score": 0.0, "vector_rank": None, "fts_rank": rank}
        else:
            doc_map[doc_id]["fts_rank"] = rank
            
        doc_map[doc_id]["rrf_score"] += w_fts / (k + rank)

    # 3. Apply Recency Modification Exponential Time-Decay
    combined_results = list(doc_map.values())
    for doc in combined_results:
        mtime = doc.get("mtime") or doc.get("timestamp") or now
        if isinstance(mtime, (int, float)):
            delta_days = (now - mtime) / 86400.0
            recency_decay = math.exp(-time_decay_lambda * max(0.0, delta_days))
            doc["rrf_score"] *= recency_decay

    # 4. Sort by RRF score descending
    combined_results.sort(key=lambda x: x["rrf_score"], reverse=True)
    return combined_results
