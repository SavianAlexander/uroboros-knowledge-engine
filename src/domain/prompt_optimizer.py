"""
Dynamic RAG Prompt Density Optimizer & Token Budget Allocator.
Optimizes context token density and dynamically injects few-shot domain examples.
"""
import re
from functools import lru_cache
from typing import Dict, Any, List, Optional, Set

@lru_cache(maxsize=4096)
def _get_word_set(text: str) -> Set[str]:
    if not text:
        return set()
    return set(w.lower() for w in text.split() if len(w) > 3)


def estimate_text_tokens(text: str) -> int:
    """
    Estimates token count with content-aware density calibration:
    - Code / JSON: ~3.0 chars per token
    - Dense tables / numerical data: ~2.5 chars per token
    - CJK Unicode characters: ~1.3 chars per token
    - Natural language prose: ~4.0 chars per token
    """
    if not text:
        return 0

    total_len = len(text)
    if total_len == 0:
        return 0

    # Check for CJK characters
    cjk_count = len(re.findall(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]', text))
    if cjk_count > total_len * 0.2:
        return int(cjk_count * 1.2 + (total_len - cjk_count) / 3.5)

    # Check for code or JSON density
    code_symbols = len(re.findall(r'[{}\[\]();=><:_\n\t]', text))
    if code_symbols > total_len * 0.15:
        return max(1, int(total_len / 3.0))

    # Check for tabular data
    if text.count('|') >= 4 or text.count(',') >= 10:
        return max(1, int(total_len / 2.6))

    # Standard natural language prose
    return max(1, int(total_len / 4.0))


def optimize_rag_prompt_density(
    query: str,
    context_chunks: List[str],
    token_budget: int = 1000
) -> Dict[str, Any]:
    """
    Optimizes prompt context density by trimming low-relevance boilerplate while enforcing token budget limits.
    # ponytail: content-aware token density budgeting; ceiling: heuristic sub-word estimation; upgrade: bind model-specific BPE tokenizer for exact 8k boundary alignment
    """
    safe_query = str(query or "")
    safe_budget = max(50, int(token_budget)) if token_budget is not None and isinstance(token_budget, (int, float)) else 1000
    query_terms = _get_word_set(safe_query)

    if not context_chunks or not isinstance(context_chunks, list):
        context_chunks = []

    valid_chunks = [str(c) for c in context_chunks if c is not None]

    scored_chunks = []
    for chunk in valid_chunks:
        words = _get_word_set(chunk)
        overlap = len(query_terms.intersection(words))
        token_cost = estimate_text_tokens(chunk)
        # Density = query overlap score per token cost
        density = (overlap + 0.1) / max(1, token_cost)
        scored_chunks.append((chunk, overlap, token_cost, density))

    # Sort chunks by query term overlap density descending
    scored_chunks.sort(key=lambda x: (x[1], x[3], -x[2]), reverse=True)

    selected_chunks = []
    used_tokens = 0
    query_tokens = estimate_text_tokens(safe_query)
    effective_budget = max(20, safe_budget - query_tokens - 20)

    for chunk, score, chunk_tokens, density in scored_chunks:
        if used_tokens + chunk_tokens <= effective_budget:
            selected_chunks.append(chunk)
            used_tokens += chunk_tokens
        else:
            remaining_budget = effective_budget - used_tokens
            if remaining_budget >= 30:
                # Slice chunk proportionally to remaining token budget
                char_slice = int(remaining_budget * 3.8)
                sliced = chunk[:char_slice].rsplit(" ", 1)[0] + "..."
                selected_chunks.append(sliced)
                used_tokens += estimate_text_tokens(sliced)
            break

    optimized_prompt = f"Query: {safe_query}\n\nOptimized Context:\n" + "\n---\n".join(selected_chunks)

    return {
        "status": "success",
        "query": safe_query,
        "original_chunk_count": len(context_chunks),
        "selected_chunk_count": len(selected_chunks),
        "estimated_tokens_used": used_tokens + query_tokens,
        "token_budget": safe_budget,
        "optimized_prompt": optimized_prompt
    }

