"""
Comprehensive Unit & Integration Test Suite for Boundary Invariants (Milestone M4).
Covers:
- F7: Speed-of-Light Optical Fiber & Vacuum Latency Invariant Guard
- F8: Universal Scalability Law (USL) Guard
- F9: CAP & PACELC Latency-Consistency Bounds
- F10: Carnot Thermodynamic Efficiency & Landauer Erasure Energy Limits
- F11: Shannon Channel Capacity Ceiling
- Unified Evaluator & Natural Language Claim Parser

Includes positive (valid claims), boundary (exact thresholds), negative (violations),
and adversarial edge cases across all domain functions and contract interfaces.
"""

import math
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
    VIOLATION_INVALID_INPUT
)


# ==============================================================================
# 1. F7: SPEED-OF-LIGHT OPTICAL FIBER & VACUUM PROPAGATION TESTS
# ==============================================================================

class TestOpticalLatencyInvariant:

    def test_haversine_distance_geodesic(self):
        # London (51.5074 N, 0.1278 W) to New York (40.7128 N, 74.0060 W)
        d_london_nyc = haversine_distance_km(51.5074, -0.1278, 40.7128, -74.0060)
        assert 5500.0 < d_london_nyc < 5650.0

        # Tokyo (35.6762 N, 139.6503 E) to San Francisco (37.7749 N, 122.4194 W)
        d_tokyo_sf = haversine_distance_km(35.6762, 139.6503, 37.7749, -122.4194)
        assert 8200.0 < d_tokyo_sf < 8400.0

        # Identical coordinates -> 0 km
        assert haversine_distance_km(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_positive_realistic_latencies(self):
        # 1. Transatlantic optical fiber: 6000 km, reported 75 ms RTT
        # c_fiber = c / 1.47 ≈ 203,940.45 km/s -> RTT_min = 2 * 6000 / 203940.45 * 1000 = 58.84 ms
        res_transatlantic = check_optical_latency_invariant(
            distance_km=6000.0,
            reported_latency_ms=75.0,
            medium="silica_fiber"
        )
        assert res_transatlantic["is_physically_possible"] is True
        assert res_transatlantic["violation_type"] is None
        assert res_transatlantic["theoretical_min_rtt_ms"] < 75.0

        # 2. Local datacenter interconnect: 20 km fiber, 0.5 ms RTT (RTT_min ≈ 0.196 ms)
        res_dc = check_optical_latency_invariant(distance_km=20.0, reported_latency_ms=0.5)
        assert res_dc["is_physically_possible"] is True

        # 3. Vacuum propagation: Moon to Earth (384,400 km, reported 3000 ms RTT)
        # In vacuum: c = 299,792.458 km/s -> RTT_min = 2 * 384400 / 299792.458 * 1000 ≈ 2564.44 ms
        res_moon = check_optical_latency_invariant(
            distance_km=384400.0,
            reported_latency_ms=3000.0,
            medium="vacuum"
        )
        assert res_moon["is_physically_possible"] is True

        # 4. Copper transmission line (n ≈ 1.4925, 0.67c): 100 km, 1.2 ms RTT
        res_copper = check_optical_latency_invariant(
            distance_km=100.0,
            reported_latency_ms=1.2,
            medium="copper"
        )
        assert res_copper["is_physically_possible"] is True

    def test_one_way_vs_rtt_evaluation(self):
        # 10,000 km in fiber: One-way min ≈ 49.03 ms, RTT min ≈ 98.07 ms
        # Claiming 60 ms one-way -> valid
        res_oneway_valid = check_optical_latency_invariant(
            distance_km=10000.0,
            reported_latency_ms=60.0,
            is_rtt=False
        )
        assert res_oneway_valid["is_physically_possible"] is True

        # Claiming 60 ms RTT for 10,000 km -> impossible (< 98.07 ms)
        res_rtt_invalid = check_optical_latency_invariant(
            distance_km=10000.0,
            reported_latency_ms=60.0,
            is_rtt=True
        )
        assert res_rtt_invalid["is_physically_possible"] is False
        assert res_rtt_invalid["violation_type"] == VIOLATION_SPEED_OF_LIGHT

    def test_route_curvature_refraction_factor(self):
        # Straight distance = 1000 km. Curvature k = 1.3 -> effective distance = 1300 km
        # RTT_min for 1300 km in fiber (n=1.47) ≈ 2 * 1300 / 203940.45 * 1000 ≈ 12.75 ms
        # 11 ms would be valid for 1000 km straight (min 9.8 ms), but invalid with k=1.3 (min 12.75 ms)
        res_straight = check_optical_latency_invariant(distance_km=1000.0, reported_latency_ms=11.0, route_curvature_factor=1.0)
        assert res_straight["is_physically_possible"] is True

        res_curved = check_optical_latency_invariant(distance_km=1000.0, reported_latency_ms=11.0, route_curvature_factor=1.3)
        assert res_curved["is_physically_possible"] is False
        assert res_curved["violation_type"] == VIOLATION_SPEED_OF_LIGHT

    def test_coordinate_input_haversine_integration(self):
        # London to NYC (~5570 km). Claiming 5 ms RTT -> impossible
        res = check_optical_latency_invariant(
            lat1=51.5074, lon1=-0.1278,
            lat2=40.7128, lon2=-74.0060,
            reported_latency_ms=5.0
        )
        assert res["is_physically_possible"] is False
        assert res["distance_km"] > 5500.0

    def test_boundary_exact_propagation_threshold(self):
        dist = 5000.0
        c_fiber = SPEED_OF_LIGHT_VACUUM_KM_S / 1.47
        t_exact_rtt = (2.0 * dist / c_fiber) * 1000.0

        # Exact threshold -> physically valid
        res_exact = check_optical_latency_invariant(distance_km=dist, reported_latency_ms=t_exact_rtt)
        assert res_exact["is_physically_possible"] is True

        # Just 0.1 ms below threshold -> physical violation
        res_below = check_optical_latency_invariant(distance_km=dist, reported_latency_ms=t_exact_rtt - 0.1)
        assert res_below["is_physically_possible"] is False
        assert res_below["violation_type"] == VIOLATION_SPEED_OF_LIGHT

    def test_edge_cases_and_invalid_inputs(self):
        # Negative distance
        assert check_optical_latency_invariant(distance_km=-100.0, reported_latency_ms=10.0)["is_physically_possible"] is False
        # Negative latency
        assert check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=-5.0)["is_physically_possible"] is False
        # Negative or zero refractive index
        assert check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=10.0, n_refractive=0.0)["is_physically_possible"] is False
        # Curvature factor < 1.0 (sub-geodesic impossibility)
        assert check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=10.0, route_curvature_factor=0.8)["is_physically_possible"] is False
        # Sub-vacuum refractive index (superluminal n < 1.0)
        assert check_optical_latency_invariant(distance_km=100.0, reported_latency_ms=10.0, n_refractive=0.9)["is_physically_possible"] is False

    def test_interface_contract_verify_optical_latency(self):
        ok, msg = verify_optical_latency_invariant(5000.0, 70.0, n_refractive=1.47)
        assert ok is True
        assert "Compliant" in msg

        bad, msg_bad = verify_optical_latency_invariant(5000.0, 5.0, n_refractive=1.47)
        assert bad is False
        assert "violates physical limit" in msg_bad


