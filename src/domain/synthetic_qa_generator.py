"""
Autonomous Synthetic QA Dataset Generator Engine.
Generates synthetic question-answer-context triples from raw text for continuous evaluation.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any, List
from src.domain.rag_grounding_guard import split_sentences


def generate_synthetic_qa_triples(
    document_text: str,
    max_triples: int = 5
) -> Dict[str, Any]:
    """
    Parses document text and generates synthetic QA triples for offline benchmarking.
    """
    if not document_text:
        return {"triples": [], "count": 0, "status": "empty_text"}

    sentences = [s for s in split_sentences(document_text) if len(s) > 20]
    
    triples = []
    for idx, sent in enumerate(sentences[:max_triples]):
        # Extract main key phrase for question generation
        words = re.findall(r'\b[a-zA-Z]{4,}\b', sent)
        key_phrase = " ".join(words[:3]) if len(words) >= 3 else "concept"

        question = f"What does the document state regarding {key_phrase}?"
        answer = sent
        triples.append({
            "id": f"syn_qa_{idx+1}",
            "question": question,
            "answer": answer,
            "context_sentence": sent,
            "confidence_score": 0.92
        })

    return {
        "triples": triples,
        "total_generated": len(triples),
        "status": "success"
    }
