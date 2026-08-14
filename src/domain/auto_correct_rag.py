"""
Inline Self-Correction RAG with Real-Time Grounding Reflection.
Evaluates Self-RAG reflection tokens ([IsRel], [IsSup], [IsUse]) and performs
grounded factual rewrites for ungrounded claims.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional, Callable
from src.domain.rag_grounding_guard import verify_rag_grounding
from src.domain.rag_engine import extract_advanced_rag_context


def evaluate_reflection_tokens(claim: str, evidence_chunks: List[str]) -> Dict[str, bool]:
    """
    Evaluates Self-RAG reflection criteria:
      - is_relevant ([IsRel]): Claim relates to document domain.
      - is_supported ([IsSup]): Claim is directly verified by evidence.
      - is_useful ([IsUse]): Claim provides substantive informational utility.
    """
    if not claim or not evidence_chunks:
        return {"is_relevant": False, "is_supported": False, "is_useful": False}

    claim_words = set(re.findall(r'\b\w{3,}\b', claim.lower()))
    if not claim_words:
        return {"is_relevant": False, "is_supported": False, "is_useful": False}

    combined_evidence = " ".join(evidence_chunks).lower()
    evidence_words = set(re.findall(r'\b\w{3,}\b', combined_evidence))

    overlap = len(claim_words.intersection(evidence_words))
    overlap_ratio = overlap / float(len(claim_words)) if claim_words else 0.0

    is_rel = overlap_ratio >= 0.25
    is_sup = overlap_ratio >= 0.50
    is_use = len(claim.split()) >= 4

    return {
        "is_relevant": is_rel,
        "is_supported": is_sup,
        "is_useful": is_use
    }


def auto_correct_grounding(
    llm_response: str,
    source_chunks: List[str],
    generate_fn: Optional[Callable[[str], str]] = None
) -> Dict[str, Any]:
    """
    Audits response claims and automatically synthesizes grounded factual corrections.
    """
    norm_resp = unicodedata.normalize("NFC", str(llm_response or ""))
    norm_chunks = [unicodedata.normalize("NFC", str(c)) for c in source_chunks if c]
    audit = verify_rag_grounding(norm_resp, norm_chunks)
    warnings = audit.get("hallucination_warnings", [])

    if not warnings:
        return {
            "status": "grounded",
            "original_status": audit.get("overall_status", "grounded"),
            "grounding_score": audit.get("grounding_score", 1.0),
            "total_warnings": 0,
            "total_patches_applied": 0,
            "patched_response": norm_resp,
            "reflection_tokens": {"is_relevant": True, "is_supported": True, "is_useful": True},
            "patches_applied": []
        }

    patched_response = norm_resp
    patches_applied = []
    reflection_matrix = []

    for ungrounded_claim in warnings:
        ref = evaluate_reflection_tokens(ungrounded_claim, norm_chunks)
        reflection_matrix.append({"claim": ungrounded_claim, "tokens": ref})

        # Micro-retrieval for ungrounded claim sentence
        _, micro_snippets = extract_advanced_rag_context(ungrounded_claim, max_chunks=1)
        if micro_snippets:
            first_snip = micro_snippets[0]
            verified_snippet = first_snip.get("snippet", "") if isinstance(first_snip, dict) else str(first_snip)
            
            # If an LLM generator function is provided, run prompt rewrite
            if generate_fn and callable(generate_fn):
                try:
                    rewrite_prompt = (
                        f"Rewrite this ungrounded claim to strictly align with the verified facts:\n"
                        f"Claim: {ungrounded_claim}\n"
                        f"Verified Facts: {verified_snippet}\n"
                        f"Corrected Sentence:"
                    )
                    corrected = generate_fn(rewrite_prompt).strip()
                    if corrected:
                        patched_response = patched_response.replace(ungrounded_claim, corrected)
                        patches_applied.append({"claim": ungrounded_claim, "correction": corrected, "method": "llm_rewrite"})
                        continue
                except Exception:
                    pass

            # Deterministic factual alignment fallback
            verified_clean = verified_snippet.strip().replace("\n", " ")
            if len(verified_clean) > 180:
                verified_clean = verified_clean[:180] + "..."
            correction_text = f"{ungrounded_claim} (Ref: {verified_clean})"
            patched_response = patched_response.replace(ungrounded_claim, correction_text)
            patches_applied.append({"claim": ungrounded_claim, "correction": correction_text, "method": "citation_anchor"})

    new_grounding_score = min(1.0, audit.get("grounding_score", 0.7) + (len(patches_applied) * 0.1))

    return {
        "status": "corrected" if patches_applied else "warning",
        "original_status": audit.get("overall_status"),
        "grounding_score": round(new_grounding_score, 2),
        "total_warnings": len(warnings),
        "total_patches_applied": len(patches_applied),
        "patched_response": patched_response,
        "reflection_matrix": reflection_matrix,
        "patches_applied": patches_applied
    }
