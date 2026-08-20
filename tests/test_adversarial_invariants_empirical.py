import unittest
"""
Empirical Challenger Adversarial Test Suite.
Zero-mock, rigorous mathematical and physical boundary challenge harness.
Tests all physical invariants, extreme corner cases, random perturbations, and stress boundaries.
"""

import math
import random
import pytest
from src.domain.grounded_retrieval_engine import (
    check_optical_latency_invariant,
    check_usl_scalability_invariant,
    check_carnot_efficiency_invariant,
    check_landauer_limit_invariant,
    check_cap_pacelc_invariant,
    check_shannon_capacity_invariant,
    evaluate_all_boundary_invariants,
    GroundedRetrievalEngine,
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    detect_temporal_validity,
    compute_temporal_decay,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)


# ==============================================================================
# 1. OPTICAL LATENCY ADVERSARIAL STRESS SUITE
# ==============================================================================
class TestAdversarialOpticalLatency(unittest.TestCase):

    def test_negative_distance_and_latency(self):
        for neg_d in [-1e-9, -1.0, -100.0, -1e6]:
            res = check_optical_latency_invariant(distance_km=neg_d, reported_latency_ms=10.0)
            assert res["is_physically_possible"] is False, f"Allowed negative distance: {neg_d}"

        for neg_l in [-1e-9, -1.0, -50.0]:
            res = check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=neg_l)
            assert res["is_physically_possible"] is False, f"Allowed negative latency: {neg_l}"

    def test_non_positive_refractive_index(self):
        for invalid_n in [0.0, -0.5, -1.47, -10.0]:
            res = check_optical_latency_invariant(distance_km=1000.0, reported_latency_ms=10.0, n_refractive=invalid_n)
            assert res["is_physically_possible"] is False, f"Allowed non-positive refractive index: {invalid_n}"

    def test_sub_vacuum_refractive_index(self):
        # n < 1.0 means faster than speed of light in vacuum (c > c_0).
        # In check_optical_latency_invariant, if n = 1.0, c_fiber = c_0.
        res_vac = check_optical_latency_invariant(distance_km=299792.458, reported_latency_ms=2000.0, n_refractive=1.0)
        assert res_vac["is_physically_possible"] is True

        # Claiming faster than vacuum: 1900 ms for 299,792 km in vacuum
        res_super_c = check_optical_latency_invariant(distance_km=299792.458, reported_latency_ms=1900.0, n_refractive=1.0)
        assert res_super_c["is_physically_possible"] is False

    def test_extreme_astronomical_distances(self):
        # Earth-Moon (384,400 km) in fiber (n=1.47): c_fiber ~ 203,940.45 km/s -> RTT_min = 2 * 384400 / 203940.45 * 1000 = 3769.73 ms
        t_moon_min = 2.0 * (384400.0 / (299792.458 / 1.47)) * 1000.0
        res_moon_under = check_optical_latency_invariant(distance_km=384400.0, reported_latency_ms=t_moon_min - 1.0)
        assert res_moon_under["is_physically_possible"] is False

        res_moon_exact = check_optical_latency_invariant(distance_km=384400.0, reported_latency_ms=t_moon_min + 1.0)
        assert res_moon_exact["is_physically_possible"] is True

        # Earth-Sun (149,597,870.7 km) in vacuum (n=1.0): RTT_min ~ 998,000 ms (~16.63 minutes)
        t_sun_min = 2.0 * (149597870.7 / 299792.458) * 1000.0
        assert check_optical_latency_invariant(distance_km=149597870.7, reported_latency_ms=t_sun_min - 10.0, n_refractive=1.0)["is_physically_possible"] is False
        assert check_optical_latency_invariant(distance_km=149597870.7, reported_latency_ms=t_sun_min + 10.0, n_refractive=1.0)["is_physically_possible"] is True

    def test_nanoscale_distances(self):
        # 1 millimeter = 1e-6 km. RTT_min in fiber (n=1.47) ~ 2 * 1e-6 / 203940.45 * 1000 = 9.8e-9 ms (9.8 ps)
        res_nano = check_optical_latency_invariant(distance_km=1e-6, reported_latency_ms=1e-6)
        assert res_nano["is_physically_possible"] is True


