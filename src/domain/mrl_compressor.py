"""
Matryoshka Representation Learning (MRL) Vector Truncation & Compression Engine.
Enables dynamic sub-dimension vector indexing (256d / 512d / 768d) with zero-dependency L2 re-normalization.
"""

import math
from typing import List, Dict, Any


def truncate_mrl_embedding(embedding: List[float], target_dim: int = 256) -> List[float]:
    """
    Truncates a high-dimensional vector (e.g., 1536d) to a Matryoshka sub-dimension (e.g., 256d)
    and applies L2 re-normalization.
    """
    if not embedding:
        return []
    
    sliced = embedding[:target_dim]
    norm = math.sqrt(sum(x * x for x in sliced))
    if norm == 0.0:
        return sliced
    
    return [round(x / norm, 6) for x in sliced]


def batch_compress_embeddings(embeddings: List[List[float]], target_dim: int = 256) -> List[List[float]]:
    """Compresses a batch of dense embeddings to target Matryoshka dimension."""
    return [truncate_mrl_embedding(emb, target_dim) for emb in embeddings]


def mrl_cosine_similarity(vec_a: List[float], vec_b: List[float], target_dim: int = 256) -> float:
    """Calculates cosine similarity on Matryoshka truncated vector slices."""
    trunc_a = truncate_mrl_embedding(vec_a, target_dim)
    trunc_b = truncate_mrl_embedding(vec_b, target_dim)
    
    min_len = min(len(trunc_a), len(trunc_b))
    if min_len == 0:
        return 0.0
    
    dot = sum(trunc_a[i] * trunc_b[i] for i in range(min_len))
    return round(dot, 4)
