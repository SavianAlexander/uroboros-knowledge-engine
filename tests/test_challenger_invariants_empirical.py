"""
Adversarial Empirical Challenge Harness for Milestone M4:
Physical, Mathematical & Computational Boundary Invariant Guards (Features F7, F8, F9, F10, F11).

Authored by: challenger_1_m4_gen2 (Empirical Challenger)
Focus:
- Monte Carlo parameter sweeps & exact boundary testing
- Sub-millisecond geodesic & propagation anomalies
- Asymptotic USL scaling (N = 10^6, zero contention/coherency, retrograde curves)
- CAP/PACELC Lipton-Sandberg & Quorum overlap (R+W <= N, W <= N/2)
- Near-absolute zero thermodynamics (T -> 0+), sub-zeptojoule Landauer (< 10^-21 J)
- Shannon-Hartley negative dB SNR & high/low asymptotic bounds
- Adversarial & deceptive natural language parsing across complex unit dimensions
"""

import math
import random
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
    EARTH_RADIUS_KM,
    DEFAULT_SILICA_FIBER_REFRACTIVE_INDEX,
    REFRACTIVE_INDICES,
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
    VIOLATION_INVALID_INPUT,
)


# ==============================================================================
# 1. EMPIRICAL CHALLENGE: SPEED OF LIGHT & GEODESIC INVARIANTS (F7)
# ==============================================================================

