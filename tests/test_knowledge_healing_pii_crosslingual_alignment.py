import unittest
from src.domain.knowledge_self_healing import audit_knowledge_self_healing
from src.domain.pii_privacy_guard import redact_pii_from_text
from src.domain.rag_engine import align_cross_lingual_query
from fastapi.testclient import TestClient
from src.app.main import app

class TestHealingPiiAndCrossLingual(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_audit_knowledge_self_healing(self):
        res = audit_knowledge_self_healing()
        self.assertEqual(res["status"], "success")
        self.assertIn("health_score", res)

    def test_02_redact_pii_from_text(self):
        sample = "User SSN is 123-45-6789 and API key is sk_live_abc1234567890xyz. Email: admin@test.com"
        redacted = redact_pii_from_text(sample)
        self.assertEqual(redacted["status"], "success")
        self.assertIn("[REDACTED_SSN]", redacted["redacted_text"])
        self.assertIn("[REDACTED_API_KEY]", redacted["redacted_text"])
        self.assertIn("[REDACTED_EMAIL]", redacted["redacted_text"])

    def test_03_align_cross_lingual_query(self):
        q = "informe financiero de contabilidad"
        aligned = align_cross_lingual_query(q)
        self.assertTrue(aligned["translated"])
        self.assertIn("financial", aligned["aligned_query"])

    def test_04_healing_pii_endpoints(self):
        res1 = self.client.get("/api/system/knowledge-healing")
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.post("/api/search/redact-pii", json={"text": "SSN: 111-22-3333"})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

        res3 = self.client.get("/api/search/cross-lingual?query=informe")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
