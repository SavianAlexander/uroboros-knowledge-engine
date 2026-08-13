import time
import unittest
from src.domain.recency_decay import apply_recency_decay
from src.domain.vector_health_monitor import audit_vector_health
from fastapi.testclient import TestClient
from src.app.main import app

class TestRecencyAndVectorHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_apply_recency_decay(self):
        now = time.time()
        cands = [
            {"filename": "old.md", "rrf_score": 0.05, "mtime": now - (86400 * 60)}, # 60 days old
            {"filename": "new.md", "rrf_score": 0.05, "mtime": now - (86400 * 1)}   # 1 day old
        ]
        reranked = apply_recency_decay(cands, decay_half_life_days=30.0)
        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0]["filename"], "new.md")

    def test_02_audit_vector_health(self):
        res = audit_vector_health()
        self.assertEqual(res["status"], "success")
        self.assertIn("coverage_pct", res)

    def test_03_recency_and_vector_health_endpoints(self):
        res1 = self.client.get("/api/system/vector-health")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "success")

        res2 = self.client.post("/api/search/recency-rerank", json={"candidates": [{"filename": "doc.txt", "score": 0.1}], "decay_half_life_days": 30.0})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