class TestEmpiricalOpticalLatencyChallenge:
    """Stress-tests optical fiber, vacuum latency, and geodesic mathematics."""

    def test_antipodal_geodesic_distance_precision(self):
        """Verify spherical antipodal coordinate pairs reach exact theoretical semi-circumference."""
        expected_semi_circ = math.pi * EARTH_RADIUS_KM  # ~20,015.087 km

        # Equatorial antipodes (0, 0) and (0, 180)
        d_eq = haversine_distance_km(0.0, 0.0, 0.0, 180.0)
        assert abs(d_eq - expected_semi_circ) < 1e-4

        # Polar antipodes (90, 0) and (-90, 0)
        d_polar = haversine_distance_km(90.0, 0.0, -90.0, 0.0)
        assert abs(d_polar - expected_semi_circ) < 1e-4

        # Arbitrary antipodal pair: (37.7749, -122.4194) and (-37.7749, 57.5806)
        d_arb = haversine_distance_km(37.7749, -122.4194, -37.7749, 57.5806)
        assert abs(d_arb - expected_semi_circ) < 1e-4

    def test_sub_millisecond_superluminal_boundary_sweep(self):
        """Sweep distances from 100 km to 20,000 km, testing exact microsecond bounds."""
        distances = [100.0, 500.0, 1000.0, 5000.0, 10000.0, 20000.0]
        n_fiber = 1.47
        c_medium = SPEED_OF_LIGHT_VACUUM_KM_S / n_fiber

        for dist in distances:
            t_min_rtt = (2.0 * dist / c_medium) * 1000.0  # in ms

            # 1. Exact minimum bound -> physically possible
            res_exact = check_optical_latency_invariant(
                distance_km=dist,
                reported_latency_ms=t_min_rtt,
                medium="silica_fiber"
            )
            assert res_exact["is_physically_possible"] is True
            assert res_exact["violation_type"] is None

            # 2. 0.001 ms (1 microsecond) below minimum bound -> superluminal violation
            res_superluminal = check_optical_latency_invariant(
                distance_km=dist,
                reported_latency_ms=t_min_rtt - 0.002,
                medium="silica_fiber"
            )
            assert res_superluminal["is_physically_possible"] is False
            assert res_superluminal["violation_type"] == VIOLATION_SPEED_OF_LIGHT

            # 3. 0.001 ms above minimum bound -> physically possible
            res_above = check_optical_latency_invariant(
                distance_km=dist,
                reported_latency_ms=t_min_rtt + 0.002,
                medium="silica_fiber"
            )
            assert res_above["is_physically_possible"] is True

    def test_refractive_index_medium_variations(self):
        """Test custom and standard refractive indices across multiple physical media."""
        dist = 1000.0  # km

        # Vacuum (n = 1.0): t_rtt_min = 2 * 1000 / 299792.458 * 1000 = 6.671 ms
        res_vac = check_optical_latency_invariant(dist, 6.70, medium="vacuum")
        assert res_vac["is_physically_possible"] is True

        # Silica Fiber (n = 1.47): t_rtt_min = 9.807 ms. 8.0 ms must FAIL
        res_fib_fail = check_optical_latency_invariant(dist, 8.0, medium="silica_fiber")
        assert res_fib_fail["is_physically_possible"] is False

        # Hollow Core Fiber (custom n = 1.20): t_rtt_min = 2 * 1000 / (c/1.2) * 1000 = 8.005 ms
        # 8.1 ms is valid for n=1.20, but invalid for standard silica (n=1.47)
        res_hollow = check_optical_latency_invariant(dist, 8.1, n_refractive=1.20)
        assert res_hollow["is_physically_possible"] is True

        # Superluminal refractive index (n < 1.0) must be rejected
        res_sub_vac = check_optical_latency_invariant(dist, 5.0, n_refractive=0.95)
        assert res_sub_vac["is_physically_possible"] is False
        assert res_sub_vac["violation_type"] == VIOLATION_SPEED_OF_LIGHT

    def test_astronomical_and_microscopic_scale_sweeps(self):
        """Verify scale invariance from microscopic on-chip interconnect to interplanetary scales."""
        # 1. On-chip interconnect: 1 mm (1e-6 km), 0.00001 ms (10 ns) -> valid
        res_chip = check_optical_latency_invariant(distance_km=1e-6, reported_latency_ms=1e-5, medium="copper")
        assert res_chip["is_physically_possible"] is True

        # 2. Interplanetary: Earth to Mars (2.25e8 km in vacuum)
        # RTT_min = 2 * 2.25e8 / 299792.458 * 1000 ≈ 1,501,038 ms (~1501 seconds)
        # Claiming 1000 seconds (1,000,000 ms) -> impossible
        res_mars_bad = check_optical_latency_invariant(distance_km=2.25e8, reported_latency_ms=1.0e6, medium="vacuum")
        assert res_mars_bad["is_physically_possible"] is False

        # Claiming 2000 seconds (2,000,000 ms) -> valid
        res_mars_good = check_optical_latency_invariant(distance_km=2.25e8, reported_latency_ms=2.0e6, medium="vacuum")
        assert res_mars_good["is_physically_possible"] is True


# ==============================================================================
# 2. EMPIRICAL CHALLENGE: UNIVERSAL SCALABILITY LAW (USL) & CONCURRENCY (F8)
# ==============================================================================

