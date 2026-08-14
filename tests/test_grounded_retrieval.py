"""
Unit test suite for Empirically Grounded Retrieval & Epistemic Invariant Engine.
Covers Epistemic Tiering (F1), Authority-Weighted RRF (F2), Temporal Validity (F3),
Exponential Staleness Decay (F4), Propositions, Consensus, and Invariants.
"""

import pytest
import math
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
    execute_grounded_retrieval,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)


def test_epistemic_tier_classification():
    # Tier 1 - Standards & Protocols
    t1_rfc, w1_rfc = classify_source_epistemic_tier("rfc9110_http_semantics.pdf")
    assert t1_rfc == "TIER_1_PRIMARY"
    assert w1_rfc == 1.00

    t1_iso, w1_iso = classify_source_epistemic_tier("iso27001_security_standard.pdf")
    assert t1_iso == "TIER_1_PRIMARY"
    assert w1_iso == 1.00

    t1_sec, w1_sec = classify_source_epistemic_tier("sec_10-k_annual_filing_2025.pdf")
    assert t1_sec == "TIER_1_PRIMARY"
    assert w1_sec == 1.00

    t1_law, w1_law = classify_source_epistemic_tier("18_usc_1030_cfaa_statute.txt")
    assert t1_law == "TIER_1_PRIMARY"
    assert w1_law == 1.00

    # Tier 1 - Formal Code & Data Schemas
    t1_py, w1_py = classify_source_epistemic_tier("database_engine.py")
    assert t1_py == "TIER_1_PRIMARY"
    assert w1_py == 1.00

    t1_proto, w1_proto = classify_source_epistemic_tier("consensus_message.proto")
    assert t1_proto == "TIER_1_PRIMARY"
    assert w1_proto == 1.00

    # Tier 2 - Official Technical Specifications
    t2_spec, w2_spec = classify_source_epistemic_tier("fastapi_rest_api_specification.md")
    assert t2_spec == "TIER_2_TECH_SPEC"
    assert w2_spec == 0.85

    t2_arch, w2_arch = classify_source_epistemic_tier("distributed_system_architecture_whitepaper.pdf")
    assert t2_arch == "TIER_2_TECH_SPEC"
    assert w2_arch == 0.85

    # Tier 3 - Academic Textbooks & Peer-Reviewed Literature
    t3_acc, w3_acc = classify_source_epistemic_tier("Intermediate_Accounting_17th_Edition.pdf")
    assert t3_acc == "TIER_3_SECONDARY"
    assert w3_acc == 0.70

    t3_guide, w3_guide = classify_source_epistemic_tier("computer_systems_curriculum_handbook.pdf")
    assert t3_guide == "TIER_3_SECONDARY"
    assert w3_guide == 0.70

    # Tier 4 - Informal Commentary & Notes
    t4_scratch, w4_scratch = classify_source_epistemic_tier("scratch_notes.txt")
    assert t4_scratch == "TIER_4_COMMENTARY"
    assert w4_scratch == 0.35

    t4_blog, w4_blog = classify_source_epistemic_tier("engineering_blog_post_opinion.md")
    assert t4_blog == "TIER_4_COMMENTARY"
    assert w4_blog == 0.35


