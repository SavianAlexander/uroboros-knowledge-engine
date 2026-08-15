"""
Legacy shim for backward-compatibility.
Canonical implementation is in `src.domain.decomposed_hybrid_rag`.
"""
from src.domain.decomposed_hybrid_rag import (
    decompose_query,
    compress_context_chunks,
    execute_hybrid_decomposed_search,
    execute_sota_rag_search,
    get_decomposed_rag_capabilities,
    get_sota_rag_capabilities
)

__all__ = [
    "decompose_query",
    "compress_context_chunks",
    "execute_hybrid_decomposed_search",
    "execute_sota_rag_search",
    "get_decomposed_rag_capabilities",
    "get_sota_rag_capabilities"
]
