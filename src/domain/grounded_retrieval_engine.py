"""
Empirically True, Real-World Grounded Retrieval & Epistemic Invariant Engine.
Zero-dependency, standard-library implementation for evidentiary source tiering,
temporal staleness & superseding document detection, propositional breadcrumb scoping,
cross-document contradiction resolution, and physical/computational boundary guards.
"""

import re
import math
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set, Union

from src.infrastructure.database import get_db
from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)
from src.domain.temporal_validity import (
    detect_temporal_validity,
    compute_temporal_decay,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)
from src.domain.dense_propositions import (
    decompose_into_propositions,
    expand_propositions_to_parent_context,
    format_breadcrumb_scope
)
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

# Re-export for backward compatibility
__all__ = [
    "classify_source_epistemic_tier",
    "compute_authority_weighted_rrf",
    "detect_temporal_validity",
    "compute_temporal_decay",
    "decompose_into_propositions",
    "expand_propositions_to_parent_context",
    "format_breadcrumb_scope",
    "evaluate_cross_document_consensus",
    "extract_document_assertions",
    "compute_consensus_boost",
    "resolve_contradiction_hierarchy",
    "check_optical_latency_invariant",
    "check_usl_scalability_invariant",
    "check_carnot_efficiency_invariant",
    "check_landauer_limit_invariant",
    "check_cap_pacelc_invariant",
    "check_shannon_capacity_invariant",
    "evaluate_all_boundary_invariants",
    "verify_optical_latency_invariant",
    "verify_usl_invariant",
    "verify_cap_pacelc_invariant",
    "verify_carnot_landauer_invariant",
    "verify_shannon_capacity_invariant",
    "execute_grounded_retrieval",
    "GroundedRetrievalEngine",
    "TIER_WEIGHTS",
    "TIER_1_PRIMARY",
    "TIER_2_TECH_SPEC",
    "TIER_3_SECONDARY",
    "TIER_4_COMMENTARY",
    "DOMAIN_HALF_LIVES",
    "STATUS_PENALTY_CAPS",
    "HIGH_CONSENSUS",
    "MODERATE_CONSENSUS",
    "NEUTRAL",
    "SINGLE_SOURCE",
    "MINOR_DISCREPANCY",
    "CONTRADICTION_DETECTED",
    "CONTRADICTION_UNRESOLVED"
]


# --- 5. Physical & Computational Boundary Invariant Guards ---
# All physical, mathematical and computational boundary invariants are implemented in
# src.domain.boundary_invariants and re-exported above for backward compatibility.


