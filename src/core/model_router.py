"""
Intelligent 4-Tier Neural Model Router for Ollama LLM integration.
Dynamically routes prompts to the optimal specialized model:
- Micro Tier (< 50ms): qwen2.5:0.5b / smollm2:1.7b (intent, keywords, hyde, auto-tags)
- Coder Tier (Expert Programming): qwen2.5-coder:14b / qwen2.5-coder:7b (AST, refactoring, SQL)
- Long-Context Tier (128k Context): phi4-mini:latest (large document digests > 8k tokens)
- Master RAG Tier (General Reasoning): qwen2.5:7b (conversational RAG, briefings)
"""
import os
import re
import json
import logging
import urllib.request
from typing import Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

# Regular expressions detecting technical / code-centric prompts
_RE_COMPLEX_CODE = re.compile(
    r'\b(def |class |import |from |function |const |let |var |async |await |return |'
    r'SELECT |INSERT |UPDATE |DELETE |CREATE TABLE|'
    r'refactor|architecture|syntax|regex|ast|algorithm|bug|traceback|exception|sql|quant)\b',
    re.IGNORECASE
)

# Regular expressions detecting micro / fast keyword tasks
_RE_MICRO_TASK = re.compile(
    r'\b(expand query|synonyms|generate keywords|extract tags|intent|classify|json entity|tag taxonomy)\b',
    re.IGNORECASE
)

_cached_available_models: Optional[Set[str]] = None
_last_probe_time: float = 0.0

def get_available_models(force_refresh: bool = False) -> Set[str]:
    """Probes the local Ollama daemon for installed model tags with 60s TTL cache."""
    global _cached_available_models, _last_probe_time
    import time
    now = time.time()
    if not force_refresh and _cached_available_models is not None and (now - _last_probe_time < 60.0):
        return _cached_available_models

    host = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:11434").replace("/v1", "").replace("host.docker.internal", "127.0.0.1")
    url = f"{host.rstrip('/')}/api/tags"
    discovered = set()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UroborosRouter"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                name = m.get("name", "")
                if name:
                    discovered.add(name)
                    # Also register base name without tag (e.g. 'qwen2.5:0.5b' and 'qwen2.5')
                    if ":" in name:
                        discovered.add(name.split(":")[0])
    except Exception as e:
        logger.debug(f"Ollama model probe notice: {e}")
        # Default known models on standard installation
        discovered = {"qwen2.5:7b", "qwen2.5-coder:14b", "qwen2.5-coder:7b", "qwen2.5:0.5b", "phi4-mini:latest", "smollm2:1.7b", "nomic-embed-text:latest"}

    _cached_available_models = discovered
    _last_probe_time = now
    return _cached_available_models


def _pick_best_available(candidates: list, default_model: str = "qwen2.5:7b") -> str:
    """Selects the first candidate present in Ollama's model tags, with graceful fallback."""
    available = get_available_models()
    for c in candidates:
        if c in available or (":" in c and c.split(":", 1)[0] in available):
            return c
    return os.environ.get("OLLAMA_MODEL", default_model)


def route_prompt_model(
    prompt: str = "",
    task_type: str = "auto",
    token_estimate: int = 0
) -> Dict[str, Any]:
    """
    Intelligent 4-Tier Neural Model Router.
    Analyzes prompt text, task category, and token density to select the optimal model.
    """
    default_master = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    raw_prompt = str(prompt or "").strip()
    word_count = len(raw_prompt.split()) if raw_prompt else 0

    # 1. LONG-CONTEXT TIER (> 8,000 tokens or explicit long_doc task)
    if task_type in ("long_doc", "book", "digest") or token_estimate > 8000:
        chosen = _pick_best_available(["phi4-mini:latest", "phi4-mini", "qwen2.5:7b"], default_master)
        return {
            "model": chosen,
            "tier": "long_context",
            "reason": f"high_token_volume_digest_{token_estimate}_tokens",
            "num_ctx": min(131072, max(8192, token_estimate + 2048)),
            "temperature": 0.2
        }

    # 2. MICRO TIER (Sub-50ms query expansion, auto-tagging, intent classification)
    if task_type in ("micro", "intent", "tag", "hyde", "expand", "keyword") or _RE_MICRO_TASK.search(raw_prompt):
        chosen = _pick_best_available(["qwen2.5:0.5b", "smollm2:1.7b", "qwen2.5:7b"], default_master)
        return {
            "model": chosen,
            "tier": "micro",
            "reason": "sub_50ms_fast_classification_and_expansion",
            "num_ctx": 4096,
            "temperature": 0.1
        }

    # 3. CODER TIER (Code analysis, AST refactoring, SQL generation, debugging)
    is_code = task_type in ("code", "ast", "refactor", "sql", "debug") or bool(_RE_COMPLEX_CODE.search(raw_prompt))
    if is_code:
        # Prefer 14B Coder for deep reasoning, fallback to 7B Coder or base 7B
        chosen = _pick_best_available(["qwen2.5-coder:14b", "qwen2.5-coder:7b", "qwen2.5:7b"], default_master)
        return {
            "model": chosen,
            "tier": "coder",
            "reason": "specialized_programming_and_ast_reasoning",
            "num_ctx": 8192 if token_estimate > 2000 else 4096,
            "temperature": 0.2
        }

    # 4. MASTER RAG TIER (Standard conversational RAG, daily briefings, executive summaries)
    chosen = _pick_best_available(["qwen2.5:7b"], default_master)
    return {
        "model": chosen,
        "tier": "master_rag",
        "reason": "balanced_conversational_rag",
        "num_ctx": 8192 if token_estimate > 2000 else 4096,
        "temperature": 0.3 if word_count > 50 else 0.7
    }
