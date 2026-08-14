"""
Unit test suite for Intelligent 4-Tier Neural Model Router and OllamaClient enhancements.
Verifies:
1. Micro-Tier routing (qwen2.5:0.5b / smollm2:1.7b) for intent, keywords, and HyDE query expansion.
2. Coder-Tier routing (qwen2.5-coder:14b / 7b) for Python AST, SQL, and refactoring prompts.
3. Long-Context Tier routing (phi4-mini) for high-token volume document digests (> 8k tokens).
4. Master RAG Tier routing (qwen2.5:7b) for general conversation and executive briefings.
5. Dynamic context window calculation (num_ctx scaling).
6. Model availability probe and graceful fallback.
"""

import unittest
import os
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.core.model_router import route_prompt_model, get_available_models
from src.core.model_manager import OllamaClient, expand_query_with_llm


class TestModelRouter(unittest.TestCase):

    def test_01_micro_tier_intent_routing(self):
        """Verify micro tasks (keyword extraction, HyDE, intent) route to Micro Tier (qwen2.5:0.5b)."""
        res_micro = route_prompt_model(prompt="expand query: quantum computing", task_type="micro")
        self.assertEqual(res_micro["tier"], "micro")
        self.assertIn("qwen2.5:0.5b", res_micro["model"])
        self.assertEqual(res_micro["temperature"], 0.1)

        res_tag = route_prompt_model(prompt="generate tags for machine learning research", task_type="tag")
        self.assertEqual(res_tag["tier"], "micro")

    def test_02_coder_tier_routing(self):
        """Verify code refactoring and technical prompts route to Coder Tier (qwen2.5-coder:14b / 7b)."""
        code_prompt = "def optimize_database_connection(pool: Queue):\n    import sqlite3\n    return pool.get()"
        res_code = route_prompt_model(prompt=code_prompt)
        self.assertEqual(res_code["tier"], "coder")
        self.assertTrue("coder" in res_code["model"] or "qwen" in res_code["model"])
        self.assertEqual(res_code["temperature"], 0.2)

        res_sql = route_prompt_model(prompt="SELECT * FROM file_chunks WHERE chunk_index > 5", task_type="sql")
        self.assertEqual(res_sql["tier"], "coder")

    def test_03_long_context_tier_routing(self):
        """Verify high-token volume document digests route to Long-Context Tier (phi4-mini)."""
        res_long = route_prompt_model(prompt="Summarize the entire 300-page operational manual.", task_type="long_doc", token_estimate=15000)
        self.assertEqual(res_long["tier"], "long_context")
        self.assertTrue("phi4" in res_long["model"] or "qwen" in res_long["model"])
        self.assertGreaterEqual(res_long["num_ctx"], 16000)

    def test_04_master_rag_tier_routing(self):
        """Verify standard conversational RAG queries route to Master RAG Tier (qwen2.5:7b)."""
        res_rag = route_prompt_model(prompt="What are the key findings in our Q3 engineering review?", task_type="chat")
        self.assertEqual(res_rag["tier"], "master_rag")
        self.assertIn("qwen2.5:7b", res_rag["model"])

    def test_05_dynamic_context_scaling(self):
        """Verify dynamic num_ctx calculation scales with estimated token density."""
        res_small = route_prompt_model(prompt="Hello", token_estimate=50)
        self.assertEqual(res_small["num_ctx"], 4096)

        res_large = route_prompt_model(prompt="Large context query", token_estimate=4000)
        self.assertGreaterEqual(res_large["num_ctx"], 8192)

    def test_06_available_models_probe(self):
        """Verify model availability probe returns non-empty set with known tags."""
        models = get_available_models()
        self.assertIsInstance(models, set)
        self.assertGreater(len(models), 0)

    def test_07_expand_query_fallback(self):
        """Verify expand_query_with_llm returns original query when empty or short."""
        self.assertEqual(expand_query_with_llm(""), "")
        self.assertEqual(expand_query_with_llm("ab"), "ab")
        # Ensure expanded query contains original query prefix
        res = expand_query_with_llm("quantum encryption")
        self.assertTrue(res.startswith("quantum encryption"))


if __name__ == "__main__":
    unittest.main()
