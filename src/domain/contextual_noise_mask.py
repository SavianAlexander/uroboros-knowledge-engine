"""
Document Boilerplate & Noise Reduction Engine.
Identifies and strips repetitive boilerplate lines (legal notices, copyright headers, pagination markers)
to maximize information density in retrieval contexts.
Standard: Pure Python standard library (unicodedata, collections, math, typing).
"""
import collections
import math
import unicodedata
from typing import Dict, Any, List

BOILERPLATE_TRIGGERS = [
    "all rights reserved",
    "confidential and proprietary",
    "page 1 of",
    "terms of service apply",
    "disclaimer:",
    "copyright (c)",
    "table of contents",
    "this page intentionally left blank"
]


def _compute_entropy(text: str) -> float:
    """Computes byte-level Shannon Entropy."""
    if not text:
        return 0.0
    b = text.encode("utf-8")
    length = len(b)
    if length == 0:
        return 0.0
    counts = collections.Counter(b)
    return round(-sum((c / length) * math.log2(c / length) for c in counts.values()), 4)


def mask_low_entropy_noise(text_chunk: str) -> Dict[str, Any]:
    """
    Strips repetitive low-information boilerplate lines and calculates density improvements.
    """
    if not text_chunk or not isinstance(text_chunk, str):
        return {
            "original_word_count": 0,
            "clean_word_count": 0,
            "token_reduction_pct": 0.0,
            "clean_text": "",
            "entropy_before": 0.0,
            "entropy_after": 0.0,
            "status": "empty_input"
        }

    norm_text = unicodedata.normalize("NFC", text_chunk)
    lines = norm_text.split("\n")
    clean_lines = []
    masked_lines_count = 0

    for line in lines:
        line_lower = line.strip().lower()
        if any(trigger in line_lower for trigger in BOILERPLATE_TRIGGERS):
            masked_lines_count += 1
            continue
        clean_lines.append(line)

    clean_text = "\n".join(clean_lines).strip()
    orig_words = len(text_chunk.split())
    clean_words = len(clean_text.split())
    reduction = round(((orig_words - clean_words) / max(orig_words, 1)) * 100.0, 2)

    return {
        "original_word_count": orig_words,
        "clean_word_count": clean_words,
        "token_reduction_pct": reduction,
        "clean_text": clean_text,
        "entropy_before": _compute_entropy(text_chunk),
        "entropy_after": _compute_entropy(clean_text),
        "masked_lines_count": masked_lines_count,
        "status": "success"
    }
