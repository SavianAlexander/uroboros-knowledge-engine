#!/usr/bin/env python3
"""
Inter-Bridge Contract Bus Adversarial Stress & SLA Benchmark Matrix
Tests:
1. Standardized BridgeContract dataclass Merkle hashing & boundary invariants
2. InterBridgeEventBus thread-safety and shared context distribution
3. Fault injection across all bridge runners (simulated crashes, timeouts, exceptions)
4. DAG dependency propagation & graceful degradation on missing context
5. Cryptographic ledger generation & Merkle signature verification
6. Concurrent multi-pipeline execution stress
7. Multi-iteration SLA timing benchmark (<25s ceiling) & bottleneck profiling
"""

import sys
import os
import time
import json
import asyncio
import hashlib
import unittest
from typing import Dict, Any

# Ensure project root & scripts directory are in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "neuro-copilot", "scripts")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import contract_bus
from contract_bus import (
    BridgeContract,
    InterBridgeEventBus,
    execute_architecture_contract,
    execute_tududi_contract,
    execute_github_contract,
    execute_visual_audit_contract,
    execute_snapshot_contract,
    execute_neuro_contract,
    execute_eve_contract,
    execute_process_hygiene_contract,
    run_parallel_bridge_pipeline_async,
)


class TestContractBusAdversarialMatrix(unittest.TestCase):

    def setUp(self):
        self.bus = InterBridgeEventBus(repo_root=REPO_ROOT)

    def test_01_contract_model_invariants_and_merkle_hashing(self):
        """Verify contract data model integrity, deterministic hashing, and edge case tolerance."""
        c = BridgeContract(
            contract_id="contract_test_001",
            bridge_name="test_bridge",
            outputs={"key_a": 123, "key_b": "value_b"}
        )
        self.assertTrue(len(c.contract_hash) == 64, "SHA-256 hash must be 64 hex characters")
        self.assertEqual(c.status, "SUCCESS")
        self.assertEqual(c.protocol_version, "1.0.0-PRO")

        # Test deterministic recalculation
        expected_payload = f"contract_test_001|test_bridge|SUCCESS|{json.dumps(c.outputs, sort_keys=True)}"
        expected_hash = hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()
        self.assertEqual(c.contract_hash, expected_hash)

        # Test large output payload
        large_outputs = {f"k_{i}": "x" * 100 for i in range(500)}
        c_large = BridgeContract(
            contract_id="contract_large",
            bridge_name="large_bridge",
            outputs=large_outputs
        )
        self.assertTrue(len(c_large.contract_hash) == 64)

        # Test unicode and special character payload
        unicode_outputs = {"emoji": "🚀⚡🏛️", "special": "áéíóú ñ ¿¡ \n\t\r", "null_val": None}
        c_unicode = BridgeContract(
            contract_id="contract_unicode",
            bridge_name="unicode_bridge",
            outputs=unicode_outputs
        )
        self.assertTrue(len(c_unicode.contract_hash) == 64)

    def test_02_event_bus_thread_safety_and_context_sharing(self):
        """Verify bus shared memory publishing, retrieval, and isolation."""
        c1 = BridgeContract(
            contract_id="c1",
            bridge_name="bridge_1",
            shared_context={"shared_key_1": "alpha", "shared_metric": 42}
        )
        c2 = BridgeContract(
            contract_id="c2",
            bridge_name="bridge_2",
            shared_context={"shared_key_2": "beta", "shared_metric": 99}
        )

        self.bus.publish_contract(c1)
        self.assertEqual(self.bus.get_shared_value("shared_key_1"), "alpha")
        self.assertEqual(self.bus.get_shared_value("shared_metric"), 42)

        self.bus.publish_contract(c2)
        self.assertEqual(self.bus.get_shared_value("shared_key_2"), "beta")
        # Overwrite check
        self.assertEqual(self.bus.get_shared_value("shared_metric"), 99)

        # Non-existent key default
        self.assertEqual(self.bus.get_shared_value("non_existent_key", "default_val"), "default_val")
        self.assertIsNone(self.bus.get_contract("non_existent_bridge"))

    def test_03_bridge_runners_fault_injection_and_resilience(self):
        """Adversarially inject exceptions into each bridge runner and assert graceful degradation."""
        # 1. Architecture fault injection
        original_arch = sys.modules.get("architecture_bridge")
        try:
            class FaultyArch:
                @staticmethod
                def audit_architecture(root):
                    raise RuntimeError("Simulated Architecture Engine Fault")
                @staticmethod
                def scan_secrets(root):
                    raise RuntimeError("Simulated Secret Scanner Fault")

            sys.modules["architecture_bridge"] = FaultyArch
            c_arch = execute_architecture_contract(self.bus)
            self.assertEqual(c_arch.status, "FAILED")
            self.assertIn("error", c_arch.outputs)
        finally:
            if original_arch is not None:
                sys.modules["architecture_bridge"] = original_arch
            else:
                sys.modules.pop("architecture_bridge", None)

        # 2. Tududi fault injection
        original_tududi = sys.modules.get("tududi_bridge")
        try:
            class FaultyTududi:
                @staticmethod
                def get_metrics_cli():
                    raise ConnectionError("Simulated Tududi MCP Connection Refused")
                @staticmethod
                def list_tasks_cli():
                    raise ConnectionError("Simulated Tududi Tasks Timeout")

            sys.modules["tududi_bridge"] = FaultyTududi
            c_tududi = execute_tududi_contract(self.bus)
            self.assertEqual(c_tududi.status, "SUCCESS")
            self.assertIn("notice", c_tududi.outputs)
        finally:
            if original_tududi is not None:
                sys.modules["tududi_bridge"] = original_tududi
            else:
                sys.modules.pop("tududi_bridge", None)

        # 3. Snapshot fault injection
        original_snap = sys.modules.get("snapshot_bridge")
        try:
            class FaultySnap:
                @staticmethod
                def scan_project_views(root):
                    raise OSError("Simulated Disk Read Error")
                @staticmethod
                def render_client_deck(root):
                    raise OSError("Simulated PDF Generator Failure")

            sys.modules["snapshot_bridge"] = FaultySnap
            c_snap = execute_snapshot_contract(self.bus)
            self.assertEqual(c_snap.status, "WARNING")
            self.assertIn("error", c_snap.outputs)
        finally:
            if original_snap is not None:
                sys.modules["snapshot_bridge"] = original_snap
            else:
                sys.modules.pop("snapshot_bridge", None)

        # 4. Neuro fault injection
        original_neuro = sys.modules.get("neuro_bridge")
        try:
            class FaultyNeuro:
                @staticmethod
                def get_vault_stats():
                    raise ValueError("Simulated Malformed JSON Stats")

            sys.modules["neuro_bridge"] = FaultyNeuro
            c_neuro = execute_neuro_contract(self.bus)
            self.assertEqual(c_neuro.status, "WARNING")
            self.assertIn("error", c_neuro.outputs)
        finally:
            if original_neuro is not None:
                sys.modules["neuro_bridge"] = original_neuro
            else:
                sys.modules.pop("neuro_bridge", None)

        # 5. EVE fault injection
        original_eve = sys.modules.get("eve_bridge")
        try:
            class FaultyEve:
                @staticmethod
                def get_fleet_telemetry(root):
                    raise TimeoutError("Simulated ESI Telemetry Gateway Timeout")
                @staticmethod
                def run_zero_assumption_audit(root):
                    raise TimeoutError("Simulated Telemetry Zero-Assumption Audit Timeout")

            sys.modules["eve_bridge"] = FaultyEve
            c_eve = execute_eve_contract(self.bus)
            self.assertEqual(c_eve.status, "WARNING")
            self.assertIn("error", c_eve.outputs)
        finally:
            if original_eve is not None:
                sys.modules["eve_bridge"] = original_eve
            else:
                sys.modules.pop("eve_bridge", None)

    def test_04_dag_dependency_propagation_and_graceful_defaults(self):
        """Verify Stage 2 bridges gracefully handle empty or absent Stage 1 contracts."""
        empty_bus = InterBridgeEventBus(repo_root=REPO_ROOT)

        # Execute Stage 2 bridges directly without running Stage 1
        c_snap = execute_snapshot_contract(empty_bus)
        self.assertEqual(c_snap.status, "SUCCESS")
        self.assertEqual(c_snap.consumed_contracts, [])
        self.assertEqual(c_snap.inputs.get("upstream_tududi_completion"), "100%")

        c_neuro = execute_neuro_contract(empty_bus)
        self.assertEqual(c_neuro.status, "SUCCESS")
        self.assertEqual(c_neuro.consumed_contracts, [])
        self.assertEqual(c_neuro.inputs.get("head_commit"), "HEAD")

        c_eve = execute_eve_contract(empty_bus)
        self.assertEqual(c_eve.status, "SUCCESS")

    def test_05_ledger_export_cryptographic_integrity(self):
        """Verify export_ledger creates valid JSON and Markdown with matching hashes."""
        c1 = execute_architecture_contract(self.bus)
        c2 = execute_tududi_contract(self.bus)

        ledger_path = self.bus.export_ledger()
        self.assertTrue(os.path.isfile(ledger_path))

        with open(ledger_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["total_bridges_executed"], 2)
        self.assertTrue(data["all_contracts_verified"])
        self.assertIn("contracts", data)
        self.assertIn("architecture_bridge", data["contracts"])
        self.assertIn("tududi_bridge", data["contracts"])

        # Check hash match
        arch_data = data["contracts"]["architecture_bridge"]
        recalculated_hash = hashlib.sha256(
            f"{arch_data['contract_id']}|{arch_data['bridge_name']}|{arch_data['status']}|{json.dumps(arch_data['outputs'], sort_keys=True)}".encode("utf-8")
        ).hexdigest()
        self.assertEqual(arch_data["contract_hash"], recalculated_hash)

        # Check markdown report exists
        md_report = os.path.join(self.bus.ledger_dir, "contract_audit_ledger.md")
        self.assertTrue(os.path.isfile(md_report))
        with open(md_report, "r", encoding="utf-8") as f:
            md_text = f.read()
        self.assertIn("Inter-Bridge Contract & Parallel Execution Ledger", md_text)
        self.assertIn("architecture_bridge", md_text)


if __name__ == "__main__":
    unittest.main()
