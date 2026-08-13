"""
Agentic Self-Correction RAG Rewriter Engine.
Scans RAG output and rewrites ungrounded hallucination claims using verified source context.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List
from src.domain.rag_grounding_guard import verify_rag_grounding, split_sentences


def rewrite_grounded_answer(
    llm_response: str,
    source_chunks: List[str],
    threshold: float = 0.4
) -> Dict[str, Any]:
    """
    Evaluates LLM response for hallucination warnings.
    If hallucinated claims are found, strip-purges or rewrites them using grounded source chunks.
    """
    import unicodedata
    norm_resp = unicodedata.normalize("NFC", str(llm_response or ""))
    norm_chunks = [unicodedata.normalize("NFC", str(c)) for c in source_chunks if c]
    guard_res = verify_rag_grounding(norm_resp, norm_chunks, threshold)
    
    if guard_res["overall_status"] == "grounded" or not guard_res["hallucination_warnings"]:
        return {
            "original_answer": llm_response,
            "rewritten_answer": llm_response,
            "was_rewritten": False,
            "warnings_resolved": 0,
            "status": "grounded"
        }

    sentences = split_sentences(llm_response)
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
