"""
Inline Self-Correction RAG with Real-Time Source Patching.
Automatically identifies ungrounded claims during text generation and patches them with verified context.
"""

from typing import Dict, Any, List
from src.domain.rag_grounding_guard import verify_rag_grounding
from src.domain.rag_engine import extract_advanced_rag_context


def auto_correct_grounding(
    llm_response: str,
    source_chunks: List[str]
) -> Dict[str, Any]:
    """
    Audits response claims and automatically patches ungrounded claims with targeted micro-retrievals.
    # ponytail: real-time grounding audit and patch loop
    """
    audit = verify_rag_grounding(llm_response, source_chunks)
    warnings = audit.get("hallucination_warnings", [])

    patched_response = llm_response
    patches_applied = []

    for ungrounded_claim in warnings:
        # Micro-retrieval for ungrounded claim sentence
        _, micro_snippets = extract_advanced_rag_context(ungrounded_claim, max_chunks=1)
        if micro_snippets:
            verified_snippet = micro_snippets[0].get("snippet", "")
            patch_note = f" [Verified Context: {verified_snippet[:150]}...]"
            patched_response = patched_response.replace(ungrounded_claim, f"{ungrounded_claim}{patch_note}")
            patches_applied.append({"claim": ungrounded_claim, "patch": patch_note})

    return {
        "status": "success",
        "original_status": audit.get("overall_status"),
        "total_warnings": len(warnings),
        "total_patches_applied": len(patches_applied),
        "patched_response": patched_response,
        "patches_applied": patches_applied
    }
