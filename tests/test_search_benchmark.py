import unittest
from fastapi.testclient import TestClient
from src.app.main import app

class TestSearchBenchmark(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_search_benchmark_endpoint(self):
        res = self.client.get("/api/search/benchmark?query=financial")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["query"], "financial")
        self.assertIn("rrf_hybrid_latency_ms", data)
        self.assertIn("vector_cosine_latency_ms", data)
        self.assertIn("total_rrf_hits", data)

if __name__ == "__main__":
    unittest.main()
