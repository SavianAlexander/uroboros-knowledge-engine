"""
Empirically True, Real-World Grounded Retrieval & Epistemic Invariant Engine (Milestone M5).
Primary Coordinator integrating:
- Epistemic Evidentiary Tiering (F1) & Authority-Weighted RRF (F2)
- Temporal Validity & Superseding Detection (F3) & Staleness Decay (F4)
- Dense Propositional Decomposition & Breadcrumb Scoping (F5)
- Cross-Document Consensus Matrix & Contradiction Resolution (F6)
- Physical, Mathematical & Computational Boundary Guards (F7, F8, F9, F10, F11)
- Composite Grounding Scorecard & Hallucination Refusal Gate (F12)
"""

import math
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Set, Union

try:
    from src.infrastructure.database import get_db
except ImportError:
    get_db = None

# Epistemic Evidentiary Tiering & RRF Fusion (M1)
from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)

# Temporal Validity & Staleness Decay (M1)
from src.domain.temporal_validity import (
    detect_temporal_validity,
    compute_temporal_decay,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)

# Dense Propositional Decomposition & Breadcrumb Scoping (M2)
from src.domain.dense_propositions import (
    decompose_into_propositions,
    expand_propositions_to_parent_context,
    format_breadcrumb_scope
)

# Cross-Document Consensus & Contradiction Resolution Matrix (M3)
from src.domain.consensus_matrix import (
    evaluate_cross_document_consensus,
    extract_document_assertions,
    compute_consensus_boost,
    resolve_contradiction_hierarchy,
    HIGH_CONSENSUS,
    MODERATE_CONSENSUS,
    NEUTRAL,
    SINGLE_SOURCE,
    MINOR_DISCREPANCY,
    CONTRADICTION_DETECTED,
    CONTRADICTION_UNRESOLVED,
    CONFLICT_NUMERICAL_DISCREPANCY,
    CONFLICT_POLARITY_INVERSION,
    CONFLICT_STATUS_COLLISION,
    TIER_1_EPISTEMIC_DOMINANCE,
    TIER_2_TEMPORAL_DOMINANCE,
    TIER_3_CONDITION_SCOPE,
    TIER_4_UNRESOLVABLE
)

# Boundary Invariant Guards (M4)
from src.domain.boundary_invariants import (
    check_optical_latency_invariant,
    check_usl_scalability_invariant,
    check_carnot_efficiency_invariant,
    check_landauer_erasure_invariant,
    check_landauer_limit_invariant,
    check_cap_pacelc_invariant,
    check_shannon_capacity_invariant,
    evaluate_all_boundary_invariants,
    verify_optical_latency_invariant,
    verify_usl_invariant,
    verify_cap_pacelc_invariant,
    verify_carnot_landauer_invariant,
    verify_shannon_capacity_invariant,
    parse_claims_from_text,
    INV_SPEED_OF_LIGHT,
    INV_USL,
    INV_CAP_PACELC,
    INV_CARNOT,
    INV_LANDAUER,
    INV_SHANNON,
    VIOLATION_SPEED_OF_LIGHT,
    VIOLATION_SUPERLINEAR_SPEEDUP,
    VIOLATION_COHERENCY_RETROGRADE,
    VIOLATION_USL_SCALABILITY,
    VIOLATION_CAP_PARTITION,
    VIOLATION_PACELC_ZERO_LATENCY,
    VIOLATION_QUORUM_DEFICIT,
    VIOLATION_SPLIT_BRAIN,
    VIOLATION_CARNOT_SECOND_LAW,
    VIOLATION_LANDAUER_THERMODYNAMIC,
    VIOLATION_SHANNON_CAPACITY
)

# Grounding Scorecard & Refusal Gate (M5)
from src.domain.grounding_scorecard import (
    compute_grounding_scorecard,
    generate_knowledge_gap_diagnostic_report,
    KnowledgeGapDiagnosticReport,
    REFUSAL_THRESHOLD,
    WEIGHT_TIER,
    WEIGHT_CONSENSUS,
    WEIGHT_TEMPORAL,
    STATUS_ACCEPTED,
    STATUS_REFUSED,
    STATUS_GROUNDED,
    STATUS_UNGROUNDED
)

