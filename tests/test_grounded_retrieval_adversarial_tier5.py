"""
Tier 5 Adversarial Verification Suite & Edge-Case Oracle.
Empirical challenger tests for Grounded Retrieval & Epistemic Invariant Engine (Milestone M6).

Covers:
- Category 1: Numerical Extremes, Boundary Singularities & Float Precision
- Category 2: Unicode NFC/NFD, Exotic Encodings, Malicious Strings & Path Injections
- Category 3: Dense Propositional Stress & Extreme Token Decompositions
- Category 4: Multi-Way Consensus Cycles, Graph Relations & 4-Tier Contradiction Adjudication
- Category 5: Adversarial Spoofing, Binary Invariant Vetoes & End-to-End Refusal Diagnostics
"""

import pytest
import math
import unicodedata
from datetime import datetime, date

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
    check_landauer_limit_invariant,
    check_landauer_erasure_invariant,
    check_cap_pacelc_invariant,
    check_shannon_capacity_invariant,
    evaluate_all_boundary_invariants,
    verify_optical_latency_invariant,
    verify_usl_invariant,
    verify_cap_pacelc_invariant,
    verify_carnot_landauer_invariant,
    verify_shannon_capacity_invariant,
    compute_grounding_scorecard,
    generate_knowledge_gap_diagnostic_report,
    KnowledgeGapDiagnosticReport,
    GroundedRetrievalEngine,
    execute_grounded_retrieval,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS,
    REFUSAL_THRESHOLD
)


