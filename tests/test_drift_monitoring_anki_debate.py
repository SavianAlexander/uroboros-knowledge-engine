import unittest
from src.domain.semantic_drift_monitor import audit_semantic_concept_drift
from src.domain.synthetic_qa_generator import extract_empirical_qa_triples
from src.domain.multi_agent_debate import execute_multi_agent_debate
from fastapi.testclient import TestClient
from src.app.main import app

class TestDriftDebateAndAnki(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_audit_semantic_concept_drift(self):
        res = audit_semantic_concept_drift("test")
        self.assertEqual(res["status"], "success")

    def test_02_synthesize_qa_cards(self):
        doc = "Project Phoenix is a resilient local knowledge engine that operates with zero cloud dependencies."
        res = extract_empirical_qa_triples(doc)
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["triples"]), 0)

    def test_03_execute_multi_agent_debate(self):
        passages = [{"filename": "doc.md", "content": "Context argument text"}]
        res = execute_multi_agent_debate("financial audit", passages)
        self.assertEqual(res["status"], "success")
        self.assertIn("debate_consensus", res)

    def test_04_drift_debate_anki_endpoints(self):
        res1 = self.client.get("/api/knowledge/semantic-drift?term=architecture")
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.post("/api/knowledge/generate-flashcards", json={"passages": [{"content": "[[Concept]]"}]})
        self.assertEqual(res2.status_code, 200)

        res3 = self.client.post("/api/search/multi-agent-debate", json={"query": "test", "passages": [{"content": "text"}]})
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