# ==============================================================================
# 2. F8: UNIVERSAL SCALABILITY LAW (USL) TESTS
# ==============================================================================

class TestUniversalScalabilityLawInvariant:

    def test_positive_usl_concurrency_scaling(self):
        # N=16, alpha=0.02 (2% contention), beta=0.0005 (0.05% coherency)
        # denom = 1 + 0.02*15 + 0.0005*16*15 = 1 + 0.30 + 0.12 = 1.42 -> C(16) ≈ 11.27x
        res = check_usl_scalability_invariant(
            node_count=16,
            alpha=0.02,
            beta=0.0005,
            claimed_speedup=10.5
        )
        assert res["is_computationally_valid"] is True
        assert res["violation_type"] is None
        assert res["theoretical_max_speedup"] >= 10.5

    def test_usl_single_node_speedup(self):
        # Single node cannot exceed 1.0x speedup
        assert check_usl_scalability_invariant(node_count=1, alpha=0.1, beta=0.01, claimed_speedup=1.0)["is_computationally_valid"] is True
        assert check_usl_scalability_invariant(node_count=1, alpha=0.1, beta=0.01, claimed_speedup=1.04)["is_computationally_valid"] is True
        assert check_usl_scalability_invariant(node_count=1, alpha=0.1, beta=0.01, claimed_speedup=2.0)["is_computationally_valid"] is False

    def test_superlinear_speedup_rejection(self):
        # Claiming speedup > N on parallel computing architectures is physically invalid
        for nodes in [4, 8, 16, 32, 64]:
            res = check_usl_scalability_invariant(node_count=nodes, alpha=0.0, beta=0.0, claimed_speedup=nodes * 1.5)
            assert res["is_computationally_valid"] is False
            assert res["violation_type"] == VIOLATION_SUPERLINEAR_SPEEDUP

    def test_retrograde_peak_coherency_calculation(self):
        # alpha = 0.04, beta = 0.001
        # N* = sqrt((1 - 0.04) / 0.001) = sqrt(0.96 / 0.001) = sqrt(960) ≈ 30.98 -> peak at N ≈ 31
        alpha = 0.04
        beta = 0.001
        n_star = math.sqrt((1.0 - alpha) / beta)
        assert 30.0 < n_star < 32.0

        # Capacity at peak N=31: C(31) = 31 / (1 + 0.04*30 + 0.001*31*30) = 31 / (1 + 1.20 + 0.93) = 31 / 3.13 ≈ 9.90x
        res_peak = check_usl_scalability_invariant(node_count=31, alpha=alpha, beta=beta, claimed_speedup=9.5)
        assert res_peak["is_computationally_valid"] is True
        assert res_peak["optimal_concurrency_n_star"] == round(n_star, 2)

        # In retrograde regime at N=200: C(200) = 200 / (1 + 0.04*199 + 0.001*200*199) = 200 / (1 + 7.96 + 39.8) = 200 / 48.76 ≈ 4.10x
        # Claiming 9.0x speedup at N=200 must fail with COHERENCY_RETROGRADE_VIOLATION
        res_retrograde = check_usl_scalability_invariant(node_count=200, alpha=alpha, beta=beta, claimed_speedup=9.0)
        assert res_retrograde["is_computationally_valid"] is False
        assert res_retrograde["violation_type"] == VIOLATION_COHERENCY_RETROGRADE

    def test_amdahl_asymptote_when_beta_is_zero(self):
        # beta = 0 -> Amdahl asymptote = 1 / alpha
        alpha = 0.05  # Max asymptote = 20x
        res_valid = check_usl_scalability_invariant(node_count=1000, alpha=alpha, beta=0.0, claimed_speedup=18.0)
        assert res_valid["is_computationally_valid"] is True
        assert res_valid["optimal_concurrency_n_star"] is None

        res_invalid = check_usl_scalability_invariant(node_count=1000, alpha=alpha, beta=0.0, claimed_speedup=25.0)
        assert res_invalid["is_computationally_valid"] is False
        assert res_invalid["violation_type"] == VIOLATION_USL_SCALABILITY

    def test_throughput_scaling_with_base_gamma(self):
        # Base gamma = 500 QPS. N=8, alpha=0.1, beta=0.0
        # C(8) = 8 / (1 + 0.1*7) = 8 / 1.7 ≈ 4.706 -> Max throughput = 500 * 4.706 = 2352.9 QPS
        res_tput_valid = check_usl_scalability_invariant(
            node_count=8, alpha=0.1, beta=0.0,
            base_throughput_gamma=500.0,
            claimed_throughput=2200.0
        )
        assert res_tput_valid["is_computationally_valid"] is True

        res_tput_invalid = check_usl_scalability_invariant(
            node_count=8, alpha=0.1, beta=0.0,
            base_throughput_gamma=500.0,
            claimed_throughput=4000.0
        )
        assert res_tput_invalid["is_computationally_valid"] is False

    def test_usl_edge_cases_invalid_inputs(self):
        assert check_usl_scalability_invariant(node_count=0, alpha=0.1, beta=0.0)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=-10, alpha=0.1, beta=0.0)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, alpha=-0.05, beta=0.0)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, alpha=0.05, beta=-0.01)["is_computationally_valid"] is False
        assert check_usl_scalability_invariant(node_count=10, alpha=1.5, beta=0.0)["is_computationally_valid"] is False

    def test_interface_contract_verify_usl(self):
        ok, msg = verify_usl_invariant(concurrency=10, throughput=5000.0, gamma=1000.0, alpha=0.05, beta=0.001)
        assert ok is True
        assert "Compliant" in msg

        bad, msg_bad = verify_usl_invariant(concurrency=10, throughput=20000.0, gamma=1000.0, alpha=0.05, beta=0.001)
        assert bad is False
        assert "exceeds" in msg_bad or "violates" in msg_bad