class TestEmpiricalUslChallenge:
    """Stress-tests USL, Amdahl's Law, and Gunther's coherency retrograde curves."""

    def test_extreme_node_count_sweeps(self):
        """Test large-scale distributed architectures up to N = 1,000,000 nodes."""
        # N = 10^6, ideal linear scaling (alpha = 0, beta = 0)
        res_linear = check_usl_scalability_invariant(node_count=1_000_000, alpha=0.0, beta=0.0, claimed_speedup=999_999.0)
        assert res_linear["is_computationally_valid"] is True
        assert res_linear["theoretical_max_speedup"] == 1_000_000.0

        # Superlinear claim on N = 10^6 (claiming 1,100,000x speedup) -> superlinear violation
        res_super = check_usl_scalability_invariant(node_count=1_000_000, alpha=0.0, beta=0.0, claimed_speedup=1_100_000.0)
        assert res_super["is_computationally_valid"] is False
        assert res_super["violation_type"] == VIOLATION_SUPERLINEAR_SPEEDUP

        # N = 10^6, contention alpha = 0.001 (0.1% serialized). Amdahl limit = 1/alpha = 1000x
        # Claiming 2000x -> USL violation
        res_amdahl = check_usl_scalability_invariant(node_count=1_000_000, alpha=0.001, beta=0.0, claimed_speedup=2000.0)
        assert res_amdahl["is_computationally_valid"] is False
        assert res_amdahl["theoretical_max_speedup"] < 1000.0

    def test_retrograde_coherency_peak_and_collapse_curve(self):
        """Empirically test Gunther's USL retrograde collapse past optimal concurrency N*."""
        alpha = 0.05
        beta = 0.0005
        # N* = sqrt((1 - 0.05) / 0.0005) = sqrt(0.95 / 0.0005) = sqrt(1900) ≈ 43.59
        n_star = math.sqrt((1.0 - alpha) / beta)
        assert 43.0 < n_star < 44.0

        # Calculate theoretical capacity at peak N=44:
        # C(44) = 44 / (1 + 0.05*43 + 0.0005*44*43) = 44 / (1 + 2.15 + 0.946) = 44 / 4.096 ≈ 10.74x
        res_peak = check_usl_scalability_invariant(node_count=44, alpha=alpha, beta=beta, claimed_speedup=10.5)
        assert res_peak["is_computationally_valid"] is True

        # Now test deep in retrograde regime: N = 500
        # C(500) = 500 / (1 + 0.05*499 + 0.0005*500*499) = 500 / (1 + 24.95 + 124.75) = 500 / 150.7 ≈ 3.32x
        # Claiming 8.0x speedup at N=500 must fail with COHERENCY_RETROGRADE_VIOLATION
        res_retro = check_usl_scalability_invariant(node_count=500, alpha=alpha, beta=beta, claimed_speedup=8.0)
        assert res_retro["is_computationally_valid"] is False
        assert res_retro["violation_type"] == VIOLATION_COHERENCY_RETROGRADE

        # Claiming 3.0x speedup at N=500 -> compliant with degraded capacity
        res_retro_ok = check_usl_scalability_invariant(node_count=500, alpha=alpha, beta=beta, claimed_speedup=3.0)
        assert res_retro_ok["is_computationally_valid"] is True

    def test_monte_carlo_usl_monotonicity_under_zero_beta(self):
        """When beta = 0, C(N) is strictly monotonic increasing up to 1/alpha."""
        random.seed(42)
        for _ in range(50):
            alpha = random.uniform(0.001, 0.20)
            n1 = random.randint(2, 50)
            n2 = n1 + random.randint(10, 100)

            c1 = n1 / (1.0 + alpha * (n1 - 1.0))
            c2 = n2 / (1.0 + alpha * (n2 - 1.0))

            assert c2 > c1
            assert c2 < (1.0 / alpha)

            # Test invariant check with valid scaling
            res = check_usl_scalability_invariant(node_count=n1, alpha=alpha, beta=0.0, claimed_speedup=c1 * 0.98)
            assert res["is_computationally_valid"] is True


# ==============================================================================
# 3. EMPIRICAL CHALLENGE: CAP, PACELC & DISTRIBUTED QUORUM INVARIANTS (F9)
# ==============================================================================

