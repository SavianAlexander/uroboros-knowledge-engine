"""
Comprehensive End-to-End Integration Test Suite for Grounded Retrieval Engine.
Integrates:
- Epistemic Tiering (M1)
- Temporal Validity & Staleness Decay (M1)
- Dense Propositional Decomposition (M2)
- Cross-Document Consensus Matrix (M3)
- Boundary Invariant Guards (M4)
- Grounding Scorecard & Refusal Gate (M5)
"""

import pytest
import math
from typing import List, Dict, Any

from src.domain.grounded_retrieval_engine import (
    GroundedRetrievalEngine,
    execute_grounded_retrieval,
    evaluate_grounding_for_claim,
    classify_source_epistemic_tier,
    detect_temporal_validity,
    decompose_into_propositions,
    evaluate_cross_document_consensus,
    evaluate_all_boundary_invariants,
    compute_grounding_scorecard,
    KnowledgeGapDiagnosticReport,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY,
    REFUSAL_THRESHOLD,
    STATUS_ACCEPTED,
    STATUS_REFUSED
)


class TestGroundedRetrievalEngineEndToEnd:

    def test_full_pipeline_accepted_grounded_query(self):
        """
        Tests complete pipeline from query to decomposition, consensus, and scorecard:
        Tier 1 RFC 9110 specification with active status yields ACCEPTED / GROUNDED verdict.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        raw_text_1 = "The HTTP 200 OK status code indicates that the request has succeeded. Payload represents response."
        raw_text_2 = "HTTP 200 OK status code signifies successful request execution under standard semantics."

        passages = [
            {"filename": "rfc9110_http_semantics.pdf", "content": raw_text_1, "rank": 1},
            {"filename": "rfc9110_part2.pdf", "content": raw_text_2, "rank": 2}
        ]

        res = engine.evaluate_grounding(
            query="HTTP 200 OK status code semantics",
            candidate_passages=passages
        )

        assert res["status"] == "success"
        assert res["is_grounded"] is True
        assert res["refusal_status"] is False
        assert res["overall_grounded_confidence"] >= 0.80
        assert res["epistemic_tier_average"] == 1.00
        assert res["temporal_validity_average"] >= 0.95
        assert len(res["passages"]) == 2
        assert res["diagnostics"]["knowledge_gaps"] == [] or len(res["diagnostics"]["epistemic_deficits"]) == 0

    def test_full_pipeline_tier4_commentary_refusal(self):
        """
        Tests that a query supported solely by Tier 4 informal commentary is REFUSED
        due to insufficient evidentiary weight (< 0.65).
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {"filename": "dev_chat_log.txt", "content": "I think the server timeout might be 60 seconds.", "rank": 1},
            {"filename": "scratch_notes.txt", "content": "General unverified notes on architecture.", "rank": 2}
        ]

        res = engine.evaluate_grounding(
            query="server timeout configuration",
            candidate_passages=passages
        )

        assert res["status"] == "refusal"
        assert res["is_grounded"] is False
        assert res["refusal_status"] is True
        assert res["overall_grounded_confidence"] < 0.65
        assert "HALLUCINATION_REFUSAL_GATE" in res["reason"]
        assert len(res["diagnostic_report"]["epistemic_deficits"]) >= 1

    def test_full_pipeline_superseded_document_decay_refusal(self):
        """
        Tests that an outdated superseded document receives severe staleness penalties
        and triggers refusal when no active primary source corroborates it.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {
                "filename": "legacy_api_v1_spec.md",
                "content": "Specification published 2015. Superseded by API v3 specification.",
                "rank": 1
            }
        ]

        res = engine.evaluate_grounding(
            query="API v1 specification framing",
            candidate_passages=passages
        )

        assert res["status"] == "refusal"
        assert res["temporal_validity_average"] <= 0.40
        assert any("SUPERSEDED" in d for d in res["diagnostic_report"]["temporal_deficits"])

    def test_full_pipeline_unresolved_contradiction_refusal(self):
        """
        Tests that an unresolvable factual contradiction between equal-tier sources
        depresses the consensus score and triggers the refusal gate.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {"filename": "blog_a.md", "content": "The maximum cache TTL is 3600 seconds.", "rank": 1},
            {"filename": "blog_b.md", "content": "The maximum cache TTL is 86400 seconds.", "rank": 2}
        ]

        res = engine.evaluate_grounding(
            query="cache TTL limit",
            candidate_passages=passages
        )

        assert res["status"] == "refusal"
        assert res["consensus_score"] <= 0.50
        assert len(res["diagnostic_report"]["dissenting_ledger"]) >= 1

    def test_full_pipeline_physical_invariant_binary_veto(self):
        """
        Tests that any physical boundary invariant violation (e.g. FTL optical propagation)
        vetoes the scorecard with score 0.0 regardless of Tier 1 primary sources.
        """
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP specification.", "rank": 1},
            {"filename": "iso27001.pdf", "content": "Security standard.", "rank": 2}
        ]
        ftl_claim = {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 1.0}

        res = engine.evaluate_grounding(
            query="transpacific network latency",
            candidate_passages=passages,
            generated_claim=ftl_claim
        )

        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0
        assert res["invariant_multiplier"] == 0.0
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert len(res["diagnostic_report"]["invariant_violations"]) >= 1


