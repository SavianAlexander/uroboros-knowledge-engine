"""
World-Class AI Validation Verification Suite.
Covers Auto-Weight Tuner, Synthetic QA Generator, AST Code RAG, Multimodal Visual Canvas, SSE Event Formatter, Counterfactual Simulator, SLA Circuit Breaker, and Cryptographic Audit Ledger.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.auto_weight_tuner import optimize_search_parameters
from src.domain.synthetic_qa_generator import generate_synthetic_qa_triples
from src.domain.ast_code_rag import parse_codebase_ast
from src.domain.visual_canvas_rag import extract_visual_canvas_regions
from src.domain.sse_sync_stream import format_sse_event
from src.domain.counterfactual_rag import simulate_counterfactual_scenario
from src.domain.sla_circuit_breaker import execute_with_sla_circuit_breaker
from src.domain.crypto_audit_ledger import append_crypto_audit_block, verify_crypto_chain_integrity


class TestFrontierAIValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_auto_weight_tuner(self):
        feedback = [{"score": 0.40}, {"score": 0.50}]
        res = optimize_search_parameters(feedback)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["adjustment_applied"])

    def test_02_synthetic_qa_generator(self):
        text = "Quantum computing leverages superposition and entanglement for rapid calculation."
        res = generate_synthetic_qa_triples(text)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_generated"], 0)

    def test_03_ast_code_rag(self):
        code = "import os\nclass Model:\n    pass\ndef run_query():\n    pass"
        res = parse_codebase_ast(code)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(len(res["functions"]), 1)
        self.assertIn("os", res["imports"])

    def test_04_visual_canvas_rag(self):
        layout = {
            "text_blocks": [{"text": "Sample title paragraph", "bbox": [0, 0, 100, 50]}],
            "images": [{"caption": "Architecture diagram", "bbox": [0, 100, 200, 300]}]
        }
        res = extract_visual_canvas_regions(layout)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["visual_regions"]), 2)

    def test_05_counterfactual_simulator(self):
        query = "Project details"
        contexts = ["Context 1 text", "Context 2 text", "Context 3 text"]
        res = simulate_counterfactual_scenario(query, contexts, [1])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["active_context_count"], 2)

    def test_06_sla_circuit_breaker(self):
        # High latency -> Degraded fallback
        res_high = execute_with_sla_circuit_breaker(
            primary_func=lambda: "Primary",
            fallback_func=lambda: "Fallback",
            latency_ms=120.0,
            max_sla_ms=50.0
        )
        self.assertTrue(res_high["circuit_tripped"])
        self.assertEqual(res_high["status"], "degraded_fallback")

        # Low latency -> Primary
        res_low = execute_with_sla_circuit_breaker(
            primary_func=lambda: "Primary",
            fallback_func=lambda: "Fallback",
            latency_ms=25.0,
            max_sla_ms=50.0
        )
        self.assertFalse(res_low["circuit_tripped"])
        self.assertEqual(res_low["status"], "success")

    def test_07_crypto_audit_ledger(self):
        res1 = append_crypto_audit_block("query 1", "answer 1", ["ctx1"])
        res2 = append_crypto_audit_block("query 2", "answer 2", ["ctx2"])
        self.assertEqual(res1["status"], "success")
        self.assertEqual(res2["status"], "success")
        self.assertTrue(verify_crypto_chain_integrity())

    def test_08_endpoints(self):
        res_ast = self.client.post("/api/rag/code/ast-parse", json={"code_snippet": "def foo(): pass"})
        self.assertEqual(res_ast.status_code, 200)
        self.assertEqual(res_ast.json()["status"], "success")

        res_crypto = self.client.post("/api/rag/audit/append-crypto", json={"query": "q", "answer": "a", "contexts": ["c"]})
        self.assertEqual(res_crypto.status_code, 200)
        self.assertEqual(res_crypto.json()["status"], "success")


if __name__ == "__main__":
    unittest.main()
