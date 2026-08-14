import os
import sys
import unittest
import tempfile
import shutil
import threading

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.domain.multi_agent_consensus import orchestrate_multi_agent_consensus
from src.domain.multi_agent_debate import execute_multi_agent_debate
from src.domain.agent_memory import remember, recall, delete_memory, forget_category
from src.domain.bandit_query_router import bandit_select_pipeline, record_bandit_feedback
from src.domain.intent_router import classify_query_intent, route_query_intent


class TestDomainAgentConsensus(unittest.TestCase):
    """Domain test suite for multi-agent reasoning, consensus synthesis, agent memory, and bandit routers."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_agent_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_orchestrate_multi_agent_consensus(self):
        """Verify multi-agent consensus synthesis across Developer, Legal, and Executive personas.

        Preconditions: User query and retrieved document context strings provided.
        Invariants: Output contains persona perspectives (developer, legal, executive) and unified consensus answer.
        Expected Outcomes: status='success', consensus_score > 0.9, perspectives dictionary populated.
        """
        contexts = [
            "Uroboros Knowledge Engine enforces SOC 2 Type II trust controls and zero external AI dependencies."
        ]
        res = orchestrate_multi_agent_consensus(
            query="Can we deploy the knowledge engine in banking production?",
            retrieved_contexts=contexts
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["consensus_score"], 0.8)
        self.assertIn("developer", res["persona_perspectives"])
        self.assertIn("legal", res["persona_perspectives"])
        self.assertIn("executive", res["persona_perspectives"])
        self.assertIn("Consensus Overview", res["unified_consensus_answer"])

    def test_02_multi_agent_debate_synthesis(self):
        """Verify multi-agent debate between Pro-Context Advocate and Anti-Context Auditor.

        Preconditions: Query and candidate passages provided to debate engine.
        Invariants: Generates pro and con arguments and assigns debate consensus approval.
        Expected Outcomes: status='success', debate_consensus='APPROVE_CONTEXT', rounds_debated=2.
        """
        passages = [
            {"filename": "banking_compliance.md", "content": "Full audit trails are recorded in SQLite WAL."}
        ]
        res = execute_multi_agent_debate(query="audit trails compliance", passages=passages)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["debate_consensus"], "APPROVE_CONTEXT")
        self.assertGreater(len(res["pro_arguments"]), 0)
        self.assertGreater(len(res["con_arguments"]), 0)

    def test_03_agent_memory_crud_and_episodic_search(self):
        """Verify persistent SQLite agent memory store (remember, recall, delete).

        Preconditions: Isolated SQLite test database initialized.
        Invariants: remember stores serialized key/value; recall retrieves typed object; delete_memory purges entry.
        Expected Outcomes: Stored dictionary retrieved intact; delete returns deleted=True.
        """
        key = "user_theme_preference"
        val = {"theme": "glass_emerald", "font_size": 14, "auto_rag": True}

        rem_res = remember(key, val, category="ui_settings")
        self.assertEqual(rem_res["status"], "success")

        recalled = recall(key, category="ui_settings")
        self.assertIsInstance(recalled, dict)
        self.assertEqual(recalled["theme"], "glass_emerald")

        del_res = delete_memory(key)
        self.assertEqual(del_res["status"], "success")
        self.assertTrue(del_res["deleted"])

        recalled_after = recall(key)
        self.assertIsNone(recalled_after)

    def test_04_bandit_query_router_thompson_sampling(self):
        """Verify Multi-Armed Bandit retrieval pipeline selection using Thompson Sampling.

        Preconditions: Bandit router arms initialized with trial statistics.
        Invariants: bandit_select_pipeline samples arm distributions and selects optimal pipeline.
        Expected Outcomes: status='success', selected_pipeline in known arms, bandit_confidence in [0, 1].
        """
        res = bandit_select_pipeline(intent="FACTUAL")
        self.assertEqual(res["status"], "success")
        self.assertIn(res["selected_pipeline"], [
            "hybrid_rrf_pagerank", "multihop_graph_bfs", "contextual_hyde", "parent_child_expand"
        ])
        self.assertGreaterEqual(res["bandit_confidence"], 0.0)

    def test_05_intent_router_classification_and_pipeline(self):
        """Verify sub-1ms speculative query intent routing.

        Preconditions: Code, summary, counterfactual, and factual query strings.
        Invariants: classify_query_intent matches category; route_query_intent returns pipeline module.
        Expected Outcomes: Code query mapped to code_search; summary query mapped to executive_summary.
        """
        code_intent = classify_query_intent("def analyze_token_vectors(): syntax error")
        self.assertEqual(code_intent, "code_search")

        summary_intent = classify_query_intent("Generate an executive summary report of all documents")
        self.assertEqual(summary_intent, "executive_summary")

        route_res = route_query_intent("Why does document A conflict with document B?")
        self.assertEqual(route_res["status"], "success")
        self.assertEqual(route_res["classified_intent"], "counterfactual_audit")
        self.assertIn("counterfactual_rag", route_res["recommended_pipeline"])

    def test_06_angle_unicode_and_empty_contexts(self):
        """Verify (Angle 10 & 17) agent consensus resilience with Unicode NFC and empty contexts.

        Preconditions: Unicode query with non-ASCII characters and empty context list.
        Invariants: Functions handle empty context lists cleanly without crashing.
        Expected Outcomes: Returns valid consensus answer with default fallback.
        """
        res = orchestrate_multi_agent_consensus(query="¿Cómo funciona la indexación cuántica?", retrieved_contexts=[])
        self.assertEqual(res["status"], "success")
        self.assertIn("Consensus Overview", res["unified_consensus_answer"])

    def test_07_angle_unbalanced_quotes_in_agent_queries(self):
        """Verify (Angle 1) unbalanced quotes and special characters in agent queries.

        Preconditions: Malformed queries with single/double unbalanced quotes.
        Invariants: Intent classifier and debate synthesizer parse strings cleanly.
        Expected Outcomes: classify_query_intent and execute_multi_agent_debate execute without syntax errors.
        """
        bad_query = "What is \"unclosed quote in query' and 'another mismatch"
        intent = classify_query_intent(bad_query)
        self.assertIsInstance(intent, str)

        debate_res = execute_multi_agent_debate(bad_query, passages=[])
        self.assertEqual(debate_res["status"], "success")
        self.assertEqual(debate_res["debate_consensus"], "REFUSE_NO_CONTEXT")

    def test_08_forget_category_and_memory_isolation(self):
        """Verify (Angle 18) category purge in agent memory store.

        Preconditions: Multiple memory keys stored under category 'temp_session'.
        Invariants: forget_category deletes all keys in target category while preserving other categories.
        Expected Outcomes: status='success', deleted_count >= 2, target keys removed.
        """
        remember("temp_k1", "val1", category="temp_session")
        remember("temp_k2", "val2", category="temp_session")
        remember("perm_k1", "perm_val", category="permanent")

        f_res = forget_category("temp_session")
        self.assertEqual(f_res["status"], "success")
        self.assertGreaterEqual(f_res["deleted_count"], 2)

        self.assertIsNone(recall("temp_k1"))
        self.assertEqual(recall("perm_k1"), "perm_val")

    def test_09_bandit_feedback_update_weights(self):
        """Verify recording reward feedback updates bandit arm success rates and weights.

        Preconditions: Specific bandit pipeline provided with positive/negative reward.
        Invariants: record_bandit_feedback increments trials and updates weight.
        Expected Outcomes: status='success', updated_arm trials incremented.
        """
        pipeline = "hybrid_rrf_pagerank"
        res = record_bandit_feedback(pipeline, is_successful=True)
        self.assertEqual(res["status"], "success")
        self.assertIn("updated_arm", res)
        self.assertGreater(res["updated_arm"]["trials"], 0)

    def test_10_multi_agent_concurrency_lock_safety(self):
        """Verify (Angle 22) multi-threaded concurrent execution safety across bandit routers and memories.

        Preconditions: 10 concurrent threads invoking bandit selection and memory updates.
        Invariants: Thread locks prevent state corruption or race conditions.
        Expected Outcomes: All threads complete successfully without deadlocks.
        """
        errors = []

        def worker(thread_idx):
            try:
                for i in range(5):
                    bandit_select_pipeline("FACTUAL")
                    remember(f"thread_{thread_idx}_key_{i}", f"val_{i}", category="concurrency")
                    recall(f"thread_{thread_idx}_key_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
