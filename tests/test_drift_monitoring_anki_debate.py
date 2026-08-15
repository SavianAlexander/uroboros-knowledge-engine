import unittest
from src.domain.semantic_drift_monitor import audit_semantic_concept_drift
from src.domain.anki_card_synthesizer import synthesize_anki_flashcards
from src.domain.multi_agent_debate import execute_multi_agent_debate
from fastapi.testclient import TestClient
from src.app.main import app

class TestDriftDebateAndAnki(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_audit_semantic_concept_drift(self):
        res = audit_semantic_concept_drift("test")
        self.assertEqual(res["status"], "success")

    def test_02_synthesize_anki_flashcards(self):
        passages = [{"filename": "note.md", "content": "Referencing [[Project Phoenix]] concept."}]
        res = synthesize_anki_flashcards(passages)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["cards_generated"], 0)

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
