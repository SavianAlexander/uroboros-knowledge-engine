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


def text_to_token_bitpacks(text: str) -> List[int]:
    """
    Projects arbitrary text tokens into 64-bit binary bitpacks via cryptographic hashing.
    Enables sub-millisecond late-interaction token scoring on plain text without GPU dependencies.
    """
    if not text or not isinstance(text, str):
        return []
    
    import hashlib
    words = [w.strip() for w in text.lower().split() if w.strip()]
    bitpacks = []
    for w in words[:128]:
        # Generate 64-bit integer hash from token
        h = hashlib.sha256(w.encode("utf-8")).digest()
        # Take first 8 bytes as 64-bit integer
        val = int.from_bytes(h[:8], byteorder="big")
        bitpacks.append(val)
    return bitpacks


def rerank_search_results_colbert(query: str, results: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Reranks a list of search result dictionaries using Binary ColBERT MaxSim token late-interaction.
    """
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

        total_maxsim = 0.0
        for q_bits in q_bitpacks:
            min_h = 64
            for d_bits in d_bitpacks:
                dist = (q_bits ^ d_bits).bit_count()
                if dist < min_h:
                    min_h = dist
                    if min_h == 0:
                        break
            total_maxsim += (64.0 - min_h) / 64.0
        
        colbert_score = round(total_maxsim / float(len(q_bitpacks)), 4)
        # Blend existing score with ColBERT late-interaction score
        existing_score = float(item.get("score", 0.5) or 0.5)
        combined_score = round(0.4 * existing_score + 0.6 * colbert_score, 4)
        
        updated_item = dict(item)
        updated_item["colbert_maxsim_score"] = colbert_score
        updated_item["score"] = combined_score
        scored_results.append((combined_score, updated_item))

    # Sort descending by blended ColBERT score
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in scored_results[:top_k]]
