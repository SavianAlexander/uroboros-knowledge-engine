"""
Intelligent 5-Tier Neural Model Router for Ollama SLM/LLM integration.
Standard: Pure Python Standard Library (urllib, re, json, logging)
Ponytail Senior Dev Principle: Min-maxed intelligence-per-watt routing to ultra-lean 2-3GB specialized models:
- Logic & Reasoning Tier: deepseek-r1:1.5b / phi4-mini (Chain-of-thought, self-correction, math, planning)
- Coder Tier: qwen2.5-coder:3b / qwen2.5-coder:7b (AST code analysis, refactoring, SQL, diffs)
- Long-Context Tier (128k): phi4-mini:latest (large document digests, book analysis > 8k tokens)
- Micro Tier (< 30ms): qwen2.5:0.5b / smollm2:1.7b (intent classification, keywords, hyde, auto-tags)
- Master RAG Tier: phi4-mini:latest / qwen2.5:7b (conversational RAG, briefings, general QA)
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

# Regular expressions detecting deep reasoning / logic tasks
_RE_LOGIC_TASK = re.compile(
    r'\b(think|reason|step by step|proof|math|diagnose|root cause|deduce|logic|why did|evaluate plan|tot|tree of thoughts|cove|chain of verification)\b',
    re.IGNORECASE
)

# Regular expressions detecting high-complexity / multi-architecture escalation
_RE_FRONTIER_COMPLEXITY = re.compile(
    r'\b(monolithic refactor|multi-file architecture|cross-system protocol|mathematical proof|'
    r'concurrency race condition|deadlock prevention|formal verification|invariant proof|'
    r'frontier reasoning|tree of thoughts|mcts|multi-agent orchestration)\b',
    re.IGNORECASE
)

import threading

_cached_available_models: Optional[Set[str]] = None
_last_probe_time: float = 0.0
_probe_lock = threading.Lock()

def get_available_models(force_refresh: bool = False) -> Set[str]:
    """Probes the local Ollama daemon for installed model tags with 60s TTL cache."""
    global _cached_available_models, _last_probe_time
    import time
    now = time.time()
    with _probe_lock:
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

    if not discovered:
        discovered = {"deepseek-r1:1.5b", "qwen2.5-coder:3b", "phi4-mini:latest", "qwen2.5:0.5b", "qwen2.5:7b", "nomic-embed-text:latest"}

    _cached_available_models = discovered
    _last_probe_time = now
    return _cached_available_models


def _pick_best_available(candidates: list, default_model: str = "phi4-mini:latest") -> str:
    """Selects the first candidate present in Ollama's model tags, with graceful fallback."""
    available = get_available_models()
    for c in candidates:
        if c in available or (":" in c and c.split(":", 1)[0] in available):
            return c
    return os.environ.get("OLLAMA_MODEL", default_model)


def calculate_reasoning_complexity(
    prompt: str = "",
    task_type: str = "auto",
    token_estimate: int = 0
) -> Dict[str, Any]:
    """
    Computes empirical reasoning complexity score (0.0 to 1.0) and determines
    whether the task is eligible for Frontier (Google Gemini / Anthropic Claude / Antigravity) escalation.
    """
    raw_prompt = str(prompt or "").strip()
    words = raw_prompt.split()
    word_count = len(words)

    score = 0.1  # baseline

    # Token volume factor
    if token_estimate > 6000 or word_count > 600:
        score += 0.35
    elif token_estimate > 2000 or word_count > 200:
        score += 0.20

    # Logic & reasoning indicators
    if _RE_LOGIC_TASK.search(raw_prompt):
        score += 0.25

    # Code / architecture indicators
    if _RE_COMPLEX_CODE.search(raw_prompt):
        score += 0.20

    # Frontier complexity indicators
    if _RE_FRONTIER_COMPLEXITY.search(raw_prompt):
        score += 0.35

    # Task type overrides
    if task_type in ("reason", "logic", "proof", "tot", "cove"):
        score += 0.20
    elif task_type in ("micro", "tag", "intent", "keyword"):
        score = min(score, 0.25)

    final_score = round(min(1.0, max(0.05, score)), 2)
    is_frontier_eligible = final_score >= 0.70

    suggested_engine = "local_slm"
    if final_score >= 0.85:
        suggested_engine = "claude-3.7-sonnet"
    elif final_score >= 0.70:
        suggested_engine = "gemini-3.7-flash"

    return {
        "complexity_score": final_score,
        "frontier_escalation_eligible": is_frontier_eligible,
        "suggested_frontier_engine": suggested_engine,
        "confidence_tier": "frontier_recommended" if is_frontier_eligible else "local_optimal"
    }


