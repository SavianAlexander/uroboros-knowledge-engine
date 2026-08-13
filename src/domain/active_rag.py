"""
Active RAG Iterative Query Refinement Loop Engine.
Evaluates initial retrieval confidence and automatically reformulates query for a second targeted retrieval pass if confidence is low.
Zero-dependency, stdlib implementation.
"""

import re
from typing import List, Dict, Any
from src.domain.rag_grounding_guard import compute_ngram_overlap

RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')
STOP_WORDS = {"the", "and", "is", "in", "it", "of", "to", "a", "for", "with", "on", "that", "this", "by", "an", "are", "as", "at", "be", "or", "from"}


def reformulate_query(query: str, current_chunks: List[str]) -> str:
    """Reformulates query string by extracting key entity keywords and adding context descriptors."""
    words = [w for w in RE_WORD.findall(query) if w.lower() not in STOP_WORDS]
    if not words:
        return query
    
    # Expand with key nouns or overview terms
    reformulated = " ".join(words) + " detailed architecture technical overview"
    return reformulated


def execute_active_rag_loop(
    query: str,
    initial_chunks: List[str],
    confidence_threshold: float = 0.40
) -> Dict[str, Any]:
    """
    Executes Active RAG verification. If initial context overlap is low (< threshold),
    triggers iterative query reformulation and marks second_pass_required=True.
    """
    if not initial_chunks:
        refined_query = reformulate_query(query, [])
        return {
            "original_query": query,
            "refined_query": refined_query,
            "confidence_score": 0.0,
            "second_pass_required": True,
            "status": "refinement_needed"
        }

    import unicodedata
    norm_query = unicodedata.normalize("NFC", str(query or ""))
    norm_chunks = [unicodedata.normalize("NFC", str(c)) for c in initial_chunks if c]
    combined_text = " ".join(norm_chunks)
    score = compute_ngram_overlap(norm_query, combined_text)
    
    second_pass_required = score < confidence_threshold
    refined_query = reformulate_query(query, initial_chunks) if second_pass_required else query

    return {
        "original_query": query,
        "refined_query": refined_query,
        "confidence_score": score,
        "second_pass_required": second_pass_required,
        "status": "refinement_needed" if second_pass_required else "optimal"
    }
