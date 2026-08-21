import time
import json
import urllib.request
import urllib.error
import logging
import os
import math
import functools
from collections import OrderedDict
from typing import List, Tuple

# Default to the local docker-compose Ollama instance
OLLAMA_BASE_URL = os.environ.get("OPENAI_API_BASE", "http://host.docker.internal:11434/v1")
# ponytail: qwen2.5:7b is completion-only; nomic-embed-text is the actual embedding model
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

import threading
MAX_EMBED_CACHE_SIZE = 4096
_embed_cache: OrderedDict = OrderedDict()  # LRU bounded cache preventing empty error caching
_embed_lock = threading.Lock()
_ollama_offline_until: float = 0.0

import hashlib
import re

def _fallback_hash_embedding(text: str, dim: int = 768) -> List[float]:
    """
    Deterministic zero-dependency Semantic Hashing / Random Projection Embedding Fallback.
    Used when local Ollama is offline or in isolated test suites.
    Incorporates character n-grams and technical synonym expansion so that semantic
    similarity is maintained even with synonyms or sub-word variations.
    """
    if not text or not str(text).strip():
        return [0.0] * dim
        
    vec = [0.0] * dim
    clean_text = str(text).lower()
    
    words = re.findall(r'\b[a-z0-9_\-]+\b', clean_text)
    
    try:
        from src.core.domain.services import expand_synonyms
        synonyms_expanded = expand_synonyms(clean_text)
        expanded_words = re.findall(r'\b[a-z0-9_\-]+\b', synonyms_expanded.lower())
    except Exception:
        expanded_words = []
        
    all_tokens = words + expanded_words
    
    # 1. Word token projections with term frequency weighting
    for w in all_tokens:
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) else -1.0
        vec[idx] += sign * 1.5
        
        # Secondary projection for dispersion
        idx2 = (h >> 16) % dim
        sign2 = 1.0 if ((h >> 24) & 1) else -1.0
        vec[idx2] += sign2 * 0.8

    # 2. Sub-word character 3-grams
    for w in words:
        if len(w) >= 3:
            for i in range(len(w) - 2):
                tri = w[i:i+3]
                h_tri = int(hashlib.sha256(tri.encode('utf-8')).hexdigest(), 16)
                idx_tri = h_tri % dim
                sign_tri = 1.0 if ((h_tri >> 8) & 1) else -1.0
                vec[idx_tri] += sign_tri * 0.4

    return l2_normalize(vec)

