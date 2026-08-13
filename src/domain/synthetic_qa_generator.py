"""
Autonomous Synthetic QA Dataset Generator Engine.
Generates synthetic question-answer-context triples from raw text for continuous evaluation.
Zero-dependency, stdlib implementation.
"""

import functools
import re
import unicodedata
from typing import Dict, Any, List
from src.domain.rag_grounding_guard import split_sentences

RE_KEY_WORDS = re.compile(r'\b[a-zA-Z]{4,}\b')


@functools.lru_cache(maxsize=1024)
def _extract_key_phrase(sentence: str) -> str:
    """Extracts high-information key phrases from sentences with LRU caching."""
    words = RE_KEY_WORDS.findall(sentence)
    return " ".join(words[:3]) if len(words) >= 3 else "concept"


def generate_synthetic_qa_triples(
    document_text: str,
    max_triples: int = 5
) -> Dict[str, Any]:
    """
    Parses document text and generates synthetic QA triples for offline benchmarking.
    """
    if not document_text or not isinstance(document_text, str) or not document_text.strip():
        return {"triples": [], "count": 0, "total_generated": 0, "status": "empty_text"}

    norm_doc = unicodedata.normalize("NFC", document_text)
    sentences = [s for s in split_sentences(norm_doc) if len(s) > 20]
    
    limit = max(0, int(max_triples)) if max_triples is not None and isinstance(max_triples, (int, float)) else 5
    triples = []
    for idx, sent in enumerate(sentences[:limit]):
        key_phrase = _extract_key_phrase(sent)

        question = f"What does the document state regarding {key_phrase}?"
        answer = sent
        triples.append({
            "id": f"syn_qa_{idx+1}",
            "question": question,
            "answer": answer,
            "context_sentence": sent,
            "key_phrase": key_phrase,
            "character_count": len(sent),
            "word_count": len(sent.split()),
            "confidence_score": 0.92,
            "synthetic_quality_score": round(min(1.0, len(sent) / 150.0), 2)
        })

    return {
        "triples": triples,
        "total_generated": len(triples),
        "count": len(triples),
        "status": "success"
    }