class TestEmpiricalCapPacelcChallenge:
    """Stress-tests CAP partition exclusivity, PACELC Lipton-Sandberg, and Quorum boundaries."""

    def test_monte_carlo_quorum_overlap_boundary_sweep(self):
        """
        Monte Carlo sweep over quorum configurations (R, W, N) verifying:
        - R + W <= N -> QUORUM_DEFICIT
        - W <= N/2 -> SPLIT_BRAIN_RISK
        - R + W > N and W > N/2 -> VALID
        """
        random.seed(1337)
        for _ in range(100):
            n = random.randint(3, 50)
            r = random.randint(1, n)
            w = random.randint(1, n)

            claim = {
                "n_replicas": n,
                "r_quorum": r,
                "w_quorum": w,
                "strong_consistency": True
            }
            res = check_cap_pacelc_invariant(claim)

            if (r + w) <= n:
                assert res["is_computationally_valid"] is False
                assert res["violation_type"] == VIOLATION_QUORUM_DEFICIT
            elif w <= (n / 2.0):
                assert res["is_computationally_valid"] is False
                assert res["violation_type"] == VIOLATION_SPLIT_BRAIN
            else:
                assert res["is_computationally_valid"] is True
                assert res["violation_type"] is None

    def test_lipton_sandberg_pacelc_boundary_conditions(self):
        """
        Lipton-Sandberg inequality states write/read operations across distance D
        satisfy latency r + w >= D / c.
        Multi-region distributed clusters claiming 0ms latency with linearizability are impossible.
        """
        # Multi-region linearizable claiming 0 ms -> PACELC violation
        claim_zero = {
            "multi_region": True,
            "consistency": "linearizable",
            "replication_latency_ms": 0.0
        }
        res_zero = check_cap_pacelc_invariant(claim_zero)
        assert res_zero["is_computationally_valid"] is False
        assert res_zero["violation_type"] == VIOLATION_PACELC_ZERO_LATENCY

        # Multi-region linearizable claiming 20 ms -> valid
        claim_ok = {
            "multi_region": True,
            "consistency": "linearizable",
            "replication_latency_ms": 20.0
        }
        res_ok = check_cap_pacelc_invariant(claim_ok)
        assert res_ok["is_computationally_valid"] is True

        # Single region (local memory) claiming 0 ms -> valid (not multi_region)
        claim_local = {
            "multi_region": False,
            "consistency": "linearizable",
            "replication_latency_ms": 0.0
        }
        res_local = check_cap_pacelc_invariant(claim_local)
        assert res_local["is_computationally_valid"] is True


# ==============================================================================
# 4. EMPIRICAL CHALLENGE: THERMODYNAMICS & LANDAUER PRINCIPLE (F10)
# ==============================================================================

class TestEmpiricalThermodynamicsChallenge:
    """Stress-tests Carnot 2nd law efficiency and Landauer information erasure energy limits."""

    def test_near_absolute_zero_carnot_asymptote(self):
        """As T_cold -> 0+ K, Carnot efficiency approaches 100% (eta_max -> 1.0)."""
        t_hot = 300.0  # Room temp

        # At T_cold = 1e-6 K (microKelvin): eta_max = 1 - (1e-6 / 300) = 0.9999999967
        res_micro = check_carnot_efficiency_invariant(t_hot_k=t_hot, t_cold_k=1e-6, claimed_efficiency=0.9999)
        assert res_micro["is_physically_possible"] is True

        # Claiming 1.0001 (over-unity) at near-absolute zero must still FAIL
        res_over = check_carnot_efficiency_invariant(t_hot_k=t_hot, t_cold_k=1e-6, claimed_efficiency=1.0001)
        assert res_over["is_physically_possible"] is False
        assert res_over["violation_type"] == VIOLATION_CARNOT_SECOND_LAW

    def test_sub_zeptojoule_landauer_erasure_violations(self):
        """
        Landauer limit at T = 300 K: E_min = 1.380649e-23 * 300 * ln(2) = 2.87058e-21 J (~2.87 zeptojoules).
        Erasing 1 bit below 2.87 zJ is physically impossible under classical statistical mechanics.
        """
        t_room = 300.0
        e_min_1bit = BOLTZMANN_CONSTANT_J_K * t_room * math.log(2.0)

        # 1. Claiming exactly 2.88 zJ (2.88e-21 J) -> valid
        res_exact_ok = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=t_room, claimed_energy_joules=2.88e-21)
        assert res_exact_ok["is_physically_possible"] is True

        # 2. Claiming 2.00 zJ (2.00e-21 J) -> Landauer violation
        res_zJ_fail = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=t_room, claimed_energy_joules=2.00e-21)
        assert res_zJ_fail["is_physically_possible"] is False
        assert res_zJ_fail["violation_type"] == VIOLATION_LANDAUER_THERMODYNAMIC

        # 3. Claiming 1 yoctojoule (1e-24 J) -> severe Landauer violation
        res_yocto_fail = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=t_room, claimed_energy_joules=1e-24)
        assert res_yocto_fail["is_physically_possible"] is False

        # 4. Multi-bit batch erasure: 10^9 bits (1 Gigabit) at 300 K
        # E_min = 10^9 * 2.87058e-21 = 2.87058e-12 J (2.87 picojoules)
        # Claiming 1.0 pJ (1e-12 J) -> fails
        res_gigabit_fail = check_landauer_erasure_invariant(bits_erased=10**9, ambient_temp_k=t_room, claimed_energy_joules=1e-12)
        assert res_gigabit_fail["is_physically_possible"] is False

        # Claiming 5.0 pJ (5e-12 J) -> passes
        res_gigabit_ok = check_landauer_erasure_invariant(bits_erased=10**9, ambient_temp_k=t_room, claimed_energy_joules=5e-12)
        assert res_gigabit_ok["is_physically_possible"] is True