# ==============================================================================
# 2. UNIVERSAL SCALABILITY LAW (USL) ADVERSARIAL STRESS SUITE
# ==============================================================================
class TestAdversarialUSL(unittest.TestCase):

    def test_invalid_node_counts(self):
        for n in [0, -1, -50, -1000]:
            res = check_usl_scalability_invariant(node_count=n, alpha=0.01, beta=0.01, claimed_speedup=1.0)
            assert res["is_computationally_valid"] is False, f"Allowed invalid node count: {n}"

    def test_extreme_coherency_collapse_beta_approaching_one(self):
        # When beta = 0.99, coherency penalty dominates: S(N) collapses dramatically as N increases
        # N=10, alpha=0.01, beta=0.99 -> denom = 1 + 0.01*9 + 0.99*10*9 = 1 + 0.09 + 89.1 = 90.19 -> S_max = 10/90.19 ≈ 0.11x
        res_valid = check_usl_scalability_invariant(node_count=10, alpha=0.01, beta=0.99, claimed_speedup=0.10)
        assert res_valid["is_computationally_valid"] is True

        res_invalid = check_usl_scalability_invariant(node_count=10, alpha=0.01, beta=0.99, claimed_speedup=1.0)
        assert res_invalid["is_computationally_valid"] is False

    def test_retrograde_peak_phenomenon(self):
        # USL peak concurrency: N_opt = sqrt((1-alpha)/beta)
        alpha = 0.05
        beta = 0.005
        n_opt = math.sqrt((1.0 - alpha) / beta)  # sqrt(0.95 / 0.005) = sqrt(190) ≈ 13.78 -> peak near N=14
        # S(14) = 14 / (1 + 0.05*13 + 0.005*14*13) = 14 / (1 + 0.65 + 0.91) = 14 / 2.56 ≈ 5.46x
        s_peak = 14.0 / (1.0 + alpha * 13.0 + beta * 14.0 * 13.0)

        # At N=100: denom = 1 + 0.05*99 + 0.005*100*99 = 1 + 4.95 + 49.5 = 55.45 -> S(100) = 100 / 55.45 ≈ 1.80x
        s_100 = 100.0 / (1.0 + alpha * 99.0 + beta * 100.0 * 99.0)
        assert s_100 < s_peak, "USL did not exhibit retrograde scaling past N_opt"

        # Claiming peak speedup (5.0x) at N=100 must be rejected
        res = check_usl_scalability_invariant(node_count=100, alpha=alpha, beta=beta, claimed_speedup=5.0)
        assert res["is_computationally_valid"] is False

    def test_amdahl_asymptote_beta_zero(self):
        # When beta = 0, USL reduces to Amdahl's law: S(N) -> 1/alpha as N -> inf
        alpha = 0.10
        # At N=1000, S(1000) = 1000 / (1 + 0.10*999) = 1000 / 100.9 ≈ 9.91x (< 10.0x)
        res_valid = check_usl_scalability_invariant(node_count=1000, alpha=alpha, beta=0.0, claimed_speedup=9.8)
        assert res_valid["is_computationally_valid"] is True

        res_invalid = check_usl_scalability_invariant(node_count=1000, alpha=alpha, beta=0.0, claimed_speedup=15.0)
        assert res_invalid["is_computationally_valid"] is False

    def test_superlinear_speedup_attacks(self):
        # S > N is computationally impossible for parallel compute workloads
        for n in [2, 4, 8, 16, 32, 64, 128]:
            res = check_usl_scalability_invariant(node_count=n, alpha=0.0, beta=0.0, claimed_speedup=float(n) * 1.10)
            assert res["is_computationally_valid"] is False, f"Allowed superlinear speedup on {n} nodes"


# ==============================================================================
# 3. CARNOT & LANDAUER THERMODYNAMICS ADVERSARIAL STRESS SUITE
# ==============================================================================
class TestAdversarialThermodynamics(unittest.TestCase):

    def test_carnot_hot_le_cold(self):
        # Equal temperatures -> eta = 0. Any positive work without delta_T violates 2nd Law.
        assert check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=300.0, claimed_efficiency=0.001)["is_physically_possible"] is False
        # T_cold > T_hot -> inverted temperature gradient cannot generate positive work spontaneously
        assert check_carnot_efficiency_invariant(t_hot_k=200.0, t_cold_k=400.0, claimed_efficiency=0.10)["is_physically_possible"] is False

    def test_carnot_absolute_zero_and_negative_temperatures(self):
        assert check_carnot_efficiency_invariant(t_hot_k=0.0, t_cold_k=0.0, claimed_efficiency=0.5)["is_physically_possible"] is False
        assert check_carnot_efficiency_invariant(t_hot_k=-50.0, t_cold_k=-100.0, claimed_efficiency=0.5)["is_physically_possible"] is False

    def test_carnot_over_unity_claims(self):
        # Th=1000K, Tc=100K -> eta_max = 0.90. Claiming 0.95 or 1.05 must fail.
        assert check_carnot_efficiency_invariant(t_hot_k=1000.0, t_cold_k=100.0, claimed_efficiency=0.95)["is_physically_possible"] is False
        assert check_carnot_efficiency_invariant(t_hot_k=1000.0, t_cold_k=100.0, claimed_efficiency=1.05)["is_physically_possible"] is False

    def test_landauer_cryogenic_limits(self):
        # Cryogenic milliKelvin range: T = 15 mK (0.015 K)
        # E_min = 1 * 1.380649e-23 * 0.015 * ln(2) ≈ 1.435e-25 J
        k_b = 1.380649e-23
        e_min_15mk = k_b * 0.015 * math.log(2)

        res_valid = check_landauer_limit_invariant(t_kelvin=0.015, claimed_energy_joules=e_min_15mk * 1.05, bit_count=1)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_landauer_limit_invariant(t_kelvin=0.015, claimed_energy_joules=e_min_15mk * 0.50, bit_count=1)
        assert res_invalid["is_physically_possible"] is False

    def test_landauer_zero_and_negative_temperature(self):
        assert check_landauer_limit_invariant(t_kelvin=0.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_landauer_limit_invariant(t_kelvin=-10.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=1e-20, bit_count=0)["is_physically_possible"] is False
        assert check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=1e-20, bit_count=-5)["is_physically_possible"] is False

    def test_landauer_massive_bit_scale(self):
        # 1 Terabit = 10^12 bits at room temp 300K: E_min ≈ 10^12 * 2.87e-21 J ≈ 2.87e-9 J (2.87 nanojoules)
        k_b = 1.380649e-23
        e_min_terabit = 10**12 * k_b * 300.0 * math.log(2)

        res_valid = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=e_min_terabit * 1.01, bit_count=10**12)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_landauer_limit_invariant(t_kelvin=300.0, claimed_energy_joules=e_min_terabit * 0.90, bit_count=10**12)
        assert res_invalid["is_physically_possible"] is False


