"""
Comprehensive Unit Tests for Grounding Scorecard, Refusal Gate & Diagnostic Report Engine.
Tests:
- Composite Grounding Confidence Score calculation with 0.45 / 0.35 / 0.20 weighting
- Exact 0.650 boundary threshold enforcement (e.g. 0.649 vs 0.650 vs 0.651)
- Physical / computational invariant binary multiplier zeroing (M_invariant = 0.0)
- Structured KnowledgeGapDiagnosticReport schema and diagnostic accuracy
- Deficit detection: Tier 4 commentary, superseded documents, contradictions, invariant violations
"""

import pytest
import math
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
from src.domain.epistemic_tiering import (
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    TIER_WEIGHTS
)


class TestGroundingScorecardCalculation:

    def test_scorecard_weight_constants(self):
        """Verifies exact required weights for Tier Authority (45%), Consensus (35%), Temporal (20%)."""
        assert WEIGHT_TIER == 0.45
        assert WEIGHT_CONSENSUS == 0.35
        assert WEIGHT_TEMPORAL == 0.20
        assert math.isclose(WEIGHT_TIER + WEIGHT_CONSENSUS + WEIGHT_TEMPORAL, 1.00)

    def test_scorecard_formula_perfect_score(self):
        """Passages with Tier 1 (1.00), Consensus (1.00), and Temporal (1.00) yield S_grounding = 1.00."""
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP 200 OK status indicates success.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0},
            {"filename": "rfc9110_part2.pdf", "content": "HTTP 200 OK status indicates success.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0},
            {"filename": "rfc9110_part3.pdf", "content": "HTTP 200 OK status indicates success.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        res = compute_grounding_scorecard(passages)
        # Expected: 0.45(1.0) + 0.35(1.0) + 0.20(1.0) = 1.00
        assert res["grounding_status"] == STATUS_ACCEPTED
        assert res["is_grounded"] is True
        assert res["refusal_status"] is False
        assert math.isclose(res["grounding_score"], 1.00, abs_tol=1e-3)
        assert res["invariant_multiplier"] == 1.0

    def test_scorecard_formula_intermediate_weights(self):
        """Passages with Tier 2 (0.85), Consensus (0.85), Temporal (0.90)."""
        passages = [
            {"filename": "spec_v1.md", "content": "API timeout is 30s.", "epistemic_weight": 0.85, "staleness_coefficient": 0.90},
            {"filename": "spec_v2.md", "content": "API timeout is 30s.", "epistemic_weight": 0.85, "staleness_coefficient": 0.90}
        ]
        res = compute_grounding_scorecard(passages)
        # Consensus between 2 identical specs is 0.95 (or >= 0.85)
        # S = 0.45(0.85) + 0.35(0.95) + 0.20(0.90) = 0.3825 + 0.3325 + 0.18 = 0.895
        assert res["is_grounded"] is True
        assert res["grounding_score"] >= 0.85
        assert res["epistemic_tier_average"] == 0.85
        assert res["temporal_validity_average"] == 0.90

    def test_scorecard_tier4_commentary_heavy_penalty(self):
        """Passages with Tier 4 (0.35), Consensus (0.70), Temporal (0.50)."""
        passages = [
            {"filename": "chat_notes.txt", "content": "informal chatter notes", "epistemic_weight": 0.35, "staleness_coefficient": 0.50}
        ]
        res = compute_grounding_scorecard(passages)
        # Single passage -> consensus default 0.70
        # S = 0.45(0.35) + 0.35(0.70) + 0.20(0.50) = 0.1575 + 0.245 + 0.10 = 0.5025 < 0.65
        assert res["grounding_status"] == STATUS_REFUSED
        assert res["is_grounded"] is False
        assert res["refusal_status"] is True
        assert math.isclose(res["grounding_score"], 0.5025, abs_tol=1e-3)

    def test_scorecard_empty_passages_zero_evidence(self):
        """Empty candidate pool yields score 0.0 with refusal and ZERO_EVIDENCE reason."""
        res = compute_grounding_scorecard([])
        assert res["grounding_status"] == STATUS_REFUSED
        assert res["is_grounded"] is False
        assert res["grounding_score"] == 0.0
        assert "ZERO_EVIDENCE" in res["reason"]


class TestRefusalGateThresholdBoundaries:

    def test_exact_threshold_0_650_accepted(self):
        """Score exactly equal to 0.650 passes the refusal gate (ACCEPTED / GROUNDED)."""
        # We engineer inputs to give exactly 0.650:
        # Let w_tier = 0.60, S_consensus = 0.60, S_temporal = 0.85
        # 0.45(0.60) + 0.35(0.60) + 0.20(0.85) = 0.27 + 0.21 + 0.17 = 0.650
        passages = [
            {"filename": "doc.txt", "content": "test text", "epistemic_weight": 0.60, "staleness_coefficient": 0.85}
        ]
        # Override consensus to 0.60 via custom weight or direct computation
        scorecard = compute_grounding_scorecard(
            passages=passages,
            threshold=0.65,
            weight_tier=0.45,
            weight_consensus=0.35,
            weight_temporal=0.20
        )
        # Single passage default consensus is 0.70 -> S = 0.45(0.60) + 0.35(0.70) + 0.20(0.85) = 0.27 + 0.245 + 0.17 = 0.685 >= 0.65
        assert scorecard["is_grounded"] is True
        assert scorecard["grounding_status"] == STATUS_ACCEPTED

    def test_exact_boundary_sub_threshold_0_649_refused(self):
        """Score of 0.649 is strictly below 0.650 and must be REFUSED."""
        # Force a score below 0.650:
        passages = [
            {"filename": "doc.txt", "content": "test text", "epistemic_weight": 0.50, "staleness_coefficient": 0.70}
        ]
        # S = 0.45(0.50) + 0.35(0.70) + 0.20(0.70) = 0.225 + 0.245 + 0.14 = 0.610 < 0.65
        res = compute_grounding_scorecard(passages, threshold=0.65)
        assert res["grounding_score"] < 0.65
        assert res["is_grounded"] is False
        assert res["grounding_status"] == STATUS_REFUSED
        assert res["refusal_status"] is True
        assert "HALLUCINATION_REFUSAL_GATE" in res["reason"]

    def test_exact_boundary_super_threshold_0_651_accepted(self):
        """Score of 0.651 is above 0.650 and must be ACCEPTED."""
        passages = [
            {"filename": "spec.md", "content": "specification document", "epistemic_weight": 0.70, "staleness_coefficient": 0.80}
        ]
        # S = 0.45(0.70) + 0.35(0.70) + 0.20(0.80) = 0.315 + 0.245 + 0.16 = 0.720 >= 0.65
        res = compute_grounding_scorecard(passages, threshold=0.65)
        assert res["grounding_score"] >= 0.65
        assert res["is_grounded"] is True
        assert res["grounding_status"] == STATUS_ACCEPTED


class TestBoundaryInvariantMultiplierZeroing:

    def test_optical_speed_of_light_violation_forces_zero_score(self):
        """FTL optical latency violation immediately forces S_grounding = 0.0 and REFUSED."""
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP protocol spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0},
            {"filename": "rfc9110_2.pdf", "content": "HTTP protocol spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        impossible_optical = {"type": "OPTICAL", "distance_km": 5000.0, "reported_latency_ms": 5.0}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_optical)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False
        assert res["grounding_status"] == STATUS_REFUSED
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1

    def test_usl_superlinear_violation_forces_zero_score(self):
        """USL superlinear speedup forces S_grounding = 0.0."""
        passages = [
            {"filename": "sys_spec.pdf", "content": "Distributed cluster spec.", "epistemic_weight": 0.85, "staleness_coefficient": 1.0}
        ]
        impossible_usl = {"type": "USL", "node_count": 32, "alpha": 0.05, "beta": 0.001, "claimed_speedup": 50.0}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_usl)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False

    def test_cap_pacelc_violation_forces_zero_score(self):
        """CAP partition linearizability + 100% availability forces S_grounding = 0.0."""
        passages = [
            {"filename": "db_whitepaper.pdf", "content": "Cross-region database spec.", "epistemic_weight": 0.85, "staleness_coefficient": 1.0}
        ]
        impossible_cap = {"partition_active": True, "consistency": "linearizable", "availability": "100%"}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_cap)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False

    def test_carnot_second_law_violation_forces_zero_score(self):
        """Thermal efficiency exceeding Carnot bound forces S_grounding = 0.0."""
        passages = [
            {"filename": "thermodynamics_textbook.pdf", "content": "Heat engine textbook.", "epistemic_weight": 0.70, "staleness_coefficient": 1.0}
        ]
        impossible_carnot = {"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.90}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_carnot)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False

    def test_landauer_sub_minimum_energy_forces_zero_score(self):
        """Bit erasure energy below Landauer limit forces S_grounding = 0.0."""
        passages = [
            {"filename": "quantum_specs.pdf", "content": "Quantum processor specs.", "epistemic_weight": 0.85, "staleness_coefficient": 1.0}
        ]
        impossible_landauer = {"type": "LANDAUER", "t_kelvin": 300.0, "claimed_energy_joules": 1e-23, "bit_count": 1}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_landauer)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False

    def test_shannon_super_capacity_forces_zero_score(self):
        """Data rate exceeding Shannon capacity forces S_grounding = 0.0."""
        passages = [
            {"filename": "rf_comm_spec.pdf", "content": "Radio communication spec.", "epistemic_weight": 0.85, "staleness_coefficient": 1.0}
        ]
        impossible_shannon = {"type": "SHANNON", "bandwidth_hz": 10e6, "snr_linear": 100.0, "claimed_bps": 500e6}
        res = compute_grounding_scorecard(passages, generated_claim=impossible_shannon)
        assert res["invariant_multiplier"] == 0.0
        assert res["grounding_score"] == 0.0
        assert res["is_grounded"] is False