# ==============================================================================
# 5. EMPIRICAL CHALLENGE: SHANNON-HARTLEY CHANNEL CAPACITY (F11)
# ==============================================================================

class TestEmpiricalShannonCapacityChallenge:
    """Stress-tests Shannon-Hartley capacity ceiling across extreme SNR and bandwidths."""

    def test_negative_db_snr_low_capacity_regime(self):
        """
        Negative SNR in dB corresponds to 0 < SNR_linear < 1.
        e.g., -10 dB -> SNR_linear = 0.1
        C = B * log2(1 + 0.1) = B * 0.1375 bps
        """
        bw = 1e6  # 1 MHz
        snr_db = -10.0  # 0.1 linear
        expected_c = bw * math.log2(1.1)  # ~137,503.5 bps

        # Claiming 100 kbps (100,000 bps) -> valid (< 137.5 kbps)
        res_ok = check_shannon_capacity_invariant(bandwidth_hz=bw, snr_db=snr_db, claimed_bps=100e3)
        assert res_ok["is_physically_possible"] is True
        assert abs(res_ok["theoretical_capacity_bps"] - expected_c) < 1.0

        # Claiming 200 kbps (200,000 bps) -> Shannon violation
        res_bad = check_shannon_capacity_invariant(bandwidth_hz=bw, snr_db=snr_db, claimed_bps=200e3)
        assert res_bad["is_physically_possible"] is False
        assert res_bad["violation_type"] == VIOLATION_SHANNON_CAPACITY

    def test_high_snr_asymptotic_scaling(self):
        """At high SNR, C ≈ B * (SNR_dB / 3.0103)."""
        bw = 10e6  # 10 MHz
        snr_db = 60.0  # SNR_linear = 10^6 -> log2(10^6) ≈ 19.93 bits/s/Hz
        # Capacity ≈ 10e6 * 19.93156 = 199.315 Mbps
        res_high_ok = check_shannon_capacity_invariant(bandwidth_hz=bw, snr_db=snr_db, claimed_bps=190e6)
        assert res_high_ok["is_physically_possible"] is True

        res_high_bad = check_shannon_capacity_invariant(bandwidth_hz=bw, snr_db=snr_db, claimed_bps=250e6)
        assert res_high_bad["is_physically_possible"] is False
        assert res_high_bad["violation_type"] == VIOLATION_SHANNON_CAPACITY


# ==============================================================================
# 6. EMPIRICAL CHALLENGE: NATURAL LANGUAGE CLAIM PARSER & DECEPTIVE PROMPTS
# ==============================================================================

