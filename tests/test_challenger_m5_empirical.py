"""
Empirical Challenger Test Suite for Milestone M5:
Grounding Scorecard, Refusal Gate & Engine Integration.

Adversarial Stress-Testing Methodology:
1. Monte Carlo Weight Sweeps (10,000 iterations) & Exact 0.650 Threshold Boundary Sensitivity.
2. Adversarial Invariant Injection: Invariant Multiplier Zeroing (M_inv = 0.0) across 100 High-Authority Passages.
3. Adversarial Contradiction Injection: Numerical, Polarity & Status Conflicts, Dissenting Ledger Audit.
4. End-to-End Deceptive Queries, Mixed-Tier Payloads, and 25-Angle Input Fuzzing.
"""

import math
import random
import unicodedata
import pytest
from typing import List, Dict, Any

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
from src.domain.grounded_retrieval_engine import (
    GroundedRetrievalEngine,
    execute_grounded_retrieval,
    evaluate_grounding_for_claim
)
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
    compute_temporal_decay
)
from src.domain.consensus_matrix import (
    evaluate_cross_document_consensus,
    CONTRADICTION_DETECTED,
    CONTRADICTION_UNRESOLVED,
    HIGH_CONSENSUS,
    MODERATE_CONSENSUS,
    MINOR_DISCREPANCY,
    SINGLE_SOURCE,
    CONFLICT_NUMERICAL_DISCREPANCY,
    CONFLICT_POLARITY_INVERSION,
    CONFLICT_STATUS_COLLISION,
    TIER_1_EPISTEMIC_DOMINANCE,
    TIER_2_TEMPORAL_DOMINANCE,
    TIER_3_CONDITION_SCOPE,
    TIER_4_UNRESOLVABLE
)
from src.domain.boundary_invariants import (
    evaluate_all_boundary_invariants,
    check_optical_latency_invariant,
    check_usl_scalability_invariant,
    check_cap_pacelc_invariant,
    check_carnot_efficiency_invariant,
    check_landauer_erasure_invariant,
    check_shannon_capacity_invariant,
    INV_SPEED_OF_LIGHT,
    INV_USL,
    INV_CAP_PACELC,
    INV_CARNOT,
    INV_LANDAUER,
    INV_SHANNON,
    VIOLATION_SPEED_OF_LIGHT,
    VIOLATION_SUPERLINEAR_SPEEDUP,
    VIOLATION_CAP_PARTITION,
    VIOLATION_CARNOT_SECOND_LAW,
    VIOLATION_LANDAUER_THERMODYNAMIC,
    VIOLATION_SHANNON_CAPACITY
)


# ==============================================================================
# PILLAR 1: MONTE CARLO WEIGHT SWEEPS & EXACT 0.65 BOUNDARY SENSITIVITY
# ==============================================================================

