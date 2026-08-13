"""
ColBERT Late Interaction Reranker Engine.
Computes token-level MaxSim similarity matrices between query and document token vectors.
Zero-dependency, stdlib-first math implementation.
"""

import math
from typing import List, Dict, Any


def dot_product(v1: List[float], v2: List[float]) -> float:
    """Calculates dot product of two equal-length float vectors."""
    min_len = min(len(v1), len(v2))
    if min_len == 0:
        return 0.0
    return sum(v1[i] * v2[i] for i in range(min_len))


def normalize_vector(v: List[float]) -> List[float]:
    """Applies L2 normalization to a vector."""
    if not v or not isinstance(v, (list, tuple)):
        return []
    norm = math.sqrt(sum(x * x for x in v if isinstance(x, (int, float))))
    if norm == 0.0:
        return list(v)
    return [round(x / norm, 6) for x in v if isinstance(x, (int, float))]


def colbert_maxsim_score(query_token_embeddings: List[List[float]], doc_token_embeddings: List[List[float]]) -> float:
    """
    Computes ColBERT Late Interaction MaxSim score:
    Score = sum_{i in QueryTokens} max_{j in DocTokens} (E_q_i . E_d_j)
    """
    if not query_token_embeddings or not doc_token_embeddings:
        return 0.0

    total_score = 0.0
    for q_emb in query_token_embeddings:
        q_norm = normalize_vector(q_emb)
        max_sim = max(
            dot_product(q_norm, normalize_vector(d_emb))
            for d_emb in doc_token_embeddings
        )
        total_score += max_sim

    # Normalize by query length for fair candidate comparisons
    return round(total_score / len(query_token_embeddings), 4)


def rerank_documents_colbert(
    query_tokens: List[List[float]],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Reranks document candidates using token-level ColBERT MaxSim scores.
    Each candidate dictionary should contain 'token_embeddings' and 'content' / 'filepath'.
    """
    reranked = []
    for cand in candidates:
        doc_tokens = cand.get("token_embeddings", [])
        if not doc_tokens:
            score = cand.get("score", 0.0)
        else:
            score = colbert_maxsim_score(query_tokens, doc_tokens)
        
        cand_copy = dict(cand)
        cand_copy["colbert_maxsim_score"] = score
        reranked.append(cand_copy)

    reranked.sort(key=lambda x: x["colbert_maxsim_score"], reverse=True)
    return reranked