# ==============================================================================
# CATEGORY 1: NUMERICAL EXTREMES, BOUNDARY SINGULARITIES & FLOAT PRECISION
# ==============================================================================
class TestCategory1NumericalExtremesAndSingularities:

    def test_rrf_invalid_and_extreme_k_values(self):
        candidates = [{"id": "d1", "filename": "rfc9110.pdf", "rank": 1}]
        # Non-positive k values must be clamped to max(1, int(k))
        fused_zero = compute_authority_weighted_rrf(candidates, [], k=0)
        assert len(fused_zero) == 1
        assert fused_zero[0]["raw_rrf_score"] > 0

        fused_neg = compute_authority_weighted_rrf(candidates, [], k=-50)
        assert len(fused_neg) == 1
        assert fused_neg[0]["raw_rrf_score"] > 0

        # String representation of integer
        fused_str = compute_authority_weighted_rrf(candidates, [], k="60")
        assert len(fused_str) == 1

        # Astronomical k
        fused_huge = compute_authority_weighted_rrf(candidates, [], k=1_000_000)
        assert len(fused_huge) == 1
        assert fused_huge[0]["raw_rrf_score"] > 0

    def test_rrf_zero_and_negative_intent_weights(self):
        candidates = [{"id": "d1", "filename": "spec.md", "rank": 1}]
        # Both weights 0.0 -> should fallback gracefully to 0.5/0.5
        fused_zero_w = compute_authority_weighted_rrf(
            candidates, candidates, k=60, intent_weights={"lexical": 0.0, "dense": 0.0}
        )
        assert len(fused_zero_w) == 1
        assert fused_zero_w[0]["raw_rrf_score"] > 0

    def test_usl_boundary_concurrency_and_retrograde_peak(self):
        # High node count with zero coherency penalty: N=1000, alpha=0.001, beta=0.0 -> C(N) ≈ 500x
        res_high = check_usl_scalability_invariant(node_count=1000, alpha=0.001, beta=0.0, claimed_speedup=450.0)
        assert res_high["is_computationally_valid"] is True

        # Extreme node count with coherency penalty: N=1,000,000, alpha=0.001, beta=0.0001 -> C(N) collapses to ~0.01x
        res_huge_valid = check_usl_scalability_invariant(node_count=1_000_000, alpha=0.001, beta=0.0001, claimed_speedup=0.005)
        assert res_huge_valid["is_computationally_valid"] is True

        res_huge_invalid = check_usl_scalability_invariant(node_count=1_000_000, alpha=0.001, beta=0.0001, claimed_speedup=10.0)
        assert res_huge_invalid["is_computationally_valid"] is False

        # alpha=0, beta=0: ideal scaling, speedup = node_count
        res_linear = check_usl_scalability_invariant(node_count=100, alpha=0.0, beta=0.0, claimed_speedup=100.0)
        assert res_linear["is_computationally_valid"] is True

        # alpha=1.0: complete serialization ceiling C(N) = 1.0 for all N
        res_serialized = check_usl_scalability_invariant(node_count=500, alpha=1.0, beta=0.0, claimed_speedup=1.0)
        assert res_serialized["is_computationally_valid"] is True

        # Invalid alpha > 1.0 or alpha < 0
        res_bad_alpha = check_usl_scalability_invariant(node_count=10, alpha=1.5, beta=0.0, claimed_speedup=1.0)
        assert res_bad_alpha["is_computationally_valid"] is False

    def test_carnot_extreme_and_singular_temperatures(self):
        # Hot and cold equal -> efficiency must be 0
        res_equal = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=300.0, claimed_efficiency=0.01)
        assert res_equal["is_physically_possible"] is False

        # Absolute zero cold reservoir (T_cold = 0 K is physically impossible under 3rd law)
        res_zero_k = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=0.0, claimed_efficiency=0.5)
        assert res_zero_k["is_physically_possible"] is False

        # Inverted temperatures (T_cold > T_hot)
        res_inv = check_carnot_efficiency_invariant(t_hot_k=200.0, t_cold_k=400.0, claimed_efficiency=0.1)
        assert res_inv["is_physically_possible"] is False

        # Claimed efficiency > 1.0 (over 100% efficiency)
        res_over_100 = check_carnot_efficiency_invariant(t_hot_k=1000.0, t_cold_k=300.0, claimed_efficiency=1.05)
        assert res_over_100["is_physically_possible"] is False

    def test_landauer_cryogenic_and_extreme_bitcounts(self):
        # Cryogenic milli-Kelvin computing: T = 0.01 K (10 mK)
        # E_min = 1 * 1.380649e-23 * 0.01 * ln(2) ≈ 9.569e-26 J
        res_cryo_valid = check_landauer_erasure_invariant(bit_count=1, t_kelvin=0.01, claimed_energy_joules=1.0e-25)
        assert res_cryo_valid["is_physically_possible"] is True

        res_cryo_invalid = check_landauer_erasure_invariant(bit_count=1, t_kelvin=0.01, claimed_energy_joules=1.0e-27)
        assert res_cryo_invalid["is_physically_possible"] is False

        # Exabyte bit erasure: 10^18 bits at 300 K
        # E_min ≈ 10^18 * 2.87e-21 J ≈ 2.87 mJ
        res_exabit = check_landauer_erasure_invariant(bit_count=10**18, t_kelvin=300.0, claimed_energy_joules=3.0e-3)
        assert res_exabit["is_physically_possible"] is True

    def test_shannon_zero_snr_and_extreme_bandwidths(self):
        # Zero bandwidth -> invalid input
        res_zero_b = check_shannon_capacity_invariant(bandwidth_hz=0.0, snr_linear=100.0, claimed_bps=100.0)
        assert res_zero_b["is_physically_possible"] is False

        # Terahertz communication: B = 1 THz = 10^12 Hz, SNR = 100
        # C = 10^12 * log2(101) ≈ 6.658 Tbps
        res_thz_valid = check_shannon_capacity_invariant(bandwidth_hz=1e12, snr_linear=100.0, claimed_bps=6.0e12)
        assert res_thz_valid["is_physically_possible"] is True

        res_thz_invalid = check_shannon_capacity_invariant(bandwidth_hz=1e12, snr_linear=100.0, claimed_bps=10.0e12)
        assert res_thz_invalid["is_physically_possible"] is False

    def test_grounding_scorecard_exact_float_precision_boundary(self):
        # Scorecard threshold is exactly 0.65
        # Test just at or above threshold
        passages_pass = [
            {"filename": "rfc9110.pdf", "content": "HTTP semantics standard with verified parameters.", "epistemic_weight": 0.85}
        ]
        # Single passage -> consensus_score = 0.70, staleness = 1.0
        # score = 0.45 * 0.85 + 0.35 * 0.70 + 0.20 * 1.0 = 0.3825 + 0.245 + 0.20 = 0.8275 >= 0.65
        res_pass = compute_grounding_scorecard(passages=passages_pass)
        assert res_pass["is_grounded"] is True
        assert res_pass["grounding_score"] >= 0.65

        # All Tier 4 commentary passages (weight 0.35, staleness 0.35, consensus 0.45)
        passages_fail = [
            {"filename": "notes.txt", "content": "Unverified blog post.", "epistemic_weight": 0.35, "staleness_coefficient": 0.35}
        ]
        res_fail = compute_grounding_scorecard(passages=passages_fail)
        assert res_fail["is_grounded"] is False
        assert res_fail["refusal_status"] is True


