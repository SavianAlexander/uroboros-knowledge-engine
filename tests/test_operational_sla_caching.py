"""
Operational RAG Validation Verification Suite.
Covers Tabular Schema RAG Extractor, Temporal Recency Decay Scoring, and Tenant ACL Vector Isolation Guard.
"""

import unittest
import time
from fastapi.testclient import TestClient
from main import app
from src.domain.schema_rag import extract_tabular_schema_chunks
from src.domain.temporal_rag import apply_temporal_decay_scoring
from src.domain.acl_vector_guard import filter_candidates_by_acl


class TestOperationalRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_tabular_schema_extractor(self):
        table_markdown = (
            "| Quarter | Revenue | Profit |\n"
            "| --- | --- | --- |\n"
            "| Q1 2026 | $5.2M | $1.1M |\n"
            "| Q2 2026 | $6.1M | $1.4M |"
        )
        chunks = extract_tabular_schema_chunks(table_markdown)
        self.assertEqual(len(chunks), 2)
        self.assertIn("Quarter: Q1 2026", chunks[0]["content"])
        self.assertIn("Revenue: $5.2M", chunks[0]["content"])

    def test_02_temporal_decay_scoring(self):
        now = time.time()
        cands = [
            {"id": "old_doc", "score": 0.90, "timestamp": now - (365 * 86400)},  # 1 yr old
            {"id": "new_doc", "score": 0.85, "timestamp": now - (5 * 86400)}     # 5 days old
        ]
        scored = apply_temporal_decay_scoring(cands, half_life_days=90.0)
        self.assertEqual(len(scored), 2)
        # New doc should rank first due to recency decay
        self.assertEqual(scored[0]["id"], "new_doc")
        self.assertGreater(scored[0]["final_temporal_score"], scored[1]["final_temporal_score"])

    def test_03_tenant_acl_filter(self):
        cands = [
            {"id": "doc_tenantA", "tenant_id": "tenant_A", "allowed_roles": ["role:analyst"]},
            {"id": "doc_tenantB", "tenant_id": "tenant_B", "allowed_roles": ["role:analyst"]},
            {"id": "doc_global", "tenant_id": "global", "allowed_roles": ["role:analyst", "role:user"]}
        ]
        
        # Test Tenant A Analyst
        res_a = filter_candidates_by_acl(cands, user_tenant_id="tenant_A", user_roles=["role:analyst"])
        self.assertEqual(res_a["status"], "success")
        self.assertEqual(len(res_a["allowed_candidates"]), 2) # tenant_A and global
        self.assertEqual(res_a["blocked_count"], 1)

    def test_04_schema_rag_endpoint(self):
        payload = {"table_text": "| Name | Value |\n| --- | --- |\n| Item1 | 100 |"}
        res = self.client.post("/api/rag/operational/schema", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["total"], 0)

    def test_05_temporal_rag_endpoint(self):
        payload = {
            "candidates": [{"id": "c1", "score": 0.8, "timestamp": time.time()}],
            "half_life_days": 90.0
        }
        res = self.client.post("/api/rag/operational/temporal", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("final_temporal_score", data["scored_candidates"][0])

    def test_06_acl_filter_endpoint(self):
        payload = {
            "candidates": [{"id": "doc1", "tenant_id": "t1", "allowed_roles": ["role:user"]}],
            "user_tenant_id": "t1",
            "user_roles": ["role:user"]
        }
        res = self.client.post("/api/rag/operational/acl-filter", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["allowed_candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
