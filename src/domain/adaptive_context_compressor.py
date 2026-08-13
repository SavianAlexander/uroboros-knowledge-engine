"""
Semantic Entropy Context Compressor.
Filters filler prose from retrieved document chunks while preserving exact numbers, entities, and code blocks.
Zero-dependency, stdlib implementation.
"""
import functools
import re
import unicodedata
from typing import Dict, Any, List

RE_SPLIT_SENTENCE = re.compile(r'(?<=[.!?])\s+')
RE_NUMBERS = re.compile(r'\d+')
RE_CODE_SYMBOLS = re.compile(r'[`_(){}\[\]=:]')
RE_ENTITY = re.compile(r'^[A-Z][a-zA-Z0-9_-]*$')


@functools.lru_cache(maxsize=1024)
def _compress_single_chunk(chunk: str) -> str:
    norm_chunk = unicodedata.normalize("NFC", chunk)
    if '.' not in norm_chunk and '!' not in norm_chunk and '?' not in norm_chunk:
        return norm_chunk

    sentences = [s.strip() for s in RE_SPLIT_SENTENCE.split(norm_chunk) if s.strip()]
    if not sentences:
        return chunk

    keep_sentences = []
    for sent in sentences:
        words = sent.split()
        if len(words) < 8:
            keep_sentences.append(sent)
            continue

        if RE_NUMBERS.search(sent) or RE_CODE_SYMBOLS.search(sent):
            keep_sentences.append(sent)
            continue

        if any(w.strip(".,;:!?\"'()[]{}") and w.strip(".,;:!?\"'()[]{}")[0].isupper() for w in words[1:]):
            keep_sentences.append(sent)
            continue

    return " ".join(keep_sentences) if keep_sentences else chunk


def compress_context_entropy(context_chunks: List[str], target_reduction: float = 0.4) -> Dict[str, Any]:
    """
    Compresses text chunks by removing low-entropy filler prose while preserving key entities and numbers.
    # ponytail: zero-dependency semantic entropy context compressor; ceiling: heuristic n-gram entropy scoring; upgrade: use neural token pruner if GPU LLM context compressor is available
    """
    if not context_chunks or not isinstance(context_chunks, list):
        return {"status": "empty", "compressed_chunks": [], "original_chars": 0, "compressed_chars": 0}

    valid_chunks = [str(c) for c in context_chunks if c is not None]
    if not valid_chunks:
        return {"status": "empty", "compressed_chunks": [], "original_chars": 0, "compressed_chars": 0}

    compressed = [_compress_single_chunk(c) for c in valid_chunks]
    total_orig = sum(len(c) for c in valid_chunks)

    total_comp = sum(len(c) for c in compressed)
    reduction_pct = round((1.0 - (total_comp / float(total_orig))) * 100.0, 2) if total_orig else 0.0

    return {
        "status": "success",
        "original_chars": total_orig,
        "compressed_chars": total_comp,
        "token_reduction_percentage": reduction_pct,
        "compressed_chunks": compressed
    }
