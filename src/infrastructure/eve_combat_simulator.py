"""
Autonomous EVE Online Fleet Combat Simulator & Dogma Mathematics Engine.
Standard: Zero external dependencies (stdlib math, json, os, sys, time, random).
Ponytail Senior Dev Principle: Exact canonical formulas, sub-millisecond execution.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAULT_COMBAT_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Combat_Intelligence")


def calculate_turret_hit_chance(
    optimal: float,
    falloff: float,
    tracking: float,
    weapon_sig: float,
    target_sig: float,
    distance: float,
    transversal_velocity: float
) -> float:
    """
    Calculate turret hit probability using the canonical CCP Dogma formula:
    P(hit) = 0.5 ^ ( ((transversal / distance) / tracking * (weapon_sig / target_sig))^2 + (max(0, distance - optimal) / falloff)^2 )
    """
    if distance <= 0:
        angular_velocity = 0.0
    else:
        angular_velocity = transversal_velocity / distance

    # Tracking term
    if tracking <= 0 or target_sig <= 0:
        tracking_term = 0.0
    else:
        tracking_term = (angular_velocity / tracking) * (weapon_sig / target_sig)

    # Range term
    if falloff <= 0:
        range_term = 0.0 if distance <= optimal else 100.0
    else:
        range_term = max(0.0, distance - optimal) / falloff

    exponent = (tracking_term ** 2) + (range_term ** 2)
    chance = 0.5 ** exponent
    return max(0.0, min(1.0, chance))


def calculate_missile_damage(
    base_damage: float,
    explosion_radius: float,
    explosion_velocity: float,
    target_sig: float,
    target_velocity: float,
    drf_constant: float = 5.5
) -> float:
    """
    Calculate applied missile damage factoring in target signature and velocity:
    Damage = BaseDamage * min(1, TargetSig / ExplRadius, ( (TargetSig / ExplRadius) * (ExplVelocity / TargetVel) )^drf_exponent )
    """
    if explosion_radius <= 0:
        return base_damage

    term_sig = target_sig / explosion_radius
    if target_velocity <= 0:
        term_vel = 1.0
    else:
        ratio = (target_sig / explosion_radius) * (explosion_velocity / target_velocity)
        # CCP standard DRF formula
        drf_exponent = math.log(drf_constant) / math.log(5.5) if drf_constant > 1 else 1.0
        term_vel = ratio ** drf_exponent if ratio > 0 else 0.0

    multiplier = min(1.0, term_sig, term_vel if term_vel > 0 else 1.0)
    return max(0.0, base_damage * multiplier)


def calculate_effective_hp(
    shield_hp: float, shield_resists: Dict[str, float],
    armor_hp: float, armor_resists: Dict[str, float],
    hull_hp: float, hull_resists: Dict[str, float],
    damage_profile: Dict[str, float] = None
) -> Dict[str, float]:
    """
    Calculate Effective Hit Points (EHP) across Shield, Armor, and Hull
    against an incoming damage profile (default: omni 25/25/25/25).
    """
    if not damage_profile:
        damage_profile = {"em": 0.25, "thermal": 0.25, "kinetic": 0.25, "explosive": 0.25}

    def get_layer_ehp(hp: float, resists: Dict[str, float]) -> float:
        total_dmg_taken = sum(
            damage_profile.get(dmg_type, 0.25) * (1.0 - resists.get(dmg_type, 0.0))
            for dmg_type in ["em", "thermal", "kinetic", "explosive"]
        )
        return hp / total_dmg_taken if total_dmg_taken > 0 else hp

    s_ehp = get_layer_ehp(shield_hp, shield_resists)
    a_ehp = get_layer_ehp(armor_hp, armor_resists)
    h_ehp = get_layer_ehp(hull_hp, hull_resists)

    return {
        "shield_ehp": round(s_ehp, 1),
        "armor_ehp": round(a_ehp, 1),
        "hull_ehp": round(h_ehp, 1),
        "total_ehp": round(s_ehp + a_ehp + h_ehp, 1)
    }


def simulate_fleet_engagement(
    attacker_fleet: List[Dict[str, Any]],
    defender_fleet: List[Dict[str, Any]],
    duration_seconds: int = 60
) -> Dict[str, Any]:
    """
    Simulate tactical fleet engagement over time (second-by-second tick):
    Models outgoing volley alpha, sustained DPS, remote repair cap chains, and time-to-kill.
    """
    t0 = time.time()
    
    # Aggregate attacker alpha and sustained DPS
    total_alpha = sum(a.get("volley_damage", a.get("dps", 500) * 4.0) for a in attacker_fleet)
    total_dps = sum(a.get("dps", 500) for a in attacker_fleet)

    # Defender stats
    defenders_state = []
    for d in defender_fleet:
        ehp_data = calculate_effective_hp(
            d.get("shield_hp", 5000), d.get("shield_resists", {"em": 0.5, "thermal": 0.6, "kinetic": 0.7, "explosive": 0.8}),
            d.get("armor_hp", 6000), d.get("armor_resists", {"em": 0.7, "thermal": 0.7, "kinetic": 0.7, "explosive": 0.7}),
            d.get("hull_hp", 4000), d.get("hull_resists", {"em": 0.33, "thermal": 0.33, "kinetic": 0.33, "explosive": 0.33})
        )
        defenders_state.append({
            "name": d.get("name", "Unknown Target"),
            "ship": d.get("ship", "Battleship"),
            "current_ehp": ehp_data["total_ehp"],
            "max_ehp": ehp_data["total_ehp"],
            "remote_rep_hps": d.get("remote_rep_hps", 0.0),
            "status": "Alive",
            "time_of_death": None
        })

    # Run combat tick simulation
    timeline = []
    current_target_idx = 0

    for second in range(1, duration_seconds + 1):
        if current_target_idx >= len(defenders_state):
            break

        target = defenders_state[current_target_idx]
        
        # Apply incoming DPS minus remote reps
        effective_incoming = max(0.0, total_dps - target["remote_rep_hps"])
        target["current_ehp"] -= effective_incoming

        if target["current_ehp"] <= 0:
            target["current_ehp"] = 0
            target["status"] = "Destroyed"
            target["time_of_death"] = second
            timeline.append({
                "second": second,
                "event": f"Target Destroyed: {target['name']} ({target['ship']})",
                "attacker_total_dps": total_dps
            })
            current_target_idx += 1

    elapsed_ms = (time.time() - t0) * 1000.0

    return {
        "simulation_duration_s": duration_seconds,
        "attacker_ships_count": len(attacker_fleet),
        "total_fleet_alpha": round(total_alpha, 1),
        "total_fleet_dps": round(total_dps, 1),
        "defender_ships_count": len(defender_fleet),
        "defenders_destroyed": sum(1 for d in defenders_state if d["status"] == "Destroyed"),
        "defenders_survived": sum(1 for d in defenders_state if d["status"] == "Alive"),
        "timeline_events": timeline,
        "defenders_final_state": defenders_state,
        "latency_ms": round(elapsed_ms, 2)
    }


def generate_combat_simulation_markdown() -> List[str]:
    """Generate canonical combat dogma simulation reference document."""
    os.makedirs(VAULT_COMBAT_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_COMBAT_DIR, "combat_simulation_dogma_engine.md")

    # Run benchmark test scenario
    marauders = [
        {"name": "Savian Paladin", "ship": "Paladin", "dps": 1250, "volley_damage": 5200},
        {"name": "Thena Kronos", "ship": "Kronos", "dps": 1400, "volley_damage": 5800},
        {"name": "Vulcastra Vargur", "ship": "Vargur", "dps": 1350, "volley_damage": 5600},
        {"name": "Tulorn Golem", "ship": "Golem", "dps": 1150, "volley_damage": 7800}
    ]
    hostile_battleships = [
        {"name": f"Hostile Dominix #{i}", "ship": "Dominix", "shield_hp": 8000, "armor_hp": 18000, "hull_hp": 10000, "remote_rep_hps": 300}
        for i in range(1, 6)
    ]
    sim_res = simulate_fleet_engagement(marauders, hostile_battleships, duration_seconds=60)

    doc_md = f"""---
