"""
Unit test suite for Empirically Grounded Retrieval & Epistemic Invariant Engine.
"""

import pytest
from src.domain.grounded_retrieval_engine import (
    classify_source_epistemic_tier,
    detect_temporal_validity,
    decompose_into_propositions,
    evaluate_cross_document_consensus,
    check_optical_latency_invariant,
    check_usl_scalability_invariant,
    check_carnot_efficiency_invariant,
    execute_grounded_retrieval
)


def test_epistemic_tier_classification():
    t1, w1 = classify_source_epistemic_tier("rfc9110_http_semantics.pdf")
    assert t1 == "TIER_1_PRIMARY"
    assert w1 == 1.00

    t2, w2 = classify_source_epistemic_tier("fastapi_rest_api_specification.md")
    assert t2 == "TIER_2_TECH_SPEC"
    assert w2 == 0.85

    t3, w3 = classify_source_epistemic_tier("Intermediate_Accounting_17th_Edition.pdf")
    assert t3 == "TIER_3_SECONDARY"
    assert w3 == 0.70

    t4, w4 = classify_source_epistemic_tier("scratch_notes.txt")
    assert t4 == "TIER_4_COMMENTARY"
    assert w4 == 0.35


def test_temporal_validity_and_superseding():
    content_superseded = "This protocol is superseded by RFC 9110 and should not be used in modern deployments."
    res = detect_temporal_validity(content_superseded, publication_year=2015)
    assert res["is_superseded"] is True
    assert "RFC 9110" in res["superseded_by"]
    assert res["staleness_coefficient"] <= 0.40

    content_active = "Current active ISO 27001 standard guidance for security operations."
    res_active = detect_temporal_validity(content_active, publication_year=2026)
    assert res_active["is_superseded"] is False
    assert res_active["staleness_coefficient"] >= 0.95


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
    usl_ok = check_usl_scalability_invariant(32, 0.05, 0.001, 10.0)
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