# ==============================================================================
# CATEGORY 2: UNICODE NFC/NFD, EXOTIC ENCODINGS, MALICIOUS STRINGS & PATHS
# ==============================================================================
class TestCategory2UnicodeEncodingsAndSecurityStrings:

    def test_unicode_nfc_nfd_normalization_in_tiering(self):
        # Decomposed NFD unicode vs Composed NFC
        nfc_filename = "spécification_rfc9110.pdf"
        nfd_filename = unicodedata.normalize("NFD", nfc_filename)

        t_nfc, w_nfc = classify_source_epistemic_tier(nfc_filename)
        t_nfd, w_nfd = classify_source_epistemic_tier(nfd_filename)

        assert t_nfc == TIER_1_PRIMARY
        assert t_nfd == TIER_1_PRIMARY
        assert w_nfc == 1.00
        assert w_nfd == 1.00

    def test_sql_injection_and_path_traversal_filenames(self):
        malicious_filenames = [
            "../../../../etc/passwd",
            "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "'; DROP TABLE files; --.py",
            "<script>alert('xss')</script>.rfc9110.pdf",
            "\x00nullbyte_rfc9110.pdf",
            "C:\\Users\\Admin\\AppData\\Local\\Temp\\scratch_notes.txt"
        ]
        for m_name in malicious_filenames:
            tier, weight = classify_source_epistemic_tier(m_name)
            assert tier in (TIER_1_PRIMARY, TIER_2_TECH_SPEC, TIER_3_SECONDARY, TIER_4_COMMENTARY)
            assert isinstance(weight, float)

    def test_unicode_fullwidth_and_mathematical_symbols(self):
        # Fullwidth dot and characters
        text = "The transaction throughput is 1000\uff0etps under production load."
        assertions = extract_document_assertions(text)
        assert len(assertions["numerical_assertions"]) >= 1

    def test_zero_width_and_control_characters_in_text(self):
        text_with_zwsp = "Valid\u200b factual\u200c proposition\u200d statement\ufeff with hidden characters."
        props = decompose_into_propositions(text_with_zwsp, "DocZWSP")
        assert len(props) >= 1
        assert "proposition" in props[0]["statement"]

    def test_optical_haversine_antipodal_and_boundary_coordinates(self):
        # Same point (distance = 0)
        d_same = check_optical_latency_invariant(lat1=40.7128, lon1=-74.0060, lat2=40.7128, lon2=-74.0060, reported_latency_ms=0.1)
        assert d_same["is_physically_possible"] is True
        assert d_same["distance_km"] == 0.0

        # Exact Antipodal points: North pole (90, 0) to South pole (-90, 0)
        # Half circumference ≈ 20,015 km. In fiber: RTT min ≈ 196.2 ms
        d_antipodal_valid = check_optical_latency_invariant(lat1=90.0, lon1=0.0, lat2=-90.0, lon2=0.0, reported_latency_ms=250.0)
        assert d_antipodal_valid["is_physically_possible"] is True
        assert math.isclose(d_antipodal_valid["distance_km"], 20015.08, rel_tol=1e-2)

        d_antipodal_invalid = check_optical_latency_invariant(lat1=90.0, lon1=0.0, lat2=-90.0, lon2=0.0, reported_latency_ms=50.0)
        assert d_antipodal_invalid["is_physically_possible"] is False


