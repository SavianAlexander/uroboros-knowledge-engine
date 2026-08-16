"""
LLM Inference infrastructure wrapper: Routes cleanly to local Ollama SLM engine.
Standard: Zero-dependency, pure Python standard library.
"""
import os
import logging
import functools
from typing import Optional, List, Dict, Any, Generator

logger = logging.getLogger(__name__)

MAX_CONTEXT = 4096
HAS_LLAMA = False

def get_fallback_llm():
    """Retrieve initialized Ollama model manager instance."""
    try:
        from src.core.model_manager import get_fallback_llm as mm_get_llm
        return mm_get_llm()
    except Exception as e:
        logger.debug(f"Ollama get_fallback_llm notice: {e}")
        return None

def is_llm_available() -> bool:
    """Check if local LLM engine is available and active."""
    return get_fallback_llm() is not None or os.environ.get("MOCK_LLM") == "1"

def require_llm():
    """Check LLM availability and raise NotImplementedError if unavailable."""
    if not is_llm_available():
        raise NotImplementedError("Local Ollama inference engine is not available on this system.")

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


def ensure_local_model_directory(models_dir: str = "models") -> Dict[str, Any]:
    """Ensures models directory exists and scans for available GGUF model files."""
    abs_dir = os.path.abspath(models_dir)
    os.makedirs(abs_dir, exist_ok=True)
    gguf_files = [f for f in os.listdir(abs_dir) if f.endswith(".gguf")]
    return {
        "status": "success",
        "models_dir": abs_dir,
        "available_models": gguf_files,
        "active_model": os.environ.get("LLM_MODEL_PATH", "models/llama-2-7b.Q4_K_M.gguf")
    }

