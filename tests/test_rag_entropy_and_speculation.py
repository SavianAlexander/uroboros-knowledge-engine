"""
RAG Entropy & Speculative Synthesis Verification Suite.
Covers Dynamic Entropy-Based Semantic Boundary Chunking and Speculative Multi-Hypothesis Synthesis.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.entropy_chunker import chunk_by_semantic_entropy
from src.domain.rag_engine import synthesize_speculative_rag, generate_hypotheses_from_chunks


class TestRAGEntropyAndSpeculation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_entropy_boundary_chunker(self):
        sample_doc = (
            "Quantum entanglement is a phenomenon in physics. "
            "Particles remain correlated regardless of distance. "
            "The stock market experienced heavy volatility today. "
            "Federal Reserve interest rates remained unchanged."
        )
        chunks = chunk_by_semantic_entropy(sample_doc, distance_threshold=0.5, max_chunk_size=300)
        self.assertGreater(len(chunks), 0)
        self.assertIn("content", chunks[0])
        self.assertIn("boundary_entropy_score", chunks[0])

    def test_02_speculative_rag_synthesis(self):
        query = "Quantum Computing"
        chunks = ["Quantum computing utilizes qubits for parallel computation.", "Superconducting circuits are used in quantum hardware."]
        
        result = synthesize_speculative_rag(query, chunks)
        self.assertEqual(result["status"], "success")
        self.assertIn("synthesized_answer", result)
        self.assertGreater(result["confidence_score"], 0.0)
        self.assertEqual(len(result["hypotheses"]), 3)

    def test_03_entropy_chunking_endpoint(self):
        payload = {
            "text": "First topic statement. Second related statement. Completely unrelated financial market update.",
            "distance_threshold": 0.5,
            "max_chunk_size": 400
        }
        res = self.client.post("/api/rag/chunking/entropy", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("chunks", data)
        self.assertGreater(data["total"], 0)

    def test_04_speculative_rag_endpoint(self):
        payload = {
            "query": "Neural Networks",
            "source_chunks": ["Neural networks consist of interconnected artificial neurons.", "Backpropagation updates weights during training."]
        }
        res = self.client.post("/api/rag/speculative/synthesize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("synthesized_answer", data)
        self.assertIn("hypotheses", data)


if __name__ == "__main__":
    unittest.main()
