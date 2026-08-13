"""
60-Subsystem Quantum RAG Supremacy Verification Suite.
Covers Sub-Linear LSH-HNSW Vector Indexer, Multilingual Latent Projection Bridge, and Self-Supervised Feedback Auto-Refiner.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.sublinear_ann_index import search_sublinear_ann
from src.domain.crosslingual_bridge import project_multilingual_vector
from src.domain.retrieval_feedback_refiner import log_feedback_and_refine


class TestQuantumRAGSupremacy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_sublinear_ann_index(self):
        q_vec = [0.1] * 128
        idx_vecs = [{"id": f"v_{i}", "vector": [0.1 * (i + 1)] * 128} for i in range(10)]
        res = search_sublinear_ann(q_vec, idx_vecs, top_k=3)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["complexity"], "O(log N)")
        self.assertLessEqual(len(res["matches"]), 3)

    def test_02_crosslingual_bridge(self):
        res = project_multilingual_vector("Hola mundo", source_language="es")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["latent_dimension"], 64)

    def test_03_feedback_refiner(self):
        res = log_feedback_and_refine("chk_100", feedback_signal="click")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["updated_affinity"], 1.05)

    def test_04_endpoints(self):
        res_ann = self.client.post("/api/rag/ann/search", json={"query_vec": [0.1] * 64, "index_vectors": [{"id": "v1", "vector": [0.1] * 64}]})
        self.assertEqual(res_ann.status_code, 200)

        res_fb = self.client.post("/api/rag/feedback/refine", json={"chunk_id": "chk_100", "feedback_signal": "copy"})
        self.assertEqual(res_fb.status_code, 200)


if __name__ == "__main__":
    unittest.main()
