"""
Zero-Shot Cross-Lingual RAG Fusion Engine.
Maps query terms across multi-lingual term dictionaries to enable cross-lingual vault retrieval.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context

CROSS_LINGUAL_DICT = {
    "database": ["base de datos", "datenbank", "base de données"],
    "search": ["búsqueda", "suche", "recherche"],
    "security": ["seguridad", "sicherheit", "sécurité"],
    "performance": ["rendimiento", "leistung", "performance"],
    "architecture": ["arquitectura", "architektur", "architecture"]
}


def expand_cross_lingual_query(query: str) -> str:
    """Expands an English query string with multilingual terms."""
    if not query or not isinstance(query, str):
        return ""

    expanded_terms = [query]
    words = [w.strip(".,;:!?\"'()[]{}").lower() for w in query.split() if w.strip(".,;:!?\"'()[]{}")]

    for w in words:
        if w in CROSS_LINGUAL_DICT:
            expanded_terms.extend(CROSS_LINGUAL_DICT[w])

    return " OR ".join(expanded_terms)


def cross_lingual_rag_search(query: str, max_chunks: int = 4) -> Dict[str, Any]:
    """
    Executes cross-lingual RAG search over multi-lingual document vaults.
    # ponytail: zero-dependency cross-lingual term fusion
    """
    safe_q = str(query or "")
    expanded_q = expand_cross_lingual_query(safe_q)

    safe_k = max(1, int(max_chunks)) if max_chunks is not None and isinstance(max_chunks, (int, float)) else 4
    formatted_ctx, snippets = extract_advanced_rag_context(expanded_q, max_chunks=safe_k)

    return {
        "status": "success",
        "original_query": query,
        "expanded_cross_lingual_query": expanded_q,
        "total_snippets_found": len(snippets),
        "snippets": snippets,
        "formatted_context": formatted_ctx
    }