# ==============================================================================
# 4. SHANNON CAPACITY ADVERSARIAL STRESS SUITE
# ==============================================================================
class TestAdversarialShannonCapacity(unittest.TestCase):

    def test_zero_and_negative_bandwidth_and_snr(self):
        assert check_shannon_capacity_invariant(bandwidth_hz=0.0, snr_linear=100.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=-1e6, snr_linear=100.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=1e6, snr_linear=-1.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=1e6, snr_linear=100.0, claimed_bps=-10.0)["is_physically_possible"] is False

    def test_low_snr_regime_asymptote(self):
        # When SNR << 1, C = B * log2(1 + SNR) ≈ B * SNR / ln(2)
        b = 10e3  # 10 kHz
        snr = 1e-4
        c_exact = b * math.log2(1.0 + snr)
        c_approx = b * snr / math.log(2)
        assert math.isclose(c_exact, c_approx, rel_tol=1e-3)

        res_valid = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=c_exact * 0.95)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=c_exact * 1.50)
        assert res_invalid["is_physically_possible"] is False

    def test_high_snr_regime_scaling(self):
        # SNR = 10^12 (120 dB), B = 1 GHz -> C = 10^9 * log2(10^12 + 1) ≈ 10^9 * 39.86 ≈ 39.86 Gbps
        b = 1e9
        snr = 1e12
        c_theory = b * math.log2(1.0 + snr)

        res_valid = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=39e9)
        assert res_valid["is_physically_possible"] is True

        res_invalid = check_shannon_capacity_invariant(bandwidth_hz=b, snr_linear=snr, claimed_bps=50e9)
        assert res_invalid["is_physically_possible"] is False


# ==============================================================================
# 5. CAP / PACELC & QUORUM ADVERSARIAL STRESS SUITE
# ==============================================================================
class TestAdversarialDistributedQuorum(unittest.TestCase):

    def test_quorum_matrix_exhaustive_boundary(self):
        # Test odd node counts 3, 5, 7, 9, 11
        for n in [3, 5, 7, 9, 11]:
            for r in range(1, n + 1):
                for w in range(1, n + 1):
                    claim = {"r_quorum": r, "w_quorum": w, "n_replicas": n, "strong_consistency": True}
                    res = check_cap_pacelc_invariant(claim)
                    # Quorum condition: R + W > N AND W > N / 2
                    is_expected_valid = (r + w > n) and (w > n / 2.0)
                    assert res["is_computationally_valid"] == is_expected_valid, (
                        f"Quorum failure at N={n}, R={r}, W={w}. Expected {is_expected_valid}, got {res['is_computationally_valid']}"
                    )

    def test_pacelc_instantaneous_distributed_replication(self):
        for zero_lat in [0.0, -1.0, 0]:
            claim = {"multi_region": True, "consistency": "linearizable", "replication_latency_ms": zero_lat}
            res = check_cap_pacelc_invariant(claim)
            assert res["is_computationally_valid"] is False
            assert res["tradeoff_model"] == "PACELC_ZERO_LATENCY_VIOLATION"


# ==============================================================================
# 6. ENGINE COMPOSITE CONFIDENCE & REFUSAL GATE STRESS SUITE
# ==============================================================================
class TestAdversarialEngineIntegration(unittest.TestCase):

    def test_invariant_veto_multi_violation_diagnostics(self):
        engine = GroundedRetrievalEngine()
        passages = [
            {"filename": "rfc9110.pdf", "content": "HTTP 200 OK response indicates success.", "rank": 1}
        ]
        # Multi-invariant violations in combined claim payload
        claims = [
            {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 1.0},
            {"type": "CARNOT", "t_hot_k": 300.0, "t_cold_k": 300.0, "claimed_efficiency": 0.80},
            {"type": "USL", "node_count": 50, "alpha": 0.1, "beta": 0.05, "claimed_speedup": 100.0}
        ]
        res = engine.evaluate_grounding("HTTP distributed scaling", passages, generated_claim=claims)
        assert res["status"] == "refusal"
        assert res["overall_grounded_confidence"] == 0.0
        assert len(res["diagnostics"]["invariant_violations"]) == 3
