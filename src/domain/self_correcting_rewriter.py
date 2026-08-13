"""
Agentic Self-Correction RAG Rewriter Engine.
Scans RAG output and rewrites ungrounded hallucination claims using verified source context.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List
from src.domain.rag_grounding_guard import verify_rag_grounding, RE_SENTENCE


def rewrite_grounded_answer(
    llm_response: str,
    source_chunks: List[str],
    threshold: float = 0.4
) -> Dict[str, Any]:
    """
    Evaluates LLM response for hallucination warnings.
    If hallucinated claims are found, strip-purges or rewrites them using grounded source chunks.
    """
    guard_res = verify_rag_grounding(llm_response, source_chunks, threshold)
    
    if guard_res["overall_status"] == "grounded" or not guard_res["hallucination_warnings"]:
        return {
            "original_answer": llm_response,
            "rewritten_answer": llm_response,
            "was_rewritten": False,
            "warnings_resolved": 0,
            "status": "grounded"
        }

    sentences = [s.strip() for s in RE_SENTENCE.findall(llm_response) if s.strip()]
    bad_sentences = set(guard_res["hallucination_warnings"])
    
    clean_sentences = [s for s in sentences if s not in bad_sentences]
    
    if not clean_sentences and source_chunks:
        rewritten = f"Based on verified vault records: {source_chunks[0]}"
    else:
        rewritten = " ".join(clean_sentences)

    return {
        "original_answer": llm_response,
        "rewritten_answer": rewritten,
        "was_rewritten": True,
        "warnings_resolved": len(guard_res["hallucination_warnings"]),
        "status": "self_corrected"
    }
