"""
Cross-Lingual Semantic Alignment & Transliteration Engine.
Maps non-English queries across Spanish, French, and German to English canonical domain terms.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any

# Cross-lingual canonical term mappings (Zero-dependency stdlib dict)
CROSS_LINGUAL_MAP = {
    "es": {
        "algoritmo": "algorithm",
        "red neuronal": "neural network",
        "busqueda": "search",
        "vector": "vector",
        "base de datos": "database",
        "rendimiento": "performance",
        "configuracion": "configuration"
    },
    "fr": {
        "algorithme": "algorithm",
        "reseau neuronal": "neural network",
        "recherche": "search",
        "base de donnees": "database",
        "performance": "performance"
    },
    "de": {
        "algorithmus": "algorithm",
        "neuronales netz": "neural network",
        "suche": "search",
        "datenbank": "database",
        "leistung": "performance"
    }
}


def align_cross_lingual_query(query: str, source_lang: str = "auto") -> Dict[str, Any]:
    """
    Aligns non-English query terms with English canonical terms for cross-lingual vector search.
    """
    if not query:
        return {"original_query": "", "aligned_query": "", "translations_applied": 0, "status": "success"}

    import unicodedata
    query_lower = unicodedata.normalize("NFC", str(query)).lower()
    aligned = query_lower
    translations_applied = 0

    for lang, term_map in CROSS_LINGUAL_MAP.items():
        if source_lang != "auto" and source_lang != lang:
            continue
        for src_term, target_term in term_map.items():
            if src_term in aligned:
                aligned = aligned.replace(src_term, target_term)
                translations_applied += 1

    return {
        "original_query": query,
        "aligned_query": aligned,
        "translations_applied": translations_applied,
        "status": "success"
    }
