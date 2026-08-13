"""
Dynamic Entropy-Based Semantic Boundary Chunker Engine.
Calculates semantic distance between consecutive sentence n-grams and creates topic boundaries when distance spikes above threshold theta.
Zero-dependency, stdlib implementation.
"""
import functools
import re
import math
from typing import List, Dict, Any, Tuple

from src.domain.rag_grounding_guard import split_sentences, RE_WORD, STOP_WORDS


@functools.lru_cache(maxsize=2048)
def _get_sentence_words_tuple(sentence: str) -> Tuple[str, ...]:
    return tuple(set(w.lower() for w in RE_WORD.findall(sentence) if w.lower() not in STOP_WORDS))


def get_sentence_words(sentence: str) -> set:
    """Extracts non-stopword tokens from a sentence string."""
    return set(_get_sentence_words_tuple(sentence))


def compute_jaccard_distance(s1_words: set, s2_words: set) -> float:
    """Computes Jaccard distance between two word sets (1 - similarity)."""
    if not s1_words or not s2_words:
        return 1.0
    union = s1_words.union(s2_words)
    if not union:
        return 0.0
    intersection = s1_words.intersection(s2_words)
    similarity = len(intersection) / float(len(union))
    raw_dist = 1.0 - similarity
    return round(max(0.0, min(1.0, raw_dist)), 4)


def chunk_by_semantic_entropy(
    text: str,
    distance_threshold: float = 0.65,
    max_chunk_size: int = 500
) -> List[Dict[str, Any]]:
    """
    Chunks text by calculating semantic entropy distance between adjacent sentences.
    Creates a new chunk whenever distance spikes above distance_threshold or max_chunk_size is exceeded.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return []

    sentences = split_sentences(text)
    if not sentences:
        return []

    sentence_words_list = [get_sentence_words(s) for s in sentences]
    chunks = []
    current_sentences = []
    current_length = 0
    prev_words = None

    for i, sent in enumerate(sentences):
        sent_words = sentence_words_list[i]
        distance = compute_jaccard_distance(prev_words, sent_words) if prev_words is not None else 0.0

        # Trigger boundary if distance exceeds threshold or character length exceeds limit
        if current_sentences and (distance >= distance_threshold or (current_length + len(sent) > max_chunk_size)):
            chunk_content = " ".join(current_sentences)
            chunks.append({
                "chunk_index": len(chunks),
                "content": chunk_content,
                "char_length": len(chunk_content),
                "sentence_count": len(current_sentences),
                "boundary_entropy_score": distance
            })
            current_sentences = [sent]
            current_length = len(sent)
            prev_words = sent_words
        else:
            current_sentences.append(sent)
            current_length += len(sent)
            prev_words = sent_words

    if current_sentences:
        chunk_content = " ".join(current_sentences)
        chunks.append({
            "chunk_index": len(chunks),
            "content": chunk_content,
            "char_length": len(chunk_content),
            "sentence_count": len(current_sentences),
            "boundary_entropy_score": 0.0
        })

    return chunks