# ==============================================================================
# CATEGORY 3: DENSE PROPOSITIONAL STRESS & EXTREME TOKEN DECOMPOSITIONS
# ==============================================================================
class TestCategory3PropositionalStressAndDeepHierarchies:

    def test_deeply_nested_and_out_of_order_markdown_headings(self):
        md_content = """# Architecture System
Root overview of the system.
### Deep Section 1.1
This subsection was skipped directly from H1 to H3.
##### Even Deeper 1.1.1
Ultra deep technical specification proposition.
## Back to Section 2
Level 2 heading after popping deep stack.
###### Extreme Deep 2.1
Extreme depth proposition under section 2."""
        props = decompose_into_propositions(md_content, "ArchitectureDoc")
        assert len(props) >= 4
        # Verify heading stack unwinding
        h2_prop = next(p for p in props if "Level 2 heading" in p["statement"])
        assert "Deep Section" not in h2_prop["breadcrumb_scope"]
        assert "Back to Section 2" in h2_prop["breadcrumb_scope"]

    def test_proposition_decomposition_with_embedded_code_and_math(self):
        text = """The equation E = m * c^2 governs relativistic mass energy equivalence.
The hash function uses SHA-256 with 256-bit output size.
The IP address 192.168.1.1 is reserved for private network routing."""
        props = decompose_into_propositions(text, "TechnicalDoc")
        assert len(props) == 3
        assert any("SHA-256" in p["statement"] for p in props)
        assert any("192.168.1.1" in p["statement"] for p in props)

    def test_massive_single_document_proposition_throughput(self):
        # Generate 200 distinct factual sentences
        sentences = [f"Factual statement number {i} validating system invariant {i % 10}." for i in range(200)]
        large_text = " ".join(sentences)
        props = decompose_into_propositions(large_text, "MassiveDoc")
        assert len(props) == 200
        assert props[0]["proposition_id"] == "MassiveDoc#prop_0"
        assert props[199]["proposition_id"] == "MassiveDoc#prop_199"

    def test_parent_context_expansion_without_database(self):
        props = [
            {"file_id": None, "breadcrumb_scope": "Doc > Sec", "statement": "Target statement here.", "contextual_statement": "[Doc > Sec] Target statement here."}
        ]
        expanded = expand_propositions_to_parent_context(props, db_connection=None)
        assert len(expanded) == 1
        assert expanded[0]["has_parent_context"] is True