# Comprehensive re-export for backward compatibility
__all__ = [
    # M1 Tiering & RRF
    "classify_source_epistemic_tier",
    "compute_authority_weighted_rrf",
    "TIER_WEIGHTS",
    "TIER_1_PRIMARY",
    "TIER_2_TECH_SPEC",
    "TIER_3_SECONDARY",
    "TIER_4_COMMENTARY",
    # M1 Temporal
    "detect_temporal_validity",
    "compute_temporal_decay",
    "DOMAIN_HALF_LIVES",
    "STATUS_PENALTY_CAPS",
    # M2 Propositions
    "decompose_into_propositions",
    "expand_propositions_to_parent_context",
    "format_breadcrumb_scope",
    # M3 Consensus
    "evaluate_cross_document_consensus",
    "extract_document_assertions",
    "compute_consensus_boost",
    "resolve_contradiction_hierarchy",
    "HIGH_CONSENSUS",
    "MODERATE_CONSENSUS",
    "NEUTRAL",
    "SINGLE_SOURCE",
    "MINOR_DISCREPANCY",
    "CONTRADICTION_DETECTED",
    "CONTRADICTION_UNRESOLVED",
    "CONFLICT_NUMERICAL_DISCREPANCY",
    "CONFLICT_POLARITY_INVERSION",
    "CONFLICT_STATUS_COLLISION",
    "TIER_1_EPISTEMIC_DOMINANCE",
    "TIER_2_TEMPORAL_DOMINANCE",
    "TIER_3_CONDITION_SCOPE",
    "TIER_4_UNRESOLVABLE",
    # M4 Invariants
    "check_optical_latency_invariant",
    "check_usl_scalability_invariant",
    "check_carnot_efficiency_invariant",
    "check_landauer_limit_invariant",
    "check_landauer_erasure_invariant",
    "check_cap_pacelc_invariant",
    "check_shannon_capacity_invariant",
    "evaluate_all_boundary_invariants",
    "verify_optical_latency_invariant",
    "verify_usl_invariant",
    "verify_cap_pacelc_invariant",
    "verify_carnot_landauer_invariant",
    "verify_shannon_capacity_invariant",
    "parse_claims_from_text",
    "INV_SPEED_OF_LIGHT",
    "INV_USL",
    "INV_CAP_PACELC",
    "INV_CARNOT",
    "INV_LANDAUER",
    "INV_SHANNON",
    "VIOLATION_SPEED_OF_LIGHT",
    "VIOLATION_SUPERLINEAR_SPEEDUP",
    "VIOLATION_COHERENCY_RETROGRADE",
    "VIOLATION_USL_SCALABILITY",
    "VIOLATION_CAP_PARTITION",
    "VIOLATION_PACELC_ZERO_LATENCY",
    "VIOLATION_QUORUM_DEFICIT",
    "VIOLATION_SPLIT_BRAIN",
    "VIOLATION_CARNOT_SECOND_LAW",
    "VIOLATION_LANDAUER_THERMODYNAMIC",
    "VIOLATION_SHANNON_CAPACITY",
    # M5 Scorecard & Refusal Gate
    "compute_grounding_scorecard",
    "generate_knowledge_gap_diagnostic_report",
    "KnowledgeGapDiagnosticReport",
    "REFUSAL_THRESHOLD",
    "WEIGHT_TIER",
    "WEIGHT_CONSENSUS",
    "WEIGHT_TEMPORAL",
    "STATUS_ACCEPTED",
    "STATUS_REFUSED",
    "STATUS_GROUNDED",
    "STATUS_UNGROUNDED",
    # Coordinators & High-Level APIs
    "execute_grounded_retrieval",
    "evaluate_grounding_for_claim",
    "GroundedRetrievalEngine"
]


# ==============================================================================
# GROUNDED RETRIEVAL ENGINE COORDINATOR CLASS
# ==============================================================================

