"""
Unified Cognitive, Physical & Empirical Verification Guards.
Consolidates Boundary Invariants (Speed-of-Light, USL, CAP/PACELC, Carnot/Landauer, Shannon Capacity),
Cross-Document Consensus & Contradiction Resolution, Epistemic Tiering, and Grounding Scorecard Metrics.
Standard: Pure Python standard library, zero external dependencies.
"""

# Re-export core modules for unified verification
from src.domain.boundary_invariants import (
    evaluate_boundary_invariants,
    SPEED_OF_LIGHT_VACUUM_KM_S,
    BOLTZMANN_CONSTANT_J_K,
    EARTH_RADIUS_KM,
    REFRACTIVE_INDICES,
    INV_SPEED_OF_LIGHT,
    INV_USL,
    INV_CAP_PACELC,
    INV_CARNOT,
    INV_LANDAUER,
    INV_SHANNON
)

from src.domain.consensus_engine import (
    HIGH_CONSENSUS,
    MODERATE_CONSENSUS,
    NEUTRAL,
    SINGLE_SOURCE,
    MINOR_DISCREPANCY,
    CONTRADICTION_DETECTED,
    CONTRADICTION_UNRESOLVED,
    NLI_ENTAILMENT,
    NLI_CONTRADICTION,
    NLI_NEUTRAL,
    evaluate_cross_document_consensus,
    resolve_contradiction_hierarchy,
    compute_consensus_boost
)

# Aliases
resolve_contradictions = resolve_contradiction_hierarchy
compute_consensus_confidence = compute_consensus_boost

from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)

from src.domain.temporal_validity import detect_temporal_validity
from src.domain.grounding_scorecard import compute_grounding_scorecard, KnowledgeGapDiagnosticReport

evaluate_grounding_scorecard = compute_grounding_scorecard
GroundingScorecard = KnowledgeGapDiagnosticReport


def verify_claims_and_consensus(
    claims_or_text: str,
    reference_passages: list = None
) -> dict:
    """
    Unified high-level verification pass combining boundary physical checks,
    cross-document consensus, and grounding evaluation.
    """
    boundary_results = evaluate_boundary_invariants(claims_or_text) if isinstance(claims_or_text, str) else {"invariants": []}
    
    consensus_results = {}
    if reference_passages:
        consensus_results = evaluate_cross_document_consensus(reference_passages)

    return {
        "boundary_verification": boundary_results,
        "consensus_verification": consensus_results,
        "status": "success"
    }
