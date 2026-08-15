#!/usr/bin/env python3
"""
Inter-Bridge Contract Bus Empirical SLA Benchmark & Concurrency Harness
Executes:
1. Multi-iteration timing benchmark under sequential execution
2. Multi-pipeline concurrent execution stress (parallel async pipelines)
3. Statistical jitter analysis (min, max, mean, median, stdev, p95)
4. Bottleneck breakdown across all 8 active bridge runners
5. SLA compliance verification (< 25.0s ceiling)
"""

import sys
import os
import time
import json
import asyncio
import statistics
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "neuro-copilot", "scripts")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from contract_bus import run_parallel_bridge_pipeline_async


async def benchmark_sequential(iterations: int = 3) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"⚡ Running Sequential SLA Benchmark ({iterations} Iterations)")
    print(f"=======================================================")
    
    pipeline_durations = []
    bridge_durations: Dict[str, List[float]] = {}
    reports = []

    for i in range(1, iterations + 1):
        print(f"\n--- Iteration {i}/{iterations} ---")
        t0 = time.time()
        rep = await run_parallel_bridge_pipeline_async(repo_root=REPO_ROOT)
        dur = (time.time() - t0) * 1000
        pipeline_durations.append(dur)
        reports.append(rep)
        print(f"Iteration {i} Total Time: {dur:.2f}ms (Reported: {rep['total_duration_ms']:.2f}ms)")
        
        for name, summary in rep.get("contracts_summary", {}).items():
            bridge_durations.setdefault(name, []).append(summary["duration_ms"])

    stats = {
        "iterations": iterations,
        "durations_ms": pipeline_durations,
        "min_ms": round(min(pipeline_durations), 2),
        "max_ms": round(max(pipeline_durations), 2),
        "mean_ms": round(statistics.mean(pipeline_durations), 2),
        "median_ms": round(statistics.median(pipeline_durations), 2),
        "stdev_ms": round(statistics.stdev(pipeline_durations), 2) if len(pipeline_durations) > 1 else 0.0,
        "sla_ceiling_ms": 25000.0,
        "sla_compliant": all(d < 25000.0 for d in pipeline_durations),
        "bridge_breakdown_avg_ms": {
            k: round(statistics.mean(v), 2) for k, v in bridge_durations.items()
        }
    }
    return stats


async def benchmark_concurrency(concurrency_level: int = 2) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"⚡ Running Concurrency Stress Test ({concurrency_level} Concurrent Pipelines)")
    print(f"=======================================================")
    
    t0 = time.time()
    tasks = [run_parallel_bridge_pipeline_async(repo_root=REPO_ROOT) for _ in range(concurrency_level)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_elapsed_ms = (time.time() - t0) * 1000

    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
    all_verified = all(isinstance(r, dict) and r.get("all_contracts_verified") for r in results)

    print(f"Concurrent execution finished in {total_elapsed_ms:.2f}ms")
    print(f"Success count: {success_count}/{concurrency_level}, All verified: {all_verified}")

    return {
        "concurrency_level": concurrency_level,
        "total_elapsed_ms": round(total_elapsed_ms, 2),
        "success_count": success_count,
        "all_contracts_verified": all_verified,
        "exceptions": [str(r) for r in results if isinstance(r, Exception)]
    }


async def main_async():
    print("=== Inter-Bridge Contract Bus Empirical Benchmark & Stress Suite ===")
    
    # 1. Sequential SLA Benchmark
    seq_stats = await benchmark_sequential(iterations=3)
    
    # 2. Concurrency Stress
    conc_stats = await benchmark_concurrency(concurrency_level=2)

    print("\n=======================================================")
    print("📊 BENCHMARK SUMMARY")
    print("=======================================================")
    print(f"Sequential Iterations : {seq_stats['iterations']}")
    print(f"Min Duration          : {seq_stats['min_ms']}ms ({seq_stats['min_ms']/1000:.2f}s)")
    print(f"Max Duration          : {seq_stats['max_ms']}ms ({seq_stats['max_ms']/1000:.2f}s)")
    print(f"Mean Duration         : {seq_stats['mean_ms']}ms ({seq_stats['mean_ms']/1000:.2f}s)")
    print(f"Median Duration       : {seq_stats['median_ms']}ms ({seq_stats['median_ms']/1000:.2f}s)")
    print(f"Standard Deviation    : {seq_stats['stdev_ms']}ms")
    print(f"SLA Ceiling (<25.0s)  : {'✅ COMPLIANT' if seq_stats['sla_compliant'] else '❌ BREACHED'}")
    print("\nBridge Average Breakdown:")
    for b_name, b_avg in sorted(seq_stats["bridge_breakdown_avg_ms"].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {b_name:<26}: {b_avg:.1f}ms")

    print("\nConcurrency Test Summary:")
    print(f"  - Pipelines Executed: {conc_stats['concurrency_level']}")
    print(f"  - Success Rate      : {conc_stats['success_count']}/{conc_stats['concurrency_level']}")
    print(f"  - Total Elapsed     : {conc_stats['total_elapsed_ms']:.1f}ms")
    print(f"  - All Verified      : {conc_stats['all_contracts_verified']}")

    # Assertions
    assert seq_stats["sla_compliant"], f"SLA violated: Max {seq_stats['max_ms']}ms exceeds 25000ms"
    assert conc_stats["all_contracts_verified"], "Concurrent execution contract verification failed"

    print("\n=======================================================")
    print("✅ ALL EMPIRICAL CHALLENGER BENCHMARKS PASSED")
    print("=======================================================")

    # Write results to json for reporting
    out_file = os.path.join(REPO_ROOT, ".agents", "challenger_m3_1", "benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"sequential": seq_stats, "concurrency": conc_stats}, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main_async())
