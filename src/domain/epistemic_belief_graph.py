"""
Claim Consistency & Contradiction Resolution Engine.
Maintains a consistency graph of facts and claims across sessions, detecting and resolving contradictory assertions.
Standard: Pure Python standard library (unicodedata, re, functools, typing).
"""
import functools
import re
import unicodedata
from typing import Dict, Any, List

OPPOSITE_PAIRS = [
    ("enabled", "disabled"),
    ("allowed", "forbidden"),
    ("valid", "invalid"),
    ("true", "false"),
    ("required", "optional"),
    ("active", "inactive"),
    ("supported", "unsupported")
]


@functools.lru_cache(maxsize=1024)
def _normalize_claim(claim: str) -> str:
    """Normalizes claim string to NFC format and lowercases for conflict matching."""
    if not claim or not isinstance(claim, str):
        return ""
    return unicodedata.normalize("NFC", str(claim)).strip().lower()


def _is_contradiction(c1: str, c2: str) -> bool:
    """Detects whether two claims contradict each other based on negation or antonym polarity."""
    tokens1 = set(re.findall(r'\b\w+\b', c1))
    tokens2 = set(re.findall(r'\b\w+\b', c2))

    # Check for direct 'not' / 'never' inversion on shared subject
    core1 = {w for w in tokens1 if w not in {"not", "never", "no", "is", "are", "a", "the"}}
    core2 = {w for w in tokens2 if w not in {"not", "never", "no", "is", "are", "a", "the"}}
    
    if len(core1.intersection(core2)) >= 2:
        neg1 = bool(tokens1.intersection({"not", "never", "no"}))
        neg2 = bool(tokens2.intersection({"not", "never", "no"}))
        if neg1 != neg2:
            return True

        # Check for antonym polarity
        for pos, neg in OPPOSITE_PAIRS:
            if (pos in tokens1 and neg in tokens2) or (neg in tokens1 and pos in tokens2):
                return True

    return False


def update_epistemic_belief_graph(
    new_claim: str,
    existing_beliefs: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates consistency graph with a new claim, detecting and partitioning conflicting prior assertions.
    """
    safe_claim = str(new_claim or "").strip()
    norm_claim = _normalize_claim(safe_claim)
    beliefs = [b for b in (existing_beliefs or []) if isinstance(b, dict)]

    if not safe_claim:
        return {
            "new_belief": {},
            "conflicts_resolved": 0,
            "total_active_beliefs": len(beliefs),
            "active_beliefs": beliefs,
            "status": "empty_claim"
        }

    conflicts = []
    for b in beliefs:
        b_norm = _normalize_claim(str(b.get("claim", "")))
        if _is_contradiction(norm_claim, b_norm):
            conflicts.append(b)

    words = safe_claim.split()
    confidence = round(min(0.99, 0.80 + min(0.15, len(words) * 0.015)), 2)

    new_entry = {
        "belief_id": f"bel_{len(beliefs)+1}",
        "claim": safe_claim,
        "confidence": confidence,
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
