"""
Autonomous EVE Online Celestial & Exotic Space Systems Engine (Wormholes, Pochven & Thera).
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Zero external dependencies, exact J-space mass and Pochven clade math.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_WH_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Wormhole_Pochven")

WORMHOLE_EFFECTS = {
    "Pulsar": {
        "shield_hp_bonus": "+100%",
        "cap_recharge_bonus": "+100%",
        "armor_resist_penalty": "-50% EM",
        "signature_radius_penalty": "+100%",
        "doctrine_focus": "Shield Tanking Missiles / Drones"
    },
    "Magnetar": {
        "damage_bonus": "+100% (Turrets & Missiles)",
        "missile_explosion_radius": "+50%",
        "tracking_speed_penalty": "-50%",
        "targeting_range_penalty": "-50%",
        "doctrine_focus": "High-Alpha Artillery / Dreadnought Blasters"
    },
    "Wolf-Rayet": {
        "armor_hp_bonus": "+100%",
        "small_weapon_damage": "+100%",
        "shield_resist_penalty": "-50%",
        "signature_radius_bonus": "-50%",
        "doctrine_focus": "Armor T3 Destroyers (Confessor / Svipul / Hecate)"
    },
    "Black Hole": {
        "missile_velocity_bonus": "+100%",
        "ship_velocity_bonus": "+100%",
        "inertia_modifier_penalty": "+100% (Slow Align)",
        "targeting_range_bonus": "+100%",
        "doctrine_focus": "Kiting Long-Range Cruisers / Interceptors"
    },
    "Red Giant": {
        "heat_damage_penalty": "+100%",
        "overload_bonus": "+100%",
        "smartbomb_range_bonus": "+100%",
        "smartbomb_damage_bonus": "+100%",
        "doctrine_focus": "Pipe-Bombing Battleships / Overheated Brawlers"
    },
    "Cataclysmic Variable": {
        "remote_armor_repair_bonus": "+100%",
        "remote_shield_transfer_bonus": "+100%",
        "local_repair_penalty": "-50%",
        "cap_transfer_bonus": "+100%",
        "doctrine_focus": "Spider-Tanked Battleships / Nestor Cap Chains"
    }
}

POCHVEN_SYSTEMS = {
    "Svarog Clade": ["Arche", "Kuharah", "Nalvula", "Raravoss", "Sakenta", "Skarkon", "Urghas", "Vale", "Wirflai"],
    "Dazh Clade": ["Angoff", "Harva", "Ichoriya", "Kinnakka", "Konotoka", "Otela", "Preset", "Senda", "Tunudan"],
    "Veles Clade": ["Ala", "Archee", "Arvasaras", "Ahtila", "Ignebaer", "Kaunid", "Niarja", "Pochven Core", "Terramon"]
}


def calculate_wormhole_mass_state(
    total_capacity_gg: float = 3000.0,
    max_jump_mass_gg: float = 300.0,
    mass_jumped_gg: float = 1650.0
) -> Dict[str, Any]:
    """
    Calculate wormhole remaining mass, stability stage, and collapse risk.
    1 Gg = 1,000 Metric Tonnes = 1,000,000 kg.
    """
    remaining_mass = max(0.0, total_capacity_gg - mass_jumped_gg)
    percent_remaining = (remaining_mass / total_capacity_gg) * 100.0

    if percent_remaining > 50.0:
        stage = "Stage 1: Stable / Healthy (>50% mass remaining)"
        state_code = "STABLE"
    elif percent_remaining > 10.0:
        stage = "Stage 2: Destabilized (Has had its stability reduced, but not to a critical degree)"
        state_code = "DESTABILIZED"
    else:
        stage = "Stage 3: Critical (Approaching the brink of collapse, <10% remaining)"
        state_code = "CRITICAL"

    max_battleships_remaining = int(remaining_mass / max_jump_mass_gg)

    return {
        "total_capacity_gg": total_capacity_gg,
        "max_single_jump_mass_gg": max_jump_mass_gg,
        "total_mass_jumped_gg": mass_jumped_gg,
        "remaining_mass_gg": round(remaining_mass, 1),
        "percent_remaining": round(percent_remaining, 1),
        "stability_stage": stage,
        "stability_code": state_code,
        "battleship_passes_remaining": max_battleships_remaining,
        "safe_to_pass_capital": remaining_mass >= 1000.0 and max_jump_mass_gg >= 1000.0
    }


def calculate_pochven_ofp_yield(
    pilots_in_fleet: int = 15,
    sites_per_hour: float = 2.0
) -> Dict[str, Any]:
    """Calculate Observatory Flashpoint (OFP) ISK/LP payout split in Pochven."""
    total_site_isk = 3500000000.0  # 3.5 Billion ISK gross payout
    total_site_lp = 150000.0  # 150,000 Dazh/Veles LP

    isk_per_pilot = total_site_isk / max(1, min(15, pilots_in_fleet))
    lp_per_pilot = total_site_lp / max(1, min(15, pilots_in_fleet))

    hourly_isk_per_pilot = isk_per_pilot * sites_per_hour
    hourly_lp_per_pilot = lp_per_pilot * sites_per_hour

    return {
        "site_name": "Triglavian Observatory Flashpoint (OFP)",
        "fleet_size": pilots_in_fleet,
        "sites_per_hour": sites_per_hour,
        "isk_per_pilot_per_site": round(isk_per_pilot, 2),
        "lp_per_pilot_per_site": round(lp_per_pilot, 0),
        "hourly_isk_per_pilot_m": round(hourly_isk_per_pilot / 1000000.0, 1),
        "hourly_isk_per_pilot_b": round(hourly_isk_per_pilot / 1000000000.0, 2),
        "hourly_lp_per_pilot": round(hourly_lp_per_pilot, 0)
    }


def generate_celestial_markdown() -> List[str]:
    """Generate Wormhole J-Space & Pochven reference document."""
    os.makedirs(VAULT_WH_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_WH_DIR, "wormhole_pochven_celestials.md")

    wh_calc = calculate_wormhole_mass_state(total_capacity_gg=3200.0, max_jump_mass_gg=300.0, mass_jumped_gg=2400.0)
    ofp_calc = calculate_pochven_ofp_yield(pilots_in_fleet=15, sites_per_hour=2.0)

    doc_md = f"""---
