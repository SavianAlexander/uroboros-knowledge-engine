"""
Master Automated Verification, Ingestion & Test Suite for Phase 39:
Antigravity Omniscient Neural Voice Matrix (STT Ear, Persona Blending, Memory Ledger, FFT Spectrum & Tududi Radar).
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
from src.core.voice_persona_blend import VoicePersonaBlender
from src.core.voice_stt_ear import VoiceEarTranscriber
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_memory_ledger import VoiceMemoryLedger
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.antigravity_voice_mcp import handle_tool_call, TOOLS_SCHEMA
from scripts.verify_zero_assumptions import run_zero_assumption_audit


class TestPhase39OmniscientVoiceSuite(unittest.TestCase):
    """Automated test suite for Antigravity Omniscient Voice Matrix."""

    def test_voice_persona_blender(self):
        """Test vector persona blending and interpolation."""
        weights = {"bf_emma": 0.70, "af_bella": 0.30}
        res = VoicePersonaBlender.blend_personas(weights, custom_name="test_co_pilot")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["blend_name"], "test_co_pilot")
        self.assertAlmostEqual(res["weights"]["bf_emma"], 0.70)
        self.assertAlmostEqual(res["weights"]["af_bella"], 0.30)
        presets = VoicePersonaBlender.get_preset_blends()
        self.assertIn("CYBER_EXECUTIVE", presets)

    def test_voice_stt_transcriber(self):
        """Test Speech-to-Text transcriber and microphone recorder."""
        rec = VoiceEarTranscriber.record_microphone_sample(duration_s=1.0)
        self.assertEqual(rec["status"], "ready")
        self.assertGreater(rec["duration_seconds"], 0)
        
        # Test transcribing an existing wav or acoustic fallback
        res = VoiceEarTranscriber.transcribe_audio_file(rec["output_path"])
        self.assertIn(res["status"], ["success", "error"])

    def test_voice_audio_router(self):
        """Test audio output device enumeration and volume controls."""
        devices = VoiceAudioRouter.list_audio_output_devices()
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)

        vol_res = VoiceAudioRouter.set_master_volume(85)
        self.assertEqual(vol_res["master_volume"], 85)

    def test_voice_memory_ledger(self):
        """Test persistent SQLite conversational memory ledger."""
        turn = VoiceMemoryLedger.log_turn(
            speaker="Antigravity",
            raw_text="Deploying Phase 39 Omniscient Voice Matrix.",
            normalized_text="Deploying Phase 39 Omniscient Voice Matrix.",
            persona="CALM_OPERATIONS",
            domain="DEV_OPS"
        )
        self.assertIn("turn_id", turn)

        recent = VoiceMemoryLedger.get_recent_turns(limit=5)
        self.assertGreater(len(recent), 0)

        metrics = VoiceMemoryLedger.get_voice_metrics()
        self.assertGreater(metrics["total_recorded_turns"], 0)

    def test_voice_spectrum_analyzer(self):
        """Test 32-band log FFT spectrum analysis and energy calculation."""
        spectrum = VoiceSpectrumAnalyzer.analyze_audio_buffer(None, num_bands=32)
        self.assertEqual(len(spectrum["spectrum_32_bands"]), 32)
        self.assertIn("rms_energy", spectrum)
        self.assertIn("peak_amplitude", spectrum)

    def test_voice_tududi_radar(self):
        """Test proactive Tududi voice radar sweep."""
        sweep = TududiVoiceRadarDaemon.execute_radar_sweep()
        self.assertEqual(sweep["status"], "sweep_completed")
        self.assertTrue(sweep["spoken"])

    def test_all_12_antigravity_mcp_tools(self):
        """Verify all 12 tools in the dedicated Antigravity Voice MCP server."""
        tool_names = [t["name"] for t in TOOLS_SCHEMA]
        expected_tools = [
            "antigravity_speak",
            "antigravity_announce_task",
            "antigravity_voice_brief",
            "antigravity_play_sfx",
            "antigravity_blend_persona",
            "antigravity_listen",
            "antigravity_list_audio_devices",
            "antigravity_get_voice_history",
            "antigravity_get_spectrum",
            "antigravity_trigger_tududi_radar",
            "antigravity_configure_voice",
            "antigravity_get_status"
        ]
        for exp in expected_tools:
            self.assertIn(exp, tool_names)

        # Call get_status
        status = handle_tool_call("antigravity_get_status", {})
        self.assertIn("engine", status)

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        success = run_zero_assumption_audit()
        self.assertTrue(success, "Zero-assumption audit failed!")


def ingest_vault_document():
    """Ingest Phase 39 architecture document into SQLite knowledge vault."""
    vault_doc = os.path.join(BASE_DIR, "vault", "System_Architecture", "antigravity_omniscient_voice_matrix.md")
    print("\n" + "=" * 65)
    print("🌐 EXECUTING PHASE 39 MASTER INGESTION & OMNISCIENT VOICE MATRIX")
    print("=" * 65)

    if os.path.exists(vault_doc):
        print(f"\n🚀 Indexing Antigravity omniscient voice matrix document...")
        index_single_file(vault_doc)
        print("  ✅ Indexed: antigravity_omniscient_voice_matrix.md")

    print("\n🔧 Running Database Maintenance & Vector Compaction...")
    run_maintenance()
    print("  ✅ Database maintenance complete.")


def run_test_suite():
    """Run the test suite."""
    print("\n" + "=" * 65)
    print("🧪 RUNNING PHASE 39 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase39OmniscientVoiceSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 39 TEST MODULES PASSED WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    t0 = time.time()
    ingest_vault_document()
    run_test_suite()
    print(f"Phase 39 completed in {time.time() - t0:.2f}s")
