import unittest
"""
Tier 5 Adversarial Verification & Stress Test Suite for Grounded Retrieval & Consensus Matrix Engine.
Milestone M6 Final Verification Suite.

Comprehensive white-box edge case mining, boundary value stress, fuzz-like input robustness,
numerical under/overflow, unicode/special char resilience, and multi-invariant attack scenarios.
"""

import pytest
import math
import unicodedata
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

from src.domain.grounded_retrieval_engine import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    detect_temporal_validity,
    compute_temporal_decay,
    decompose_into_propositions,
    expand_propositions_to_parent_context,
    format_breadcrumb_scope,
    evaluate_cross_document_consensus,
    extract_document_assertions,
    compute_consensus_boost,
    resolve_contradiction_hierarchy,
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
    compute_grounding_scorecard,
    generate_knowledge_gap_diagnostic_report,
    execute_grounded_retrieval,
    evaluate_grounding_for_claim,
    GroundedRetrievalEngine,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS,
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
    TIER_4_UNRESOLVABLE,
    REFUSAL_THRESHOLD,
    STATUS_ACCEPTED,
    STATUS_REFUSED,
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


# ==============================================================================
# 1. EPISTEMIC TIERING & RRF FUSION ADVERSARIAL STRESS
# ==============================================================================
class TestTier5EpistemicTieringAdversarial(unittest.TestCase):
    """Adversarial stress tests for epistemic tiering and mathematical RRF fusion."""

    def test_null_empty_and_non_string_filenames(self):
        """Test resilience against None, empty, whitespace, and non-string inputs."""
        assert classify_source_epistemic_tier(None) == (TIER_4_COMMENTARY, 0.35)
        assert classify_source_epistemic_tier("") == (TIER_4_COMMENTARY, 0.35)
        assert classify_source_epistemic_tier("   \t\n  ") == (TIER_4_COMMENTARY, 0.35)
        assert classify_source_epistemic_tier(12345) == (TIER_4_COMMENTARY, 0.35)
        assert classify_source_epistemic_tier(["rfc9110.pdf"]) == (TIER_1_PRIMARY, 1.00)

    def test_extreme_filename_lengths_and_deep_traversal(self):
        """Test massive paths (>10,000 characters) and complex traversal delimiters."""
        deep_path = "C:/" + "/".join(["nested_dir"] * 500) + "/iso27001_standard.pdf"
        tier, weight = classify_source_epistemic_tier(deep_path)
        assert tier == TIER_1_PRIMARY
        assert weight == 1.00

        massive_name = "a" * 20000 + "_rfc9110.txt"
        t, w = classify_source_epistemic_tier(massive_name)
        assert t == TIER_1_PRIMARY
        assert w == 1.00

    def test_adversarial_commentary_masking_with_standards_keywords(self):
        """Ensure commentary files citing standards are strictly locked to Tier 4."""
        tricky_filenames = [
            "blog_about_rfc9110_and_iso27001.txt",
            "scratch_notes_on_sec_10-k_filing.md",
            "chat_discussion_regarding_18_usc_1030.log",
            "memo_unverified_ieee802_draft.txt",
            "forum_commentary_on_iec62443.html",
            "draft_notes_on_merkle_provenance.txt",
            "todo_notes_review_statute_cfr.txt"
        ]
        for name in tricky_filenames:
            tier, weight = classify_source_epistemic_tier(name, content_snippet="Strictly citing RFC 9110 and 18 U.S.C. 1030")
            assert tier == TIER_4_COMMENTARY, f"Failed commentary lockdown for {name}"
            assert weight == 0.35

    def test_mixed_slash_and_unicode_normalization(self):
        """Test mixed Windows/Unix backslashes and unicode combining characters."""
        path = "vault\\specs/sub_spec\\api_specification_v2.json"
        tier, weight = classify_source_epistemic_tier(path)
        assert tier == TIER_1_PRIMARY  # .json extension takes Tier 1 priority
        assert weight == 1.00

        unicode_name = unicodedata.normalize("NFD", "tèxtboôk_comp_sci_handbook.pdf")
        tier_u, weight_u = classify_source_epistemic_tier(unicode_name)
        assert tier_u == TIER_3_SECONDARY
        assert weight_u == 0.70

    def test_metadata_override_type_corruptions(self):
        """Test metadata override dictionary with invalid weights, strings, and types."""
        # Valid override
        t1, w1 = classify_source_epistemic_tier("arbitrary.txt", metadata={"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 0.99})
        assert t1 == "TIER_1_PRIMARY"
        assert w1 == 0.99

        # Corrupted weight string falls back to standard tier weight
        t2, w2 = classify_source_epistemic_tier("arbitrary.txt", metadata={"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": "corrupted_nan"})
        assert t2 == "TIER_2_TECH_SPEC"
        assert w2 == 0.85

        # Unknown tier in metadata falls back to filename/content classifier
        t3, w3 = classify_source_epistemic_tier("rfc793_tcp.txt", metadata={"epistemic_tier": "UNKNOWN_TIER_99"})
        assert t3 == TIER_1_PRIMARY
        assert w3 == 1.00

    def test_rrf_with_extreme_k_and_intent_weights(self):
        """Test RRF algorithm behavior with edge-case k smoothing constants and weights."""
        lex = [{"id": "doc1", "filename": "rfc9110.pdf", "rank": 1}]
        dense = [{"id": "doc1", "filename": "rfc9110.pdf", "rank": 1}]

        # Non-positive or zero k must be safely clamped to k >= 1
        res_zero_k = compute_authority_weighted_rrf(lex, dense, k=0)
        assert len(res_zero_k) == 1
        assert res_zero_k[0]["normalized_score"] > 0

        res_neg_k = compute_authority_weighted_rrf(lex, dense, k=-100)
        assert len(res_neg_k) == 1
        assert res_neg_k[0]["normalized_score"] > 0

        # Extreme intent weights
        res_zero_weights = compute_authority_weighted_rrf(lex, dense, intent_weights={"lexical": 0.0, "dense": 0.0})
        assert len(res_zero_weights) == 1
        assert res_zero_weights[0]["grounded_score"] > 0

        res_unbalanced = compute_authority_weighted_rrf(lex, dense, intent_weights={"lexical": 1000.0, "dense": 1.0})
        assert len(res_unbalanced) == 1

    def test_rrf_large_scale_candidate_pool(self):
        """Test RRF ranking stability and monotonicity over a 200-item candidate pool."""
        lex_candidates = [
            {"id": f"doc_{i}", "filename": f"doc_{i}_notes.txt", "rank": i + 1}
            for i in range(200)
        ]
        # Insert a high-tier spec deep in lexical search
        lex_candidates[150] = {"id": "doc_150", "filename": "rfc9110_http_semantics.pdf", "rank": 151}

        fused = compute_authority_weighted_rrf(lexical_ranks=lex_candidates, dense_ranks=[], k=60)
        assert len(fused) == 200
        # Ensure scores are strictly monotonically ordered
        for idx in range(len(fused) - 1):
            assert fused[idx]["grounded_score"] >= fused[idx + 1]["grounded_score"]
            assert fused[idx]["final_rank"] == idx + 1


# ==============================================================================
# 2. TEMPORAL VALIDITY & STALENESS DECAY ADVERSARIAL STRESS
# ==============================================================================
class TestTier5TemporalDecayAdversarial(unittest.TestCase):
    """Adversarial stress tests for temporal validity, superseding markers, and exponential decay."""

    def test_far_future_and_ancient_dates(self):
        """Test temporal decay handling of future dates and historical millennia."""
        # Future date (delta_t <= 0) should yield decay factor 1.00 (no decay)
        future_decay = compute_temporal_decay(document_year_or_date=2099, domain="tech_spec")
        assert future_decay == 1.00

        # Ancient date (e.g. year 1800) must hit the floor of 0.05 and not go to 0 or negative
        ancient_decay = compute_temporal_decay(document_year_or_date=1800, domain="tech_spec")
        assert ancient_decay == 0.05

    def test_decay_monotonicity_across_all_domains(self):
        """Verify strict exponential decay monotonicity across 50 continuous yearly intervals."""
        domains = ["law", "iso", "academic", "tech_spec", "commentary", "general"]
        current_year = datetime.now().year

        for dom in domains:
            prev_decay = 1.05
            for age in range(0, 50):
                yr = current_year - age
                d = compute_temporal_decay(document_year_or_date=yr, domain=dom)
                assert d <= prev_decay + 1e-6, f"Monotonicity violation in domain {dom} at age {age}: {d} > {prev_decay}"
                assert 0.05 <= d <= 1.00
                prev_decay = d

    def test_malformed_and_ambiguous_date_strings(self):
        """Test resilience against irregular, corrupt, or multiple date occurrences."""
        texts = [
            "Published in 1998, amended 2004, superseded in 2012 by RFC 7230, reviewed 2024.",
            "Effective as of February 29, 2020 (Leap Year Edition).",
            "Dated 31 December 1999 23:59:59.",
            "Random string with no valid dates: 99999-99-99 and 0000-00-00.",
            ""
        ]
        for t in texts:
            info = detect_temporal_validity(t)
            assert isinstance(info, dict)
            assert "staleness_coefficient" in info
            assert 0.05 <= info["staleness_coefficient"] <= 1.00

    def test_chained_superseding_markers(self):
        """Test multi-hop superseding and deprecation markers in document headers."""
        header_text = (
            "RFC 2616 - Hypertext Transfer Protocol -- HTTP/1.1\n"
            "Obsoletes: RFC 2068\n"
            "Obsoleted by: RFC 7230, RFC 7231, RFC 7232, RFC 7233, RFC 7234, RFC 7235\n"
            "Updates: RFC 2817\n"
            "Status: SUPERSEDED\n"
            "Date: June 1999"
        )
        info = detect_temporal_validity(header_text)
        assert info["is_superseded"] is True
        assert info["temporal_status"] == "SUPERSEDED"
        assert info["staleness_coefficient"] <= STATUS_PENALTY_CAPS["SUPERSEDED"]
        assert "7230" in str(info["superseded_by"])

    def test_half_life_override_extremes(self):
        """Test explicit half_life_days parameter with sub-day, minimum clamped, and multi-century values."""
        now = datetime.now()
        # 1-year-old document with 0.1 year (~36.5 days) half life -> exp(-10 * ln2) ~ 0.00097 -> floor 0.05
        one_year_ago_date = (now - timedelta(days=366)).date()
        fast_decay = compute_temporal_decay(document_year_or_date=one_year_ago_date, half_life_days=36.525)
        assert fast_decay == 0.05

        # 10-day-old document with sub-month half-life (guarded by 0.1 year / ~36.5 day minimum half-life clamp)
        ten_days_ago_date = (now - timedelta(days=10)).date()
        clamped_decay = compute_temporal_decay(document_year_or_date=ten_days_ago_date, half_life_days=1.0)
        assert 0.80 <= clamped_decay <= 0.85

        # 100,000-day half-life (~273 years) on a 10-year-old document
        slow_decay = compute_temporal_decay(document_year_or_date=now.year - 10, half_life_days=100000.0)
        assert slow_decay >= 0.95


# ==============================================================================
# 3. DENSE PROPOSITIONS & BREADCRUMB ADVERSARIAL STRESS
# ==============================================================================
class TestTier5DensePropositionsAdversarial(unittest.TestCase):
    """Adversarial stress tests for propositional deconstruction and breadcrumbs."""

    def test_decimal_ip_address_and_url_preservation(self):
        """Verify that decimals, IPv4/IPv6 addresses, URLs, and code dots are not split."""
        text = (
            "The cluster controller at 192.168.1.100 communicates via protocol v2.5.4 over https://api.neuro.internal:8080/v1/sync. "
            "Pi is approximately 3.1415926535 and Euler's number is 2.71828. "
            "Memory usage reached 99.9% while processing 10.5 GB of log data."
        )
        props = decompose_into_propositions(text, "NetworkingDoc")
        assert len(props) == 3
        # Check that IP address and URLs remain intact
        assert "192.168.1.100" in props[0]["statement"]
        assert "https://api.neuro.internal:8080/v1/sync" in props[0]["statement"]
        assert "3.1415926535" in props[1]["statement"]
        assert "99.9%" in props[2]["statement"]

    def test_chaotic_markdown_heading_nesting(self):
        """Test heading tree parser with chaotic jump depths (H1 -> H6 -> H2 -> H4 -> H1)."""
        markdown_text = (
            "# Main Title (H1)\n"
            "Introduction statement to the architectural principles.\n"
            "###### Deep Subsection (H6)\n"
            "Very deep isolated technical note in section 6.\n"
            "## Architecture Overview (H2)\n"
            "Overview statement of the system components.\n"
            "#### Component Details (H4)\n"
            "Detailed specification of the consensus engine.\n"
            "# Concluding Summary (H1)\n"
            "Final summarizing statement of the entire specification."
        )
        props = decompose_into_propositions(markdown_text, "SpecDoc")
        assert len(props) >= 5

        # Check breadcrumb stacks
        h6_prop = [p for p in props if "Deep Subsection" in p["breadcrumb_scope"]][0]
        assert "Main Title (H1) > Deep Subsection (H6)" in h6_prop["breadcrumb_scope"]

        h4_prop = [p for p in props if "Component Details" in p["breadcrumb_scope"]][0]
        assert "Architecture Overview (H2) > Component Details (H4)" in h4_prop["breadcrumb_scope"]

        h1_final = [p for p in props if "Concluding Summary" in p["breadcrumb_scope"]][0]
        assert h1_final["breadcrumb_scope"] == "SpecDoc > Concluding Summary (H1)"

    def test_adversarial_abbreviations_and_latinates(self):
        """Test that common technical, legal, and academic abbreviations are handled properly."""
        text = (
            "Pursuant to 18 U.S. sec. 1030 et al., the defendant was charged. "
            "See Fig. 4.2 vs. Fig. 4.3 in reference layout for the circuit board. "
            "Dr. Smith and Mr. Doe met at 9:00 a.m. at Corp. Inc. headquarters. "
            "The algorithm supports e.g. SQLite, i.e. local SQL engines etc. with zero latency."
        )
        props = decompose_into_propositions(text, "LegalBrief")
        assert len(props) == 4
        assert "18 U.S. sec. 1030 et al." in props[0]["statement"]
        assert "Fig. 4.2 vs. Fig. 4.3" in props[1]["statement"]
        assert "Dr. Smith and Mr. Doe" in props[2]["statement"]
        assert "e.g. SQLite, i.e. local SQL engines etc." in props[3]["statement"]

    def test_parent_context_expansion_mock_database(self):
        """Test parent context window extraction around proposition statements."""
        class MockCursor:
            def execute(self, query, params=()):
                pass
            def fetchone(self):
                return ("This is the surrounding parent documentation block. The Landauer limit sets minimum energy for bit erasure in irreversible computation. This is additional trailing context.",)

        class MockConnection:
            def cursor(self):
                return MockCursor()

        props = [
            {
                "proposition_id": "doc1#prop_0",
                "file_id": 101,
                "statement": "The Landauer limit sets minimum energy for bit erasure",
                "contextual_statement": "[Thermo > Section 1] The Landauer limit sets minimum energy for bit erasure",
                "breadcrumb_scope": "Thermo > Section 1"
            }
        ]
        expanded = expand_propositions_to_parent_context(props, db_connection=MockConnection())
        assert len(expanded) == 1
        assert expanded[0]["has_parent_context"] is True
        assert "Landauer limit" in expanded[0]["parent_context"]
        assert "surrounding parent" in expanded[0]["parent_context"]


# ==============================================================================
# 4. CROSS-DOCUMENT CONSENSUS & CONTRADICTION MATRIX ADVERSARIAL STRESS
# ==============================================================================
class TestTier5ConsensusMatrixAdversarial(unittest.TestCase):
    """Adversarial stress tests for consensus extraction, pairwise NLI, and 4-tier contradiction resolution."""

    def test_five_way_conflicting_numerical_passages(self):
        """Test multi-source conflict matrix where 5 sources report distinct throughput numbers."""
        passages = [
            {"filename": "spec_v1.md", "content": "The system throughput is 1000 TPS under benchmark.", "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC"}},
            {"filename": "spec_v2.md", "content": "The system throughput is 2000 TPS under benchmark.", "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC"}},
            {"filename": "rfc_standard.txt", "content": "The system throughput is 5000 TPS under benchmark.", "metadata": {"epistemic_tier": "TIER_1_PRIMARY"}},
            {"filename": "blog_post.md", "content": "The system throughput is 500 TPS under benchmark.", "metadata": {"epistemic_tier": "TIER_4_COMMENTARY"}},
            {"filename": "textbook.pdf", "content": "The system throughput is 1500 TPS under benchmark.", "metadata": {"epistemic_tier": "TIER_3_SECONDARY"}}
        ]
        audit = evaluate_cross_document_consensus(passages)
        assert audit["contradictions_count"] >= 4
        assert len(audit["resolved_claims"]) >= 1

        # Check that Tier 1 Primary RFC standard overrules lower tiers
        t1_resolutions = [r for r in audit["resolved_claims"] if r.get("resolution_tier") == TIER_1_EPISTEMIC_DOMINANCE]
        assert len(t1_resolutions) >= 1
        assert any(r["resolved_source"] == "rfc_standard.txt" for r in t1_resolutions)

    def test_unresolvable_epistemic_stalemate_equal_tier_equal_date(self):
        """Test Tier 4 Unresolvable Epistemic Conflict when equal-tier sources clash unconditionally without date difference."""
        passages = [
            {
                "filename": "iso_standard_variant_a.pdf",
                "content": "The maximum encryption key length is 256 bits.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "effective_date": "2024-01-01"}
            },
            {
                "filename": "iso_standard_variant_b.pdf",
                "content": "The maximum encryption key length is 512 bits.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "effective_date": "2024-01-01"}
            }
        ]
        audit = evaluate_cross_document_consensus(passages)
        assert len(audit["dissenting_ledger"]) == 1
        dissent = audit["dissenting_ledger"][0]
        assert dissent["resolution_tier"] == TIER_4_UNRESOLVABLE
        assert dissent["status"] == "UNRESOLVED_EPISTEMIC_CONFLICT"
        assert audit["consensus_level"] == CONTRADICTION_DETECTED
        assert audit["consensus_score"] <= 0.45

    def test_temporal_superseding_resolution_between_rfcs(self):
        """Test Tier 2 Temporal Resolution when older RFC is superseded by newer RFC."""
        passages = [
            {
                "filename": "rfc2616_http11.txt",
                "content": "The default keep-alive timeout is 15 seconds. Obsoleted by RFC 7230.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "publication_year": 1999}
            },
            {
                "filename": "rfc7230_http11.txt",
                "content": "The default keep-alive timeout is 60 seconds.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "publication_year": 2014}
            }
        ]
        audit = evaluate_cross_document_consensus(passages)
        assert len(audit["resolved_claims"]) >= 1
        res = audit["resolved_claims"][0]
        assert res["resolution_tier"] == TIER_2_TEMPORAL_DOMINANCE
        assert res["resolved_source"] == "rfc7230_http11.txt"
        assert res["overruled_source"] == "rfc2616_http11.txt"

    def test_condition_scope_specificity_harmonization(self):
        """Test Tier 3 Condition Scope Harmonization for dual-operating modes."""
        passages = [
            {
                "filename": "engine_spec_read.md",
                "content": "For read operations the query latency is 5 ms.",
                "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC"}
            },
            {
                "filename": "engine_spec_write.md",
                "content": "For write workloads the query latency is 45 ms.",
                "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC"}
            }
        ]
        audit = evaluate_cross_document_consensus(passages)
        assert len(audit["resolved_claims"]) >= 1
        res = audit["resolved_claims"][0]
        assert res["resolution_tier"] == TIER_3_CONDITION_SCOPE
        assert res["status"] == "HARMONIZED_DUAL_SCOPE"
        assert len(res["harmonized_scopes"]) == 2

    def test_polarity_and_status_collision_detection(self):
        """Test polarity / negation and status keyword conflict detection."""
        passages = [
            {"filename": "feature_doc_a.txt", "content": "TLS 1.3 protocol compression is active and production ready."},
            {"filename": "feature_doc_b.txt", "content": "TLS 1.3 protocol compression is deprecated and forbidden due to CRIME attack."}
        ]
        audit = evaluate_cross_document_consensus(passages)
        assert audit["contradictions_count"] >= 1
        conflict_types = [c["conflict_type"] for c in audit["contradictions"]]
        assert CONFLICT_STATUS_COLLISION in conflict_types or CONFLICT_POLARITY_INVERSION in conflict_types