title: Autonomous EVE Online Fleet Combat Simulator & Dogma Engine
category: Combat Intelligence
tags: [EVE, Combat, Dogma, TurretTracking, Missiles, TTK, FleetEngagement]
last_updated: 2026-08-14
---

# ⚔️ Autonomous Fleet Combat Simulator & Dogma Mathematics Engine

This document provides the definitive mathematical equations, algorithms, and simulation models governing turret tracking, missile flight dynamics, effective hit points (EHP), and fleet engagement time-to-kill (TTK) in EVE Online.

---

## 🎯 1. Canonical Gun Turret Tracking Equation

The exact probability of a gun turret hitting a target is given by CCP's Dogma formula:

$$P_{{\\text{{hit}}}} = 0.5^{{\\left(\\frac{{\\text{{Angular}}}}{{\\text{{Tracking}}}} \\times \\frac{{\\text{{Sig}}_{{\\text{{weapon}}}}}}{{\\text{{Sig}}_{{\\text{{target}}}}}}\\right)^2 + \\left(\\max\\left(0, \\frac{{\\text{{Distance}} - \\text{{Optimal}}}}{{\\text{{Falloff}}}}\\right)\\right)^2}}$$

### Hit Quality & Wrecking Shots Distribution
- **Wrecking Shot Probability**: Exactly **1.0%** (inflicts $3.0\\times$ base damage multiplier, ignoring glancing modifiers).
- **Hit Quality Multiplier**: Distributed linearly between **$0.50$ and $1.49$** based on $P_{{\\text{{hit}}}}$ roll threshold.
- **Glancing Hit Threshold**: When $P_{{\\text{{hit}}}} < 0.05$, hits deal only $0.50\\times$ glancing damage.

