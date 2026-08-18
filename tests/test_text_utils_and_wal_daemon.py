"""
Unit and Integration Tests for Text Utilities and SQLite WAL Truncation Daemon.
Standard: Pure Python unittest + standard library.
"""

import unittest
import os
import time
import unicodedata
from src.core.text_utils import (
    normalize_nfc,
    sanitise_fts_query,
    sanitize_tag,
    estimate_tokens,
    truncate_context_window,
    extract_top_keywords,
    build_token_budget_context,
    smart_extract_context,
)
from src.infrastructure.database import (
    SQLiteWALDaemon,
    start_wal_daemon,
    init_db,
    reset_db_connections,
)


class TestTextUtils(unittest.TestCase):
    def test_01_normalize_nfc(self):
        decomposed = "e\u0301"  # e with combining acute accent (NFD)
        composed = "\u00e9"     # e with acute (NFC)
        self.assertEqual(normalize_nfc(decomposed), composed)
        self.assertEqual(normalize_nfc(""), "")

    def test_02_sanitise_fts_query(self):
        # Unbalanced quotes, wildcards, operators
        dirty = 'quantum "unbalanced * AND OR NOT NEAR(test, 5) <script>alert(1)</script>'
        cleaned = sanitise_fts_query(dirty)
        self.assertNotIn('"', cleaned)
        self.assertNotIn('<', cleaned)
        self.assertNotIn('>', cleaned)
        self.assertNotIn('(', cleaned)
        self.assertNotIn(')', cleaned)
        self.assertNotIn('AND', cleaned.split())
        self.assertNotIn('OR', cleaned.split())

        # Diacritics NFC equivalence
        nfd_str = "caf" + "e\u0301"
        self.assertEqual(sanitise_fts_query(nfd_str), "caf\u00e9")

    def test_03_sanitize_tag(self):
        self.assertEqual(sanitize_tag("#Machine Learning,"), "machine_learning")
        self.assertEqual(sanitize_tag("   AI   "), "ai")
        self.assertEqual(sanitize_tag(""), "")

    def test_04_estimate_tokens(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertGreaterEqual(estimate_tokens("Hello world"), 1)
        long_text = "word " * 100
        self.assertGreater(estimate_tokens(long_text), 50)

    def test_05_truncate_context_window(self):
        system_prompt = "You are a helpful assistant."
        messages = [
            {"role": "user", "content": "Turn 1 " * 50},
            {"role": "assistant", "content": "Response 1 " * 50},
            {"role": "user", "content": "Turn 2 " * 50},
            {"role": "assistant", "content": "Response 2 " * 50},
            {"role": "user", "content": "Turn 3 - Latest"},
        ]
        truncated = truncate_context_window(messages, max_tokens=100, system_prompt=system_prompt)
        self.assertEqual(truncated[0]["role"], "system")
        self.assertEqual(truncated[0]["content"], system_prompt)
        # Latest message must be present
        self.assertEqual(truncated[-1]["content"], "Turn 3 - Latest")

    def test_06_extract_top_keywords(self):
        text = "architecture database performance index database query query database architecture"
        keywords = extract_top_keywords(text, top_k=3)
        self.assertEqual(keywords[0], "database")
        self.assertIn("architecture", keywords)
        self.assertIn("query", keywords)

    def test_07_build_token_budget_context(self):
        chunks = [
            "Chunk 1: First important document section.",
            "Chunk 2: Second important section with more details.",
            "Chunk 3: Third section that might exceed small budget.",
        ]
        packed = build_token_budget_context(chunks, max_tokens=15)
        self.assertTrue(len(packed) > 0)
        self.assertIn("Chunk 1", packed)

    def test_08_smart_extract_context(self):
        context = (
            "Introduction to system components.\n\n"
            "The neural voice synthesis pipeline uses Kokoro ONNX model weights.\n\n"
            "General background information on unrelated topics.\n\n"
            "Audio playback is managed directly in browser."
        )
        extracted = smart_extract_context(context, query="Kokoro neural voice audio")
        self.assertIn("Kokoro", extracted)


class TestSQLiteWALDaemon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()

    def test_01_daemon_lifecycle(self):
        daemon = SQLiteWALDaemon(boot_grace_seconds=1, interval_seconds=1, cooloff_seconds=1)
        res = daemon.perform_maintenance_cycle()
        self.assertEqual(res.get("status"), "success")
        self.assertIn("checkpoint_mode", res)
        daemon.start()
        time.sleep(1.5)
        daemon.stop()
        daemon.join(timeout=2.0)
        self.assertFalse(daemon._running)


if __name__ == "__main__":
    unittest.main()
