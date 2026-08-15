"""
Comparative RAG Validation Verification Suite.
Covers Hyper-Graph Knowledge Router, Dynamic Sparse-Dense Fusion Reranker, and Entropy Noise Masker.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.hypergraph_router import route_hypergraph_query
from src.domain.sparse_dense_fusion import rerank_sparse_dense_fusion
from src.domain.contextual_noise_mask import mask_low_entropy_noise


class TestComparativeRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_hypergraph_router(self):
        res = route_hypergraph_query("Find user contract details", ["User", "Contract"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["complexity"], "O(1)")
        self.assertGreater(res["total_matches"], 0)

    def test_02_sparse_dense_fusion_reranker(self):
        chunks = [
            {"id": "chk_1", "text": "def test(): pass", "sparse_score": 0.9, "dense_score": 0.4, "colbert_score": 0.5},
            {"id": "chk_2", "text": "general text", "sparse_score": 0.2, "dense_score": 0.8, "colbert_score": 0.7}
        ]
        res = rerank_sparse_dense_fusion("def test() code function", chunks)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["computed_weights"]["alpha"], 0.5)

    def test_03_entropy_noise_masker(self):
        text = "Important data here.\nAll rights reserved.\nConfidential and Proprietary.\nMore data."
        res = mask_low_entropy_noise(text)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["token_reduction_pct"], 0.0)

    def test_04_endpoints(self):
        res_hg = self.client.post("/api/rag/hypergraph/route", json={"query": "Test query", "target_entities": ["User"]})
        self.assertEqual(res_hg.status_code, 200)

        res_nm = self.client.post("/api/rag/noise/mask-entropy", json={"text_chunk": "Copyright (c) 2026. Data."})
        self.assertEqual(res_nm.status_code, 200)


if __name__ == "__main__":
    unittest.main()