# ==============================================================================
# 3. F9: CAP & PACELC LATENCY-CONSISTENCY BOUNDS TESTS
# ==============================================================================

class TestCapPacelcInvariant:

    def test_cap_partition_consistency_availability_exclusivity(self):
        # 1. Partition active + Strong Consistency + 100% Availability -> CAP VIOLATION
        claim_cap_violation = {
            "partition_active": True,
            "consistency": "linearizable",
            "availability": "100%"
        }
        res = check_cap_pacelc_invariant(claim_cap_violation)
        assert res["is_computationally_valid"] is False
        assert res["violation_type"] == VIOLATION_CAP_PARTITION
        assert res["tradeoff_model"] == "CP_VIOLATION"

        # 2. Partition active + Eventual Consistency + 100% Availability -> VALID (AP model)
        claim_ap = {
            "partition_active": True,
            "consistency": "eventual",
            "availability": "100%"
        }
        res_ap = check_cap_pacelc_invariant(claim_ap)
        assert res_ap["is_computationally_valid"] is True

        # 3. Partition active + Strong Consistency + Refusal/Partial Availability -> VALID (CP model)
        claim_cp = {
            "partition_active": True,
            "consistency": "linearizable",
            "availability": "degraded_or_refusal"
        }
        res_cp = check_cap_pacelc_invariant(claim_cp)
        assert res_cp["is_computationally_valid"] is True

    def test_pacelc_zero_latency_multi_region_rejection(self):
        # Multi-region linearizable replication claiming 0ms latency violates Lipton-Sandberg bound (r + w >= D)
        claim_pacelc_zero = {
            "multi_region": True,
            "consistency": "linearizable",
            "replication_latency_ms": 0.0
        }
        res = check_cap_pacelc_invariant(claim_pacelc_zero)
        assert res["is_computationally_valid"] is False
        assert res["violation_type"] == VIOLATION_PACELC_ZERO_LATENCY

        # Multi-region with realistic cross-datacenter latency (50ms) -> VALID
        claim_pacelc_ok = {
            "multi_region": True,
            "consistency": "linearizable",
            "replication_latency_ms": 50.0
        }
        assert check_cap_pacelc_invariant(claim_pacelc_ok)["is_computationally_valid"] is True

    def test_distributed_quorum_overlap_and_split_brain(self):
        # 1. Valid quorum: N=5, R=3, W=3 -> R+W=6 > 5, W=3 > 2.5
        claim_q_ok = {"n_replicas": 5, "r_quorum": 3, "w_quorum": 3, "strong_consistency": True}
        assert check_cap_pacelc_invariant(claim_q_ok)["is_computationally_valid"] is True

        # 2. Quorum Deficit: N=5, R=2, W=3 -> R+W=5 <= 5 -> QUORUM_DEFICIT
        claim_q_deficit = {"n_replicas": 5, "r_quorum": 2, "w_quorum": 3, "strong_consistency": True}
        res_def = check_cap_pacelc_invariant(claim_q_deficit)
        assert res_def["is_computationally_valid"] is False
        assert res_def["violation_type"] == VIOLATION_QUORUM_DEFICIT

        # 3. Split-brain write conflict risk: N=6, R=5, W=3 -> R+W=8 > 6, but W=3 <= N/2=3.0 -> SPLIT_BRAIN_RISK
        claim_split_brain = {"n_replicas": 6, "r_quorum": 5, "w_quorum": 3, "strong_consistency": True}
        res_sb = check_cap_pacelc_invariant(claim_split_brain)
        assert res_sb["is_computationally_valid"] is False
        assert res_sb["violation_type"] == VIOLATION_SPLIT_BRAIN

    def test_natural_language_cap_pacelc_assertions(self):
        # CAP text violation
        txt_cap = "Our new database provides linearizable consistency and 100% availability during network partition."
        res_cap = check_cap_pacelc_invariant(txt_cap)
        assert res_cap["is_computationally_valid"] is False
        assert res_cap["violation_type"] == VIOLATION_CAP_PARTITION

        # PACELC text violation
        txt_pacelc = "The distributed multi-region cluster achieves instantaneous replication with 0ms latency and strong consistency."
        res_pacelc = check_cap_pacelc_invariant(txt_pacelc)
        assert res_pacelc["is_computationally_valid"] is False
        assert res_pacelc["violation_type"] == VIOLATION_PACELC_ZERO_LATENCY

        # Quorum text deficit
        txt_q = "The cluster runs strong consistency with r=1, w=2, n=5."
        res_q = check_cap_pacelc_invariant(txt_q)
        assert res_q["is_computationally_valid"] is False
        assert res_q["violation_type"] == VIOLATION_QUORUM_DEFICIT

    def test_interface_contract_verify_cap_pacelc(self):
        claim_valid = {"n_replicas": 3, "r_quorum": 2, "w_quorum": 2, "strong_consistency": True}
        ok, msg = verify_cap_pacelc_invariant(claim_valid)
        assert ok is True
        assert "Compliant" in msg

        claim_invalid = {"partition_active": True, "consistency": "linearizable", "availability": "100%"}
        bad, msg_bad = verify_cap_pacelc_invariant(claim_invalid)
        assert bad is False
        assert "CAP theorem violation" in msg_bad


