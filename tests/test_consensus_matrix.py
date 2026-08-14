"""
Comprehensive Unit Test Suite for Cross-Document Consensus & Contradiction Resolution Matrix Engine.
Validates Assertion Extraction, Pairwise NLI Heuristics, Multi-Source Confidence Boosting,
and the 4-Tier Contradiction Resolution Hierarchy.
"""

import pytest
import math
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
    NLI_ENTAILMENT,
    NLI_CONTRADICTION,
    NLI_NEUTRAL,
    CONFLICT_NUMERICAL_DISCREPANCY,
    CONFLICT_POLARITY_INVERSION,
    CONFLICT_STATUS_COLLISION,
    TIER_1_EPISTEMIC_DOMINANCE,
    TIER_2_TEMPORAL_DOMINANCE,
    TIER_3_CONDITION_SCOPE,
    TIER_4_UNRESOLVABLE
)
from src.domain.epistemic_tiering import (
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)


def test_assertion_extraction_numerical_and_units():
    text = (
        "The cluster node allocates 1024MB RAM and achieves 5000tps throughput "
        "with 12ms latency at a cost of $250. Operating frequency is 3.5GHz."
    )
    assertions = extract_document_assertions(text, "cluster_spec.pdf")

    nums = assertions["numerical_assertions"]
    assert len(nums) >= 5

    # Check 1024MB
    mb_assert = next((n for n in nums if n["unit"] == "MB"), None)
    assert mb_assert is not None
    assert mb_assert["value"] == 1024.0

    # Check 5000tps
    tps_assert = next((n for n in nums if n["unit"] == "TPS"), None)
    assert tps_assert is not None
    assert tps_assert["value"] == 5000.0

    # Check 12ms
    ms_assert = next((n for n in nums if n["unit"] == "MS"), None)
    assert ms_assert is not None
    assert ms_assert["value"] == 12.0

    # Check $250
    usd_assert = next((n for n in nums if n["unit"] == "USD"), None)
    assert usd_assert is not None
    assert usd_assert["value"] == 250.0

    # Check 3.5GHz
    ghz_assert = next((n for n in nums if n["unit"] == "GHZ"), None)
    assert ghz_assert is not None
    assert ghz_assert["value"] == 3.5


def test_assertion_extraction_polarity_and_negation():
    text_pos = "OAuth 2.0 PKCE authentication is supported and enabled by default."
    ast_pos = extract_document_assertions(text_pos, "auth_spec.md")
    assert len(ast_pos["polarity_assertions"]) >= 1
    assert ast_pos["polarity_assertions"][0]["is_positive"] is True

    text_neg = "OAuth 2.0 PKCE authentication is not supported and forbidden in legacy mode."
    ast_neg = extract_document_assertions(text_neg, "legacy_notes.txt")
    assert len(ast_neg["polarity_assertions"]) >= 1
    assert ast_neg["polarity_assertions"][0]["is_positive"] is False


def test_assertion_extraction_status_keywords():
    text = "Protocol v1 is deprecated while Protocol v2 is active and stable."
    ast = extract_document_assertions(text, "api_versioning.md")
    statuses = [s["status"] for s in ast["status_assertions"]]
    assert "DEPRECATED" in statuses
    assert "ACTIVE" in statuses
    assert "STABLE" in statuses


def test_assertion_extraction_condition_scopes():
    text_1 = "Under load < 50 req/s, query latency is 5ms."
    ast_1 = extract_document_assertions(text_1, "perf_report.md")
    assert len(ast_1["condition_scopes"]) >= 1
    assert "50" in ast_1["condition_scopes"][0]["raw_scope"]

    text_2 = "In production mode on Linux, caching is enabled."
    ast_2 = extract_document_assertions(text_2, "deploy_guide.md")
    scopes = [sc["raw_scope"].lower() for sc in ast_2["condition_scopes"]]
    assert any("production" in s or "linux" in s for s in scopes)


