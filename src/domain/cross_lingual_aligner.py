"""
Zero-dependency Cross-Lingual Semantic Translation & Alignment Engine.
Aligns multi-lingual search queries (Spanish, French, German) with English vault documents.
"""
import unicodedata
import re
from typing import Dict, Any, List

import os
import json
from functools import lru_cache

_LEXICON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "lexicon_cross_lingual.json")
)

@lru_cache(maxsize=1)
def load_cross_lingual_translations() -> Dict[str, str]:
    """Loads and caches the empirical cross-lingual translation dictionary from JSON."""
    if not os.path.exists(_LEXICON_PATH):
        raise FileNotFoundError(f"Empirical cross-lingual lexicon not found at '{_LEXICON_PATH}'.")
    with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("translations", {})


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

    translations = load_cross_lingual_translations()
    for t in tokens:
        translated = translations.get(t)
        if not translated:
            import os
            import sqlite3
            from src.infrastructure.database import DB_FILE, get_db_connection
            if os.path.exists(DB_FILE):
                try:
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT synonym FROM synonyms WHERE word = ? LIMIT 1", (t,))
                        row = cursor.fetchone()
                        if row:
                            translated = str(row[0])
                        else:
                            cursor.execute("SELECT target_tag FROM tag_aliases WHERE alias = ? LIMIT 1", (t,))
                            row2 = cursor.fetchone()
                            if row2:
                                translated = str(row2[0])
                except Exception:
                    pass
        translated_tokens.append(translated or t)

    aligned_query = " ".join(translated_tokens)

    return {
        "original_query": query,
        "normalized_query": stripped_query,
        "aligned_query": aligned_query,
        "translated": aligned_query != query.lower(),
        "status": "success"
    }
