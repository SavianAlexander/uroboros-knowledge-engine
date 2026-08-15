import unittest
from src.domain.decomposed_hybrid_rag import decompose_query, compress_context_chunks, execute_hybrid_decomposed_search
from fastapi.testclient import TestClient
from src.app.main import app

class TestDecomposedHybridRagEngine(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_decompose_query(self):
        q = "International Financial Reporting Standards vs Generally Accepted Accounting Principles"
        parts = decompose_query(q)
        self.assertGreater(len(parts), 1)

    def test_02_compress_context_chunks(self):
        chunks = [
            "Accounting standards regulate corporate financial reporting worldwide.",
            "Accounting standards regulate corporate financial reporting worldwide.",
            "Zero-dependency software architectures eliminate supply chain vulnerabilities."
        ]
        compressed = compress_context_chunks(chunks, similarity_threshold=0.8)
        self.assertEqual(len(compressed), 2)

    def test_03_execute_hybrid_decomposed_search(self):
        res = execute_hybrid_decomposed_search("accounting standards", top_k=3)
        self.assertEqual(res["status"], "success")
        self.assertIn("top_candidates", res)
        self.assertIn("compression_stats", res)

    def test_04_decomposed_rag_endpoint(self):
        res = self.client.get("/api/search/decomposed-rag?query=accounting&top_k=3")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("sub_queries", data)

    def test_05_legacy_sota_rag_endpoint_alias(self):
        res = self.client.get("/api/search/sota-rag?query=accounting&top_k=3")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("sub_queries", data)

if __name__ == "__main__":
    unittest.main()
