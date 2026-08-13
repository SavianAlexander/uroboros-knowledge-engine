"""
Streaming Semantic Token Compressor Engine.
Prunes filler words and redundant stop phrases from prompt context in real-time.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any

FILLER_WORDS = {
    "basically", "essentially", "in order to", "as a matter of fact",
    "at the present time", "due to the fact that", "for the purpose of", "it should be noted that"
}


def compress_streaming_tokens(text: str) -> Dict[str, Any]:
    """
    Prunes filler words from text prompt to maximize LLM token throughput.
    """
    if not text:
        return {"compressed_text": "", "tokens_saved": 0, "status": "empty_input"}

    sanitized = text
    saved_count = 0

    for filler in FILLER_WORDS:
        pattern = re.compile(re.escape(filler), re.IGNORECASE)
        matches = len(pattern.findall(sanitized))
        if matches > 0:
            saved_count += matches
            sanitized = pattern.sub("", sanitized)

    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    orig_len = len(text)
    new_len = len(sanitized)
    reduction = round(1.0 - (new_len / float(orig_len)), 4) if orig_len > 0 else 0.0

    return {
        "original_char_count": orig_len,
        "compressed_char_count": new_len,
        "character_reduction": reduction,
        "fillers_removed_count": saved_count,
        "compressed_text": sanitized,
        "status": "success"
    }
