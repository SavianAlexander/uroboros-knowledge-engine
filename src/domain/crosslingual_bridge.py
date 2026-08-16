"""
Multilingual Deterministic Vector Projection Bridge Engine.
Projects multilingual queries and text into a canonical, unit-normalized invariant vector space.
Standard: Zero-dependency, pure Python standard library (math, unicodedata, re).
"""
import math
import re
import unicodedata
from typing import Dict, Any, List


def project_multilingual_vector(
    text: str,
    source_language: str = "auto",
    dim: int = 64
) -> Dict[str, Any]:
    """
    Projects multilingual text into a unit-normalized invariant latent space vector
    using character trigrams and NFC/NFD Unicode decomposition.
    """
    if not text or not str(text).strip():
        return {
            "text": text,
            "source_language": source_language,
            "latent_dimension": dim,
            "unit_normalized_vector": [0.0] * dim,
            "latent_vector": [],
            "status": "empty_input"
        }

    # 1. Unicode NFC normalization followed by NFD decomposition for accent insensitivity
    norm_nfc = unicodedata.normalize("NFC", str(text))
    norm_nfd = unicodedata.normalize("NFD", norm_nfc)
    clean_text = "".join(c for c in norm_nfd if unicodedata.category(c) != "Mn").lower()

    # 2. Extract character trigrams for robust cross-lingual subword matching
    padded = f"  {clean_text}  "
    trigrams = [padded[i:i+3] for i in range(len(padded) - 2)]

    vec = [0.0] * dim
    for tg in trigrams:
        # Stable FNV-1a 32-bit hash mapped to vector dimensions
        h = 2166136261
        for b in tg.encode("utf-8"):
            h ^= b
            h = (h * 16777619) & 0xFFFFFFFF
        idx = h % dim
        vec[idx] += 1.0

    # 3. L2 Unit Normalization
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    norm_vec = [round(v / norm, 4) for v in vec]

    return {
        "text": text,
        "source_language": source_language,
        "latent_dimension": dim,
        "unit_normalized_vector": norm_vec,
        "latent_vector": norm_vec,
        "status": "success"
    }
