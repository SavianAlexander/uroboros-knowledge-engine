"""
Matryoshka Representation Learning (MRL) Vector Truncation & Compression Engine.
Delegates directly to src.core.embeddings for zero-dependency vector dimension slicing.
"""
from typing import List
from src.core.embeddings import matryoshka_slice, dot_product

# Primary delegation aliases
truncate_mrl_embedding = matryoshka_slice


def batch_compress_embeddings(embeddings: List[List[float]], target_dim: int = 256) -> List[List[float]]:
    """Compresses a batch of dense embeddings to target Matryoshka dimension."""
    return [matryoshka_slice(emb, target_dim) for emb in embeddings]


def mrl_cosine_similarity(vec_a: List[float], vec_b: List[float], target_dim: int = 256) -> float:
    """Calculates cosine similarity on Matryoshka truncated vector slices."""
    if not vec_a or not vec_b:
        return 0.0
    trunc_a = matryoshka_slice(vec_a, target_dim)
    trunc_b = matryoshka_slice(vec_b, target_dim)
    return round(dot_product(trunc_a, trunc_b), 4)
