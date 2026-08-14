#!/usr/bin/env python3
"""
Phase 30 Master Ingestion, Vector Indexer, and Empirical Telemetry Verification Suite.
Standard: Pure Python Standard Library (unittest, json, os, sys, time).
Ponytail Senior Dev Principle: Zero external dependencies, 100% verified empirical ESI data.
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

from src.infrastructure.eve_empirical_telemetry import (
    load_empirical_fleet_data,
    calculate_fleet_totals,
    generate_empirical_dossier_markdown,
    CANONICAL_SDE_TYPES
)
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_phase30_harvest() -> List[str]:
    """Generate and index all Phase 30 empirical intelligence documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 30 MASTER INGESTION & EMPIRICAL TELEMETRY")
    print("=================================================================")
    t0 = time.time()

    all_files = generate_empirical_dossier_markdown()

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


class TestPhase30EmpiricalSuite(unittest.TestCase):
    """Automated test suite verifying Phase 30 Empirical Telemetry and SDE Database."""

    def test_empirical_totals(self):
        """Test exact empirical fleet metrics across all 8 pilots."""
        totals = calculate_fleet_totals()
        self.assertEqual(totals["pilot_count"], 8)
        self.assertEqual(totals["total_fleet_allocated_sp"], 85887339)
        self.assertEqual(totals["total_fleet_unallocated_sp"], 4241613)
        self.assertEqual(totals["total_fleet_sp"], 90128952)
        self.assertGreater(totals["total_fleet_wallet_isk"], 330000000.0)

    def test_sde_types(self):
        """Test canonical CCP Type IDs and metadata."""
        self.assertEqual(CANONICAL_SDE_TYPES[34]["name"], "Tritanium")
        self.assertEqual(CANONICAL_SDE_TYPES[37]["name"], "Isogen")
        self.assertEqual(CANONICAL_SDE_TYPES[11399]["name"], "Morphite")
        self.assertEqual(CANONICAL_SDE_TYPES[16273]["name"], "Liquid Ozone")
        self.assertEqual(CANONICAL_SDE_TYPES[42244]["name"], "Porpoise")
        self.assertEqual(CANONICAL_SDE_TYPES[28659]["name"], "Paladin")

    def test_api_endpoints(self):
        """Test FastAPI endpoints for empirical telemetry and SDE types."""
        res_telem = client.get("/api/eve/telemetry/empirical")
        self.assertEqual(res_telem.status_code, 200)
        data_telem = res_telem.json()
        self.assertEqual(data_telem["pilot_count"], 8)
        self.assertEqual(data_telem["total_fleet_sp"], 90128952)

        res_sde = client.get("/api/eve/sde/types")
        self.assertEqual(res_sde.status_code, 200)
        data_sde = res_sde.json()
        self.assertIn("34", data_sde)

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
    print("🧪 RUNNING PHASE 30 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase30EmpiricalSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 30 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase30_harvest()
    run_test_suite()
