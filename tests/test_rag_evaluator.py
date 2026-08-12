import unittest
import os
import json
from src.domain.rag_evaluator import (
    evaluate_rag_faithfulness,
    run_metamorphic_rag_benchmark,
    export_benchmark_report
)

class TestRAGEvaluator(unittest.TestCase):
    def test_evaluates_faithfulness_and_precision(self):
        query = "What is quantum mechanics?"
        context = "Quantum mechanics is a fundamental theory in physics describing microscopic particles."
        response = "Quantum mechanics describes microscopic particles in physics."
        citations = [{"citation": "[Source: doc1.txt]", "confidence_score": 0.05}]

        res = evaluate_rag_faithfulness(query, response, citations, context)
        self.assertGreaterEqual(res["faithfulness_score"], 0.70)
        self.assertEqual(res["status"], "pass")

    def test_run_metamorphic_rag_benchmark(self):
        query = "vector search indexing"
        retrieved_docs = [{"id": 1, "filename": "vector.md", "content": "vector search indexing engine"}]
        res = run_metamorphic_rag_benchmark(query, retrieved_docs)
        self.assertIn("reciprocal_rank_score", res)
        self.assertEqual(res["status"], "pass")
        self.assertEqual(len(res["query_variants"]), 3)

    def test_export_benchmark_report(self):
        target_path = "docs/test_rag_benchmark_report.json"
        report = export_benchmark_report(target_path)
        self.assertEqual(report["audit_status"], "PASSED")
        self.assertTrue(os.path.exists(target_path))
        if os.path.exists(target_path):
            os.remove(target_path)

if __name__ == "__main__":
    unittest.main()
