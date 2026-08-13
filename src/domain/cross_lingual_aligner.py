"""
Zero-dependency Cross-Lingual Semantic Translation & Alignment Engine.
Aligns multi-lingual search queries (Spanish, French, German) with English vault documents.
"""

import unicodedata
import re
from typing import Dict, Any, List

COMMON_TRANSLATIONS = {
    # Spanish
    "financiero": "financial", "contabilidad": "accounting", "informe": "report", "auditoria": "audit",
    "estandar": "standard", "norma": "rule", "documento": "document", "sistema": "system",
    # French
    "financier": "financial", "comptabilite": "accounting", "rapport": "report", "norme": "standard",
    # German
    "finanz": "financial", "bericht": "report", "standard": "standard", "system": "system"
}


def align_cross_lingual_query(query: str) -> Dict[str, Any]:
    """
    Normalizes accents/diacritics (NFC/NFD) and aligns non-English terms to English vault equivalents.
    Zero-dependency stdlib implementation.
    """
    # Unicode NFC & NFD normalization
    norm_nfc = unicodedata.normalize("NFC", str(query))
    norm_query = unicodedata.normalize("NFD", norm_nfc)
    stripped_query = "".join(c for c in norm_query if unicodedata.category(c) != "Mn").lower()

    tokens = re.findall(r'\b[a-z0-9_-]{3,}\b', stripped_query)
    translated_tokens = []

    for t in tokens:
        translated_tokens.append(COMMON_TRANSLATIONS.get(t, t))

    aligned_query = " ".join(translated_tokens)

    return {
        "original_query": query,
        "normalized_query": stripped_query,
        "aligned_query": aligned_query,
        "translated": aligned_query != query.lower(),
        "status": "success"
    }