class GroundedRetrievalEngine:
    """
    Coordinator engine executing end-to-end grounded retrieval:
    1. Lexical and dense candidate rank fusion with epistemic authority coefficients
    2. Atomic propositional breadcrumb extraction
    3. Cross-document consensus analysis & contradiction matrix resolution
    4. Physical, mathematical & computational boundary invariant validation
    5. Composite Grounding Scorecard calculation and refusal gating
    """

    def __init__(self, top_k: int = 5, refusal_threshold: float = REFUSAL_THRESHOLD):
        self.top_k = max(1, int(top_k))
        self.refusal_threshold = float(refusal_threshold)

    def evaluate_grounding(
        self,
        query: str,
        candidate_passages: Optional[List[Dict[str, Any]]] = None,
        generated_claim: Optional[Union[str, Dict[str, Any], List[Dict[str, Any]]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates composite Grounding Confidence Score (0-100%) and returns refusal verdict
        if score < 0.65 with structured missing knowledge gap diagnostics.
        """
        # Guard for empty or whitespace query
        if not query or not query.strip() or not candidate_passages:
            return {
                "status": "refusal",
                "grounding_status": STATUS_REFUSED,
                "is_grounded": False,
                "refusal_status": True,
                "reason": "ZERO_EVIDENCE",
                "overall_grounded_confidence": 0.0,
                "grounding_score": 0.0,
                "score": 0.0,
                "refusal_threshold": self.refusal_threshold,
                "message": f"Confidence score 0.0 < {self.refusal_threshold} threshold. Zero evidence found for query: '{query}'",
                "top_passages_count": 0,
                "diagnostics": {
                    "knowledge_gaps": ["No relevant primary or secondary documents retrieved for query."],
                    "retrieved_count": len(candidate_passages) if candidate_passages else 0,
                    "avg_tier_weight": 0.0,
                    "avg_staleness": 0.0,
                    "consensus_score": 0.0,
                    "invariant_violations": [],
                    "epistemic_deficits": ["No candidate passages retrieved; zero evidentiary backing."],
                    "temporal_deficits": [],
                    "consensus_deficits": [],
                    "recommended_actions": ["Provide relevant reference documents or reformulate query with more specific search terms."],
                    "dissenting_ledger": []
                },
                "diagnostic_report": {
                    "refusal_status": True,
                    "score": 0.0,
                    "threshold": self.refusal_threshold,
                    "epistemic_deficits": ["No candidate passages retrieved; zero evidentiary backing."],
                    "temporal_deficits": [],
                    "consensus_deficits": [],
                    "invariant_violations": [],
                    "recommended_actions": ["Provide relevant reference documents or reformulate query with more specific search terms."],
                    "dissenting_ledger": []
                },
                "passages": [],
                "consensus_audit": {},
                "invariant_audit": {}
            }

        # 1. Authority-Weighted RRF Ranking
        scored_passages = compute_authority_weighted_rrf(
            lexical_ranks=candidate_passages,
            dense_ranks=[],
            k=60,
            intent_weights={"lexical": 1.0, "dense": 0.0}
        )
        top_passages = scored_passages[:self.top_k]

        # 2. Evaluate Grounding Scorecard
        scorecard = compute_grounding_scorecard(
            passages=top_passages,
            generated_claim=generated_claim,
            threshold=self.refusal_threshold
        )

        scorecard["query"] = query
        scorecard["top_passages_count"] = len(top_passages)
        scorecard["consensus_level"] = scorecard.get("consensus_audit", {}).get("consensus_level", NEUTRAL)

        return scorecard

    def execute_retrieval(
        self,
        query: str,
        candidate_passages: Optional[List[Dict[str, Any]]] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Executes retrieval and grounding evaluation."""
        if top_k is not None:
            self.top_k = max(1, int(top_k))
        return execute_grounded_retrieval(query=query, passages=candidate_passages, top_k=self.top_k)

    def evaluate_claim(
        self,
        claim: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        passages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluates grounding for a generated claim against a collection of passages."""
        return evaluate_grounding_for_claim(claim=claim, retrieved_passages=passages, threshold=self.refusal_threshold)


# ==============================================================================
# TOP-LEVEL EXECUTION APIS & BACKWARD-COMPATIBLE SHIMS
# ==============================================================================

def evaluate_grounding_for_claim(
    claim: Union[str, Dict[str, Any], List[Dict[str, Any]]],
    retrieved_passages: List[Dict[str, Any]],
    threshold: float = REFUSAL_THRESHOLD
) -> Dict[str, Any]:
    """
    Evaluates grounding for a specific claim given retrieved passages.
    Cross-checks physical/computational invariants, authority tiering, temporal validity, and consensus.
    """
    return compute_grounding_scorecard(
        passages=retrieved_passages,
        generated_claim=claim,
        threshold=threshold
    )


def execute_grounded_retrieval(
    query: str,
    passages: Optional[List[Dict[str, Any]]] = None,
    top_k: int = 5,
    require_grounded: bool = True
) -> Dict[str, Any]:
    """
    Executes empirically grounded search pipeline across SQLite FTS5 index (or explicit candidate passages),
    applies epistemic source weighting, temporal staleness decay, cross-document consensus, and refusal gating.
    """
    if passages is not None:
        raw_rows = list(passages)
    else:
        raw_rows = []
        if get_db is not None:
            try:
                with get_db() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            """SELECT f.id, f.filepath, f.filename, f.content,
                                      rank
                               FROM fts_files MATCH ?
                               JOIN files f ON fts_files.filepath = f.filepath
                               ORDER BY rank LIMIT 25""",
                            (query,)
                        )
                        raw_rows = [dict(r) for r in cursor.fetchall()]
                    except Exception:
                        cursor.execute(
                            "SELECT id, filepath, filename, content, 0 as rank FROM files WHERE content LIKE ? LIMIT 25",
                            (f"%{query}%",)
                        )
                        raw_rows = [dict(r) for r in cursor.fetchall()]
            except Exception:
                raw_rows = []

    if not raw_rows:
        return {
            "status": "refusal",
            "grounding_status": STATUS_REFUSED,
            "is_grounded": False,
            "refusal_status": True,
            "reason": "HALLUCINATION_REFUSAL_GATE",
            "overall_grounded_confidence": 0.0,
            "grounding_score": 0.0,
            "score": 0.0,
            "refusal_threshold": REFUSAL_THRESHOLD,
            "message": f"Confidence score 0.0 < {REFUSAL_THRESHOLD} threshold. No grounded primary evidence found for query: '{query}'",
            "top_passages_count": 0,
            "diagnostics": {
                "knowledge_gaps": ["No grounded primary evidence found for query."],
                "epistemic_deficits": ["No candidate passages retrieved."],
                "temporal_deficits": [],
                "consensus_deficits": [],
                "recommended_actions": ["Expand retrieval query or provide reference documents."],
                "invariant_violations": [],
                "dissenting_ledger": []
            },
            "diagnostic_report": {
                "refusal_status": True,
                "score": 0.0,
                "threshold": REFUSAL_THRESHOLD,
                "epistemic_deficits": ["No candidate passages retrieved."],
                "temporal_deficits": [],
                "consensus_deficits": [],
                "invariant_violations": [],
                "recommended_actions": ["Expand retrieval query or provide reference documents."],
                "dissenting_ledger": []
            },
            "passages": []
        }

    # Format lexical ranks for authority-weighted RRF
    lexical_candidates = []
    for rank_idx, r in enumerate(raw_rows):
        fname = str(r.get("filename") or r.get("filepath") or "")
        content = str(r.get("content") or r.get("snippet") or "")
        temporal_info = detect_temporal_validity(content)

        lexical_candidates.append({
            "id": r.get("id", rank_idx + 1),
            "filepath": r.get("filepath", ""),
            "filename": fname,
            "content": content[:500],
            "rank": int(r.get("rank") or (rank_idx + 1)),
            "temporal_validity": temporal_info,
            "staleness_coefficient": temporal_info["staleness_coefficient"],
            "epistemic_weight": r.get("epistemic_weight"),
            "epistemic_tier": r.get("epistemic_tier")
        })

    engine = GroundedRetrievalEngine(top_k=top_k, refusal_threshold=REFUSAL_THRESHOLD)
    result = engine.evaluate_grounding(query=query, candidate_passages=lexical_candidates)

    if not require_grounded and result["status"] == "refusal":
        result["forced_status"] = "UNGROUNDED_ALLOW"

    return result