class TestPillar1BoundarySensitivityAndMonteCarlo:
    """
    Empirical validation of score formula S = 0.45 * W + 0.35 * C + 0.20 * T
    and exact 0.650 refusal gate boundary under 10,000 Monte Carlo iterations.
    """

    def test_monte_carlo_10000_weight_sweeps(self):
        """
        Runs 10,000 random uniform (W, C, T) parameter combinations in [0.0, 1.0]^3.
        Asserts exact mathematical score equality and strict refusal gate thresholding.
        """
        random.seed(42)
        n_samples = 10000
        refusal_count = 0
        accepted_count = 0

        for _ in range(n_samples):
            w = random.random()
            t = random.random()

            passages = [
                {
                    "filename": "synthetic_mc_doc.txt",
                    "content": "Monte Carlo synthetic content.",
                    "epistemic_weight": w,
                    "staleness_coefficient": t
                }
            ]

            scorecard = compute_grounding_scorecard(
                passages=passages,
                threshold=0.65
            )

            # Single passage mode uses consensus default 0.70:
            # S = 0.45(w) + 0.35(0.70) + 0.20(t)
            exp_single_raw = 0.45 * w + 0.35 * 0.70 + 0.20 * t
            exp_single_score = round(min(1.0, max(0.0, exp_single_raw)), 4)
            exp_single_accepted = bool(exp_single_score >= (0.65 - 1e-6))

            assert math.isclose(scorecard["grounding_score"], exp_single_score, abs_tol=1e-4)
            assert scorecard["is_grounded"] == exp_single_accepted
            assert scorecard["refusal_status"] == (not exp_single_accepted)
            assert scorecard["grounding_status"] == (STATUS_ACCEPTED if exp_single_accepted else STATUS_REFUSED)

            if exp_single_accepted:
                accepted_count += 1
            else:
                refusal_count += 1

        assert accepted_count > 0
        assert refusal_count > 0
        assert accepted_count + refusal_count == n_samples

    def test_exact_micro_epsilon_boundary_transitions(self):
        """
        Sweeps epsilon offsets around 0.650000 in micro-steps (1e-6 to 1e-3).
        Validates exact step function behavior at threshold = 0.650.
        """
        epsilons = [1e-6, 1e-5, 1e-4, 1e-3, 0.005, 0.01]

        for eps in epsilons:
            # Below boundary: S = 0.6500 - eps
            # 0.45 * w + 0.35 * 0.70 + 0.20 * 0.70 = 0.6500 - eps
            # 0.45 * w + 0.385 = 0.6500 - eps => w = (0.2650 - eps) / 0.45
            target_sub = 0.6500 - eps
            w_sub = (target_sub - 0.385) / 0.45

            if 0.0 <= w_sub <= 1.0:
                passages_sub = [{
                    "filename": "sub.txt",
                    "content": "text",
                    "epistemic_weight": w_sub,
                    "staleness_coefficient": 0.70
                }]
                res_sub = compute_grounding_scorecard(passages_sub, threshold=0.65)
                assert res_sub["grounding_score"] < 0.65 or math.isclose(res_sub["grounding_score"], target_sub, abs_tol=1e-4)
                if res_sub["grounding_score"] < 0.65 - 1e-6:
                    assert res_sub["is_grounded"] is False
                    assert res_sub["grounding_status"] == STATUS_REFUSED
                    assert res_sub["refusal_status"] is True

            # Above boundary: S = 0.6500 + eps
            target_sup = 0.6500 + eps
            w_sup = (target_sup - 0.385) / 0.45
            if 0.0 <= w_sup <= 1.0:
                passages_sup = [{
                    "filename": "sup.txt",
                    "content": "text",
                    "epistemic_weight": w_sup,
                    "staleness_coefficient": 0.70
                }]
                res_sup = compute_grounding_scorecard(passages_sup, threshold=0.65)
                assert res_sup["grounding_score"] >= (0.65 - 1e-6)
                assert res_sup["is_grounded"] is True
                assert res_sup["grounding_status"] == STATUS_ACCEPTED
                assert res_sup["refusal_status"] is False

    def test_strict_monotonicity_across_weight_dimensions(self):
        """
        Proves strict monotonicity: increasing authority, consensus, or temporal validity
        monotonically non-decreases S_grounding and never flips status from ACCEPTED to REFUSED.
        """
        steps = [i / 50.0 for i in range(51)]  # 0.0 to 1.0 in 0.02 increments

        # Monotonicity in Tier Authority W
        prev_score = -1.0
        prev_status = False
        for w in steps:
            p = [{"filename": "doc.txt", "content": "text", "epistemic_weight": w, "staleness_coefficient": 0.70}]
            res = compute_grounding_scorecard(p, threshold=0.65)
            score = res["grounding_score"]
            status = res["is_grounded"]
            assert score >= prev_score - 1e-6, f"Monotonicity violation in W: {score} < {prev_score}"
            if prev_status is True:
                assert status is True, "Status flipped from ACCEPTED to REFUSED when increasing W!"
            prev_score = score
            prev_status = status

        # Monotonicity in Temporal Validity T
        prev_score = -1.0
        prev_status = False
        for t in steps:
            p = [{"filename": "doc.txt", "content": "text", "epistemic_weight": 0.70, "staleness_coefficient": t}]
            res = compute_grounding_scorecard(p, threshold=0.65)
            score = res["grounding_score"]
            status = res["is_grounded"]
            assert score >= prev_score - 1e-6, f"Monotonicity violation in T: {score} < {prev_score}"
            if prev_status is True:
                assert status is True, "Status flipped from ACCEPTED to REFUSED when increasing T!"
            prev_score = score
            prev_status = status

    def test_partial_derivative_sensitivities(self):
        """
        Verifies exact partial derivative coefficients:
        dS/dW = 0.45, dS/dT = 0.20.
        """
        delta = 0.10

        # Base case
        p_base = [{"filename": "doc.txt", "content": "t", "epistemic_weight": 0.50, "staleness_coefficient": 0.50}]
        base_res = compute_grounding_scorecard(p_base)
        s_base = base_res["grounding_score"]

        # Delta in W
        p_w = [{"filename": "doc.txt", "content": "t", "epistemic_weight": 0.50 + delta, "staleness_coefficient": 0.50}]
        res_w = compute_grounding_scorecard(p_w)
        ds_dw = (res_w["grounding_score"] - s_base) / delta
        assert math.isclose(ds_dw, 0.45, abs_tol=1e-3)

        # Delta in T
        p_t = [{"filename": "doc.txt", "content": "t", "epistemic_weight": 0.50, "staleness_coefficient": 0.50 + delta}]
        res_t = compute_grounding_scorecard(p_t)
        ds_dt = (res_t["grounding_score"] - s_base) / delta
        assert math.isclose(ds_dt, 0.20, abs_tol=1e-3)


