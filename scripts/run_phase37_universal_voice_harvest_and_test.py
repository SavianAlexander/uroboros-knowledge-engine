#!/usr/bin/env python3
"""
Phase 37 Master Ingestion, Vector Indexer, and Universal Polyglot Voice Bridge Verification Suite.
Standard: Pure Python Standard Library (unittest, json, os, sys, time, asyncio).
Ponytail Senior Dev Principle: 100% deterministic validation of OpenAI Audio API, MCP Voice Tools, and Multi-Domain Profiles.
"""

import os
import sys
import json
import time
import asyncio
import unittest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit
from fastapi.testclient import TestClient
from main import app
from src.mcp_server import handle_call_tool

client = TestClient(app)


def run_phase37_harvest():
    """Generate and index all Phase 37 Universal Voice Bridge documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 37 MASTER INGESTION & UNIVERSAL VOICE BRIDGE")
    print("=================================================================")
    t0 = time.time()

    doc_file = os.path.join(BASE_DIR, "vault", "System_Architecture", "universal_voice_bridge_architecture.md")
    print(f"\n🚀 Indexing universal voice bridge document into Knowledge Vault...")
    index_single_file(doc_file)
    print(f"  [1/1] ✅ Indexed: universal_voice_bridge_architecture.md")

    print("\n🔧 Running Database Maintenance & Vector Compaction...")
    run_maintenance()
    print("  ✅ Database maintenance complete.")

    elapsed = time.time() - t0
    print(f"\n🎉 Ingestion complete in {elapsed:.2f}s!")
    return [doc_file]


class TestPhase37UniversalVoiceSuite(unittest.TestCase):
    """Automated test suite verifying Phase 37 Universal Voice Bridge."""

    def test_voice_bridge_profiles(self):
        """Test all multi-domain profiles and helper dispatchers."""
        for domain, conf in DOMAIN_PROFILES.items():
            res = VoiceBridge.speak(f"Testing {domain} audio dispatch.", domain=domain, priority="NORMAL")
            self.assertTrue(res["dispatched"])
            self.assertEqual(res["domain"], domain)

        # Test DevOps and Tududi helpers
        r_ci = VoiceBridge.announce_ci_pipeline_status("CI Pipeline", passed=True)
        self.assertTrue(r_ci["dispatched"])
        r_brief = VoiceBridge.announce_tududi_daily_brief(pending_count=4, completed_today=7)
        self.assertTrue(r_brief["dispatched"])

    def test_openai_speech_api(self):
        """Test standard OpenAI /v1/audio/speech and /v1/audio/voices endpoints."""
        # 1. POST /v1/audio/speech
        payload = {
            "model": "kokoro",
            "input": "Universal OpenAI audio protocol verified.",
            "voice": "bf_emma",
            "response_format": "wav"
        }
        res_speech = client.post("/v1/audio/speech", json=payload)
        self.assertEqual(res_speech.status_code, 200)
        self.assertEqual(res_speech.headers["content-type"], "audio/wav")
        self.assertGreater(len(res_speech.content), 5000)

        # 2. GET /v1/audio/voices
        res_voices = client.get("/v1/audio/voices")
        self.assertEqual(res_voices.status_code, 200)
        self.assertIn("voices", res_voices.json())

    def test_universal_api_endpoints(self):
        """Test /api/voice/speak, /api/voice/profiles, /api/voice/sfx endpoints."""
        res_speak = client.post("/api/voice/speak", json={"text": "Hello world", "domain": "EXECUTIVE_ASSISTANT"})
        self.assertEqual(res_speak.status_code, 200)
        self.assertEqual(res_speak.json()["status"], "success")

        res_prof = client.get("/api/voice/profiles")
        self.assertEqual(res_prof.status_code, 200)
        self.assertIn("DEV_OPS", res_prof.json()["domain_profiles"])

        res_sfx = client.get("/api/voice/sfx/target_lock")
        self.assertEqual(res_sfx.status_code, 200)
        self.assertEqual(res_sfx.headers["content-type"], "audio/wav")

    def test_mcp_voice_tools(self):
        """Test neuro_speak and neuro_play_sfx MCP tools."""
        async def run_mcp_checks():
            res_speak = await handle_call_tool("neuro_speak", {"text": "MCP Voice tool verified.", "domain": "DEV_OPS"})
            self.assertEqual(len(res_speak), 1)
            self.assertIn("Spoken via VoiceBridge", res_speak[0].text)

            res_sfx = await handle_call_tool("neuro_play_sfx", {"sfx_name": "shield_critical"})
            self.assertEqual(len(res_sfx), 1)
            self.assertIn("synthesized successfully", res_sfx[0].text)

        asyncio.run(run_mcp_checks())

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
    print("🧪 RUNNING PHASE 37 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase37UniversalVoiceSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 37 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase37_harvest()
    run_test_suite()
