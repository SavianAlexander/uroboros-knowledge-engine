"""
Unified Search Reranking & Score Fusion Engine.
Consolidates Reciprocal Rank Fusion (RRF), Binary ColBERT Late-Interaction MaxSim,
Sparse-Dense dynamic scalar fusion, and candidate score explanation.
Standard: Zero-dependency, pure Python standard library (math, time, hashlib, functools, unicodedata, typing).
"""

import math
import time
import hashlib
import functools
import unicodedata
from typing import List, Dict, Any, Optional, Tuple, Set


# ==============================================================================
# 1. Reciprocal Rank Fusion (RRF)
# ==============================================================================

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


reciprocal_rank_fusion = compute_rrf_scores
score_rerank_candidates = compute_rrf_scores


# ==============================================================================
# 2. Binary ColBERT Late-Interaction MaxSim
# ==============================================================================

@functools.lru_cache(maxsize=8192)
def _quantize_tuple_to_bitpack(vec_tuple: Tuple[float, ...]) -> int:
    bitpack = 0
    for i, val in enumerate(vec_tuple[:64]):
        if isinstance(val, (int, float)) and val > 0.0:
            bitpack |= (1 << i)
    return bitpack


@functools.lru_cache(maxsize=16384)
def _token_to_64bitpack(token_str: str) -> int:
    """
    Locality-Sensitive Hashing (LSH) bitpack projection of text tokens using character n-grams.
    Preserves lexical, morphological, and stem similarity in Hamming space for accurate MaxSim scoring.
    """
    clean = unicodedata.normalize("NFC", str(token_str or "").lower().strip())
    if not clean:
        return 0
    
    bitpack = 0
    # Whole-word seed
    h_word = (hash(clean) ^ 0x5555555555555555) & 0xFFFFFFFFFFFFFFFF
    bitpack |= (1 << (h_word % 64))

    # Prefix and suffix anchors
    if len(clean) >= 3:
        prefix_h = (hash(clean[:3]) ^ 0xAAAAAAAAAAAAAAA) & 0x3F
        suffix_h = (hash(clean[-3:]) ^ 0x555555555555555) & 0x3F
        bitpack |= (1 << prefix_h) | (1 << suffix_h)

    # Character n-grams (2-gram and 3-gram) LSH features
    for n in (2, 3):
        if len(clean) >= n:
            for i in range(len(clean) - n + 1):
                gram = clean[i : i + n]
                pos = hash(gram) & 0x3F
                bitpack |= (1 << pos)

    return bitpack


from src.domain.binary_colbert import (
    _quantize_to_binary_bitpack,
    quantize_embeddings_batch,
    hamming_distance,
    compute_maxsim_from_bitpacks,
    binary_colbert_maxsim,
    text_to_token_bitpacks,
    batch_binary_colbert_maxsim,
    rerank_search_results_colbert,
)



def dot_product(v1: List[float], v2: List[float]) -> float:
    """Calculates dot product of two equal-length float vectors."""
    if not v1 or not v2:
        return 0.0
    return sum(x * y for x, y in zip(v1, v2))


def normalize_vector(v: List[float]) -> List[float]:
    """Applies L2 normalization to a vector."""
    if not v or not isinstance(v, (list, tuple)):
        return []
    norm = math.sqrt(sum(x * x for x in v if isinstance(x, (int, float))))
    if norm == 0.0:
        return [0.0] * len(v)
    return [round(x / norm, 6) for x in v if isinstance(x, (int, float))]


def colbert_maxsim_score(query_token_embeddings: List[List[float]], doc_token_embeddings: List[List[float]]) -> float:
    """Computes ColBERT Late Interaction MaxSim score across token embeddings."""
    if not query_token_embeddings or not doc_token_embeddings:
        return 0.0
    normalized_docs = [normalize_vector(d) for d in doc_token_embeddings if d and isinstance(d, (list, tuple))]
    if not normalized_docs:
        return 0.0
    total_score = 0.0
    valid_query_tokens = 0
    for q_emb in query_token_embeddings:
        if not q_emb or not isinstance(q_emb, (list, tuple)):
            continue
        q_norm = normalize_vector(q_emb)
        max_sim = -1.0
        for d_norm in normalized_docs:
            sim = dot_product(q_norm, d_norm)
            if sim > max_sim:
                max_sim = sim
                if max_sim >= 0.9999:
                    break
        if max_sim > -1.0:
            total_score += max_sim
            valid_query_tokens += 1
    return round(total_score / float(valid_query_tokens), 4) if valid_query_tokens > 0 else 0.0


