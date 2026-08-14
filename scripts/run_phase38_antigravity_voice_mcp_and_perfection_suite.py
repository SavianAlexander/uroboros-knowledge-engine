"""
Master Automated Verification, Ingestion & Test Suite for Phase 38:
Antigravity Neural Voice MCP Server, Phonetic Normalizer & Audio Mastering Matrix.
"""

import os
import sys
import unittest
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from batch_index import index_single_file, run_maintenance
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_bridge import VoiceBridge
from src.antigravity_voice_mcp import handle_tool_call, TOOLS_SCHEMA, VOICE_CONFIG
from scripts.verify_zero_assumptions import run_zero_assumption_audit


class TestPhase38AntigravityVoiceSuite(unittest.TestCase):
    """Automated test suite for Antigravity Neural Voice MCP & Audio Perfection Matrix."""

    def test_voice_normalizer_phonetics(self):
        """Test technical acronym expansion, markdown stripping, and cadence pacing."""
        raw_text = "# Task Complete\n- CI/CD pipeline passed at 25ms (24kHz at -14dB).\n- SQLite PRAGMA journal_mode=WAL; API v2.1.0 online."
        clean = VoiceNormalizer.normalize_for_speech(raw_text)
        
        self.assertIn("C-I C-D", clean)
        self.assertIn("25 milliseconds", clean)
        self.assertIn("24 kilohertz", clean)
        self.assertIn("-14 decibels", clean)
        self.assertIn("Sequel Light pragma", clean)
        self.assertIn("wall", clean)
        self.assertIn("A-P-I", clean)
        self.assertIn("version 2 point 1 point 0", clean)
        self.assertNotIn("#", clean)
        self.assertNotIn("```", clean)

    def test_audio_mastering_peak_limiter(self):
        """Test true-peak normalization and soft saturation limiter."""
        try:
            import numpy as np
            samples = np.array([-1.5, -0.5, 0.0, 0.5, 1.8], dtype=np.float32)
            mastered = VoiceNormalizer.master_audio_buffer(samples, target_dbfs=-1.0)
            self.assertEqual(len(mastered), len(samples))
            self.assertLessEqual(np.max(np.abs(mastered)), 1.0)
        except ImportError:
            pass

    def test_antigravity_voice_mcp_tools(self):
        """Test all 6 tools in the dedicated Antigravity Voice MCP server."""
        # 1. antigravity_get_status
        status = handle_tool_call("antigravity_get_status", {})
        self.assertIn("engine", status)
        self.assertIn("supported_personas", status)

        # 2. antigravity_configure_voice
        cfg = handle_tool_call("antigravity_configure_voice", {"default_speed": 1.1, "default_persona": "AURA_SHIP_AI"})
        self.assertEqual(cfg["status"], "updated")
        self.assertEqual(cfg["config"]["default_speed"], 1.1)

        # 3. antigravity_speak
        speak_res = handle_tool_call("antigravity_speak", {
            "text": "Antigravity voice synthesis operational with CI/CD normalizer.",
            "persona": "CALM_OPERATIONS",
            "priority": "HIGH"
        })
        self.assertTrue(speak_res["dispatched"])
        self.assertIn("normalized_text", speak_res)

        # 4. antigravity_announce_task
        task_res = handle_tool_call("antigravity_announce_task", {
            "task_name": "Phase 38 Voice MCP Matrix",
            "state": "COMPLETED",
            "details": "All unit tests verified 100 percent green."
        })
        self.assertTrue(task_res["dispatched"])
        self.assertEqual(task_res["state"], "COMPLETED")

        # 5. antigravity_voice_brief
        brief_res = handle_tool_call("antigravity_voice_brief", {
            "title": "Evening Engineering Briefing",
            "items": ["Kokoro 82M model synchronized.", "Phonetic normalizer active.", "True-peak mastering enabled."]
        })
        self.assertTrue(brief_res["dispatched"])
        self.assertEqual(brief_res["item_count"], 3)

        # 6. antigravity_play_sfx
        sfx_res = handle_tool_call("antigravity_play_sfx", {"sfx_name": "target_lock"})
        self.assertEqual(sfx_res["sfx_name"], "target_lock")

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        success = run_zero_assumption_audit()
        self.assertTrue(success, "Zero-assumption audit failed!")


def ingest_vault_document():
    """Ingest Phase 38 architecture document into SQLite knowledge vault."""
    vault_doc = os.path.join(BASE_DIR, "vault", "System_Architecture", "antigravity_voice_mcp_perfection_matrix.md")
    print("\n" + "=" * 65)
    print("🌐 EXECUTING PHASE 38 MASTER INGESTION & ANTIGRAVITY VOICE MCP")
    print("=" * 65)

    if os.path.exists(vault_doc):
        print(f"\n🚀 Indexing Antigravity voice MCP document into Knowledge Vault...")
        index_single_file(vault_doc)
        print("  ✅ Indexed: antigravity_voice_mcp_perfection_matrix.md")

    print("\n🔧 Running Database Maintenance & Vector Compaction...")
    run_maintenance()
    print("  ✅ Database maintenance complete.")


def run_test_suite():
    """Run the test suite."""
    print("\n" + "=" * 65)
    print("🧪 RUNNING PHASE 38 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase38AntigravityVoiceSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 38 TEST MODULES PASSED WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    t0 = time.time()
    ingest_vault_document()
    run_test_suite()
    print(f"Phase 38 completed in {time.time() - t0:.2f}s")