def test_pairwise_nli_entailment_agreement():
    passages = [
        {
            "filename": "rfc9110_http_semantics.pdf",
            "content": "The maximum cache size is 1024MB per cluster node."
        },
        {
            "filename": "iso27001_standard.pdf",
            "content": "Each node maintains 1024MB cache memory limit."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["consensus_level"] == HIGH_CONSENSUS
    assert res["consensus_score"] >= 0.95
    assert res["agreements_count"] >= 1
    assert res["contradictions_count"] == 0
    assert len(res["pairwise_nli"]) == 1
    assert res["pairwise_nli"][0]["relation"] == NLI_ENTAILMENT


def test_pairwise_nli_numerical_discrepancy_contradiction():
    passages = [
        {
            "filename": "bench_report_a.txt",
            "content": "The maximum transaction throughput is 500tps."
        },
        {
            "filename": "bench_report_b.txt",
            "content": "The maximum transaction throughput is 5000tps."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert res["contradictions"][0]["conflict_type"] == CONFLICT_NUMERICAL_DISCREPANCY
    assert res["contradictions"][0]["unit"] == "TPS"
    assert res["contradictions"][0]["value_a"] == 500.0
    assert res["contradictions"][0]["value_b"] == 5000.0


def test_pairwise_nli_polarity_inversion_contradiction():
    passages = [
        {
            "filename": "service_spec.md",
            "content": "Bi-directional gRPC streaming is supported."
        },
        {
            "filename": "client_manual.txt",
            "content": "Bi-directional gRPC streaming is not supported."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert res["contradictions"][0]["conflict_type"] == CONFLICT_POLARITY_INVERSION


def test_pairwise_nli_status_collision_contradiction():
    passages = [
        {
            "filename": "security_policy.pdf",
            "content": "TLS 1.0 encryption protocol is forbidden and obsolete."
        },
        {
            "filename": "legacy_gateway.txt",
            "content": "TLS 1.0 encryption protocol is active and recommended."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert res["contradictions"][0]["conflict_type"] == CONFLICT_STATUS_COLLISION


def test_multi_source_consensus_confidence_boosting():
    # Mathematical boosting formula: S = min(1.0, W_bar_E * (1.0 + gamma * log2(1 + N_agree)))
    # With W_bar = 0.85, gamma = 0.15:
    # N_agree = 1 -> log2(2) = 1.0 -> S = 0.85 * (1 + 0.15*1) = 0.85 * 1.15 = 0.9775
    # N_agree = 3 -> log2(4) = 2.0 -> S = 0.85 * (1 + 0.15*2) = 0.85 * 1.30 = 1.105 -> min(1.0, ...) = 1.0
    w_list = [0.85, 0.85]
    boost_1 = compute_consensus_boost(w_list, agreements_count=1, gamma=0.15)
    assert 0.97 <= boost_1 <= 0.98

    boost_3 = compute_consensus_boost(w_list, agreements_count=3, gamma=0.15)
    assert boost_3 == 1.00

    # Three agreeing passages in evaluate_cross_document_consensus
    passages_3 = [
        {"filename": "spec_1.md", "content": "Database timeout is 30s."},
        {"filename": "spec_2.md", "content": "Database timeout is 30s."},
        {"filename": "spec_3.md", "content": "Database timeout is 30s."}
    ]
    res_3 = evaluate_cross_document_consensus(passages_3)
    assert res_3["consensus_level"] == HIGH_CONSENSUS
    assert res_3["consensus_score"] == 1.00
    assert res_3["agreements_count"] >= 3


def test_contradiction_resolution_tier_1_epistemic_authority_dominance():
    # Primary Tier 1 (RFC 9110, weight 1.0) vs Commentary Tier 4 (Blog, weight 0.35)
    # Delta = 0.65 >= 0.20 -> Epistemic Authority Dominance adopts RFC 9110!
    passages = [
        {
            "filename": "rfc9110_http.pdf",
            "content": "HTTP 404 status code indicates resource not found."
        },
        {
            "filename": "blog_discussion.txt",
            "content": "HTTP 404 status code indicates internal server error."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert len(res["resolved_claims"]) == 1
    resolved = res["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_1_EPISTEMIC_DOMINANCE
    assert resolved["resolved_source"] == "rfc9110_http.pdf"
    assert resolved["overruled_source"] == "blog_discussion.txt"
    assert resolved["authority_delta"] >= 0.20
    assert len(res["dissenting_ledger"]) == 0


def test_contradiction_resolution_tier_2_temporal_superseding_dominance():
    # Both sources are Tier 2 (Technical Specifications, weight 0.85)
    # Delta < 0.20 -> Check Temporal Dominance!
    # Doc A has "superseded by API v2" and older year 2020 vs Doc B active in 2026.
    passages = [
        {
            "filename": "api_v1_spec.md",
            "content": "The default auth header is X-Auth-Key. This protocol is superseded by API v2 and deprecated."
        },
        {
            "filename": "api_v2_spec.md",
            "content": "The default auth header is Bearer token. Published 2026-01-10."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] >= 1
    assert len(res["resolved_claims"]) >= 1
    resolved = res["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_2_TEMPORAL_DOMINANCE
    assert resolved["resolved_source"] == "api_v2_spec.md"
    assert resolved["overruled_source"] == "api_v1_spec.md"


def test_contradiction_resolution_tier_3_condition_scope_specificity():
    # Both sources are Tier 2 specs (weight 0.85), same era.
    # Claims differ numerically: 10ms vs 80ms, but qualify under distinct condition scopes!
    # Doc A: "Under load < 50 req/s, query latency is 10ms."
    # Doc B: "Under load >= 50 req/s, query latency is 80ms."
    passages = [
        {
            "filename": "spec_light_load.md",
            "content": "Under load < 50 req/s, query latency is 10ms."
        },
        {
            "filename": "spec_heavy_load.md",
            "content": "Under load >= 50 req/s, query latency is 80ms."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert len(res["resolved_claims"]) == 1
    resolved = res["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_3_CONDITION_SCOPE
    assert resolved["status"] == "HARMONIZED_DUAL_SCOPE"
    assert len(resolved["harmonized_scopes"]) == 2
    assert res["consensus_level"] == MINOR_DISCREPANCY
    assert res["consensus_score"] == 0.50


def test_contradiction_resolution_tier_4_unresolvable_epistemic_conflict():
    # Equal Tier 1 sources (e.g. ISO vs RFC), unconditional collision, same era!
    # Cannot be resolved by Tiers 1, 2, or 3 -> Enters Dissenting Knowledge Ledger!
    passages = [
        {
            "filename": "iso_standard_9901.pdf",
            "content": "The mandatory encryption block size is 256 bits."
        },
        {
            "filename": "rfc_standard_8801.pdf",
            "content": "The mandatory encryption block size is 512 bits."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert len(res["resolved_claims"]) == 0
    assert len(res["dissenting_ledger"]) == 1
    dissent = res["dissenting_ledger"][0]
    assert dissent["status"] == "UNRESOLVED_EPISTEMIC_CONFLICT"
    assert dissent["resolution_tier"] == TIER_4_UNRESOLVABLE
    assert res["consensus_level"] == CONTRADICTION_DETECTED
    assert res["consensus_score"] == 0.45


def test_consensus_single_source_and_neutral_edge_cases():
    # Empty list
    res_empty = evaluate_cross_document_consensus([])
    assert res_empty["consensus_level"] == SINGLE_SOURCE
    assert res_empty["consensus_score"] == 0.70

    # Single source
    res_single = evaluate_cross_document_consensus([{"filename": "notes.txt", "content": "Just one doc."}])
    assert res_single["consensus_level"] == SINGLE_SOURCE
    assert res_single["consensus_score"] == 0.70

    # Two unrelated docs (Neutral)
    passages_neutral = [
        {"filename": "solar_system.txt", "content": "Jupiter is the largest planet in our solar system."},
        {"filename": "cooking_recipes.txt", "content": "Preheat oven to 350 degrees for chocolate cake baking."}
    ]
    res_neutral = evaluate_cross_document_consensus(passages_neutral)
    assert res_neutral["consensus_level"] == NEUTRAL
    assert res_neutral["consensus_score"] == 0.70
    assert res_neutral["agreements_count"] == 0
    assert res_neutral["contradictions_count"] == 0


def test_mixed_consensus_with_resolved_low_tier_contradiction():
    # 3 documents:
    # Doc 1 (Tier 1 RFC): Default port is 443.
    # Doc 2 (Tier 1 ISO): Default port is 443.
    # Doc 3 (Tier 4 Blog): Default port is 8080.
    passages = [
        {"filename": "rfc_tls.pdf", "content": "The default port is 443."},
        {"filename": "iso_sec.pdf", "content": "The default port is 443."},
        {"filename": "blog_post.txt", "content": "The default port is 8080."}
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["agreements_count"] >= 1
    assert res["contradictions_count"] >= 1
    # Contradictions with blog_post are resolved via Tier 1 Epistemic Dominance
    assert len(res["resolved_claims"]) >= 1
    assert len(res["dissenting_ledger"]) == 0
    assert res["consensus_level"] == HIGH_CONSENSUS
    assert res["consensus_score"] == 0.95


def test_moderate_consensus_with_authority_resolution():
    # 2 documents: Tier 1 RFC (weight 1.0) vs Tier 4 Blog (weight 0.35)
    # Contradiction is resolved via Tier 1 Epistemic Dominance, resulting in MODERATE_CONSENSUS (0.85)
    passages = [
        {"filename": "rfc_standard.pdf", "content": "The session timeout is 300s."},
        {"filename": "blog_discussion.txt", "content": "The session timeout is 900s."}
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert len(res["resolved_claims"]) == 1
    assert res["resolved_claims"][0]["resolution_tier"] == TIER_1_EPISTEMIC_DOMINANCE
    assert res["consensus_level"] == MODERATE_CONSENSUS
    assert res["consensus_score"] == 0.85


def test_explicit_metadata_authority_override():
    # Unnamed doc with metadata override to Tier 1 vs Tier 4 scratchpad
    passages = [
        {
            "filename": "doc_unnamed.txt",
            "content": "The rate limit is 100rps.",
            "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 1.00}
        },
        {
            "filename": "scratchpad.txt",
            "content": "The rate limit is 500rps."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["contradictions_count"] == 1
    assert len(res["resolved_claims"]) == 1
    assert res["resolved_claims"][0]["resolution_tier"] == TIER_1_EPISTEMIC_DOMINANCE
    assert res["resolved_claims"][0]["resolved_source"] == "doc_unnamed.txt"


def test_various_units_and_currency_assertions():
    text = (
        "Memory allocated is 16GB. Packet size is 64KB. Storage capacity is 2TB. "
        "Availability is 99.9%. Budget is €500 and £300. "
        "Capacity is 1000 users across 8 nodes and 32 cores."
    )
    ast = extract_document_assertions(text, "datacenter_spec.md")
    nums = ast["numerical_assertions"]

    units = [n["unit"] for n in nums]
    assert "GB" in units
    assert "KB" in units
    assert "TB" in units
    assert "%" in units
    assert "EUR" in units
    assert "GBP" in units
    assert "USERS" in units
    assert "NODES" in units
    assert "CORES" in units


def test_deep_condition_scopes_environment_modes():
    # Scope comparison: "in development mode" vs "in production mode"
    passages_env = [
        {
            "filename": "dev_config.md",
            "content": "In development mode, debug logging is enabled."
        },
        {
            "filename": "prod_config.md",
            "content": "In production mode, debug logging is disabled."
        }
    ]
    res_env = evaluate_cross_document_consensus(passages_env)
    assert res_env["contradictions_count"] == 1
    assert len(res_env["resolved_claims"]) == 1
    assert res_env["resolved_claims"][0]["resolution_tier"] == TIER_3_CONDITION_SCOPE
    assert res_env["resolved_claims"][0]["status"] == "HARMONIZED_DUAL_SCOPE"
    assert res_env["consensus_level"] == MINOR_DISCREPANCY

