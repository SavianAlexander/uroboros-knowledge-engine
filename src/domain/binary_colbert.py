"""
Binary ColBERT MaxSim Late-Interaction Reranking Engine.
Computes token-level late-interaction similarity matrices using 1-bit binary vector quantization.
Zero-dependency, stdlib implementation.
"""

import math
from typing import Dict, Any, List, Tuple


def _quantize_to_binary_bitpack(vector: List[float]) -> int:
    """Quantizes a float vector into a 64-bit integer bitpack based on sign (> 0 -> 1)."""
    bitpack = 0
    for i, val in enumerate(vector[:64]):
        if val > 0.0:
            bitpack |= (1 << i)
    return bitpack


def hamming_distance(bitpack_a: int, bitpack_b: int) -> int:
    """Computes Hamming distance between two 64-bit integer bitpacks via XOR bit count."""
    return bin(bitpack_a ^ bitpack_b).count('1')


def binary_colbert_maxsim(query_token_vecs: List[List[float]], doc_token_vecs: List[List[float]]) -> float:
    """
    Computes ColBERT MaxSim score over 1-bit quantized binary token vector matrices.
    MaxSim = sum over query tokens of max(similarity with doc tokens).
    # ponytail: zero-dependency binary ColBERT MaxSim late interaction
    """
    if not query_token_vecs or not doc_token_vecs:
        return 0.0

    q_bitpacks = [_quantize_to_binary_bitpack(qv) for qv in query_token_vecs]
    d_bitpacks = [_quantize_to_binary_bitpack(dv) for dv in doc_token_vecs]

    total_maxsim = 0.0
    for q_bits in q_bitpacks:
        max_sim = 0.0
        for d_bits in d_bitpacks:
            # Similarity derived from inverted normalized Hamming distance (64 - hamming) / 64
            h_dist = hamming_distance(q_bits, d_bits)
            sim = (64.0 - h_dist) / 64.0
            if sim > max_sim:
                max_sim = sim
        total_maxsim += max_sim

    return round(total_maxsim / float(len(q_bitpacks)), 4)
