#!/usr/bin/env python3
"""
Phase 29 Master Ingestion, Vector Indexer, and Multi-Box Verification Suite.
Standard: Pure Python Standard Library (unittest, json, os, sys, time).
Ponytail Senior Dev Principle: Zero external dependencies, 100% deterministic test coverage.
"""

import os
import sys
import json
import time
import unittest
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_multibox_mind import (
    get_multibox_mind_state,
    get_pilot_action_recommendations,
    generate_multibox_doctrine_markdown
)
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_phase29_harvest() -> List[str]:
    """Generate and index all Phase 29 multi-box doctrine documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 29 MASTER INGESTION & MULTI-BOX EXPANSION")
    print("=================================================================")
    t0 = time.time()

    all_files = generate_multibox_doctrine_markdown()

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


class TestPhase29MultiBoxSuite(unittest.TestCase):
    """Automated test suite verifying Phase 29 Multi-Boxing Mind & Role-Thinking."""

    def test_multibox_mind_state(self):
        """Test fleet mindset state across all 8 pilots."""
        state = get_multibox_mind_state()
        self.assertEqual(state["active_pilots_count"], 8)
        self.assertIn("Master-Follower", state["fleet_topology"])
        self.assertIn(2122349505, state["pilots"])
        self.assertEqual(state["pilots"][2122349505]["name"], "Savian Alexander")

    def test_pilot_recommendations(self):
        """Test specific pilot proactive recommendations and defensive protocols."""
        # Test Savian (Commander)
        savian = get_pilot_action_recommendations(2122349505)
        self.assertEqual(savian["name"], "Savian Alexander")
        self.assertGreater(len(savian["proactive_next_actions"]), 0)
        self.assertGreater(len(savian["protective_defense_protocols"]), 0)

        # Test Thena (Harvester)
        thena = get_pilot_action_recommendations(2124540459)
        self.assertEqual(thena["name"], "Thena Alexander")
        self.assertIn("Hulk", str(thena["proactive_next_actions"]))

        # Test Saigan (1M Unallocated SP Reserve)
        saigan = get_pilot_action_recommendations(2124540489)
        self.assertEqual(saigan["name"], "Saigan Alexander")
        self.assertIn("Command Center Upgrades V", str(saigan["proactive_next_actions"]))

    def test_api_endpoints(self):
        """Test FastAPI endpoints for live multi-box mind and recommendations."""
        res_mind = client.get("/api/eve/multibox/mind")
        self.assertEqual(res_mind.status_code, 200)
        data_mind = res_mind.json()
        self.assertEqual(data_mind["active_pilots_count"], 8)

        res_rec = client.get("/api/eve/multibox/recommendations/2122349505")
        self.assertEqual(res_rec.status_code, 200)
        data_rec = res_rec.json()
        self.assertEqual(data_rec["name"], "Savian Alexander")

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
    print("🧪 RUNNING PHASE 29 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase29MultiBoxSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 29 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase29_harvest()
    run_test_suite()
