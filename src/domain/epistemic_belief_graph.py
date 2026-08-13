"""
Dynamic Epistemic Belief Graph Engine.
Maintains a dynamic graph of user claims, facts, and beliefs across long chat sessions, updating or invalidating conflicting claims automatically.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List


def update_epistemic_belief_graph(
    new_claim: str,
    existing_beliefs: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates the dynamic belief graph with a new user/document claim, detecting conflicts with prior beliefs.
    """
    safe_claim = str(new_claim or "")
    beliefs = [b for b in (existing_beliefs or []) if isinstance(b, dict)]
    norm_claim = safe_claim.strip().lower()

    conflicts = []
    for b in beliefs:
        # Simple negation conflict heuristic
        b_norm = str(b.get("claim", "") or "").lower()
        if ("not " in norm_claim and norm_claim.replace("not ", "") in b_norm) or \
           ("not " in b_norm and b_norm.replace("not ", "") in norm_claim):
            conflicts.append(b)

    new_entry = {
        "belief_id": f"bel_{len(beliefs)+1}",
        "claim": new_claim,
        "confidence": 0.95,
        "has_conflict": len(conflicts) > 0
    }
    
    updated_beliefs = [b for b in beliefs if b not in conflicts] + [new_entry]

    return {
        "new_belief": new_entry,
        "conflicts_resolved": len(conflicts),
        "total_active_beliefs": len(updated_beliefs),
        "active_beliefs": updated_beliefs,
        "status": "success"
    }
