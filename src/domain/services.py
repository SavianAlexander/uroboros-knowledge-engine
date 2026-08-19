"""
Domain Services Facade.
Exposes high-level unified service operations for MCP tools and application layers.
"""
from typing import Optional, Dict, Any, List
from src.domain.rag_engine import generate_hyde_expansion, extract_advanced_rag_context, build_augmented_prompt

def generate_hyde(query: Optional[str] = None) -> str:
    """Generate HyDE expansion for a search or RAG query."""
    if not query:
        return ""
    return generate_hyde_expansion(query)

__all__ = [
    "generate_hyde",
    "generate_hyde_expansion",
    "extract_advanced_rag_context",
    "build_augmented_prompt",
]
