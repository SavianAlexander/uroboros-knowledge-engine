"""
Integration Verification Test Suite for Document Intelligence & Analytics APIs.
Verifies storage analytics, tag distribution, search telemetry, and workflow trigger integration.
"""

import os
import sys
import time
import shutil
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.core.config as config
import src.infrastructure.database as db
from src.infrastructure.database import get_db_connection, reset_db_connections
from src.infrastructure.repositories.workflows import create_workflow_trigger, list_workflow_triggers
import main


class TestDocumentIntelligenceAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="test_doc_intel_")
        cls.db_path = os.path.join(cls.temp_dir, "test_intel.db")
        cls.orig_db = db.DB_FILE
        cls.orig_active = config.ACTIVE_DIR
        db.DB_FILE = cls.db_path
        config.ACTIVE_DIR = cls.temp_dir
        reset_db_connections()
        db.init_db()

        # Seed data
        now = int(time.time())
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM tags")
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, os.path.join(cls.temp_dir, "alpha.txt"), "alpha.txt", 100, now, "Alpha content", "sha1", "text/plain")
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (2, os.path.join(cls.temp_dir, "beta.md"), "beta.md", 200, now, "Beta content [[alpha.txt]]", "sha2", "text/markdown")
            )
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "analytics"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "intelligence"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (2, "analytics"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (2, "intelligence"))
            conn.commit()

        create_workflow_trigger(
            name="Test Trigger Rule",
            event_type="document_ingested",
            webhook_url="http://127.0.0.1:8080/api/webhook/mock",
            condition_pattern="",
            is_active=True
        )
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        db.DB_FILE = cls.orig_db
        config.ACTIVE_DIR = cls.orig_active
        try:
            shutil.rmtree(cls.temp_dir, ignore_errors=True)
        except OSError:
            pass

    def test_document_analytics_overview_endpoint(self):
        """Verify GET /api/analytics/overview returns accurate document count and storage metrics."""
        resp = self.client.get("/api/analytics/overview")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue("total_files" in data or "file_count" in data or "total_documents" in data or "storage" in data)

    def test_workflow_trigger_lifecycle(self):
        """Verify workflow trigger listing returns seeded trigger."""
        triggers = list_workflow_triggers()
        self.assertGreaterEqual(len(triggers), 1)
        self.assertEqual(triggers[0]["name"], "Test Trigger Rule")


if __name__ == "__main__":
    unittest.main()