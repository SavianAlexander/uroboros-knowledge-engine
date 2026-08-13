import unittest
from src.domain.conflict_resolver import detect_and_resolve_conflicts
from src.domain.predictive_precacher import precache_graph_neighborhood
from src.domain.bandit_query_router import bandit_select_pipeline, record_bandit_feedback

class TestConflictPrecacheAndBandit(unittest.TestCase):

    def test_01_detect_and_resolve_conflicts(self):
        res = detect_and_resolve_conflicts()
        self.assertEqual(res["status"], "success")
        self.assertIn("conflicts_found", res)

    def test_02_precache_graph_neighborhood(self):
        res = precache_graph_neighborhood("non_existent_doc")
        self.assertIn("status", res)

    def test_03_bandit_select_pipeline_and_feedback(self):
        res = bandit_select_pipeline("FACTUAL")
        self.assertEqual(res["status"], "success")
        self.assertIn("selected_pipeline", res)

        fb = record_bandit_feedback(res["selected_pipeline"], True)
        self.assertEqual(fb["status"], "success")

    def test_04_conflict_precache_bandit_endpoints(self):
        from fastapi.testclient import TestClient
        from src.app.main import app
        client = TestClient(app)

        res1 = client.get("/api/knowledge/resolve-conflicts")
        self.assertEqual(res1.status_code, 200)

        res2 = client.post("/api/search/precache-context", json={"source_doc": "test"})
        self.assertEqual(res2.status_code, 200)

        res3 = client.get("/api/search/bandit-route")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
