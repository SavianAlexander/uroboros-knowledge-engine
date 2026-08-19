"""
Empirical Adversarial Test Suite for Chat Sessions & SSE Streaming.
Tests SSE stream fragmentation resilience and high-throughput session CRUD operations.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent

import src.infrastructure.database as db
from src.app.server import app
from src.core.auth_jwt import sign_jwt


class TestConsensusAdversarial(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_consensus_adv_")
        self.test_db_path = os.path.join(self.tmp_dir, "test_rapid_m3.db")
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

    def test_sse_stream_fragmentation_handling_simulation(self):
        """Empirically test partial SSE stream line handling logic with split chunks."""
        sse_events = [
            'data: {"type": "token", "content": "Hello"}\n\n',
            'data: {"type": "token", "content": " World"}\n\n',
            'data: {"type": "sources", "local_citations": [{"file": "doc1.txt"}]}\n\n',
            'data: [DONE]\n\n'
        ]
        raw_stream = "".join(sse_events)

        # Chunk stream into 3-char fragments
        fragments = [raw_stream[i:i+3] for i in range(0, len(raw_stream), 3)]

        line_buffer = ""
        parsed_tokens = []
        parsed_sources = []

        for frag in fragments:
            line_buffer += frag
            lines = line_buffer.split("\n")
            line_buffer = lines.pop()

            for line in lines:
                line_str = line.strip()
                if not line_str or line_str.startswith(":"):
                    continue
                if line_str.startswith("data: "):
                    payload = line_str[6:].strip()
                    if payload == "[DONE]":
                        continue
                    try:
                        data = json.loads(payload)
                        if "content" in data:
                            parsed_tokens.append(data["content"])
                        if "local_citations" in data:
                            parsed_sources.extend(data["local_citations"])
                    except json.JSONDecodeError:
                        self.fail(f"Partial JSON syntax error encountered on line: {line_str}")

        self.assertEqual("".join(parsed_tokens), "Hello World")
        self.assertEqual(len(parsed_sources), 1)
        self.assertEqual(parsed_sources[0]["file"], "doc1.txt")

    def test_rapid_session_api_stress_crud(self):
        """Empirically stress test backend session creation, listing, getting, and deleting 20 sessions."""
        token = sign_jwt({"user_id": 999, "username": "test_user", "role": "admin"})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        created_ids = []

        # Rapidly create 20 sessions
        for i in range(20):
            res = self.client.post(
                "/api/chat/sessions",
                json={
                    "title": f"Stress Session {i}",
                    "model_path": "models/tinyllama.gguf",
                    "temperature": 0.7,
                    "context_window": 4096
                },
                headers=headers
            )
            self.assertEqual(res.status_code, 200)
            created_ids.append(res.json()["id"])

        self.assertEqual(len(created_ids), 20)

        # List sessions
        list_res = self.client.get("/api/chat/sessions", headers=headers)
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.json()), 20)

        # Delete 10 sessions
        for sid in created_ids[:10]:
            del_res = self.client.delete(f"/api/chat/sessions/{sid}", headers=headers)
            self.assertEqual(del_res.status_code, 200)

        # Verify list contains remaining 10
        list_res2 = self.client.get("/api/chat/sessions", headers=headers)
        self.assertEqual(list_res2.status_code, 200)
        self.assertEqual(len(list_res2.json()), 10)


if __name__ == "__main__":
    unittest.main()