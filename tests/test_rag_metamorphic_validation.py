"""
Adversarial Metamorphic & Next-Gen RAG Validation Verification Suite.
Covers ColBERT MaxSim, Matryoshka MRL Compression, and Self-Correction RAG Grounding.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.reranking import colbert_maxsim_score, rerank_documents_colbert
from src.domain.mrl_compressor import truncate_mrl_embedding, mrl_cosine_similarity
from src.domain.rag_grounding_guard import verify_rag_grounding, compute_ngram_overlap


class TestAdversarialRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_colbert_maxsim_reranking(self):
        query_tokens = [[0.8, 0.2, 0.0], [0.1, 0.9, 0.0]]
        doc1_tokens = [[0.8, 0.2, 0.0], [0.1, 0.9, 0.0]]  # Exact match
        doc2_tokens = [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]  # Partial match
        
        candidates = [
            {"id": "doc2", "token_embeddings": doc2_tokens},
            {"id": "doc1", "token_embeddings": doc1_tokens}
        ]
        
        reranked = rerank_documents_colbert(query_tokens, candidates)
        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0]["id"], "doc1")
        self.assertGreater(reranked[0]["colbert_maxsim_score"], reranked[1]["colbert_maxsim_score"])

    def test_02_matryoshka_mrl_compression(self):
        orig_vec = [0.5] * 1536
        truncated_256 = truncate_mrl_embedding(orig_vec, target_dim=256)
        
        self.assertEqual(len(truncated_256), 256)
        
        # Test similarity calculation
        sim = mrl_cosine_similarity(orig_vec, orig_vec, target_dim=256)
        self.assertAlmostEqual(sim, 1.0, delta=0.01)

    def test_03_rag_hallucination_guard(self):
        source = ["Quantum entanglement allows instant state correlation across spatial distances."]
        grounded_resp = "Quantum entanglement allows state correlation across spatial distances."
        hallucinated_resp = "The stock market indices increased sharply due to interest rate cuts."
        
        res_good = verify_rag_grounding(grounded_resp, source, threshold=0.4)
        self.assertEqual(res_good["overall_status"], "grounded")
        self.assertEqual(len(res_good["hallucination_warnings"]), 0)

        res_bad = verify_rag_grounding(hallucinated_resp, source, threshold=0.4)
        self.assertEqual(res_bad["overall_status"], "hallucination_risk")
        self.assertGreater(len(res_bad["hallucination_warnings"]), 0)

    def test_04_colbert_rerank_endpoint(self):
        payload = {
            "query_tokens": [[0.5, 0.5]],
            "candidates": [
                {"id": "c1", "token_embeddings": [[0.5, 0.5]]},
                {"id": "c2", "token_embeddings": [[0.1, 0.0]]}
            ]
        }
        res = self.client.post("/api/rag/colbert/rerank", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["results"][0]["id"], "c1")

    def test_05_mrl_compress_endpoint(self):
        payload = {
            "embeddings": [[0.1] * 512, [0.2] * 512],
            "target_dim": 128
        }
        res = self.client.post("/api/rag/mrl/compress", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["target_dim"], 128)
        self.assertEqual(len(data["compressed_embeddings"][0]), 128)

    def test_06_grounding_verify_endpoint(self):
        payload = {
            "llm_response": "Astrophysics studies celestial bodies.",
            "source_chunks": ["Astrophysics is the branch of astronomy that studies celestial bodies."],
            "threshold": 0.3
        }
        res = self.client.post("/api/rag/grounding/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["overall_status"], "grounded")


if __name__ == "__main__":
    unittest.main()