# ==============================================================================
# 5. PHYSICAL & COMPUTATIONAL BOUNDARY INVARIANTS ADVERSARIAL STRESS
# ==============================================================================
class TestTier5BoundaryInvariantsAdversarial(unittest.TestCase):
    """Adversarial stress tests for first-principles physical and computational boundary guards."""

    # --- F7: Speed-of-Light Optical Invariants ---
    def test_optical_antipodal_and_zero_distance(self):
        """Test optical latency checks at exact antipodal points (20,015 km) and zero distance."""
        # 0 km distance with 0 ms latency
        res_zero = check_optical_latency_invariant(distance_km=0.0, reported_latency_ms=0.0)
        assert res_zero["is_physically_possible"] is True

        # Antipodal Earth distance (~20,015 km). Speed in fiber is ~203,940 km/s.
        # One-way min is ~98.14 ms, RTT min is ~196.28 ms.
        antipodal_km = math.pi * 6371.0  # ~20,015.08 km
        res_antipodal_valid = check_optical_latency_invariant(distance_km=antipodal_km, reported_latency_ms=200.0, is_rtt=True)
        assert res_antipodal_valid["is_physically_possible"] is True

        # Claiming 50 ms RTT across antipodal points is superluminal
        res_antipodal_violation = check_optical_latency_invariant(distance_km=antipodal_km, reported_latency_ms=50.0, is_rtt=True)
        assert res_antipodal_violation["is_physically_possible"] is False
        assert res_antipodal_violation["violation_type"] == VIOLATION_SPEED_OF_LIGHT

    def test_optical_refractive_index_sub_unity_tachyonic(self):
        """Test that refractive index n < 1.0 (faster than vacuum c) is rejected as physically impossible."""
        res_tachyonic = check_optical_latency_invariant(distance_km=1000.0, reported_latency_ms=2.0, n_refractive=0.8)
        assert res_tachyonic["is_physically_possible"] is False
        assert "violates special relativity" in res_tachyonic["violation_details"]

    def test_haversine_coordinate_extremes(self):
        """Test Haversine distance from North Pole to South Pole."""
        # Lat 90, Lon 0 to Lat -90, Lon 0 -> exact half circumference (~20,015 km)
        res_polar = check_optical_latency_invariant(lat1=90.0, lon1=0.0, lat2=-90.0, lon2=0.0, reported_latency_ms=10.0, is_rtt=False)
        assert res_polar["is_physically_possible"] is False
        assert res_polar["distance_km"] > 20000.0

    # --- F8: Universal Scalability Law (USL) ---
    def test_usl_massive_concurrency_and_superlinear_veto(self):
        """Test USL at N=1,000,000 nodes and superlinear speedup veto."""
        # N=100 nodes claiming 150x speedup -> superlinear violation
        res_superlinear = check_usl_scalability_invariant(node_count=100, alpha=0.01, beta=0.0001, claimed_speedup=150.0)
        assert res_superlinear["is_computationally_valid"] is False
        assert res_superlinear["violation_type"] == VIOLATION_SUPERLINEAR_SPEEDUP

        # N=1,000,000 nodes with coherency beta=0.001. Peak N* is sqrt((1-0.05)/0.001) ~ 30.8 nodes.
        # Claiming speedup of 100x at N=1,000,000 violates retrograde coherency limit.
        res_massive_retrograde = check_usl_scalability_invariant(node_count=1000000, alpha=0.05, beta=0.001, claimed_speedup=100.0)
        assert res_massive_retrograde["is_computationally_valid"] is False
        assert res_massive_retrograde["violation_type"] == VIOLATION_COHERENCY_RETROGRADE

    def test_usl_invalid_parameter_guards(self):
        """Test USL parameter validation for negative or out-of-range alpha/beta/N."""
        assert check_usl_scalability_invariant(node_count=0)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=-10)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, alpha=1.5)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, alpha=-0.1)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, beta=-0.05)["is_computationally_valid"] is False

    # --- F9: CAP & PACELC Invariants ---
    def test_cap_pacelc_split_brain_and_quorum_deficits(self):
        """Test distributed quorum deficit (R+W <= N) and split-brain (W <= N/2) risks."""
        # 5-node cluster with R=2, W=3 (R+W=5 <= 5) -> quorum deficit
        res_quorum = check_cap_pacelc_invariant({"n_replicas": 5, "r_quorum": 2, "w_quorum": 3, "strong_consistency": True})
        assert res_quorum["is_computationally_valid"] is False
        assert res_quorum["violation_type"] == VIOLATION_QUORUM_DEFICIT

        # 5-node cluster with R=4, W=2 (R+W=6 > 5, but W=2 <= 5/2=2.5) -> split-brain risk
        res_split_brain = check_cap_pacelc_invariant({"n_replicas": 5, "r_quorum": 4, "w_quorum": 2, "strong_consistency": True})
        assert res_split_brain["is_computationally_valid"] is False
        assert res_split_brain["violation_type"] == VIOLATION_SPLIT_BRAIN

        # Cross-region linearizable replication with 0ms latency claim
        res_zero_lat = check_cap_pacelc_invariant({"multi_region": True, "strong_consistency": True, "replication_latency_ms": 0.0})
        assert res_zero_lat["is_computationally_valid"] is False
        assert res_zero_lat["violation_type"] == VIOLATION_PACELC_ZERO_LATENCY

    # --- F10: Carnot & Landauer Thermodynamic Limits ---
    def test_carnot_second_law_violations(self):
        """Test Carnot efficiency upper bounds across various temperature differentials."""
        # Th = 400K, Tc = 300K -> eta_max = 1 - 300/400 = 0.25 (25%)
        # Claiming 26% efficiency violates 2nd law
        res_carnot_viol = check_carnot_efficiency_invariant(t_hot_k=400.0, t_cold_k=300.0, claimed_efficiency=0.26)
        assert res_carnot_viol["is_physically_possible"] is False
        assert res_carnot_viol["violation_type"] == VIOLATION_CARNOT_SECOND_LAW

        # Th = 0K or Th <= Tc is invalid input
        res_invalid_temp = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=400.0, claimed_efficiency=0.10)
        assert res_invalid_temp["is_physically_possible"] is False

    def test_landauer_sub_minimum_energy_dissipation(self):
        """Test Landauer bit erasure limit at cryogenic (4.2K), room temp (300K), and high temp (1000K)."""
        # At 300K, 1 bit erasure min energy is k_B * 300 * ln2 ~ 2.8705e-21 Joules (2.87 zJ)
        res_room_viol = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=300.0, claimed_energy_joules=1.0e-22)
        assert res_room_viol["is_physically_possible"] is False
        assert res_room_viol["violation_type"] == VIOLATION_LANDAUER_THERMODYNAMIC

        # At 4.2K (Liquid Helium), min energy for 1000 bits is 1000 * k_B * 4.2 * ln2 ~ 4.0187e-20 Joules
        res_cryo_valid = check_landauer_erasure_invariant(bits_erased=1000, ambient_temp_k=4.2, claimed_energy_joules=5.0e-20)
        assert res_cryo_valid["is_physically_possible"] is True

        res_cryo_viol = check_landauer_erasure_invariant(bits_erased=1000, ambient_temp_k=4.2, claimed_energy_joules=1.0e-21)
        assert res_cryo_viol["is_physically_possible"] is False

    # --- F11: Shannon Channel Capacity Limits ---
    def test_shannon_capacity_ceiling_and_spectral_efficiency(self):
        """Test Shannon-Hartley capacity bounds under standard, high SNR, and low SNR conditions."""
        # Bandwidth 20 MHz (2e7 Hz), SNR = 15 (linear) -> C = 2e7 * log2(1 + 15) = 2e7 * 4 = 80 Mbps (8e7 bps)
        # Claiming 100 Mbps (1e8 bps) exceeds capacity
        res_shannon_viol = check_shannon_capacity_invariant(bandwidth_hz=2e7, snr_linear=15.0, claimed_bps=1.0e8)
        assert res_shannon_viol["is_physically_possible"] is False
        assert res_shannon_viol["violation_type"] == VIOLATION_SHANNON_CAPACITY

        res_shannon_valid = check_shannon_capacity_invariant(bandwidth_hz=2e7, snr_linear=15.0, claimed_bps=7.5e7)
        assert res_shannon_valid["is_physically_possible"] is True
        assert res_shannon_valid["spectral_efficiency_bps_hz"] == 3.75

    # --- Unified Evaluator & NLP Claim Parser ---
    def test_nlp_freeform_claim_parser_multi_violation(self):
        """Test free-form natural language text containing multiple physical assertions."""
        nlp_text = (
            "We deployed a geo-distributed database across 8000 km in silica fiber with only 5 ms latency. "
            "Our cluster of 64 nodes achieves 128x speedup using Universal Scalability algorithms. "
            "The thermodynamic heat pump operates between 600 K and 300 K with 65% thermal efficiency. "
            "Each bit erasure at 300 K requires only 1.0e-23 Joules of energy."
        )
        res = evaluate_all_boundary_invariants(nlp_text)
        assert res["valid"] is False
        assert res["multiplier"] == 0.0
        assert len(res["violations"]) >= 3  # All 4 statements in the text violate physical laws!


