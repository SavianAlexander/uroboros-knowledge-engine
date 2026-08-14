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
    "STATUS_PENALTY_CAPS"
]


# --- 4. Cross-Document Consensus & Contradiction Resolver ---
def evaluate_cross_document_consensus(passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates cross-passage consensus and isolates factual/numerical contradictions."""
    if len(passages) < 2:
        return {"consensus_level": "SINGLE_SOURCE", "contradictions": [], "consensus_score": 0.70, "agreements_count": 0, "contradictions_count": 0}

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

    # Majority consensus determination
    if agreements >= 1 and (agreements >= len(contradictions) or agreements >= len(claims) // 2):
        consensus_level = "HIGH_CONSENSUS"
        score = 0.95
    elif contradictions:
        consensus_level = "CONTRADICTION_DETECTED"
        score = 0.45
    else:
        consensus_level = "NEUTRAL"
        score = 0.70

    return {
        "consensus_level": consensus_level,
        "consensus_score": score,
        "agreements_count": agreements,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions
    }


# --- 5. Physical & Computational Boundary Invariant Guards ---
def check_optical_latency_invariant(distance_km: float, reported_latency_ms: float, n_refractive: float = 1.47) -> Dict[str, Any]:
    """Checks speed-of-light propagation lower bound in optical fiber (c_fiber = c / n)."""
    if distance_km < 0 or reported_latency_ms < 0 or n_refractive <= 0:
        return {
            "invariant": "SPEED_OF_LIGHT_OPTICAL_FIBER",
            "distance_km": distance_km,
            "theoretical_min_rtt_ms": 0.0,
            "reported_latency_ms": reported_latency_ms,
            "is_physically_possible": False,
            "violation_details": "Distance, latency, and refractive index must be non-negative."
        }

    c_fiber = 299792.458 / n_refractive
    t_min_one_way_ms = (distance_km / c_fiber) * 1000.0 if distance_km > 0 else 0.0
    t_min_rtt_ms = t_min_one_way_ms * 2.0

    violates = reported_latency_ms < (t_min_rtt_ms - 1e-6)
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
    if node_count <= 0:
        return {
            "invariant": "UNIVERSAL_SCALABILITY_LAW",
            "node_count": node_count,
            "is_computationally_valid": False,
            "violation_details": "Node count must be greater than 0."
        }

    if node_count == 1:
        is_valid = (claimed_speedup <= 1.05)
        return {
            "invariant": "UNIVERSAL_SCALABILITY_LAW",
            "node_count": 1,
            "alpha_contention": alpha,
            "beta_coherency": beta,
            "theoretical_max_speedup": 1.0,
            "claimed_speedup": claimed_speedup,
            "is_computationally_valid": is_valid,
            "violation_details": "Single node speedup cannot exceed 1.0x" if not is_valid else "Compliant with USL."
        }

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
    if t_hot_k <= t_cold_k or t_hot_k <= 0 or t_cold_k < 0:
        return {
            "invariant": "CARNOT_THERMODYNAMIC_LIMIT",
            "t_hot_k": t_hot_k,
            "t_cold_k": t_cold_k,
            "is_physically_possible": False,
            "violation_details": "T_hot must exceed T_cold and 0 Kelvin."
        }

    max_eta = 1.0 - (t_cold_k / t_hot_k)
    violates = claimed_efficiency > (max_eta + 1e-6)
    return {
        "invariant": "CARNOT_THERMODYNAMIC_LIMIT",
        "t_hot_k": t_hot_k,
        "t_cold_k": t_cold_k,
        "max_theoretical_efficiency": round(max_eta, 4),
        "claimed_efficiency": claimed_efficiency,
        "is_physically_possible": not violates,
        "violation_details": f"Claimed efficiency {claimed_efficiency*100}% exceeds Carnot ceiling of {round(max_eta*100, 2)}%" if violates else "Compliant with 2nd law of thermodynamics."
    }


def check_landauer_limit_invariant(t_kelvin: float, claimed_energy_joules: float, bit_count: int = 1) -> Dict[str, Any]:
    """Landauer Limit: Minimum energy to erase bit_count bits: E_min = bit_count * k_B * T * ln(2)."""
    if t_kelvin <= 0 or bit_count <= 0:
        return {
            "invariant": "LANDAUER_LIMIT",
            "t_kelvin": t_kelvin,
            "bit_count": bit_count,
            "theoretical_min_energy_joules": 0.0,
            "claimed_energy_joules": claimed_energy_joules,
            "is_physically_possible": False,
            "violation_details": "Temperature and bit count must be strictly positive (> 0 Kelvin)."
        }

    k_b = 1.380649e-23  # J/K
    theoretical_min_energy = bit_count * k_b * t_kelvin * math.log(2)
    violates = claimed_energy_joules < theoretical_min_energy * 0.999

    return {
        "invariant": "LANDAUER_LIMIT",
        "t_kelvin": t_kelvin,
        "bit_count": bit_count,
        "theoretical_min_energy_joules": theoretical_min_energy,
        "claimed_energy_joules": claimed_energy_joules,
        "is_physically_possible": not violates,
        "violation_details": f"Claimed energy {claimed_energy_joules:.3e} J for erasing {bit_count} bit(s) at {t_kelvin}K is below Landauer minimum {theoretical_min_energy:.3e} J." if violates else "Compliant with Landauer thermodynamic limit."
    }


def check_cap_pacelc_invariant(claim: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """
    Evaluates CAP and PACELC theorem bounds on distributed system claims.
    Under partition (P), consistency (C) and availability (A) are mutually exclusive.
    Under normal operation (E), latency (L) and consistency (C) must trade off (PACELC).
    Quorum intersection rule: R + W > N and W > N/2 for strong/linearizable consistency.
    """
    is_valid = True
    violation_reasons = []
    tradeoff_model = "GENERAL_DISTRIBUTED"

    if isinstance(claim, dict):
        partition = claim.get("partition_active", claim.get("partition", False))
        consistency = str(claim.get("consistency", "")).lower()
        availability = str(claim.get("availability", "")).lower()

        is_linearizable = consistency in ("linearizable", "strong", "strict_serializable", "1.0", "true")
        is_fully_available = availability in ("100%", "high", "available", "always", "1.0", "true")

        if partition and is_linearizable and is_fully_available:
            is_valid = False
            violation_reasons.append("CAP theorem violation: Cannot guarantee 100% availability and linearizable consistency simultaneously during a network partition.")
            tradeoff_model = "CP_VIOLATION"

        # Quorum intersection check
        r = claim.get("r_quorum", claim.get("read_quorum"))
        w = claim.get("w_quorum", claim.get("write_quorum"))
        n = claim.get("n_replicas", claim.get("nodes", claim.get("replicas")))

        if r is not None and w is not None and n is not None:
            r, w, n = int(r), int(w), int(n)
            if n > 1:
                if is_linearizable or claim.get("strong_consistency", False):
                    if r + w <= n:
                        is_valid = False
                        violation_reasons.append(f"Quorum violation: R ({r}) + W ({w}) = {r+w} <= N ({n}). Read/write quorum overlap required for strong consistency.")
                        tradeoff_model = "QUORUM_DEFICIT"
                    elif w <= n / 2:
                        is_valid = False
                        violation_reasons.append(f"Quorum write conflict risk: W ({w}) <= N/2 ({n/2}). Majority write quorum required to prevent split-brain.")
                        tradeoff_model = "SPLIT_BRAIN_RISK"
                else:
                    tradeoff_model = "EVENTUAL_CONSISTENCY_QUORUM"

        # PACELC Zero-Latency check
        multi_region = claim.get("multi_region", claim.get("distributed", False))
        claimed_latency_ms = claim.get("replication_latency_ms", claim.get("latency_ms"))
        if multi_region and is_linearizable and claimed_latency_ms is not None:
            if float(claimed_latency_ms) <= 0.0:
                is_valid = False
                violation_reasons.append("PACELC violation: Zero-latency linearizable replication across distributed regions violates speed-of-light propagation bounds.")
                tradeoff_model = "PACELC_ZERO_LATENCY_VIOLATION"

    elif isinstance(claim, str):
        claim_lower = claim.lower()
        has_partition = any(k in claim_lower for k in ("partition", "network split", "disconnected nodes", "island"))
        has_strong_c = any(k in claim_lower for k in ("linearizable", "strong consistency", "strictly consistent", "acid"))
        has_100_a = any(k in claim_lower for k in ("100% availability", "100% available", "zero downtime", "always available", "full availability"))

        if has_partition and has_strong_c and has_100_a:
            is_valid = False
            violation_reasons.append("CAP theorem violation: Claims simultaneous strong consistency and 100% availability during network partition.")
            tradeoff_model = "CP_VIOLATION"

        has_zero_latency = any(k in claim_lower for k in ("0ms latency", "zero latency", "zero-latency", "instantaneous replication", "0 ms"))
        has_distributed = any(k in claim_lower for k in ("multi-region", "cross-datacenter", "transatlantic", "cross-region", "geo-distributed"))

        if has_zero_latency and has_distributed and has_strong_c:
            is_valid = False
            violation_reasons.append("PACELC violation: Zero latency replication with strong consistency across distributed network is physically impossible.")
            tradeoff_model = "PACELC_ZERO_LATENCY_VIOLATION"

        q_match = re.search(r'\br\s*=\s*(\d+).*?\bw\s*=\s*(\d+).*?\bn\s*=\s*(\d+)', claim_lower)
        if q_match:
            r, w, n = int(q_match.group(1)), int(q_match.group(2)), int(q_match.group(3))
            if has_strong_c and (r + w <= n):
                is_valid = False
                violation_reasons.append(f"Quorum violation: R={r} + W={w} <= N={n} cannot guarantee strong consistency.")
                tradeoff_model = "QUORUM_DEFICIT"

    return {
        "invariant": "CAP_PACELC_BOUND",
        "is_computationally_valid": is_valid,
        "is_physically_possible": is_valid,
        "tradeoff_model": tradeoff_model,
        "violation_details": " ".join(violation_reasons) if violation_reasons else "Compliant with CAP/PACELC theorem."
    }


def check_shannon_capacity_invariant(bandwidth_hz: float, snr_linear: float, claimed_bps: float) -> Dict[str, Any]:
    """Shannon Channel Capacity: C = B * log2(1 + SNR)."""
    if bandwidth_hz <= 0 or snr_linear < 0 or claimed_bps < 0:
        return {
            "invariant": "SHANNON_CHANNEL_CAPACITY",
            "bandwidth_hz": bandwidth_hz,
            "snr_linear": snr_linear,
            "theoretical_capacity_bps": 0.0,
            "claimed_bps": claimed_bps,
            "spectral_efficiency_bps_hz": 0.0,
            "is_physically_possible": False,
            "violation_details": "Bandwidth must be > 0 and SNR/claimed rate must be >= 0."
        }

    c_bps = bandwidth_hz * math.log2(1.0 + snr_linear) if snr_linear > 0 else 0.0
    violates = claimed_bps > c_bps * 1.01

    return {
        "invariant": "SHANNON_CHANNEL_CAPACITY",
        "bandwidth_hz": bandwidth_hz,
        "snr_linear": snr_linear,
        "theoretical_capacity_bps": round(c_bps, 2),
        "claimed_bps": claimed_bps,
        "spectral_efficiency_bps_hz": round(claimed_bps / bandwidth_hz, 4) if bandwidth_hz > 0 else 0.0,
        "is_physically_possible": not violates,
        "violation_details": f"Claimed throughput {claimed_bps} bps exceeds Shannon channel capacity {round(c_bps, 2)} bps for B={bandwidth_hz}Hz, SNR={snr_linear}." if violates else "Compliant with Shannon capacity."
    }


def evaluate_all_boundary_invariants(claims_or_text: Union[str, List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a collection of claims or structured invariant dictionaries against physical & computational laws.
    Returns:
        {
            "valid": bool,
            "violations": List[Dict[str, Any]],
            "multiplier": 1.0 (if valid) or 0.0 (if any invariant violated)
        }
    """
    violations = []

    if isinstance(claims_or_text, dict):
        inv_type = str(claims_or_text.get("type", claims_or_text.get("invariant", ""))).upper()
        if "OPTICAL" in inv_type or "LATENCY" in inv_type or ("distance_km" in claims_or_text and "reported_latency_ms" in claims_or_text):
            res = check_optical_latency_invariant(float(claims_or_text["distance_km"]), float(claims_or_text["reported_latency_ms"]))
            if not res["is_physically_possible"]:
                violations.append(res)
        elif "USL" in inv_type or "SCALABILITY" in inv_type or ("node_count" in claims_or_text and "claimed_speedup" in claims_or_text):
            res = check_usl_scalability_invariant(int(claims_or_text["node_count"]), float(claims_or_text.get("alpha", 0.0)), float(claims_or_text.get("beta", 0.0)), float(claims_or_text["claimed_speedup"]))
            if not res["is_computationally_valid"]:
                violations.append(res)
        elif "CARNOT" in inv_type or ("t_hot_k" in claims_or_text and "t_cold_k" in claims_or_text and "claimed_efficiency" in claims_or_text):
            res = check_carnot_efficiency_invariant(float(claims_or_text["t_hot_k"]), float(claims_or_text["t_cold_k"]), float(claims_or_text["claimed_efficiency"]))
            if not res["is_physically_possible"]:
                violations.append(res)
        elif "LANDAUER" in inv_type or ("t_kelvin" in claims_or_text and "claimed_energy_joules" in claims_or_text):
            res = check_landauer_limit_invariant(float(claims_or_text["t_kelvin"]), float(claims_or_text["claimed_energy_joules"]), int(claims_or_text.get("bit_count", 1)))
            if not res["is_physically_possible"]:
                violations.append(res)
        elif "SHANNON" in inv_type or ("bandwidth_hz" in claims_or_text and "claimed_bps" in claims_or_text):
            res = check_shannon_capacity_invariant(float(claims_or_text["bandwidth_hz"]), float(claims_or_text.get("snr_linear", 1.0)), float(claims_or_text["claimed_bps"]))
            if not res["is_physically_possible"]:
                violations.append(res)
        elif "CAP" in inv_type or "PACELC" in inv_type or "partition_active" in claims_or_text or "r_quorum" in claims_or_text or "multi_region" in claims_or_text:
            res = check_cap_pacelc_invariant(claims_or_text)
            if not res["is_computationally_valid"]:
                violations.append(res)
    elif isinstance(claims_or_text, list):
        for item in claims_or_text:
            sub = evaluate_all_boundary_invariants(item)
            violations.extend(sub["violations"])
    elif isinstance(claims_or_text, str):
        cap_res = check_cap_pacelc_invariant(claims_or_text)
        if not cap_res["is_computationally_valid"]:
            violations.append(cap_res)

    is_valid = len(violations) == 0
    return {
        "valid": is_valid,
        "violations": violations,
        "multiplier": 1.0 if is_valid else 0.0
    }


# Contract interface compatibility aliases
verify_optical_latency_invariant = check_optical_latency_invariant
verify_usl_invariant = check_usl_scalability_invariant
verify_cap_pacelc_invariant = check_cap_pacelc_invariant
verify_carnot_landauer_invariant = lambda claim: (
    check_carnot_efficiency_invariant(claim["t_hot_k"], claim["t_cold_k"], claim["claimed_efficiency"])
    if "t_hot_k" in claim
    else check_landauer_limit_invariant(claim["t_kelvin"], claim["claimed_energy_joules"], claim.get("bit_count", 1))
)
verify_shannon_capacity_invariant = check_shannon_capacity_invariant


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
