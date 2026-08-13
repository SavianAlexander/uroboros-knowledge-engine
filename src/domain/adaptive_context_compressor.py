"""
Semantic Entropy Context Compressor.
Filters filler prose from retrieved document chunks while preserving exact numbers, entities, and code blocks.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any, List


def compress_context_entropy(context_chunks: List[str], target_reduction: float = 0.4) -> Dict[str, Any]:
    """
    Compresses text chunks by removing low-entropy filler prose while preserving key entities and numbers.
    # ponytail: zero-dependency semantic entropy context compressor
    """
    if not context_chunks or not isinstance(context_chunks, list):
        return {"status": "empty", "compressed_chunks": [], "original_chars": 0, "compressed_chars": 0}

    valid_chunks = [str(c) for c in context_chunks if c is not None]
    if not valid_chunks:
        return {"status": "empty", "compressed_chunks": [], "original_chars": 0, "compressed_chars": 0}

    compressed = []
    total_orig = sum(len(c) for c in valid_chunks)

    for chunk in valid_chunks:
        import unicodedata
        norm_chunk = unicodedata.normalize("NFC", chunk)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', norm_chunk) if s.strip()]
        if not sentences:
            sentences = [chunk]

        keep_sentences = []
        for sent in sentences:
            # High-entropy indicators: numbers, code symbols, uppercase entities
            has_numbers = bool(re.search(r'\d+', sent))
            has_code = bool(re.search(r'[`_(){}\[\]=:]', sent))
            words = sent.split()
            middle_words = words[1:] if len(words) > 1 else []
            has_entities = any(bool(re.match(r'^[A-Z][a-zA-Z0-9_-]*$', w.strip(".,;:!?\"'()[]{}"))) for w in middle_words)

            if has_numbers or has_code or has_entities or len(words) < 8:
                keep_sentences.append(sent)

        compressed_text = " ".join(keep_sentences) if keep_sentences else chunk
        compressed.append(compressed_text)

    total_comp = sum(len(c) for c in compressed)
    reduction_pct = round((1.0 - (total_comp / float(total_orig))) * 100.0, 2) if total_orig else 0.0

    return {
        "status": "success",
        "original_chars": total_orig,
        "compressed_chars": total_comp,
        "token_reduction_percentage": reduction_pct,
        "compressed_chunks": compressed
    }