# --- 6. Grounding Scorecard & Refusal Gate Engine ---
class GroundedRetrievalEngine:
    def __init__(self, top_k: int = 5, refusal_threshold: float = 0.65):
        self.top_k = top_k
        self.refusal_threshold = refusal_threshold

    def evaluate_grounding(
        self,
        query: str,
        candidate_passages: List[Dict[str, Any]],
        generated_claim: Union[str, Dict[str, Any], List[Dict[str, Any]]] = ""
    ) -> Dict[str, Any]:
        """
        Calculates composite Grounding Confidence Score (0-100%) and returns refusal verdict
        if score < 0.65 with structured missing knowledge gap diagnostics.
        """
        if not query or not query.strip() or not candidate_passages:
            return {
                "status": "refusal",
                "reason": "ZERO_EVIDENCE",
                "overall_grounded_confidence": 0.0,
                "refusal_threshold": self.refusal_threshold,
                "message": f"Confidence score 0.0 < {self.refusal_threshold} threshold. Zero evidence found for query: '{query}'",
                "diagnostics": {
                    "knowledge_gaps": ["No relevant primary or secondary documents retrieved for query."],
                    "retrieved_count": len(candidate_passages) if candidate_passages else 0
                },
                "passages": []
            }

        # 1. Authority-Weighted RRF Ranking
        scored_passages = compute_authority_weighted_rrf(
            lexical_ranks=candidate_passages,
            dense_ranks=[],
            k=60,
            intent_weights={"lexical": 1.0, "dense": 0.0}
        )
        top_passages = scored_passages[:self.top_k]

        # 2. Cross-Document Consensus Analysis
        consensus = evaluate_cross_document_consensus(top_passages)

        # 3. Physical & Computational Invariant Evaluation
        inv_audit = evaluate_all_boundary_invariants(generated_claim) if generated_claim else {"valid": True, "violations": [], "multiplier": 1.0}
        invariant_mult = inv_audit["multiplier"]

        # 4. Composite Confidence Calculation
        avg_tier_weight = sum(p.get("epistemic_weight", 0.35) for p in top_passages) / max(1, len(top_passages))
        avg_staleness = sum(p.get("staleness_coefficient", 1.0) for p in top_passages) / max(1, len(top_passages))
        consensus_score = float(consensus.get("consensus_score", 0.70))

        # Formula: 50% Tier Authority, 30% Consensus, 20% Temporal Freshness, multiplied by Invariant Gate
        base_confidence = (avg_tier_weight * 0.50) + (consensus_score * 0.30) + (avg_staleness * 0.20)
        overall_confidence = round(min(1.0, max(0.0, base_confidence * invariant_mult)), 2)

        is_success = (overall_confidence >= self.refusal_threshold) and inv_audit["valid"]

        if not is_success:
            reasons = []
            if not inv_audit["valid"]:
                reasons.append("BOUNDARY_INVARIANT_VETO")
            if overall_confidence < self.refusal_threshold:
                reasons.append("HALLUCINATION_REFUSAL_GATE")

            return {
                "status": "refusal",
                "reason": "_AND_".join(reasons) or "HALLUCINATION_REFUSAL_GATE",
                "overall_grounded_confidence": overall_confidence,
                "refusal_threshold": self.refusal_threshold,
                "message": f"Grounded confidence ({overall_confidence}) is below the required {self.refusal_threshold} threshold or violated physical invariants.",
                "diagnostics": {
                    "avg_tier_weight": round(avg_tier_weight, 2),
                    "avg_staleness": round(avg_staleness, 2),
                    "consensus_score": round(consensus_score, 2),
                    "invariant_violations": inv_audit["violations"],
                    "knowledge_gaps": ["Retrieved sources lack sufficient evidentiary authority or consensus."]
                },
                "passages": top_passages,
                "consensus_audit": consensus,
                "invariant_audit": inv_audit
            }

        return {
            "status": "success",
            "query": query,
            "overall_grounded_confidence": overall_confidence,
            "refusal_threshold": self.refusal_threshold,
            "consensus_level": consensus["consensus_level"],
            "top_passages_count": len(top_passages),
            "passages": top_passages,
            "consensus_audit": consensus,
            "invariant_audit": inv_audit
        }


# --- 7. Unified Grounded Retrieval Pipeline ---
def execute_grounded_retrieval(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Executes empirically grounded search across SQLite FTS5 index, applies epistemic source weighting,
    temporal staleness penalties, and evaluates cross-document consensus.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # FTS5 Lexical Search with Snippets
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

    if not raw_rows:
        return {
            "status": "refusal",
            "reason": "HALLUCINATION_REFUSAL_GATE",
            "overall_grounded_confidence": 0.0,
            "message": f"Confidence score 0.0 < 0.65 threshold. No grounded primary evidence found for query: '{query}'",
            "passages": []
        }

    # Format lexical ranks for authority-weighted RRF
    lexical_candidates = []
    for rank_idx, r in enumerate(raw_rows):
        fname = r.get("filename", "")
        content = r.get("content", "")
        temporal_info = detect_temporal_validity(content)

        lexical_candidates.append({
            "id": r.get("id"),
            "filepath": r.get("filepath", ""),
            "filename": fname,
            "content": content[:500],
            "rank": rank_idx + 1,
            "temporal_validity": temporal_info,
            "staleness_coefficient": temporal_info["staleness_coefficient"]
        })

    engine = GroundedRetrievalEngine(top_k=top_k)
    return engine.evaluate_grounding(query=query, candidate_passages=lexical_candidates)
