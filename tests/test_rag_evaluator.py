import unittest
from src.domain.rag_evaluator import evaluate_rag_faithfulness

class TestRAGEvaluator(unittest.TestCase):
    def test_evaluates_faithfulness_and_precision(self):
        query = "What is quantum mechanics?"
        context = "Quantum mechanics is a fundamental theory in physics describing microscopic particles."
        response = "Quantum mechanics describes microscopic particles in physics."
        citations = [{"citation": "[Source: doc1.txt]", "confidence_score": 0.05}]

        res = evaluate_rag_faithfulness(query, response, citations, context)
        self.assertGreaterEqual(res["faithfulness_score"], 0.70)
        self.assertEqual(res["status"], "pass")

if __name__ == "__main__":
    unittest.main()
