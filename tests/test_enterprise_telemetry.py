import unittest
from src.domain.system_telemetry import gather_system_telemetry
from src.domain.near_duplicate_detector import detect_near_duplicates, compute_shingles, jaccard_similarity
from src.domain.graph_pagerank import compute_graph_pagerank
from fastapi.testclient import TestClient
from src.app.main import app

class TestEnterpriseTelemetry(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_gather_system_telemetry(self):
        res = gather_system_telemetry()
        self.assertEqual(res["status"], "healthy")
        self.assertIn("runtime", res)
        self.assertIn("database", res)

    def test_02_minhash_jaccard_similarity(self):
        shingles_a = compute_shingles("Accounting standards regulate corporate financial reporting", k=2)
        shingles_b = compute_shingles("Accounting standards regulate corporate financial balance sheets", k=2)
        sim = jaccard_similarity(shingles_a, shingles_b)
        self.assertGreater(sim, 0.5)

    def test_03_detect_near_duplicates(self):
        res = detect_near_duplicates(similarity_threshold=0.5)
        self.assertEqual(res["status"], "success")
        self.assertIn("duplicate_pairs", res)

    def test_04_compute_graph_pagerank(self):
        res = compute_graph_pagerank()
        self.assertEqual(res["status"], "success")
        self.assertIn("rankings", res)

    def test_05_telemetry_and_graph_endpoints(self):
        res1 = self.client.get("/api/system/telemetry")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "healthy")

        res2 = self.client.get("/api/vault/duplicates?threshold=0.5")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

        res3 = self.client.get("/api/graph/pagerank")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
