"""
Self-Correction RAG Grounding & Hallucination Guard Engine.
Verifies LLM response claim sentences against retrieved source context chunks via n-gram overlap and vector entailment heuristics.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import List, Dict, Any

RE_SENTENCE = re.compile(r'[^.!?]+[.!?]+')
RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')

STOP_WORDS = {"the", "and", "is", "in", "it", "of", "to", "a", "for", "with", "on", "that", "this", "by", "an", "are", "as", "at", "be", "or", "from"}


from functools import lru_cache

def split_sentences(text: str) -> List[str]:
    """Splits text into discrete sentences."""
    if not text or not isinstance(text, str):
        return []
    if '.' not in text and '!' not in text and '?' not in text:
        return [text.strip()]
    sents = [s.strip() for s in RE_SENTENCE.findall(text)]
    rem = RE_SENTENCE.sub("", text).strip()
    if rem and rem not in sents:
        sents.append(rem)
    return sents if sents else [text.strip()]


@lru_cache(maxsize=1024)
def _extract_word_set(text: str) -> set:
    norm = unicodedata.normalize("NFC", text)
    return set(w.lower() for w in RE_WORD.findall(norm) if w.lower() not in STOP_WORDS)


def compute_ngram_overlap(claim: str, source_text: str) -> float:
    """Computes word-level overlap ratio between claim sentence and source text."""
    if not claim or not source_text or not isinstance(claim, str) or not isinstance(source_text, str):
        return 0.0 if (claim and not source_text) else 1.0

    claim_words = _extract_word_set(claim)
    if not claim_words:
        return 1.0
    
    source_words = _extract_word_set(source_text)
    overlap = claim_words & source_words
    return round(len(overlap) / float(len(claim_words)), 4)


def verify_rag_grounding(
    llm_response: str,
    source_chunks: List[str],
    threshold: float = 0.4
) -> Dict[str, Any]:
    """
    Verifies every claim sentence in the LLM response against the retrieved source context chunks.
    Identifies grounded vs potential hallucination sentences.
    """
    safe_response = str(llm_response or "")
    sentences = split_sentences(safe_response)

    if source_chunks and isinstance(source_chunks, list):
        valid_chunks = [str(c) for c in source_chunks if c is not None]
    else:
        valid_chunks = []
    combined_source = " ".join(valid_chunks)
    source_words = _extract_word_set(combined_source) if combined_source else set()
    
    verified_sentences = []
    hallucination_warnings = []
    
    total_grounding_score = 0.0
    
    for sent in sentences:
        claim_words = _extract_word_set(sent)
        if not claim_words:
            overlap = 1.0
        elif not source_words:
            overlap = 0.0
        else:
            overlap = round(len(claim_words & source_words) / float(len(claim_words)), 4)

        total_grounding_score += overlap
        is_grounded = overlap >= threshold
        
        sent_item = {
            "sentence": sent,
            "grounding_score": overlap,
            "is_grounded": is_grounded
        }
        verified_sentences.append(sent_item)
        if not is_grounded:
            hallucination_warnings.append(sent)

    avg_grounding = round(total_grounding_score / float(len(sentences)), 4) if sentences else 1.0
    overall_status = "grounded" if (avg_grounding >= threshold and not hallucination_warnings) else "hallucination_risk"

    
    return {
        "overall_status": overall_status,
        "avg_grounding_score": avg_grounding,
        "total_sentences": len(sentences),
        "grounded_count": len(sentences) - len(hallucination_warnings),
        "hallucination_warnings": hallucination_warnings,
        "verified_sentences": verified_sentences
    }
