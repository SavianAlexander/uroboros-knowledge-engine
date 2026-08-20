"""
Adversarial Stress Harness for Milestone M1 (F1-F4).
Empirically stress-tests Epistemic Evidentiary Tiering (F1), Authority-Weighted RRF (F2),
Temporal Validity (F3), and Exponential Staleness Decay (F4).
"""

import math
from datetime import datetime, date
import pytest

from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)
from src.domain.temporal_validity import (
    detect_temporal_validity,
    compute_temporal_decay,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS
)
from src.domain.grounded_retrieval_engine import (
    GroundedRetrievalEngine,
    execute_grounded_retrieval
)


# ============================================================================
# Section 1: Epistemic Evidentiary Tier Classifier (F1) Adversarial Tests
# ============================================================================

import unittest


class TestEpistemicTieringTemporalValidityStress(unittest.TestCase):
    def test_f1_empty_and_none_inputs(self):
        """Verify classifier handles None, empty string, and whitespace without exceptions."""
        tier, weight = classify_source_epistemic_tier(None)
        assert tier == TIER_4_COMMENTARY
        assert weight == 0.35

        tier, weight = classify_source_epistemic_tier("")
        assert tier == TIER_4_COMMENTARY
        assert weight == 0.35

        tier, weight = classify_source_epistemic_tier("   ", content_snippet=None, metadata=None)
        assert tier == TIER_4_COMMENTARY
        assert weight == 0.35


    def test_f1_cjk_and_zero_width_unicode(self):
        """Verify Unicode NFC normalization with non-Latin scripts and zero-width spaces."""
        # CJK unicode characters mixed with standard identifier
        cjk_filename = "关于RFC9110标准文档.txt"
        tier, weight = classify_source_epistemic_tier(cjk_filename)
        assert tier == TIER_1_PRIMARY
        assert weight == 1.00

        # Right-to-left / zero-width space characters surrounding keyword
        zw_filename = "\u200brfc9110\u200b.pdf"
        tier, weight = classify_source_epistemic_tier(zw_filename)
        assert tier == TIER_1_PRIMARY
        assert weight == 1.00


    def test_f1_deeply_nested_paths_and_path_separators(self):
        """Verify deep directory hierarchies and mixed Windows/POSIX slashes."""
        deep_windows_path = "D:\\projects\\2026\\enterprise\\architecture\\specs\\v2\\service_api_spec.json"
        tier, weight = classify_source_epistemic_tier(deep_windows_path)
        assert tier == TIER_1_PRIMARY  # .json extension
        assert weight == 1.00

        deep_posix_path = "/var/log/archive/temp/notes/unrelated_document.txt"
        tier, weight = classify_source_epistemic_tier(deep_posix_path)
        assert tier == TIER_4_COMMENTARY
        assert weight == 0.35


    def test_f1_statutory_regex_precision(self):
        """Verify statutory citation boundaries in text snippets."""
        # Real U.S. Code citation
        t_usc, w_usc = classify_source_epistemic_tier(
            "citation.txt",
            content_snippet="According to 18 U.S.C. 1030, unauthorized access to protected computers is unlawful."
        )
        assert t_usc == TIER_1_PRIMARY
        assert w_usc == 1.00

        # CFR citation
        t_cfr, w_cfr = classify_source_epistemic_tier(
            "reg.txt",
            content_snippet="Under 45 CFR § 164.312 technical safeguards must be enforced."
        )
        assert t_cfr == TIER_1_PRIMARY
        assert w_cfr == 1.00


    # ============================================================================
    # Section 2: Temporal Validity & Exponential Staleness (F3 & F4) Tests
    # ============================================================================

    def test_f2_temporal_future_and_ancient_dates(self):
        """Test boundary years: future (2099), ancient (1900), and epoch boundary (1970)."""
        current_year = datetime.now().year

        # Future year 2099: age clamped to 0.0, decay = 1.0 (no negative age anomaly)
        decay_future = compute_temporal_decay(document_year_or_date=2099, domain="general")
        assert decay_future == 1.00

        # Ancient year 1900: hits the 0.05 floor, not 0.0 or negative
        decay_ancient = compute_temporal_decay(document_year_or_date=1900, domain="tech_spec")
        assert decay_ancient == 0.05

        # Epoch boundary 1970
        decay_1970 = compute_temporal_decay(document_year_or_date=1970, domain="academic")
        assert 0.05 <= decay_1970 <= 0.10


    def test_f2_temporal_decay_mathematical_monotonicity(self):
        """Verify decay is strictly monotonic decreasing with respect to document age."""
        current_year = datetime.now().year
        decays = [
            compute_temporal_decay(document_year_or_date=current_year - i, domain="tech_spec")
            for i in range(10)
        ]
        for i in range(len(decays) - 1):
            assert decays[i] >= decays[i+1], f"Monotonicity violation at step {i}: {decays[i]} < {decays[i+1]}"


    def test_f2_temporal_invalid_inputs_and_malformed_dates(self):
        """Test None, invalid types, unparseable strings, negative half-life."""
        decay_none = compute_temporal_decay(document_year_or_date=None)
        assert decay_none == 1.00

        decay_garbage = compute_temporal_decay(document_year_or_date="not-a-real-date-at-all-xyz")
        assert decay_garbage == 1.00

        decay_zero_hl = compute_temporal_decay(document_year_or_date=2020, half_life_days=0)
        assert 0.05 <= decay_zero_hl <= 1.00

        decay_neg_hl = compute_temporal_decay(document_year_or_date=2020, half_life_days=-100)
        assert 0.05 <= decay_neg_hl <= 1.00

        decay_unknown_domain = compute_temporal_decay(document_year_or_date=2023, domain="quantum_alien_tech")
        assert 0.05 <= decay_unknown_domain <= 1.00


    def test_f2_superseding_detection_edge_cases(self):
        """Test varied phrasing and punctuation for superseding detection."""
        content_multi = "RFC 9110\nObsoletes: 7230, 7231, 7232, 7233, 7234, 7235."
        res = detect_temporal_validity(content_multi)
        assert res["is_superseded"] is True
        assert "7230" in res["superseded_by"]

        content_narrative = "Note: this framework was replaced by NewFramework v2 in late 2024."
        res_nar = detect_temporal_validity(content_narrative)
        assert res_nar["is_superseded"] is True
        assert "NewFramework v2" in res_nar["superseded_by"]


    # ============================================================================
    # Section 3: Authority-Weighted RRF Ranking (F2) Stress Tests
    # ============================================================================

    def test_f3_rrf_empty_channels(self):
        """Test empty lexical list, empty dense list, and both empty."""
        res_both_empty = compute_authority_weighted_rrf(lexical_ranks=[], dense_ranks=[])
        assert res_both_empty == []

        single_lex = [{"id": "doc1", "filename": "spec.pdf", "rank": 1}]
        res_dense_empty = compute_authority_weighted_rrf(lexical_ranks=single_lex, dense_ranks=[])
        assert len(res_dense_empty) == 1
        assert res_dense_empty[0]["id"] == "doc1"
        assert res_dense_empty[0]["final_rank"] == 1

        single_dense = [{"id": "doc2", "filename": "rfc9110.pdf", "rank": 1}]
        res_lex_empty = compute_authority_weighted_rrf(lexical_ranks=[], dense_ranks=single_dense)
        assert len(res_lex_empty) == 1
        assert res_lex_empty[0]["id"] == "doc2"
        assert res_lex_empty[0]["final_rank"] == 1


    def test_f3_rrf_k_parameter_bounds(self):
        """Test smoothing constant k values: k=1, k=60, k=10000."""
        candidates = [
            {"id": "doc1", "filename": "rfc9110.pdf", "rank": 1},
            {"id": "doc2", "filename": "blog.md", "rank": 2}
        ]

        res_60 = compute_authority_weighted_rrf(candidates, candidates, k=60)
        assert len(res_60) == 2
        assert res_60[0]["id"] == "doc1"

        res_large_k = compute_authority_weighted_rrf(candidates, candidates, k=10000)
        assert len(res_large_k) == 2
        assert res_large_k[0]["id"] == "doc1"

        res_k1 = compute_authority_weighted_rrf(candidates, candidates, k=1)
        assert len(res_k1) == 2
        assert res_k1[0]["id"] == "doc1"


    def test_f3_rrf_missing_fields_and_unranked_candidates(self):
        """Test candidate dictionaries with missing id, missing filename, extra attributes."""
        malformed_candidates = [
            {"custom_id": 999, "content": "only content here"},
            {"filename": "some_doc.txt", "metadata": {}},
            {"id": "valid_doc", "filename": "api_spec.yaml", "rank": 1}
        ]

        res = compute_authority_weighted_rrf(lexical_ranks=malformed_candidates, dense_ranks=[])
        assert len(res) == 3
        assert all("grounded_score" in d for d in res)
        assert all("final_rank" in d for d in res)
        assert res[0]["final_rank"] == 1


    def test_f3_rrf_large_candidate_stress(self):
        """Stress test with 1,000 candidate documents in each channel."""
        lex_1000 = [{"id": f"doc_{i}", "filename": f"doc_{i}.txt", "rank": i + 1} for i in range(1000)]
        dense_1000 = [{"id": f"doc_{999 - i}", "filename": f"doc_{999 - i}.txt", "rank": i + 1} for i in range(1000)]

        res = compute_authority_weighted_rrf(lexical_ranks=lex_1000, dense_ranks=dense_1000, k=60)
        assert len(res) == 1000
        assert res[0]["final_rank"] == 1
        assert res[-1]["final_rank"] == 1000
        for idx in range(len(res) - 1):
            assert res[idx]["grounded_score"] >= res[idx+1]["grounded_score"]


    # ============================================================================
    # Section 4: Grounded Retrieval Engine Coordinator (F4) Integration Tests
    # ============================================================================

    def test_f4_engine_zero_evidence_refusal(self):
        """Verify engine returns structured refusal when 0 candidate passages are provided."""
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        res = engine.evaluate_grounding("test query", candidate_passages=[])
        assert res["status"] == "refusal"
        assert res["reason"] == "ZERO_EVIDENCE"
        assert res["overall_grounded_confidence"] == 0.0
        assert "diagnostics" in res
        assert len(res["diagnostics"]["knowledge_gaps"]) > 0


    def test_f4_engine_boundary_invariant_veto(self):
        """Verify that a physical invariant violation forces confidence to 0 and triggers refusal."""
        engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
        candidates = [
            {
                "id": "doc1",
                "filename": "quantum_spec.pdf",
                "epistemic_tier": TIER_1_PRIMARY,
                "epistemic_weight": 1.0,
                "staleness_coefficient": 1.0,
                "rank": 1,
                "content": "Superluminal optical fiber 5000km with 5ms latency."
            }
        ]
        impossible_claim = {
            "type": "OPTICAL_LATENCY",
            "distance_km": 5000.0,
            "reported_latency_ms": 5.0
        }
        res = engine.evaluate_grounding("superluminal latency", candidate_passages=candidates, generated_claim=impossible_claim)
        assert res["status"] == "refusal"
        assert "BOUNDARY_INVARIANT_VETO" in res["reason"]
        assert res["overall_grounded_confidence"] == 0.0
        assert len(res["diagnostics"]["invariant_violations"]) > 0


    # ============================================================================
    # Section 5: Challenger Remediation Regression Tests (Defects 1 - 4)
    # ============================================================================

    def test_remediation_defect_1_commentary_filename_priority(self):
        """Verify commentary filenames citing standards are strictly classified as TIER_4_COMMENTARY."""
        probes = [
            "blog_about_rfc9110.txt",
            "iso_notes.scratch",
            "unverified_statute_claims.memo",
            "in_a_sec_notes.txt",
            "draft_protocol_rfc9110.md",
            "todo_iso27001_tasks.txt",
            "team_chat_about_statute.txt"
        ]
        for probe in probes:
            tier, weight = classify_source_epistemic_tier(probe)
            assert tier == TIER_4_COMMENTARY, f"Expected TIER_4_COMMENTARY for {probe}, got {tier}"
            assert weight == 0.35, f"Expected weight 0.35 for {probe}, got {weight}"


    def test_remediation_defect_2_string_publication_year_coercion(self):
        """Verify detect_temporal_validity safely parses string years from metadata without TypeError."""
        res = detect_temporal_validity("Document text", metadata={"publication_year": "2023"})
        assert res["publication_year"] == 2023
        assert isinstance(res["age_years"], float)
        assert res["age_years"] >= 0.0

        res_invalid_str = detect_temporal_validity("Document text", metadata={"publication_year": "invalid_year"})
        assert res_invalid_str["publication_year"] is None
        assert res_invalid_str["age_years"] == 0.0


    def test_remediation_defect_3_rrf_non_positive_k_guard(self):
        """Verify compute_authority_weighted_rrf enforces k >= 1 and prevents ZeroDivisionError."""
        candidates = [{"id": "doc1", "rank": 1}, {"id": "doc2", "rank": 2}]
        # k <= 0 or negative
        for test_k in [-10, -1, 0]:
            res = compute_authority_weighted_rrf(candidates, candidates, k=test_k)
            assert len(res) == 2
            assert all("grounded_score" in d and d["grounded_score"] > 0 for d in res)


    def test_remediation_defect_4_rrf_null_candidate_fields(self):
        """Verify compute_authority_weighted_rrf handles candidate dictionaries with explicit None fields."""
        malformed_candidates = [
            {"id": "doc_null_rank", "rank": None},
            {"id": "doc_null_weight", "rank": 1, "epistemic_tier": "TIER_1_PRIMARY", "epistemic_weight": None},
            {"id": "doc_null_staleness", "rank": 1, "staleness_coefficient": None},
            {"id": "doc_null_all", "rank": None, "epistemic_weight": None, "staleness_coefficient": None}
        ]
        res = compute_authority_weighted_rrf(lexical_ranks=malformed_candidates, dense_ranks=[])
        assert len(res) == 4
        for doc in res:
            assert isinstance(doc["final_rank"], int)
            assert isinstance(doc["grounded_score"], float)
            assert isinstance(doc["epistemic_weight"], float)
            assert isinstance(doc["staleness_coefficient"], float)

