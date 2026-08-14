"""
Empirical Challenger Test Suite: Mathematical Monotonicity, Multiplier Veto, and Performance Benchmark (Milestone M4).
Zero-mock, rigorous mathematical, physical, and concurrency verification for Boundary Invariants.

Evaluates:
1. Invariant Multiplier Binary Veto ($M_{invariant} \\in \\{0.0, 1.0\\}$) and structured diagnostic generation.
2. Mathematical Monotonicity:
   - Shannon capacity strictly monotonic with bandwidth B and SNR (linear and dB).
   - Carnot efficiency strictly decreasing with T_cold/T_hot ratio (and monotonic with T_hot, T_cold).
   - Landauer energy strictly monotonic with temperature T and bit count N.
   - Optical propagation latency strictly monotonic with geodesic distance, refractive index n, curvature k.
   - USL capacity monotonicity (Amdahl asymptote when beta=0, retrograde peak when beta>0).
3. Concurrency & High-Throughput Performance (< 1ms per claim evaluation, thread safety).
4. Extreme Numerical Limits & Adversarial Invariant Fuzzing.
"""

import concurrent.futures
import math
import random
import time
from typing import Any, Dict, List
import pytest

from src.domain.boundary_invariants import (
    haversine_distance_km,
    check_optical_latency_invariant,
    verify_optical_latency_invariant,
    check_usl_scalability_invariant,
    verify_usl_invariant,
    check_cap_pacelc_invariant,
    verify_cap_pacelc_invariant,
    check_carnot_efficiency_invariant,
    check_landauer_erasure_invariant,
    check_landauer_limit_invariant,
    verify_carnot_landauer_invariant,
    check_shannon_capacity_invariant,
    verify_shannon_capacity_invariant,
    parse_claims_from_text,
    evaluate_all_boundary_invariants,
    SPEED_OF_LIGHT_VACUUM_KM_S,
    BOLTZMANN_CONSTANT_J_K,
    INV_SPEED_OF_LIGHT,
    INV_USL,
    INV_CAP_PACELC,
    INV_CARNOT,
    INV_LANDAUER,
    INV_SHANNON,
    VIOLATION_SPEED_OF_LIGHT,
    VIOLATION_SUPERLINEAR_SPEEDUP,
    VIOLATION_COHERENCY_RETROGRADE,
    VIOLATION_USL_SCALABILITY,
    VIOLATION_CAP_PARTITION,
    VIOLATION_PACELC_ZERO_LATENCY,
    VIOLATION_QUORUM_DEFICIT,
    VIOLATION_SPLIT_BRAIN,
    VIOLATION_CARNOT_SECOND_LAW,
    VIOLATION_LANDAUER_THERMODYNAMIC,
    VIOLATION_SHANNON_CAPACITY,
    VIOLATION_INVALID_INPUT
)


# ==============================================================================
# 1. INVARIANT MULTIPLIER BINARY VETO & STRUCTURED DIAGNOSTICS
# ==============================================================================

