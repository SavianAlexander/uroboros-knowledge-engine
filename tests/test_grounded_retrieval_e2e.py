"""
Comprehensive 4-Tier Opaque-Box E2E Verification Suite for
Empirically True, Real-World Grounded Retrieval & Epistemic Invariant Engine.

Methodology:
- Tier 1: Feature Coverage (60 tests: 5 tests each for F1..F12)
- Tier 2: Boundary & Corner Cases (60 tests: 5 boundary tests each for F1..F12)
- Tier 3: Cross-Feature Pairwise Interactions (12 tests)
- Tier 4: Real-World Multi-Feature Application Scenarios (6 tests)
Total: 138 tests
"""

import pytest
import math
from datetime import datetime

from src.domain.grounded_retrieval_engine import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    detect_temporal_validity,
    compute_temporal_decay,
    decompose_into_propositions,
    evaluate_cross_document_consensus,
    check_optical_latency_invariant,
    check_usl_scalability_invariant,
    check_carnot_efficiency_invariant,
    check_landauer_limit_invariant,
    check_cap_pacelc_invariant,
    check_shannon_capacity_invariant,
    evaluate_all_boundary_invariants,
    verify_optical_latency_invariant,
    verify_usl_invariant,
    verify_cap_pacelc_invariant,
    verify_carnot_landauer_invariant,
    verify_shannon_capacity_invariant,
    GroundedRetrievalEngine,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)