class TestTopLevelExecutionAPIs:

    def test_execute_grounded_retrieval_with_passages(self):
        """Verifies top-level execute_grounded_retrieval function with explicit passages."""
        passages = [
            {"filename": "fastapi_spec.md", "content": "FastAPI routes are defined via decorators.", "rank": 1}
        ]
        res = execute_grounded_retrieval("fastapi routing", passages=passages, top_k=3)
        assert "overall_grounded_confidence" in res
        assert "diagnostic_report" in res
        assert res["status"] in ("success", "refusal")

    def test_execute_grounded_retrieval_empty_query(self):
        """Verifies refusal handling for empty or whitespace queries."""
        res = execute_grounded_retrieval("   ", passages=[])
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0

    def test_evaluate_grounding_for_claim_valid(self):
        """Verifies evaluate_grounding_for_claim with physically valid claim and Tier 1 docs."""
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP 200 status.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        valid_claim = "The server responds with HTTP 200 on success."
        res = evaluate_grounding_for_claim(claim=valid_claim, retrieved_passages=passages)
        assert res["is_grounded"] is True
        assert res["grounding_status"] == STATUS_ACCEPTED

    def test_evaluate_grounding_for_claim_invalid_invariant(self):
        """Verifies evaluate_grounding_for_claim fails immediately on physical violation."""
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP spec.", "epistemic_weight": 1.0, "staleness_coefficient": 1.0}
        ]
        invalid_claim = {"type": "CARNOT", "t_hot_k": 500.0, "t_cold_k": 300.0, "claimed_efficiency": 0.95}
        res = evaluate_grounding_for_claim(claim=invalid_claim, retrieved_passages=passages)
        assert res["is_grounded"] is False
        assert res["grounding_score"] == 0.0
        assert res["grounding_status"] == STATUS_REFUSED


class TestMultiPhasePipelineChaining:

    def test_dense_propositions_to_consensus_to_scorecard(self):
        """
        Tests end-to-end multi-phase chaining:
        1. Raw document text -> decompose into propositions
        2. Format into candidate passages
        3. Cross-document consensus
        4. Invariant evaluation
        5. Scorecard & Refusal Gate
        """
        doc1_text = "# Database Architecture\n## Concurrency\nSQLite operates in WAL mode with single writer and multi-readers."
        doc2_text = "# System Guidelines\n## Storage\nSQLite operates in WAL mode with single writer and multi-readers."

        props1 = decompose_into_propositions(doc1_text, "ArchDoc.md")
        props2 = decompose_into_propositions(doc2_text, "GuideDoc.md")

        passages = [
            {
                "filename": props1[0]["proposition_id"],
                "content": props1[0]["statement"],
                "epistemic_tier": TIER_2_TECH_SPEC,
                "epistemic_weight": 0.85,
                "staleness_coefficient": 1.0
            },
            {
                "filename": props2[0]["proposition_id"],
                "content": props2[0]["statement"],
                "epistemic_tier": TIER_2_TECH_SPEC,
                "epistemic_weight": 0.85,
                "staleness_coefficient": 1.0
            }
        ]

        # Evaluate consensus across extracted propositions
        consensus = evaluate_cross_document_consensus(passages)
        assert consensus["agreements_count"] >= 1

        # Evaluate scorecard
        scorecard = compute_grounding_scorecard(passages=passages)
        assert scorecard["is_grounded"] is True
        assert scorecard["grounding_score"] >= 0.80
        assert scorecard["diagnostic_report"]["refusal_status"] is False
