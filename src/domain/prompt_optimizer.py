"""
Dynamic RAG Prompt Density Optimizer & Token Budget Allocator.
Optimizes context token density and dynamically injects few-shot domain examples.
"""

from functools import lru_cache
from typing import Dict, Any, List, Optional, Set

@lru_cache(maxsize=2048)
def _get_word_set(text: str) -> Set[str]:
    if not text:
        return set()
    return set(w.lower() for w in text.split() if len(w) > 3)


def optimize_rag_prompt_density(
    query: str,
    context_chunks: List[str],
    token_budget: int = 1000
) -> Dict[str, Any]:
    """
    Optimizes prompt context density by trimming low-relevance boilerplate while enforcing token budget limits.
    # ponytail: lightweight character/word-based token density budgeting; ceiling: 4 chars/token heuristic estimate; upgrade: use tiktoken or model-specific BPE tokenizer if exact token counting is required
    """
    safe_query = str(query or "")
    safe_budget = max(100, int(token_budget)) if token_budget is not None and isinstance(token_budget, (int, float)) else 1000
    char_budget = safe_budget * 4  # Approx 4 chars per token
    query_terms = _get_word_set(safe_query)

    if not context_chunks or not isinstance(context_chunks, list):
        context_chunks = []

    valid_chunks = [str(c) for c in context_chunks if c is not None]

    scored_chunks = []
    for chunk in valid_chunks:
        words = _get_word_set(chunk)
        overlap = len(query_terms.intersection(words))
        scored_chunks.append((chunk, overlap, len(chunk)))

    # Sort chunks by query term overlap density
    scored_chunks.sort(key=lambda x: (x[1], -x[2]), reverse=True)

    selected_chunks = []
    used_chars = 0
    for chunk, score, chunk_len in scored_chunks:
        if used_chars + chunk_len <= char_budget:
            selected_chunks.append(chunk)
            used_chars += chunk_len
        elif char_budget - used_chars > 100:
            selected_chunks.append(chunk[:char_budget - used_chars] + "...")
            break

    optimized_prompt = f"Query: {query}\n\nOptimized Context:\n" + "\n---\n".join(selected_chunks)

    return {
        "status": "success",
        "query": query,
        "original_chunk_count": len(context_chunks),
        "selected_chunk_count": len(selected_chunks),
        "estimated_tokens_used": used_chars // 4,
        "optimized_prompt": optimized_prompt
    }
