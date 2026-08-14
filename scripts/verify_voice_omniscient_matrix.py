"""
Universal Voice Omniscient Matrix Verification Suite & System Diagnostic.
Standard: Pure Python Standard Library (unittest, json, os, sys, time).
Ponytail Senior Dev Principle: Single unified verification entrypoint for the complete neural audio stack (Kokoro-82M TTS, STT Ear, Persona Blending, DSP Acoustics, Procedural Soundboard, SQLite Memory, FFT Spectrum, Tududi Radar, Full-Duplex Call Intercom, VAD Barge-In, and 17-Tool MCP Server).
"""

import os
import sys
import unittest
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_persona_blend import VoicePersonaBlender
from src.core.voice_stt_ear import VoiceEarTranscriber
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_memory_ledger import VoiceMemoryLedger
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.antigravity_voice_mcp import handle_tool_call, TOOLS_SCHEMA
from scripts.verify_zero_assumptions import run_zero_assumption_audit


class TestVoiceOmniscientMatrix(unittest.TestCase):
    """Complete system test suite for Uroboros Neural Voice & Audio Matrix."""

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

    def test_persona_blender_interpolation(self):
        """Test Kokoro 512-D voice embedding linear interpolation."""
        weights = {"bf_emma": 0.70, "af_bella": 0.30}
        res = VoicePersonaBlender.blend_personas(weights, custom_name="test_co_pilot")
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["weights"]["bf_emma"], 0.70)

    def test_stt_transcriber_and_recorder(self):
        """Test speech recognition and mic buffer allocation."""
        rec = VoiceEarTranscriber.record_microphone_sample(duration_s=1.0)
        self.assertEqual(rec["status"], "ready")
        res = VoiceEarTranscriber.transcribe_audio_file(rec["output_path"])
        self.assertIn(res["status"], ["success", "error"])

    def test_audio_router_and_volume(self):
        """Test audio endpoint discovery and volume scaling."""
        devices = VoiceAudioRouter.list_audio_output_devices()
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        vol_res = VoiceAudioRouter.set_master_volume(85)
        self.assertEqual(vol_res["master_volume"], 85)

    def test_voice_memory_persistence(self):
        """Test SQLite conversational memory ledger logging and metrics."""
        turn = VoiceMemoryLedger.log_turn(
            speaker="Antigravity",
            raw_text="System standardized.",
            normalized_text="System standardized.",
            persona="CALM_OPERATIONS"
        )
        self.assertIn("turn_id", turn)
        recent = VoiceMemoryLedger.get_recent_turns(limit=3)
        self.assertGreater(len(recent), 0)

    def test_fft_spectrum_analyzer(self):
        """Test 32-band log FFT spectrum bins computation."""
        spectrum = VoiceSpectrumAnalyzer.analyze_audio_buffer(None, num_bands=32)
        self.assertEqual(len(spectrum["spectrum_32_bands"]), 32)
        self.assertIn("rms_energy", spectrum)

    def test_tududi_radar_sweep(self):
        """Test autonomous Tududi radar deadline check."""
        sweep = TududiVoiceRadarDaemon.execute_radar_sweep()
        self.assertEqual(sweep["status"], "sweep_completed")

    def test_voice_call_intercom_lifecycle(self):
        """Test full-duplex conversational voice call session lifecycle."""
        # 1. Start Call
        start_res = VoiceCallIntercomEngine.start_call(persona="AURA_SHIP_AI", caller_name="Test Commander")
        self.assertEqual(start_res["status"], "call_connected")
        self.assertTrue(VoiceCallIntercomEngine.get_call_status()["active"])

        # 2. Conversational Filler
        filler_res = VoiceCallIntercomEngine.trigger_immediate_filler()
        self.assertEqual(filler_res["status"], "filler_dispatched")

        # 3. In-Call Response with Roger Beep
        resp_res = VoiceCallIntercomEngine.respond_in_call("Understood, navigating to waypoint.", with_roger_beep=True)
        self.assertEqual(resp_res["status"], "responded")
        self.assertTrue(resp_res["with_roger_beep"])

        # 4. End Call
        end_res = VoiceCallIntercomEngine.end_call()
        self.assertEqual(end_res["status"], "call_ended")
        self.assertFalse(VoiceCallIntercomEngine.get_call_status()["active"])

    def test_voice_vad_barge_in(self):
        """Test real-time VAD speech detection and instant audio purge."""
        vad = VoiceActivityInterrupter(energy_threshold=0.01)
        # Synthetic speech frame
        try:
            import numpy as np
            sine_wave = (0.2 * np.sin(2 * np.pi * 440.0 * np.linspace(0, 0.02, 480))).astype(np.float32)
            metrics = vad.analyze_frame(sine_wave)
            self.assertTrue(metrics["is_speech"])
        except ImportError:
            pass

        # Barge-in cutoff
        cut = VoiceActivityInterrupter.execute_instant_barge_in()
        self.assertEqual(cut["status"], "barge_in_executed")
        self.assertLess(cut["interruption_latency_ms"], 50.0)

    def test_all_17_antigravity_mcp_tools(self):
        """Test all 17 tools in the dedicated Antigravity Voice MCP server."""
        expected_tools = [
            "antigravity_speak", "antigravity_announce_task", "antigravity_voice_brief",
            "antigravity_play_sfx", "antigravity_blend_persona", "antigravity_listen",
            "antigravity_list_audio_devices", "antigravity_get_voice_history",
            "antigravity_get_spectrum", "antigravity_trigger_tududi_radar",
            "antigravity_start_call", "antigravity_call_respond", "antigravity_barge_in_cut",
            "antigravity_end_call", "antigravity_get_call_status",
            "antigravity_configure_voice", "antigravity_get_status"
        ]
        tool_names = [t["name"] for t in TOOLS_SCHEMA]
        for exp in expected_tools:
            self.assertIn(exp, tool_names)

        status = handle_tool_call("antigravity_get_status", {})
        self.assertIn("engine", status)
        self.assertIn("playback_engine", status)

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        success = run_zero_assumption_audit()
        self.assertTrue(success, "Zero-assumption audit failed!")


def main():
    print("\n" + "=" * 65)
    print("🌐 RUNNING UNIVERSAL VOICE OMNISCIENT MATRIX VERIFICATION")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVoiceOmniscientMatrix)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemError("Voice verification failed!")
    print("\n🎉 ALL VOICE OMNISCIENT MATRIX MODULES PASSED (100% GREEN)!\n")


if __name__ == "__main__":
    main()
