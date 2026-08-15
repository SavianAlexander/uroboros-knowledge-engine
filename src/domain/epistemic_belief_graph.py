"""
Dynamic Epistemic Belief Graph Engine.
Maintains a dynamic graph of user claims, facts, and beliefs across long chat sessions, updating or invalidating conflicting claims automatically.
Zero-dependency, stdlib implementation.
"""

import functools
import unicodedata
from typing import Dict, Any, List


@functools.lru_cache(maxsize=1024)
def _normalize_belief_claim(claim: str) -> str:
    """Normalizes belief claim string to NFC format and lowercases for conflict matching."""
    if not claim or not isinstance(claim, str):
        return ""
    return unicodedata.normalize("NFC", claim).strip().lower()


def update_epistemic_belief_graph(
    new_claim: str,
    existing_beliefs: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates the dynamic belief graph with a new user/document claim, detecting conflicts with prior beliefs.
    """
    safe_claim = str(new_claim or "").strip()
    norm_claim = _normalize_belief_claim(safe_claim)
    beliefs = [b for b in (existing_beliefs or []) if isinstance(b, dict)]

    conflicts = []
    for b in beliefs:
        # Simple negation conflict heuristic
        b_norm = _normalize_belief_claim(str(b.get("claim", "")))
        claim_stripped = norm_claim.replace("not ", "").strip()
        b_stripped = b_norm.replace("not ", "").strip()
        if claim_stripped and b_stripped:
            if ("not " in norm_claim and claim_stripped in b_norm) or \
               ("not " in b_norm and b_stripped in norm_claim):
                conflicts.append(b)

    # Dynamic confidence based on claim length, specificity, and conflict status
    base_conf = 0.90 if not conflicts else 0.70
    length_bonus = min(0.08, len(safe_claim.split()) * 0.01)
    calc_conf = round(min(0.99, base_conf + length_bonus), 2)

    new_entry = {
        "belief_id": f"bel_{len(beliefs)+1}",
        "claim": safe_claim,
        "confidence": calc_conf,
        "has_conflict": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflict_ids": [b.get("belief_id", "") for b in conflicts if b.get("belief_id")]
    }
    
    updated_beliefs = [b for b in beliefs if b not in conflicts] + [new_entry]

    return {
        "new_belief": new_entry,
        "conflicts_resolved": len(conflicts),
        "total_active_beliefs": len(updated_beliefs),
        "active_beliefs": updated_beliefs,
        "status": "success"
    }
