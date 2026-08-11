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
OLLAMA_MODEL = "nomic-embed-text" # Standard small embedding model on ollama

@functools.lru_cache(maxsize=4096)
def generate_embedding(text: str) -> List[float]:
    """Generate dense vector embeddings via local Ollama instance (Zero-Dependency fallback)."""
    if not text or not text.strip():
        return []
        
    try:
        # Check if we should use Ollama directly via its native API (faster than v1 compat layer)
        base = OLLAMA_BASE_URL.replace("/v1", "")
        url = f"{base}/api/embeddings"
        data = json.dumps({"model": OLLAMA_MODEL, "prompt": text[:4000]}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as res:
            res_body = json.loads(res.read().decode("utf-8"))
            return res_body.get("embedding", [])
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