def rerank_documents_colbert(
    query_tokens: List[List[float]],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Reranks document candidates using token-level ColBERT MaxSim scores."""
    if not candidates or not isinstance(candidates, list):
        return []
    valid_candidates = [c for c in candidates if isinstance(c, dict)]
    reranked = []
    for cand in valid_candidates:
        doc_tokens = cand.get("token_embeddings", [])
        if not doc_tokens:
            score = _safe_float(cand.get("score"), 0.0)
        else:
            score = colbert_maxsim_score(query_tokens, doc_tokens)
        cand_copy = dict(cand)
        cand_copy["colbert_maxsim_score"] = score
        reranked.append(cand_copy)
    reranked.sort(key=lambda x: x["colbert_maxsim_score"], reverse=True)
    return reranked


def _safe_float(val, default=0.5):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def rerank_sparse_dense_fusion(
    query: str,
    candidate_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Reranks chunks using dynamic alpha (sparse), beta (dense), and gamma (ColBERT) scalars."""
    safe_query = str(query or "")
    if not candidate_chunks or not isinstance(candidate_chunks, list):
        return {"reranked_chunks": [], "status": "empty_input"}

    valid_chunks = [c for c in candidate_chunks if isinstance(c, dict)]
    if not valid_chunks:
        return {"reranked_chunks": [], "status": "empty_input"}

    norm_query = unicodedata.normalize("NFC", safe_query)
    is_code = "def " in norm_query or "class " in norm_query or "import " in norm_query
    is_legal = "policy" in norm_query.lower() or "contract" in norm_query.lower()

    if is_code:
        alpha, beta, gamma = 0.5, 0.2, 0.3
    elif is_legal:
        alpha, beta, gamma = 0.2, 0.3, 0.5
    else:
        alpha, beta, gamma = 0.3, 0.4, 0.3

    reranked = []
    for chunk in valid_chunks:
        text = chunk.get("text", "")
        s_raw = chunk.get("sparse_score")
        d_raw = chunk.get("dense_score")
        c_raw = chunk.get("colbert_score")

        sparse_score = _safe_float(s_raw, 0.5)
        dense_score = _safe_float(d_raw, 0.6)
        colbert_score = _safe_float(c_raw, 0.7)

        fused_score = (alpha * sparse_score) + (beta * dense_score) + (gamma * colbert_score)
        reranked.append({
            "chunk_id": chunk.get("id", "chk_0"),
            "text": text,
            "fused_score": round(fused_score, 4),
            "scalars": {"alpha": alpha, "beta": beta, "gamma": gamma}
        })

    reranked.sort(key=lambda x: x["fused_score"], reverse=True)

    return {
        "query": query,
        "reranked_chunks": reranked,
        "computed_weights": {"alpha": alpha, "beta": beta, "gamma": gamma},
        "status": "success"
    }


fuse_sparse_dense_rankings = rerank_sparse_dense_fusion


# ==============================================================================
# 4. Score Deconstruction Explainer
# ==============================================================================

def explain_candidate_score(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Deconstructs candidate search score into component weights and explanations."""
    if not candidate or not isinstance(candidate, dict):
        candidate = {}
    raw_name = str(candidate.get("filename") or "document.md")
    filename = unicodedata.normalize("NFC", raw_name)
    try:
        fts_rank = int(candidate.get("fts_rank", 1))
    except (ValueError, TypeError):
        fts_rank = 1

    try:
        pagerank_score = float(candidate.get("pagerank_score", 0.001))
    except (ValueError, TypeError):
        pagerank_score = 0.001

    try:
        recency_multiplier = float(candidate.get("recency_multiplier", 1.0))
    except (ValueError, TypeError):
        recency_multiplier = 1.0

    try:
        final_score = float(candidate.get("final_score") or candidate.get("rrf_score") or 0.05)
    except (ValueError, TypeError):
        final_score = 0.05

    bm25_weight = round(1.0 / (60.0 + fts_rank), 6)
    pr_boost = round(pagerank_score * 10.0, 6)

    explanation = (
        f"Document '{filename}' achieved a Final Score of {final_score:.6f}.\n"
        f"• Keyword FTS5 BM25 Rank #{fts_rank} contributed {bm25_weight:.6f} points.\n"
        f"• Knowledge Graph PageRank Centrality ({pagerank_score:.6f}) contributed a boost of {pr_boost:.6f} points.\n"
        f"• Recency Time-Decay Multiplier applied: {recency_multiplier:.4f}x."
    )

    return {
        "filename": filename,
        "final_score": final_score,
        "score_components": {
            "bm25_weight": bm25_weight,
            "pagerank_boost": pr_boost,
            "recency_multiplier": recency_multiplier
        },
        "explanation": explanation,
        "status": "success"
    }
