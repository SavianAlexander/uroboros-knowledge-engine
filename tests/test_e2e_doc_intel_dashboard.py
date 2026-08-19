"""
Unit & Integration Test Suite for Document Intelligence Analytics Dashboard & Graph Endpoints.
"""

import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from main import app
from src.infrastructure.database import init_db


class TestDocIntelDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_analytics_storage_endpoint(self):
        res = self.client.get("/api/analytics/storage")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("by_mime", data)
        self.assertIn("by_extension", data)
        self.assertIn("top_directories", data)

    def test_analytics_tags_endpoint(self):
        res = self.client.get("/api/analytics/tags")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_tags", data)
        self.assertIn("top_tags", data)
        self.assertIn("tag_cooccurrence", data)

    def test_analytics_search_activity_endpoint(self):
        res = self.client.get("/api/analytics/search-activity")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_queries", data)
        self.assertIn("avg_latency_ms", data)
        self.assertIn("top_queries", data)
        self.assertIn("recent_queries", data)

    def test_workflow_logs_and_test_endpoints(self):
        res_logs = self.client.get("/api/workflows/logs")
        self.assertEqual(res_logs.status_code, 200)

        res_triggers = self.client.get("/api/workflows/triggers")
        self.assertEqual(res_triggers.status_code, 200)

        res_test = self.client.post("/api/workflows/test", json={"event_type": "document_ingested", "payload": {"test": True}})
        self.assertEqual(res_test.status_code, 200)
        self.assertEqual(res_test.json().get("status"), "dispatched")

    def test_graph_limit_1000_endpoint(self):
        res = self.client.get("/api/graph?limit=1000&include_wikilinks=true&include_clusters=true")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)


if __name__ == "__main__":
    unittest.main()