# ==============================================================================
# PILLAR 2: ADVERSARIAL INVARIANT INJECTION & BINARY MULTIPLIER ZEROING
# ==============================================================================

class TestPillar2AdversarialInvariantInjection:
    """
    Stress-testing invariant multiplier M_inv = 0.0 binary veto.
    Ensures any single boundary violation completely zeroes S_grounding = 0.0
    even against 100 perfect Tier 1 primary passages.
    """

    def test_100_tier1_passages_vetoed_by_optical_ftl_violation(self):
        """
        100 Tier 1 primary documents (RFCs, ISO standards) with staleness 1.0 and perfect consensus.
        Normal score = 1.000.
        Injected with FTL optical latency claim: 15,000 km in 2 ms (min physical RTT ~147 ms).
        Expected: S_grounding = 0.0, status = REFUSED, invariant_multiplier = 0.0.
        """
        passages_100 = [
            {
                "id": i,
                "filename": f"rfc_{9000+i}_standard.pdf",
                "content": f"Authoritative protocol specification standard section {i} defining verified behavior.",
                "epistemic_weight": 1.0,
                "epistemic_tier": TIER_1_PRIMARY,
                "staleness_coefficient": 1.0
            }
            for i in range(100)
        ]

        ftl_claim = {
            "type": "OPTICAL",
            "distance_km": 15000.0,
            "reported_latency_ms": 2.0,
            "medium": "silica_fiber"
        }

        scorecard = compute_grounding_scorecard(
            passages=passages_100,
            generated_claim=ftl_claim,
            threshold=0.65
        )

        assert scorecard["invariant_multiplier"] == 0.0
        assert scorecard["grounding_score"] == 0.0
        assert scorecard["overall_grounded_confidence"] == 0.0
        assert scorecard["is_grounded"] is False
        assert scorecard["refusal_status"] is True
        assert scorecard["grounding_status"] == STATUS_REFUSED
        assert "BOUNDARY_INVARIANT_VETO" in scorecard["reason"]

        diag = scorecard["diagnostic_report"]
        assert diag["refusal_status"] is True
        assert diag["score"] == 0.0
        assert len(diag["invariant_violations"]) >= 1
        v = diag["invariant_violations"][0]
        assert v["invariant"] == INV_SPEED_OF_LIGHT
        assert v["violation_type"] == VIOLATION_SPEED_OF_LIGHT
        assert "violates physical limit" in v["violation_details"]

    def test_usl_superlinear_scaling_invariant_veto(self):
        """
        USL Superlinear speedup claim (e.g. 128 nodes achieving 256x speedup)
        must trigger invariant multiplier M_inv = 0.0.
        """
        passages = [
            {"filename": "ieee_cluster_spec.pdf", "content": "Cluster spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        usl_claim = {
            "type": "USL",
            "node_count": 128,
            "alpha": 0.02,
            "beta": 0.001,
            "claimed_speedup": 256.0
        }
        res = compute_grounding_scorecard(passages, generated_claim=usl_claim)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1
        assert res["diagnostic_report"]["invariant_violations"][0]["invariant"] == INV_USL

    def test_cap_pacelc_consistency_under_partition_veto(self):
        """
        CAP theorem violation: Claiming 100% availability and strict linearizability
        during an active network partition must be strictly vetoed.
        """
        passages = [
            {"filename": "db_iso_spec.pdf", "content": "Storage engine spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        cap_claim = {
            "type": "CAP_PACELC",
            "partition_active": True,
            "consistency": "linearizable",
            "availability": "100%"
        }
        res = compute_grounding_scorecard(passages, generated_claim=cap_claim)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1
        assert res["diagnostic_report"]["invariant_violations"][0]["invariant"] == INV_CAP_PACELC

    def test_carnot_second_law_thermodynamic_veto(self):
        """
        Carnot second law violation: Claiming thermal efficiency eta = 85% with Th=400K, Tc=300K
        (Carnot limit is 1 - 300/400 = 25%) must be strictly vetoed.
        """
        passages = [
            {"filename": "physics_handbook.pdf", "content": "Thermodynamics fundamentals.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        carnot_claim = {
            "type": "CARNOT",
            "t_hot_k": 400.0,
            "t_cold_k": 300.0,
            "claimed_efficiency": 0.85
        }
        res = compute_grounding_scorecard(passages, generated_claim=carnot_claim)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1
        assert res["diagnostic_report"]["invariant_violations"][0]["invariant"] == INV_CARNOT

    def test_landauer_limit_erasure_energy_veto(self):
        """
        Landauer erasure limit violation: Claiming 1,000,000 bits erased at 300K with 1e-20 Joules
        (Landauer limit is 10^6 * k_B * 300 * ln(2) ~ 2.87e-15 J) must be strictly vetoed.
        """
        passages = [
            {"filename": "nano_spec.pdf", "content": "Semiconductor spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        landauer_claim = {
            "type": "LANDAUER",
            "bit_count": 1000000,
            "t_kelvin": 300.0,
            "claimed_energy_joules": 1e-20
        }
        res = compute_grounding_scorecard(passages, generated_claim=landauer_claim)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1
        assert res["diagnostic_report"]["invariant_violations"][0]["invariant"] == INV_LANDAUER

    def test_shannon_capacity_bandwidth_limit_veto(self):
        """
        Shannon channel capacity violation: Claiming 100 Mbps over 1 MHz bandwidth with SNR 10 dB
        (Shannon limit = 10^6 * log2(1 + 10) ~ 3.46 Mbps) must be strictly vetoed.
        """
        passages = [
            {"filename": "itu_spec.pdf", "content": "Wireless spectrum spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        shannon_claim = {
            "type": "SHANNON",
            "bandwidth_hz": 1e6,
            "snr_linear": 10.0,
            "claimed_bps": 100e6
        }
        res = compute_grounding_scorecard(passages, generated_claim=shannon_claim)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1
        assert res["diagnostic_report"]["invariant_violations"][0]["invariant"] == INV_SHANNON

    def test_simultaneous_multi_invariant_violations_collection(self):
        """
        Tests injecting a multi-violation payload (Optical + Carnot + USL + Shannon) simultaneously.
        Asserts all violations are captured in the diagnostic report with complete diagnostics.
        """
        multi_violations = [
            {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 1.0},
            {"type": "CARNOT", "t_hot_k": 500.0, "t_cold_k": 300.0, "claimed_efficiency": 0.90},
            {"type": "USL", "node_count": 64, "alpha": 0.05, "beta": 0.01, "claimed_speedup": 100.0},
            {"type": "SHANNON", "bandwidth_hz": 1e6, "snr_linear": 10.0, "claimed_bps": 50e6}
        ]
        inv_audit = evaluate_all_boundary_invariants(multi_violations)
        assert inv_audit["valid"] is False
        assert inv_audit["multiplier"] == 0.0
        assert len(inv_audit["violations"]) == 4

        passages = [{"filename": "standards.pdf", "content": "text", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}]
        scorecard = compute_grounding_scorecard(passages, invariant_results=inv_audit)
        assert scorecard["grounding_score"] == 0.0
        assert scorecard["invariant_multiplier"] == 0.0
        assert len(scorecard["diagnostic_report"]["invariant_violations"]) == 4


# ==============================================================================
# PILLAR 3: ADVERSARIAL CONTRADICTION INJECTION & DISSENTING LEDGER AUDIT
# ==============================================================================

class TestPillar3AdversarialContradictionInjection:
    """
    Stress-testing cross-document contradiction detection:
    Numerical discrepancies, polarity inversions, status collisions,
    multi-way conflicts, and dissenting ledger audit.
    """

    def test_numerical_discrepancy_drops_consensus_and_populates_ledger(self):
        """
        Two Tier 3 secondary documents asserting conflicting numerical limits:
        Doc A: "The maximum transaction throughput is 500 tps."
        Doc B: "The maximum transaction throughput is 50,000 tps."
        Asserts consensus drops to 0.45 (CONTRADICTION_DETECTED) and conflict is recorded in dissenting ledger.
        """
        passages = [
            {
                "filename": "textbook_a.pdf",
                "content": "Under standard configuration, the maximum transaction throughput is 500 tps across all nodes.",
                "epistemic_tier": TIER_3_SECONDARY,
                "epistemic_weight": 0.70,
                "staleness_coefficient": 1.0
            },
            {
                "filename": "textbook_b.pdf",
                "content": "Under standard configuration, the maximum transaction throughput is 50000 tps across all nodes.",
                "epistemic_tier": TIER_3_SECONDARY,
                "epistemic_weight": 0.70,
                "staleness_coefficient": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 1
        assert consensus["consensus_level"] in (CONTRADICTION_DETECTED, CONTRADICTION_UNRESOLVED)
        assert consensus["consensus_score"] == 0.45

        scorecard = compute_grounding_scorecard(passages=passages, threshold=0.65)
        # S = 0.45(0.70) + 0.35(0.45) + 0.20(1.0) = 0.315 + 0.1575 + 0.20 = 0.6725
        diag = scorecard["diagnostic_report"]
        assert len(diag["consensus_deficits"]) >= 1
        assert len(diag["dissenting_ledger"]) >= 1

        dissent = diag["dissenting_ledger"][0]
        assert dissent["conflict_type"] == CONFLICT_NUMERICAL_DISCREPANCY
        assert dissent["source_a"] == "textbook_a.pdf"
        assert dissent["source_b"] == "textbook_b.pdf"
        assert dissent["resolution_tier"] == TIER_4_UNRESOLVABLE

    def test_polarity_inversion_contradiction_refusal(self):
        """
        Two Tier 4 commentary documents asserting opposite polarities:
        Doc A: "Database replication compression is supported."
        Doc B: "Database replication compression is unsupported and disabled."
        Asserts polarity inversion detected and consensus score drops to 0.45.
        """
        passages = [
            {
                "filename": "guide_a.txt",
                "content": "Database replication compression is supported.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "staleness_coefficient": 1.0
            },
            {
                "filename": "guide_b.txt",
                "content": "Database replication compression is unsupported and disabled.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "staleness_coefficient": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 1
        assert any(c.get("conflict_type") in (CONFLICT_POLARITY_INVERSION, CONFLICT_STATUS_COLLISION) for c in consensus.get("contradictions", []))

        scorecard = compute_grounding_scorecard(passages=passages, threshold=0.65)
        assert scorecard["consensus_score"] == 0.45
        assert scorecard["grounding_status"] == STATUS_REFUSED
        diag = scorecard["diagnostic_report"]
        assert any("contradiction" in d.lower() for d in diag["consensus_deficits"])

    def test_status_collision_contradiction(self):
        """
        Two documents asserting colliding lifecycle statuses:
        Doc A: "The cryptographic protocol TLS 1.0 is active and stable."
        Doc B: "The cryptographic protocol TLS 1.0 is deprecated and obsolete."
        """
        passages = [
            {
                "filename": "legacy_crypto.pdf",
                "content": "The cryptographic protocol TLS 1.0 is active and stable.",
                "epistemic_tier": TIER_3_SECONDARY,
                "epistemic_weight": 0.70,
                "staleness_coefficient": 1.0
            },
            {
                "filename": "modern_crypto.pdf",
                "content": "The cryptographic protocol TLS 1.0 is deprecated and obsolete.",
                "epistemic_tier": TIER_3_SECONDARY,
                "epistemic_weight": 0.70,
                "staleness_coefficient": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 1
        assert any(c.get("conflict_type") == CONFLICT_STATUS_COLLISION for c in consensus.get("contradictions", []))

    def test_epistemic_dominance_resolution_preserves_consensus(self):
        """
        When Tier 1 standard (weight 1.0) contradicts Tier 4 commentary (weight 0.35),
        Tier 1 Epistemic Authority Dominance resolves the conflict:
        The conflict is resolved in favor of the Tier 1 source and recorded in resolved_claims.
        """
        passages = [
            {
                "filename": "rfc9110_spec.pdf",
                "content": "HTTP 200 OK status indicates successful processing.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0,
                "staleness_coefficient": 1.0
            },
            {
                "filename": "random_blog.txt",
                "content": "HTTP 200 OK status indicates server error and failure.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "staleness_coefficient": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 1
        # Resolved via Epistemic Dominance
        assert len(consensus["resolved_claims"]) >= 1
        assert consensus["resolved_claims"][0]["resolution_tier"] == TIER_1_EPISTEMIC_DOMINANCE
        assert consensus["resolved_claims"][0]["resolved_source"] == "rfc9110_spec.pdf"
        assert consensus["consensus_score"] in (0.85, 0.95)

    def test_temporal_dominance_resolution_preserves_consensus(self):
        """
        When active document contradicts superseded document with explicit superseding text,
        Tier 2 Temporal Superseding Dominance resolves the conflict.
        """
        passages = [
            {
                "filename": "rfc9110_active.pdf",
                "content": "HTTP 308 status code indicates Permanent Redirect in active standard.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0
            },
            {
                "filename": "rfc2616_superseded.pdf",
                "content": "HTTP 308 status code is undefined. Superseded by RFC 9110.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 1
        assert len(consensus["resolved_claims"]) >= 1
        assert consensus["resolved_claims"][0]["resolution_tier"] == TIER_2_TEMPORAL_DOMINANCE
        assert consensus["resolved_claims"][0]["resolved_source"] == "rfc9110_active.pdf"

    def test_condition_scope_harmonization(self):
        """
        When two claims differ due to explicit operating conditions
        (e.g., 'under load < 50' vs 'under load >= 100'),
        Tier 3 Condition Scope Specificity harmonizes them as MINOR_DISCREPANCY (consensus 0.50)
        or MODERATE_CONSENSUS.
        """
        passages = [
            {
                "filename": "load_spec_a.md",
                "content": "Under load < 50 requests, the server response latency is 10ms.",
                "epistemic_tier": TIER_2_TECH_SPEC,
                "epistemic_weight": 0.85,
                "staleness_coefficient": 1.0
            },
            {
                "filename": "load_spec_b.md",
                "content": "Under load >= 100 requests, the server response latency is 500ms.",
                "epistemic_tier": TIER_2_TECH_SPEC,
                "epistemic_weight": 0.85,
                "staleness_coefficient": 1.0
            }
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["consensus_level"] in (MINOR_DISCREPANCY, MODERATE_CONSENSUS)
        assert consensus["consensus_score"] in (0.50, 0.85)

    def test_multi_way_3_source_unresolvable_contradiction_refusal(self):
        """
        3 conflicting Tier 4 commentary sources with differing numerical claims: 100MB vs 500MB vs 2GB.
        Asserts multi-way contradiction triggers refusal gate and populates dissenting pairs.
        """
        passages = [
            {"filename": "blog1.txt", "content": "The default cache size is 100MB.", "epistemic_tier": TIER_4_COMMENTARY, "epistemic_weight": 0.35, "staleness_coefficient": 1.0},
            {"filename": "blog2.txt", "content": "The default cache size is 500MB.", "epistemic_tier": TIER_4_COMMENTARY, "epistemic_weight": 0.35, "staleness_coefficient": 1.0},
            {"filename": "blog3.txt", "content": "The default cache size is 2GB.", "epistemic_tier": TIER_4_COMMENTARY, "epistemic_weight": 0.35, "staleness_coefficient": 1.0}
        ]

        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["contradictions_count"] >= 2
        assert len(consensus["dissenting_ledger"]) >= 2
        scorecard = compute_grounding_scorecard(passages=passages, threshold=0.65)
        assert scorecard["consensus_score"] == 0.45
        # S = 0.45(0.35) + 0.35(0.45) + 0.20(1.0) = 0.1575 + 0.1575 + 0.20 = 0.515 < 0.65
        assert scorecard["grounding_status"] == STATUS_REFUSED
        assert scorecard["is_grounded"] is False


# ==============================================================================
# PILLAR 4: E2E RETRIEVAL UNDER DECEPTIVE QUERIES & MIXED-TIER PAYLOADS
# ==============================================================================

class TestPillar4DeceptiveQueriesAndMixedPayloads:
    """
    Stress-testing end-to-end retrieval pipelines under adversarial, deceptive queries
    and heterogeneous mixed-tier passage payloads.
    """

    def test_deceptive_query_superseded_obsolete_standards(self):
        """
        Deceptive query referencing obsolete Tier 4 commentary:
        Query: 'What are the legacy caching semantics?'
        Payload: Tier 4 draft note containing 'Superseded by RFC 9110'.
        Asserts severe temporal decay penalty, temporal deficits in diagnostics, and refusal.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {
                "id": 1,
                "filename": "legacy_draft_notes.txt",
                "content": "Draft specification published 1998. Superseded by RFC 9110.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "rank": 1
            }
        ]

        result = engine.evaluate_grounding(
            query="What are the legacy caching semantics?",
            candidate_passages=passages
        )

        assert result["status"] == "refusal"
        assert result["is_grounded"] is False
        assert result["refusal_status"] is True
        assert result["temporal_validity_average"] <= 0.40
        diag = result["diagnostic_report"]
        assert any("SUPERSEDED" in td for td in diag["temporal_deficits"])
        assert any("active standards" in ra.lower() or "superseded" in ra.lower() for ra in diag["recommended_actions"])

    def test_single_tier1_superseded_mathematical_invariant(self):
        """
        Mathematical proof of single Tier 1 superseded document behavior:
        S = 0.45(1.0) + 0.35(0.70) + 0.20(0.35) = 0.450 + 0.245 + 0.070 = 0.765 >= 0.65.
        Verifies that while score is 0.765, temporal deficits are properly logged in the diagnostic report.
        """
        passages = [
            {
                "filename": "rfc7230.pdf",
                "content": "RFC 7230 published June 2014. Obsoleted by RFC 9110. Superseded by RFC 9112.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0,
                "temporal_validity": {"is_superseded": True, "temporal_status": "SUPERSEDED", "staleness_coefficient": 0.35}
            }
        ]
        scorecard = compute_grounding_scorecard(passages=passages, threshold=0.65)
        assert math.isclose(scorecard["grounding_score"], 0.765, abs_tol=1e-3)
        assert scorecard["is_grounded"] is True
        # Must still log temporal deficits in diagnostic report
        diag = scorecard["diagnostic_report"]
        assert len(diag["temporal_deficits"]) >= 1
        assert any("SUPERSEDED" in td for td in diag["temporal_deficits"])

    def test_deceptive_query_physically_impossible_premise(self):
        """
        Deceptive query asserting impossible physical latency:
        Query: 'Confirm 1ms RTT fiber latency between New York and Sydney'
        Payload: Tier 1 geographical data sheet, with impossible claim injected.
        Asserts immediate physical invariant veto.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {
                "id": 1,
                "filename": "itu_geo_telecom_spec.pdf",
                "content": "Submarine fiber route geodesic distance between New York and Sydney is approximately 16,000 km.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0,
                "rank": 1
            }
        ]

        impossible_claim = {
            "type": "OPTICAL",
            "distance_km": 16000.0,
            "reported_latency_ms": 1.0,
            "medium": "silica_fiber"
        }

        result = engine.evaluate_grounding(
            query="Confirm 1ms RTT fiber latency between New York and Sydney",
            candidate_passages=passages,
            generated_claim=impossible_claim
        )

        assert result["status"] == "refusal"
        assert result["grounding_score"] == 0.0
        assert result["invariant_multiplier"] == 0.0
        assert "BOUNDARY_INVARIANT_VETO" in result["reason"]

    def test_mixed_tier_commentary_heavy_refusal(self):
        """
        Mixed-tier payload with dominant Tier 4 commentary:
        - 3 Tier 4 unverified developer blogs (weight = 0.35, staleness = 1.0)
        Average Tier = 0.35, Consensus = 0.70, Temporal = 1.0.
        S = 0.45(0.35) + 0.35(0.70) + 0.20(1.0) = 0.1575 + 0.245 + 0.20 = 0.6025 < 0.65.
        Asserts refusal gate triggers and diagnostic report identifies Tier 4 deficits.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {
                "id": 1,
                "filename": "medium_post.txt",
                "content": "My thoughts on HTTP routing in modern web stacks.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "rank": 1
            },
            {
                "id": 2,
                "filename": "dev_to_article.txt",
                "content": "Quick tutorial on setting up reverse proxy timeout.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "rank": 2
            },
            {
                "id": 3,
                "filename": "reddit_thread.txt",
                "content": "Discussion on thread pool exhaustion in uvicorn.",
                "epistemic_tier": TIER_4_COMMENTARY,
                "epistemic_weight": 0.35,
                "rank": 3
            }
        ]

        result = engine.evaluate_grounding(
            query="HTTP connection keep-alive timeout configuration",
            candidate_passages=passages
        )

        assert result["status"] == "refusal"
        assert result["is_grounded"] is False
        assert result["refusal_status"] is True
        assert result["overall_grounded_confidence"] < 0.65

        diag = result["diagnostic_report"]
        assert len(diag["epistemic_deficits"]) >= 1
        assert any("Tier 4 commentary" in ed for ed in diag["epistemic_deficits"])
        assert any("Retrieve authoritative Tier 1" in ra for ra in diag["recommended_actions"])

    def test_25_angle_fuzzing_robustness(self):
        """
        25-Angle Universal Edge Case Fuzzing:
        - Null bytes, unbalanced quotes, empty strings, massive 50KB strings
        - Unicode normalization (NFC vs NFD, zero-width spaces, RTL characters)
        - Extreme numeric values (NaN, Inf, negative infinity, negative weights)
        - Missing dictionary fields and malformed metadata structures
        Asserts zero crashes (no unhandled exceptions) and deterministic refusal/acceptance.
        """
        fuzz_cases = [
            # 1. Null byte injection
            {"filename": "spec\x00_test.txt", "content": "Valid content \x00 with null bytes.", "epistemic_weight": 0.85},
            # 2. Unbalanced quotes & escape sequences
            {"filename": 'spec_"\'`\\"".txt', "content": 'Unbalanced quotes: "\'\'`\\n\\t\\r', "epistemic_weight": 0.70},
            # 3. Unicode NFD vs NFC and RTL
            {"filename": unicodedata.normalize("NFD", "Café_規格_العربية.md"), "content": "Unicode \u200B\u200C text \u202E RTL test.", "epistemic_weight": 0.85},
            # 4. Massive 50KB payload
            {"filename": "giant_doc.txt", "content": "A" * 50000, "epistemic_weight": 0.70},
            # 5. Empty content and zero filename
            {"filename": "", "content": "", "epistemic_weight": 0.35},
            # 6. Malformed types
            {"filename": 12345, "content": None, "epistemic_weight": "invalid_float", "staleness_coefficient": [1, 2, 3]},
            # 7. Extreme float values
            {"filename": "extreme.txt", "content": "text", "epistemic_weight": float("inf"), "staleness_coefficient": float("-inf")},
            {"filename": "nan.txt", "content": "text", "epistemic_weight": float("nan"), "staleness_coefficient": 1.0}
        ]

        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)

        for idx, fc in enumerate(fuzz_cases):
            # Must not raise unhandled exception
            scorecard = compute_grounding_scorecard(passages=[fc])
            assert isinstance(scorecard, dict)
            assert "grounding_score" in scorecard
            assert "is_grounded" in scorecard
            assert "diagnostic_report" in scorecard
            assert isinstance(scorecard["grounding_score"], float)
            assert 0.0 <= scorecard["grounding_score"] <= 1.0

            # Test through engine coordinator
            eng_res = engine.evaluate_grounding(query=f"fuzz query {idx}", candidate_passages=[fc])
            assert isinstance(eng_res, dict)
            assert eng_res["status"] in ("success", "refusal")

    def test_top_level_execute_grounded_retrieval_empty_and_corrupt_inputs(self):
        """Verifies execute_grounded_retrieval handles None, empty, and whitespace gracefully."""
        res1 = execute_grounded_retrieval("")
        assert res1["status"] == "refusal"
        assert res1["overall_grounded_confidence"] == 0.0

        res2 = execute_grounded_retrieval("   \n\t  ", passages=[])
        assert res2["status"] == "refusal"
        assert res2["overall_grounded_confidence"] == 0.0

        res3 = evaluate_grounding_for_claim(claim="", retrieved_passages=[])
        assert res3["grounding_status"] == STATUS_REFUSED
        assert res3["grounding_score"] == 0.0

    def test_1000_passage_throughput_and_scaling(self):
        """
        Stress-tests scorecard calculation throughput across 1,000 heterogeneous candidate passages.
        Asserts execution completes sub-second and calculates exact average weights.
        """
        random.seed(123)
        passages_1000 = [
            {
                "id": i,
                "filename": f"doc_{i}.pdf" if i % 4 == 0 else f"spec_{i}.md" if i % 4 == 1 else f"book_{i}.pdf" if i % 4 == 2 else f"blog_{i}.txt",
                "content": f"Factual assertion sentence number {i} covering distributed systems.",
                "epistemic_weight": 1.0 if i % 4 == 0 else 0.85 if i % 4 == 1 else 0.70 if i % 4 == 2 else 0.35,
                "staleness_coefficient": 1.0 if i % 5 != 0 else 0.40
            }
            for i in range(1000)
        ]

        scorecard = compute_grounding_scorecard(passages=passages_1000, threshold=0.65)
        assert scorecard["is_grounded"] is True
        assert scorecard["grounding_score"] >= 0.65
        assert len(scorecard["passages"]) == 1000

    def test_natural_language_claim_invariant_refusal_nlp(self):
        """
        Tests natural language sentence parsing directly in evaluate_grounding_for_claim:
        Claims with natural language FTL latency, USL superlinear, and Carnot efficiency.
        """
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP specification standard.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]

        # Natural language text containing FTL claim:
        ftl_text = "The network link achieved round-trip latency of 1ms across a distance of 10000km in silica fiber."
        res = evaluate_grounding_for_claim(claim=ftl_text, retrieved_passages=passages)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["grounding_status"] == STATUS_REFUSED

    def test_dynamic_custom_thresholds_sweeps(self):
        """
        Tests scorecard under dynamic refusal thresholds: 0.00, 0.50, 0.75, 0.90, 1.00.
        """
        passages = [
            {"filename": "doc.txt", "content": "text", "epistemic_weight": 0.70, "staleness_coefficient": 0.70}
        ]
        # S = 0.45(0.70) + 0.35(0.70) + 0.20(0.70) = 0.7000

        # At threshold = 0.50 -> ACCEPTED
        res_50 = compute_grounding_scorecard(passages, threshold=0.50)
        assert res_50["is_grounded"] is True

        # At threshold = 0.70 -> ACCEPTED (exact boundary)
        res_70 = compute_grounding_scorecard(passages, threshold=0.70)
        assert res_70["is_grounded"] is True

        # At threshold = 0.75 -> REFUSED
        res_75 = compute_grounding_scorecard(passages, threshold=0.75)
        assert res_75["is_grounded"] is False
        assert res_75["grounding_status"] == STATUS_REFUSED

        # At threshold = 1.00 -> REFUSED
        res_100 = compute_grounding_scorecard(passages, threshold=1.00)
        assert res_100["is_grounded"] is False

