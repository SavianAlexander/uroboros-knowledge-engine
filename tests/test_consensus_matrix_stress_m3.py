"""
Adversarial Stress Test Suite for Milestone M3 (Feature F6: Consensus Matrix & Contradiction Resolution).
Empirically executed by challenger_m3.
"""

import pytest
import math
from src.domain.consensus_matrix import (
    evaluate_cross_document_consensus,
    extract_document_assertions,
    compute_consensus_boost,
    resolve_contradiction_hierarchy,
    _normalize_unit,
    _extract_condition_scopes,
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


# ==============================================================================
# SECTION 1: 4-TIER RESOLUTION HIERARCHY VERIFICATION
# ==============================================================================

def test_tier_1_statutory_vs_commentary_dominance():
    """
    Tier 1 statutory/RFC (weight 1.0) vs Tier 4 blog commentary (weight 0.35).
    Delta = 0.65 >= 0.20 -> Epistemic Authority Dominance must adopt Tier 1.
    """
    passages = [
        {
            "filename": "rfc_9110_http_spec.pdf",
            "content": "The standard port for HTTPS traffic is 443.",
            "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 1.00}
        },
        {
            "filename": "blog_dev_opinion.txt",
            "content": "The standard port for HTTPS traffic is 8443.",
            "metadata": {"epistemic_tier": "TIER_4_COMMENTARY", "authority_weight": 0.35}
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] == 1
    assert len(result["resolved_claims"]) == 1
    assert len(result["dissenting_ledger"]) == 0

    resolved = result["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_1_EPISTEMIC_DOMINANCE
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_source"] == "rfc_9110_http_spec.pdf"
    assert resolved["overruled_source"] == "blog_dev_opinion.txt"
    assert resolved["winning_tier"] == TIER_1_PRIMARY
    assert resolved["losing_tier"] == TIER_4_COMMENTARY
    assert resolved["authority_delta"] >= 0.20
    assert "rationale" in resolved


def test_tier_2_active_2026_vs_superseded_2014_dominance():
    """
    Tier 2: Both sources are technical specifications (Tier 2, weight 0.85).
    Source A is superseded from 2014, Source B is active from 2026.
    Temporal Superseding Dominance must adopt 2026 active source.
    """
    passages = [
        {
            "filename": "tls_arch_v1.md",
            "content": "The cipher suite requires TLS 1.0. This specification is superseded and deprecated as of 2014-06-01.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        },
        {
            "filename": "tls_arch_v2.md",
            "content": "The cipher suite requires TLS 1.3. Active standard released 2026-02-15.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] >= 1
    assert len(result["resolved_claims"]) >= 1

    resolved = result["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_2_TEMPORAL_DOMINANCE
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_source"] == "tls_arch_v2.md"
    assert resolved["overruled_source"] == "tls_arch_v1.md"
    assert "rationale" in resolved


def test_tier_2_publication_year_delta_dominance():
    """
    Tier 2: Equal epistemic tier (both Tier 2, weight 0.85), active status,
    but publication year 2026 vs 2018 (delta = 8 years >= 1 year).
    Temporal dominance must adopt newer 2026 source.
    """
    passages = [
        {
            "filename": "database_config_2018.md",
            "content": "The default connection pool capacity is 50 connections. Released 2018.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        },
        {
            "filename": "database_config_2026.md",
            "content": "The default connection pool capacity is 250 connections. Released 2026.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] >= 1
    assert len(result["resolved_claims"]) >= 1

    for resolved in result["resolved_claims"]:
        assert resolved["resolution_tier"] == TIER_2_TEMPORAL_DOMINANCE
        assert resolved["resolved_source"] == "database_config_2026.md"
        assert resolved["overruled_source"] == "database_config_2018.md"


def test_tier_3_condition_scope_conflict_harmonization():
    """
    Tier 3: Equal tier, same era, but conflicting metrics qualified under distinct condition scopes.
    Load < 50 req/s -> 5ms vs Load >= 50 req/s -> 45ms.
    Must be harmonized as HARMONIZED_DUAL_SCOPE under CONDITION_SCOPE_SPECIFICITY.
    """
    passages = [
        {
            "filename": "perf_low_load.md",
            "content": "Under load < 50 req/s, the p99 latency is 5ms.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        },
        {
            "filename": "perf_high_load.md",
            "content": "Under load >= 50 req/s, the p99 latency is 45ms.",
            "metadata": {"epistemic_tier": "TIER_2_TECH_SPEC", "authority_weight": 0.85}
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] == 1
    assert len(result["resolved_claims"]) == 1
    assert len(result["dissenting_ledger"]) == 0

    resolved = result["resolved_claims"][0]
    assert resolved["resolution_tier"] == TIER_3_CONDITION_SCOPE
    assert resolved["status"] == "HARMONIZED_DUAL_SCOPE"
    assert len(resolved["harmonized_scopes"]) == 2
    assert result["consensus_level"] == MINOR_DISCREPANCY
    assert result["consensus_score"] == 0.50


def test_tier_4_identical_tier_condition_clash_dissenting_ledger():
    """
    Tier 4: Two Tier 1 standards (weight 1.0), same era, unconditional contradictory assertion.
    Cannot be resolved by Tier 1, Tier 2, or Tier 3 -> Enters Dissenting Knowledge Ledger.
    """
    passages = [
        {
            "filename": "iso_standard_security_x.pdf",
            "content": "The required key derivation iteration count is 100000.",
            "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 1.00}
        },
        {
            "filename": "nist_special_publication_y.pdf",
            "content": "The required key derivation iteration count is 600000.",
            "metadata": {"epistemic_tier": "TIER_1_PRIMARY", "authority_weight": 1.00}
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] == 1
    assert len(result["resolved_claims"]) == 0
    assert len(result["dissenting_ledger"]) == 1

    dissent = result["dissenting_ledger"][0]
    assert dissent["resolution_tier"] == TIER_4_UNRESOLVABLE
    assert dissent["status"] == "UNRESOLVED_EPISTEMIC_CONFLICT"
    assert "conflict_id" in dissent
    assert dissent["conflict_id"].startswith("dissent_")
    assert "recommended_action" in dissent
    assert result["consensus_level"] == CONTRADICTION_DETECTED
    assert result["consensus_score"] == 0.45


# ==============================================================================
# SECTION 2: COMPLEX CONTRADICTIONS & ASSERTIONS
# ==============================================================================

def test_complex_negated_syntax_assertions():
    """
    Test polarity assertions with various natural language negation patterns:
    'without', 'forbidden', 'disallowed', 'incompatible', 'cannot', 'deprecated'.
    """
    samples = [
        ("Feature X is forbidden in production.", False),
        ("Feature X is disallowed in legacy clusters.", False),
        ("Feature X is incompatible with ARM64 architecture.", False),
        ("System operates without external dependencies.", False),
        ("Clients cannot connect using plaintext HTTP.", False),
        ("Feature X is deprecated and obsolete.", False),
        ("Protocol is active and supported.", True),
        ("Feature X is mandatory and required.", True)
    ]
    for text, expected_positive in samples:
        ast = extract_document_assertions(text, "test.md")
        assert len(ast["polarity_assertions"]) >= 1, f"Failed to extract polarity from: '{text}'"
        assert ast["polarity_assertions"][0]["is_positive"] == expected_positive, (
            f"Expected positive={expected_positive} for '{text}', got {ast['polarity_assertions'][0]['is_positive']}"
        )


def test_pairwise_contradiction_between_affirmative_and_prohibited():
    """
    Contradiction between 'mandatory' and 'forbidden'.
    """
    passages = [
        {
            "filename": "policy_a.md",
            "content": "Mutual TLS authentication is mandatory for internal microservices."
        },
        {
            "filename": "policy_b.md",
            "content": "Mutual TLS authentication is forbidden for internal microservices."
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] >= 1
    contradiction = result["contradictions"][0]
    assert contradiction["conflict_type"] == CONFLICT_POLARITY_INVERSION


def test_status_collision_active_vs_deprecated():
    """
    Status collision: 'active' vs 'deprecated'.
    """
    passages = [
        {
            "filename": "v1_manifest.json",
            "content": "Storage engine v1 is active in current deployments."
        },
        {
            "filename": "v2_manifest.json",
            "content": "Storage engine v1 is deprecated and obsolete."
        }
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["contradictions_count"] >= 1
    assert any(c["conflict_type"] == CONFLICT_STATUS_COLLISION for c in result["contradictions"])


def test_subtle_unit_assertions_and_normalization():
    """
    Test extraction and canonical normalization across various unit dimensions:
    Data storage (MB, GB, KB, TB, PB), Time (ms, s, min, hr), Frequency (Hz, MHz, GHz),
    Throughput (TPS, RPS, QPS), Currencies (USD, EUR, GBP).
    """
    test_cases = [
        ("The buffer is 1024MB.", "MB", 1024.0),
        ("The storage is 1GB.", "GB", 1.0),
        ("The latency is 500ms.", "MS", 500.0),
        ("The timeout is 0.5s.", "S", 0.5),
        ("The throughput is 2500rps.", "RPS", 2500.0),
        ("The query rate is 500qps.", "QPS", 500.0),
        ("The budget is $1500.", "USD", 1500.0),
        ("The license fee is €1200.", "EUR", 1200.0)
    ]
    for text, expected_unit, expected_val in test_cases:
        ast = extract_document_assertions(text, "sample.txt")
        nums = ast["numerical_assertions"]
        assert len(nums) >= 1
        assert nums[0]["unit"] == expected_unit
        assert nums[0]["value"] == expected_val


def test_cross_document_agreement_with_lexical_overlap():
    """
    Passages with shared topic keywords agree when statements are mutually consistent.
    """
    passages = [
        {
            "filename": "doc_a.txt",
            "content": "The maximum cache size is 1024MB per cluster node."
        },
        {
            "filename": "doc_b.txt",
            "content": "The maximum cache size is 1024MB per cluster node."
        }
    ]
    res = evaluate_cross_document_consensus(passages)
    assert res["consensus_level"] == HIGH_CONSENSUS
    assert res["agreements_count"] >= 1
    assert res["contradictions_count"] == 0


# ==============================================================================
# SECTION 3: EDGE CASES & RESILIENCE
# ==============================================================================

def test_empty_passage_list():
    """Empty passage list should return SINGLE_SOURCE with score 0.70 without throwing exceptions."""
    result = evaluate_cross_document_consensus([])
    assert result["consensus_level"] == SINGLE_SOURCE
    assert result["consensus_score"] == 0.70
    assert result["agreements_count"] == 0
    assert result["contradictions_count"] == 0
    assert result["contradictions"] == []
    assert result["resolved_claims"] == []
    assert result["dissenting_ledger"] == []
    assert result["pairwise_nli"] == []


def test_single_passage():
    """Single passage should return SINGLE_SOURCE with score 0.70 without throwing exceptions."""
    result = evaluate_cross_document_consensus([
        {"filename": "lone_doc.txt", "content": "Database pool size is 20 connections."}
    ])
    assert result["consensus_level"] == SINGLE_SOURCE
    assert result["consensus_score"] == 0.70
    assert result["agreements_count"] == 0
    assert result["contradictions_count"] == 0


def test_passages_with_identical_content():
    """Identical passages should yield 100% agreement / HIGH_CONSENSUS."""
    text = "The connection timeout is set to 30s across all cluster nodes."
    passages = [
        {"filename": "replica_1.md", "content": text},
        {"filename": "replica_2.md", "content": text},
        {"filename": "replica_3.md", "content": text}
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["consensus_level"] == HIGH_CONSENSUS
    assert result["consensus_score"] >= 0.95
    assert result["agreements_count"] >= 3
    assert result["contradictions_count"] == 0


def test_passages_with_no_numbers_or_entities():
    """Passages with pure conversational or non-factual prose."""
    passages = [
        {"filename": "intro1.txt", "content": "Welcome to the system. Please read the documentation carefully."},
        {"filename": "intro2.txt", "content": "Hello there! We hope you have a great experience using our platform."}
    ]
    result = evaluate_cross_document_consensus(passages)
    assert result["consensus_level"] in (NEUTRAL, HIGH_CONSENSUS)
    assert result["contradictions_count"] == 0


def test_passages_with_corrupt_or_missing_fields():
    """Passages containing None, empty strings, missing filenames, or missing metadata."""
    passages = [
        {"filename": "", "content": ""},
        {"content": None},
        {"filename": "valid.txt", "content": "The cache buffer is 512MB.", "metadata": None},
        {"filename": "valid2.txt", "content": "The cache buffer is 512MB."}
    ]
    # Should not raise exception and should gracefully process valid entries
    result = evaluate_cross_document_consensus(passages)
    assert "consensus_level" in result
    assert "consensus_score" in result
    assert isinstance(result["contradictions"], list)
    assert isinstance(result["resolved_claims"], list)


def test_extract_assertions_with_extreme_values():
    """Extraction with floats, large numbers, and special characters."""
    text = "The system processed 100,000,000 records with 0.0001% error rate at €0.00 cost in 0.5s."
    ast = extract_document_assertions(text, "extreme.md")
    nums = ast["numerical_assertions"]
    assert len(nums) >= 3

    assert any(math.isclose(n["value"], 100000000.0) for n in nums)
    assert any(math.isclose(n["value"], 0.0001) for n in nums)
    assert any(math.isclose(n["value"], 0.0) for n in nums)
    assert any(math.isclose(n["value"], 0.5) for n in nums)


def test_multi_source_consensus_boosting_formula_bounds():
    """Verify consensus boost score mathematical bounds and ceiling at 1.00."""
    w_high = [1.0, 1.0, 1.0]
    boost = compute_consensus_boost(w_high, agreements_count=10, gamma=0.15)
    assert boost == 1.00

    w_low = [0.35, 0.35]
    boost_low = compute_consensus_boost(w_low, agreements_count=0, gamma=0.15)
    assert math.isclose(boost_low, 0.35, abs_tol=1e-3)
