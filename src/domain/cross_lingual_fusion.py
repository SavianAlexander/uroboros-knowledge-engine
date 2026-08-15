"""
Zero-Shot Cross-Lingual RAG Fusion Engine.
Bi-directional cross-lingual term alignment mapping queries across English, Spanish, German, French, and Portuguese.
Enables unified multi-language vault retrieval with zero external neural translation dependencies.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context

# Comprehensive multilingual domain dictionary with bi-directional aliases
MULTILINGUAL_CONCEPT_MAP = {
    # Architecture & Systems
    "database": ["base de datos", "datenbank", "base de données", "banco de dados", "db", "sqlite", "postgres"],
    "base de datos": ["database", "datenbank", "base de données", "banco de dados"],
    "datenbank": ["database", "base de datos", "base de données"],
    "search": ["búsqueda", "suche", "recherche", "busca", "retrieval", "fts", "vector"],
    "búsqueda": ["search", "suche", "recherche", "retrieval"],
    "suche": ["search", "búsqueda", "recherche"],
    "security": ["seguridad", "sicherheit", "sécurité", "segurança", "auth", "audit", "rbac"],
    "seguridad": ["security", "sicherheit", "sécurité"],
    "performance": ["rendimiento", "leistung", "desempenho", "latency", "throughput", "speed"],
    "rendimiento": ["performance", "leistung", "speed", "throughput"],
    "architecture": ["arquitectura", "architektur", "arquitetura", "system design", "clean architecture"],
    "arquitectura": ["architecture", "architektur", "system design"],
    "compliance": ["cumplimiento", "einhaltung", "conformité", "conformidade", "soc2", "gdpr", "hipaa"],
    "cumplimiento": ["compliance", "soc2", "audit"],
    "cache": ["memoria caché", "zwischenspeicher", "caching", "lru"],
    "contract": ["contrato", "vertrag", "accord", "agreement"],
    "contrato": ["contract", "agreement", "policy"]
}


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
    for phrase, translations in MULTILINGUAL_CONCEPT_MAP.items():
        if phrase in q_lower:
            for t in translations[:3]:
                if t not in expanded_terms:
                    expanded_terms.append(t)

    # Check individual words
    words = [w.strip(".,;:!?\"'()[]{}").lower() for w in norm_query.split() if len(w) > 3]
    for w in words:
        if w in MULTILINGUAL_CONCEPT_MAP:
            for t in MULTILINGUAL_CONCEPT_MAP[w][:2]:
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