class TestEmpiricalParserAndDeceptiveTextChallenge:
    """Stress-tests regex heuristics against deceptive text, complex units, and multi-claim payloads."""

    def test_complex_unit_conversions_optical_latency(self):
        """Parse miles to km, microsecond/nanosecond/second to millisecond."""
        # 1. Miles to km: 100 miles = 160.934 km. In fiber, RTT min = 2 * 160.934 / 203940.45 * 1000 = 1.578 ms
        txt_miles = "Our network spans 100 miles with latency 5 ms."
        parsed = parse_claims_from_text(txt_miles)
        assert len(parsed) >= 1
        assert parsed[0]["type"] == "OPTICAL"
        assert abs(parsed[0]["distance_km"] - 160.934) < 0.1
        assert parsed[0]["reported_latency_ms"] == 5.0

        # 2. Nanoseconds conversion: 100 km with 500000 ns (0.5 ms). In fiber RTT min = 0.98 ms -> must FAIL
        txt_ns = "The link covers 100 km with 500000 ns latency."
        res_ns = evaluate_all_boundary_invariants(txt_ns)
        assert res_ns["valid"] is False
        assert any(v["violation_type"] == VIOLATION_SPEED_OF_LIGHT for v in res_ns["violations"])

    def test_energy_unit_variations_landauer_parsing(self):
        """Parse nanojoules, picojoules, femtojoules, attojoules, zeptojoules, yoctojoules."""
        units_and_values = [
            ("100 nj", 100e-9),
            ("50 pj", 50e-12),
            ("10 fj", 10e-15),
            ("5 aj", 5e-18),
            ("2 zj", 2e-21),
            ("1 yj", 1e-24),
        ]
        for unit_str, expected_joules in units_and_values:
            txt = f"Erasing 1 bits at 300 K dissipates {unit_str}."
            parsed = parse_claims_from_text(txt)
            assert len(parsed) >= 1
            claim = parsed[0]
            assert claim["type"] == "LANDAUER"
            assert math.isclose(claim["claimed_energy_joules"], expected_joules, rel_tol=1e-5)

    def test_data_rate_and_bandwidth_unit_variations(self):
        """Parse kbps, mbps, gbps, tbps and kHz, MHz, GHz."""
        txt = "The satellite channel has bandwidth 500 MHz and SNR of 20 dB delivering 10 Gbps."
        parsed = parse_claims_from_text(txt)
        assert len(parsed) >= 1
        claim = parsed[0]
        assert claim["type"] == "SHANNON"
        assert claim["bandwidth_hz"] == 500e6
        assert claim["claimed_bps"] == 10e9
        # C = 500e6 * log2(101) ≈ 3.329 Gbps. Claiming 10 Gbps is a violation
        res = evaluate_all_boundary_invariants(txt)
        assert res["valid"] is False
        assert res["multiplier"] == 0.0

    def test_deceptive_mixed_claims_payload(self):
        """Test a deceptive text where 4 claims are valid and 1 is a subtle physical violation."""
        text_mixed = (
            "1. Optical link: 500 km fiber with 10 ms RTT. "
            "2. Cluster: 16 nodes achieving 8x speedup with alpha=0.05. "
            "3. Engine: Th=500K and Tc=300K achieving 35% efficiency. "
            "4. Bit erasure: 100 bits at 300 K using 1e-15 J. "
            "5. Channel: 10 MHz bandwidth with SNR 10 dB achieving 500 Mbps throughput."  # Impossible!
        )
        res = evaluate_all_boundary_invariants(text_mixed)
        assert res["valid"] is False
        assert res["multiplier"] == 0.0
        assert len(res["violations"]) >= 1
        assert any(v["invariant"] == INV_SHANNON for v in res["violations"])


