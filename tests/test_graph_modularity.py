import unittest
from src.domain.graph_reasoning import detect_community_clusters, discover_knowledge_gaps

class TestGraphModularity(unittest.TestCase):
    def test_detect_community_clusters(self):
        res = detect_community_clusters()
        self.assertIn("status", res)
        self.assertEqual(res["status"], "success")
        self.assertIn("modularity_score", res)
        self.assertIn("total_communities", res)
        self.assertIsInstance(res["clusters"], list)

    def test_discover_knowledge_gaps(self):
        res = discover_knowledge_gaps()
        self.assertIn("status", res)
        self.assertEqual(res["status"], "success")
        self.assertIn("missing_concepts", res)
        self.assertIn("orphan_documents", res)

if __name__ == "__main__":
    unittest.main()
