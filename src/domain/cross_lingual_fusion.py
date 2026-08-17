"""
Zero-Shot Cross-Lingual RAG Fusion Engine.
Bi-directional cross-lingual term alignment mapping queries across English, Spanish, German, French, and Portuguese.
Enables unified multi-language vault retrieval with zero external neural translation dependencies.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context

import os
import json
from functools import lru_cache

_LEXICON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "lexicon_cross_lingual.json")
)

@lru_cache(maxsize=1)
def load_multilingual_concept_map() -> Dict[str, List[str]]:
    """Loads and caches the empirical multilingual concept map from JSON."""
    if os.path.exists(_LEXICON_PATH):
        try:
            with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("concept_map", {})
        except Exception:
            pass
    return {}


def expand_cross_lingual_query(query: str) -> str:
    """
    Expands an input query with bi-directional multilingual equivalents for comprehensive RAG search.
    """
    if not query or not isinstance(query, str):
        return ""
    norm_query = unicodedata.normalize("NFC", str(query).strip())
    expanded_terms = [norm_query]
    
    # Check multi-word phrases first
    q_lower = norm_query.lower()
    concept_map = load_multilingual_concept_map()
    for phrase, translations in concept_map.items():
        if phrase in q_lower:
            for t in translations[:3]:
                if t not in expanded_terms:
                    expanded_terms.append(t)

    # Check individual words
    words = [w.strip(".,;:!?\"'()[]{}").lower() for w in norm_query.split() if len(w) > 3]
    for w in words:
        if w in concept_map:
            for t in concept_map[w][:2]:
                if t not in expanded_terms:
                    expanded_terms.append(t)
        else:
            import os
            import sqlite3
            from src.infrastructure.database import DB_FILE, get_db_connection
            if os.path.exists(DB_FILE):
                try:
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT synonym FROM synonyms WHERE word = ? LIMIT 2", (w,))
                        for row in cursor.fetchall():
                            syn = str(row[0])
                            if syn not in expanded_terms:
                                expanded_terms.append(syn)
                except Exception:
                    pass

    return " OR ".join(expanded_terms) if len(expanded_terms) > 1 else norm_query


def cross_lingual_rag_search(query: str, max_chunks: int = 4) -> Dict[str, Any]:
    """
    Executes cross-lingual RAG search over multi-lingual document vaults.
    """
    safe_q = str(query or "").strip()
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
