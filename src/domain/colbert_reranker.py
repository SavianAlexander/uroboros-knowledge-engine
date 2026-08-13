"""
ColBERT Late Interaction Reranker Engine.
Computes token-level MaxSim similarity matrices between query and document token vectors.
Zero-dependency, stdlib-first math implementation.
"""
import math
import functools
from typing import List, Dict, Any, Tuple

def dot_product(v1: List[float], v2: List[float]) -> float:
    """Calculates dot product of two equal-length float vectors."""
    min_len = min(len(v1), len(v2))
    if min_len == 0:
        return 0.0
    return sum(v1[i] * v2[i] for i in range(min_len))


@functools.lru_cache(maxsize=4096)
def _normalize_vector_cached(v_tuple: Tuple[float, ...]) -> Tuple[float, ...]:
    norm = math.sqrt(sum(x * x for x in v_tuple if isinstance(x, (int, float))))
    if norm == 0.0:
        return tuple(0.0 for x in v_tuple if isinstance(x, (int, float)))
    return tuple(round(x / norm, 6) for x in v_tuple if isinstance(x, (int, float)))


def normalize_vector(v: List[float]) -> List[float]:
    """Applies L2 normalization to a vector."""
    if not v or not isinstance(v, (list, tuple)):
        return []
    return list(_normalize_vector_cached(tuple(v)))


def colbert_maxsim_score(query_token_embeddings: List[List[float]], doc_token_embeddings: List[List[float]]) -> float:
    """
    Computes ColBERT Late Interaction MaxSim score:
    Score = sum_{i in QueryTokens} max_{j in DocTokens} (E_q_i . E_d_j)
    """
    if not query_token_embeddings or not doc_token_embeddings:
        return 0.0
    if not isinstance(query_token_embeddings, (list, tuple)) or not isinstance(doc_token_embeddings, (list, tuple)):
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

    if valid_query_tokens == 0:
        return 0.0

    # Normalize by valid query token length for fair candidate comparisons
    return round(total_score / float(valid_query_tokens), 4)


def _safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def rerank_documents_colbert(
    query_tokens: List[List[float]],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Reranks document candidates using token-level ColBERT MaxSim scores.
    Each candidate dictionary should contain 'token_embeddings' and 'content' / 'filepath'.
    """
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
