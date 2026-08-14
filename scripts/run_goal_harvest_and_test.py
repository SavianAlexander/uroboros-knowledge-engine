"""
Master Harvest, Vector Indexing & Comprehensive Test Suite for /goal Omniscience.

Ponytail: Zero-dependency stdlib implementation (unittest, sqlite3, json, os, sys, time).
"""

import os
import sys
import time
import unittest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_pi_solver import generate_pi_solver_markdown
from src.infrastructure.eve_market_arbitrage import generate_market_arbitrage_markdown
from src.infrastructure.eve_t3c_subsystems import generate_t3c_markdown
from src.infrastructure.eve_wormhole_mechanics import generate_wormhole_markdown
from src.infrastructure.eve_incursions_pochven import generate_incursions_pochven_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance


def run_goal_ingestion():
    print("=================================================================")
    print("🌐 EXECUTING /GOAL MASTER INGESTION & OMNISCIENCE EXPANSION")
    print("=================================================================")

    start_time = time.time()
    all_files = []

    print("\n[1/5] Ingesting Planetary Industry (PI) Solver...")
    all_files.extend(generate_pi_solver_markdown())

    print("[2/5] Ingesting Regional Market Arbitrage Engine...")
    all_files.extend(generate_market_arbitrage_markdown())

    print("[3/5] Ingesting Tech 3 Strategic Cruiser (T3C) Subsystems...")
    all_files.extend(generate_t3c_markdown())

    print("[4/5] Ingesting Wormhole J-Space Mechanics & Space Weather...")
    all_files.extend(generate_wormhole_markdown())

    print("[5/5] Ingesting Incursions & Pochven Flashpoint Blueprints...")
    all_files.extend(generate_incursions_pochven_markdown())

    print(f"\n🚀 Indexing {len(all_files)} new intelligence documents into Knowledge Vault...")
    for idx, f in enumerate(all_files):
        index_single_file(f)
        print(f"  [{idx+1}/{len(all_files)}] ✅ Indexed: {os.path.basename(f)}")

    print("\n🔧 Running Database Maintenance & Vector Compaction...")
    try:
        run_maintenance()
        print("  ✅ Database maintenance complete.")
    except Exception as ex:
        print(f"  ⚠️ Warning: {ex}")

    elapsed = time.time() - start_time
    print(f"\n🎉 Ingestion complete in {elapsed:.2f}s! Total files indexed: {len(all_files)}")


class TestEveOmniscienceSuite(unittest.TestCase):
    def test_sde_cache(self):
        from src.infrastructure.eve_sde_cache import resolve_id_fast
        name = resolve_id_fast(2122349505)
        self.assertIn("Savian", name)

    def test_hybrid_rag(self):
        from src.infrastructure.eve_hybrid_rag import hybrid_search_rrf
        res = hybrid_search_rrf("Savian Alexander Master Refiner")
        self.assertGreaterEqual(res["results_count"], 1)
        self.assertLess(res["latency_ms"], 50.0)

    def test_pi_solver(self):
        from src.infrastructure.eve_pi_solver import solve_pi_production_tree
        res = solve_pi_production_tree("Broadcast Node")
        self.assertEqual(res["commodity"], "Broadcast Node")
        self.assertIn("Barren", res["required_planets"])

    def test_market_arbitrage(self):
        from src.infrastructure.eve_market_arbitrage import calculate_trade_margin
        res = calculate_trade_margin(100.0, 150.0)
        self.assertGreater(res["net_profit"], 30.0)

    def test_zero_assumptions(self):
        from scripts.verify_zero_assumptions import run_zero_assumption_audit
        # Should execute without throwing AssertionError
        run_zero_assumption_audit()


def run_test_suite():
    print("\n=================================================================")
    print("🧪 RUNNING COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEveOmniscienceSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL 5 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_goal_ingestion()
    run_test_suite()
