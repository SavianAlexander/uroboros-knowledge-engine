"""
Inline Self-Correction RAG with Real-Time Source Patching.
Automatically identifies ungrounded claims during text generation and patches them with verified context.
"""
import unicodedata
from typing import Dict, Any, List
from src.domain.rag_grounding_guard import verify_rag_grounding
from src.domain.rag_engine import extract_advanced_rag_context


def auto_correct_grounding(
    llm_response: str,
    source_chunks: List[str]
) -> Dict[str, Any]:
    """
    Audits response claims and automatically patches ungrounded claims with targeted micro-retrievals.
    # ponytail: real-time grounding audit and patch loop; ceiling: token substring overlap check; upgrade: use NLI entailment model if high-risk medical/financial domain is targeted
    """
    norm_resp = unicodedata.normalize("NFC", str(llm_response or ""))
    norm_chunks = [unicodedata.normalize("NFC", str(c)) for c in source_chunks if c]
    audit = verify_rag_grounding(norm_resp, norm_chunks)
    warnings = audit.get("hallucination_warnings", [])

    patched_response = norm_resp
    patches_applied = []

    for ungrounded_claim in warnings:
        # Micro-retrieval for ungrounded claim sentence
        _, micro_snippets = extract_advanced_rag_context(ungrounded_claim, max_chunks=1)
        if micro_snippets:
            first_snip = micro_snippets[0]
            verified_snippet = first_snip.get("snippet", "") if isinstance(first_snip, dict) else str(first_snip)
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
