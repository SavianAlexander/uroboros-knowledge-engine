"""
Governance RAG Validation Verification Suite.
Covers Autonomous Index Self-Healing, Cross-Lingual Semantic Alignment, and PII Redaction Guard.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.index_self_healing import audit_index_health, execute_index_self_healing
from src.domain.multilingual_rag import align_cross_lingual_query
from src.domain.privacy_anonymizer import anonymize_text_pii


class TestGovernanceRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_index_self_healing(self):
        health = audit_index_health()
        self.assertIn("status", health)
        self.assertIn("fragmentation_pct", health)

        heal_res = execute_index_self_healing()
        self.assertEqual(heal_res["status"], "success")
        self.assertIn("healed_version", heal_res)

    def test_02_cross_lingual_alignment(self):
        res = align_cross_lingual_query("algoritmo de busqueda y red neuronal", source_lang="es")
        self.assertEqual(res["status"], "success")
        self.assertIn("algorithm", res["aligned_query"])
        self.assertIn("search", res["aligned_query"])
        self.assertIn("neural network", res["aligned_query"])
        self.assertGreater(res["translations_applied"], 0)

    def test_03_privacy_anonymizer(self):
        raw_text = "Contact user@example.com with SSN 123-45-6789 on IP 192.168.1.50"
        res = anonymize_text_pii(raw_text)
        self.assertEqual(res["status"], "success")
        self.assertIn("[REDACTED_EMAIL]", res["anonymized_text"])
        self.assertIn("[REDACTED_SSN]", res["anonymized_text"])
        self.assertIn("[REDACTED_IP]", res["anonymized_text"])
        self.assertEqual(res["redactions_count"], 3)

    def test_04_self_heal_endpoint(self):
        res = self.client.post("/api/rag/governance/self-heal")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_05_cross_lingual_endpoint(self):
        payload = {"query": "busqueda de vectores", "source_lang": "es"}
        res = self.client.post("/api/rag/governance/cross-lingual", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("search", data["aligned_query"])

    def test_06_anonymize_endpoint(self):
        payload = {"text": "Send credentials to admin@company.com"}
        res = self.client.post("/api/rag/governance/anonymize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("[REDACTED_EMAIL]", data["anonymized_text"])


if __name__ == "__main__":
    unittest.main()
