"""
LLM Inference infrastructure wrapper with safe try-except import guards for llama_cpp.
Includes LRU caching, context window bounding, and stream generation.
"""

import os
import functools
from typing import Optional, List, Dict, Any, Generator

HAS_LLAMA = False
try:
    import llama_cpp
    HAS_LLAMA = True
except Exception:
    HAS_LLAMA = False

_llm_instance = None
MAX_CONTEXT = 2048

def get_fallback_llm():
    """Retrieve initialized Llama instance or None if unavailable."""
    global _llm_instance, HAS_LLAMA
    if not HAS_LLAMA:
        return None
    if _llm_instance is not None:
        return _llm_instance
    try:
        model_path = os.environ.get("LLM_MODEL_PATH", "models/llama-2-7b.Q4_K_M.gguf")
        if os.path.exists(model_path):
            _llm_instance = llama_cpp.Llama(model_path=model_path, n_ctx=MAX_CONTEXT, verbose=False)
            return _llm_instance
    except Exception:
        pass
    return None

def is_llm_available() -> bool:
    """Check if llama_cpp engine is available and active."""
    return HAS_LLAMA and (get_fallback_llm() is not None or os.environ.get("MOCK_LLM") == "1")

def require_llm():
    """Check LLM availability and raise NotImplementedError if unavailable."""
    if not is_llm_available():
        raise NotImplementedError("Local LLM inference module (llama_cpp) is not available on this system.")

def _enforce_context_window(prompt: str, max_tokens: int) -> str:
    """Truncate the prompt if it exceeds the estimated context window limit."""
    # Rough estimation: 1 token ~= 4 characters
    max_chars = (MAX_CONTEXT - max_tokens - 100) * 4
    if len(prompt) > max_chars:
        # Keep the start and end of the prompt, stripping the middle to preserve instructions
        half = max_chars // 2
        return prompt[:half] + "\n...[TRUNCATED_CONTEXT]...\n" + prompt[-half:]
    return prompt

@functools.lru_cache(maxsize=128)
def generate_cached_completion(prompt: str, max_tokens: int = 150) -> str:
    """Generate completion with LRU caching for deterministic AI tasks (tagging, classification)."""
    require_llm()
    prompt = _enforce_context_window(prompt, max_tokens)
    
    if os.environ.get("MOCK_LLM") == "1":
        return f"[MOCK_CACHED_RESPONSE] Length: {len(prompt)}"
        
    llm = get_fallback_llm()
    response = llm(prompt, max_tokens=max_tokens, echo=False, stream=False)
    return response["choices"][0]["text"].strip()

def stream_completion(prompt: str, max_tokens: int = 500) -> Generator[str, None, None]:
    """Generate completion and yield token chunks for real-time SSE streaming."""
    require_llm()
    prompt = _enforce_context_window(prompt, max_tokens)
    
    if os.environ.get("MOCK_LLM") == "1":
        yield "[MOCK_STREAM] Hello "
        yield "world! "
        yield "This is a stream."
        return
        
    llm = get_fallback_llm()
    for chunk in llm(prompt, max_tokens=max_tokens, echo=False, stream=True):
        yield chunk["choices"][0]["text"]

