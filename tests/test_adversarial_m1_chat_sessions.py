import os
import gc
import json
import sqlite3
import tempfile
import unittest
from fastapi.testclient import TestClient

import know
import src.infrastructure.database as db
from src.app.server import app

class TestAdversarialM1ChatSessions(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = os.path.join(self.tmp_dir.name, "test_adversarial_m1.db")
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
        except Exception:
            pass

    # ---------------------------------------------------------------------------
    # 1. Non-existent session IDs (404 responses & safe DB returns)
    # ---------------------------------------------------------------------------
    def test_non_existent_session_ids_api(self):
        fake_id = "non_existent_uuid_999999"

        # GET /api/chat/sessions/{fake_id}
        resp = self.client.get(f"/api/chat/sessions/{fake_id}")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Session not found", resp.json()["detail"])

        # PUT /api/chat/sessions/{fake_id}
        resp = self.client.put(f"/api/chat/sessions/{fake_id}", json={"title": "Ghost Session"})
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Session not found", resp.json()["detail"])

        # DELETE /api/chat/sessions/{fake_id}
        resp = self.client.delete(f"/api/chat/sessions/{fake_id}")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Session not found", resp.json()["detail"])

        # POST /api/chat/sessions/{fake_id}/messages
        resp = self.client.post(f"/api/chat/sessions/{fake_id}/messages", json={"role": "user", "content": "Hello ghost"})
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Session not found", resp.json()["detail"])

    def test_non_existent_session_ids_db(self):
        fake_id = "non_existent_uuid_999999"

        self.assertIsNone(know.get_chat_session(fake_id))
        self.assertIsNone(know.update_chat_session(fake_id, title="Ghost"))
        self.assertFalse(know.delete_chat_session(fake_id))
        self.assertEqual(know.get_chat_messages(fake_id), [])

    # ---------------------------------------------------------------------------
    # 2. Invalid / Malformed JSON metadata and unusual types
    # ---------------------------------------------------------------------------
    def test_invalid_and_unusual_metadata_types_db(self):
        # Nested dict metadata
        dict_meta = {"user_pref": {"theme": "dark", "tags": ["a", "b"]}, "active": True}
        sess1 = know.create_chat_session(title="Dict Meta", metadata_json=dict_meta)
        self.assertIsNotNone(sess1["id"])
        # Should be serialized to JSON string in DB return
        self.assertEqual(json.loads(sess1["metadata_json"]), dict_meta)

        # Raw JSON string metadata
        str_meta = '{"key": "raw_string_json"}'
        sess2 = know.create_chat_session(title="Str Meta", metadata_json=str_meta)
        self.assertEqual(sess2["metadata_json"], str_meta)

        # Malformed JSON string metadata (should be saved as-is string without crashing)
        malformed_meta = '{"invalid_json": true, missing_brace'
        sess3 = know.create_chat_session(title="Malformed Meta", metadata_json=malformed_meta)
        self.assertEqual(sess3["metadata_json"], malformed_meta)

        # Primitive types: int, float, list, None
        sess4 = know.create_chat_session(title="Int Meta", metadata_json=12345)
        self.assertEqual(sess4["metadata_json"], 12345)

        sess5 = know.create_chat_session(title="List Meta", metadata_json=[1, 2, "three"])
        self.assertEqual(json.loads(sess5["metadata_json"]), [1, 2, "three"])

        # Update metadata to another structure
        updated_sess = know.update_chat_session(sess1["id"], metadata_json={"updated": True})
        self.assertIsNotNone(updated_sess)
        self.assertEqual(json.loads(updated_sess["metadata_json"]), {"updated": True})

    def test_invalid_and_unusual_metadata_api(self):
        # POST with dict metadata
        resp = self.client.post("/api/chat/sessions", json={
            "title": "API Dict Meta",
            "metadata_json": {"setting": "enabled", "count": 42}
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        sess_id = data["id"]
        self.assertEqual(json.loads(data["metadata_json"]), {"setting": "enabled", "count": 42})

        # Add message with list citations and dict metadata
        resp = self.client.post(f"/api/chat/sessions/{sess_id}/messages", json={
            "role": "user",
            "content": "Testing metadata on message",
            "citations_json": [{"source": "doc1.txt", "page": 4}],
            "web_sources_json": ["https://example.com"],
            "tokens_used": 150,
            "metadata_json": {"flag": "verified"}
        })
        self.assertEqual(resp.status_code, 200)
        msg = resp.json()
        self.assertEqual(json.loads(msg["citations_json"]), [{"source": "doc1.txt", "page": 4}])
        self.assertEqual(json.loads(msg["web_sources_json"]), ["https://example.com"])
        self.assertEqual(json.loads(msg["metadata_json"]), {"flag": "verified"})

    # ---------------------------------------------------------------------------
    # 3. Empty titles, long titles, unicode/emoji strings, injection vectors
    # ---------------------------------------------------------------------------
    def test_empty_and_default_titles(self):
        # Create session with None title -> defaults to "New Chat"
        sess1 = know.create_chat_session(title=None)
        self.assertEqual(sess1["title"], "New Chat")

        # Create session with empty title ""
        sess2 = know.create_chat_session(title="")
        self.assertEqual(sess2["title"], "")

        # Create session with whitespace title "   "
        sess3 = know.create_chat_session(title="   ")
        self.assertEqual(sess3["title"], "   ")

    def test_extremely_long_titles_and_messages(self):
        huge_title = "A" * 10000
        sess = know.create_chat_session(title=huge_title)
        self.assertEqual(sess["title"], huge_title)

        retrieved = know.get_chat_session(sess["id"])
        self.assertEqual(retrieved["title"], huge_title)

        huge_content = "X" * 100000
        msg = know.add_chat_message(sess["id"], role="user", content=huge_content)
        self.assertEqual(msg["content"], huge_content)

        retrieved_msg = know.get_chat_messages(sess["id"])[0]
        self.assertEqual(retrieved_msg["content"], huge_content)

    def test_unicode_emojis_and_special_characters(self):
        unicode_title = "🧪 Subagent 🐍 Test 🚀 👾 🦙 🦔 🦀 🎉 💻 🔍 🔥 汉语/漢語 UTF-8 💡"
        sess = know.create_chat_session(title=unicode_title)
        self.assertEqual(sess["title"], unicode_title)

        unicode_content = "日本語のテスト: 🤖 Hello world! €£¥ ₹ 𐍈 𓀀 𓀁"
        msg = know.add_chat_message(sess["id"], role="user", content=unicode_content)
        self.assertEqual(msg["content"], unicode_content)

        # Retrieve via API
        resp = self.client.get(f"/api/chat/sessions/{sess['id']}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["title"], unicode_title)
        self.assertEqual(data["messages"][0]["content"], unicode_content)

    def test_sql_injection_and_xss_safety(self):
        sqli_title = "' OR '1'='1'; DROP TABLE chat_sessions; --"
        sess = know.create_chat_session(title=sqli_title)
        self.assertEqual(sess["title"], sqli_title)

        # Verify DB is intact
        sessions = know.list_chat_sessions()
        self.assertTrue(any(s["id"] == sess["id"] for s in sessions))

        xss_content = "<script>alert('XSS Attack');</script><iframe src='javascript:alert(1)'></iframe>"
        msg = know.add_chat_message(sess["id"], role="user", content=xss_content)
        self.assertEqual(msg["content"], xss_content)

    # ---------------------------------------------------------------------------
    # 4. Cascade deletion integrity
    # ---------------------------------------------------------------------------
    def test_cascade_deletion_db_and_api(self):
        # Create session A
        sessA = know.create_chat_session(title="Session A")
        idA = sessA["id"]
        for i in range(10):
            know.add_chat_message(idA, role="user" if i % 2 == 0 else "assistant", content=f"Message A{i}")

        # Create session B
        sessB = know.create_chat_session(title="Session B")
        idB = sessB["id"]
        for i in range(5):
            know.add_chat_message(idB, role="user", content=f"Message B{i}")

        # Verify initial counts directly from SQLite DB
        with db.get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (idA,))
            countA = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (idB,))
            countB = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chat_messages")
            total_count = c.fetchone()[0]

        self.assertEqual(countA, 10)
        self.assertEqual(countB, 5)
        self.assertEqual(total_count, 15)

        # Delete session A via API DELETE /api/chat/sessions/{idA}
        resp = self.client.delete(f"/api/chat/sessions/{idA}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "deleted", "id": idA})

        # Verify session A is gone from API
        resp = self.client.get(f"/api/chat/sessions/{idA}")
        self.assertEqual(resp.status_code, 404)

        # Verify direct DB query: chat_messages for session A MUST BE 0 (cascade delete verified)
        with db.get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (idA,))
            countA_after = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (idB,))
            countB_after = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chat_sessions WHERE id = ?", (idA,))
            sessA_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chat_sessions WHERE id = ?", (idB,))
            sessB_count = c.fetchone()[0]

        self.assertEqual(countA_after, 0, "Cascade delete failed! Orphaned messages found for session A.")
        self.assertEqual(sessA_count, 0, "Session A still present in chat_sessions.")
        self.assertEqual(countB_after, 5, "Session B messages affected by session A deletion!")
        self.assertEqual(sessB_count, 1, "Session B deleted unexpectedly!")

    # ---------------------------------------------------------------------------
    # 5. Order, updates & session parameters
    # ---------------------------------------------------------------------------
    def test_session_ordering_and_partial_updates(self):
        s1 = know.create_chat_session(title="First")
        s2 = know.create_chat_session(title="Second")
        s3 = know.create_chat_session(title="Third")

        # Update s1 -> updated_at changes -> s1 should come first in list_chat_sessions()
        know.update_chat_session(s1["id"], title="First Updated", temperature=0.2)
        sessions = know.list_chat_sessions()
        self.assertEqual(sessions[0]["id"], s1["id"])
        self.assertEqual(sessions[0]["title"], "First Updated")
        self.assertEqual(sessions[0]["temperature"], 0.2)

        # Verify partial update preserves unmodified attributes
        updated_s1 = know.update_chat_session(s1["id"], context_window=8192)
        self.assertEqual(updated_s1["context_window"], 8192)
        self.assertEqual(updated_s1["title"], "First Updated")
        self.assertEqual(updated_s1["temperature"], 0.2)

if __name__ == "__main__":
    unittest.main()
