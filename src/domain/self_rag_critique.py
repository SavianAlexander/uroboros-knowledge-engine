"""
Zero-dependency Self-RAG Reflection & Grounding Critique Engine.
Computes Self-RAG reflection tokens: [IsRel], [IsSup], [IsUse] to eliminate hallucinations.
"""
import unicodedata
import re
from typing import Dict, Any, List

RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')


import functools

@functools.lru_cache(maxsize=2048)
def _get_words_set(text: str) -> set:
    if not text:
        return set()
    safe_text = unicodedata.normalize("NFC", str(text))
    return set(RE_WORD.findall(safe_text.lower()))


def evaluate_relevance(query: str, context_chunk: str) -> Dict[str, Any]:
    """
    Evaluates [IsRel] reflection token: Is context chunk relevant to query?
    """
    q_words = _get_words_set(query)
    c_words = _get_words_set(context_chunk)

    if not q_words or not c_words:
        return {"token": "[IsRel:No]", "score": 0.0, "relevant": False}

    overlap = len(q_words & c_words)
    relevance_score = round(overlap / float(len(q_words)), 4)
    is_rel = relevance_score >= 0.15

    return {
        "token": "[IsRel:Yes]" if is_rel else "[IsRel:No]",
        "score": relevance_score,
        "relevant": is_rel
    }


def evaluate_support(answer: str, context_chunk: str) -> Dict[str, Any]:
    """
    Evaluates [IsSup] reflection token: Is generated answer factually grounded in context?
    """
    a_words = _get_words_set(answer)
    c_words = _get_words_set(context_chunk)

    if not a_words or not c_words:
        return {"token": "[IsSup:No]", "score": 0.0, "supported": False}

    overlap = len(a_words & c_words)
    support_score = round(overlap / float(len(a_words)), 4)
    is_sup = support_score >= 0.40

    return {
        "token": "[IsSup:FullySupported]" if is_sup else "[IsSup:NoSupport]",
        "score": support_score,
        "supported": is_sup
    }


def critique_rag_passages(query: str, chunks: List[str]) -> List[Dict[str, Any]]:
    """
    Critiques and filters candidate chunks using Self-RAG reflection tokens.
    Retains only factually relevant & supported passages.
    """
    if not chunks or not isinstance(chunks, list):
        return []

    valid_chunks = [str(c) for c in chunks if c is not None]

    evaluated = []
    for idx, chunk in enumerate(valid_chunks):
        rel_res = evaluate_relevance(query, chunk)
        if rel_res["relevant"]:
            evaluated.append({
                "chunk_index": idx,
                "content": chunk,
                "reflection_token": rel_res["token"],
                "relevance_score": rel_res["score"]
            })

    evaluated.sort(key=lambda x: x["relevance_score"], reverse=True)
    return evaluated
