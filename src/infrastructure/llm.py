"""
LLM Inference infrastructure wrapper with safe try-except import guards for llama_cpp.
Handles fallback and raises 501 NotImplemented if llama_cpp is missing or unavailable.
"""

import os
from typing import Optional, List, Dict, Any

HAS_LLAMA = False
try:
    import llama_cpp
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False

_llm_instance = None

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
            _llm_instance = llama_cpp.Llama(model_path=model_path, n_ctx=2048, verbose=False)
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