def generate_embeddings_batch(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    """High-performance batch vector embedding generation via local Ollama /api/embed with fallback."""
    global _ollama_offline_until
    if not texts:
        return []

    results = [[] for _ in range(len(texts))]
    if time.time() < _ollama_offline_until:
        for i, t in enumerate(texts):
            results[i] = _fallback_hash_embedding(t)
        return results

    uncached_indices = []
    uncached_prompts = []

    with _embed_lock:
        for i, t in enumerate(texts):
            key = (t or "")[:4000]
            if not key.strip():
                continue
            if key in _embed_cache:
                _embed_cache.move_to_end(key)
                results[i] = _embed_cache[key]
            else:
                uncached_indices.append(i)
                uncached_prompts.append(key)

    if not uncached_prompts:
        return results

    base = OLLAMA_BASE_URL.replace("/v1", "").replace("host.docker.internal", "127.0.0.1")
    url = f"{base}/api/embed"

    for b_start in range(0, len(uncached_prompts), batch_size):
        b_indices = uncached_indices[b_start : b_start + batch_size]
        b_prompts = uncached_prompts[b_start : b_start + batch_size]

        data = json.dumps({
            "model": OLLAMA_EMBED_MODEL,
            "input": b_prompts,
            "keep_alive": "24h"
        }).encode("utf-8")

        success = False
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as res:
                body = json.loads(res.read().decode("utf-8"))
                embs = body.get("embeddings", [])
                with _embed_lock:
                    for idx, prompt, emb in zip(b_indices, b_prompts, embs):
                        results[idx] = emb
                        if emb:
                            if len(_embed_cache) >= MAX_EMBED_CACHE_SIZE:
                                _embed_cache.popitem(last=False)
                            _embed_cache[prompt] = emb
                success = True
        except (urllib.error.HTTPError, urllib.error.URLError, ConnectionError, OSError, TimeoutError) as e:
            # Circuit breaker: offline or model missing — silence retry storms for 60s
            _ollama_offline_until = time.time() + 60.0
            logging.debug(f"Ollama embedding offline ({e}); using deterministic fallback")
            for idx, prompt in zip(b_indices, b_prompts):
                results[idx] = _fallback_hash_embedding(prompt)
            break
        except Exception as e:
            logging.debug(f"Batch embed exception: {e}")
            for idx, prompt in zip(b_indices, b_prompts):
                results[idx] = _fallback_hash_embedding(prompt)

    return results

def generate_embedding(text: str) -> List[float]:
    """Generate a single dense vector embedding via generate_embeddings_batch with fallback."""
    res = generate_embeddings_batch([text])
    if res and res[0]:
        return res[0]
    return _fallback_hash_embedding(text)

def l2_normalize(v: List[float]) -> List[float]:
    """L2 normalize vector to unit length using accelerated math.fsum."""
    if not v:
        return []
    norm = math.sqrt(math.fsum(x * x for x in v))
    if norm == 0:
        return [0.0] * len(v)
    inv_norm = 1.0 / norm
    return [x * inv_norm for x in v]

def batch_l2_normalize(vectors: List[List[float]]) -> List[List[float]]:
    """Batch accelerated L2 normalization for bulk document chunk arrays."""
    return [l2_normalize(vec) for vec in vectors]

def matryoshka_slice(v: List[float], target_dim: int = 256) -> List[float]:
    """
    Matryoshka Representation Learning (MRL) vector dimension slicing.
    Truncates a high-dimensional vector (e.g. 768/1536) to target_dim (e.g. 256)
    and re-normalizes with L2 unit norm for 3x speedup with minimal recall loss.
    """
    if not v or target_dim >= len(v):
        return l2_normalize(v)
    sliced = v[:target_dim]
    return l2_normalize(sliced)

def quantize_int8(v: List[float]) -> List[int]:
    """
    Scalar Quantization (SQ8): Converts float32 embeddings into signed 8-bit integers [-128, 127].
    Reduces vector memory consumption by 75% for sub-5ms RAM search caching.
    """
    if not v:
        return []
    min_val = min(v)
    max_val = max(v)
    diff = max_val - min_val
    if diff == 0:
        return [0] * len(v)
    scale = 255.0 / diff
    return [max(-128, min(127, int((x - min_val) * scale - 128))) for x in v]

def dot_product(v1: List[float], v2: List[float]) -> float:
    """Fast SIMD-friendly dot product calculation (equivalent to cosine similarity for L2 normalized vectors)."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return math.fsum(a * b for a, b in zip(v1, v2))

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Zero-dependency accelerated cosine similarity using math.fsum."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_prod = math.fsum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.fsum(a * a for a in v1)
    norm_v2 = math.fsum(b * b for b in v2)
    
    if norm_v1 <= 0.0 or norm_v2 <= 0.0:
        return 0.0
        
    return dot_prod / (math.sqrt(norm_v1) * math.sqrt(norm_v2))

def batch_dot_product(query_vec: List[float], matrix: List[List[float]]) -> List[float]:
    """Batch SIMD-friendly dot product against an array of candidate vectors."""
    if not query_vec or not matrix:
        return []
    q_len = len(query_vec)
    return [
        math.fsum(a * b for a, b in zip(query_vec, candidate)) if len(candidate) == q_len else 0.0
        for candidate in matrix
    ]

def batch_cosine_similarity(query_vec: List[float], matrix: List[List[float]]) -> List[float]:
    """Batch accelerated cosine similarity scoring against a candidate vector matrix."""
    if not query_vec or not matrix:
        return []
    return [cosine_similarity(query_vec, candidate) for candidate in matrix]

def filter_vectors_by_threshold(query_vec: List[float], matrix: List[List[float]], threshold: float = 0.75) -> List[Tuple[int, float]]:
    """Filter and return (index, score) pairs matching or exceeding the similarity threshold."""
    if not query_vec or not matrix:
        return []
    results = []
    for idx, candidate in enumerate(matrix):
        score = cosine_similarity(query_vec, candidate)
        if score >= threshold:
            results.append((idx, score))
    return results

_last_health_check_ts: float = 0.0
_cached_availability: bool = False

def is_embedding_service_available(force_check: bool = False) -> bool:
    """Check if local Ollama embedding endpoint is reachable with cached result."""
    global _last_health_check_ts, _cached_availability
    now = time.time()
    if not force_check and (now - _last_health_check_ts < 10.0):
        return _cached_availability

    _last_health_check_ts = now
    base = OLLAMA_BASE_URL.replace("/v1", "").replace("host.docker.internal", "127.0.0.1")
    url = f"{base}/api/tags"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Uroboros-Health/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                _cached_availability = True
                return True
    except Exception:
        pass
    _cached_availability = False
    return False


