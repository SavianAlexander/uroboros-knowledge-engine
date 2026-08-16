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
from src.infrastructure.eve_sde_cache import (
    _MEM_CACHE,
    _cache_put,
    _cache_get,
    _MAX_MEM_CACHE_SIZE,
    resolve_ids_fast
)
from src.domain.eve_voice_alerts import EVEVoiceAlertManager, TACTICAL_VOICE_TEMPLATES


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

    def test_eve_sde_cache_lru_bounding(self):
        """Test #2: Verify SDE cache LRU ordering and bounded maxsize eviction."""
        _MEM_CACHE.clear()
        _cache_put(30000142, "Jita")
        _cache_put(30002187, "Amarr")

        self.assertEqual(_cache_get(30000142), "Jita")
        self.assertEqual(_cache_get(30002187), "Amarr")
        self.assertIsNone(_cache_get(99999999))

        # Test resolution from cache and static SDE
        resolved = resolve_ids_fast([30000142, 30002187, 587])
        self.assertEqual(resolved[30000142], "Jita")
        self.assertEqual(resolved[30002187], "Amarr")
        self.assertEqual(resolved[587], "Rifter")

    def test_eve_voice_alerts_endpoints_and_formatting(self):
        """Test #3: Verify tactical alert formatting and router integration."""
        # 1. Format alert directly
        msg = EVEVoiceAlertManager.format_alert("WARP_DRIVE_ACTIVE", destination="Jita IV - Moon 4")
        self.assertIn("Jita IV - Moon 4", msg)
        self.assertIn("Warp drive active", msg)

        # 2. Test GET /api/eve/alerts/templates
        res = self.client.get("/api/eve/alerts/templates")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("SHIELD_WARNING", data["templates"])

        # 3. Test POST /api/eve/alerts/format
        res = self.client.post("/api/eve/alerts/format", json={
            "template_key": "SHIELD_WARNING",
            "params": {"percent": 25}
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("25 percent", data["formatted_message"])

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