def test_epistemic_tier_edge_cases():
    # Edge Case 1: Commentary file citing statutory law must NOT be elevated to Tier 1
    commentary_text = "In this blog post we review RFC 9110 and 18 U.S.C. § 1030 for general thoughts."
    t_comm, w_comm = classify_source_epistemic_tier("blog_notes_informal.txt", content_snippet=commentary_text)
    assert t_comm == "TIER_4_COMMENTARY"
    assert w_comm == 0.35

    # Edge Case 2: Explicit metadata override
    metadata_override = {"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 1.0}
    t_meta, w_meta = classify_source_epistemic_tier("unnamed_doc.txt", metadata=metadata_override)
    assert t_meta == "TIER_1_PRIMARY"
    assert w_meta == 1.00

    # Edge Case 3: Content-based detection for neutral filename
    snippet_statute = "Pursuant to 42 U.S.C. § 1983, every person who under color of statute..."
    t_snip, w_snip = classify_source_epistemic_tier("document_482.txt", content_snippet=snippet_statute)
    assert t_snip == "TIER_1_PRIMARY"
    assert w_snip == 1.00


def test_authority_weighted_rrf_fusion():
    # Lexical: Doc A (Tier 4) is #1, Doc B (Tier 1) is #2
    lexical_candidates = [
        {"id": "doc_a", "filename": "blog_discussion.md", "rank": 1, "content": "informal commentary"},
        {"id": "doc_b", "filename": "rfc9110_spec.pdf", "rank": 2, "content": "formal RFC standard"}
    ]
    # Dense: Doc A is #2, Doc B is #1
    dense_candidates = [
        {"id": "doc_b", "filename": "rfc9110_spec.pdf", "rank": 1, "content": "formal RFC standard"},
        {"id": "doc_a", "filename": "blog_discussion.md", "rank": 2, "content": "informal commentary"}
    ]

    fused = compute_authority_weighted_rrf(
        lexical_ranks=lexical_candidates,
        dense_ranks=dense_candidates,
        k=60,
        intent_weights={"lexical": 0.5, "dense": 0.5}
    )

    assert len(fused) == 2
    # Doc B (Tier 1, weight 1.0) must decisively outrank Doc A (Tier 4, weight 0.35)
    assert fused[0]["id"] == "doc_b"
    assert fused[0]["epistemic_tier"] == "TIER_1_PRIMARY"
    assert fused[0]["grounded_score"] > fused[1]["grounded_score"]
    assert fused[0]["final_rank"] == 1
    assert fused[1]["final_rank"] == 2


def test_authority_weighted_rrf_temporal_dampening():
    # Doc Old (Tier 1 but superseded staleness 0.35) vs Doc Active (Tier 2 active staleness 1.0)
    lexical_ranks = [
        {
            "id": "rfc7230",
            "filename": "rfc7230_http11.pdf",
            "epistemic_tier": "TIER_1_PRIMARY",
            "epistemic_weight": 1.00,
            "staleness_coefficient": 0.35,
            "rank": 1
        },
        {
            "id": "api_v2",
            "filename": "system_api_v2_spec.md",
            "epistemic_tier": "TIER_2_TECH_SPEC",
            "epistemic_weight": 0.85,
            "staleness_coefficient": 1.00,
            "rank": 2
        }
    ]

    fused = compute_authority_weighted_rrf(lexical_ranks=lexical_ranks, dense_ranks=[], k=60)
    # api_v2 (0.85 * 1.0 * (1/62) ≈ 0.0137) should beat rfc7230 (1.00 * 0.35 * (1/61) ≈ 0.0057)
    assert fused[0]["id"] == "api_v2"
    assert fused[0]["grounded_score"] > fused[1]["grounded_score"]


def test_temporal_validity_and_superseding():
    # 1. Superseded marker
    content_superseded = "This protocol is superseded by RFC 9110 and should not be used in modern deployments."
    res = detect_temporal_validity(content_superseded, publication_year=2015)
    assert res["is_superseded"] is True
    assert "RFC 9110" in res["superseded_by"]
    assert res["temporal_status"] == "SUPERSEDED"
    assert res["staleness_coefficient"] <= 0.40

    # 2. Active standard in current year
    content_active = "Current active ISO 27001 standard guidance for security operations."
    res_active = detect_temporal_validity(content_active, publication_year=2026)
    assert res_active["is_superseded"] is False
    assert res_active["temporal_status"] == "ACTIVE"
    assert res_active["staleness_coefficient"] >= 0.95

    # 3. Standards Header: Obsoletes
    content_rfc = "Network Working Group\nRequest for Comments: 9110\nObsoletes: 7230, 7231, 7232\nCategory: Standards Track"
    res_rfc = detect_temporal_validity(content_rfc)
    assert res_rfc["is_superseded"] is True
    assert "7230" in res_rfc["superseded_by"]

    # 4. Deprecation marker
    content_deprecated = "Notice: This API endpoint is deprecated in v3.2 and will be removed in v4.0."
    res_dep = detect_temporal_validity(content_deprecated)
    assert res_dep["temporal_status"] == "DEPRECATED"
    assert res_dep["staleness_coefficient"] <= 0.50

    # 5. Date extraction from ISO text
    content_iso_date = "Official Specification published 2021-04-15 by Architecture Board."
    res_date = detect_temporal_validity(content_iso_date)
    assert res_date["publication_year"] == 2021
    assert "2021-04-15" in res_date["effective_date"]


def test_exponential_temporal_decay():
    # Domain half-lives:
    # Law (10y): at delta_t = 10, decay should be approx 0.50
    decay_law_10y = compute_temporal_decay(document_year_or_date=2016, domain="law", status="ACTIVE")
    # delta_t = 2026 - 2016 = 10y -> exp(-ln(2)) = 0.50
    assert 0.48 <= decay_law_10y <= 0.52

    # Specs (2y): at delta_t = 2y, decay should be approx 0.50; at delta_t = 6y (3 half-lives) -> 0.125
    decay_spec_2y = compute_temporal_decay(document_year_or_date=2024, domain="tech_spec", status="ACTIVE")
    assert 0.48 <= decay_spec_2y <= 0.52

    # Superseded hard cap <= 0.40
    decay_superseded_fresh = compute_temporal_decay(document_year_or_date=2026, domain="law", status="SUPERSEDED")
    assert decay_superseded_fresh <= 0.40

    # Deprecated hard cap <= 0.50
    decay_deprecated_fresh = compute_temporal_decay(document_year_or_date=2026, domain="tech_spec", status="DEPRECATED")
    assert decay_deprecated_fresh <= 0.50

    # Custom half-life in days (e.g. 365.25 days = 1 year)
    decay_custom = compute_temporal_decay(document_year_or_date=2025, half_life_days=365.25)
    # delta_t = 1y -> half-life = 1y -> decay approx 0.50
    assert 0.48 <= decay_custom <= 0.52


def test_propositional_decomposition():
    text = "The Uroboros Knowledge Engine enforces zero external dependencies. All database calls route through SQLite WAL mode. Every commit produces a SHA-256 Merkle root."
    props = decompose_into_propositions(text, "Architecture_Overview.md", ["Core", "Database"])
    assert len(props) == 3
    assert "[Architecture_Overview.md > Core > Database]" in props[0]["contextual_statement"]


def test_cross_document_consensus():
    passages_agree = [
        {"filename": "spec_v1.pdf", "content": "The maximum cache size is 1024MB per cluster node."},
        {"filename": "spec_v2.pdf", "content": "Each node maintains 1024MB cache memory limit."}
    ]
    res_agree = evaluate_cross_document_consensus(passages_agree)
    assert res_agree["consensus_level"] == "HIGH_CONSENSUS"
    assert res_agree["agreements_count"] >= 1

    passages_conflict = [
        {"filename": "doc_a.pdf", "content": "The transaction limit is 500tps."},
        {"filename": "doc_b.pdf", "content": "The transaction limit is 5000tps."}
    ]
    res_conflict = evaluate_cross_document_consensus(passages_conflict)
    assert res_conflict["contradictions_count"] >= 1


def test_physical_boundary_invariants():
    # 1. Speed of light (5,000 km transatlantic fiber)
    opt_ok = check_optical_latency_invariant(5000.0, 70.0)
    assert opt_ok["is_physically_possible"] is True

    opt_bad = check_optical_latency_invariant(5000.0, 10.0)  # 10ms is faster than light in fiber!
    assert opt_bad["is_physically_possible"] is False
    assert "violates physical limit" in opt_bad["violation_details"]

    # 2. Universal Scalability Law (USL)
    # At N=32, alpha=0.05, beta=0.001 -> C(32) ≈ 9.03. Claiming 8.0x speedup is physically valid.
    usl_ok = check_usl_scalability_invariant(32, 0.05, 0.001, 8.0)
    assert usl_ok["is_computationally_valid"] is True

    usl_bad = check_usl_scalability_invariant(32, 0.05, 0.001, 100.0)  # Impossible speedup > N
    assert usl_bad["is_computationally_valid"] is False

    # 3. Carnot limit (T_hot = 600K, T_cold = 300K -> Max efficiency 50%)
    carnot_ok = check_carnot_efficiency_invariant(600.0, 300.0, 0.45)
    assert carnot_ok["is_physically_possible"] is True

    carnot_bad = check_carnot_efficiency_invariant(600.0, 300.0, 0.85)  # 85% violates 2nd law!
    assert carnot_bad["is_physically_possible"] is False


def test_grounded_retrieval_execution():
    res = execute_grounded_retrieval("accounting", top_k=3)
    assert res["status"] in ("success", "refusal")
    if res["status"] == "success":
        assert res["overall_grounded_confidence"] >= 0.65
        assert len(res["passages"]) > 0
