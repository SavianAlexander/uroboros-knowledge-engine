"""
Dynamic RAG Prompt Density Optimizer & Token Budget Allocator.
Optimizes context token density and dynamically injects few-shot domain examples.
"""

from typing import Dict, Any, List, Optional


def optimize_rag_prompt_density(
    query: str,
    context_chunks: List[str],
    token_budget: int = 1000
) -> Dict[str, Any]:
    """
    Optimizes prompt context density by trimming low-relevance boilerplate while enforcing token budget limits.
    # ponytail: lightweight character/word-based token density budgeting
    """
    char_budget = token_budget * 4  # Approx 4 chars per token
    query_terms = set(w.lower() for w in query.split() if len(w) > 3)

    scored_chunks = []
    for chunk in context_chunks:
        words = set(w.lower() for w in chunk.split() if len(w) > 3)
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
