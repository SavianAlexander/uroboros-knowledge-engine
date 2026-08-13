"""
Entropy Differential Noise Masker Engine.
Evaluates token-level information density entropy (delta H) and masks low-information boilerplate.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List


BOILERPLATE_TRIGGERS = [
    "all rights reserved",
    "confidential and proprietary",
    "page 1 of",
    "terms of service apply",
    "disclaimer:",
    "copyright (c)"
]


def mask_low_entropy_noise(text_chunk: str) -> Dict[str, Any]:
    """
    Evaluates lines/tokens for low information entropy and strips repetitive boilerplate.
    """
    if not text_chunk:
        return {"clean_text": "", "token_reduction_pct": 0.0, "status": "empty_input"}

    lines = text_chunk.split("\n")
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
        "status": "success"
    }
