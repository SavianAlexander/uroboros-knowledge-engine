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
from typing import List, Dict, Any, Optional, Tuple, Set

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

# Re-export for backward compatibility
__all__ = [
    "classify_source_epistemic_tier",
    "compute_authority_weighted_rrf",
    "detect_temporal_validity",
    "compute_temporal_decay",
    "decompose_into_propositions",
    "evaluate_cross_document_consensus",
    "check_optical_latency_invariant",
    "check_usl_scalability_invariant",
    "check_carnot_efficiency_invariant",
    "execute_grounded_retrieval",
    "TIER_WEIGHTS",
    "TIER_1_PRIMARY",
    "TIER_2_TECH_SPEC",
    "TIER_3_SECONDARY",
    "TIER_4_COMMENTARY",
    "DOMAIN_HALF_LIVES",
    "STATUS_PENALTY_CAPS"
]


# --- 3. Atomic Propositional Decomposition & Breadcrumbs ---
def decompose_into_propositions(
    text: str,
    document_title: str,
    section_hierarchy: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Deconstructs complex document text into atomic self-contained factual propositions with breadcrumb scope."""
    breadcrumb = " > ".join([document_title] + (section_hierarchy or []))
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    propositions = []

    for idx, s in enumerate(sentences):
        s_clean = s.strip()
        if len(s_clean) < 15:
            continue
        propositions.append({
            "proposition_id": f"{document_title}#prop_{idx}",
            "breadcrumb_scope": breadcrumb,
            "statement": s_clean,
            "contextual_statement": f"[{breadcrumb}] {s_clean}"
        })

    return propositions


# --- 4. Cross-Document Consensus & Contradiction Resolver ---
def evaluate_cross_document_consensus(passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates cross-passage consensus and isolates factual/numerical contradictions."""
    if len(passages) < 2:
        return {"consensus_level": "SINGLE_SOURCE", "contradictions": [], "consensus_score": 0.70}

    contradictions = []
    agreements = 0

    # Numerical & status assertion extraction
    claims = []
    for p in passages:
        text = p.get("content", "")
        # Extract numerical quantities with context
        nums = re.findall(r'(\b\d+(?:\.\d+)?\s*(?:%|mb|gb|ms|s|usd|\$|users|nodes|tps|mhz|ghz)?\b)', text, re.I)
        claims.append({"source": p.get("filename", "unknown"), "nums": nums, "text": text})

    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            c1, c2 = claims[i], claims[j]
            # Check for direct numerical contradiction in similar sentences
            overlap = set(c1["nums"]).intersection(set(c2["nums"]))
            if overlap:
                agreements += 1
            elif c1["nums"] and c2["nums"]:
                contradictions.append({
                    "source_a": c1["source"],
                    "source_b": c2["source"],
                    "conflict_type": "NUMERICAL_DISCREPANCY",
                    "values_a": c1["nums"],
                    "values_b": c2["nums"]
                })

    consensus_level = "HIGH_CONSENSUS" if agreements > len(contradictions) else ("CONTRADICTION_DETECTED" if contradictions else "NEUTRAL")
    score = 0.95 if consensus_level == "HIGH_CONSENSUS" else (0.45 if consensus_level == "CONTRADICTION_DETECTED" else 0.70)

    return {
        "consensus_level": consensus_level,
        "consensus_score": score,
        "agreements_count": agreements,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions
    }


# --- 5. Physical & Computational Boundary Invariant Guards ---
def check_optical_latency_invariant(distance_km: float, reported_latency_ms: float) -> Dict[str, Any]:
    """Checks speed-of-light propagation lower bound in optical fiber (n = 1.47)."""
    c_fiber = 299792.458 / 1.47  # ~203,940 km/s
    t_min_one_way_ms = (distance_km / c_fiber) * 1000.0
    t_min_rtt_ms = t_min_one_way_ms * 2.0

    violates = reported_latency_ms < t_min_rtt_ms
    return {
        "invariant": "SPEED_OF_LIGHT_OPTICAL_FIBER",
        "distance_km": distance_km,
        "theoretical_min_rtt_ms": round(t_min_rtt_ms, 2),
        "reported_latency_ms": reported_latency_ms,
        "is_physically_possible": not violates,
        "violation_details": f"Reported {reported_latency_ms}ms RTT violates physical limit of {round(t_min_rtt_ms, 2)}ms for {distance_km}km" if violates else "Compliant with relativity."
    }


def check_usl_scalability_invariant(node_count: int, alpha: float, beta: float, claimed_speedup: float) -> Dict[str, Any]:
    """Universal Scalability Law: speedup = N / (1 + alpha*(N-1) + beta*N*(N-1))."""
    n = float(node_count)
    denom = 1.0 + alpha * (n - 1.0) + beta * n * (n - 1.0)
    theoretical_max_speedup = n / denom if denom > 0 else 1.0

    violates = claimed_speedup > theoretical_max_speedup * 1.05
    return {
        "invariant": "UNIVERSAL_SCALABILITY_LAW",
        "node_count": node_count,
        "alpha_contention": alpha,
        "beta_coherency": beta,
        "theoretical_max_speedup": round(theoretical_max_speedup, 2),
        "claimed_speedup": claimed_speedup,
        "is_computationally_valid": not violates,
        "violation_details": f"Claimed {claimed_speedup}x speedup exceeds USL bound of {round(theoretical_max_speedup, 2)}x at N={node_count}" if violates else "Compliant with USL."
    }


def check_carnot_efficiency_invariant(t_hot_k: float, t_cold_k: float, claimed_efficiency: float) -> Dict[str, Any]:
    """Carnot Thermodynamic Limit: eta_max = 1 - (T_cold / T_hot)."""
    if t_hot_k <= t_cold_k or t_hot_k <= 0:
        return {"is_physically_possible": False, "violation_details": "T_hot must exceed T_cold and 0 Kelvin."}

    max_eta = 1.0 - (t_cold_k / t_hot_k)
    violates = claimed_efficiency > max_eta
    return {
        "invariant": "CARNOT_THERMODYNAMIC_LIMIT",
        "t_hot_k": t_hot_k,
        "t_cold_k": t_cold_k,
        "max_theoretical_efficiency": round(max_eta, 4),
        "claimed_efficiency": claimed_efficiency,
        "is_physically_possible": not violates,
        "violation_details": f"Claimed efficiency {claimed_efficiency*100}% exceeds Carnot ceiling of {round(max_eta*100, 2)}%" if violates else "Compliant with 2nd law of thermodynamics."
    }


# --- 6. Unified Grounded Retrieval Pipeline ---
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

    # Compute authority-weighted RRF across retrieved candidates
    fused_passages = compute_authority_weighted_rrf(
        lexical_ranks=lexical_candidates,
        dense_ranks=[],
        k=60,
        intent_weights={"lexical": 1.0, "dense": 0.0}
    )

    top_passages = fused_passages[:top_k]

    # Evaluate consensus across top passages
    consensus = evaluate_cross_document_consensus(top_passages)

    # Calculate overall confidence
    avg_tier_weight = sum(p["epistemic_weight"] for p in top_passages) / max(1, len(top_passages))
    overall_confidence = round(min(1.0, (avg_tier_weight * 0.7) + (consensus["consensus_score"] * 0.3)), 2)

    # Enforce Refusal Gate
    if overall_confidence < 0.65:
        return {
            "status": "refusal",
            "reason": "HALLUCINATION_REFUSAL_GATE",
            "overall_confidence": overall_confidence,
            "message": f"Grounded confidence ({overall_confidence}) is below the required 0.65 threshold.",
            "passages": top_passages,
            "consensus": consensus
        }

    return {
        "status": "success",
        "query": query,
        "overall_grounded_confidence": overall_confidence,
        "consensus_level": consensus["consensus_level"],
        "top_passages_count": len(top_passages),
        "passages": top_passages,
        "consensus_audit": consensus
    }