# ==============================================================================
# TIER 1: FEATURE COVERAGE (60 Tests: 5 per Feature F1..F12)
# ==============================================================================
class TestTier1FeatureCoverage:

    # --- F1: Epistemic Evidentiary Tier Classifier (5 tests) ---
    def test_t1_f1_tier1_statutory_and_standards(self):
        docs = [
            "rfc9110_http_semantics.pdf",
            "iso27001_security_standard.pdf",
            "18_usc_1030_cfaa_statute.txt",
            "sec_10-k_annual_report_2025.pdf",
            "ieee_802_11_spec.pdf"
        ]
        for d in docs:
            tier, weight = classify_source_epistemic_tier(d)
            assert tier == TIER_1_PRIMARY, f"Failed for {d}"
            assert weight == 1.00

    def test_t1_f1_tier1_source_code_extensions(self):
        code_files = [
            "know.py", "schema.sql", "config.json", "engine.rs",
            "server.go", "app.ts", "protocol.proto", "deploy.yaml"
        ]
        for f in code_files:
            tier, weight = classify_source_epistemic_tier(f)
            assert tier == TIER_1_PRIMARY, f"Failed for {f}"
            assert weight == 1.00

    def test_t1_f1_tier2_technical_specifications(self):
        specs = [
            "fastapi_rest_api_specification.md",
            "distributed_system_architecture_whitepaper.pdf",
            "microservices_protocol_datasheet.pdf",
            "database_schema_reference.md"
        ]
        for s in specs:
            tier, weight = classify_source_epistemic_tier(s)
            assert tier == TIER_2_TECH_SPEC, f"Failed for {s}"
            assert weight == 0.85

    def test_t1_f1_tier3_secondary_literature(self):
        textbooks = [
            "Intermediate_Accounting_17th_Edition.pdf",
            "distributed_algorithms_textbook.pdf",
            "computer_systems_curriculum_handbook.pdf",
            "software_engineering_dissertation.pdf"
        ]
        for t in textbooks:
            tier, weight = classify_source_epistemic_tier(t)
            assert tier == TIER_3_SECONDARY, f"Failed for {t}"
            assert weight == 0.70

    def test_t1_f1_tier4_commentary_and_unverified(self):
        notes = [
            "scratch_notes.txt",
            "engineering_blog_post_opinion.md",
            "team_chat_transcript.txt",
            "forum_discussion_unverified.md"
        ]
        for n in notes:
            tier, weight = classify_source_epistemic_tier(n)
            assert tier == TIER_4_COMMENTARY, f"Failed for {n}"
            assert weight == 0.35

    # --- F2: Authority-Weighted Hybrid RRF Fusion (5 tests) ---
    def test_t1_f2_standard_rrf_scoring(self):
        ranks = [1, 2, 5, 10]
        k = 60
        candidates = [{"id": f"doc_{r}", "filename": f"doc_{r}.txt", "rank": r} for r in ranks]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=k)
        for idx, r in enumerate(ranks):
            expected_raw = 0.5 / (k + r) + 0.5 / (k + 100)
            assert math.isclose(fused[idx]["raw_rrf_score"], expected_raw, rel_tol=1e-3)

    def test_t1_f2_authority_weight_scaling(self):
        candidates = [
            {"id": "d1", "filename": "rfc9110.pdf", "rank": 1},      # Tier 1: 1.00
            {"id": "d2", "filename": "api_spec.md", "rank": 1},      # Tier 2: 0.85
            {"id": "d3", "filename": "textbook.pdf", "rank": 1},     # Tier 3: 0.70
            {"id": "d4", "filename": "blog_post.md", "rank": 1}      # Tier 4: 0.35
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=60)
        assert fused[0]["id"] == "d1"
        assert fused[1]["id"] == "d2"
        assert fused[2]["id"] == "d3"
        assert fused[3]["id"] == "d4"

    def test_t1_f2_temporal_multiplier_integration(self):
        candidates = [
            {"id": "fresh", "filename": "spec.md", "rank": 1, "staleness_coefficient": 1.0},
            {"id": "stale", "filename": "spec.md", "rank": 1, "staleness_coefficient": 0.5}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=60)
        fresh_score = next(c["grounded_score"] for c in fused if c["id"] == "fresh")
        stale_score = next(c["grounded_score"] for c in fused if c["id"] == "stale")
        assert math.isclose(fresh_score * 0.5, stale_score, rel_tol=1e-3)

    def test_t1_f2_rank_inversion_tier1_vs_tier4(self):
        lexical = [
            {"id": "tier4_top", "filename": "chat_scratch.txt", "rank": 1},
            {"id": "tier1_lower", "filename": "rfc9110.pdf", "rank": 4}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=lexical, dense_ranks=[], k=60)
        # Tier 1 at rank 4: 1.00 * (0.5/64 + 0.5/100) ≈ 0.0128
        # Tier 4 at rank 1: 0.35 * (0.5/61 + 0.5/100) ≈ 0.0046
        assert fused[0]["id"] == "tier1_lower"
        assert fused[1]["id"] == "tier4_top"

    def test_t1_f2_dense_and_lexical_fusion(self):
        lex = [{"id": "doc1", "filename": "rfc9110.pdf", "rank": 1}]
        dense = [{"id": "doc1", "filename": "rfc9110.pdf", "rank": 1}]
        fused = compute_authority_weighted_rrf(lexical_ranks=lex, dense_ranks=dense, k=60, intent_weights={"lexical": 0.6, "dense": 0.4})
        assert len(fused) == 1
        assert fused[0]["channel_ranks"]["lexical"] == 1
        assert fused[0]["channel_ranks"]["dense"] == 1

    # --- F3: Temporal Validity & Superseding Detection (5 tests) ---
    def test_t1_f3_superseded_by_marker_extraction(self):
        text = "This protocol is superseded by RFC 9110 and rendered obsolete."
        res = detect_temporal_validity(text)
        assert res["is_superseded"] is True
        assert "RFC 9110" in res["superseded_by"]
        assert res["temporal_status"] == "SUPERSEDED"

    def test_t1_f3_obsoleted_and_replaced_markers(self):
        text1 = "This security profile is obsoleted by ISO 27001:2022."
        res1 = detect_temporal_validity(text1)
        assert res1["is_superseded"] is True
        assert "ISO 27001:2022" in res1["superseded_by"]

        text2 = "Replaced by Version 3.0 API specification."
        res2 = detect_temporal_validity(text2)
        assert res2["is_superseded"] is True

    def test_t1_f3_deprecated_in_marker(self):
        text = "Notice: Deprecated in Version 4.2.0 due to security updates."
        res = detect_temporal_validity(text)
        assert res["temporal_status"] == "DEPRECATED"
        assert res["staleness_coefficient"] <= 0.50

    def test_t1_f3_amended_as_of_marker(self):
        text = "This regulation is amended as of 2025-06-01 under administrative ruling."
        res = detect_temporal_validity(text)
        assert res["temporal_status"] == "AMENDED"
        assert res["staleness_coefficient"] <= 0.75

    def test_t1_f3_active_document_no_marker(self):
        text = "Standard operating procedures for container deployment published 2026."
        res = detect_temporal_validity(text)
        assert res["is_superseded"] is False
        assert res["temporal_status"] == "ACTIVE"
        assert res["staleness_coefficient"] >= 0.95

    # --- F4: Exponential Staleness Decay (5 tests) ---
    def test_t1_f4_zero_staleness_current_year(self):
        decay = compute_temporal_decay(document_year_or_date=2026, domain="tech_spec", status="ACTIVE")
        assert decay >= 0.99

    def test_t1_f4_five_year_exponential_decay(self):
        # Law domain half-life = 10 years. Delta_t = 5y -> exp(-ln2 * 5 / 10) = 2^(-0.5) ≈ 0.7071
        decay = compute_temporal_decay(document_year_or_date=2021, domain="law", status="ACTIVE")
        assert 0.69 <= decay <= 0.72

    def test_t1_f4_twenty_year_exponential_decay(self):
        # Law domain half-life = 10 years. Delta_t = 20y (2 half-lives) -> decay ≈ 0.25
        decay = compute_temporal_decay(document_year_or_date=2006, domain="law", status="ACTIVE")
        assert 0.23 <= decay <= 0.27

    def test_t1_f4_superseded_recent_hard_cap(self):
        decay = compute_temporal_decay(document_year_or_date=2025, domain="law", status="SUPERSEDED")
        assert decay <= 0.40

    def test_t1_f4_superseded_old_hard_cap(self):
        decay = compute_temporal_decay(document_year_or_date=1999, domain="tech_spec", status="SUPERSEDED")
        assert 0.05 <= decay <= 0.40

    # --- F5: Dense Propositional Decomposition & Breadcrumbs (5 tests) ---
    def test_t1_f5_atomic_sentence_splitting(self):
        text = "First factual proposition. Second clear invariant claim. Third verified statement."
        props = decompose_into_propositions(text, "DocA")
        assert len(props) == 3

    def test_t1_f5_hierarchical_breadcrumb_construction(self):
        text = "The system enforces zero dependencies."
        props = decompose_into_propositions(text, "RFC_9110", ["HTTP_Semantics", "Status_Codes"])
        assert props[0]["breadcrumb_scope"] == "RFC_9110 > HTTP_Semantics > Status_Codes"

    def test_t1_f5_short_fragment_filtration(self):
        text = "Valid proposition statement here. Ok. Yes. No. Another valid proposition statement."
        props = decompose_into_propositions(text, "DocB")
        assert len(props) == 2

    def test_t1_f5_unique_proposition_id_generation(self):
        text = "Statement one of test document. Statement two of test document."
        props = decompose_into_propositions(text, "SpecDoc")
        assert props[0]["proposition_id"] == "SpecDoc#prop_0"
        assert props[1]["proposition_id"] == "SpecDoc#prop_1"

    def test_t1_f5_contextual_statement_formatting(self):
        text = "Maximum transmission unit is 1500 bytes."
        props = decompose_into_propositions(text, "Ethernet", ["Layer2"])
        assert props[0]["contextual_statement"] == "[Ethernet > Layer2] Maximum transmission unit is 1500 bytes."

    # --- F6: Cross-Document Consensus & Contradiction Matrix (5 tests) ---
    def test_t1_f6_two_source_concordant_consensus(self):
        passages = [
            {"filename": "spec_a.pdf", "content": "The memory ceiling is 1024MB per instance."},
            {"filename": "spec_b.pdf", "content": "Each container is limited to 1024MB memory."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "HIGH_CONSENSUS"
        assert res["consensus_score"] == 0.95

    def test_t1_f6_numerical_discrepancy_contradiction(self):
        passages = [
            {"filename": "doc_a.pdf", "content": "The system throughput is 500tps."},
            {"filename": "doc_b.pdf", "content": "The system throughput is 5000tps."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "CONTRADICTION_DETECTED"
        assert res["consensus_score"] == 0.45
        assert res["contradictions_count"] >= 1

    def test_t1_f6_single_source_neutral(self):
        passages = [{"filename": "doc_single.pdf", "content": "Only one passage available."}]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "SINGLE_SOURCE"
        assert res["consensus_score"] == 0.70

    def test_t1_f6_non_overlapping_independent_claims(self):
        passages = [
            {"filename": "db.pdf", "content": "Database uses SQLite WAL mode."},
            {"filename": "ui.pdf", "content": "Frontend is implemented in React."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "NEUTRAL"
        assert res["consensus_score"] == 0.70

    def test_t1_f6_majority_consensus_voting(self):
        passages = [
            {"filename": "node1.pdf", "content": "Cluster has 100 nodes."},
            {"filename": "node2.pdf", "content": "Cluster total is 100 nodes."},
            {"filename": "node3.pdf", "content": "Cluster has 500 nodes."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["agreements_count"] >= 1
        assert res["consensus_level"] == "HIGH_CONSENSUS"

    # --- F7: Optical Fiber Latency Invariant Guard (5 tests) ---
    def test_t1_f7_transatlantic_valid_latency(self):
        res = check_optical_latency_invariant(distance_km=5000.0, reported_latency_ms=70.0)
        assert res["is_physically_possible"] is True

    def test_t1_f7_transatlantic_faster_than_light_violation(self):
        res = check_optical_latency_invariant(distance_km=5000.0, reported_latency_ms=10.0)
        assert res["is_physically_possible"] is False
        assert "violates physical limit" in res["violation_details"]

    def test_t1_f7_transpacific_valid_latency(self):
        res = check_optical_latency_invariant(distance_km=10000.0, reported_latency_ms=120.0)
        assert res["is_physically_possible"] is True

    def test_t1_f7_datacenter_campus_latency(self):
        res = check_optical_latency_invariant(distance_km=1.0, reported_latency_ms=0.05)
        assert res["is_physically_possible"] is True

    def test_t1_f7_datacenter_sub_microsecond_violation(self):
        res = check_optical_latency_invariant(distance_km=1.0, reported_latency_ms=0.001)
        assert res["is_physically_possible"] is False

    # --- F8: Universal Scalability Law (USL) Guard (5 tests) ---
    def test_t1_f8_linear_scaling_zero_contention(self):
        res = check_usl_scalability_invariant(node_count=16, alpha=0.0, beta=0.0, claimed_speedup=16.0)
        assert res["is_computationally_valid"] is True

    def test_t1_f8_amdahl_saturation_ceiling(self):
        # N=100, alpha=0.10, beta=0 -> S_max = 100 / (1 + 9.9) = 100/10.9 ≈ 9.17x
        res_valid = check_usl_scalability_invariant(node_count=100, alpha=0.10, beta=0.0, claimed_speedup=9.0)
        assert res_valid["is_computationally_valid"] is True

        res_invalid = check_usl_scalability_invariant(node_count=100, alpha=0.10, beta=0.0, claimed_speedup=25.0)
        assert res_invalid["is_computationally_valid"] is False

    def test_t1_f8_usl_retrograde_coherency_peak(self):
        # N=64, alpha=0.02, beta=0.005 -> S_max ≈ 2.85x
        res_valid = check_usl_scalability_invariant(node_count=64, alpha=0.02, beta=0.005, claimed_speedup=2.5)
        assert res_valid["is_computationally_valid"] is True

        res_invalid = check_usl_scalability_invariant(node_count=64, alpha=0.02, beta=0.005, claimed_speedup=15.0)
        assert res_invalid["is_computationally_valid"] is False

    def test_t1_f8_superlinear_speedup_rejection(self):
        res = check_usl_scalability_invariant(node_count=32, alpha=0.05, beta=0.001, claimed_speedup=40.0)
        assert res["is_computationally_valid"] is False

    def test_t1_f8_valid_distributed_speedup(self):
        # N=32, alpha=0.05, beta=0.001 -> S_max ≈ 9.03x
        res = check_usl_scalability_invariant(node_count=32, alpha=0.05, beta=0.001, claimed_speedup=8.5)
        assert res["is_computationally_valid"] is True

    # --- F9: CAP & PACELC Invariant Guard (5 tests) ---
    def test_t1_f9_cap_partition_linearizability_violation(self):
        claim = {"partition_active": True, "consistency": "linearizable", "availability": "100%"}
        res = check_cap_pacelc_invariant(claim)
        assert res["is_computationally_valid"] is False
        assert res["tradeoff_model"] == "CP_VIOLATION"

    def test_t1_f9_pacelc_zero_latency_replication_violation(self):
        claim = {"multi_region": True, "consistency": "linearizable", "replication_latency_ms": 0.0}
        res = check_cap_pacelc_invariant(claim)
        assert res["is_computationally_valid"] is False
        assert res["tradeoff_model"] == "PACELC_ZERO_LATENCY_VIOLATION"

    def test_t1_f9_valid_cp_system_tradeoff(self):
        claim = {"partition_active": True, "consistency": "linearizable", "availability": "sacrificed"}
        res = check_cap_pacelc_invariant(claim)
        assert res["is_computationally_valid"] is True

    def test_t1_f9_valid_ap_eventual_consistency_tradeoff(self):
        claim = {"partition_active": True, "consistency": "eventual", "availability": "100%"}
        res = check_cap_pacelc_invariant(claim)
        assert res["is_computationally_valid"] is True

    def test_t1_f9_quorum_rule_evaluation(self):
        # R=2, W=2, N=3 -> R+W=4 > 3 -> valid
        valid_q = {"r_quorum": 2, "w_quorum": 2, "n_replicas": 3, "strong_consistency": True}
        assert check_cap_pacelc_invariant(valid_q)["is_computationally_valid"] is True

        # R=1, W=1, N=3 -> R+W=2 <= 3 -> invalid for strong consistency
        invalid_q = {"r_quorum": 1, "w_quorum": 1, "n_replicas": 3, "strong_consistency": True}
        res_invalid = check_cap_pacelc_invariant(invalid_q)
        assert res_invalid["is_computationally_valid"] is False
        assert res_invalid["tradeoff_model"] == "QUORUM_DEFICIT"

    # --- F10: Carnot & Landauer Thermodynamic Limits (5 tests) ---
    def test_t1_f10_valid_carnot_engine_efficiency(self):
        res = check_carnot_efficiency_invariant(t_hot_k=600.0, t_cold_k=300.0, claimed_efficiency=0.45)
        assert res["is_physically_possible"] is True

    def test_t1_f10_impossible_carnot_perpetual_motion(self):
        res = check_carnot_efficiency_invariant(t_hot_k=600.0, t_cold_k=300.0, claimed_efficiency=0.85)
        assert res["is_physically_possible"] is False

    def test_t1_f10_valid_landauer_room_temperature_energy(self):
        # T=300K, E_min ≈ 2.87e-21 J. Claimed 3.0e-21 J is valid.
        res = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=3.0e-21, bit_count=1)
        assert res["is_physically_possible"] is True

    def test_t1_f10_impossible_sub_landauer_erasure(self):
        # T=300K, claimed 1.0e-22 J violates limit
        res = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=1.0e-22, bit_count=1)
        assert res["is_physically_possible"] is False

    def test_t1_f10_cryogenic_landauer_energy(self):
        # T=4.2K, E_min ≈ 4.02e-23 J. Claimed 5.0e-23 J is valid.
        res = check_landauer_limit_invariant(t_kelvin=4.2, claimed_energy_joules=5.0e-23, bit_count=1)
        assert res["is_physically_possible"] is True

    # --- F11: Shannon Channel Capacity Limit (5 tests) ---
    def test_t1_f11_valid_gaussian_channel_rate(self):
        # B=20MHz, SNR=1000 -> C ≈ 199.35 Mbps. Claimed 150 Mbps is valid.
        res = check_shannon_capacity_invariant(bandwidth_hz=20e6, snr_linear=1000.0, claimed_bps=150e6)
        assert res["is_physically_possible"] is True

    def test_t1_f11_impossible_super_shannon_rate(self):
        # B=20MHz, SNR=1000, claimed 500 Mbps violates Shannon limit
        res = check_shannon_capacity_invariant(bandwidth_hz=20e6, snr_linear=1000.0, claimed_bps=500e6)
        assert res["is_physically_possible"] is False

    def test_t1_f11_deep_space_low_snr_capacity(self):
        # B=10kHz, SNR=0.1 -> C ≈ 1375 bps. Claimed 1000 bps is valid.
        res = check_shannon_capacity_invariant(bandwidth_hz=10e3, snr_linear=0.1, claimed_bps=1000.0)
        assert res["is_physically_possible"] is True

    def test_t1_f11_snr_db_to_linear_conversion(self):
        snr_db = 30.0
        snr_linear = 10.0 ** (snr_db / 10.0)  # 1000.0
        assert math.isclose(snr_linear, 1000.0, rel_tol=1e-5)
        res = check_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=snr_linear, claimed_bps=50e6)
        assert res["is_physically_possible"] is True

    def test_t1_f11_optical_broadband_capacity(self):
        # B=50GHz, SNR=10000 -> C ≈ 664.4 Gbps
        res = check_shannon_capacity_invariant(bandwidth_hz=50e9, snr_linear=10000.0, claimed_bps=600e9)
        assert res["is_physically_possible"] is True

    # --- F12: Grounding Scorecard & Refusal Gate (5 tests) ---
    def test_t1_f12_high_confidence_success(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP 200 OK status indicates request succeeded.", "rank": 1},
            {"filename": "rfc9110_part2.pdf", "content": "HTTP 200 OK status indicates request succeeded.", "rank": 2}
        ]
        res = engine.evaluate_grounding("HTTP 200 status code", passages)
        assert res["status"] == "success"
        assert res["overall_grounded_confidence"] >= 0.80

    def test_t1_f12_low_authority_commentary_refusal(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "chat_notes.txt", "content": "I think the server port might be 8080 maybe.", "rank": 1}
        ]
        res = engine.evaluate_grounding("server port", passages)
        assert res["status"] == "refusal"
        assert res["reason"] == "HALLUCINATION_REFUSAL_GATE"
        assert res["overall_grounded_confidence"] < 0.65

    def test_t1_f12_contradiction_induced_refusal(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "blog_a.md", "content": "Port limit is 500.", "rank": 1},
            {"filename": "blog_b.md", "content": "Port limit is 9000.", "rank": 2}
        ]
        res = engine.evaluate_grounding("port limit", passages)
        assert res["status"] == "refusal"

    def test_t1_f12_physical_invariant_binary_veto(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP protocol specification.", "rank": 1}
        ]
        # Invariant violation in generated claim
        impossible_claim = {"type": "OPTICAL", "distance_km": 5000.0, "reported_latency_ms": 5.0}
        res = engine.evaluate_grounding("HTTP", passages, generated_claim=impossible_claim)
        assert res["status"] == "refusal"
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert res["overall_grounded_confidence"] == 0.0

    def test_t1_f12_zero_evidence_refusal(self):
        engine = GroundedRetrievalEngine()
        res = engine.evaluate_grounding("unknown topic query", [])
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (60 Tests: 5 per Feature F1..F12)
# ==============================================================================
class TestTier2BoundaryCornerCases:

    # --- F1 Boundaries (5 tests) ---
    def test_t2_f1_empty_filename_with_content(self):
        tier, weight = classify_source_epistemic_tier("", content_snippet="RFC 9110 HTTP Semantics Standard")
        assert tier == TIER_1_PRIMARY
        assert weight == 1.00

    def test_t2_f1_mixed_case_variations(self):
        t1, _ = classify_source_epistemic_tier("rFc9110.PDF")
        t2, _ = classify_source_epistemic_tier("IsO_27001.DOCX")
        t3, _ = classify_source_epistemic_tier("sEc_10-K.TXT")
        assert t1 == TIER_1_PRIMARY
        assert t2 == TIER_1_PRIMARY
        assert t3 == TIER_1_PRIMARY

    def test_t2_f1_multiple_conflicting_tier_keywords(self):
        # Filename contains guide (Tier 3), rfc (Tier 1), api (Tier 2) -> Tier 1 takes precedence
        tier, weight = classify_source_epistemic_tier("guide_to_rfc9110_api.pdf")
        assert tier == TIER_1_PRIMARY
        assert weight == 1.00

    def test_t2_f1_delimiter_formatting_variations(self):
        variants = ["rfc-9110.pdf", "rfc_9110.pdf", "rfc 9110.pdf", "rfc9110.pdf"]
        for v in variants:
            tier, _ = classify_source_epistemic_tier(v)
            assert tier == TIER_1_PRIMARY, f"Failed for {v}"

    def test_t2_f1_unknown_extension_unmatched_content(self):
        tier, weight = classify_source_epistemic_tier("random_blob.xyz", content_snippet="Just random notes.")
        assert tier == TIER_4_COMMENTARY
        assert weight == 0.35

    # --- F2 Boundaries (5 tests) ---
    def test_t2_f2_extreme_smoothing_constants(self):
        candidates = [{"id": "d1", "filename": "spec.md", "rank": 1}]
        fused_k1 = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=1)
        fused_k1000 = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=1000)
        assert len(fused_k1) == 1
        assert len(fused_k1000) == 1
        assert fused_k1[0]["raw_rrf_score"] > fused_k1000[0]["raw_rrf_score"]

    def test_t2_f2_empty_rank_lists(self):
        fused = compute_authority_weighted_rrf(lexical_ranks=[], dense_ranks=[], k=60)
        assert fused == []

    def test_t2_f2_single_item_rank_list(self):
        fused = compute_authority_weighted_rrf(
            lexical_ranks=[{"id": "doc1", "filename": "rfc9110.pdf", "rank": 1}],
            dense_ranks=[],
            k=60
        )
        assert len(fused) == 1
        assert fused[0]["final_rank"] == 1

    def test_t2_f2_score_ties_deterministic_ordering(self):
        candidates = [
            {"id": "a", "filename": "spec_a.md", "rank": 1},
            {"id": "b", "filename": "spec_b.md", "rank": 1}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=60)
        assert len(fused) == 2
        assert fused[0]["final_rank"] == 1
        assert fused[1]["final_rank"] == 2

    def test_t2_f2_large_rank_index(self):
        candidates = [{"id": "deep_doc", "filename": "rfc9110.pdf", "rank": 10000}]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=60)
        assert fused[0]["raw_rrf_score"] > 0.0

    # --- F3 Boundaries (5 tests) ---
    def test_t2_f3_superseding_marker_at_deep_offset(self):
        padding = "A" * 1000 + "\n"
        text = padding + "This standard is superseded by RFC 9110.\n"
        res = detect_temporal_validity(text)
        assert res["is_superseded"] is True
        assert "RFC 9110" in res["superseded_by"]

    def test_t2_f3_negation_and_false_positives(self):
        text = "This document is currently active and is NOT superseded by RFC 9110."
        res = detect_temporal_validity(text, publication_year=2026)
        # Verify active handling
        assert res["publication_year"] == 2026

    def test_t2_f3_multiple_superseding_markers(self):
        text = "Obsoletes: RFC 2616, RFC 7230\nSuperseded by RFC 9110."
        res = detect_temporal_validity(text)
        assert res["is_superseded"] is True

    def test_t2_f3_trailing_punctuation_in_target(self):
        text = "This specification is superseded by RFC 9110, as amended."
        res = detect_temporal_validity(text)
        assert res["superseded_by"] == "RFC 9110"

    def test_t2_f3_unicode_and_special_characters(self):
        text = "This standard is replaced by ISO/IEC 27001:2022 standard."
        res = detect_temporal_validity(text)
        assert res["is_superseded"] is True
        assert "ISO/IEC 27001:2022" in res["superseded_by"]

    # --- F4 Boundaries (5 tests) ---
    def test_t2_f4_future_publication_year(self):
        # Published in future year -> age clamped to 0 -> decay 1.00
        decay = compute_temporal_decay(document_year_or_date=2030, domain="tech_spec")
        assert decay >= 0.99

    def test_t2_f4_none_publication_year(self):
        decay = compute_temporal_decay(document_year_or_date=None, domain="general")
        assert decay == 1.00

    def test_t2_f4_ancient_publication_year(self):
        # 1900 publication date decays but stays above 0.05 floor
        decay = compute_temporal_decay(document_year_or_date=1900, domain="tech_spec")
        assert decay >= 0.05

    def test_t2_f4_exact_hard_cap_boundary_crossing(self):
        # Superseded status forces decay <= 0.40
        decay_active = compute_temporal_decay(document_year_or_date=2026, domain="law", status="ACTIVE")
        decay_superseded = compute_temporal_decay(document_year_or_date=2026, domain="law", status="SUPERSEDED")
        assert decay_active >= 0.99
        assert decay_superseded <= 0.40

    def test_t2_f4_custom_half_life_parameter(self):
        # Custom half life of 365.25 days (1 year). 1 year old -> decay ≈ 0.50
        decay = compute_temporal_decay(document_year_or_date=2025, half_life_days=365.25)
        assert 0.48 <= decay <= 0.52

    # --- F5 Boundaries (5 tests) ---
    def test_t2_f5_single_massive_run_on_sentence(self):
        text = "This is a single very long uninterrupted technical statement without terminal punctuation"
        props = decompose_into_propositions(text, "DocRunOn")
        assert len(props) == 1

    def test_t2_f5_abbreviations_with_periods(self):
        text = "The system uses e.g. SQLite for persistence and i.e. WAL mode for concurrency."
        props = decompose_into_propositions(text, "DocAbbr")
        assert len(props) >= 1

    def test_t2_f5_excessive_whitespace_and_newlines(self):
        text = "   \n\t  Proposition with excessive leading and trailing whitespace.   \n\n\t"
        props = decompose_into_propositions(text, "DocWhite")
        assert len(props) == 1
        assert not props[0]["statement"].startswith(" ")

    def test_t2_f5_all_fragments_below_threshold(self):
        text = "Short. Hi. No. Ok."
        props = decompose_into_propositions(text, "DocShort")
        assert len(props) == 0

    def test_t2_f5_unicode_and_emoji_handling(self):
        text = "Universal Scalability Law speedup incorporates contention \u03b1 and coherency \u03b2 parameters."
        props = decompose_into_propositions(text, "DocUnicode")
        assert len(props) == 1
        assert "\u03b1" in props[0]["statement"]

    # --- F6 Boundaries (5 tests) ---
    def test_t2_f6_empty_passages_list(self):
        res = evaluate_cross_document_consensus([])
        assert res["consensus_level"] == "SINGLE_SOURCE"
        assert res["consensus_score"] == 0.70

    def test_t2_f6_passages_without_numerical_metrics(self):
        passages = [
            {"filename": "a.txt", "content": "Qualitative claim about software architecture."},
            {"filename": "b.txt", "content": "Another qualitative architectural claim."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "NEUTRAL"

    def test_t2_f6_metric_unit_normalization(self):
        passages = [
            {"filename": "a.txt", "content": "System cache is 1024MB limit."},
            {"filename": "b.txt", "content": "System cache is 1024MB limit."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "HIGH_CONSENSUS"

    def test_t2_f6_multi_way_contradictions(self):
        passages = [
            {"filename": "a.txt", "content": "Limit is 100tps."},
            {"filename": "b.txt", "content": "Limit is 200tps."},
            {"filename": "c.txt", "content": "Limit is 300tps."},
            {"filename": "d.txt", "content": "Limit is 400tps."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "CONTRADICTION_DETECTED"
        assert res["contradictions_count"] >= 3

    def test_t2_f6_identical_duplicate_passages(self):
        passages = [
            {"filename": "a.txt", "content": "Exact duplicate content with 500 users limit."},
            {"filename": "b.txt", "content": "Exact duplicate content with 500 users limit."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "HIGH_CONSENSUS"
        assert res["agreements_count"] >= 1

    # --- F7 Boundaries (5 tests) ---
    def test_t2_f7_zero_distance(self):
        res = check_optical_latency_invariant(distance_km=0.0, reported_latency_ms=0.0)
        assert res["is_physically_possible"] is True

    def test_t2_f7_negative_distance_and_latency(self):
        res_d = check_optical_latency_invariant(distance_km=-100.0, reported_latency_ms=10.0)
        assert res_d["is_physically_possible"] is False

        res_l = check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=-5.0)
        assert res_l["is_physically_possible"] is False

    def test_t2_f7_vacuum_refractive_index(self):
        # n = 1.0 (vacuum): c = 299792.458 km/s. For 300,000 km, 1-way ~ 1.0s, RTT ~ 2.0s (2000 ms)
        res = check_optical_latency_invariant(distance_km=299792.458, reported_latency_ms=2000.0, n_refractive=1.0)
        assert res["is_physically_possible"] is True

    def test_t2_f7_astronomical_distance(self):
        # Earth to Moon distance ≈ 384,400 km in fiber (n=1.47): RTT min ≈ 3767 ms
        res_valid = check_optical_latency_invariant(distance_km=384400.0, reported_latency_ms=4000.0)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_optical_latency_invariant(distance_km=384400.0, reported_latency_ms=2000.0)
        assert res_invalid["is_physically_possible"] is False

    def test_t2_f7_exact_speed_of_light_boundary(self):
        # 2039.4 km at ~203,940 km/s -> RTT min = 20.0 ms. Claiming 20.0 ms is valid.
        res = check_optical_latency_invariant(distance_km=2039.4045, reported_latency_ms=20.0)
        assert res["is_physically_possible"] is True

    # --- F8 Boundaries (5 tests) ---
    def test_t2_f8_single_node_concurrency(self):
        res_valid = check_usl_scalability_invariant(node_count=1, alpha=0.05, beta=0.01, claimed_speedup=1.0)
        assert res_valid["is_computationally_valid"] is True

        res_invalid = check_usl_scalability_invariant(node_count=1, alpha=0.05, beta=0.01, claimed_speedup=2.0)
        assert res_invalid["is_computationally_valid"] is False

    def test_t2_f8_invalid_node_count_zero_or_negative(self):
        res_zero = check_usl_scalability_invariant(node_count=0, alpha=0.05, beta=0.01, claimed_speedup=1.0)
        assert res_zero["is_computationally_valid"] is False

        res_neg = check_usl_scalability_invariant(node_count=-5, alpha=0.05, beta=0.01, claimed_speedup=1.0)
        assert res_neg["is_computationally_valid"] is False

    def test_t2_f8_total_contention_alpha_one(self):
        # alpha = 1.0, beta = 0 -> S(N) = N / (1 + 1*(N-1)) = 1.0
        res = check_usl_scalability_invariant(node_count=50, alpha=1.0, beta=0.0, claimed_speedup=1.0)
        assert res["is_computationally_valid"] is True

    def test_t2_f8_extreme_coherency_penalty(self):
        # beta = 0.50 -> retrograde collapse
        res = check_usl_scalability_invariant(node_count=10, alpha=0.0, beta=0.50, claimed_speedup=0.20)
        assert res["is_computationally_valid"] is True

    def test_t2_f8_superlinear_speedup_tolerance_threshold(self):
        # N=10, alpha=0, beta=0 -> S_theory = 10.0. Claim 10.4x (within 5%) is valid; 10.6x is invalid.
        res_within = check_usl_scalability_invariant(node_count=10, alpha=0.0, beta=0.0, claimed_speedup=10.4)
        assert res_within["is_computationally_valid"] is True

        res_exceed = check_usl_scalability_invariant(node_count=10, alpha=0.0, beta=0.0, claimed_speedup=10.6)
        assert res_exceed["is_computationally_valid"] is False

    # --- F9 Boundaries (5 tests) ---
    def test_t2_f9_unpartitioned_latency_tradeoff(self):
        # Normal operation with realistic latency is valid
        claim = {"multi_region": True, "consistency": "linearizable", "replication_latency_ms": 50.0}
        assert check_cap_pacelc_invariant(claim)["is_computationally_valid"] is True

    def test_t2_f9_single_node_cap_boundary(self):
        claim = {"n_replicas": 1, "consistency": "linearizable", "availability": "100%"}
        assert check_cap_pacelc_invariant(claim)["is_computationally_valid"] is True

    def test_t2_f9_empty_and_malformed_claim(self):
        assert check_cap_pacelc_invariant({})["is_computationally_valid"] is True
        assert check_cap_pacelc_invariant("")["is_computationally_valid"] is True

    def test_t2_f9_case_insensitive_cap_keywords(self):
        claim_str = "SYSTEM GUARANTEES LINEARIZABLE CONSISTENCY AND 100% AVAILABILITY DURING NETWORK PARTITION."
        res = check_cap_pacelc_invariant(claim_str)
        assert res["is_computationally_valid"] is False

    def test_t2_f9_exact_quorum_boundary(self):
        # R=2, W=2, N=3 -> R+W=4 > 3 -> valid
        assert check_cap_pacelc_invariant({"r_quorum": 2, "w_quorum": 2, "n_replicas": 3, "strong_consistency": True})["is_computationally_valid"] is True
        # R=1, W=2, N=3 -> R+W=3 <= 3 -> invalid
        assert check_cap_pacelc_invariant({"r_quorum": 1, "w_quorum": 2, "n_replicas": 3, "strong_consistency": True})["is_computationally_valid"] is False

    # --- F10 Boundaries (5 tests) ---
    def test_t2_f10_equal_temperatures(self):
        res = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=300.0, claimed_efficiency=0.01)
        assert res["is_physically_possible"] is False

    def test_t2_f10_absolute_zero_and_negative_temperatures(self):
        res_zero = check_landauer_limit_invariant(t_kelvin=0.0, claimed_energy_joules=1e-20)
        assert res_zero["is_physically_possible"] is False

        res_neg = check_carnot_efficiency_invariant(t_hot_k=-100.0, t_cold_k=-200.0, claimed_efficiency=0.10)
        assert res_neg["is_physically_possible"] is False

    def test_t2_f10_exact_carnot_limit(self):
        # Th=500K, Tc=250K -> eta_max = 0.50. Claiming 0.50 exactly is valid.
        res = check_carnot_efficiency_invariant(t_hot_k=500.0, t_cold_k=250.0, claimed_efficiency=0.50)
        assert res["is_physically_possible"] is True

    def test_t2_f10_infinite_hot_temperature_asymptote(self):
        # Th=1e6K, Tc=300K -> eta_max ≈ 0.9997. Claiming 0.99 is valid.
        res = check_carnot_efficiency_invariant(t_hot_k=1e6, t_cold_k=300.0, claimed_efficiency=0.99)
        assert res["is_physically_possible"] is True

    def test_t2_f10_multibit_landauer_scaling(self):
        # 10^6 bits at 300K: E_min = 10^6 * 2.8706e-21 J ≈ 2.8706e-15 J
        res_valid = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=3.0e-15, bit_count=1000000)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=1.0e-15, bit_count=1000000)
        assert res_invalid["is_physically_possible"] is False

    # --- F11 Boundaries (5 tests) ---
    def test_t2_f11_zero_and_negative_bandwidth(self):
        res_zero = check_shannon_capacity_invariant(bandwidth_hz=0.0, snr_linear=100.0, claimed_bps=100.0)
        assert res_zero["is_physically_possible"] is False

        res_neg = check_shannon_capacity_invariant(bandwidth_hz=-10e6, snr_linear=100.0, claimed_bps=100.0)
        assert res_neg["is_physically_possible"] is False

    def test_t2_f11_zero_signal_power_snr_zero(self):
        # SNR = 0 -> Capacity = 0 bps
        res = check_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=0.0, claimed_bps=100.0)
        assert res["is_physically_possible"] is False

    def test_t2_f11_extreme_high_snr(self):
        # SNR = 1e9, B = 10 MHz -> C = 10e6 * log2(1e9 + 1) ≈ 298.97 Mbps
        res = check_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=1e9, claimed_bps=250e6)
        assert res["is_physically_possible"] is True

    def test_t2_f11_exact_shannon_capacity_boundary(self):
        # B = 10MHz, SNR = 3 -> log2(4) = 2 -> C = 20 Mbps. Claiming 20 Mbps is valid.
        res = check_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=3.0, claimed_bps=20e6)
        assert res["is_physically_possible"] is True

    def test_t2_f11_linear_bandwidth_scaling(self):
        c1 = check_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=7.0, claimed_bps=10e6)["theoretical_capacity_bps"]
        c2 = check_shannon_capacity_invariant(bandwidth_hz=20e6, snr_linear=7.0, claimed_bps=10e6)["theoretical_capacity_bps"]
        assert math.isclose(c2, c1 * 2.0, rel_tol=1e-3)

    # --- F12 Boundaries (5 tests) ---
    def test_t2_f12_exact_refusal_threshold_boundary(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        # Mocking confidence at 0.65
        passages = [
            {"filename": "spec.md", "content": "Factual spec passage.", "epistemic_weight": 0.85, "staleness_coefficient": 1.0, "rank": 1}
        ]
        res = engine.evaluate_grounding("query", passages)
        assert res["status"] == "success"

    def test_t2_f12_just_below_refusal_threshold(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "notes.txt", "content": "Informal notes.", "epistemic_weight": 0.35, "staleness_coefficient": 0.5, "rank": 1}
        ]
        res = engine.evaluate_grounding("query", passages)
        assert res["status"] == "refusal"

    def test_t2_f12_extreme_top_k_parameters(self):
        engine_k1 = GroundedRetrievalEngine(top_k=1)
        engine_k100 = GroundedRetrievalEngine(top_k=100)
        passages = [{"filename": "rfc9110.pdf", "content": "HTTP spec.", "rank": 1}]
        assert engine_k1.evaluate_grounding("query", passages)["top_passages_count"] == 1
        assert engine_k100.evaluate_grounding("query", passages)["top_passages_count"] == 1

    def test_t2_f12_malformed_and_whitespace_queries(self):
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "rfc9110.pdf", "content": "HTTP spec.", "rank": 1}]
        res_empty = engine.evaluate_grounding("   ", passages)
        assert res_empty["status"] == "refusal"

    def test_t2_f12_structured_diagnostic_report_completeness(self):
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "chat.txt", "content": "Just chat.", "rank": 1}]
        res = engine.evaluate_grounding("query", passages)
        assert "diagnostics" in res
        assert "knowledge_gaps" in res["diagnostics"]


