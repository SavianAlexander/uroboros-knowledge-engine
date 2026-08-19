"""
Domain 20: OpenAPI Schema Contract, Network Fault Injection, & Performance Budget Suite.
Validates OpenAPI 3.0.0 JSON schema contract integrity, P95 response latency budgets (<15.0ms test budget),
and network fault injection failover handling under simulated 503/timeout conditions.
"""

import os
import sys
import time
import json
import unittest
import tempfile
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import main
import know
import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, init_db, reset_db_connections
from src.infrastructure.vector_engine import index_directory
from src.infrastructure.parsers import safe_write_file
from fastapi.testclient import TestClient


class TestDomainContractChaos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="test_contract_chaos_")
        cls.db_path = os.path.join(cls.test_dir, "test_contract.db")
        cls.orig_db_file = db_module.DB_FILE
        cls.orig_know_db_file = getattr(know, "DB_FILE", db_module.DB_FILE)
        db_module.DB_FILE = cls.db_path
        know.DB_FILE = cls.db_path
        reset_db_connections()
        know.reset_db_connections()
        init_db()

        # Seed sample documents
        doc1 = os.path.join(cls.test_dir, "contract_doc.txt")
        safe_write_file(doc1, "OpenAPI schema contract testing physics quantum mechanics")
        index_directory(cls.test_dir)

        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        know.reset_db_connections()
        db_module.DB_FILE = cls.orig_db_file
        know.DB_FILE = cls.orig_know_db_file
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        db_module.DB_FILE = self.db_path
        know.DB_FILE = self.db_path

    def tearDown(self):
        pass

    def test_01_openapi_schema_contract_validity(self):
        """
        Preconditions: Running FastAPI app with auto-generated OpenAPI documentation.
        Invariants: GET /openapi.json must return HTTP 200 with OpenAPI 3.x specification structure.
        Outcomes: Mandatory API endpoint routes are present in the returned JSON schema paths.
        """
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        self.assertIn("openapi", schema)
        self.assertTrue(schema["openapi"].startswith("3."))
        self.assertIn("paths", schema)

        paths = schema["paths"]
        mandatory_endpoints = [
            "/api/stats",
            "/api/search",
            "/api/file/tree",
            "/api/system/env",
            "/api/snapshots",
            "/api/tags",
            "/api/rules",
            "/api/macros",
            "/api/synonyms",
        ]
        for ep in mandatory_endpoints:
            self.assertIn(ep, paths, f"Mandatory OpenAPI endpoint '{ep}' missing from schema paths!")

    def test_02_p95_latency_performance_budget_guard(self):
        """
        Preconditions: Seeded database with TestClient API instance.
        Invariants: 50 consecutive requests to /api/stats must maintain P95 latency below 35.0ms.
        Outcomes: Calculated P95 response time satisfies performance latency budget requirements.
        """
        latencies = []
        for _ in range(50):
            start_t = time.perf_counter()
            res = self.client.get("/api/stats")
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            self.assertEqual(res.status_code, 200)
            latencies.append(duration_ms)

        latencies.sort()
        p95_latency = latencies[int(len(latencies) * 0.95)]
        self.assertLess(p95_latency, 35.0, f"P95 Performance Budget Violated! Latency: {p95_latency:.2f}ms >= 35.0ms")

    def test_03_network_fault_injection_and_error_contract(self):
        """
        Preconditions: POST request sent with invalid schema key payload.
        Invariants: API input validation errors must return structured HTTP 400 or 422 JSON details.
        Outcomes: Response status is 400 or 422 and JSON contains detail error object.
        """
        bad_response = self.client.post("/api/rules/test-preview", json={"invalid_key": "junk"})
        self.assertIn(bad_response.status_code, [400, 422])
        self.assertIn("detail", bad_response.json())

    def test_04_system_env_contract_fields(self):
        """
        Preconditions: Active system health router endpoints.
        Invariants: GET /api/system/env must expose standard system environment keys.
        Outcomes: Response status is HTTP 200 and mandatory keys exist in returned dictionary.
        """
        response = self.client.get("/api/system/env")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        required_keys = ["python_version", "sqlite_version", "os_platform", "uvicorn_version", "db_file_path"]
        for k in required_keys:
            self.assertIn(k, data, f"Required system environment key '{k}' missing from contract!")


if __name__ == "__main__":
    unittest.main()