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


def _synthesize_question_for_sentence(sent: str, key_phrase: str) -> str:
    """Synthesizes diverse question forms based on sentence syntax and semantic intent."""
    s_lower = sent.lower()
    
    if any(p in s_lower for p in ["is a ", "is an ", "refers to ", "defined as ", "represents "]):
        return f"What is the definition and core role of {key_phrase}?"
    elif any(p in s_lower for p in ["must ", "shall ", "requires ", "requirement", "mandatory", "prerequisite"]):
        return f"What are the operational requirements and constraints for {key_phrase}?"
    elif any(p in s_lower for p in ["because ", "due to ", "results in ", "leads to ", "enables "]):
        return f"Why and how does {key_phrase} impact the system architecture?"
    elif any(p in s_lower for p in ["by using ", "utilizes ", "implements ", "executes ", "operates "]):
        return f"How is {key_phrase} implemented and executed in practice?"
    elif re.search(r'\d+', sent):
        return f"What quantitative metrics and parameters are associated with {key_phrase}?"
    else:
        return f"What key technical specifications and details are established for {key_phrase}?"


def generate_synthetic_qa_triples(
    document_text: str,
    max_triples: int = 5
) -> Dict[str, Any]:
    """
    Parses document text and generates synthetic QA triples for offline benchmarking.
    Zero-dependency stdlib implementation.
    """
    if not document_text or not isinstance(document_text, str) or not document_text.strip():
        return {"triples": [], "count": 0, "total_generated": 0, "status": "empty_text"}

    norm_doc = unicodedata.normalize("NFC", document_text)
    sentences = [s for s in split_sentences(norm_doc) if len(s) > 20]
    
    limit = max(0, int(max_triples)) if max_triples is not None and isinstance(max_triples, (int, float)) else 5
    triples = []
    for idx, sent in enumerate(sentences[:limit]):
        key_phrase = _extract_key_phrase(sent)
        question = _synthesize_question_for_sentence(sent, key_phrase)
        answer = sent
        
        # Dynamic quality and confidence scoring
        sent_len = len(sent)
        word_count = len(sent.split())
        confidence = round(min(1.0, 0.76 + min(0.18, sent_len / 400.0) + (0.06 if len(key_phrase.split()) >= 2 else 0.0)), 2)
        quality_score = round(min(1.0, 0.50 + min(0.50, word_count / 25.0)), 2)

        triples.append({
            "id": f"syn_qa_{idx+1}",
            "question": question,
            "answer": answer,
            "context_sentence": sent,
            "key_phrase": key_phrase,
            "character_count": sent_len,
            "word_count": word_count,
            "confidence_score": confidence,
            "synthetic_quality_score": quality_score
        })

    return {
        "triples": triples,
        "total_generated": len(triples),
        "count": len(triples),
        "status": "success"
    }
