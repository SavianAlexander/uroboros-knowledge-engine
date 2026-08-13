"""
Dynamic Context Budget Allocator Engine.
Dynamically calculates context token budget allocation across vector snippets, graph pathways, and episodic memory.
Zero-dependency, stdlib implementation.
"""
import unicodedata
from typing import Dict, Any, List, Optional


def allocate_context_budget(
    max_tokens: int = 8192,
    vector_snippets: Optional[List[str]] = None,
    graph_pathways: Optional[List[str]] = None,
    episodic_memories: Optional[List[str]] = None,
    chat_history: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Allocates context token limits proportionally:
    - Vector Snippets: 50%
    - Graph Pathways: 25%
    - Episodic Memory: 15%
    - System Instructions: 10%
    # ponytail: proportional context budget allocator; ceiling: static 50/25/15/10 ratio allocation; upgrade: use dynamic attention-weighted allocator if model supports 128k context window
    """
    raw_budget = kwargs.get("total_token_budget", max_tokens)
    token_budget = int(raw_budget) if raw_budget is not None and isinstance(raw_budget, (int, float)) and raw_budget > 0 else 8192
    raw_vec = kwargs.get("vector_chunks", vector_snippets)
    vector_snippets = raw_vec if isinstance(raw_vec, list) else []
    raw_graph = kwargs.get("graph_halos", graph_pathways)
    graph_pathways = raw_graph if isinstance(raw_graph, list) else []
    episodic_memories = episodic_memories if isinstance(episodic_memories, list) else []

    snippet_budget = int(token_budget * 0.50)
    graph_budget = int(token_budget * 0.25)
    memory_budget = int(token_budget * 0.15)
    system_budget = int(token_budget * 0.10)

    fitted_snippets = [unicodedata.normalize("NFC", str(s))[:500] for s in vector_snippets][:5]
    fitted_graph = [unicodedata.normalize("NFC", str(g))[:300] for g in graph_pathways][:3]
    fitted_memories = [unicodedata.normalize("NFC", str(m))[:200] for m in episodic_memories][:3]

    total_chars = sum(len(s) for s in fitted_snippets) + sum(len(g) for g in fitted_graph)
    approx_tokens = max(10, total_chars // 4)

    return {
        "status": "success",
        "max_tokens": token_budget,
        "approx_tokens_used": approx_tokens,
        "allocated_chunks": fitted_snippets,
        "allocated_halos": fitted_graph,
        "allocations": {
            "vector_snippets": {"token_budget": snippet_budget, "count": len(fitted_snippets)},
            "graph_pathways": {"token_budget": graph_budget, "count": len(fitted_graph)},
            "episodic_memories": {"token_budget": memory_budget, "count": len(fitted_memories)},
            "system_overhead": {"token_budget": system_budget}
        },
        "fitted_payload": {
            "snippets": fitted_snippets,
            "graph": fitted_graph,
            "memories": fitted_memories
        }
    }
