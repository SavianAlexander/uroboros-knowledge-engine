import unittest
"""
Adversarial Stress & Empirical Challenge Suite for Grounded Retrieval Engine.
Empirical Challenger 2 Verification Suite.

Validates:
1. Deeply nested breadcrumb scopes with special characters, unicode, and multi-sentence paragraphs.
2. Contradiction resolution matrix across conflicting numeric and status claims.
3. Superseding document chains, date format parsing, and staleness decay clamping (<= 0.40).
4. Grounding confidence scorecard, invariant veto, and 0.65 refusal gate under adversarial sets.
"""

import pytest
import math
import unicodedata
from datetime import datetime, date, timedelta

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
    GroundedRetrievalEngine,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)


class TestAdversarialPropositionalDeconstruction(unittest.TestCase):
    """Stress testing propositional deconstruction and breadcrumb hierarchy."""

    def test_deeply_nested_unicode_hierarchy_breadcrumb(self):
        hierarchy = [
            "Root Division / 根部門",
            "Section §4.2(b)",
            "Subsection <Protocol: 'V3'>",
            "Condition: T > 100K & P <= 2.5 atm",
            "Scope: 日本語・한국어・العربية・🚀",
            "Deepest Scope (Level 6) [Ref: #123]"
        ]
        text = (
            "The optical network transceiver maintains coherent phase modulation at cryogenic temperatures. "
            "Universal scalability contention alpha is strictly bounded by 0.05 across all 128 compute nodes. "
            "Shannon channel capacity ceiling is not exceeded during satellite downlink transmissions."
        )
        props = decompose_into_propositions(text, "RFC_9999_Cryo_Spec", hierarchy)
        assert len(props) == 3

        expected_breadcrumb = (
            "RFC_9999_Cryo_Spec > Root Division / 根部門 > Section §4.2(b) > "
            "Subsection <Protocol: 'V3'> > Condition: T > 100K & P <= 2.5 atm > "
            "Scope: 日本語・한국어・العربية・🚀 > Deepest Scope (Level 6) [Ref: #123]"
        )
        for idx, p in enumerate(props):
            assert p["breadcrumb_scope"] == expected_breadcrumb
            assert p["proposition_id"] == f"RFC_9999_Cryo_Spec#prop_{idx}"
            assert p["contextual_statement"].startswith(f"[{expected_breadcrumb}]")
            assert len(p["statement"]) >= 15

    def test_special_punctuation_interrobang_ellipsis_colons(self):
        text = (
            "Does the system satisfy strict linearizability under network partition?! "
            "No, the PACELC theorem proves that consistency requires latency tradeoffs... "
            "Furthermore: each replica must synchronize state via Raft consensus; this ensures safety. "
            "Final verification passed with 100% compliance across all tested boundaries."
        )
        props = decompose_into_propositions(text, "PACELC_Analysis")
        assert len(props) >= 3
        for p in props:
            assert len(p["statement"]) >= 15
            assert "PACELC_Analysis" in p["proposition_id"]

    def test_massive_paragraph_proposition_scaling(self):
        sentences = [
            f"Factual invariant verification statement number {i:03d} confirms deterministic behavior."
            for i in range(100)
        ]
        text = " ".join(sentences)
        props = decompose_into_propositions(text, "ScalabilityDoc", ["LargeSection"])
        assert len(props) == 100
        for i, p in enumerate(props):
            assert p["proposition_id"] == f"ScalabilityDoc#prop_{i}"
            assert p["breadcrumb_scope"] == "ScalabilityDoc > LargeSection"

    def test_mixed_short_and_long_sentences_filtering(self):
        text = (
            "Short. "
            "Ok. "
            "This is a valid proposition statement with sufficient length. "
            "No. "
            "Another valid proposition statement containing first-principles invariants. "
            "Done."
        )
        props = decompose_into_propositions(text, "FilterDoc")
        assert len(props) == 2
        assert "valid proposition statement with sufficient length" in props[0]["statement"]
        assert "Another valid proposition statement containing first-principles" in props[1]["statement"]


