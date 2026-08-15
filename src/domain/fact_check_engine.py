"""
Semantic Contradiction & Fact-Check Engine.
Detects factual contradictions between documents (e.g. Policy A vs Policy B).
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List

RE_QUANTITY = re.compile(r'(\d+(?:\.\d+)?)\s*([a-zA-Z%]+)')
RE_WORDS = re.compile(r'\b[a-zA-Z]{3,}\b')

POLARITY_PAIRS = [
    ("shall ", "shall not "),
    ("shall not ", "shall "),
    ("must ", "must not "),
    ("must not ", "must "),
    ("required", "prohibited"),
    ("prohibited", "required"),
    ("required", "optional"),
    ("optional", "required"),
    ("mandatory", "optional"),
    ("optional", "mandatory"),
    ("allowed", "forbidden"),
    ("forbidden", "allowed"),
    ("enabled", "disabled"),
    ("disabled", "enabled"),
    ("compliant", "non-compliant"),
    ("non-compliant", "compliant"),
    ("true", "false"),
    ("false", "true"),
]


def detect_semantic_contradictions(
    doc_a_clauses: List[str],
    doc_b_clauses: List[str]
) -> Dict[str, Any]:
    """
    Scans two sets of document clauses for factual contradictions, numeric discrepancies, or policy conflicts.
    Zero-dependency stdlib implementation.
    """
    contradictions = []
    valid_a = [unicodedata.normalize("NFC", str(c)).strip() for c in (doc_a_clauses or []) if c is not None and str(c).strip()]
    valid_b = [unicodedata.normalize("NFC", str(c)).strip() for c in (doc_b_clauses or []) if c is not None and str(c).strip()]

    for c_a in valid_a:
        norm_a = c_a.lower()
        words_a = set(w for w in RE_WORDS.findall(norm_a))
        quantities_a = RE_QUANTITY.findall(norm_a)

        for c_b in valid_b:
            norm_b = c_b.lower()
            words_b = set(w for w in RE_WORDS.findall(norm_b))
            quantities_b = RE_QUANTITY.findall(norm_b)

            # Compute subject term overlap
            overlap = words_a.intersection(words_b)
            overlap_ratio = len(overlap) / float(max(1, min(len(words_a), len(words_b))))

            # 1. Dynamic Numeric / Metric Discrepancy Detection on Shared Subject
            if overlap_ratio >= 0.35 and quantities_a and quantities_b:
                for val_a, unit_a in quantities_a:
                    for val_b, unit_b in quantities_b:
                        if unit_a == unit_b and val_a != val_b:
                            contradictions.append({
                                "clause_a": c_a,
                                "clause_b": c_b,
                                "conflict_type": "numerical_discrepancy",
                                "detected_conflict": f"{val_a} {unit_a} vs {val_b} {unit_b}",
                                "severity": "high"
                            })
                            break
                    if contradictions and contradictions[-1]["clause_a"] == c_a and contradictions[-1]["clause_b"] == c_b:
                        break

            # 2. Polarity / Antonym Policy Conflict Detection
            if not any(c["clause_a"] == c_a and c["clause_b"] == c_b for c in contradictions):
                for pos, neg in POLARITY_PAIRS:
                    if pos in norm_a and neg in norm_b:
                        # Ensure sufficient shared subject context
                        if overlap_ratio >= 0.25 or len(overlap) >= 2:
                            contradictions.append({
                                "clause_a": c_a,
                                "clause_b": c_b,
                                "conflict_type": "policy_discrepancy",
                                "detected_conflict": f"'{pos.strip()}' vs '{neg.strip()}'",
                                "severity": "high"
                            })
                            break

    return {
        "contradictions_found": contradictions,
        "total_contradictions": len(contradictions),
        "status": "success"
    }
