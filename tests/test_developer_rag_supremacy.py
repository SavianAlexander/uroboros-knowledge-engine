"""
Developer RAG Supremacy Verification Suite.
Covers Golden RAG Evaluator, Semantic Document Diff Comparator, and Query Intent Classifier.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.rag_evaluator import evaluate_rag_triad
from src.domain.semantic_doc_diff import compare_semantic_doc_diff
from src.domain.query_intent_classifier import classify_query_intent


class TestDeveloperRAGSupremacy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_rag_triad_evaluator(self):
        query = "Quantum Entanglement"
        answer = "Quantum entanglement correlates states over distance."
        contexts = ["Quantum entanglement allows instant state correlation over spatial distances."]
        
        res = evaluate_rag_triad(query, answer, contexts)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["faithfulness"], 0.5)
        self.assertTrue(res["benchmark_passed"])

    def test_02_semantic_doc_diff(self):
        old_text = "Section 1: Initial security policy. Section 2: Data retention 30 days."
        new_text = "Section 1: Initial security policy. Section 2: Data retention 90 days. Section 3: Encryption required."
        
        res = compare_semantic_doc_diff(old_text, new_text)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_added"], 0)
        self.assertGreater(res["similarity_ratio"], 0.0)

    def test_03_query_intent_classifier(self):
        res_code = classify_query_intent("def function_name() import api")
        self.assertEqual(res_code["intent"], "code_search")

        res_math = classify_query_intent("revenue quarter profit margin table")
        self.assertEqual(res_math["intent"], "tabular_math")

        res_summary = classify_query_intent("executive overview briefing report")
        self.assertEqual(res_summary["intent"], "analytical_summary")

    def test_04_rag_eval_endpoint(self):
        payload = {
            "query": "Neural Networks",
            "answer": "Neural networks use artificial neurons.",
            "retrieved_contexts": ["Neural networks consist of interconnected artificial neurons."]
        }
        res = self.client.post("/api/rag/eval/benchmark", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("overall_ragas_score", data)

    def test_05_semantic_diff_endpoint(self):
        payload = {
            "old_doc_text": "Clause 1: Old policy text.",
            "new_doc_text": "Clause 1: New policy text updated."
        }
        res = self.client.post("/api/rag/diff/semantic", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_06_query_intent_endpoint(self):
        payload = {"query": "class DatabaseConnection import sqlite3"}
        res = self.client.post("/api/rag/intent/classify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["intent"], "code_search")


if __name__ == "__main__":
    unittest.main()
