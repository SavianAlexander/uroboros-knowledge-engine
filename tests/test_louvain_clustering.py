import unittest
from src.domain.louvain_clustering import apply_louvain_communities

class TestLouvainClustering(unittest.TestCase):
    def test_assigns_community_id_and_colors(self):
        nodes = [
            {"id": "doc1", "filename": "doc1.txt"},
            {"id": "doc2", "filename": "doc2.txt"},
            {"id": "doc3", "filename": "doc3.txt"},
        ]
        edges = [
            {"source": "doc1", "target": "doc2", "weight": 1},
        ]
        partitioned = apply_louvain_communities(nodes, edges)
        self.assertEqual(len(partitioned), 3)
        self.assertIn("community_id", partitioned[0])
        self.assertIn("community_color", partitioned[0])
        # Connected nodes doc1 and doc2 should share the same community_id
        self.assertEqual(partitioned[0]["community_id"], partitioned[1]["community_id"])

if __name__ == "__main__":
    unittest.main()
