"""
Physical, Mathematical & Computational Boundary Invariant Guards (Milestone M4).
Features:
- F7: Speed-of-Light Optical Fiber & Vacuum Latency Invariant Guard
- F8: Universal Scalability Law (USL) Guard
- F9: CAP & PACELC Latency-Consistency Bounds
- F10: Carnot Thermodynamic Efficiency & Landauer Erasure Energy Limits
- F11: Shannon Channel Capacity Ceiling
- Unified Boundary Invariant Evaluation Coordinator & Natural Language Claim Parser

Zero-dependency, standard-library implementation adhering to first-principles physical and computational limits.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

# ==============================================================================
# PHYSICAL AND MATHEMATICAL CONSTANTS
# ==============================================================================

SPEED_OF_LIGHT_VACUUM_KM_S: float = 299792.458  # c in vacuum (km/s)
BOLTZMANN_CONSTANT_J_K: float = 1.380649e-23     # k_B in Joules/Kelvin (2019 SI definition)
EARTH_RADIUS_KM: float = 6371.0                  # Mean volumetric Earth radius in km

# Refractive Indices for Various Transmission Media (n >= 1.0)
REFRACTIVE_INDICES: Dict[str, float] = {
    "vacuum": 1.0,
    "air": 1.000293,
    "silica_fiber": 1.47,
    "fiber": 1.47,
    "optical_fiber": 1.47,
    "standard_fiber": 1.47,
    "copper": 1.492537,     # Velocity factor ~0.67c (c / 0.67)
    "coaxial": 1.492537,
}

DEFAULT_SILICA_FIBER_REFRACTIVE_INDEX: float = 1.47

# Invariant Identifiers
INV_SPEED_OF_LIGHT: str = "SPEED_OF_LIGHT_OPTICAL_FIBER"
INV_USL: str = "UNIVERSAL_SCALABILITY_LAW"
INV_CAP_PACELC: str = "CAP_PACELC_BOUND"
INV_CARNOT: str = "CARNOT_THERMODYNAMIC_LIMIT"
INV_LANDAUER: str = "LANDAUER_LIMIT"
INV_SHANNON: str = "SHANNON_CHANNEL_CAPACITY"

# Violation Descriptors
VIOLATION_SPEED_OF_LIGHT: str = "SPEED_OF_LIGHT_VIOLATION"
VIOLATION_SUPERLINEAR_SPEEDUP: str = "SUPERLINEAR_SPEEDUP_VIOLATION"
VIOLATION_COHERENCY_RETROGRADE: str = "COHERENCY_RETROGRADE_VIOLATION"
VIOLATION_USL_SCALABILITY: str = "USL_SCALABILITY_VIOLATION"
VIOLATION_CAP_PARTITION: str = "CAP_PARTITION_CONSISTENCY_VIOLATION"
VIOLATION_PACELC_ZERO_LATENCY: str = "PACELC_ZERO_LATENCY_VIOLATION"
VIOLATION_QUORUM_DEFICIT: str = "QUORUM_DEFICIT_VIOLATION"
VIOLATION_SPLIT_BRAIN: str = "SPLIT_BRAIN_RISK"
VIOLATION_CARNOT_SECOND_LAW: str = "CARNOT_SECOND_LAW_VIOLATION"
VIOLATION_LANDAUER_THERMODYNAMIC: str = "LANDAUER_THERMODYNAMIC_VIOLATION"
VIOLATION_SHANNON_CAPACITY: str = "SHANNON_CAPACITY_VIOLATION"
VIOLATION_INVALID_INPUT: str = "INVALID_PHYSICAL_PARAMETERS"


# ==============================================================================
# GEODESIC & PROPAGATION HELPER UTILITIES
# ==============================================================================

def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    earth_radius_km: float = EARTH_RADIUS_KM
) -> float:
    """
    Computes the great-circle geodesic distance between two points on a spherical Earth
    using the Haversine formula.

    Args:
        lat1, lon1: Coordinates of origin point in degrees.
        lat2, lon2: Coordinates of destination point in degrees.
        earth_radius_km: Earth radius in kilometers (default 6371.0 km).

    Returns:
        Great-circle distance in kilometers.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return earth_radius_km * c


# ==============================================================================
# FEATURE F7: SPEED-OF-LIGHT OPTICAL FIBER & VACUUM LATENCY INVARIANT GUARD
# ==============================================================================

