"""
Automated Grounding Scorecard, Refusal Gate & Diagnostic Report Engine (Milestone M5 / Feature F12).
Zero-dependency, standard-library implementation for composite grounding confidence scoring,
binary invariant veto gating, and structured knowledge gap diagnostic reporting.
"""

import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)
from src.domain.temporal_validity import detect_temporal_validity, compute_temporal_decay
from src.domain.consensus_matrix import evaluate_cross_document_consensus, SINGLE_SOURCE
from src.domain.boundary_invariants import evaluate_all_boundary_invariants

# --- Scorecard Constants & Default Weights ---
REFUSAL_THRESHOLD: float = 0.65

WEIGHT_TIER: float = 0.45
WEIGHT_CONSENSUS: float = 0.35
WEIGHT_TEMPORAL: float = 0.20

# Status Identifiers
STATUS_ACCEPTED: str = "ACCEPTED"
STATUS_REFUSED: str = "REFUSED"
STATUS_GROUNDED: str = "GROUNDED"
STATUS_UNGROUNDED: str = "UNGROUNDED"


@dataclass
class KnowledgeGapDiagnosticReport:
    """
    Structured Diagnostic Report identifying epistemic deficits, temporal staleness,
    cross-document consensus contradictions, and physical/computational boundary violations.
    """
    refusal_status: bool
    score: float
    threshold: float = REFUSAL_THRESHOLD
    epistemic_deficits: List[str] = field(default_factory=list)
    temporal_deficits: List[str] = field(default_factory=list)
    consensus_deficits: List[str] = field(default_factory=list)
    invariant_violations: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    dissenting_ledger: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes diagnostic report to standard dictionary format."""
        return asdict(self)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


def generate_knowledge_gap_diagnostic_report(
    score: float,
    threshold: float = REFUSAL_THRESHOLD,
    passages: Optional[List[Dict[str, Any]]] = None,
    consensus_audit: Optional[Dict[str, Any]] = None,
    invariant_audit: Optional[Dict[str, Any]] = None,
    avg_tier_weight: float = 0.0,
    avg_temporal_score: float = 1.0,
    consensus_score: float = 0.70
) -> KnowledgeGapDiagnosticReport:
    """
    Constructs a comprehensive KnowledgeGapDiagnosticReport based on observed evidentiary deficits.
    """
    passages = passages or []
    consensus_audit = consensus_audit or {}
    invariant_audit = invariant_audit or {}

    refusal_status = bool(score < (threshold - 1e-6) or not invariant_audit.get("valid", True))
    epistemic_deficits: List[str] = []
    temporal_deficits: List[str] = []
    consensus_deficits: List[str] = []
    recommended_actions: List[str] = []

    # 1. Epistemic Deficit Analysis
    tier_counts = {TIER_1_PRIMARY: 0, TIER_2_TECH_SPEC: 0, TIER_3_SECONDARY: 0, TIER_4_COMMENTARY: 0}
    for p in passages:
        tier = p.get("epistemic_tier", TIER_4_COMMENTARY)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        if tier == TIER_4_COMMENTARY:
            fname = p.get("filename", "unknown_source")
            epistemic_deficits.append(
                f"Passage '{fname}' is Tier 4 commentary (weight {TIER_WEIGHTS[TIER_4_COMMENTARY]}) with unverified evidentiary status."
            )

    if not passages:
        epistemic_deficits.append("No candidate passages retrieved; zero evidentiary backing.")
    elif tier_counts.get(TIER_1_PRIMARY, 0) == 0 and tier_counts.get(TIER_2_TECH_SPEC, 0) == 0:
        epistemic_deficits.append(
            "Missing primary sources (Tier 1 standards/statutes or Tier 2 technical specifications); candidate pool relies solely on lower-tier commentary/literature."
        )

    if passages and avg_tier_weight < 0.70:
        epistemic_deficits.append(
            f"Average epistemic tier weight ({round(avg_tier_weight, 3)}) is below the recommended 0.70 baseline."
        )

    # 2. Temporal Deficit Analysis
    for p in passages:
        temp = p.get("temporal_validity") or {}
        fname = p.get("filename", "unknown_source")
        if temp.get("is_superseded") or temp.get("temporal_status") == "SUPERSEDED":
            by_marker = temp.get("superseded_by")
            marker_str = f" by {by_marker}" if by_marker else ""
            temporal_deficits.append(
                f"Document '{fname}' is SUPERSEDED{marker_str} (staleness coefficient: {round(temp.get('staleness_coefficient', 0.40), 2)})."
            )
        elif temp.get("temporal_status") == "DEPRECATED":
            temporal_deficits.append(
                f"Document '{fname}' is DEPRECATED (staleness coefficient: {round(temp.get('staleness_coefficient', 0.50), 2)})."
            )

    if passages and avg_temporal_score < 0.70:
        temporal_deficits.append(
            f"Average temporal validity score ({round(avg_temporal_score, 3)}) indicates stale or superseded document reliance."
        )

    # 3. Consensus Deficit Analysis
    contradictions = consensus_audit.get("contradictions", [])
    dissenting_ledger = consensus_audit.get("dissenting_ledger", [])
    if contradictions:
        consensus_deficits.append(
            f"Detected {len(contradictions)} cross-document factual contradiction(s) across retrieved candidates."
        )
    if dissenting_ledger:
        for dissent in dissenting_ledger:
            c_type = dissent.get("conflict_type", "EPISTEMIC_CONFLICT")
            src_a = dissent.get("source_a", "Source A")
            src_b = dissent.get("source_b", "Source B")
            consensus_deficits.append(
                f"Unresolved Tier 4 epistemic conflict ({c_type}) between '{src_a}' and '{src_b}'."
            )
    if passages and len(passages) >= 2 and consensus_score < 0.65:
        consensus_deficits.append(
            f"Cross-document consensus score ({round(consensus_score, 3)}) is below required threshold due to conflicting assertions."
        )

    # 4. Invariant Violations
    invariant_violations = list(invariant_audit.get("violations", []))

    # 5. Recommended Actions
    if invariant_violations:
        recommended_actions.append(
            "Revise technical claim parameters to comply with first-principles physical, mathematical, and computational invariants."
        )
    if epistemic_deficits:
        recommended_actions.append(
            "Retrieve authoritative Tier 1 (statutes, ISO/IEC/RFC standards, source code) or Tier 2 (official API specs, datasheets) documentation."
        )
    if temporal_deficits:
        recommended_actions.append(
            "Query current active standards or latest amendments to replace superseded/deprecated documents."
        )
    if dissenting_ledger:
        recommended_actions.append(
            "Arbitrate conflicting factual assertions between equal-authority sources or isolate distinct operational condition scopes."
        )
    elif consensus_deficits:
        recommended_actions.append(
            "Corroborate findings across additional independent multi-source references."
        )
    if not recommended_actions and refusal_status:
        recommended_actions.append(
            "Expand retrieval query context to gather corroborating factual evidence."
        )

    return KnowledgeGapDiagnosticReport(
        refusal_status=refusal_status,
        score=round(score, 4),
        threshold=threshold,
        epistemic_deficits=epistemic_deficits,
        temporal_deficits=temporal_deficits,
        consensus_deficits=consensus_deficits,
        invariant_violations=invariant_violations,
        recommended_actions=recommended_actions,
        dissenting_ledger=dissenting_ledger
    )


def compute_grounding_scorecard(
    passages: Optional[List[Dict[str, Any]]] = None,
    invariant_results: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    generated_claim: Optional[Union[str, Dict[str, Any], List[Dict[str, Any]]]] = None,
    threshold: float = REFUSAL_THRESHOLD,
    weight_tier: float = WEIGHT_TIER,
    weight_consensus: float = WEIGHT_CONSENSUS,
    weight_temporal: float = WEIGHT_TEMPORAL
) -> Dict[str, Any]:
    """
    Calculates the Composite Grounding Confidence Score:
        S_grounding = M_invariant * (w_tier * W_bar_tier + w_consensus * S_consensus + w_temporal * S_temporal)

    Enforces the >= 0.65 threshold hallucination refusal gate and returns a complete
    evaluation dictionary including status, score breakdown, and KnowledgeGapDiagnosticReport.

    Args:
        passages: List of candidate passages with metadata, epistemic tier, and temporal validity.
        invariant_results: Pre-computed invariant evaluation dictionary or list of violations.
        generated_claim: Raw claim text or structured claim dict(s) to evaluate against boundary invariants.
        threshold: Refusal gate threshold (default: 0.65).
        weight_tier: Weight for average epistemic tier authority (default: 0.45).
        weight_consensus: Weight for cross-document consensus score (default: 0.35).
        weight_temporal: Weight for average temporal validity score (default: 0.20).

    Returns:
        Structured evaluation dictionary containing:
        - status: 'ACCEPTED' / 'GROUNDED' or 'REFUSED' / 'UNGROUNDED'
        - grounding_score: float in [0.0, 1.0]
        - refusal_status: bool (True if refused, False if accepted)
        - refusal_threshold: float
        - epistemic_tier_average: float
        - temporal_validity_average: float
        - consensus_score: float
        - invariant_multiplier: 1.0 or 0.0
        - diagnostic_report: KnowledgeGapDiagnosticReport dict
        - passages: evaluated candidate passages
    """
    candidate_passages = passages or []

    # 1. Epistemic Tier Processing
    enriched_passages = []
    tier_weights_list = []
    temporal_scores_list = []

    for p in candidate_passages:
        doc = dict(p)
        fname = str(doc.get("filename") or doc.get("filepath") or "")
        content = str(doc.get("content") or doc.get("snippet") or "")
        meta = doc.get("metadata") or {}

        # Epistemic tier resolution
        if "epistemic_weight" in doc and doc["epistemic_weight"] is not None:
            try:
                w_tier = float(doc["epistemic_weight"])
            except (ValueError, TypeError):
                w_tier = 0.35
            tier = doc.get("epistemic_tier") or (
                TIER_1_PRIMARY if w_tier >= 1.0 else
                TIER_2_TECH_SPEC if w_tier >= 0.85 else
                TIER_3_SECONDARY if w_tier >= 0.70 else
                TIER_4_COMMENTARY
            )
            doc["epistemic_tier"] = tier
            doc["epistemic_weight"] = w_tier
        elif "epistemic_tier" in doc and doc["epistemic_tier"] in TIER_WEIGHTS:
            tier = doc["epistemic_tier"]
            w_tier = float(doc.get("epistemic_weight") or TIER_WEIGHTS[tier])
            doc["epistemic_weight"] = w_tier
        else:
            tier, w_tier = classify_source_epistemic_tier(fname, content, meta)
            doc["epistemic_tier"] = tier
            doc["epistemic_weight"] = w_tier

        # Temporal validity resolution
        if "staleness_coefficient" in doc and doc["staleness_coefficient"] is not None:
            try:
                staleness = float(doc["staleness_coefficient"])
            except (ValueError, TypeError):
                staleness = 1.0
            if "temporal_validity" not in doc or not isinstance(doc["temporal_validity"], dict):
                temp_info = detect_temporal_validity(content, metadata=meta)
                temp_info["staleness_coefficient"] = staleness
                doc["temporal_validity"] = temp_info
        elif "temporal_validity" in doc and isinstance(doc["temporal_validity"], dict):
            temp_info = doc["temporal_validity"]
            staleness = float(temp_info.get("staleness_coefficient", 1.0))
            doc["staleness_coefficient"] = staleness
        else:
            temp_info = detect_temporal_validity(content, metadata=meta)
            staleness = float(temp_info.get("staleness_coefficient", 1.0))
            doc["temporal_validity"] = temp_info
            doc["staleness_coefficient"] = staleness

        tier_weights_list.append(w_tier)
        temporal_scores_list.append(staleness)
        enriched_passages.append(doc)

    avg_tier = (sum(tier_weights_list) / len(tier_weights_list)) if tier_weights_list else 0.35
    avg_temporal = (sum(temporal_scores_list) / len(temporal_scores_list)) if temporal_scores_list else 1.0

    # 2. Cross-Document Consensus Evaluation
    if len(enriched_passages) >= 2:
        consensus_audit = evaluate_cross_document_consensus(enriched_passages)
        consensus_score = float(consensus_audit.get("consensus_score", 0.70))
    elif len(enriched_passages) == 1:
        consensus_audit = {
            "consensus_level": SINGLE_SOURCE,
            "consensus_score": 0.70,
            "agreements_count": 0,
            "contradictions_count": 0,
            "contradictions": [],
            "resolved_claims": [],
            "dissenting_ledger": [],
            "pairwise_nli": []
        }
        consensus_score = 0.70
    else:
        consensus_audit = {
            "consensus_level": SINGLE_SOURCE,
            "consensus_score": 0.0,
            "agreements_count": 0,
            "contradictions_count": 0,
            "contradictions": [],
            "resolved_claims": [],
            "dissenting_ledger": [],
            "pairwise_nli": []
        }
        consensus_score = 0.0

    # 3. Physical & Computational Boundary Invariant Evaluation
    if invariant_results is not None:
        if isinstance(invariant_results, dict):
            inv_audit = invariant_results
        elif isinstance(invariant_results, list):
            inv_audit = {
                "valid": len(invariant_results) == 0,
                "violations": invariant_results,
                "multiplier": 0.0 if len(invariant_results) > 0 else 1.0,
                "diagnostics": [v.get("violation_details", "") for v in invariant_results if isinstance(v, dict)]
            }
        else:
            inv_audit = {"valid": True, "violations": [], "multiplier": 1.0, "diagnostics": []}
    elif generated_claim is not None and generated_claim != "":
        inv_audit = evaluate_all_boundary_invariants(generated_claim)
    else:
        inv_audit = {"valid": True, "violations": [], "multiplier": 1.0, "diagnostics": []}

    m_invariant = float(inv_audit.get("multiplier", 1.0 if inv_audit.get("valid", True) else 0.0))

    # 4. Composite Grounding Score Calculation
    # Normalize weights if custom
    total_w = weight_tier + weight_consensus + weight_temporal
    w_t = weight_tier / total_w if total_w > 0 else WEIGHT_TIER
    w_c = weight_consensus / total_w if total_w > 0 else WEIGHT_CONSENSUS
    w_temp = weight_temporal / total_w if total_w > 0 else WEIGHT_TEMPORAL

    if not candidate_passages:
        raw_score = 0.0
        final_score = 0.0
    else:
        raw_score = (w_t * avg_tier) + (w_c * consensus_score) + (w_temp * avg_temporal)
        final_score = m_invariant * raw_score

    final_score = round(min(1.0, max(0.0, final_score)), 4)

    # 5. Hallucination Refusal Gate Thresholding
    is_grounded = bool(final_score >= (threshold - 1e-6) and m_invariant > 0.5)
    status = STATUS_ACCEPTED if is_grounded else STATUS_REFUSED

    # 6. Generate Structured KnowledgeGapDiagnosticReport
    diagnostic_report = generate_knowledge_gap_diagnostic_report(
        score=final_score,
        threshold=threshold,
        passages=enriched_passages,
        consensus_audit=consensus_audit,
        invariant_audit=inv_audit,
        avg_tier_weight=avg_tier,
        avg_temporal_score=avg_temporal,
        consensus_score=consensus_score
    )

    # Build refusal reason code
    reasons = []
    if m_invariant == 0.0:
        reasons.append("BOUNDARY_INVARIANT_VETO")
    if not candidate_passages:
        reasons.append("ZERO_EVIDENCE")
    elif final_score < (threshold - 1e-6):
        reasons.append("HALLUCINATION_REFUSAL_GATE")
    reason_code = "_AND_".join(reasons) if reasons else "GROUNDED_AND_VERIFIED"

    return {
        "status": "success" if is_grounded else "refusal",
        "grounding_status": status,
        "is_grounded": is_grounded,
        "refusal_status": not is_grounded,
        "grounding_score": final_score,
        "overall_grounded_confidence": round(final_score, 2),
        "score": final_score,
        "refusal_threshold": threshold,
        "reason": reason_code,
        "message": (
            f"Grounding confidence ({final_score}) meets threshold {threshold}."
            if is_grounded else
            f"Grounded confidence ({final_score}) is below the required {threshold} threshold or violated physical invariants."
        ),
        "epistemic_tier_average": round(avg_tier, 4),
        "temporal_validity_average": round(avg_temporal, 4),
        "consensus_score": round(consensus_score, 4),
        "invariant_multiplier": m_invariant,
        "diagnostic_report": diagnostic_report.to_dict(),
        "diagnostics": {
            "avg_tier_weight": round(avg_tier, 2),
            "avg_staleness": round(avg_temporal, 2),
            "consensus_score": round(consensus_score, 2),
            "invariant_violations": inv_audit.get("violations", []),
            "knowledge_gaps": diagnostic_report.epistemic_deficits + diagnostic_report.temporal_deficits + diagnostic_report.consensus_deficits,
            "epistemic_deficits": diagnostic_report.epistemic_deficits,
            "temporal_deficits": diagnostic_report.temporal_deficits,
            "consensus_deficits": diagnostic_report.consensus_deficits,
            "recommended_actions": diagnostic_report.recommended_actions,
            "dissenting_ledger": diagnostic_report.dissenting_ledger
        },
        "passages": enriched_passages,
        "consensus_audit": consensus_audit,
        "invariant_audit": inv_audit
    }