# ==============================================================================
# 4. F10: CARNOT THERMODYNAMIC & LANDAUER ERASURE LIMITS TESTS
# ==============================================================================

class TestCarnotAndLandauerInvariants:

    def test_positive_carnot_efficiency(self):
        # T_hot = 600K, T_cold = 300K -> eta_max = 1 - (300/600) = 50.0%
        # Claiming 45% -> valid
        res = check_carnot_efficiency_invariant(t_hot_k=600.0, t_cold_k=300.0, claimed_efficiency=0.45)
        assert res["is_physically_possible"] is True
        assert res["max_theoretical_efficiency"] == 0.50

        # T_hot = 1000K, T_cold = 250K -> eta_max = 1 - (250/1000) = 75.0%
        res_high = check_carnot_efficiency_invariant(t_hot_k=1000.0, t_cold_k=250.0, claimed_efficiency=0.70)
        assert res_high["is_physically_possible"] is True

    def test_negative_carnot_efficiency_violations(self):
        # 1. Exceeding Carnot bound: 600K / 300K claiming 65% (max is 50%)
        res_over = check_carnot_efficiency_invariant(t_hot_k=600.0, t_cold_k=300.0, claimed_efficiency=0.65)
        assert res_over["is_physically_possible"] is False
        assert res_over["violation_type"] == VIOLATION_CARNOT_SECOND_LAW

        # 2. Over-unity claim (> 100% efficiency)
        res_over_unity = check_carnot_efficiency_invariant(t_hot_k=1000.0, t_cold_k=100.0, claimed_efficiency=1.10)
        assert res_over_unity["is_physically_possible"] is False

        # 3. Equal reservoir temperatures (T_hot = T_cold -> eta_max = 0)
        res_equal = check_carnot_efficiency_invariant(t_hot_k=300.0, t_cold_k=300.0, claimed_efficiency=0.10)
        assert res_equal["is_physically_possible"] is False

        # 4. Inverted temperatures (T_cold > T_hot)
        res_inverted = check_carnot_efficiency_invariant(t_hot_k=250.0, t_cold_k=500.0, claimed_efficiency=0.20)
        assert res_inverted["is_physically_possible"] is False

    def test_positive_landauer_erasure_limits(self):
        # Room temp 300K: E_min = 1 * k_B * 300 * ln(2) ≈ 2.87e-21 J
        e_min_1bit = BOLTZMANN_CONSTANT_J_K * 300.0 * math.log(2.0)
        res_room = check_landauer_erasure_invariant(bits_erased=1, ambient_temp_k=300.0, claimed_energy_joules=3.0e-21)
        assert res_room["is_physically_possible"] is True

        # Cryogenic milliKelvin range: 15 mK, 1000 bits
        e_min_15mk = 1000 * BOLTZMANN_CONSTANT_J_K * 0.015 * math.log(2.0)
        res_cryo = check_landauer_erasure_invariant(bits_erased=1000, ambient_temp_k=0.015, claimed_energy_joules=e_min_15mk * 1.05)
        assert res_cryo["is_physically_possible"] is True

    def test_negative_landauer_violations(self):
        # Erasing 1 bit at 300K with 1.0e-22 J (below minimum of 2.87e-21 J)
        res_sub_landauer = check_landauer_erasure_invariant(
            bits_erased=1,
            ambient_temp_k=300.0,
            claimed_energy_joules=1.0e-22
        )
        assert res_sub_landauer["is_physically_possible"] is False
        assert res_sub_landauer["violation_type"] == VIOLATION_LANDAUER_THERMODYNAMIC

    def test_thermodynamic_edge_cases_and_invalid_inputs(self):
        # Zero and negative Kelvin
        assert check_carnot_efficiency_invariant(t_hot_k=0.0, t_cold_k=0.0, claimed_efficiency=0.5)["is_physically_possible"] is False
        assert check_carnot_efficiency_invariant(t_hot_k=-50.0, t_cold_k=-100.0, claimed_efficiency=0.5)["is_physically_possible"] is False
        assert check_landauer_erasure_invariant(ambient_temp_k=0.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_landauer_erasure_invariant(ambient_temp_k=-10.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_landauer_erasure_invariant(bits_erased=0, ambient_temp_k=300.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False
        assert check_landauer_erasure_invariant(bits_erased=-5, ambient_temp_k=300.0, claimed_energy_joules=1e-20)["is_physically_possible"] is False

    def test_interface_contract_verify_carnot_landauer(self):
        # Carnot dict
        claim_carnot = {"t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.45}
        ok_c, _ = verify_carnot_landauer_invariant(claim_carnot)
        assert ok_c is True

        claim_carnot_bad = {"t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.85}
        bad_c, _ = verify_carnot_landauer_invariant(claim_carnot_bad)
        assert bad_c is False

        # Landauer dict
        claim_landauer = {"ambient_temp_k": 300.0, "bits_erased": 10, "claimed_energy_joules": 1e-18}
        ok_l, _ = verify_carnot_landauer_invariant(claim_landauer)
        assert ok_l is True


# ==============================================================================
# 5. F11: SHANNON CHANNEL CAPACITY CEILING TESTS
# ==============================================================================

class TestShannonChannelCapacityInvariant:

    def test_positive_shannon_capacity(self):
        # 20 MHz channel, SNR = 30 dB (SNR_linear = 1000)
        # C = 20e6 * log2(1001) ≈ 20e6 * 9.967 ≈ 199.35 Mbps
        # Claiming 150 Mbps -> valid
        b_hz = 20e6
        snr_db = 30.0
        res = check_shannon_capacity_invariant(
            bandwidth_hz=b_hz,
            snr_db=snr_db,
            claimed_bps=150e6
        )
        assert res["is_physically_possible"] is True
        assert res["theoretical_capacity_bps"] > 190e6
        assert res["spectral_efficiency_bps_hz"] == 7.5

    def test_negative_shannon_capacity_violation(self):
        # 10 MHz channel, SNR_linear = 10 -> C = 10e6 * log2(11) ≈ 34.59 Mbps
        # Claiming 100 Mbps -> exceeds capacity
        res_violation = check_shannon_capacity_invariant(
            bandwidth_hz=10e6,
            snr_linear=10.0,
            claimed_bps=100e6
        )
        assert res_violation["is_physically_possible"] is False
        assert res_violation["violation_type"] == VIOLATION_SHANNON_CAPACITY

    def test_low_and_high_snr_asymptotic_regimes(self):
        # Low SNR: B = 100 kHz, SNR = 1e-4 -> C ≈ B * SNR / ln(2) ≈ 14.42 bps
        c_low = check_shannon_capacity_invariant(bandwidth_hz=100e3, snr_linear=1e-4, claimed_bps=10.0)
        assert c_low["is_physically_possible"] is True

        c_low_bad = check_shannon_capacity_invariant(bandwidth_hz=100e3, snr_linear=1e-4, claimed_bps=50.0)
        assert c_low_bad["is_physically_possible"] is False

        # High SNR: B = 1 GHz, SNR = 100 dB (10^10) -> C ≈ 10^9 * 33.22 ≈ 33.22 Gbps
        c_high = check_shannon_capacity_invariant(bandwidth_hz=1e9, snr_db=100.0, claimed_bps=30e9)
        assert c_high["is_physically_possible"] is True

        c_high_bad = check_shannon_capacity_invariant(bandwidth_hz=1e9, snr_db=100.0, claimed_bps=50e9)
        assert c_high_bad["is_physically_possible"] is False

    def test_shannon_edge_cases_invalid_inputs(self):
        assert check_shannon_capacity_invariant(bandwidth_hz=0.0, snr_linear=10.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=-1e6, snr_linear=10.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=1e6, snr_linear=-5.0, claimed_bps=10.0)["is_physically_possible"] is False
        assert check_shannon_capacity_invariant(bandwidth_hz=1e6, snr_linear=10.0, claimed_bps=-100.0)["is_physically_possible"] is False

    def test_interface_contract_verify_shannon_capacity(self):
        ok, msg = verify_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=15.0, claimed_bps=30e6)
        assert ok is True
        assert "Compliant" in msg

        bad, msg_bad = verify_shannon_capacity_invariant(bandwidth_hz=10e6, snr_linear=15.0, claimed_bps=200e6)
        assert bad is False
        assert "exceeds Shannon channel capacity" in msg_bad


# ==============================================================================
# 6. UNIFIED INVARIANT EVALUATOR & NATURAL LANGUAGE CLAIM PARSER TESTS
# ==============================================================================

class TestUnifiedInvariantEvaluatorAndParser:

    def test_parse_claims_from_text(self):
        # Multi-claim paragraph
        text = (
            "We deployed a transatlantic fiber link across 6000 km with 10 ms latency. "
            "Our cluster of 64 nodes achieved 150x speedup with contention alpha=0.05. "
            "The heat engine operates between Th=600K and Tc=300K with 85% efficiency. "
            "Erasing 1000 bits at 300 K using 1e-25 J of energy. "
            "The wireless link has bandwidth 20 MHz and SNR of 30 dB delivering 5 Gbps."
        )
        parsed = parse_claims_from_text(text)
        assert len(parsed) >= 4

        # Evaluate parsed claims
        eval_res = evaluate_all_boundary_invariants(text)
        assert eval_res["valid"] is False
        assert eval_res["multiplier"] == 0.0
        assert len(eval_res["violations"]) >= 3
        assert len(eval_res["diagnostics"]) >= 3

    def test_evaluate_all_structured_list_all_valid(self):
        valid_claims = [
            {"type": "OPTICAL", "distance_km": 5000.0, "reported_latency_ms": 70.0},
            {"type": "USL", "node_count": 16, "alpha": 0.02, "beta": 0.001, "claimed_speedup": 10.0},
            {"type": "CARNOT", "t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.40},
            {"type": "LANDAUER", "bit_count": 100, "t_kelvin": 300.0, "claimed_energy_joules": 1e-18},
            {"type": "SHANNON", "bandwidth_hz": 20e6, "snr_linear": 1000.0, "claimed_bps": 100e6},
            {"type": "CAP", "n_replicas": 5, "r_quorum": 3, "w_quorum": 3, "strong_consistency": True}
        ]
        res = evaluate_all_boundary_invariants(valid_claims)
        assert res["valid"] is True
        assert res["multiplier"] == 1.0
        assert len(res["violations"]) == 0

    def test_evaluate_all_single_violation_binary_multiplier(self):
        # Single invalid optical claim in a mixed payload resets multiplier to 0.0
        claims = [
            {"type": "CARNOT", "t_hot_k": 800.0, "t_cold_k": 400.0, "claimed_efficiency": 0.40},
            {"type": "OPTICAL", "distance_km": 10000.0, "reported_latency_ms": 1.0}  # Impossible
        ]
        res = evaluate_all_boundary_invariants(claims)
        assert res["valid"] is False
        assert res["multiplier"] == 0.0
        assert len(res["violations"]) == 1
        assert res["violations"][0]["invariant"] == INV_SPEED_OF_LIGHT