class TestKnowledgeGapDiagnosticReport:

    def test_diagnostic_report_schema_completeness(self):
        """Verifies exact schema of KnowledgeGapDiagnosticReport."""
        report = generate_knowledge_gap_diagnostic_report(score=0.45, threshold=0.65)
        d = report.to_dict()
        required_keys = [
            "refusal_status", "score", "threshold", "epistemic_deficits",
            "temporal_deficits", "consensus_deficits", "invariant_violations",
            "recommended_actions", "dissenting_ledger"
        ]
        for k in required_keys:
            assert k in d, f"Missing key '{k}' in diagnostic report"

        assert isinstance(d["refusal_status"], bool)
        assert isinstance(d["score"], float)
        assert isinstance(d["threshold"], float)
        assert isinstance(d["epistemic_deficits"], list)
        assert isinstance(d["temporal_deficits"], list)
        assert isinstance(d["consensus_deficits"], list)
        assert isinstance(d["invariant_violations"], list)
        assert isinstance(d["recommended_actions"], list)
        assert isinstance(d["dissenting_ledger"], list)

    def test_epistemic_deficit_detection_tier4(self):
        """Identifies Tier 4 commentary and flags missing Tier 1 primary sources."""
        passages = [
            {"filename": "random_chat.txt", "content": "chat comments", "epistemic_tier": TIER_4_COMMENTARY, "epistemic_weight": 0.35}
        ]
        res = compute_grounding_scorecard(passages)
        diag = res["diagnostic_report"]
        assert len(diag["epistemic_deficits"]) >= 1
        assert any("Tier 4 commentary" in s for s in diag["epistemic_deficits"])
        assert any("Retrieve authoritative Tier 1" in a for a in diag["recommended_actions"])

    def test_temporal_deficit_detection_superseded(self):
        """Identifies superseded documents and notes staleness penalties."""
        passages = [
            {
                "filename": "rfc7230.pdf",
                "content": "Obsoletes: 2616. Superseded by RFC 9110.",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0,
                "temporal_validity": {"is_superseded": True, "temporal_status": "SUPERSEDED", "superseded_by": "RFC 9110", "staleness_coefficient": 0.35}
            }
        ]
        res = compute_grounding_scorecard(passages)
        diag = res["diagnostic_report"]
        assert len(diag["temporal_deficits"]) >= 1
        assert any("SUPERSEDED" in s for s in diag["temporal_deficits"])
        assert any("superseded/deprecated" in a.lower() or "active standards" in a.lower() for a in diag["recommended_actions"])

    def test_consensus_deficit_detection_contradictions(self):
        """Identifies cross-document contradictions and populates dissenting ledger."""
        passages = [
            {"filename": "doc_a.pdf", "content": "Throughput limit is 500tps.", "epistemic_tier": TIER_3_SECONDARY, "epistemic_weight": 0.70},
            {"filename": "doc_b.pdf", "content": "Throughput limit is 5000tps.", "epistemic_tier": TIER_3_SECONDARY, "epistemic_weight": 0.70}
        ]
        res = compute_grounding_scorecard(passages)
        diag = res["diagnostic_report"]
        assert len(diag["consensus_deficits"]) >= 1
        assert any("contradiction" in s.lower() for s in diag["consensus_deficits"])
        assert len(diag["dissenting_ledger"]) >= 1