# ==============================================================================
# 7. EMPIRICAL CHALLENGE: ADVERSARIAL EDGE CASES & NUMERICAL STABILITY
# ==============================================================================

class TestEmpiricalBoundaryEdgeCases:
    """Stress-tests corner cases, zero-quantities, numerical singularity, and contract resilience."""

    def test_optical_zero_distance_and_sub_unity_curvature(self):
        # Zero distance, zero latency -> valid (local loopback)
        res_zero = check_optical_latency_invariant(distance_km=0.0, reported_latency_ms=0.0)
        assert res_zero["is_physically_possible"] is True

        # Curvature factor k < 1.0 is physically impossible (shortcuts Euclidean/geodesic space)
        res_sub_curv = check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=5.0, route_curvature_factor=0.99)
        assert res_sub_curv["is_physically_possible"] is False
        assert res_sub_curv["violation_type"] == VIOLATION_INVALID_INPUT

    def test_usl_alpha_one_pure_serialization(self):
        # When alpha = 1.0, all work is serialized -> C(N) = N / (1 + 1*(N-1)) = N / N = 1.0
        for nodes in [2, 10, 100, 1000]:
            res = check_usl_scalability_invariant(node_count=nodes, alpha=1.0, beta=0.0, claimed_speedup=1.0)
            assert res["is_computationally_valid"] is True
            assert res["theoretical_max_speedup"] == 1.0

            res_fail = check_usl_scalability_invariant(node_count=nodes, alpha=1.0, beta=0.0, claimed_speedup=1.5)
            assert res_fail["is_computationally_valid"] is False

    def test_single_node_quorum_and_degenerate_clusters(self):
        # Single node N=1, R=1, W=1 -> single node trivial consistency
        claim_single = {"n_replicas": 1, "r_quorum": 1, "w_quorum": 1, "strong_consistency": True}
        res_single = check_cap_pacelc_invariant(claim_single)
        assert res_single["is_computationally_valid"] is True

        # Degenerate 2-node cluster with R=1, W=1 (R+W=2 <= 2) -> Quorum deficit
        claim_two_bad = {"n_replicas": 2, "r_quorum": 1, "w_quorum": 1, "strong_consistency": True}
        res_two = check_cap_pacelc_invariant(claim_two_bad)
        assert res_two["is_computationally_valid"] is False
        assert res_two["violation_type"] == VIOLATION_QUORUM_DEFICIT

    def test_carnot_equal_temperatures_and_negative_kelvin(self):
        # T_hot == T_cold (isothermal reservoir, no work extraction possible)
        res_iso = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=300.0, claimed_efficiency=0.01)
        assert res_iso["is_physically_possible"] is False
        assert res_iso["violation_type"] == VIOLATION_INVALID_INPUT

        # Negative temperature (unphysical in thermodynamic engine context)
        res_neg = check_carnot_efficiency_invariant(t_hot_k=-100.0, t_cold_k=-200.0, claimed_efficiency=0.5)
        assert res_neg["is_physically_possible"] is False
        assert res_neg["violation_type"] == VIOLATION_INVALID_INPUT

    def test_evaluator_empty_corrupted_and_nested_payloads(self):
        # Empty inputs
        assert evaluate_all_boundary_invariants("")["valid"] is True
        assert evaluate_all_boundary_invariants([])["valid"] is True
        assert evaluate_all_boundary_invariants({})["valid"] is True

        # Nested valid list with string claims
        mixed = [
            {"type": "OPTICAL", "distance_km": 1000.0, "reported_latency_ms": 20.0},
            "Our cluster of 8 nodes achieves 6x speedup with alpha=0.02.",
            {"type": "CARNOT", "t_hot_k": 500.0, "t_cold_k": 250.0, "claimed_efficiency": 0.40}
        ]
        res = evaluate_all_boundary_invariants(mixed)
        assert res["valid"] is True
        assert res["multiplier"] == 1.0
        assert len(res["violations"]) == 0

