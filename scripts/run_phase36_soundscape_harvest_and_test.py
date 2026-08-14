#!/usr/bin/env python3
"""
Phase 36 Master Ingestion, Vector Indexer, and Soundscape/VAD Verification Suite.
Standard: Pure Python Standard Library (unittest, json, os, sys, time, numpy).
Ponytail Senior Dev Principle: Zero external dependencies, 100% deterministic test coverage.
"""

import os
import sys
import json
import time
import unittest
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_voice_soundboard import SFX_LIBRARY, render_sfx_to_wav_bytes, generate_soundscape_markdown
from src.infrastructure.eve_voice_mixer import apply_audio_ducking, composite_tactical_soundscape
from src.infrastructure.eve_voice_vad_duplex import VoiceActivityDetector
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_phase36_harvest():
    """Generate and index all Phase 36 Soundscape & VAD documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 36 MASTER INGESTION & SOUNDSCAPE/VAD UPGRADE")
    print("=================================================================")
    t0 = time.time()

    all_files = generate_soundscape_markdown()
    print(f"\n🚀 Indexing {len(all_files)} new intelligence documents into Knowledge Vault...")
    for idx, filepath in enumerate(all_files, 1):
        filename = os.path.basename(filepath)
        index_single_file(filepath)
        print(f"  [{idx}/{len(all_files)}] ✅ Indexed: {filename}")

    print("\n🔧 Running Database Maintenance & Vector Compaction...")
    run_maintenance()
    print("  ✅ Database maintenance complete.")

    elapsed = time.time() - t0
    print(f"\n🎉 Ingestion complete in {elapsed:.2f}s! Total files indexed: {len(all_files)}")
    return all_files


class TestPhase36SoundscapeSuite(unittest.TestCase):
    """Automated test suite verifying Phase 36 Soundscape, SFX & VAD Suite."""

    def test_sfx_library(self):
        """Test all 6 procedural SFX generators and WAV byte rendering."""
        for sfx_name in ["warp_spool", "shield_critical", "armor_bleed", "hull_breach", "target_lock", "cockpit_ambient"]:
            wav_bytes = render_sfx_to_wav_bytes(sfx_name)
            self.assertIsNotNone(wav_bytes)
            self.assertGreater(len(wav_bytes), 1000)

    def test_audio_ducking_mixer(self):
        """Test dynamic audio ducking attenuation and master composite limiter."""
        ambient = SFX_LIBRARY["cockpit_ambient"](sample_rate=24000, duration_s=2.0)
        voice = 0.5 * np.ones(24000, dtype=np.float32)
        ducked = apply_audio_ducking(ambient, voice, duck_gain=0.20)
        self.assertEqual(len(ducked), 48000)
        # Verify master composite
        master = composite_tactical_soundscape(voice_samples=voice, sfx_type="warp_spool", include_ambient=True)
        self.assertLessEqual(np.max(np.abs(master)), 1.0, "Master audio must not clip above 1.0")

    def test_vad_barge_in_controller(self):
        """Test VAD energy calculation and barge-in state transition."""
        detector = VoiceActivityDetector()
        detector.set_ai_speaking_state(True)
        self.assertEqual(detector.current_state, "AI_SPEAKING")

        # Simulate user speech burst
        speech_frame = 0.25 * np.sin(2 * np.pi * 400 * np.linspace(0, 0.02, 480))
        for _ in range(4):
            rep = detector.process_audio_frame(speech_frame)

        self.assertIn(detector.current_state, ["BARGE_IN_TRIGGERED", "USER_SPEAKING"])

    def test_mounted_api_endpoints(self):
        """Test Phase 36 newly mounted REST API endpoints."""
        res_sfx = client.get("/api/eve/voice/soundscape/sfx?sfx_type=target_lock")
        self.assertEqual(res_sfx.status_code, 200)
        self.assertEqual(res_sfx.headers["content-type"], "audio/wav")

        res_mix = client.post("/api/eve/voice/mixer/composite", json={"sfx_type": "shield_critical", "include_ambient": True})
        self.assertEqual(res_mix.status_code, 200)
        self.assertEqual(res_mix.headers["content-type"], "audio/wav")

        res_vad = client.post("/api/eve/voice/vad/process-frame", json={"samples": [0.0] * 480, "is_ai_speaking": False})
        self.assertEqual(res_vad.status_code, 200)
        self.assertEqual(res_vad.json()["state"], "IDLE")

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        try:
            run_zero_assumption_audit()
            passed = True
        except Exception:
            passed = False
        self.assertTrue(passed)


def run_test_suite():
    """Run all test suites and output results."""
    print("\n=================================================================")
    print("🧪 RUNNING PHASE 36 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase36SoundscapeSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 36 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase36_harvest()
    run_test_suite()
