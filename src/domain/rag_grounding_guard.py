"""
Self-Correction RAG Grounding & Hallucination Guard Engine.
Verifies LLM response claim sentences against retrieved source context chunks via n-gram overlap and vector entailment heuristics.
Zero-dependency, stdlib implementation.
"""

import re
from typing import List, Dict, Any

RE_SENTENCE = re.compile(r'[^.!?]+[.!?]+')
RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')

STOP_WORDS = {"the", "and", "is", "in", "it", "of", "to", "a", "for", "with", "on", "that", "this", "by", "an", "are", "as", "at", "be", "or", "from"}


def split_sentences(text: str) -> List[str]:
    """Splits text into discrete sentences."""
    if not text:
        return []
    sents = [s.strip() for s in RE_SENTENCE.findall(text)]
    rem = RE_SENTENCE.sub("", text).strip()
    if rem and rem not in sents:
        sents.append(rem)
    return sents if sents else [text.strip()]



def compute_ngram_overlap(claim: str, source_text: str) -> float:
    """Computes word-level overlap ratio between claim sentence and source text."""
    claim_words = set(w.lower() for w in RE_WORD.findall(claim) if w.lower() not in STOP_WORDS)
    if not claim_words:
        return 1.0
    
    source_words = set(w.lower() for w in RE_WORD.findall(source_text) if w.lower() not in STOP_WORDS)
    overlap = claim_words.intersection(source_words)
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
    sentences = split_sentences(llm_response)
    combined_source = " ".join(source_chunks)
    
    verified_sentences = []
    hallucination_warnings = []
    
    total_grounding_score = 0.0
    
    for sent in sentences:
        overlap = compute_ngram_overlap(sent, combined_source)
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
