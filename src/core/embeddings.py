import json
import urllib.request
import urllib.error
import logging
import os
import math
import functools
from typing import List

# Default to the local docker-compose Ollama instance
OLLAMA_BASE_URL = os.environ.get("OPENAI_API_BASE", "http://host.docker.internal:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

@functools.lru_cache(maxsize=4096)
def generate_embedding(text: str) -> List[float]:
    """Generate dense vector embeddings via local Ollama instance (Zero-Dependency fallback)."""
    if not text or not text.strip():
        return []
        
    try:
        base = OLLAMA_BASE_URL.replace("/v1", "")
        url = f"{base}/api/embeddings"
        data = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": text[:4000],
            "keep_alive": "24h"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                res_body = json.loads(res.read().decode("utf-8"))
                return res_body.get("embedding", [])
        except urllib.error.URLError as url_err:
            if "host.docker.internal" in base or "getaddrinfo failed" in str(url_err):
                fallback_url = url.replace("host.docker.internal", "127.0.0.1")
                fallback_req = urllib.request.Request(fallback_url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(fallback_req, timeout=10) as res:
                    res_body = json.loads(res.read().decode("utf-8"))
                    return res_body.get("embedding", [])
            raise url_err
    except Exception as e:
        logging.warning(f"Failed to generate embedding via Ollama: {e}")
        return []

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Zero-dependency pure Python cosine similarity."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)