# ==============================================================================
# 6. GROUNDING SCORECARD & REFUSAL GATE ADVERSARIAL STRESS
# ==============================================================================
class TestTier5GroundingScorecardAndRefusalGateAdversarial(unittest.TestCase):
    """Adversarial stress tests for Grounding Scorecard, refusal threshold gating, and diagnostics."""

    def test_refusal_boundary_precision(self):
        """Test exact refusal boundary float precision around threshold 0.65."""
        # 1. Custom weights set to achieve exactly 0.6499 vs 0.6500
        score_sub = compute_grounding_scorecard(
            passages=[{"filename": "doc.txt", "epistemic_weight": 0.6499, "staleness_coefficient": 0.6499}],
            threshold=0.65,
            weight_tier=1.0,
            weight_consensus=0.0,
            weight_temporal=0.0
        )
        assert score_sub["is_grounded"] is False
        assert score_sub["status"] == "refusal"

        score_exact = compute_grounding_scorecard(
            passages=[{"filename": "doc.txt", "epistemic_weight": 0.6500, "staleness_coefficient": 0.6500}],
            threshold=0.65,
            weight_tier=1.0,
            weight_consensus=0.0,
            weight_temporal=0.0
        )
        assert score_exact["is_grounded"] is True
        assert score_exact["status"] == "success"

    def test_compound_adversarial_failure_diagnostics(self):
        """Test diagnostic report generation when all evidentiary pillars fail simultaneously."""
        passages = [
            {
                "filename": "unverified_blog_post_notes.txt",
                "content": "The system throughput is 10000 TPS under all conditions. Obsoleted by V2.",
                "metadata": {"epistemic_tier": "TIER_4_COMMENTARY", "effective_date": "2000-01-01"}
            },
            {
                "filename": "forum_scratchpad.txt",
                "content": "The system throughput is 100 TPS under all conditions. Obsoleted by V2.",
                "metadata": {"epistemic_tier": "TIER_4_COMMENTARY", "effective_date": "2000-01-01"}
            }
        ]
        # Invariant claim that violates Speed of Light
        claim = {"distance_km": 10000.0, "reported_latency_ms": 1.0}

        scorecard = compute_grounding_scorecard(passages=passages, generated_claim=claim, threshold=0.65)
        assert scorecard["is_grounded"] is False
        assert scorecard["invariant_multiplier"] == 0.0
        assert scorecard["score"] == 0.0

        diag = scorecard["diagnostic_report"]
        assert diag["refusal_status"] is True
        assert len(diag["epistemic_deficits"]) >= 1
        assert len(diag["temporal_deficits"]) >= 1
        assert len(diag["consensus_deficits"]) >= 1
        assert len(diag["invariant_violations"]) >= 1
        assert len(diag["recommended_actions"]) >= 1

    def test_grounded_retrieval_engine_e2e_stress_pipeline(self):
        """Test full GroundedRetrievalEngine pipeline under diverse adversarial query workloads."""
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)

        # 1. Empty and whitespace queries
        r_empty = engine.evaluate_grounding(query="")
        assert r_empty["is_grounded"] is False
        assert r_empty["reason"] == "ZERO_EVIDENCE"

        r_ws = engine.evaluate_grounding(query="    \t\n   ")
        assert r_ws["is_grounded"] is False
        assert r_ws["reason"] == "ZERO_EVIDENCE"

        # 2. Query with Tier 1 RFC & ISO passages
        good_passages = [
            {
                "id": "rfc9110",
                "filename": "rfc9110_http_semantics.pdf",
                "content": "The HTTP/1.1 protocol specifies idempotent GET, HEAD, and PUT methods.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "effective_date": "2024-01-01"}
            },
            {
                "id": "iso27001",
                "filename": "iso27001_security.pdf",
                "content": "Information security management requires strict access control policies.",
                "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "effective_date": "2024-01-01"}
            }
        ]
        r_good = engine.evaluate_grounding(query="HTTP security specifications", candidate_passages=good_passages)
        assert r_good["is_grounded"] is True
        assert r_good["status"] == "success"
        assert r_good["grounding_score"] >= 0.65

        # 3. Same good passages but with a physical invariant violation attached to claim
        r_inv_fail = engine.evaluate_grounding(
            query="HTTP security specifications",
            candidate_passages=good_passages,
            generated_claim="Transatlantic optical fiber replication occurs with 0.1 ms latency across 6000 km."
        )
        assert r_inv_fail["is_grounded"] is False
        assert r_inv_fail["status"] == "refusal"
        assert r_inv_fail["invariant_multiplier"] == 0.0
        assert r_inv_fail["score"] == 0.0
