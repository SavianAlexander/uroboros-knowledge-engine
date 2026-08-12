import unittest
from src.domain.louvain_clustering import apply_louvain_communities
from src.domain.graph_reasoning import discover_knowledge_gaps

class TestGraphUpgrades(unittest.TestCase):
    def test_apply_louvain_communities(self):
        nodes = [
            {"id": "doc1", "label": "Doc 1"},
            {"id": "doc2", "label": "Doc 2"},
            {"id": "doc3", "label": "Doc 3"}
        ]
        edges = [
            {"source": "doc1", "target": "doc2"}
        ]
        result = apply_louvain_communities(nodes, edges)
        self.assertEqual(len(result), 3)
        self.assertIn("community_id", result[0])
        self.assertIn("community_color", result[0])
        # doc1 and doc2 should share the same community
        self.assertEqual(result[0]["community_id"], result[1]["community_id"])

    def test_discover_knowledge_gaps_structure(self):
        res = discover_knowledge_gaps()
        self.assertIn("missing_concepts", res)
        self.assertIn("orphan_documents", res)
        self.assertIn("gap_count", res)
        self.assertEqual(res["status"], "success")

if __name__ == "__main__":
    unittest.main()