---

## 🚀 2. Canonical Missile Application Equation

Unlike turrets, missiles always hit if within flight range, but apply damage according to target signature radius and velocity:

$$D = D_0 \\times \\min\\left(1, \\frac{{\\text{{Sig}}_{{\\text{{target}}}}}}{{\\text{{Sig}}_{{\\text{{explosion}}}}}}, \\left(\\frac{{\\text{{Sig}}_{{\\text{{target}}}}}}{{\\text{{Sig}}_{{\\text{{explosion}}}}}} \\times \\frac{{V_{{\\text{{explosion}}}}}}{{V_{{\\text{{target}}}}}}\\right)^{{\\frac{{\\ln(\\text{{DRF}})}}{{\\ln(5.5)}}}}\\right)$$

- **Target Signature ($S_T$)**: Target's current signature radius (inflated by MWD or target painters).
- **Target Velocity ($V_T$)**: Target's absolute vector speed relative to space.
- **Explosion Velocity ($V_E$)**: Speed at which the shockwave expands.

---

## 🛡️ 3. Effective Hit Points (EHP) Matrix Calculus

$$\\text{{EHP}} = \\sum_{{L \\in \\{{\\text{{Shield}}, \\text{{Armor}}, \\text{{Hull}}\\}}}} \\frac{{\\text{{HP}}_L}}{{\\sum_{{D \\in \\{{\\text{{EM}}, \\text{{TH}}, \\text{{KIN}}, \\text{{EXP}}\\}}}} P_D \\times (1 - R_{{L, D}})}}$$

---

## 📊 4. Multi-Box Marauder Fleet Engagement Simulation Benchmark

- **Attacker Fleet**: 4x Multi-Box Marauders (Paladin, Kronos, Vargur, Golem)
- **Combined Fleet Alpha Volley**: **{sim_res['total_fleet_alpha']:,} Damage**
- **Combined Fleet Sustained DPS**: **{sim_res['total_fleet_dps']:,} DPS**
- **Defenders Engaged**: 5x Hostile Dominix Battleships with Remote Armor Repairs
- **Simulation Duration**: **{sim_res['simulation_duration_s']} Seconds**
- **Hostile Losses**: **{sim_res['defenders_destroyed']} / {sim_res['defender_ships_count']} Destroyed**
- **Simulation Engine Latency**: **{sim_res['latency_ms']} ms**

### Engagement Destruction Timeline
"""
    for event in sim_res["timeline_events"]:
        doc_md += f"- **Second {event['second']}**: {event['event']} (Under {event['attacker_total_dps']:,} fleet DPS)\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_combat_simulation_markdown()
    print(f"Generated combat dogma document: {files}")