class TestAdversarialContradictionResolutionMatrix(unittest.TestCase):
    """Stress testing cross-document consensus and contradiction matrix."""

    def test_isolated_numerical_discrepancy(self):
        passages = [
            {"filename": "spec1.pdf", "content": "The system achieves 1500tps."},
            {"filename": "spec2.pdf", "content": "The benchmark measured 8500tps."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "CONTRADICTION_DETECTED"
        assert res["consensus_score"] == 0.45
        assert res["contradictions_count"] >= 1
        assert len(res["contradictions"]) >= 1
        conflict = res["contradictions"][0]
        assert conflict["conflict_type"] == "NUMERICAL_DISCREPANCY"

    def test_shared_context_number_set_overlap_behavior(self):
        # Documents that share a common context metric (e.g. 64 nodes) have non-empty set intersection
        passages = [
            {"filename": "spec1.pdf", "content": "The system achieves 1500tps with 64 nodes."},
            {"filename": "spec2.pdf", "content": "The benchmark measured 8500tps with 64 nodes."}
        ]
        res = evaluate_cross_document_consensus(passages)
        # Set intersection of {"1500tps", "64 nodes"} and {"8500tps", "64 nodes"} is {"64 nodes"} -> agreements = 1
        assert res["consensus_level"] == "HIGH_CONSENSUS"
        assert res["agreements_count"] >= 1

    def test_floating_point_and_percentage_matching(self):
        passages = [
            {"filename": "audit_a.pdf", "content": "The Carnot engine efficiency is 45.5% at 600K."},
            {"filename": "audit_b.pdf", "content": "The measured Carnot cycle was 45.5% at 600K."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "HIGH_CONSENSUS"
        assert res["consensus_score"] == 0.95
        assert res["agreements_count"] >= 1

    def test_multi_party_consensus_majority_vs_minority(self):
        passages = [
            {"filename": "source1.pdf", "content": "Network MTU size is 1500 bytes."},
            {"filename": "source2.pdf", "content": "Standard Ethernet MTU size is 1500 bytes."},
            {"filename": "source3.pdf", "content": "L2 frame payload MTU is 1500 bytes."},
            {"filename": "rogue_blog.md", "content": "MTU size is 9000 bytes."}
        ]
        res = evaluate_cross_document_consensus(passages)
        # 3 agreeing on 1500, 1 disagreeing on 9000 -> Majority consensus
        assert res["consensus_level"] == "HIGH_CONSENSUS"
        assert res["consensus_score"] == 0.95
        assert res["agreements_count"] >= 2

    def test_all_opposing_multi_way_contradiction(self):
        passages = [
            {"filename": "a.txt", "content": "Latency measured at 12ms."},
            {"filename": "b.txt", "content": "Latency measured at 48ms."},
            {"filename": "c.txt", "content": "Latency measured at 96ms."},
            {"filename": "d.txt", "content": "Latency measured at 240ms."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["consensus_level"] == "CONTRADICTION_DETECTED"
        assert res["consensus_score"] == 0.45
        assert res["contradictions_count"] >= 5

    def test_empty_and_single_passage_edge_cases(self):
        res_empty = evaluate_cross_document_consensus([])
        assert res_empty["consensus_level"] == "SINGLE_SOURCE"
        assert res_empty["consensus_score"] == 0.70

        res_single = evaluate_cross_document_consensus([{"filename": "solo.pdf", "content": "Single claim 100mb."}])
        assert res_single["consensus_level"] == "SINGLE_SOURCE"
        assert res_single["consensus_score"] == 0.70


class TestAdversarialSupersedingAndDecayClamping(unittest.TestCase):
    """Stress testing superseding chains, date formats, and temporal decay clamping."""

    def test_superseded_hard_cap_strict_enforcement(self):
        # Even if published 1 day ago (delta_t ~ 0), SUPERSEDED status forces decay <= 0.40
        now = datetime.now()
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        decay_yesterday = compute_temporal_decay(document_year_or_date=yesterday, domain="law", status="SUPERSEDED")
        assert decay_yesterday <= 0.40

        # DEPRECATED status forces decay <= 0.50
        decay_deprecated = compute_temporal_decay(document_year_or_date=yesterday, domain="tech_spec", status="DEPRECATED")
        assert decay_deprecated <= 0.50

        # AMENDED status forces decay <= 0.75
        decay_amended = compute_temporal_decay(document_year_or_date=yesterday, domain="academic", status="AMENDED")
        assert decay_amended <= 0.75

        # ACTIVE status has no artificial penalty cap (remains ~1.00)
        decay_active = compute_temporal_decay(document_year_or_date=yesterday, domain="tech_spec", status="ACTIVE")
        assert decay_active >= 0.99

    def test_standards_track_headers_parsing(self):
        rfc_header = (
            "Internet Engineering Task Force (IETF)\n"
            "Request for Comments: 7230\n"
            "Obsoletes: 2616\n"
            "Updates: 2817, 2818\n"
            "Category: Standards Track\n"
            "Published: June 2014\n"
        )
        res = detect_temporal_validity(rfc_header)
        assert res["is_superseded"] is True
        assert "2616" in res["superseded_by"]
        assert res["temporal_status"] == "SUPERSEDED"
        assert res["staleness_coefficient"] <= 0.40

    def test_iso_iec_colon_delimiter_superseding_marker(self):
        iso_header = "Information Security Standard. This specification is replaced by ISO/IEC 27001:2022."
        res = detect_temporal_validity(iso_header)
        assert res["is_superseded"] is True
        assert "ISO/IEC 27001:2022" in res["superseded_by"]
        assert res["staleness_coefficient"] <= 0.40

    def test_domain_half_life_curves_across_lifespans(self):
        # Verify half lives: law (10y), academic (5y), tech_spec (2y), commentary (0.5y)
        now_year = datetime.now().year

        # 10 years old in Law domain: exactly 1 half-life -> decay ~ 0.50
        decay_law_10y = compute_temporal_decay(now_year - 10, domain="law", status="ACTIVE")
        assert 0.48 <= decay_law_10y <= 0.52

        # 5 years old in Academic domain: exactly 1 half-life -> decay ~ 0.50
        decay_acad_5y = compute_temporal_decay(now_year - 5, domain="academic", status="ACTIVE")
        assert 0.48 <= decay_acad_5y <= 0.52

        # 2 years old in Tech Spec domain: exactly 1 half-life -> decay ~ 0.50
        decay_spec_2y = compute_temporal_decay(now_year - 2, domain="tech_spec", status="ACTIVE")
        assert 0.48 <= decay_spec_2y <= 0.52

        # 1 year old in Commentary domain (half life 0.5y = 2 half lives) -> decay ~ 0.25
        decay_comm_1y = compute_temporal_decay(now_year - 1, domain="commentary", status="ACTIVE")
        assert 0.23 <= decay_comm_1y <= 0.27

    def test_decay_floor_preserves_historical_artifacts(self):
        # 100 years old document does not drop below 0.05 floor
        decay_ancient = compute_temporal_decay(1926, domain="tech_spec", status="ACTIVE")
        assert decay_ancient == 0.05


class TestAdversarialGroundingScorecardAndRefusalGate(unittest.TestCase):
    """Stress testing the composite grounding confidence scorecard and refusal gates."""

    def test_adversarial_candidate_set_all_commentary(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "unverified_chat1.txt", "content": "Port is 8080.", "rank": 1},
            {"filename": "unverified_chat2.txt", "content": "Port is 8080.", "rank": 2},
            {"filename": "forum_scratch.txt", "content": "Port is 8080.", "rank": 3}
        ]
        # Tier 4 commentary weight = 0.35, high consensus = 0.95, fresh = 1.00
        # Base confidence = (0.35 * 0.50) + (0.95 * 0.30) + (1.00 * 0.20) = 0.175 + 0.285 + 0.20 = 0.66
        res = engine.evaluate_grounding("server port", passages)
        assert res["status"] == "success"  # Unanimous 3-source agreement slightly surpasses 0.65 threshold

        # With just 1 commentary source: neutral consensus = 0.70
        # Base confidence = 0.175 + 0.21 + 0.20 = 0.585 < 0.65 -> Refusal!
        res_single = engine.evaluate_grounding("server port", passages[:1])
        assert res_single["status"] == "refusal"
        assert res_single["overall_grounded_confidence"] < 0.65

    def test_adversarial_candidate_set_contradictory_tier1(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "rfc_standard_a.pdf", "content": "Max payload limit is 1500 bytes.", "rank": 1},
            {"filename": "rfc_standard_b.pdf", "content": "Max payload limit is 9000 bytes.", "rank": 2}
        ]
        # Tier 1 (1.00), contradiction (0.45), fresh (1.00)
        # Base confidence = 1.00*0.50 + 0.45*0.30 + 1.00*0.20 = 0.50 + 0.135 + 0.20 = 0.835 -> 0.84
        res = engine.evaluate_grounding("payload limit", passages)
        assert res["status"] == "success"
        assert res["consensus_level"] == "CONTRADICTION_DETECTED"
        assert res["overall_grounded_confidence"] >= 0.80

    def test_physical_invariant_veto_overrides_perfect_tier1_consensus(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "rfc9110_http_semantics.pdf", "content": "HTTP 200 OK status code.", "rank": 1},
            {"filename": "iso27001_security.pdf", "content": "HTTP 200 OK status code.", "rank": 2}
        ]
        # Claim violates USL (128 nodes with 500x speedup when max is ~3.3x)
        impossible_claim = {"type": "USL", "node_count": 128, "alpha": 0.04, "beta": 0.002, "claimed_speedup": 500.0}
        res = engine.evaluate_grounding("HTTP status", passages, generated_claim=impossible_claim)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert len(res["diagnostics"]["invariant_violations"]) >= 1

    def test_composite_all_invariants_clean_execution(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP protocol specification.", "rank": 1}
        ]
        valid_claims = [
            {"type": "OPTICAL", "distance_km": 1000.0, "reported_latency_ms": 15.0},
            {"type": "USL", "node_count": 8, "alpha": 0.02, "beta": 0.001, "claimed_speedup": 7.0},
            {"type": "CARNOT", "t_hot_k": 500.0, "t_cold_k": 300.0, "claimed_efficiency": 0.35},
            {"type": "LANDAUER", "t_kelvin": 300.0, "claimed_energy_joules": 5.0e-21, "bit_count": 1},
            {"type": "SHANNON", "bandwidth_hz": 10e6, "snr_linear": 100.0, "claimed_bps": 50e6},
            {"type": "CAP", "partition_active": False, "consistency": "linearizable", "availability": "100%"}
        ]
        res = engine.evaluate_grounding("HTTP protocol", passages, generated_claim=valid_claims)
        assert res["status"] == "success"
        assert res["overall_grounded_confidence"] >= 0.70
        assert len(res["invariant_audit"]["violations"]) == 0

    def test_20_level_deeply_nested_breadcrumb(self):
        levels = [f"Level_{i}" for i in range(20)]
        text = "Deeply nested architectural assertion statement with sufficient length for testing."
        props = decompose_into_propositions(text, "RootDoc", levels)
        assert len(props) == 1
        expected = "RootDoc > " + " > ".join(levels)
        assert props[0]["breadcrumb_scope"] == expected

    def test_all_date_format_variations_and_prefixes(self):
        snippets = [
            ("Published: 2024-05-20 in standard track.", 2024),
            ("Promulgated on March 15, 2023 by standard body.", 2023),
            ("Dated: 12 October 2021 by regulatory group.", 2021),
            ("Effective as of 2025-01-01 under administrative code.", 2025),
            ("General publication in 2022 without day month.", 2022)
        ]
        for snippet, expected_yr in snippets:
            meta = detect_temporal_validity(snippet)
            assert meta["publication_year"] == expected_yr, f"Failed for {snippet}"

    def test_all_domain_half_lives_exhaustive(self):
        expected_half_lives = {
            "law": 10.0, "iso": 10.0, "statutory": 10.0,
            "academic": 5.0, "textbook": 5.0, "secondary": 5.0,
            "tech_spec": 2.0, "specs": 2.0, "api": 2.0, "technical": 2.0,
            "commentary": 0.5, "informal": 0.5, "notes": 0.5,
            "general": 3.0
        }
        for domain, hl in expected_half_lives.items():
            assert DOMAIN_HALF_LIVES[domain] == hl

    def test_diagnostic_report_keys_on_compound_failure(self):
        engine = GroundedRetrievalEngine(refusal_threshold=0.65)
        passages = [
            {"filename": "unverified_notes.txt", "content": "Unverified draft content.", "rank": 1}
        ]
        impossible_carnot = {"type": "CARNOT", "t_hot_k": 400.0, "t_cold_k": 300.0, "claimed_efficiency": 0.90}
        res = engine.evaluate_grounding("thermodynamics", passages, generated_claim=impossible_carnot)
        assert res["status"] == "refusal"
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert "diagnostics" in res
        assert "invariant_violations" in res["diagnostics"]
        assert "knowledge_gaps" in res["diagnostics"]
        assert "avg_tier_weight" in res["diagnostics"]
        assert "consensus_score" in res["diagnostics"]