def check_optical_latency_invariant(
    distance_km: Optional[float] = None,
    reported_latency_ms: Optional[float] = None,
    claimed_latency_ms: Optional[float] = None,
    medium: str = "silica_fiber",
    n_refractive: Optional[float] = None,
    route_curvature_factor: float = 1.0,
    is_rtt: bool = True,
    lat1: Optional[float] = None,
    lon1: Optional[float] = None,
    lat2: Optional[float] = None,
    lon2: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculates theoretical minimum propagation latency given geodesic distance (or coordinates)
    and transmission medium ('vacuum', 'silica_fiber', 'air', 'copper').

    Propagates at v = c / n where c = 299,792.458 km/s and n is refractive index.
    Flags any claimed latency lower than propagation lower bound as SPEED_OF_LIGHT_VIOLATION.

    Args:
        distance_km: Distance in kilometers.
        reported_latency_ms: Claimed latency in milliseconds.
        claimed_latency_ms: Alias for reported_latency_ms.
        medium: Transmission medium string ('vacuum', 'silica_fiber', 'air', 'copper').
        n_refractive: Optional explicit refractive index (overrides medium default).
        route_curvature_factor: Route terrestrial curvature/refraction factor k >= 1.0 (default 1.0).
        is_rtt: Whether latency is round-trip time (RTT = 2 * one-way, default True).
        lat1, lon1, lat2, lon2: Optional geographic coordinates to compute Haversine distance.

    Returns:
        Structured evaluation dictionary with physical validity and violation diagnostics.
    """
    latency = reported_latency_ms if reported_latency_ms is not None else claimed_latency_ms

    # Handle coordinates if distance_km not provided directly
    if distance_km is None and None not in (lat1, lon1, lat2, lon2):
        distance_km = haversine_distance_km(float(lat1), float(lon1), float(lat2), float(lon2))

    if distance_km is None or latency is None:
        return {
            "invariant": INV_SPEED_OF_LIGHT,
            "distance_km": distance_km if distance_km is not None else 0.0,
            "theoretical_min_one_way_ms": 0.0,
            "theoretical_min_rtt_ms": 0.0,
            "reported_latency_ms": latency if latency is not None else 0.0,
            "is_physically_possible": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "Both distance_km and reported_latency_ms must be provided."
        }

    # Resolve refractive index
    if n_refractive is not None:
        n = float(n_refractive)
    else:
        n = REFRACTIVE_INDICES.get(medium.lower(), DEFAULT_SILICA_FIBER_REFRACTIVE_INDEX)

    # Input validation: non-negative physical quantities and valid refractive index
    if distance_km < 0 or latency < 0 or n <= 0 or route_curvature_factor < 1.0:
        return {
            "invariant": INV_SPEED_OF_LIGHT,
            "distance_km": distance_km,
            "medium": medium,
            "refractive_index": n,
            "route_curvature_factor": route_curvature_factor,
            "theoretical_min_one_way_ms": 0.0,
            "theoretical_min_rtt_ms": 0.0,
            "reported_latency_ms": latency,
            "is_physically_possible": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "Distance, latency, refractive index must be non-negative, and curvature factor k >= 1.0."
        }

    # Faster-than-vacuum refractive index (n < 1.0) is superluminal and physically impossible
    if n < 1.0:
        return {
            "invariant": INV_SPEED_OF_LIGHT,
            "distance_km": distance_km,
            "medium": medium,
            "refractive_index": n,
            "route_curvature_factor": route_curvature_factor,
            "theoretical_min_one_way_ms": 0.0,
            "theoretical_min_rtt_ms": 0.0,
            "reported_latency_ms": latency,
            "is_physically_possible": False,
            "violation_type": VIOLATION_SPEED_OF_LIGHT,
            "violation_details": f"Refractive index n={n} < 1.0 violates special relativity (superluminal propagation in vacuum)."
        }

    # Theoretical propagation speed and times
    c_medium = SPEED_OF_LIGHT_VACUUM_KM_S / n
    effective_distance = distance_km * route_curvature_factor
    t_min_one_way_ms = (effective_distance / c_medium) * 1000.0 if effective_distance > 0 else 0.0
    t_min_rtt_ms = t_min_one_way_ms * 2.0

    threshold_ms = t_min_rtt_ms if is_rtt else t_min_one_way_ms
    violates = latency < (threshold_ms - 1e-6)

    latency_mode = "RTT" if is_rtt else "one-way"
    if violates:
        details = (
            f"Reported {latency}ms {latency_mode} latency violates physical limit of "
            f"{round(threshold_ms, 2)}ms for {distance_km}km in {medium} "
            f"(n={n}, k={route_curvature_factor})."
        )
    else:
        details = "Compliant with relativity and optical propagation bounds."

    return {
        "invariant": INV_SPEED_OF_LIGHT,
        "distance_km": distance_km,
        "medium": medium,
        "refractive_index": n,
        "route_curvature_factor": route_curvature_factor,
        "theoretical_min_one_way_ms": round(t_min_one_way_ms, 4),
        "theoretical_min_rtt_ms": round(t_min_rtt_ms, 4),
        "reported_latency_ms": latency,
        "is_rtt": is_rtt,
        "is_physically_possible": not violates,
        "violation_type": VIOLATION_SPEED_OF_LIGHT if violates else None,
        "violation_details": details
    }


def verify_optical_latency_invariant(
    distance_km: float,
    claimed_latency_ms: float,
    n_refractive: float = DEFAULT_SILICA_FIBER_REFRACTIVE_INDEX
) -> Tuple[bool, str]:
    """Interface contract compatibility helper for optical latency check."""
    res = check_optical_latency_invariant(
        distance_km=distance_km,
        reported_latency_ms=claimed_latency_ms,
        n_refractive=n_refractive
    )
    return res["is_physically_possible"], res["violation_details"]


# ==============================================================================
# FEATURE F8: UNIVERSAL SCALABILITY LAW (USL) GUARD
# ==============================================================================

def check_usl_scalability_invariant(
    node_count: int,
    alpha: float = 0.0,
    beta: float = 0.0,
    claimed_speedup: Optional[float] = None,
    base_throughput_gamma: float = 1.0,
    claimed_throughput: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates concurrency and throughput scaling against Gunther's Universal Scalability Law (USL):
        C(N) = N / [1 + alpha*(N - 1) + beta*N*(N - 1)]
    where alpha >= 0 is contention/serialization and beta >= 0 is coherency delay.

    Calculates retrograde peak concurrency N* = sqrt((1 - alpha) / beta) when beta > 0.
    Flags superlinear speedup claims (C(N) > N) and monotonic throughput claims past N*.

    Args:
        node_count: Number of concurrent nodes/cores (N >= 1).
        alpha: Contention / serialization fraction (0.0 <= alpha <= 1.0).
        beta: Coherency delay parameter (beta >= 0.0).
        claimed_speedup: Claimed scaling factor C(N).
        base_throughput_gamma: Single-node base throughput gamma (default 1.0).
        claimed_throughput: Optional absolute throughput X(N) = gamma * C(N).

    Returns:
        Structured evaluation dictionary with computational validity and USL diagnostics.
    """
    if claimed_speedup is None and claimed_throughput is not None:
        claimed_speedup = claimed_throughput / base_throughput_gamma if base_throughput_gamma > 0 else claimed_throughput
    elif claimed_speedup is not None and claimed_throughput is None:
        claimed_throughput = claimed_speedup * base_throughput_gamma

    if claimed_speedup is None:
        claimed_speedup = 1.0
        claimed_throughput = base_throughput_gamma

    # Parameter validation
    if node_count <= 0:
        return {
            "invariant": INV_USL,
            "node_count": node_count,
            "alpha_contention": alpha,
            "beta_coherency": beta,
            "theoretical_max_speedup": 0.0,
            "claimed_speedup": claimed_speedup,
            "is_computationally_valid": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "Node count must be greater than 0."
        }

    if alpha < 0 or beta < 0 or alpha > 1.0:
        return {
            "invariant": INV_USL,
            "node_count": node_count,
            "alpha_contention": alpha,
            "beta_coherency": beta,
            "theoretical_max_speedup": 0.0,
            "claimed_speedup": claimed_speedup,
            "is_computationally_valid": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "USL contention parameter alpha must be in [0.0, 1.0] and coherency beta >= 0.0."
        }

    n = float(node_count)

    # Calculate optimal concurrency N* (retrograde peak) if coherency beta > 0
    n_star: Optional[float] = None
    if beta > 0:
        if (1.0 - alpha) > 0:
            n_star = math.sqrt((1.0 - alpha) / beta)
        else:
            n_star = 1.0

    # Single-node boundary check
    if node_count == 1:
        is_valid = (claimed_speedup <= 1.05)
        return {
            "invariant": INV_USL,
            "node_count": 1,
            "alpha_contention": alpha,
            "beta_coherency": beta,
            "base_throughput_gamma": base_throughput_gamma,
            "theoretical_max_speedup": 1.0,
            "theoretical_max_throughput": base_throughput_gamma,
            "claimed_speedup": claimed_speedup,
            "claimed_throughput": claimed_throughput,
            "optimal_concurrency_n_star": n_star,
            "is_computationally_valid": is_valid,
            "violation_type": VIOLATION_SUPERLINEAR_SPEEDUP if not is_valid else None,
            "violation_details": "Single node speedup cannot exceed 1.0x." if not is_valid else "Compliant with USL."
        }

    # Calculate USL theoretical capacity C(N)
    denom = 1.0 + alpha * (n - 1.0) + beta * n * (n - 1.0)
    theoretical_max_speedup = n / denom if denom > 0 else 0.0
    theoretical_max_throughput = theoretical_max_speedup * base_throughput_gamma

    # Check 1: Superlinear speedup (C(N) > N)
    if claimed_speedup > (n * 1.05):
        return {
            "invariant": INV_USL,
            "node_count": node_count,
            "alpha_contention": alpha,
            "beta_coherency": beta,
            "base_throughput_gamma": base_throughput_gamma,
            "theoretical_max_speedup": round(theoretical_max_speedup, 4),
            "theoretical_max_throughput": round(theoretical_max_throughput, 4),
            "claimed_speedup": claimed_speedup,
            "claimed_throughput": claimed_throughput,
            "optimal_concurrency_n_star": n_star,
            "is_computationally_valid": False,
            "violation_type": VIOLATION_SUPERLINEAR_SPEEDUP,
            "violation_details": f"USL_SCALABILITY violation: Claimed {claimed_speedup}x speedup exceeds linear ideal bound N={node_count}x (superlinear scaling is physically impossible for parallel compute)."
        }

    # Check 2: Retrograde coherency violation (claiming growth or exceeding USL past N*)
    if beta > 0 and n_star is not None and n > n_star:
        if claimed_speedup > (theoretical_max_speedup * 1.05):
            return {
                "invariant": INV_USL,
                "node_count": node_count,
                "alpha_contention": alpha,
                "beta_coherency": beta,
                "base_throughput_gamma": base_throughput_gamma,
                "theoretical_max_speedup": round(theoretical_max_speedup, 4),
                "theoretical_max_throughput": round(theoretical_max_throughput, 4),
                "claimed_speedup": claimed_speedup,
                "claimed_throughput": claimed_throughput,
                "optimal_concurrency_n_star": round(n_star, 2),
                "is_computationally_valid": False,
                "violation_type": VIOLATION_COHERENCY_RETROGRADE,
                "violation_details": (
                    f"USL_SCALABILITY violation: Claimed {claimed_speedup}x speedup violates USL coherency retrograde limit of "
                    f"{round(theoretical_max_speedup, 2)}x at N={node_count} (peak concurrency N*={round(n_star, 2)})."
                )
            }


    # Check 3: Standard USL capacity ceiling
    violates = claimed_speedup > (theoretical_max_speedup * 1.05)
    return {
        "invariant": INV_USL,
        "node_count": node_count,
        "alpha_contention": alpha,
        "beta_coherency": beta,
        "base_throughput_gamma": base_throughput_gamma,
        "theoretical_max_speedup": round(theoretical_max_speedup, 4),
        "theoretical_max_throughput": round(theoretical_max_throughput, 4),
        "claimed_speedup": claimed_speedup,
        "claimed_throughput": claimed_throughput,
        "optimal_concurrency_n_star": round(n_star, 2) if n_star is not None else None,
        "is_computationally_valid": not violates,
        "violation_type": VIOLATION_USL_SCALABILITY if violates else None,
        "violation_details": (
            f"Claimed {claimed_speedup}x speedup exceeds USL bound of {round(theoretical_max_speedup, 2)}x at N={node_count}."
            if violates else "Compliant with USL."
        )
    }


def verify_usl_invariant(
    concurrency: int,
    throughput: float,
    gamma: float,
    alpha: float,
    beta: float
) -> Tuple[bool, str]:
    """Interface contract compatibility helper for USL check."""
    res = check_usl_scalability_invariant(
        node_count=concurrency,
        alpha=alpha,
        beta=beta,
        base_throughput_gamma=gamma,
        claimed_throughput=throughput
    )
    return res["is_computationally_valid"], res["violation_details"]


# ==============================================================================
# FEATURE F9: CAP & PACELC LATENCY-CONSISTENCY BOUNDS
# ==============================================================================

def check_cap_pacelc_invariant(claim: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """
    Evaluates distributed systems consistency and availability against the CAP and PACELC theorems:
    - Under partition (P), consistency (C) and 100% availability (A) are mutually exclusive.
    - Under normal operation (E), latency (L) and linearizable consistency (C) must trade off (PACELC).
    - Distributed quorum intersection: R + W > N and W > N/2 for strong/linearizable consistency.

    Args:
        claim: Structured dictionary or plain text describing distributed system attributes.

    Returns:
        Structured evaluation dictionary with theorem compliance and tradeoff model diagnostics.
    """
    is_valid = True
    violation_type: Optional[str] = None
    violation_reasons: List[str] = []
    tradeoff_model = "GENERAL_DISTRIBUTED"

    if isinstance(claim, dict):
        partition = bool(claim.get("partition_active", claim.get("partition", False)))
        consistency = str(claim.get("consistency", "")).lower()
        availability = str(claim.get("availability", "")).lower()
        strong_flag = bool(claim.get("strong_consistency", False))

        is_linearizable = (
            strong_flag or
            consistency in ("linearizable", "strong", "strict_serializable", "1.0", "true", "acid")
        )
        is_fully_available = availability in ("100%", "high", "available", "always", "1.0", "true", "full", "100% available", "100% availability")

        # 1. CAP Theorem Partition Rule
        if partition and is_linearizable and is_fully_available:
            is_valid = False
            violation_type = VIOLATION_CAP_PARTITION
            tradeoff_model = "CP_VIOLATION"
            violation_reasons.append(
                "CAP theorem violation: Cannot guarantee 100% availability and linearizable consistency simultaneously during a network partition."
            )

        # 2. Distributed Quorum Overlap & Split-Brain Rules
        r = claim.get("r_quorum", claim.get("read_quorum"))
        w = claim.get("w_quorum", claim.get("write_quorum"))
        n = claim.get("n_replicas", claim.get("nodes", claim.get("replicas")))

        if r is not None and w is not None and n is not None:
            r_val, w_val, n_val = int(r), int(w), int(n)
            if n_val > 1:
                if is_linearizable or strong_flag:
                    if (r_val + w_val) <= n_val:
                        is_valid = False
                        violation_type = VIOLATION_QUORUM_DEFICIT
                        tradeoff_model = "QUORUM_DEFICIT"
                        violation_reasons.append(
                            f"Quorum violation: R ({r_val}) + W ({w_val}) = {r_val + w_val} <= N ({n_val}). "
                            "Read/write quorum overlap required for strong consistency."
                        )
                    elif w_val <= (n_val / 2.0):
                        is_valid = False
                        violation_type = VIOLATION_SPLIT_BRAIN
                        tradeoff_model = "SPLIT_BRAIN_RISK"
                        violation_reasons.append(
                            f"Quorum write conflict risk: W ({w_val}) <= N/2 ({n_val / 2.0}). "
                            "Majority write quorum required to prevent split-brain."
                        )
                else:
                    tradeoff_model = "EVENTUAL_CONSISTENCY_QUORUM"

        # 3. PACELC Latency-Consistency Bounds (Lipton-Sandberg Bound)
        multi_region = bool(claim.get("multi_region", claim.get("distributed", claim.get("cross_region", False))))
        claimed_latency = claim.get("replication_latency_ms", claim.get("latency_ms"))
        if multi_region and is_linearizable and claimed_latency is not None:
            if float(claimed_latency) <= 0.0:
                is_valid = False
                violation_type = VIOLATION_PACELC_ZERO_LATENCY
                tradeoff_model = "PACELC_ZERO_LATENCY_VIOLATION"
                violation_reasons.append(
                    "PACELC violation: Zero-latency linearizable replication across distributed regions "
                    "violates speed-of-light propagation bounds (Lipton-Sandberg bound r + w >= D)."
                )

    elif isinstance(claim, str):
        claim_lower = claim.lower()
        has_partition = any(k in claim_lower for k in ("partition", "network split", "disconnected nodes", "island", "network partition"))
        has_strong_c = any(k in claim_lower for k in ("linearizable", "strong consistency", "strictly consistent", "acid", "strict serializability"))
        has_100_a = any(k in claim_lower for k in ("100% availability", "100% available", "zero downtime", "always available", "full availability", "100% uptime"))

        if has_partition and has_strong_c and has_100_a:
            is_valid = False
            violation_type = VIOLATION_CAP_PARTITION
            tradeoff_model = "CP_VIOLATION"
            violation_reasons.append(
                "CAP theorem violation: Claims simultaneous strong consistency and 100% availability during network partition."
            )

        has_zero_latency = any(k in claim_lower for k in ("0ms latency", "zero latency", "zero-latency", "instantaneous replication", "0 ms", "0ms replication"))
        has_distributed = any(k in claim_lower for k in ("multi-region", "cross-datacenter", "transatlantic", "cross-region", "geo-distributed", "distributed network"))

        if has_zero_latency and has_distributed and has_strong_c:
            is_valid = False
            violation_type = VIOLATION_PACELC_ZERO_LATENCY
            tradeoff_model = "PACELC_ZERO_LATENCY_VIOLATION"
            violation_reasons.append(
                "PACELC violation: Zero latency replication with strong consistency across distributed network is physically impossible."
            )

        # Quorum pattern extraction: r=..., w=..., n=...
        q_match = re.search(r'\br\s*=\s*(\d+).*?\bw\s*=\s*(\d+).*?\bn\s*=\s*(\d+)', claim_lower)
        if q_match:
            r_val, w_val, n_val = int(q_match.group(1)), int(q_match.group(2)), int(q_match.group(3))
            if has_strong_c:
                if (r_val + w_val) <= n_val:
                    is_valid = False
                    violation_type = VIOLATION_QUORUM_DEFICIT
                    tradeoff_model = "QUORUM_DEFICIT"
                    violation_reasons.append(f"Quorum violation: R={r_val} + W={w_val} <= N={n_val} cannot guarantee strong consistency.")
                elif w_val <= (n_val / 2.0):
                    is_valid = False
                    violation_type = VIOLATION_SPLIT_BRAIN
                    tradeoff_model = "SPLIT_BRAIN_RISK"
                    violation_reasons.append(f"Quorum write risk: W={w_val} <= N/2 ({n_val/2.0}) permits split-brain writes.")

    return {
        "invariant": INV_CAP_PACELC,
        "is_computationally_valid": is_valid,
        "is_physically_possible": is_valid,
        "tradeoff_model": tradeoff_model,
        "violation_type": violation_type,
        "violation_details": " ".join(violation_reasons) if violation_reasons else "Compliant with CAP/PACELC theorem."
    }


def verify_cap_pacelc_invariant(claim: Union[Dict[str, Any], str]) -> Tuple[bool, str]:
    """Interface contract compatibility helper for CAP/PACELC check."""
    res = check_cap_pacelc_invariant(claim)
    return res["is_computationally_valid"], res["violation_details"]


# ==============================================================================
# FEATURE F10: CARNOT THERMODYNAMIC EFFICIENCY & LANDAUER ERASURE ENERGY LIMITS
# ==============================================================================

def check_carnot_efficiency_invariant(
    t_hot_k: float,
    t_cold_k: float,
    claimed_efficiency: float
) -> Dict[str, Any]:
    """
    Evaluates thermal engine efficiency against the Carnot upper bound:
        eta_max = 1.0 - (T_cold / T_hot)
    where temperatures are strictly positive in Kelvin (T_hot > T_cold > 0 K).
    Flags efficiency claims exceeding eta_max as CARNOT_SECOND_LAW_VIOLATION.

    Args:
        t_hot_k: Hot reservoir temperature in Kelvin.
        t_cold_k: Cold reservoir temperature in Kelvin.
        claimed_efficiency: Claimed thermal efficiency (0.0 to 1.0, or fraction).

    Returns:
        Structured evaluation dictionary with Carnot efficiency limit diagnostics.
    """
    # Validation: Kelvin temperatures must be strictly positive and T_hot > T_cold
    if t_hot_k <= 0 or t_cold_k <= 0 or t_hot_k <= t_cold_k or claimed_efficiency < 0:
        return {
            "invariant": INV_CARNOT,
            "t_hot_k": t_hot_k,
            "t_cold_k": t_cold_k,
            "max_theoretical_efficiency": 0.0,
            "claimed_efficiency": claimed_efficiency,
            "is_physically_possible": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "T_hot must strictly exceed T_cold, both temperatures must be > 0 Kelvin, and efficiency >= 0."
        }

    max_eta = 1.0 - (t_cold_k / t_hot_k)
    violates = (claimed_efficiency > (max_eta + 1e-6)) or (claimed_efficiency > 1.0)

    if violates:
        details = (
            f"Claimed efficiency {round(claimed_efficiency * 100, 2)}% exceeds Carnot ceiling of "
            f"{round(max_eta * 100, 2)}% for T_hot={t_hot_k}K, T_cold={t_cold_k}K "
            "violating the second law of thermodynamics."
        )
    else:
        details = "Compliant with 2nd law of thermodynamics and Carnot efficiency limit."

    return {
        "invariant": INV_CARNOT,
        "t_hot_k": t_hot_k,
        "t_cold_k": t_cold_k,
        "max_theoretical_efficiency": round(max_eta, 4),
        "claimed_efficiency": claimed_efficiency,
        "is_physically_possible": not violates,
        "violation_type": VIOLATION_CARNOT_SECOND_LAW if violates else None,
        "violation_details": details
    }


def check_landauer_erasure_invariant(
    bits_erased: int = 1,
    ambient_temp_k: float = 300.0,
    claimed_energy_joules: float = 0.0,
    t_kelvin: Optional[float] = None,
    bit_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluates computational energy consumption against Landauer's Principle:
        E_min = N_bits * k_B * T * ln(2)
    where k_B = 1.380649e-23 J/K and T is ambient temperature in Kelvin.
    Flags claimed energy expenditure below E_min as LANDAUER_THERMODYNAMIC_VIOLATION.

    Args:
        bits_erased: Number of irreversible bit erasures (N >= 1).
        ambient_temp_k: Ambient operating temperature in Kelvin (T > 0 K).
        claimed_energy_joules: Claimed energy dissipated during erasure in Joules.
        t_kelvin: Optional alias for ambient_temp_k.
        bit_count: Optional alias for bits_erased.

    Returns:
        Structured evaluation dictionary with Landauer energy lower bound diagnostics.
    """
    temp_k = t_kelvin if t_kelvin is not None else ambient_temp_k
    n_bits = bit_count if bit_count is not None else bits_erased

    if temp_k <= 0 or n_bits <= 0 or claimed_energy_joules < 0:
        return {
            "invariant": INV_LANDAUER,
            "t_kelvin": temp_k,
            "bit_count": n_bits,
            "theoretical_min_energy_joules": 0.0,
            "claimed_energy_joules": claimed_energy_joules,
            "is_physically_possible": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "Temperature and bit count must be strictly positive (> 0 Kelvin and >= 1 bit)."
        }

    e_min = float(n_bits) * BOLTZMANN_CONSTANT_J_K * float(temp_k) * math.log(2.0)
    violates = claimed_energy_joules < (e_min * 0.999)

    if violates:
        details = (
            f"Claimed energy {claimed_energy_joules:.3e} J for erasing {n_bits} bit(s) at {temp_k}K "
            f"is below Landauer minimum {e_min:.3e} J."
        )
    else:
        details = "Compliant with Landauer thermodynamic limit."

    return {
        "invariant": INV_LANDAUER,
        "t_kelvin": temp_k,
        "bit_count": n_bits,
        "theoretical_min_energy_joules": e_min,
        "claimed_energy_joules": claimed_energy_joules,
        "is_physically_possible": not violates,
        "violation_type": VIOLATION_LANDAUER_THERMODYNAMIC if violates else None,
        "violation_details": details
    }


# Compatibility alias
check_landauer_limit_invariant = check_landauer_erasure_invariant


def verify_carnot_landauer_invariant(claim: Dict[str, Any]) -> Tuple[bool, str]:
    """Interface contract compatibility helper for Carnot & Landauer checks."""
    if "t_hot_k" in claim or "t_cold_k" in claim:
        res = check_carnot_efficiency_invariant(
            t_hot_k=float(claim.get("t_hot_k", 0.0)),
            t_cold_k=float(claim.get("t_cold_k", 0.0)),
            claimed_efficiency=float(claim.get("claimed_efficiency", 0.0))
        )
    else:
        res = check_landauer_erasure_invariant(
            t_kelvin=float(claim.get("t_kelvin", claim.get("ambient_temp_k", 300.0))),
            claimed_energy_joules=float(claim.get("claimed_energy_joules", 0.0)),
            bit_count=int(claim.get("bit_count", claim.get("bits_erased", 1)))
        )
    return res["is_physically_possible"], res["violation_details"]


# ==============================================================================
# FEATURE F11: SHANNON CHANNEL CAPACITY CEILING
# ==============================================================================

def check_shannon_capacity_invariant(
    bandwidth_hz: float,
    snr_linear: Optional[float] = None,
    claimed_bps: Optional[float] = None,
    snr_db: Optional[float] = None,
    claimed_throughput_bps: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates communication channel data rate against the Shannon-Hartley theorem:
        C = B * log2(1 + SNR)
    where B is channel bandwidth in Hz and SNR is the signal-to-noise ratio.
    Flags claimed data rate R > C as SHANNON_CAPACITY_VIOLATION.

    Args:
        bandwidth_hz: Channel bandwidth in Hertz (B > 0).
        snr_linear: Linear signal-to-noise ratio (SNR >= 0).
        claimed_bps: Claimed transmission rate in bits/second.
        snr_db: Optional SNR in decibels (SNR_linear = 10^(SNR_db / 10)).
        claimed_throughput_bps: Optional alias for claimed_bps.

    Returns:
        Structured evaluation dictionary with Shannon capacity ceiling diagnostics.
    """
    rate = claimed_bps if claimed_bps is not None else claimed_throughput_bps
    if rate is None:
        rate = 0.0

    if snr_linear is None and snr_db is not None:
        snr_linear = 10.0 ** (snr_db / 10.0)
    elif snr_linear is None and snr_db is None:
        snr_linear = 1.0

    if snr_db is None and snr_linear is not None:
        snr_db = 10.0 * math.log10(snr_linear) if snr_linear > 0 else -math.inf

    # Parameter validation
    if bandwidth_hz <= 0 or snr_linear < 0 or rate < 0:
        return {
            "invariant": INV_SHANNON,
            "bandwidth_hz": bandwidth_hz,
            "snr_linear": snr_linear,
            "snr_db": snr_db,
            "theoretical_capacity_bps": 0.0,
            "claimed_bps": rate,
            "spectral_efficiency_bps_hz": 0.0,
            "is_physically_possible": False,
            "violation_type": VIOLATION_INVALID_INPUT,
            "violation_details": "Bandwidth must be > 0 Hz and SNR and claimed throughput must be >= 0."
        }

    c_bps = bandwidth_hz * math.log2(1.0 + snr_linear) if snr_linear > 0 else 0.0
    spectral_efficiency = rate / bandwidth_hz if bandwidth_hz > 0 else 0.0
    violates = rate > (c_bps * 1.01)

    if violates:
        details = (
            f"Claimed throughput {rate:.2e} bps exceeds Shannon channel capacity {round(c_bps, 2):.2e} bps "
            f"for B={bandwidth_hz:.2e}Hz, SNR={snr_linear} (spectral efficiency {round(spectral_efficiency, 2)} bps/Hz)."
        )
    else:
        details = "Compliant with Shannon capacity."

    return {
        "invariant": INV_SHANNON,
        "bandwidth_hz": bandwidth_hz,
        "snr_linear": snr_linear,
        "snr_db": round(snr_db, 2) if math.isfinite(snr_db) else None,
        "theoretical_capacity_bps": round(c_bps, 2),
        "claimed_bps": rate,
        "spectral_efficiency_bps_hz": round(spectral_efficiency, 4),
        "is_physically_possible": not violates,
        "violation_type": VIOLATION_SHANNON_CAPACITY if violates else None,
        "violation_details": details
    }


def verify_shannon_capacity_invariant(
    bandwidth_hz: float,
    snr_linear: float,
    claimed_bps: float
) -> Tuple[bool, str]:
    """Interface contract compatibility helper for Shannon capacity check."""
    res = check_shannon_capacity_invariant(
        bandwidth_hz=bandwidth_hz,
        snr_linear=snr_linear,
        claimed_bps=claimed_bps
    )
    return res["is_physically_possible"], res["violation_details"]


# ==============================================================================
# NATURAL LANGUAGE CLAIM PARSER & HEURISTIC EXTRACTOR
# ==============================================================================

def parse_claims_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Scans free-form plain text by analyzing individual sentences to extract structured physical claims:
    - Optical fiber / vacuum latency statements
    - USL / concurrency scaling claims
    - CAP & PACELC distributed guarantees
    - Carnot thermodynamic engine efficiencies
    - Landauer bit erasure energy claims
    - Shannon channel throughput assertions

    Args:
        text: Plain-text string containing candidate claims.

    Returns:
        List of structured claim dictionaries ready for invariant evaluation.
    """
    claims: List[Dict[str, Any]] = []
    if not text or not isinstance(text, str):
        return claims

    # Split into sentences / clauses
    sentences = [s.strip() for s in re.split(r'[.\n;]+', text) if s.strip()]

    for sent in sentences:
        sent_lower = sent.lower()

        # 1. Optical latency extraction
        dist_m = re.search(r'(\d+(?:\.\d+)?)\s*(km|kilometers|kilometer|miles|mile)\b', sent, re.IGNORECASE)
        lat_m = re.search(r'(\d+(?:\.\d+)?)\s*(ms|milliseconds|millisecond|s|seconds|second|us|µs|ns)\b', sent, re.IGNORECASE)
        if dist_m and lat_m:
            dist_val = float(dist_m.group(1))
            dist_unit = dist_m.group(2).lower()
            if dist_unit in ("miles", "mile"):
                dist_km = dist_val * 1.60934
            else:
                dist_km = dist_val

            lat_val = float(lat_m.group(1))
            lat_unit = lat_m.group(2).lower()
            if lat_unit in ("s", "seconds", "second"):
                lat_ms = lat_val * 1000.0
            elif lat_unit in ("us", "µs"):
                lat_ms = lat_val / 1000.0
            elif lat_unit == "ns":
                lat_ms = lat_val / 1e6
            else:
                lat_ms = lat_val

            med = "silica_fiber"
            if "vacuum" in sent_lower:
                med = "vacuum"
            elif "air" in sent_lower:
                med = "air"
            elif "copper" in sent_lower:
                med = "copper"

            claims.append({
                "type": "OPTICAL",
                "distance_km": dist_km,
                "reported_latency_ms": lat_ms,
                "medium": med
            })

        # 2. USL / Concurrency scaling extraction
        nodes_m = re.search(r'(\d+)\s*(?:nodes|servers|cores|threads|instances|workers|processes)\b|(?:node_count|nodes|concurrency)\s*[:=]?\s*(\d+)\b', sent, re.IGNORECASE)
        speedup_m = re.search(r'(\d+(?:\.\d+)?)\s*x\s*(?:speedup|throughput|scaling|acceleration)?\b|(?:speedup|throughput|scaling)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*x?\b', sent, re.IGNORECASE)
        if nodes_m and speedup_m:
            n_str = nodes_m.group(1) if nodes_m.group(1) is not None else nodes_m.group(2)
            s_str = speedup_m.group(1) if speedup_m.group(1) is not None else speedup_m.group(2)
            nodes = int(n_str)
            speedup = float(s_str)

            alpha = 0.0
            beta = 0.0
            alpha_m = re.search(r'\balpha\s*[:=]?\s*(\d+(?:\.\d+)?)', sent, re.IGNORECASE) or re.search(r'\balpha\s*[:=]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
            if alpha_m:
                alpha = float(alpha_m.group(1))
            beta_m = re.search(r'\bbeta\s*[:=]?\s*(\d+(?:\.\d+)?)', sent, re.IGNORECASE) or re.search(r'\bbeta\s*[:=]?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
            if beta_m:
                beta = float(beta_m.group(1))

            claims.append({
                "type": "USL",
                "node_count": nodes,
                "alpha": alpha,
                "beta": beta,
                "claimed_speedup": speedup
            })

        # 3. Carnot thermodynamic extraction
        # Look for two temperatures in Kelvin + efficiency
        k_temps = re.findall(r'(?:th|t_hot|hot)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*k\b', sent, re.IGNORECASE)
        eff_m = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:efficiency|thermal efficiency)?|(?:efficiency|eta)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(%|\b)', sent, re.IGNORECASE)
        if len(k_temps) >= 2 and eff_m:
            t1 = float(k_temps[0])
            t2 = float(k_temps[1])
            t_hot = max(t1, t2)
            t_cold = min(t1, t2)

            if eff_m.group(1) is not None:
                eff = float(eff_m.group(1)) / 100.0
            else:
                raw_eff = float(eff_m.group(2))
                is_pct = (eff_m.group(3) == "%") or (raw_eff > 1.0)
                eff = raw_eff / 100.0 if is_pct else raw_eff

            claims.append({
                "type": "CARNOT",
                "t_hot_k": t_hot,
                "t_cold_k": t_cold,
                "claimed_efficiency": eff
            })

        # 4. Landauer extraction
        bits_m = re.search(r'(\d+)\s*bits?\b', sent, re.IGNORECASE)
        temp_m = re.search(r'(\d+(?:\.\d+)?)\s*k\b', sent, re.IGNORECASE)
        energy_m = re.search(r'(\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*(j|joules|nanojoules|nj|pj|fj|aj|zj|yj)\b', sent, re.IGNORECASE)
        if bits_m and temp_m and energy_m:
            bits = int(bits_m.group(1))
            temp = float(temp_m.group(1))
            raw_e = float(energy_m.group(1))
            e_unit = energy_m.group(2).lower()
            if e_unit in ("nanojoules", "nj"):
                e_j = raw_e * 1e-9
            elif e_unit == "pj":
                e_j = raw_e * 1e-12
            elif e_unit == "fj":
                e_j = raw_e * 1e-15
            elif e_unit == "aj":
                e_j = raw_e * 1e-18
            elif e_unit == "zj":
                e_j = raw_e * 1e-21
            elif e_unit == "yj":
                e_j = raw_e * 1e-24
            else:
                e_j = raw_e

            claims.append({
                "type": "LANDAUER",
                "bit_count": bits,
                "t_kelvin": temp,
                "claimed_energy_joules": e_j
            })

        # 5. Shannon capacity extraction
        bw_m = re.search(r'(\d+(?:\.\d+)?)\s*(hz|khz|mhz|ghz)\b', sent, re.IGNORECASE)
        snr_m = re.search(r'(?:snr)\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)\s*(db|\b)', sent, re.IGNORECASE)
        rate_m = re.search(r'(\d+(?:\.\d+)?)\s*(bps|kbps|mbps|gbps|tbps)\b', sent, re.IGNORECASE)
        if bw_m and snr_m and rate_m:
            raw_bw = float(bw_m.group(1))
            bw_unit = bw_m.group(2).lower()
            if bw_unit == "khz":
                bw_hz = raw_bw * 1e3
            elif bw_unit == "mhz":
                bw_hz = raw_bw * 1e6
            elif bw_unit == "ghz":
                bw_hz = raw_bw * 1e9
            else:
                bw_hz = raw_bw

            raw_snr = float(snr_m.group(1))
            is_db = (snr_m.group(2).lower() == "db")
            snr_lin = 10.0 ** (raw_snr / 10.0) if is_db else raw_snr

            raw_rate = float(rate_m.group(1))
            rate_unit = rate_m.group(2).lower()
            if rate_unit == "kbps":
                rate_bps = raw_rate * 1e3
            elif rate_unit == "mbps":
                rate_bps = raw_rate * 1e6
            elif rate_unit == "gbps":
                rate_bps = raw_rate * 1e9
            elif rate_unit == "tbps":
                rate_bps = raw_rate * 1e12
            else:
                rate_bps = raw_rate

            claims.append({
                "type": "SHANNON",
                "bandwidth_hz": bw_hz,
                "snr_linear": snr_lin,
                "claimed_bps": rate_bps
            })

    return claims


# ==============================================================================
# UNIFIED INVARIANT EVALUATION COORDINATOR
# ==============================================================================

def evaluate_all_boundary_invariants(
    claims_or_text: Union[str, List[Dict[str, Any]], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates a collection of structured claim dictionaries, single claim dictionary,
    or natural language text against all fundamental physical and computational boundary invariants:
    - Speed-of-light optical fiber/vacuum propagation latency (F7)
    - Universal Scalability Law concurrency contention & coherency limits (F8)
    - CAP & PACELC consistency and quorum bounds (F9)
    - Carnot thermodynamic efficiency & Landauer information erasure limits (F10)
    - Shannon channel capacity ceiling (F11)

    Returns:
        {
            "valid": bool,
            "violations": List[Dict[str, Any]],
            "multiplier": 1.0 (if valid) or 0.0 (if any invariant violated),
            "diagnostics": List[str]
        }
    """
    violations: List[Dict[str, Any]] = []
    diagnostics: List[str] = []

    def evaluate_single_claim(claim_dict: Dict[str, Any]) -> None:
        inv_type = str(claim_dict.get("type", claim_dict.get("invariant", ""))).upper()

        # 1. Optical Latency
        if ("OPTICAL" in inv_type or "LATENCY" in inv_type or
                ("distance_km" in claim_dict and ("reported_latency_ms" in claim_dict or "claimed_latency_ms" in claim_dict))):
            res = check_optical_latency_invariant(
                distance_km=float(claim_dict["distance_km"]),
                reported_latency_ms=float(claim_dict.get("reported_latency_ms", claim_dict.get("claimed_latency_ms", 0.0))),
                medium=claim_dict.get("medium", "silica_fiber"),
                n_refractive=claim_dict.get("n_refractive"),
                route_curvature_factor=float(claim_dict.get("route_curvature_factor", 1.0)),
                is_rtt=bool(claim_dict.get("is_rtt", True))
            )
            if not res["is_physically_possible"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

        # 2. Universal Scalability Law (USL)
        elif ("USL" in inv_type or "SCALABILITY" in inv_type or
              ("node_count" in claim_dict and ("claimed_speedup" in claim_dict or "claimed_throughput" in claim_dict))):
            res = check_usl_scalability_invariant(
                node_count=int(claim_dict["node_count"]),
                alpha=float(claim_dict.get("alpha", claim_dict.get("alpha_contention", 0.0))),
                beta=float(claim_dict.get("beta", claim_dict.get("beta_coherency", 0.0))),
                claimed_speedup=float(claim_dict["claimed_speedup"]) if "claimed_speedup" in claim_dict else None,
                base_throughput_gamma=float(claim_dict.get("base_throughput_gamma", 1.0)),
                claimed_throughput=float(claim_dict["claimed_throughput"]) if "claimed_throughput" in claim_dict else None
            )
            if not res["is_computationally_valid"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

        # 3. Carnot Thermodynamic Limit
        elif ("CARNOT" in inv_type or
              ("t_hot_k" in claim_dict and "t_cold_k" in claim_dict and "claimed_efficiency" in claim_dict)):
            res = check_carnot_efficiency_invariant(
                t_hot_k=float(claim_dict["t_hot_k"]),
                t_cold_k=float(claim_dict["t_cold_k"]),
                claimed_efficiency=float(claim_dict["claimed_efficiency"])
            )
            if not res["is_physically_possible"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

        # 4. Landauer Thermodynamic Limit
        elif ("LANDAUER" in inv_type or
              ("t_kelvin" in claim_dict and "claimed_energy_joules" in claim_dict) or
              ("ambient_temp_k" in claim_dict and "claimed_energy_joules" in claim_dict)):
            res = check_landauer_erasure_invariant(
                bits_erased=int(claim_dict.get("bits_erased", claim_dict.get("bit_count", 1))),
                ambient_temp_k=float(claim_dict.get("ambient_temp_k", claim_dict.get("t_kelvin", 300.0))),
                claimed_energy_joules=float(claim_dict["claimed_energy_joules"])
            )
            if not res["is_physically_possible"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

        # 5. Shannon Channel Capacity
        elif ("SHANNON" in inv_type or
              ("bandwidth_hz" in claim_dict and ("claimed_bps" in claim_dict or "claimed_throughput_bps" in claim_dict))):
            res = check_shannon_capacity_invariant(
                bandwidth_hz=float(claim_dict["bandwidth_hz"]),
                snr_linear=float(claim_dict["snr_linear"]) if "snr_linear" in claim_dict else None,
                claimed_bps=float(claim_dict.get("claimed_bps", claim_dict.get("claimed_throughput_bps", 0.0))),
                snr_db=float(claim_dict["snr_db"]) if "snr_db" in claim_dict else None
            )
            if not res["is_physically_possible"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

        # 6. CAP / PACELC Bounds
        elif ("CAP" in inv_type or "PACELC" in inv_type or
              "partition_active" in claim_dict or "partition" in claim_dict or
              "r_quorum" in claim_dict or "read_quorum" in claim_dict or
              "multi_region" in claim_dict):
            res = check_cap_pacelc_invariant(claim_dict)
            if not res["is_computationally_valid"]:
                violations.append(res)
                diagnostics.append(res["violation_details"])

    if isinstance(claims_or_text, dict):
        evaluate_single_claim(claims_or_text)
    elif isinstance(claims_or_text, list):
        for item in claims_or_text:
            if isinstance(item, dict):
                evaluate_single_claim(item)
            elif isinstance(item, str):
                sub_res = evaluate_all_boundary_invariants(item)
                violations.extend(sub_res["violations"])
                diagnostics.extend(sub_res["diagnostics"])
    elif isinstance(claims_or_text, str):
        # 1. Evaluate CAP / PACELC semantic bounds directly on text
        cap_res = check_cap_pacelc_invariant(claims_or_text)
        if not cap_res["is_computationally_valid"]:
            violations.append(cap_res)
            diagnostics.append(cap_res["violation_details"])

        # 2. Parse any structured physical claims embedded in text and evaluate them
        parsed_claims = parse_claims_from_text(claims_or_text)
        for parsed in parsed_claims:
            evaluate_single_claim(parsed)

    is_valid = (len(violations) == 0)
    return {
        "valid": is_valid,
        "violations": violations,
        "multiplier": 1.0 if is_valid else 0.0,
        "diagnostics": diagnostics
    }


# Standard alias
evaluate_boundary_invariants = evaluate_all_boundary_invariants
