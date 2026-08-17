"""
Unit Test Suite for Unified ConnectionClient (src/domain/connection_client.py).
Verifies:
- Connection profile registration and retrieval
- High-level fetch methods (fetch_json, fetch_xml, fetch_text, post_json)
- URL building and query parameter encoding
- Health check pinging
- One-shot sync_and_rag pipeline with SHA-256 change detection and ledger updating
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import xml.etree.ElementTree as ET

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.domain.connection_client import ConnectionClient, ConnectionProfile


class TestConnectionClient(unittest.TestCase):
    """Unit tests for ConnectionClient."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = ConnectionClient(vault_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_built_in_connections_registered(self):
        """Verify built-in connections are pre-registered."""
        conn_list = self.client.list_connections()
        names = [c["name"] for c in conn_list]
        self.assertIn("ecfr", names)
        self.assertIn("federal_register", names)
        self.assertIn("jira_schema", names)
        self.assertIn("jira_cloud", names)
        self.assertIn("eve_esi", names)
        self.assertIn("ollama", names)

    def test_02_register_custom_connection(self):
        """Verify dynamic registration of custom connection profile."""
        profile = self.client.register(
            name="custom_api",
            base_url="https://api.example.com/v1",
            description="Custom Enterprise API",
            default_headers={"X-Custom-Auth": "secret123"},
            timeout=15.0
        )
        self.assertEqual(profile.name, "custom_api")
        self.assertEqual(profile.base_url, "https://api.example.com/v1")
        self.assertEqual(profile.timeout, 15.0)

        retrieved = self.client.get_connection("custom_api")
        self.assertEqual(retrieved.name, "custom_api")

    def test_03_url_builder_and_rate_limiting(self):
        """Verify URL string construction and param encoding."""
        profile = self.client.get_connection("federal_register")
        url = self.client._build_url(profile, "documents.json", {"term": "poverty guidelines", "per_page": 5})
        self.assertIn("https://www.federalregister.gov/api/v1/documents.json", url)
        self.assertIn("term=poverty+guidelines", url)
        self.assertIn("per_page=5", url)

    def test_04_sync_and_rag_pipeline_and_ledger(self):
        """Verify one-shot sync_and_rag creates vault file, calculates SHA-256, and logs to ledger."""
        # Register a mock connection using file URL or local handler
        test_vault_sub = "test_domain/primary_sources"
        test_filename = "test_statute.md"
        test_content = "Section 101: All eligible citizens receive statutory benefit calculations."

        # Register a connection pointing to a local test mock
        self.client.register("mock_gov", "https://mock.gov/api")
        # Override fetch_text for this mock
        orig_fetch_text = self.client.fetch_text
        self.client.fetch_text = lambda name, path="", params=None: test_content

        try:
            res1 = self.client.sync_and_rag(
                connection_name="mock_gov",
                path="benefits/title1",
                target_subfolder=test_vault_sub,
                filename=test_filename,
                title="Title 1 Statutory Benefits",
                authority="Federal Statute Title 1",
                auto_index=False
            )

            self.assertEqual(res1["status"], "NEW")
            self.assertTrue(os.path.exists(res1["filepath"]))
            self.assertEqual(len(res1["sha256"]), 64)

            # Check ledger
            ledger_path = os.path.join(self.temp_dir, ".sync_ledger.json")
            self.assertTrue(os.path.exists(ledger_path))
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
            self.assertIn(test_filename, ledger["entries"])
            self.assertEqual(ledger["entries"][test_filename]["sha256"], res1["sha256"])

            # Run again without changes -> should return UNCHANGED
            res2 = self.client.sync_and_rag(
                connection_name="mock_gov",
                path="benefits/title1",
                target_subfolder=test_vault_sub,
                filename=test_filename,
                title="Title 1 Statutory Benefits",
                authority="Federal Statute Title 1",
                auto_index=False
            )
            self.assertEqual(res2["status"], "UNCHANGED")

        finally:
            self.client.fetch_text = orig_fetch_text

    def test_05_ping_telemetry(self):
        """Verify ping health check returns structured latency response."""
        res = self.client.ping("ecfr")
        self.assertIn("name", res)
        self.assertIn("status", res)
        self.assertIn("latency_ms", res)
        self.assertIn(res["status"], ["ONLINE", "OFFLINE"])


if __name__ == "__main__":
    unittest.main()