def route_prompt_model(
    prompt: str = "",
    task_type: str = "auto",
    token_estimate: int = 0
) -> Dict[str, Any]:
    """
    Intelligent 5-Tier Neural Model Router with Frontier Escalation Gate.
    Analyzes prompt text, task category, and token density to select the optimal model.
    """
    default_master = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    raw_prompt = str(prompt or "").strip()
    word_count = len(raw_prompt.split()) if raw_prompt else 0

    complexity_meta = calculate_reasoning_complexity(raw_prompt, task_type=task_type, token_estimate=token_estimate)

    # 1. LONG-CONTEXT TIER (> 8,000 tokens or explicit long_doc task)
    if task_type in ("long_doc", "book", "digest") or token_estimate > 8000:
        chosen = _pick_best_available(["phi4-mini:latest", "phi4-mini", "qwen2.5:7b"], default_master)
        res = {
            "model": chosen,
            "tier": "long_context",
            "reason": f"high_token_volume_digest_{token_estimate}_tokens",
            "num_ctx": min(131072, max(8192, token_estimate + 2048)),
            "temperature": 0.2
        }
        res.update(complexity_meta)
        return res

    # 2. MICRO TIER (Sub-30ms query expansion, auto-tagging, intent classification)
    if task_type in ("micro", "intent", "tag", "hyde", "expand", "keyword") or _RE_MICRO_TASK.search(raw_prompt):
        chosen = _pick_best_available(["qwen2.5:0.5b", "smollm2:1.7b", "phi4-mini:latest"], default_master)
        res = {
            "model": chosen,
            "tier": "micro",
            "reason": "sub_30ms_fast_classification_and_expansion",
            "num_ctx": 4096,
            "temperature": 0.1
        }
        res.update(complexity_meta)
        return res

    # 3. REASONING & LOGIC TIER (Chain-of-thought, mathematical deduction, diagnosis)
    is_reasoning = task_type in ("reason", "logic", "think", "diagnose", "plan", "tot", "cove") or bool(_RE_LOGIC_TASK.search(raw_prompt))
    if is_reasoning:
        chosen = _pick_best_available(["deepseek-r1:1.5b", "phi4-mini:latest", "qwen2.5:7b"], default_master)
        res = {
            "model": chosen,
            "tier": "reasoning",
            "reason": "chain_of_thought_self_verifying_logic",
            "num_ctx": 8192 if token_estimate > 2000 else 4096,
            "temperature": 0.6
        }
        res.update(complexity_meta)
        return res

    # 4. CODER TIER (Code analysis, AST refactoring, SQL generation, debugging)
    is_code = task_type in ("code", "ast", "refactor", "sql", "debug") or bool(_RE_COMPLEX_CODE.search(raw_prompt))
    if is_code:
        chosen = _pick_best_available(["qwen2.5-coder:3b", "qwen2.5-coder:7b", "qwen2.5-coder:14b", "phi4-mini:latest"], default_master)
        res = {
            "model": chosen,
            "tier": "coder",
            "reason": "specialized_programming_and_ast_reasoning",
            "num_ctx": 8192 if token_estimate > 2000 else 4096,
            "temperature": 0.2
        }
        res.update(complexity_meta)
        return res

    # 5. MASTER RAG TIER (Standard conversational RAG, daily briefings, executive summaries)
    chosen = _pick_best_available(["qwen2.5:7b", "phi4-mini:latest"], default_master)
    res = {
        "model": chosen,
        "tier": "master_rag",
        "reason": "balanced_conversational_rag",
        "num_ctx": 8192 if token_estimate > 2000 else 4096,
        "temperature": 0.3 if word_count > 50 else 0.7
    }
    res.update(complexity_meta)
    return res