# ==============================================================================
# CATEGORY 4: MULTI-WAY CONSENSUS CYCLES & 4-TIER CONTRADICTION ADJUDICATION
# ==============================================================================
class TestCategory4ConsensusCyclesAndHierarchyAdjudication:

    def test_tier1_epistemic_dominance_resolution(self):
        # Tier 1 standard (RFC, weight 1.00) vs Tier 3 textbook (weight 0.70)
        # Delta = 0.30 >= 0.20 -> Epistemic Authority Dominance adopted
        passages = [
            {"filename": "rfc9110_http_standard.pdf", "content": "The maximum request header limit is 8192 bytes.", "rank": 1},
            {"filename": "web_dev_textbook.pdf", "content": "The maximum request header limit is 4096 bytes.", "rank": 2}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["contradictions_count"] >= 1
        assert len(res["resolved_claims"]) >= 1
        winner = res["resolved_claims"][0]
        assert winner["resolution_tier"] == "EPISTEMIC_AUTHORITY_DOMINANCE"
        assert winner["resolved_source"] == "rfc9110_http_standard.pdf"

    def test_tier2_temporal_superseding_dominance_resolution(self):
        # Equal tier (both Tier 1 RFCs), but RFC 7230 is superseded by RFC 9110
        passages = [
            {"filename": "rfc7230_http11.pdf", "content": "Obsoleted by RFC 9110. The connection timeout is 30s.", "metadata": {"publication_year": 2014}},
            {"filename": "rfc9110_http_semantics.pdf", "content": "The connection timeout is 60s.", "metadata": {"publication_year": 2022}}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["contradictions_count"] >= 1
        assert len(res["resolved_claims"]) >= 1
        winner = res["resolved_claims"][0]
        assert winner["resolution_tier"] == "TEMPORAL_SUPERSEDING_DOMINANCE"
        assert winner["resolved_source"] == "rfc9110_http_semantics.pdf"

    def test_tier3_condition_scope_specificity_harmonization(self):
        # Equal tier, same year, but distinct condition scopes
        passages = [
            {"filename": "spec_arm64.md", "content": "Under arm64 platform the buffer size is 64KB."},
            {"filename": "spec_x86.md", "content": "Under x86_64 platform the buffer size is 128KB."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["contradictions_count"] >= 1
        assert len(res["resolved_claims"]) >= 1
        harmonized = res["resolved_claims"][0]
        assert harmonized["resolution_tier"] == "CONDITION_SCOPE_SPECIFICITY"
        assert harmonized["status"] == "HARMONIZED_DUAL_SCOPE"

    def test_tier4_unresolvable_epistemic_conflict_dissenting_ledger(self):
        # Equal tier (both Tier 4 commentary), same year, unconditional direct clash
        passages = [
            {"filename": "blog_author_a.md", "content": "The default cache eviction policy is LFU."},
            {"filename": "blog_author_b.md", "content": "The default cache eviction policy is LRU."}
        ]
        res = evaluate_cross_document_consensus(passages)
        assert res["contradictions_count"] >= 1
        assert len(res["dissenting_ledger"]) >= 1
        dissent = res["dissenting_ledger"][0]
        assert dissent["resolution_tier"] == "UNRESOLVABLE_EPISTEMIC_CONFLICT"
        assert dissent["status"] == "UNRESOLVED_EPISTEMIC_CONFLICT"

    def test_three_way_cyclic_contradiction_graph(self):
        # Three passages all claiming different contradictory numerical values
        passages = [
            {"filename": "source_alpha.txt", "content": "The latency threshold is 10ms."},
            {"filename": "source_beta.txt", "content": "The latency threshold is 50ms."},
            {"filename": "source_gamma.txt", "content": "The latency threshold is 100ms."}
        ]
        res = evaluate_cross_document_consensus(passages)
        # Pairwise combinations: (alpha, beta), (alpha, gamma), (beta, gamma) -> 3 contradictions
        assert res["contradictions_count"] == 3
        assert res["consensus_level"] in ("CONTRADICTION_DETECTED", "MODERATE_CONSENSUS")


# ==============================================================================
# CATEGORY 5: ADVERSARIAL SPOOFING, INVARIANT VETOES & REFUSAL DIAGNOSTICS
# ==============================================================================
class TestCategory5AdversarialSpoofingAndRefusalDiagnostics:

    def test_adversarial_commentary_filename_spoofing(self):
        # Filename starts with 'scratch_' or 'blog_' but attempts to name-drop 'rfc9110'
        spoofed_files = [
            "scratch_notes_about_rfc9110.txt",
            "blog_review_of_iso27001_standard.md",
            "informal_chat_discussing_18_usc_1030.txt"
        ]
        for f in spoofed_files:
            tier, weight = classify_source_epistemic_tier(f)
            assert tier == TIER_4_COMMENTARY, f"Spoofed file {f} was incorrectly elevated!"
            assert weight == 0.35

    def test_binary_invariant_multiplier_complete_veto(self):
        # Superluminal optical latency claim: 10,000 km in 1.0 ms
        impossible_claim = {
            "type": "OPTICAL",
            "distance_km": 10000.0,
            "reported_latency_ms": 1.0,
            "medium": "silica_fiber"
        }
        scorecard = compute_grounding_scorecard(
            passages=[{"filename": "rfc9110.pdf", "content": "High authority primary source."}],
            generated_claim=impossible_claim
        )
        assert scorecard["is_grounded"] is False
        assert scorecard["refusal_status"] is True
        assert scorecard["invariant_multiplier"] == 0.0
        assert scorecard["grounding_score"] == 0.0
        assert "BOUNDARY_INVARIANT_VETO" in scorecard["reason"]

    def test_natural_language_claim_boundary_evaluation(self):
        # Text containing multiple physical claims
        text_with_violations = """
        Our high-speed trading system transmits across 5000 km of transatlantic fiber with only 2 ms latency.
        Additionally, our thermodynamic engine achieves 90% thermal efficiency between 500K and 300K.
        """
        audit = evaluate_all_boundary_invariants(text_with_violations)
        assert audit["valid"] is False
        assert audit["multiplier"] == 0.0
        assert len(audit["violations"]) >= 2

    def test_diagnostic_report_completeness_and_serialization(self):
        report = generate_knowledge_gap_diagnostic_report(
            score=0.42,
            threshold=0.65,
            passages=[{"filename": "blog_a.md", "epistemic_tier": TIER_4_COMMENTARY}],
            avg_tier_weight=0.35,
            avg_temporal_score=0.40,
            consensus_score=0.45
        )
        assert isinstance(report, KnowledgeGapDiagnosticReport)
        assert report.refusal_status is True
        assert len(report.epistemic_deficits) >= 1
        assert len(report.recommended_actions) >= 1

        d_dict = report.to_dict()
        assert "refusal_status" in d_dict
        assert "epistemic_deficits" in d_dict
        assert "recommended_actions" in d_dict

    def test_end_to_end_engine_evaluation_with_gap_diagnostics(self):
        engine = GroundedRetrievalEngine()
        # Query with only Tier 4 commentary passages
        res = engine.evaluate_grounding(
            query="quantum supremacy protocol",
            candidate_passages=[
                {"filename": "draft_notes.txt", "content": "Draft idea without formal verification.", "rank": 1}
            ]
        )
        assert res["status"] == "refusal"
        assert res["refusal_status"] is True
        assert "knowledge_gaps" in res["diagnostics"]
        assert len(res["diagnostics"]["epistemic_deficits"]) >= 1
