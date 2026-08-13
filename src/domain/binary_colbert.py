"""
Binary ColBERT MaxSim Late-Interaction Reranking Engine.
Computes token-level late-interaction similarity matrices using 1-bit binary vector quantization.
Zero-dependency, stdlib implementation.
"""
import functools
from typing import Tuple, List, Dict, Any, Optional

@functools.lru_cache(maxsize=4096)
def _quantize_tuple_to_bitpack(vec_tuple: Tuple[float, ...]) -> int:
    bitpack = 0
    for i, val in enumerate(vec_tuple[:64]):
        if isinstance(val, (int, float)) and val > 0.0:
            bitpack |= (1 << i)
    return bitpack


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


def binary_colbert_maxsim(query_token_vecs: List[List[float]], doc_token_vecs: List[List[float]]) -> float:
    """
    Computes ColBERT MaxSim score over 1-bit quantized binary token vector matrices.
    MaxSim = sum over query tokens of max(similarity with doc tokens).
    # ponytail: zero-dependency binary ColBERT MaxSim late interaction; ceiling: Python bitpack SIMD emulation; upgrade: bind C++/AVX-512 popcount extension if sub-millisecond 100k token reranking is required
    """
    valid_q = [qv for qv in query_token_vecs if isinstance(qv, (list, tuple))]
    valid_d = [dv for dv in doc_token_vecs if isinstance(dv, (list, tuple))]
    if not valid_q or not valid_d:
        return 0.0

    q_bitpacks = [_quantize_to_binary_bitpack(qv) for qv in valid_q]
    d_bitpacks = [_quantize_to_binary_bitpack(dv) for dv in valid_d]
    if not q_bitpacks:
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
        max_sim = (64.0 - min_h_dist) / 64.0
        total_maxsim += max_sim

    return round(total_maxsim / float(len(q_bitpacks)), 4)
