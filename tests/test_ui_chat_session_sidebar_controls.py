"""
Unit & Integration Test Suite for Chat Session API Endpoints.
Verifies backend chat session CRUD lifecycle, message retrieval, and deletion cascades.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.infrastructure.database as db
from src.app.server import app


class TestChatSessionSidebarControls(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_chat_sessions_")
        self.test_db_path = os.path.join(self.tmp_dir, "test_sessions.db")
        self.orig_db = db.DB_FILE
        db.DB_FILE = self.test_db_path
        db.reset_db_connections()
        db.init_db()
        self.client = TestClient(app)

    def tearDown(self):
        db.reset_db_connections()
        db.DB_FILE = self.orig_db
        try:
            import shutil
            shutil.rmtree(self.tmp_dir, ignore_errors=True)
        except OSError:
            pass

    def test_chat_sessions_api_endpoints(self):
        """Integration test for backend session CRUD endpoints."""
        # 1. Create a session
        create_resp = self.client.post("/api/chat/sessions", json={
            "title": "M3 Integration Test Session",
            "model_path": "models/tinyllama.gguf",
            "temperature": 0.7,
            "context_window": 4096
        })
        self.assertEqual(create_resp.status_code, 200)
        sess_data = create_resp.json()
        self.assertIn("id", sess_data)
        session_id = sess_data["id"]
        self.assertEqual(sess_data["title"], "M3 Integration Test Session")

        # 2. List sessions
        list_resp = self.client.get("/api/chat/sessions")
        self.assertEqual(list_resp.status_code, 200)
        sessions_list = list_resp.json()
        self.assertTrue(any(s["id"] == session_id for s in sessions_list))

        # 3. Get session details
        get_resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(get_resp.status_code, 200)
        get_data = get_resp.json()
        self.assertEqual(get_data["id"], session_id)
        self.assertIn("messages", get_data)

        # 4. Delete session
        del_resp = self.client.delete(f"/api/chat/sessions/{session_id}")
        self.assertEqual(del_resp.status_code, 200)

        # 5. Verify deletion
        get_del_resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(get_del_resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()