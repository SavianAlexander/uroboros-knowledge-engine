"""
Live Benchmark & Vault Execution Test Suite.
Simulates real-world document ingestion and runs load benchmarks across API endpoints.
"""

import time
import unittest
from fastapi.testclient import TestClient
from main import app


class TestSystemExecution(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_vault_ingestion_simulation(self):
        sample_doc = """
        # Uroboros Knowledge Engine Security Policy
        Section 1: Data retention is strictly set to 90 days.
        Section 2: All API traffic requires JWT Bearer authentication.
        def authenticate_user(token: str):
            '''Verifies JWT token signature.'''
            pass
        """
        # Test universal pipeline ingestion
        res_pipe = self.client.post("/api/rag/pipeline/ingest-universal", json={"raw_content": sample_doc, "format_type": "markdown"})
        self.assertEqual(res_pipe.status_code, 200)
        
        # Test AST code parsing on embedded snippet
        res_ast = self.client.post("/api/rag/code/ast-parse", json={"code_snippet": "def authenticate_user(token: str):\n    pass"})
        self.assertEqual(res_ast.status_code, 200)
        self.assertEqual(len(res_ast.json()["functions"]), 1)

    def test_02_latency_load_benchmark(self):
        latencies = []
        for _ in range(20):
            start = time.time()
            res = self.client.post("/api/rag/telemetry/health", json={"recent_latencies_ms": [0.80, 1.10], "cache_hits": 50, "cache_misses": 2})
            latencies.append((time.time() - start) * 1000.0)
            self.assertEqual(res.status_code, 200)

        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        self.assertLess(p95, 50.0)  # Verify sub-50ms SLA bound


if __name__ == "__main__":
    unittest.main()