title: Autonomous EVE Online Wormhole J-Space Dynamics & Pochven Triangle Economy
category: Celestial Space Intelligence
tags: [EVE, Wormholes, JSpace, MassLimits, EnvironmentalPhenomena, Pochven, Triglavian, OFP, Thera]
last_updated: 2026-08-14
---

# 🌌 Autonomous Wormhole J-Space Dynamics & Pochven Triangle Economy

This document provides the canonical mass calculation mechanics, spatial environmental multipliers, and Pochven Triglavian economy models.

---

## 🌀 1. Wormhole Mass Lifecycle & Rolling Calculus
- **Wormhole Total Mass**: **{wh_calc['total_capacity_gg']:,} Gg (3.2 Million Tonnes)**
- **Mass Jumped**: **{wh_calc['total_mass_jumped_gg']:,} Gg**
- **Remaining Mass Capacity**: **{wh_calc['remaining_mass_gg']:,} Gg ({wh_calc['percent_remaining']}%)**
- **Stability State**: **`{wh_calc['stability_stage']}`**
- **Battleship Passes Remaining**: **~{wh_calc['battleship_passes_remaining']} Passes** (Assuming 300 Gg Higg-rigged Battleships)

---

## ⚡ 2. J-Space Environmental Phenomena Multipliers

| Wormhole Effect | Primary Stat Buff | Secondary Penalty | Optimal Fleet Doctrine |
| :--- | :--- | :--- | :--- |
| **Pulsar** | **+100% Shield HP, +100% Cap Recharge** | -50% EM Armor, +100% Sig Radius | Shield Brawlers / Passive Gila |
| **Magnetar** | **+100% Turret & Missile Damage** | -50% Tracking, -50% Lock Range | Heavy Artillery Alpha / Blaster Dreads |
| **Wolf-Rayet** | **+100% Armor HP, +100% Small Weapons** | -50% Shield Resists, -50% Sig | Armor T3 Destroyers (Confessor / Hecate) |
| **Black Hole** | **+100% Ship & Missile Velocity** | +100% Inertia (Slow Align) | Nano-Kiting Cruisers / Interceptors |
| **Red Giant** | **+100% Overload Bonus, +100% Smartbombs** | +100% Heat Damage | Pipe-Bombing Battleships |
| **Cataclysmic** | **+100% Remote Shield/Armor Reps** | -50% Local Reps | Nestor / Spider-Tanked Cap Chains |

---

## 🔺 3. Pochven Triangle Economy & Observatory Flashpoints (OFP)
- **The 27 Systems**: Divided across **Svarog Clade**, **Dazh Clade**, and **Veles Clade**.
- **Observatory Flashpoint Site Payout**: **{ofp_calc['isk_per_pilot_per_site']:,.2f} ISK + {ofp_calc['lp_per_pilot_per_site']:,.0f} LP per Pilot**.
- **Fleet Hourly Income (2 Sites/hr)**: **{ofp_calc['hourly_isk_per_pilot_m']}M ISK/hr ({ofp_calc['hourly_isk_per_pilot_b']}B ISK/hr)** per pilot.
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_celestial_markdown()
    print(f"Generated celestial document: {files}")
