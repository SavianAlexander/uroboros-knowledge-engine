"""
Automated Test Suite & Empirical Validation for Video-Derived Architecture:
1. Four Micro-Moments Intent Classification and Dynamic Routing (Know, Go/Locate, Do, Buy/Decide).
2. Five-Pillar Trust Taxonomy Ingestion Tagging and Doubt/Objection Query Boosting.
3. Multi-Source Consensus & Review Attribute Corroboration.
4. Dual-LLM Anti-Drift Fact-Checking & Hallucination Correction Engine.
"""

import unittest
import os
import sys
import tempfile
import time
import json
import logging

from src.infrastructure.database import init_db, get_db_connection, reset_db_connections, DB_FILE
from src.infrastructure.vector_engine import index_file, MiniVectorEngine
from src.domain.moment_classifier import MicroMoment, MicroMomentClassifier, DynamicPromptRouter
from src.domain.consensus_corroborator import MultiSourceCorroborator
from src.domain.anti_drift_verifier import AntiDriftVerifier, VerificationResult
from src.domain.situational_cross_reranker import SituationalCrossReranker
from src.core.domain.services import extract_chunk_attributes, semantic_markdown_chunker_hierarchical

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VIDEO_ARCH_TEST")


class TestRAGVideoArchitecture(unittest.TestCase):
    """Empirical test suite for Video-Derived Architecture upgrades."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        reset_db_connections()
        init_db()
        with get_db_connection(DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM files WHERE filepath LIKE '%Temp%' OR filepath LIKE '%tmp%'")
                conn.execute("DELETE FROM parent_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                conn.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
        MiniVectorEngine.reset_cache()

    def tearDown(self):
        reset_db_connections()

    # =========================================================================
    # A. Micro-Moments Classification & Routing Tests
    # =========================================================================

    def test_micro_moment_classifier_accuracy(self):
        """
        Test 1: Evaluate intent classification across representative queries.
        Assert >= 90% confidence on explicit moments.
        """
        test_queries = [
            ("How does vector quantization actually work under the hood?", MicroMoment.WANT_TO_KNOW),
            ("Find a local specialist in San Juan for repairing hydraulic pumps on CAT mini-excavators", MicroMoment.WANT_TO_GO_LOCATE),
            ("Step-by-step instructions to rebuild a corrupt SQLite WAL index", MicroMoment.WANT_TO_DO),
            ("Is Tool X enterprise tier worth the cost compared to open-source self-hosting?", MicroMoment.WANT_TO_BUY_DECIDE)
        ]

        for q_text, expected_moment in test_queries:
            t0 = time.perf_counter()
            res = MicroMomentClassifier.classify(q_text)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            logger.info(f"[MOMENT_CLASSIFICATION] Query='{q_text}' -> Moment={res.moment.value} (Conf={res.confidence:.2f}, Latency={latency_ms:.3f}ms)")
            self.assertEqual(res.moment, expected_moment, f"Failed moment classification for: {q_text}")
            self.assertGreaterEqual(res.confidence, 0.90, f"Confidence too low for: {q_text}")
            self.assertLess(latency_ms, 5.0, "Classification must be sub-5ms")

    def test_moment_driven_retrieval_routing(self):
        """
        Test 2: Verify that classified moments configure appropriate strategy modifiers and prompts.
        """
        # GO/LOCATE strategy
        go_res = MicroMomentClassifier.classify("Where can I find an authorized vendor in Seattle?")
        self.assertEqual(go_res.moment, MicroMoment.WANT_TO_GO_LOCATE)
        self.assertTrue(go_res.retrieval_strategy.get("filter_location"))
        self.assertTrue(go_res.retrieval_strategy.get("corroborate_reviews"))

        # DO strategy
        do_res = MicroMomentClassifier.classify("How to fix database locking error on Linux")
        self.assertEqual(do_res.moment, MicroMoment.WANT_TO_DO)
        self.assertTrue(do_res.retrieval_strategy.get("prefer_procedural_chunks"))

        # BUY/DECIDE strategy
        buy_res = MicroMomentClassifier.classify("Compare Pro subscription pricing vs Enterprise plan tiers")
        self.assertEqual(buy_res.moment, MicroMoment.WANT_TO_BUY_DECIDE)
        self.assertIn("pricing", buy_res.retrieval_strategy.get("boost_trust_pillars", []))

        # Dynamic System Prompt Router
        prompt_do = DynamicPromptRouter.get_system_prompt(MicroMoment.WANT_TO_DO)
        self.assertIn("tactical operations engineer", prompt_do.lower())
        prompt_buy = DynamicPromptRouter.get_system_prompt(MicroMoment.WANT_TO_BUY_DECIDE)
        self.assertIn("trade-off", prompt_buy.lower())

    # =========================================================================
    # B. 5-Pillar Trust Taxonomy Indexing & Scoring Tests
    # =========================================================================

    def test_trust_taxonomy_tagging_on_ingestion(self):
        """
        Test 3: Ingest documents containing pricing, problems, anti-personas, repair vs replace, and env prerequisites.
        Assert automatic classification of trust_type on chunks.
        """
        samples = [
            ("pricing_guide.md", "# Product Tiers\n\nStandard pricing is $49/mo per-user with annual billing discounts.", "pricing"),
            ("diagnostics.md", "# Troubleshooting\n\nDiagnosing socket timeout crash failure mode under heavy load.", "problems"),
            ("disqualifiers.md", "# Anti-Personas\n\nWho should avoid this tool: systems with strict sub-millisecond SLA requirements.", "not_a_fit"),
            ("lifecycle.md", "# Migration Strategy\n\nTrade-off decision matrix for repair vs replace threshold on legacy servers.", "repair_vs_replace"),
            ("environment.md", "# Climate Constraints\n\nOperating system and environment context prerequisites for freezing climate deployment.", "environment_context")
        ]

        for fname, text, expected_trust in samples:
            fpath = os.path.join(self.temp_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(text)

            index_file(fpath)

            # Verify chunk in DB
            with get_db_connection(DB_FILE) as conn:
                conn.row_factory = __import__('sqlite3').Row
                cursor = conn.cursor()
                cursor.execute("SELECT c.trust_type FROM file_chunks c JOIN files f ON c.file_id = f.id WHERE f.filename = ?", (fname,))
                rows = cursor.fetchall()
                self.assertTrue(len(rows) > 0, f"No chunks found for {fname}")
                detected_trust = rows[0]["trust_type"]
                logger.info(f"[TRUST_TAXONOMY_TAGGING] File='{fname}' -> Detected='{detected_trust}' (Expected='{expected_trust}')")
                self.assertEqual(detected_trust, expected_trust)

    def test_doubt_query_boosts_not_a_fit_and_problems(self):
        """
        Test 4: Query expressing doubt ('Why should I avoid X in freezing climate?')
        Assert not_a_fit and environment_context chunks receive score boost over generic overview.
        """
        generic_path = os.path.join(self.temp_dir, "generic_tankless_overview.md")
        with open(generic_path, "w", encoding="utf-8") as f:
            f.write("# EcoFlow Tankless Heater\n\nPremium water heating solution with high energy efficiency and modern design.")

        disqualifier_path = os.path.join(self.temp_dir, "tankless_disqualifiers.md")
        with open(disqualifier_path, "w", encoding="utf-8") as f:
            f.write("# Tankless Limitations & Anti-Personas\n\nWhen to avoid: Do not install in a freezing climate without dedicated pipe trace heating due to freezing failure risks.")

        index_file(generic_path)
        index_file(disqualifier_path)

        query = "Why should I avoid installing a tankless water heater in a freezing climate?"
        
        candidates = [
            {"id": 1, "filename": "generic_tankless_overview.md", "content": "EcoFlow Tankless Heater premium water heating solution with high energy efficiency", "trust_type": "general", "score": 0.50},
            {"id": 2, "filename": "tankless_disqualifiers.md", "content": "When to avoid: Do not install in a freezing climate without dedicated trace heating due to freezing failure risks", "trust_type": "not_a_fit", "score": 0.48}
        ]

        reranked = SituationalCrossReranker.rerank(query, candidates, min_relevance_threshold=0.0)

        logger.info(f"[TRUST_BOOST_TEST] Rank 1: {reranked[0]['filename']} (Score: {reranked[0]['cross_score']}) | Rank 2: {reranked[1]['filename']} (Score: {reranked[1]['cross_score']})")
        
        # Disqualifier document must be boosted to Rank #1
        self.assertEqual(reranked[0]["filename"], "tankless_disqualifiers.md")
        self.assertGreater(reranked[0]["cross_score"], reranked[1]["cross_score"])

    # =========================================================================
    # C. Multi-Source Consensus & Attribute Corroboration Tests
    # =========================================================================

    def test_multisource_attribute_corroboration(self):
        """
        Test 5: Index primary spec and third-party reviews.
        Assert MultiSourceCorroborator combines tiers and generates consensus authority score.
        """
        candidates = [
            {
                "id": 101,
                "doc_title": "CAT Mini-Excavator Manual",
                "parent_header": "Hydraulic Pump Spec",
                "content": "Variable displacement axial piston pump rated for 3,500 PSI continuous duty.",
                "source_type": "primary_doc",
                "cross_score": 0.85
            },
            {
                "id": 102,
                "doc_title": "Field Contractor Review 2026",
                "parent_header": "Heavy Duty Longevity",
                "content": "Tested hydraulic pump in San Juan quarry for 2,000 hours at 3,500 PSI without seal degradation.",
                "source_type": "third_party_corroboration",
                "cross_score": 0.82
            },
            {
                "id": 103,
                "doc_title": "Equipment Forum Fleet Post-Mortem",
                "parent_header": "Failure Rate Analysis",
                "content": "Fleet analysis confirms hydraulic pump failures only occur when fluid contamination exceeds ISO 18/16.",
                "source_type": "third_party_corroboration",
                "cross_score": 0.79
            }
        ]

        corroboration_res = MultiSourceCorroborator.corroborate(candidates, query="CAT excavator hydraulic pump reliability under load")

        logger.info(f"[CORROBORATION_STATUS] Level={corroboration_res['consensus_level']}, Multiplier={corroboration_res['consensus_multiplier']}")
        
        self.assertEqual(corroboration_res["status"], "CORROBORATED")
        self.assertEqual(corroboration_res["consensus_level"], "HIGH_CONSENSUS")
        self.assertEqual(corroboration_res["primary_count"], 1)
        self.assertEqual(corroboration_res["corroboration_count"], 2)
        self.assertIn("Tier 1: Primary Spec", corroboration_res["assembled_context"])
        self.assertIn("Tier 2: Third-Party Review", corroboration_res["assembled_context"])

    # =========================================================================
    # D. Dual-Model Synthesis & Anti-Drift Fact-Checking Tests
    # =========================================================================

    def test_anti_drift_verifier_passes_grounded_response(self):
        """
        Test 6: Pass a fully-grounded draft response to Verifier.
        Assert Verifier approves with status PASSED and drift_detected == False.
        """
        context = "The cache cluster supports up to 5,000 writes/sec per node with sub-5ms latency."
        draft = "The distributed cache cluster safely supports up to 5,000 writes/sec per node with sub-5ms latency."

        res: VerificationResult = AntiDriftVerifier.verify_response(context, draft)

        logger.info(f"[ANTI_DRIFT_PASSED] Status={res.status}, DriftDetected={res.drift_detected}, Conf={res.verification_confidence}")
        self.assertEqual(res.status, "PASSED")
        self.assertFalse(res.drift_detected)
        self.assertEqual(res.corrected_response, draft)

    def test_anti_drift_verifier_catches_and_corrects_hallucination(self):
        """
        Test 7: Pass a draft containing an ungrounded claim (100,000 writes/sec vs context limit of 5,000 writes/sec).
        Assert Verifier catches hallucination and corrects to match ground-truth context.
        """
        context = "The database cluster maintains an active write threshold of 5,000 writes/sec per partition."
        draft = "Our high-throughput database effortlessly handles 100,000 writes/sec per partition in production."

        res: VerificationResult = AntiDriftVerifier.verify_response(context, draft)

        logger.info(f"[ANTI_DRIFT_CORRECTED] Status={res.status}, Violations={res.violations}, Corrected='{res.corrected_response}'")
        
        self.assertEqual(res.status, "CORRECTED")
        self.assertTrue(res.drift_detected)
        self.assertIn("100,000 writes/sec", res.hallucinated_claims)
        self.assertIn("5,000 writes/sec", res.corrected_response)
        self.assertNotIn("100,000 writes/sec", res.corrected_response)


if __name__ == "__main__":
    unittest.main()
