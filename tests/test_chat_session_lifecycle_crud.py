import os
import gc
import tempfile
import unittest
from fastapi.testclient import TestClient

import know
import src.infrastructure.database as db
from src.app.server import app

class TestChatSessionsM1(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = os.path.join(self.tmp_dir.name, "test_knowledge.db")
        self.orig_db = db.DB_FILE
        db.DB_FILE = self.db_path
        db.init_db()
        self.client = TestClient(app)

    def tearDown(self):
        db.reset_db_connections()
        db.DB_FILE = self.orig_db
        gc.collect()
        try:
            self.tmp_dir.cleanup()
        except Exception as e:
                pass
    def test_database_crud(self):
        # Create session
        sess = know.create_chat_session(title="Test Session", temperature=0.5)
        self.assertIsNotNone(sess["id"])
        self.assertEqual(sess["title"], "Test Session")
        self.assertEqual(sess["temperature"], 0.5)

        session_id = sess["id"]

        # List sessions
        sessions = know.list_chat_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["id"], session_id)

        # Add message
        msg1 = know.add_chat_message(session_id, role="user", content="Hello RAG engine")
        self.assertIsNotNone(msg1["id"])
        self.assertEqual(msg1["session_id"], session_id)
        self.assertEqual(msg1["content"], "Hello RAG engine")

        msg2 = know.add_chat_message(session_id, role="assistant", content="Hello! How can I help?")
        self.assertIsNotNone(msg2["id"])

        # Get session with messages
        retrieved = know.get_chat_session(session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved["messages"]), 2)
        self.assertEqual(retrieved["messages"][0]["content"], "Hello RAG engine")

        # Update session
        updated = know.update_chat_session(session_id, title="Updated Title", temperature=0.8)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["title"], "Updated Title")
        self.assertEqual(updated["temperature"], 0.8)

        # Delete session
        deleted = know.delete_chat_session(session_id)
        self.assertTrue(deleted)

        self.assertIsNone(know.get_chat_session(session_id))
        self.assertEqual(len(know.list_chat_sessions()), 0)
        self.assertEqual(len(know.get_chat_messages(session_id)), 0)

    def test_fastapi_endpoints(self):
        # Create session via POST /api/chat/sessions
        resp = self.client.post("/api/chat/sessions", json={"title": "API Session", "temperature": 0.3})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        session_id = data["id"]
        self.assertEqual(data["title"], "API Session")

        # List sessions via GET /api/chat/sessions
        resp = self.client.get("/api/chat/sessions")
        self.assertEqual(resp.status_code, 200)
        sessions = resp.json()
        self.assertTrue(any(s["id"] == session_id for s in sessions))

        # Add message via POST /api/chat/sessions/{session_id}/messages
        resp = self.client.post(f"/api/chat/sessions/{session_id}/messages", json={"role": "user", "content": "API test message"})
        self.assertEqual(resp.status_code, 200)
        msg_data = resp.json()
        self.assertEqual(msg_data["content"], "API test message")

        # Get session details via GET /api/chat/sessions/{session_id}
        resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 200)
        detail = resp.json()
        self.assertEqual(detail["title"], "API Session")
        self.assertEqual(len(detail["messages"]), 1)

        # Update session via PUT /api/chat/sessions/{session_id}
        resp = self.client.put(f"/api/chat/sessions/{session_id}", json={"title": "Renamed API Session"})
        self.assertEqual(resp.status_code, 200)
        updated_data = resp.json()
        self.assertEqual(updated_data["title"], "Renamed API Session")

        # Delete session via DELETE /api/chat/sessions/{session_id}
        resp = self.client.delete(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 200)

        # Verify 404 on deleted session
        resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 404)

if __name__ == "__main__":
    unittest.main()
