import unittest
from src.domain.rag_engine import synthesize_speculative_drafts
from src.domain.temporal_rag_lineage import get_temporal_knowledge_lineage
from src.domain.hallucination_guard import evaluate_hallucination_risk
from fastapi.testclient import TestClient
from src.app.main import app

class TestSpeculativeLineageAndGuard(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_synthesize_speculative_drafts(self):
        passages = [{"filename": "p1.md", "content": "Sample context passage"}]
        res = synthesize_speculative_drafts("query", passages)
        self.assertEqual(res["status"], "success")
        self.assertIn("best_draft", res)

    def test_02_get_temporal_knowledge_lineage(self):
        res = get_temporal_knowledge_lineage()
        self.assertEqual(res["status"], "success")
        self.assertIn("timeline", res)

    def test_03_evaluate_hallucination_risk(self):
        res1 = evaluate_hallucination_risk("financial accounting", [])
        self.assertTrue(res1["should_refuse"])

        passages = [{"content": "financial accounting report"}]
        res2 = evaluate_hallucination_risk("financial accounting", passages)
        self.assertFalse(res2["should_refuse"])
        self.assertGreaterEqual(res2["confidence_score"], 0.65)

    def test_04_speculative_lineage_endpoints(self):
        res1 = self.client.post("/api/search/speculative-rag", json={"query": "test", "passages": [{"content": "hello"}]})
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.get("/api/knowledge/temporal-lineage")
        self.assertEqual(res2.status_code, 200)

        res3 = self.client.post("/api/search/hallucination-guard", json={"query": "accounting", "passages": [{"content": "accounting text"}]})
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