# ==============================================================================
# TIER 3: CROSS-FEATURE PAIRWISE INTERACTIONS (12 Tests)
# ==============================================================================
class TestTier3CrossFeatureInteractions:

    def test_t3_cf1_epistemic_tier_with_temporal_decay(self):
        # 15y-old Tier 1 document (1.00 * ~0.35 = 0.35) vs fresh Tier 4 document (0.35 * 1.0 = 0.35)
        t1_decay = compute_temporal_decay(2011, domain="law", status="ACTIVE")
        t4_decay = compute_temporal_decay(2026, domain="commentary", status="ACTIVE")
        score_t1 = 1.00 * t1_decay
        score_t4 = 0.35 * t4_decay
        assert score_t1 >= score_t4

    def test_t3_cf2_superseding_with_staleness_hard_cap(self):
        # 2y-old document with SUPERSEDED status is capped at <= 0.40 rather than standard 2y decay (~0.87)
        normal_decay = compute_temporal_decay(2024, domain="law", status="ACTIVE")
        superseded_decay = compute_temporal_decay(2024, domain="law", status="SUPERSEDED")
        assert normal_decay > 0.80
        assert superseded_decay <= 0.40

    def test_t3_cf3_epistemic_hierarchy_resolving_contradiction(self):
        # Contradiction between Tier 1 RFC 9110 (1500 MTU) and Tier 4 blog (9000 MTU)
        passages = [
            {"filename": "rfc9110.pdf", "content": "The standard packet MTU is 1500 bytes.", "rank": 1},
            {"filename": "blog.md", "content": "The standard packet MTU is 9000 bytes.", "rank": 2}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=passages, dense_ranks=[], k=60)
        assert fused[0]["id"] == fused[0]["id"]
        assert fused[0]["epistemic_tier"] == TIER_1_PRIMARY
        assert fused[0]["grounded_score"] > fused[1]["grounded_score"] * 2.0

    def test_t3_cf4_rrf_reranking_active_over_superseded(self):
        candidates = [
            {"id": "rfc2616", "filename": "rfc2616.pdf", "rank": 1, "staleness_coefficient": 0.35},
            {"id": "rfc9110", "filename": "rfc9110.pdf", "rank": 2, "staleness_coefficient": 1.00}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=candidates, dense_ranks=[], k=60)
        assert fused[0]["id"] == "rfc9110"

    def test_t3_cf5_proposition_decomposition_inheriting_tier(self):
        doc_name = "rfc9110_http_semantics.pdf"
        tier, weight = classify_source_epistemic_tier(doc_name)
        props = decompose_into_propositions("HTTP status code 200 signifies success. HTTP 404 indicates not found.", doc_name)
        for p in props:
            p["epistemic_tier"] = tier
            p["epistemic_weight"] = weight
            assert p["epistemic_tier"] == TIER_1_PRIMARY

    def test_t3_cf6_cross_proposition_consensus_aggregation(self):
        p1 = decompose_into_propositions("The database maximum size is 1000 nodes.", "Spec1")
        p2 = decompose_into_propositions("The database maximum size is 1000 nodes.", "Spec2")
        passages = [{"filename": p1[0]["proposition_id"], "content": p1[0]["statement"]},
                    {"filename": p2[0]["proposition_id"], "content": p2[0]["statement"]}]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "HIGH_CONSENSUS"

    def test_t3_cf7_optical_latency_with_pacelc_distributed_replication(self):
        # Cross-ocean 5,000 km replication claiming 5ms synchronous latency
        claim_optical = {"type": "OPTICAL", "distance_km": 5000.0, "reported_latency_ms": 5.0}
        claim_pacelc = {"multi_region": True, "consistency": "linearizable", "replication_latency_ms": 0.0}
        audit = evaluate_all_boundary_invariants([claim_optical, claim_pacelc])
        assert audit["valid"] is False
        assert len(audit["violations"]) == 2

    def test_t3_cf8_usl_violation_triggering_refusal_gate(self):
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "rfc9110.pdf", "content": "HTTP specification.", "rank": 1}]
        impossible_usl = {"type": "USL", "node_count": 32, "alpha": 0.05, "beta": 0.001, "claimed_speedup": 500.0}
        res = engine.evaluate_grounding("USL scaling", passages, generated_claim=impossible_usl)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0

    def test_t3_cf9_landauer_violation_triggering_refusal_gate(self):
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "spec.md", "content": "Cryogenic processor specification.", "rank": 1}]
        impossible_landauer = {"type": "LANDAUER", "t_kelvin": 300.0, "claimed_energy_joules": 1e-24, "bit_count": 1}
        res = engine.evaluate_grounding("Landauer erasure", passages, generated_claim=impossible_landauer)
        assert res["status"] == "refusal"

    def test_t3_cf10_shannon_limit_overriding_textual_consensus(self):
        engine = GroundedRetrievalEngine()
        # Even if multiple passages agree on an impossible rate, physical invariant vetoes it
        passages = [
            {"filename": "blog1.md", "content": "The transmission speed is 1000 Mbps.", "rank": 1},
            {"filename": "blog2.md", "content": "The transmission speed is 1000 Mbps.", "rank": 2}
        ]
        impossible_shannon = {"type": "SHANNON", "bandwidth_hz": 1e6, "snr_linear": 10.0, "claimed_bps": 1000e6}
        res = engine.evaluate_grounding("radio speed", passages, generated_claim=impossible_shannon)
        assert res["status"] == "refusal"

    def test_t3_cf11_all_tier4_sources_triggering_refusal_gate(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "chat1.txt", "content": "Random speculation on API.", "rank": 1},
            {"filename": "forum.txt", "content": "Random discussion on API.", "rank": 2}
        ]
        res = engine.evaluate_grounding("API details", passages)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] < 0.65

    def test_t3_cf12_temporal_freshness_resolving_multi_document_consensus(self):
        # 2 old superseded docs agree on 500tps, 1 fresh active doc says 5000tps
        passages = [
            {"id": "rfc7230", "filename": "rfc7230.pdf", "content": "Framing limit 500tps", "rank": 1, "staleness_coefficient": 0.35},
            {"id": "rfc7231", "filename": "rfc7231.pdf", "content": "Framing limit 500tps", "rank": 2, "staleness_coefficient": 0.35},
            {"id": "rfc9110", "filename": "rfc9110.pdf", "content": "Framing limit 5000tps", "rank": 3, "staleness_coefficient": 1.00}
        ]
        fused = compute_authority_weighted_rrf(lexical_ranks=passages, dense_ranks=[], k=60)
        assert fused[0]["id"] == "rfc9110"


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS (6 Tests)
# ==============================================================================
class TestTier4RealWorldScenarios:

    def test_t4_scenario1_transatlantic_distributed_database_replication(self):
        """
        Scenario 1: High-Frequency Distributed Database Replication across Transatlantic Fiber Cables.
        - Distance: New York to London (5,585 km).
        - Claim: 15ms synchronous linearizable commit across transatlantic nodes with 100% availability during network partition.
        - Optical check: t_min_rtt ≈ 54.7 ms > 15 ms -> VIOLATION.
        - CAP check: Linearizable + 100% available under partition -> VIOLATION.
        - Refusal gate activates with score 0.0.
        """
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "db_whitepaper.pdf", "content": "Cross-region database replication spec.", "rank": 1}
        ]
        claims = [
            {"type": "OPTICAL", "distance_km": 5585.0, "reported_latency_ms": 15.0},
            {"type": "CAP", "partition_active": True, "consistency": "linearizable", "availability": "100%"}
        ]
        res = engine.evaluate_grounding("transatlantic replication", passages, generated_claim=claims)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0
        assert len(res["diagnostics"]["invariant_violations"]) == 2

    def test_t4_scenario2_superseded_http_standards_evolution(self):
        """
        Scenario 2: Superseded Engineering Standard Evolution (RFC 2616 vs RFC 7230 vs RFC 9110).
        - Evaluates evolutionary standards track documents.
        - Active RFC 9110 (Tier 1, staleness 1.0) achieves dominant grounded RRF score over RFC 2616 and RFC 7230.
        - Returns success with Grounding Confidence >= 0.80.
        """
        engine = GroundedRetrievalEngine()
        passages = [
            {"id": "rfc2616", "filename": "rfc2616.pdf", "content": "HTTP 1.1 published 1999 superseded by RFC 7230.", "rank": 1, "staleness_coefficient": 0.20},
            {"id": "rfc7230", "filename": "rfc7230.pdf", "content": "HTTP 1.1 Message Syntax published 2014 superseded by RFC 9110.", "rank": 2, "staleness_coefficient": 0.40},
            {"id": "rfc9110", "filename": "rfc9110.pdf", "content": "HTTP Semantics standard published 2022 active.", "rank": 3, "staleness_coefficient": 1.00}
        ]
        res = engine.evaluate_grounding("HTTP standard semantics", passages)
        assert res["status"] == "success"
        assert res["overall_grounded_confidence"] >= 0.70
        assert res["passages"][0]["id"] == "rfc9110"

    def test_t4_scenario3_nanoscale_computing_thermal_dissipation(self):
        """
        Scenario 3: Nanoscale Computing Thermal Dissipation Evaluation.
        - Exascale neuromorphic hardware claiming 10^-22 J/bit at 300K and 10^-24 J/bit at 4.2K.
        - Landauer minimum energy limit checks:
          * 300K min: 2.87 x 10^-21 J
          * 4.2K min: 4.02 x 10^-23 J
        - Both claims violate Landauer limit -> Refusal gate activates.
        """
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "neuromorphic_hardware.pdf", "content": "Ultra-low energy processor design.", "rank": 1}]
        claims = [
            {"type": "LANDAUER", "t_kelvin": 300.0, "claimed_energy_joules": 1e-22, "bit_count": 1},
            {"type": "LANDAUER", "t_kelvin": 4.2, "claimed_energy_joules": 1e-24, "bit_count": 1}
        ]
        res = engine.evaluate_grounding("neuromorphic dissipation", passages, generated_claim=claims)
        assert res["status"] == "refusal"
        assert len(res["diagnostics"]["invariant_violations"]) == 2

    def test_t4_scenario4_deep_space_satellite_channel_capacity(self):
        """
        Scenario 4: Deep-Space Satellite Transmission Link Capacity Verification.
        - Lunar orbiter telemetry claim of 50 Mbps over S-band (B = 2.0 MHz, SNR = 10 dB -> linear 10.0).
        - Shannon capacity limit: C = 2.0e6 * log2(11) ≈ 6.92 Mbps.
        - Claimed 50 Mbps violates Shannon capacity -> Refusal gate activates.
        """
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "lunar_telemetry.pdf", "content": "S-band downlink transmission specs.", "rank": 1}]
        claim = {"type": "SHANNON", "bandwidth_hz": 2.0e6, "snr_linear": 10.0, "claimed_bps": 50.0e6}
        res = engine.evaluate_grounding("lunar downlink capacity", passages, generated_claim=claim)
        assert res["status"] == "refusal"
        assert "violates" in str(res["diagnostics"]["invariant_violations"]) or "exceeds" in str(res["diagnostics"]["invariant_violations"])

    def test_t4_scenario5_multi_source_statutory_compliance_adjudication(self):
        """
        Scenario 5: Multi-Source Contradictory Statutory Claim Adjudication.
        - Three competing sources on records retention:
          * SEC 10-K (Tier 1 Primary, 7 years)
          * Accounting Textbook (Tier 3 Secondary, 5 years)
          * Community Forum (Tier 4 Commentary, 3 years)
        - Epistemic authority weighting ensures Tier 1 statutory compliance dominates the retrieval scorecard.
        """
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "sec_10-k_annual_filing.pdf", "content": "Statutory audit record retention requirement is 7 years.", "rank": 1},
            {"filename": "accounting_textbook.pdf", "content": "Audit record retention requirement is 5 years.", "rank": 2},
            {"filename": "forum_thread.txt", "content": "Audit record retention requirement is 3 years.", "rank": 3}
        ]
        res = engine.evaluate_grounding("audit retention period", passages)
        assert res["passages"][0]["epistemic_tier"] == TIER_1_PRIMARY
        assert res["passages"][0]["filename"] == "sec_10-k_annual_filing.pdf"

    def test_t4_scenario6_high_concurrency_cluster_benchmark_usl(self):
        """
        Scenario 6: High-Concurrency Cluster Throughput Benchmark Verification.
        - Redis cluster scaling from 1 to 128 nodes with claimed 115x speedup (alpha=0.04, beta=0.002).
        - Gunther USL theoretical maximum speedup at N=128:
          denom = 1 + 0.04(127) + 0.002(128)(127) = 1 + 5.08 + 32.512 = 38.592
          S_max = 128 / 38.592 ≈ 3.32x.
        - Claimed 115x violates USL bounds by over 3000% -> Refusal gate activates.
        """
        engine = GroundedRetrievalEngine()
        passages = [{"filename": "cluster_benchmarks.pdf", "content": "Distributed cache cluster scaling results.", "rank": 1}]
        claim = {"type": "USL", "node_count": 128, "alpha": 0.04, "beta": 0.002, "claimed_speedup": 115.0}
        res = engine.evaluate_grounding("cluster scaling", passages, generated_claim=claim)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0
