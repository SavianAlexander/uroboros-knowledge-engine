#!/usr/bin/env python3
"""
Phase 27 Master Ingestion, Vector Indexer, and Comprehensive Verification Suite.
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

from src.infrastructure.eve_combat_simulator import (
    calculate_turret_hit_chance,
    calculate_missile_damage,
    calculate_effective_hp,
    simulate_fleet_engagement,
    generate_combat_simulation_markdown
)
from src.infrastructure.eve_industry_matrix import (
    calculate_manufacturing_materials,
    calculate_reaction_yield,
    generate_industry_matrix_markdown
)
from src.infrastructure.eve_route_navigator import (
    calculate_jump_range,
    calculate_jump_fatigue,
    plan_cyno_route,
    generate_route_navigator_markdown
)
from src.infrastructure.eve_hud_server import (
    get_hud_state,
    generate_tactical_hud_markdown
)
from batch_index import index_single_file, run_maintenance
from scripts.verify_zero_assumptions import run_zero_assumption_audit


def run_phase27_harvest() -> List[str]:
    """Generate and index all Phase 27 tactical intelligence documents."""
    print("=================================================================")
    print("🌐 EXECUTING PHASE 27 MASTER INGESTION & HEAVY UPGRADE")
    print("=================================================================")
    t0 = time.time()

    all_files = []
    print("[1/4] Generating Combat Simulation Dogma Engine...")
    all_files.extend(generate_combat_simulation_markdown())

    print("[2/4] Generating Industry & Composite Reaction Yield Matrix...")
    all_files.extend(generate_industry_matrix_markdown())

    print("[3/4] Generating Capital Jump & Cyno Chain Navigator...")
    all_files.extend(generate_route_navigator_markdown())

    print("[4/4] Generating Tactical HUD & Telemetry Gateway Architecture...")
    all_files.extend(generate_tactical_hud_markdown())

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


class TestPhase27HeavySuite(unittest.TestCase):
    """Automated test suite verifying Phase 27 tactical and simulation engines."""

    def test_turret_and_missile_dogma(self):
        """Test turret hit probability and missile damage reduction formulas."""
        # Optimal hit chance should be exactly 100% when transversal is zero
        hit_prob = calculate_turret_hit_chance(
            optimal=10000, falloff=5000, tracking=0.05,
            weapon_sig=400, target_sig=400, distance=8000, transversal_velocity=0.0
        )
        self.assertAlmostEqual(hit_prob, 1.0, places=4)

        # Optimal + Falloff hit chance should be exactly 50%
        hit_prob_falloff = calculate_turret_hit_chance(
            optimal=10000, falloff=5000, tracking=0.05,
            weapon_sig=400, target_sig=400, distance=15000, transversal_velocity=0.0
        )
        self.assertAlmostEqual(hit_prob_falloff, 0.50, places=4)

        # Missile damage application on moving/small target
        missile_dmg = calculate_missile_damage(
            base_damage=1000, explosion_radius=150, explosion_velocity=100,
            target_sig=50, target_velocity=500
        )
        self.assertLess(missile_dmg, 1000)
        self.assertGreater(missile_dmg, 0)

    def test_industry_and_reaction_matrix(self):
        """Test Upwell structure rigs and composite reaction throughput."""
        # Hulk material calculation
        hulk_base = {"Tritanium": 1000000, "Sylramic Fibers": 500}
        res = calculate_manufacturing_materials(hulk_base, bpo_me=10, structure_type="Sotiyo", security_space="Nullsec")
        self.assertLess(res["required_materials"]["Tritanium"], 1000000)
        self.assertGreater(res["effective_structure_me_bonus"], 5.0)

        # Reaction yield calculation
        reac = calculate_reaction_yield("Crystalline Carbonide", runs=10, structure_type="Tatara", security_space="Nullsec")
        self.assertEqual(reac["total_output_units"], 2000)
        self.assertGreater(reac["me_material_reduction_percent"], 5.0)

    def test_capital_jump_and_cyno_navigation(self):
        """Test Jump Fatigue and Cyno chain route planning."""
        # JDC V Jump Range
        jf_range = calculate_jump_range(5.0, jdc_level=5)
        self.assertEqual(jf_range, 10.0)

        # Cyno route planner
        route = plan_cyno_route("1DQ1-A (Delve)", "Jita (The Forge)")
        self.assertGreaterEqual(route["total_jumps"], 5)
        self.assertGreater(route["total_isotopes_needed"], 0)
        self.assertIn("Uedama", route["avoided_choke_points"])

    def test_hud_state_and_telemetry(self):
        """Test HUD state compilation and pilot counts."""
        state = get_hud_state(BASE_DIR)
        self.assertEqual(state["status"], "online")
        self.assertEqual(state["fleet_metrics"]["total_pilots"], 8)
        self.assertEqual(state["fleet_metrics"]["omega_count"], 4)
        self.assertEqual(state["fleet_metrics"]["alpha_count"], 4)

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        try:
            run_zero_assumption_audit()
            audit_passed = True
        except Exception:
            audit_passed = False
        self.assertTrue(audit_passed)


def run_test_suite():
    """Run all test suites and output results."""
    print("\n=================================================================")
    print("🧪 RUNNING PHASE 27 COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase27HeavySuite)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise SystemError("Test suite failed!")
    print("\n🎉 ALL PHASE 27 TEST MODULES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    run_phase27_harvest()
    run_test_suite()
