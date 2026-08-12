import unittest
from src.domain.graph_reasoning import discover_knowledge_gaps

class TestGraphReasoning(unittest.TestCase):
    def test_discovers_knowledge_gaps(self):
        res = discover_knowledge_gaps()
        self.assertEqual(res["status"], "success")
        self.assertIn("missing_concepts", res)
        self.assertIn("orphan_documents", res)

if __name__ == "__main__":
    unittest.main()
