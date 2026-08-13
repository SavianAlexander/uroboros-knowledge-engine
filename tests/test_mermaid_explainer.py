import unittest
from src.domain.graph_mermaid_generator import generate_mermaid_graph
from src.domain.rerank_score_explainer import explain_candidate_score
from fastapi.testclient import TestClient
from src.app.main import app

class TestMermaidAndExplainer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_generate_mermaid_graph(self):
        res = generate_mermaid_graph()
        self.assertEqual(res["status"], "success")
        self.assertIn("mermaid_code", res)
        self.assertIn("graph TD;", res["mermaid_code"])

    def test_02_explain_candidate_score(self):
        cand = {
            "filename": "annual_report.md",
            "fts_rank": 2,
            "pagerank_score": 0.005,
            "recency_multiplier": 0.95,
            "final_score": 0.065
        }
        explained = explain_candidate_score(cand)
        self.assertEqual(explained["status"], "success")
        self.assertIn("explanation", explained)

    def test_03_mermaid_and_explainer_endpoints(self):
        res1 = self.client.get("/api/graph/mermaid")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "success")

        res2 = self.client.post("/api/search/explain-score", json={
            "candidate": {"filename": "test.md", "final_score": 0.08}
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
