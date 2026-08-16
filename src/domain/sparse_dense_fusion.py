"""
Sparse-Dense-ColBERT Fusion Reranker Engine.
Calculates optimal alpha (sparse), beta (dense), and gamma (ColBERT) scalars per query intent.
Standard: Pure Python standard library (unicodedata, typing).
"""
import unicodedata
from typing import Dict, Any, List


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
    """
    Reranks chunks using dynamic alpha (sparse), beta (dense), and gamma (ColBERT) scalars.
    """
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


# Facade alias
fuse_sparse_dense_rankings = rerank_sparse_dense_fusion
