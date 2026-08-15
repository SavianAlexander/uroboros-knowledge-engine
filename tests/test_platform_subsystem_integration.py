"""
50-Subsystem Platform Integration Validation Verification Suite.
Covers Multi-Agent Consensus Orchestrator, Autonomous Vector Drift Agent, Streaming Token Compressor, and System Health Telemetry Dashboard API.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.multi_agent_consensus import orchestrate_multi_agent_consensus
from src.domain.vector_drift_agent import audit_vector_index_drift
from src.domain.streaming_token_compressor import compress_streaming_tokens
from src.domain.system_health_telemetry import compute_system_health_telemetry


class TestPlatformIntegrationValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_multi_agent_consensus(self):
        query = "Architecture deployment plan"
        contexts = ["Context details for deployment"]
        res = orchestrate_multi_agent_consensus(query, contexts)
        self.assertEqual(res["status"], "success")
        self.assertIn("developer", res["persona_perspectives"])
        self.assertIn("legal", res["persona_perspectives"])
        self.assertIn("executive", res["persona_perspectives"])

    def test_02_vector_drift_agent(self):
        curr_centroids = [[0.1, 0.2], [0.3, 0.4]]
        new_embs = [[0.9, 0.9], [0.8, 0.8]]
        res = audit_vector_index_drift(curr_centroids, new_embs)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["rebalance_needed"])

    def test_03_streaming_token_compressor(self):
        text = "Basically in order to optimize performance it should be noted that we run fast."
        res = compress_streaming_tokens(text)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["character_reduction"], 0.0)

    def test_04_system_health_telemetry(self):
        latencies = [0.80, 1.10, 1.20, 2.50]
        res = compute_system_health_telemetry(latencies)
        self.assertEqual(res["status"], "healthy")
        self.assertTrue(res["sla_healthy"])

    def test_05_endpoints(self):
        res_consensus = self.client.post("/api/rag/consensus/multi-agent", json={"query": "q", "retrieved_contexts": ["c"]})
        self.assertEqual(res_consensus.status_code, 200)

        res_health = self.client.get("/api/rag/telemetry/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
