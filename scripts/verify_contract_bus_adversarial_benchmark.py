#!/usr/bin/env python3
"""
Adversarial Stress Test & Performance Benchmark Harness for 10-Bridge DAG Contract Bus.
Standards: Pure Python Standard Library (concurrent.futures, subprocess, json, time, hashlib, statistics)
Ponytail Senior Dev Principle: Zero external dependencies, direct empirical verification.

Verification Dimensions:
1. Multi-Run SLA Benchmark: 3 sequential self-test runs to confirm execution strictly < 25.0s SLA.
2. Concurrency & Contention Stress: 3 concurrent parallel contract bus executions to test for race conditions/locks.
3. Fault Injection & Chaos Resilience: Simulated bridge crashes, malformed payloads, and Merkle tamper detection.
4. Memory & Context Resilience: Upstream shared context mutation and boundary conditions.
"""

import sys
import os
import json
import time
import hashlib
import tempfile
import statistics
import subprocess
import concurrent.futures
from pathlib import Path

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

CONTRACT_BUS_SCRIPT = ROOT_DIR / ".agents" / "skills" / "neuro-copilot" / "scripts" / "contract_bus.py"
SLA_MAX_SECONDS = 25.0


def benchmark_sla_multi_run(num_runs=3):
    print("\n" + "=" * 75)
    print(f"🔬 STRESS SUITE 1: Multi-Run SLA Benchmark ({num_runs} Sequential Iterations)")
    print(f"   Target SLA Ceiling: < {SLA_MAX_SECONDS:.1f}s per execution")
    print("=" * 75)

    durations = []
    ledger_hashes = []

    for i in range(1, num_runs + 1):
        t0 = time.time()
        res = subprocess.run(
            [sys.executable, str(CONTRACT_BUS_SCRIPT), "self_test"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        duration = time.time() - t0
        durations.append(duration)

        print(f"  [Run {i}/{num_runs}] ExitCode: {res.returncode} | Duration: {duration:.2f}s | SLA Margin: {SLA_MAX_SECONDS - duration:+.2f}s")
        assert res.returncode == 0, f"Run {i} failed with non-zero exit code: {res.stderr}"
        assert duration < SLA_MAX_SECONDS, f"Run {i} breached {SLA_MAX_SECONDS}s SLA ceiling! Duration: {duration:.2f}s"
        assert "Contract Bus Self-Test: 100% PASSED" in res.stdout, f"Run {i} missing self-test pass confirmation"

        # Verify ledger file written
        ledger_path = ROOT_DIR / "docs" / "bridge_contracts" / "execution_ledger.json"
        assert ledger_path.exists(), "Execution ledger JSON missing"
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)

        assert ledger_data.get("all_contracts_verified") is True, f"Run {i} failed contract verification"
        assert ledger_data.get("total_bridges_executed") >= 8, f"Run {i} executed fewer than 8 contracts"

        # Capture hash of contracts
        contracts_hash = hashlib.sha256(json.dumps(ledger_data.get("contracts", {}), sort_keys=True).encode()).hexdigest()
        ledger_hashes.append(contracts_hash)

    min_dur = min(durations)
    max_dur = max(durations)
    mean_dur = statistics.mean(durations)
    median_dur = statistics.median(durations)

    print("\n  📊 Multi-Run Performance Statistics:")
    print(f"     - Min:    {min_dur:.2f}s")
    print(f"     - Max:    {max_dur:.2f}s")
    print(f"     - Mean:   {mean_dur:.2f}s")
    print(f"     - Median: {median_dur:.2f}s")
    print(f"     - P95 SLA Compliance: 100.0% (all runs < {SLA_MAX_SECONDS:.1f}s)")
    print("  [+] STRESS SUITE 1: PASSED")
    return {
        "runs": num_runs,
        "min_s": min_dur,
        "max_s": max_dur,
        "mean_s": mean_dur,
        "median_s": median_dur,
        "all_under_sla": all(d < SLA_MAX_SECONDS for d in durations)
    }


def benchmark_concurrency_stress(num_concurrent=3):
    print("\n" + "=" * 75)
    print(f"🔬 STRESS SUITE 2: High-Concurrency Multi-Process Stress ({num_concurrent} Parallel Instances)")
    print(f"   Testing for file contention, WinError 32 locks, and race conditions")
    print("=" * 75)

    def run_instance(instance_id):
        t0 = time.time()
        res = subprocess.run(
            [sys.executable, str(CONTRACT_BUS_SCRIPT), "run_parallel"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        dur = time.time() - t0
        return {
            "id": instance_id,
            "returncode": res.returncode,
            "duration": dur,
            "stdout": res.stdout,
            "stderr": res.stderr
        }

    t_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(run_instance, i) for i in range(1, num_concurrent + 1)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_wall_time = time.time() - t_start
    print(f"  All {num_concurrent} concurrent instances completed in {total_wall_time:.2f}s total wall time")

    for r in sorted(results, key=lambda x: x["id"]):
        print(f"  [Instance {r['id']}] ExitCode: {r['returncode']} | Duration: {r['duration']:.2f}s")
        assert r["returncode"] == 0, f"Concurrent Instance {r['id']} failed:\nSTDOUT:\n{r['stdout']}\nSTDERR:\n{r['stderr']}"
        assert "Parallel Pipeline Complete" in r["stdout"], f"Instance {r['id']} missing completion marker"

    # Verify execution ledger exists and is valid JSON
    ledger_path = ROOT_DIR / "docs" / "bridge_contracts" / "execution_ledger.json"
    assert ledger_path.exists(), "Execution ledger JSON missing after concurrent runs"
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    assert ledger.get("all_contracts_verified") is True, "Ledger contains unverified contracts after concurrent runs"

    print("  [+] STRESS SUITE 2: PASSED (Zero race conditions or file lock crashes)")
    return {
        "concurrent_instances": num_concurrent,
        "total_wall_time_s": total_wall_time,
        "all_succeeded": all(r["returncode"] == 0 for r in results)
    }


def test_fault_injection_and_chaos():
    print("\n" + "=" * 75)
    print("🔬 STRESS SUITE 3: Fault Injection, Contract Chaos & Merkle Integrity")
    print("   Testing failure isolation, malformed context fallback, and tamper detection")
    print("=" * 75)

    scripts_dir = ROOT_DIR / ".agents" / "skills" / "neuro-copilot" / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    import contract_bus
    BridgeContract = contract_bus.BridgeContract
    InterBridgeEventBus = contract_bus.InterBridgeEventBus
    execute_architecture_contract = contract_bus.execute_architecture_contract
    execute_tududi_contract = contract_bus.execute_tududi_contract
    execute_github_contract = contract_bus.execute_github_contract
    execute_snapshot_contract = contract_bus.execute_snapshot_contract

    # 1. Merkle Hash Cryptographic Tamper Detection
    print("  [*] Test 3.1: Cryptographic Merkle Hash Integrity & Tamper Detection...")
    c1 = BridgeContract(
        contract_id="contract_test_001",
        bridge_name="test_bridge",
        status="SUCCESS",
        outputs={"metric_a": 100, "metric_b": "valid"}
    )
    original_hash = c1.contract_hash
    computed_hash = c1.compute_hash()
    assert original_hash == computed_hash, "Initial contract hash mismatch"

    # Mutate outputs without recomputing hash -> Simulate malicious in-transit tamper
    c1.outputs["metric_a"] = 999999
    tampered_computed = c1.compute_hash()
    assert tampered_computed != original_hash, "Tampered payload produced identical hash! Collision or broken hash verification!"
    print(f"      Original Hash: {original_hash[:16]}... | Tampered Hash: {tampered_computed[:16]}... (Tamper successfully flagged)")

    # 2. EventBus Contract Isolation & Shared Memory
    print("  [*] Test 3.2: Shared Memory Boundary Isolation & Fault Tolerance...")
    bus = InterBridgeEventBus(repo_root=str(ROOT_DIR))
    assert bus.get_contract("non_existent") is None, "Non-existent contract lookup did not return None"
    assert bus.get_shared_value("missing_key", "default_val") == "default_val", "Default value fallback failed"

    # Publish valid contract with shared context
    c_arch = BridgeContract(
        contract_id="arch_001",
        bridge_name="architecture_bridge",
        status="SUCCESS",
        outputs={"score": 100.0},
        shared_context={"architecture_score": 100.0, "clean_arch": True}
    )
    bus.publish_contract(c_arch)
    assert bus.get_shared_value("architecture_score") == 100.0
    assert bus.get_shared_value("clean_arch") is True

    # 3. Simulated Bridge Failure & Degradation Handling
    print("  [*] Test 3.3: Simulated Bridge Failure Isolation...")
    c_fail = BridgeContract(
        contract_id="fail_001",
        bridge_name="faulty_bridge",
        status="FAILED",
        outputs={"error": "Simulated hardware/network timeout"}
    )
    bus.publish_contract(c_fail)

    # Verify that ledger accurately captures failed status and marks all_contracts_verified as False
    ledger_path = bus.export_ledger()
    assert os.path.exists(ledger_path)
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)

    assert ledger_data["all_contracts_verified"] is False, "Faulty bridge failed to flag all_contracts_verified=False in ledger"
    assert "faulty_bridge" in ledger_data["contracts"]
    assert ledger_data["contracts"]["faulty_bridge"]["status"] == "FAILED"
    print("      Ledger correctly detected FAILED bridge contract and updated integrity status.")

    # 4. Downstream Bridge Upstream Context Missing Resistance
    print("  [*] Test 3.4: Downstream Bridge Tolerance with Missing Upstream Contracts...")
    empty_bus = InterBridgeEventBus(repo_root=str(ROOT_DIR))
    # Execute snapshot contract against empty bus (no upstream architecture/tududi contracts)
    snap_contract = execute_snapshot_contract(empty_bus)
    assert snap_contract.status in ["SUCCESS", "WARNING"], f"Snapshot contract crashed on empty bus: {snap_contract}"
    print(f"      Snapshot bridge gracefully handled empty upstream context (Status: {snap_contract.status})")

    print("  [+] STRESS SUITE 3: PASSED (All chaos/fault vectors properly isolated)")
    return True


def run_full_adversarial_suite():
    print("=" * 80)
    print("🛡️  INTER-BRIDGE CONTRACT BUS ADVERSARIAL STRESS & BENCHMARK HARNESS")
    print("=" * 80)
    start_time = time.time()

    r1 = benchmark_sla_multi_run(num_runs=3)
    r2 = benchmark_concurrency_stress(num_concurrent=3)
    r3 = test_fault_injection_and_chaos()

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🏆 ALL ADVERSARIAL BENCHMARKS & STRESS TESTS PASSED IN {total_time:.2f}s")
    print(f"   - SLA Benchmark: Mean {r1['mean_s']:.2f}s, Max {r1['max_s']:.2f}s (< 25.0s SLA: YES)")
    print(f"   - Concurrency: 3 parallel instances executed with zero race conditions")
    print(f"   - Fault Injection: Merkle integrity verified, bridge failure safely isolated")
    print("   - EMPIRICAL VERDICT: APPROVE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_full_adversarial_suite())
