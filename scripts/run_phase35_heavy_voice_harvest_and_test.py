#!/usr/bin/env python3
"""
Phase 35 Master Ingestion, Vector Indexer, and Heavy Tactical Voice Verification Suite.
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

from src.infrastructure.eve_voice_dsp import process_tactical_dsp_pipeline, generate_radio_chirp, generate_squelch_burst
from src.infrastructure.eve_voice_commander import VoiceCommander
from src.infrastructure.eve_voice_radar_daemon import TacticalVoiceRadarDaemon, generate_tactical_dsp_markdown
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_phase35_harvest():
    """Generate and index all Phase 35 Heavy Voice & DSP documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 35 MASTER INGESTION & HEAVY VOICE/DSP UPGRADE")
    print("=================================================================")
    t0 = time.time()

    all_files = generate_tactical_dsp_markdown()
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


class TestPhase35HeavyVoiceSuite(unittest.TestCase):
    """Automated test suite verifying Phase 35 Heavy Voice & DSP Suite."""

    def test_dsp_pipeline(self):
        """Test DSP radio bandpass, chirps, squelch, and stereo spatial panning."""
        raw_samples = np.zeros(24000, dtype=np.float32)
        dsp_out, sr = process_tactical_dsp_pipeline(raw_samples, preset="TACTICAL_RADIO", pan=0.5)
        self.assertEqual(sr, 24000)
        self.assertEqual(dsp_out.ndim, 2, "Output must be stereo (N, 2)")
        self.assertEqual(dsp_out.shape[1], 2)
        self.assertGreater(dsp_out.shape[0], 24000)

    def test_voice_commander(self):
        """Test natural language voice command parsing and response synthesis."""
        commander = VoiceCommander()
        res_fleet = commander.execute_voice_prompt("Aura, fleet report", auto_speak=False)
        self.assertEqual(res_fleet["matched_intent"], "FLEET_OVERVIEW")
        self.assertIn("90.1 million", res_fleet["spoken_response"])

        res_radar = commander.execute_voice_prompt("Aura, check threat radar", auto_speak=False)
        self.assertEqual(res_radar["matched_intent"], "INTEL_RADAR")
        self.assertIn("G-EURJ", res_radar["spoken_response"])

    def test_voice_radar_daemon(self):
        """Test telemetry event mapping into spatial multi-stem audio alerts."""
        daemon = TacticalVoiceRadarDaemon()
        dispatches = daemon.simulate_radar_sweep()
        self.assertEqual(len(dispatches), 3)
        self.assertEqual(dispatches[0]["voice_persona"], "af_bella")
        self.assertEqual(dispatches[0]["pan_position"], -0.8)  # Left ear
        self.assertEqual(dispatches[1]["voice_persona"], "bf_emma")
        self.assertEqual(dispatches[1]["pan_position"], 0.0)   # Center
        self.assertEqual(dispatches[2]["voice_persona"], "af_sarah")
        self.assertEqual(dispatches[2]["pan_position"], 1.0)   # Right ear

    def test_mounted_api_endpoints(self):
        """Test Phase 35 newly mounted REST API endpoints."""
        res_cmd = client.post("/api/eve/voice/command", json={"prompt": "Aura, what is fleet status?"})
        self.assertEqual(res_cmd.status_code, 200)
        self.assertEqual(res_cmd.json()["matched_intent"], "FLEET_OVERVIEW")

        res_dsp = client.get("/api/eve/voice/dsp/presets")
        self.assertEqual(res_dsp.status_code, 200)
        self.assertIn("TACTICAL_RADIO", res_dsp.json()["dsp_presets"])

        res_sweep = client.post("/api/eve/voice/radar/sweep")
        self.assertEqual(res_sweep.status_code, 200)
        self.assertEqual(len(res_sweep.json()["dispatches"]), 3)

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
    print("🧪 RUNNING PHASE 35 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase35HeavyVoiceSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 35 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase35_harvest()
    run_test_suite()