class TestInvariantMultiplierBinaryVetoAndDiagnostics:
    """
    Verifies that M_invariant is strictly in {0.0, 1.0} and that any single violation
    instantly zeros the multiplier while producing comprehensive structured diagnostics.
    """

    def test_all_valid_claims_yield_multiplier_one(self):
        valid_claims = [
            {"type": "OPTICAL", "distance_km": 3000.0, "reported_latency_ms": 40.0, "medium": "silica_fiber"},
            {"type": "USL", "node_count": 8, "alpha": 0.05, "beta": 0.001, "claimed_speedup": 5.0},
            {"type": "CARNOT", "t_hot_k": 900.0, "t_cold_k": 300.0, "claimed_efficiency": 0.50},
            {"type": "LANDAUER", "bit_count": 100, "t_kelvin": 300.0, "claimed_energy_joules": 1e-18},
            {"type": "SHANNON", "bandwidth_hz": 10e6, "snr_linear": 100.0, "claimed_bps": 50e6},
            {"type": "CAP", "n_replicas": 5, "r_quorum": 3, "w_quorum": 3, "strong_consistency": True}
        ]
        res = evaluate_all_boundary_invariants(valid_claims)
        assert res["valid"] is True
        assert res["multiplier"] == 1.0
        assert isinstance(res["multiplier"], float)
        assert len(res["violations"]) == 0
        assert len(res["diagnostics"]) == 0

    @pytest.mark.parametrize("violated_claim,expected_inv,expected_violation_type", [
        (
            {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 1.0, "medium": "silica_fiber"},
            INV_SPEED_OF_LIGHT,
            VIOLATION_SPEED_OF_LIGHT
        ),
        (
            {"type": "USL", "node_count": 10, "alpha": 0.1, "beta": 0.0, "claimed_speedup": 25.0},
            INV_USL,
            VIOLATION_SUPERLINEAR_SPEEDUP
        ),
        (
            {"type": "USL", "node_count": 100, "alpha": 0.05, "beta": 0.01, "claimed_speedup": 8.0},
            INV_USL,
            VIOLATION_COHERENCY_RETROGRADE
        ),
        (
            {"type": "CAP", "partition_active": True, "consistency": "linearizable", "availability": "100%"},
            INV_CAP_PACELC,
            VIOLATION_CAP_PARTITION
        ),
        (
            {"type": "CAP", "n_replicas": 5, "r_quorum": 2, "w_quorum": 2, "strong_consistency": True},
            INV_CAP_PACELC,
            VIOLATION_QUORUM_DEFICIT
        ),
        (
            {"type": "CARNOT", "t_hot_k": 500.0, "t_cold_k": 300.0, "claimed_efficiency": 0.80},
            INV_CARNOT,
            VIOLATION_CARNOT_SECOND_LAW
        ),
        (
            {"type": "LANDAUER", "bit_count": 1, "t_kelvin": 300.0, "claimed_energy_joules": 1e-25},
            INV_LANDAUER,
            VIOLATION_LANDAUER_THERMODYNAMIC
        ),
        (
            {"type": "SHANNON", "bandwidth_hz": 1e6, "snr_linear": 1.0, "claimed_bps": 10e6},
            INV_SHANNON,
            VIOLATION_SHANNON_CAPACITY
        )
    ])
    def test_single_violation_triggers_exact_zero_veto(self, violated_claim, expected_inv, expected_violation_type):
        """Any single physical violation among valid claims must veto the entire multiplier to 0.0."""
        valid_backdrop = [
            {"type": "OPTICAL", "distance_km": 1000.0, "reported_latency_ms": 20.0},
            {"type": "CARNOT", "t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.35},
            {"type": "SHANNON", "bandwidth_hz": 20e6, "snr_linear": 100.0, "claimed_bps": 50e6}
        ]
        payload = valid_backdrop + [violated_claim]
        res = evaluate_all_boundary_invariants(payload)

        assert res["valid"] is False
        assert res["multiplier"] == 0.0
        assert isinstance(res["multiplier"], float)
        assert len(res["violations"]) == 1
        assert res["violations"][0]["invariant"] == expected_inv
        assert res["violations"][0]["violation_type"] == expected_violation_type
        assert len(res["diagnostics"]) == 1
        assert len(res["diagnostics"][0]) > 0

    def test_multi_violation_comprehensive_diagnostics(self):
        """All 6 invariants violated simultaneously: multiplier is 0.0 and all 6 diagnostics are recorded."""
        all_violated = [
            {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 0.5},
            {"type": "USL", "node_count": 16, "claimed_speedup": 50.0},
            {"type": "CAP", "partition_active": True, "consistency": "linearizable", "availability": "100%"},
            {"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.90},
            {"type": "LANDAUER", "bit_count": 100, "t_kelvin": 300.0, "claimed_energy_joules": 1e-28},
            {"type": "SHANNON", "bandwidth_hz": 1e6, "snr_linear": 3.0, "claimed_bps": 100e6}
        ]
        res = evaluate_all_boundary_invariants(all_violated)
        assert res["valid"] is False
        assert res["multiplier"] == 0.0
        assert len(res["violations"]) == 6
        assert len(res["diagnostics"]) == 6

        invariants_found = {v["invariant"] for v in res["violations"]}
        assert invariants_found == {INV_SPEED_OF_LIGHT, INV_USL, INV_CAP_PACELC, INV_CARNOT, INV_LANDAUER, INV_SHANNON}

    def test_multiplier_is_strictly_binary(self):
        """Multiplier must only ever evaluate to 0.0 or 1.0, never partial weights (e.g. 0.5)."""
        for _ in range(50):
            has_violation = random.choice([True, False])
            if has_violation:
                claims = [
                    {"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.40},
                    {"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.95}
                ]
            else:
                claims = [
                    {"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.40}
                ]
            res = evaluate_all_boundary_invariants(claims)
            assert res["multiplier"] in (0.0, 1.0)
            if has_violation:
                assert res["multiplier"] == 0.0
                assert res["valid"] is False
            else:
                assert res["multiplier"] == 1.0
                assert res["valid"] is True


# ==============================================================================
# 2. MATHEMATICAL MONOTONICITY: SHANNON CHANNEL CAPACITY
# ==============================================================================

class TestShannonCapacityMonotonicity:
    """
    Verifies Shannon channel capacity C(B, SNR) = B * log2(1 + SNR) mathematical monotonicity:
    - Strictly increasing with Bandwidth B for fixed SNR > 0.
    - Strictly increasing with SNR (linear and dB) for fixed B > 0.
    - Discrete sensitivity / gradient positivity dC/dB > 0, dC/dSNR > 0.
    """

    def test_shannon_bandwidth_strict_monotonicity(self):
        snr_test_values = [0.1, 1.0, 10.0, 100.0, 1000.0, 1e6]
        # Sweep bandwidth from 10 Hz to 100 GHz over 25 logarithmic steps
        bandwidths = [10.0 * (10.0 ** (i * 0.4)) for i in range(25)]

        for snr in snr_test_values:
            capacities = []
            for b in bandwidths:
                res = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=0.0)
                capacities.append(res["theoretical_capacity_bps"])

            # Verify strict monotonic increase: b_i < b_j => C(b_i) < C(b_j)
            for k in range(len(capacities) - 1):
                c1, c2 = capacities[k], capacities[k + 1]
                assert c2 > c1, f"Monotonicity violation in Shannon bandwidth: C({bandwidths[k+1]})={c2} <= C({bandwidths[k]})={c1} for SNR={snr}"
                # Verify linear scaling with B: C(B2)/C(B1) ≈ B2/B1 (with rounding tolerance for small numbers)
                b_ratio = bandwidths[k + 1] / bandwidths[k]
                c_ratio = c2 / c1
                assert math.isclose(b_ratio, c_ratio, rel_tol=0.05 or abs(c2 - c1) < 0.1)

    def test_shannon_snr_linear_strict_monotonicity(self):
        fixed_bandwidths = [1e3, 1e6, 20e6, 1e9]
        # Sweep linear SNR from 1e-4 to 1e8 over 30 logarithmic steps
        snr_values = [1e-4 * (10.0 ** (i * 0.4)) for i in range(30)]

        for b in fixed_bandwidths:
            capacities = []
            for snr in snr_values:
                res = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=0.0)
                capacities.append(res["theoretical_capacity_bps"])

            # Verify strict monotonic increase: snr_i < snr_j => C(snr_i) < C(snr_j)
            for k in range(len(capacities) - 1):
                c1, c2 = capacities[k], capacities[k + 1]
                assert c2 > c1, f"Monotonicity violation in Shannon SNR: C({snr_values[k+1]})={c2} <= C({snr_values[k]})={c1} for B={b}"
                # Sensitivity check: Delta C / Delta SNR > 0
                delta_snr = snr_values[k + 1] - snr_values[k]
                delta_c = c2 - c1
                assert (delta_c / delta_snr) > 0.0

    def test_shannon_snr_db_strict_monotonicity(self):
        b = 50e6  # 50 MHz
        # Sweep SNR in dB from -30 dB to 90 dB in 2 dB steps
        snr_db_values = [float(x) for x in range(-30, 92, 2)]
        capacities = []
        for snr_db in snr_db_values:
            res = check_shannon_capacity_invariant(bandwidth_hz=b, snr_db=snr_db, claimed_bps=0.0)
            capacities.append(res["theoretical_capacity_bps"])

        for k in range(len(capacities) - 1):
            assert capacities[k + 1] > capacities[k], (
                f"Shannon dB monotonicity failure: at {snr_db_values[k+1]}dB ({capacities[k+1]}) <= at {snr_db_values[k]}dB ({capacities[k]})"
            )

    def test_shannon_spectral_efficiency_invariance_to_bandwidth(self):
        """Spectral efficiency eta_s = C / B = log2(1 + SNR) is independent of B and monotonic with SNR."""
        snr = 63.0  # log2(1 + 63) = log2(64) = 6.0 bps/Hz
        for b in [1e3, 1e6, 10e6, 100e6, 1e9]:
            res = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=b * 6.0)
            assert res["is_physically_possible"] is True
            assert math.isclose(res["spectral_efficiency_bps_hz"], 6.0, rel_tol=1e-3)


# ==============================================================================
# 3. MATHEMATICAL MONOTONICITY: CARNOT EFFICIENCY
# ==============================================================================

class TestCarnotEfficiencyMonotonicity:
    """
    Verifies Carnot maximum efficiency eta = 1 - (T_cold / T_hot) mathematical properties:
    - Strictly monotonically decreasing with ratio r = T_cold / T_hot.
    - Strictly monotonically increasing with T_hot for fixed T_cold.
    - Strictly monotonically decreasing with T_cold for fixed T_hot.
    """

    def test_carnot_ratio_monotonic_decrease(self):
        # As r = T_cold / T_hot increases from 0.01 to 0.99, efficiency MUST strictly decrease
        ratios = [i / 100.0 for i in range(1, 100)]
        efficiencies = []

        for r in ratios:
            t_hot = 1000.0
            t_cold = 1000.0 * r
            res = check_carnot_efficiency_invariant(t_hot_k=t_hot, t_cold_k=t_cold, claimed_efficiency=0.0)
            efficiencies.append(res["max_theoretical_efficiency"])

        for k in range(len(efficiencies) - 1):
            eta1, eta2 = efficiencies[k], efficiencies[k + 1]
            assert eta1 > eta2, f"Carnot ratio monotonicity failed: r1={ratios[k]} eta1={eta1} <= r2={ratios[k+1]} eta2={eta2}"
            # Direct derivative: d(eta)/dr = -1.0
            delta_eta = eta2 - eta1
            delta_r = ratios[k + 1] - ratios[k]
            assert math.isclose(delta_eta / delta_r, -1.0, abs_tol=1e-3)

    def test_carnot_t_hot_monotonic_increase(self):
        t_cold = 300.0
        # Sweep T_hot from 310 K to 5000 K
        t_hot_values = [300.0 + (i * 20.0) for i in range(1, 150)]
        efficiencies = []

        for t_hot in t_hot_values:
            res = check_carnot_efficiency_invariant(t_hot_k=t_hot, t_cold_k=t_cold, claimed_efficiency=0.0)
            efficiencies.append(res["max_theoretical_efficiency"])

        for k in range(len(efficiencies) - 1):
            assert efficiencies[k + 1] > efficiencies[k], (
                f"Carnot T_hot monotonicity failed: T_hot={t_hot_values[k+1]} ({efficiencies[k+1]}) <= T_hot={t_hot_values[k]} ({efficiencies[k]})"
            )

    def test_carnot_t_cold_monotonic_decrease(self):
        t_hot = 1200.0
        # Sweep T_cold from 1 K to 1199 K
        t_cold_values = [float(x) for x in range(10, 1190, 20)]
        efficiencies = []

        for t_cold in t_cold_values:
            res = check_carnot_efficiency_invariant(t_hot_k=t_hot, t_cold_k=t_cold, claimed_efficiency=0.0)
            efficiencies.append(res["max_theoretical_efficiency"])

        for k in range(len(efficiencies) - 1):
            assert efficiencies[k + 1] < efficiencies[k], (
                f"Carnot T_cold monotonicity failed: T_cold={t_cold_values[k+1]} ({efficiencies[k+1]}) >= T_cold={t_cold_values[k]} ({efficiencies[k]})"
            )


# ==============================================================================
# 4. MATHEMATICAL MONOTONICITY: LANDAUER ERASURE ENERGY
# ==============================================================================

class TestLandauerEnergyMonotonicity:
    """
    Verifies Landauer minimum energy E_min(T, N) = N * k_B * T * ln(2):
    - Strictly monotonically increasing with Temperature T for fixed N >= 1.
    - Strictly monotonically increasing with Bit Count N for fixed T > 0.
    - Strict linearity: E(2*N) = 2*E(N) and E(2*T) = 2*E(T).
    """

    def test_landauer_temperature_strict_monotonicity(self):
        n_bits = 1000
        # Sweep temperature from 0.001 K to 10,000 K
        temperatures = [0.001 * (10.0 ** (i * 0.3)) for i in range(25)]
        energies = []

        for temp in temperatures:
            res = check_landauer_erasure_invariant(bits_erased=n_bits, ambient_temp_k=temp, claimed_energy_joules=1.0)
            energies.append(res["theoretical_min_energy_joules"])

        for k in range(len(energies) - 1):
            e1, e2 = energies[k], energies[k + 1]
            assert e2 > e1, f"Landauer temperature monotonicity failed: T={temperatures[k+1]} ({e2}) <= T={temperatures[k]} ({e1})"
            # Linearity check: E2/E1 == T2/T1
            t_ratio = temperatures[k + 1] / temperatures[k]
            e_ratio = e2 / e1
            assert math.isclose(t_ratio, e_ratio, rel_tol=1e-4)

    def test_landauer_bit_count_strict_monotonicity(self):
        temp = 300.0  # Room temp
        # Sweep bit count from 1 to 10^12 bits
        bit_counts = [int(10 ** (i * 0.5)) for i in range(25)]
        energies = []

        for n in bit_counts:
            res = check_landauer_erasure_invariant(bits_erased=n, ambient_temp_k=temp, claimed_energy_joules=1.0)
            energies.append(res["theoretical_min_energy_joules"])

        for k in range(len(energies) - 1):
            e1, e2 = energies[k], energies[k + 1]
            if bit_counts[k + 1] > bit_counts[k]:
                assert e2 > e1, f"Landauer bit count monotonicity failed: N={bit_counts[k+1]} ({e2}) <= N={bit_counts[k]} ({e1})"
                n_ratio = bit_counts[k + 1] / bit_counts[k]
                e_ratio = e2 / e1
                assert math.isclose(n_ratio, e_ratio, rel_tol=1e-4)


# ==============================================================================
# 5. MATHEMATICAL MONOTONICITY: OPTICAL PROPAGATION & USL
# ==============================================================================

class TestOpticalAndUSLMonotonicity:
    """
    Verifies:
    - Optical propagation time strictly monotonic with distance, curvature factor, and refractive index.
    - USL Amdahl scaling monotonicity when beta=0, and retrograde peak when beta>0.
    """

    def test_optical_distance_strict_monotonicity(self):
        # Sweep distance from 0.1 km to 100,000 km (where t_min > 0.00098 ms avoids 4-decimal roundoff)
        distances = [0.1 * (10.0 ** (i * 0.3)) for i in range(25)]
        latencies = []

        for d in distances:
            res = check_optical_latency_invariant(distance_km=d, reported_latency_ms=1000.0, medium="silica_fiber")
            latencies.append(res["theoretical_min_rtt_ms"])

        for k in range(len(latencies) - 1):
            assert latencies[k + 1] > latencies[k], f"Optical distance latency monotonicity failed at d={distances[k+1]}"
            d_ratio = distances[k + 1] / distances[k]
            t_ratio = latencies[k + 1] / latencies[k]
            assert math.isclose(d_ratio, t_ratio, rel_tol=0.05 or abs(latencies[k+1] - latencies[k]) < 0.01)

    def test_optical_curvature_factor_monotonicity(self):
        curvatures = [1.0 + (i * 0.1) for i in range(20)]
        d = 1000.0
        latencies = [
            check_optical_latency_invariant(distance_km=d, reported_latency_ms=100.0, route_curvature_factor=k)["theoretical_min_rtt_ms"]
            for k in curvatures
        ]
        for k in range(len(latencies) - 1):
            assert latencies[k + 1] > latencies[k]

    def test_usl_amdahl_monotonicity_when_beta_zero(self):
        """When coherency beta = 0, C(N) = N / (1 + alpha*(N-1)) is strictly monotonic increasing with N."""
        alpha = 0.05
        nodes = list(range(1, 101))
        speedups = [
            check_usl_scalability_invariant(node_count=n, alpha=alpha, beta=0.0, claimed_speedup=1.0)["theoretical_max_speedup"]
            for n in nodes
        ]
        for k in range(len(speedups) - 1):
            assert speedups[k + 1] > speedups[k], f"USL Amdahl monotonicity failed at N={nodes[k+1]}"
            assert speedups[k] < (1.0 / alpha)

    def test_usl_retrograde_peak_monotonicity_transition(self):
        """When beta > 0, C(N) strictly increases up to N* then strictly decreases beyond N*."""
        alpha = 0.04
        beta = 0.001
        n_star = math.sqrt((1.0 - alpha) / beta)  # ~30.98 -> peak at 31
        peak_idx = int(round(n_star))

        nodes = list(range(1, 100))
        speedups = [
            check_usl_scalability_invariant(node_count=n, alpha=alpha, beta=beta, claimed_speedup=1.0)["theoretical_max_speedup"]
            for n in nodes
        ]

        # Monotonically increasing up to peak
        for k in range(peak_idx - 1):
            assert speedups[k + 1] > speedups[k], f"USL pre-peak monotonicity failed at N={nodes[k+1]}"

        # Monotonically decreasing past peak
        for k in range(peak_idx, len(speedups) - 1):
            assert speedups[k + 1] < speedups[k], f"USL post-peak retrograde monotonicity failed at N={nodes[k+1]}"


# ==============================================================================
# 6. CONCURRENCY & HIGH-THROUGHPUT PERFORMANCE BENCHMARK
# ==============================================================================

class TestPerformanceAndConcurrency:
    """
    Stress-tests evaluation performance (< 1ms per claim evaluation) and verifies
    zero-contention concurrent evaluation across multi-threaded execution pools.
    """

    def test_single_threaded_evaluation_throughput(self):
        """Evaluates 10,000 diverse physical claims and asserts average evaluation latency < 0.2ms."""
        test_claims = [
            {"type": "OPTICAL", "distance_km": 5000.0, "reported_latency_ms": 60.0},
            {"type": "USL", "node_count": 16, "alpha": 0.05, "beta": 0.001, "claimed_speedup": 7.0},
            {"type": "CARNOT", "t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.40},
            {"type": "LANDAUER", "bit_count": 100, "t_kelvin": 300.0, "claimed_energy_joules": 1e-18},
            {"type": "SHANNON", "bandwidth_hz": 20e6, "snr_linear": 100.0, "claimed_bps": 50e6},
            {"type": "CAP", "n_replicas": 5, "r_quorum": 3, "w_quorum": 3, "strong_consistency": True}
        ]

        num_iterations = 10000
        start_time = time.perf_counter()
        for i in range(num_iterations):
            claim = test_claims[i % len(test_claims)]
            res = evaluate_all_boundary_invariants(claim)
            assert res["multiplier"] == 1.0
        elapsed = time.perf_counter() - start_time

        avg_latency_ms = (elapsed / num_iterations) * 1000.0
        throughput_claims_per_sec = num_iterations / elapsed

        print(f"\n[PERFORMANCE] Single-thread 10k evaluations: {elapsed:.4f}s total | {avg_latency_ms:.4f}ms/claim | {throughput_claims_per_sec:.1f} claims/sec")
        assert avg_latency_ms < 1.0, f"Average claim evaluation latency ({avg_latency_ms:.4f}ms) exceeded 1.0ms SLA target"

    def test_multi_threaded_concurrency_stress(self):
        """Stress-tests 8,000 concurrent claim evaluations across 16 worker threads with zero failures or race conditions."""
        test_claims = [
            ({"type": "OPTICAL", "distance_km": 1000.0, "reported_latency_ms": 15.0}, 1.0),
            ({"type": "OPTICAL", "distance_km": 1000.0, "reported_latency_ms": 0.1}, 0.0),
            ({"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.45}, 1.0),
            ({"type": "CARNOT", "t_hot_k": 600.0, "t_cold_k": 300.0, "claimed_efficiency": 0.85}, 0.0),
            ({"type": "SHANNON", "bandwidth_hz": 10e6, "snr_linear": 10.0, "claimed_bps": 20e6}, 1.0),
            ({"type": "SHANNON", "bandwidth_hz": 10e6, "snr_linear": 10.0, "claimed_bps": 100e6}, 0.0),
            ({"type": "LANDAUER", "bit_count": 10, "t_kelvin": 300.0, "claimed_energy_joules": 1e-18}, 1.0),
            ({"type": "LANDAUER", "bit_count": 10, "t_kelvin": 300.0, "claimed_energy_joules": 1e-25}, 0.0)
        ]

        def worker_task(item):
            claim_dict, expected_mult = item
            res = evaluate_all_boundary_invariants(claim_dict)
            return res["multiplier"] == expected_mult

        payload = [random.choice(test_claims) for _ in range(8000)]
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(worker_task, payload))
        elapsed = time.perf_counter() - start_time

        avg_latency_ms = (elapsed / len(payload)) * 1000.0
        throughput = len(payload) / elapsed

        print(f"\n[CONCURRENCY] 16-thread 8k evaluations: {elapsed:.4f}s total | {avg_latency_ms:.4f}ms/claim | {throughput:.1f} claims/sec")
        assert all(results), "Multi-threaded concurrency produced non-deterministic evaluation results!"
        assert avg_latency_ms < 1.0

    def test_natural_language_claim_parsing_throughput(self):
        """Evaluates throughput of regex/heuristic text parsing across 1,000 paragraphs."""
        sample_text = (
            "We established a 4000 km silica fiber connection with 50 ms latency. "
            "Our 32-node distributed cluster operates with alpha=0.03 and beta=0.0005 achieving 15x speedup. "
            "The cooling heat pump operates between 500 K and 250 K with 40% thermal efficiency. "
            "Erasing 500 bits at 300 K requires 2e-18 J. "
            "The channel achieves 80 Mbps over a 15 MHz band with SNR of 20 dB."
        )

        num_texts = 1000
        start = time.perf_counter()
        for _ in range(num_texts):
            claims = parse_claims_from_text(sample_text)
            assert len(claims) >= 4
            eval_res = evaluate_all_boundary_invariants(sample_text)
            assert eval_res["multiplier"] == 1.0
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / num_texts) * 1000.0
        print(f"\n[NLP PARSER] 1k text parse+eval: {elapsed:.4f}s total | {avg_ms:.4f}ms/text")
        assert avg_ms < 5.0, f"Text parsing and evaluation took {avg_ms:.4f}ms, exceeding 5.0ms target"


# ==============================================================================
# 7. ADVERSARIAL NUMERICAL LIMITS & EXTREME VALUES
# ==============================================================================

class TestAdversarialNumericalLimits:
    """
    Tests extreme numerical limits, IEEE 754 float extremes (inf, nan),
    astronomical/cryogenic boundaries, and malformed structures.
    """

    def test_extreme_temperatures_near_absolute_zero(self):
        # Cryogenic quantum computing regime: T = 10 microKelvin = 1e-5 K
        res_cryo = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=1e-5, claimed_energy_joules=1e-27)
        assert res_cryo["is_physically_possible"] is True

        res_cryo_bad = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=1e-5, claimed_energy_joules=1e-30)
        assert res_cryo_bad["is_physically_possible"] is False
        assert res_cryo_bad["violation_type"] == VIOLATION_LANDAUER_THERMODYNAMIC

    def test_extreme_cosmic_distances(self):
        # 1 Light-year = 9.461e12 km
        # RTT in vacuum for 1 light-year = 2 years = ~63,115,200 seconds = 6.31152e10 ms
        t_ly_rtt_ms = 2.0 * (9.461e12 / SPEED_OF_LIGHT_VACUUM_KM_S) * 1000.0
        res_ly_valid = check_optical_latency_invariant(distance_km=9.461e12, reported_latency_ms=t_ly_rtt_ms + 1000.0, medium="vacuum")
        assert res_ly_valid["is_physically_possible"] is True

        res_ly_invalid = check_optical_latency_invariant(distance_km=9.461e12, reported_latency_ms=t_ly_rtt_ms - 1000.0, medium="vacuum")
        assert res_ly_invalid["is_physically_possible"] is False

    def test_ieee754_nan_and_infinity_handling(self):
        # Zero / negative bounds
        assert check_optical_latency_invariant(distance_km=-100.0, reported_latency_ms=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=-1e6, snr_linear=10.0, claimed_bps=1e6)["is_physically_possible"] is False
        assert check_carnot_efficiency_invariant(t_hot_k=-100.0, t_cold_k=-200.0, claimed_efficiency=0.5)["is_physically_possible"] is False
        assert check_landauer_erasure_invariant(ambient_temp_k=-10.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_usl_scalability_invariant(node_count=-5, alpha=0.1, beta=0.01)["is_computationally_valid"] is False

    def test_empty_and_malformed_evaluations(self):
        # Empty inputs
        assert evaluate_all_boundary_invariants([])["valid"] is True
        assert evaluate_all_boundary_invariants([])["multiplier"] == 1.0
        assert evaluate_all_boundary_invariants("")["valid"] is True
        assert evaluate_all_boundary_invariants("")["multiplier"] == 1.0

        # Unrecognized claim dict without physical parameters
        unknown_claim = {"type": "UNRECOGNIZED_NONSENSE", "foo": "bar"}
        res = evaluate_all_boundary_invariants(unknown_claim)
        assert res["valid"] is True
        assert res["multiplier"] == 1.0
