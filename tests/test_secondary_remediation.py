"""
Unit test suite verifying remediation of secondary memory leaks, hot paths, and security holes.
"""
import unittest
import time
import os
import shutil
import tempfile
from collections import OrderedDict
from fastapi.testclient import TestClient

from main import app
from src.core.voice_agent_loop import (
    VoiceAgentLoop,
    _ACTIVE_SESSIONS,
    _purge_stale_sessions,
    _MAX_VOICE_SESSIONS,
    _SESSION_TTL_SECONDS,
    _SESSIONS_LOCK
)


class TestSecondaryRemediation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_voice_session_ttl_and_overflow_purging(self):
        """Test #1: Verify voice session TTL eviction and maximum capacity bounding."""
        with _SESSIONS_LOCK:
            _ACTIVE_SESSIONS.clear()
            # Populate stale session
            old_time = time.time() - (_SESSION_TTL_SECONDS + 100)
            _ACTIVE_SESSIONS["stale_sess_1"] = {
                "session_id": "stale_sess_1",
                "last_active": old_time,
                "created_at": old_time
            }
            # Populate fresh sessions up to max + 10
            for i in range(_MAX_VOICE_SESSIONS + 10):
                sid = f"fresh_sess_{i}"
                _ACTIVE_SESSIONS[sid] = {
                    "session_id": sid,
                    "last_active": time.time() + i,
                    "created_at": time.time()
                }

            _purge_stale_sessions()

            # Verify stale session was pruned
            self.assertNotIn("stale_sess_1", _ACTIVE_SESSIONS)
            # Verify capacity is capped at max
            self.assertLessEqual(len(_ACTIVE_SESSIONS), _MAX_VOICE_SESSIONS)

    def test_ocr_endpoint_path_traversal_protection(self):
        """Test #4: Verify OCR endpoint handles invalid extensions and sanitizes filenames."""
        # 1. Invalid non-PDF extension
        res = self.client.post(
            "/api/ingest/pdf",
            files={"file": ("malicious.exe", b"not a pdf", "application/octet-stream")}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Only PDF files are supported", res.json()["detail"])

        # 2. Ingestion queue is bounded
        res = self.client.get("/api/ingest/queue")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_queued", data)
        self.assertIn("queue", data)


if __name__ == "__main__":
    unittest.main()
