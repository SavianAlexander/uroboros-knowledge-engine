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
    """Memoized conversion of text token into a 64-bit integer bitpack via cryptographic hash."""
    h = hashlib.sha256(token_str.encode("utf-8")).digest()
    return int.from_bytes(h[:8], byteorder="big")


def _quantize_to_binary_bitpack(vector: List[float]) -> int:
    """Quantizes a float vector into a 64-bit integer bitpack based on sign (> 0 -> 1)."""
    if not vector or not isinstance(vector, (list, tuple)):
        return 0
    return _quantize_tuple_to_bitpack(tuple(vector[:64]))


def hamming_distance(bitpack_a: int, bitpack_b: int) -> int:
    """Computes Hamming distance between two 64-bit integer bitpacks via native C-level bit_count popcount."""
    a = int(bitpack_a) if isinstance(bitpack_a, (int, float)) else 0
    b = int(bitpack_b) if isinstance(bitpack_b, (int, float)) else 0
    return (a ^ b).bit_count()


def compute_maxsim_from_bitpacks(q_bitpacks: List[int], d_bitpacks: List[int]) -> float:
    """Core inner loop evaluating MaxSim directly on pre-quantized 64-bit integer token arrays."""
    if not q_bitpacks or not d_bitpacks:
        return 0.0
    
    total_maxsim = 0.0
    for q_bits in q_bitpacks:
        min_h_dist = 64
        for d_bits in d_bitpacks:
            h_dist = (q_bits ^ d_bits).bit_count()
            if h_dist < min_h_dist:
                min_h_dist = h_dist
                if min_h_dist == 0:
                    break
        total_maxsim += (64.0 - min_h_dist) / 64.0

    return round(total_maxsim / float(len(q_bitpacks)), 4)


def binary_colbert_maxsim(query_token_vecs: List[List[float]], doc_token_vecs: List[List[float]]) -> float:
    """Computes ColBERT MaxSim score over 1-bit quantized binary token vector matrices."""
    valid_q = [qv for qv in query_token_vecs if isinstance(qv, (list, tuple))]
    valid_d = [dv for dv in doc_token_vecs if isinstance(dv, (list, tuple))]
    if not valid_q or not valid_d:
        return 0.0

    q_bitpacks = [_quantize_to_binary_bitpack(qv) for qv in valid_q]
    d_bitpacks = [_quantize_to_binary_bitpack(dv) for dv in valid_d]
    if not q_bitpacks or not d_bitpacks:
        return 0.0

    return compute_maxsim_from_bitpacks(q_bitpacks, d_bitpacks)


def text_to_token_bitpacks(text: str) -> List[int]:
    """Projects text tokens into 64-bit binary bitpacks via cached cryptographic hashing."""
    if not text or not isinstance(text, str):
        return []
    words = [w.strip() for w in text.lower().split() if w.strip()]
    return [_token_to_64bitpack(w) for w in words[:128]]


def batch_binary_colbert_maxsim(query_bitpacks: List[int], doc_bitpacks_list: List[List[int]]) -> List[float]:
    """Evaluates ColBERT MaxSim across multiple document bitpack lists in a single vectorized pass."""
    if not query_bitpacks:
        return [0.0] * len(doc_bitpacks_list)
    return [compute_maxsim_from_bitpacks(query_bitpacks, d_bitpacks) for d_bitpacks in doc_bitpacks_list]


def rerank_search_results_colbert(query: str, results: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
    """Reranks search result dictionaries using Binary ColBERT MaxSim token late-interaction."""
    if not results or not query:
        return results or []

    q_bitpacks = text_to_token_bitpacks(query)
    if not q_bitpacks:
        return results

    scored_results = []
    for item in results:
        snippet = item.get("snippet", "") or item.get("content", "") or item.get("title", "") or ""
        d_bitpacks = text_to_token_bitpacks(snippet)
        if not d_bitpacks:
            scored_results.append((item.get("score", 0.0), item))
            continue

        colbert_score = compute_maxsim_from_bitpacks(q_bitpacks, d_bitpacks)
        existing_score = float(item.get("score", 0.5) or 0.5)
        combined_score = round(0.4 * existing_score + 0.6 * colbert_score, 4)
        
        updated_item = dict(item)
        updated_item["colbert_maxsim_score"] = colbert_score
        updated_item["score"] = combined_score
        scored_results.append((combined_score, updated_item))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in scored_results[:top_k]]


# ==============================================================================
# 3. Dynamic Sparse-Dense-ColBERT Fusion
# ==============================================================================

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
