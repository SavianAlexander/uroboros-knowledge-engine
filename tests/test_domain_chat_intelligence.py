"""
Domain Chat Intelligence Test Module.
Tests session CRUD lifecycle, grounded citations, context window truncation,
FastAPI REST endpoints, and unicode/metadata resilience.
"""

import os
import gc
import json
import tempfile
import unittest
from fastapi.testclient import TestClient

import know
import src.infrastructure.database as db
from src.app.server import app
from src.domain.chat_intelligence import (
    truncate_context_window,
    parse_citations_and_metadata,
    format_message_history,
    estimate_tokens
)


class TestDomainChatIntelligence(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = os.path.join(self.tmp_dir.name, "test_chat_domain.db")
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
    def test_01_chat_session_lifecycle_crud(self):
        """
        Preconditions: Isolated SQLite database initialized in temporary directory.
        Invariants: Chat session records enforce UUID keys, default attributes, and cascade message deletions.
        Outcomes: Verifies create, read, list, message append, update, and delete lifecycle for chat sessions.
        """
        sess = know.create_chat_session(title="Lifecycle Test", temperature=0.6, context_window=4096)
        self.assertIsNotNone(sess)
        self.assertIn("id", sess)
        session_id = sess["id"]
        self.assertEqual(sess["title"], "Lifecycle Test")
        self.assertEqual(sess["temperature"], 0.6)
        self.assertEqual(sess["context_window"], 4096)

        retrieved = know.get_chat_session(session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["id"], session_id)
        self.assertEqual(retrieved["title"], "Lifecycle Test")

        sessions = know.list_chat_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["id"], session_id)

        msg1 = know.add_chat_message(session_id, role="user", content="First question")
        msg2 = know.add_chat_message(session_id, role="assistant", content="First answer")
        self.assertIsNotNone(msg1["id"])
        self.assertIsNotNone(msg2["id"])

        messages = know.get_chat_messages(session_id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["content"], "First question")
        self.assertEqual(messages[1]["content"], "First answer")

        updated = know.update_chat_session(
            session_id,
            title="Updated Lifecycle Title",
            temperature=0.2,
            context_window=8192,
            model_path="models/llama-3.gguf"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated["title"], "Updated Lifecycle Title")
        self.assertEqual(updated["temperature"], 0.2)
        self.assertEqual(updated["context_window"], 8192)
        self.assertEqual(updated["model_path"], "models/llama-3.gguf")

        deleted = know.delete_chat_session(session_id)
        self.assertTrue(deleted)

        self.assertIsNone(know.get_chat_session(session_id))
        self.assertEqual(len(know.list_chat_sessions()), 0)
        self.assertEqual(len(know.get_chat_messages(session_id)), 0)

    def test_02_chat_message_history_citations(self):
        """
        Preconditions: Active chat session created in database.
        Invariants: Message sequence indices order history chronologically and parse grounded vault citations into JSON objects.
        Outcomes: Verifies formatted message history, sequence indexing, and citation object parsing.
        """
        sess = know.create_chat_session(title="Citation Test")
        session_id = sess["id"]

        citations = [
            {
                "citation": "[Source: physics_vault.pdf (Chunk #1)]",
                "filename": "physics_vault.pdf",
                "filepath": "docs/physics_vault.pdf",
                "confidence_score": 0.94
            }
        ]
        meta = {"domain": "physics", "grounded": True}

        know.add_chat_message(session_id, role="user", content="Explain quantum entanglement.")

        know.add_chat_message(
            session_id,
            role="assistant",
            content="Quantum entanglement is a non-local correlation...",
            citations_json=citations,
            web_sources_json=["https://arxiv.org/abs/quant-ph"],
            tokens_used=120,
            metadata_json=meta
        )

        raw_messages = know.get_chat_messages(session_id)
        formatted_history = format_message_history(raw_messages)

        self.assertEqual(len(formatted_history), 2)
        self.assertEqual(formatted_history[0]["sequence_index"], 0)
        self.assertEqual(formatted_history[0]["role"], "user")
        self.assertEqual(formatted_history[1]["sequence_index"], 1)
        self.assertEqual(formatted_history[1]["role"], "assistant")

        assistant_turn = formatted_history[1]
        self.assertEqual(len(assistant_turn["citations"]), 1)
        self.assertEqual(assistant_turn["citations"][0]["filename"], "physics_vault.pdf")
        self.assertEqual(assistant_turn["citations"][0]["confidence_score"], 0.94)
        self.assertEqual(assistant_turn["metadata"], meta)

    def test_03_chat_context_window_truncation(self):
        """
        Preconditions: Chat message history exceeding the specified maximum token budget.
        Invariants: System prompt is preserved at index 0 while sliding window drops oldest conversation turns.
        Outcomes: Verifies token window estimation and strict context truncation bounds.
        """
        sys_prompt = "You are a grounded domain assistant for vault intelligence."
        messages = [
            {"role": "user", "content": "Question turn 1 " + ("word " * 40)},
            {"role": "assistant", "content": "Answer turn 1 " + ("word " * 40)},
            {"role": "user", "content": "Question turn 2 " + ("word " * 40)},
            {"role": "assistant", "content": "Answer turn 2 " + ("word " * 40)},
            {"role": "user", "content": "Question turn 3 " + ("word " * 40)},
            {"role": "assistant", "content": "Answer turn 3 " + ("word " * 40)},
        ]

        truncated = truncate_context_window(messages, max_tokens=150, system_prompt=sys_prompt)

        self.assertGreater(len(truncated), 1)
        self.assertEqual(truncated[0]["role"], "system")
        self.assertEqual(truncated[0]["content"], sys_prompt)

        self.assertEqual(truncated[-1]["content"], messages[-1]["content"])
        self.assertEqual(truncated[-2]["content"], messages[-2]["content"])

        truncated_contents = [m["content"] for m in truncated]
        self.assertNotIn(messages[0]["content"], truncated_contents)

        total_tokens = sum(estimate_tokens(m["content"]) for m in truncated)
        self.assertLessEqual(total_tokens, 150)

    def test_04_chat_fastapi_rest_endpoints(self):
        """
        Preconditions: FastAPI server app connected to TestClient instance.
        Invariants: Endpoint handlers return standard status codes and structured JSON response schemas.
        Outcomes: Verifies POST, GET, PUT, and DELETE HTTP routes for /api/chat/sessions.
        """
        resp = self.client.post("/api/chat/sessions", json={"title": "REST Session Test", "temperature": 0.5})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        session_id = data["id"]
        self.assertEqual(data["title"], "REST Session Test")

        resp = self.client.get("/api/chat/sessions")
        self.assertEqual(resp.status_code, 200)
        sessions = resp.json()
        self.assertTrue(any(s["id"] == session_id for s in sessions))

        resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "REST Session Test")

        resp = self.client.post(f"/api/chat/sessions/{session_id}/messages", json={
            "role": "user",
            "content": "Hello via REST API"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "Hello via REST API")

        resp = self.client.put(f"/api/chat/sessions/{session_id}", json={
            "title": "Renamed REST Session",
            "temperature": 0.9
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "Renamed REST Session")
        self.assertEqual(resp.json()["temperature"], 0.9)

        resp = self.client.delete(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "deleted")

        resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 404)

    def test_05_chat_metadata_unicode_resilience(self):
        """
        Preconditions: SQLite database with JSON metadata extension enabled.
        Invariants: UTF-8 characters, SQL injection strings, emojis, and deeply nested dictionaries serialize/deserialize safely.
        Outcomes: Verifies metadata integrity and unicode resilience across database and API layers.
        """
        unicode_title = "🧪 Quantum AI Session 🚀 🤖 🦙 🦔 🦀 🎉 汉语 UTF-8"
        sqli_content = "' OR '1'='1'; DROP TABLE chat_sessions; --"
        deep_meta = {
            "config": {
                "nested": {
                    "deep_array": [100, 200, 300],
                    "flag": True,
                    "emoji": "🔥"
                }
            }
        }

        sess = know.create_chat_session(title=unicode_title, metadata_json=deep_meta)
        session_id = sess["id"]
        self.assertEqual(sess["title"], unicode_title)

        msg = know.add_chat_message(
            session_id,
            role="user",
            content=sqli_content,
            metadata_json=deep_meta
        )
        self.assertEqual(msg["content"], sqli_content)

        retrieved_sess = know.get_chat_session(session_id)
        self.assertIsNotNone(retrieved_sess)
        self.assertEqual(retrieved_sess["title"], unicode_title)

        parsed_cit, parsed_meta = parse_citations_and_metadata(None, retrieved_sess["metadata_json"])
        self.assertEqual(parsed_meta, deep_meta)

        resp = self.client.get(f"/api/chat/sessions/{session_id}")
        self.assertEqual(resp.status_code, 200)
        retrieved_api = resp.json()
        self.assertEqual(retrieved_api["title"], unicode_title)
        self.assertEqual(retrieved_api["messages"][0]["content"], sqli_content)


if __name__ == "__main__":
    unittest.main()
