"""
Autonomous EVE Online Supercapital Warfare & Doomsday AoE Simulation Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact canonical Doomsday damage equations and FAX Triage cycles.
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

VAULT_SUPERCAP_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Supercapital_Warfare")

TITAN_DOOMSDAYS = {
    "Judgement (Avatar)": {
        "damage_type": "EM",
        "damage_amount": 2500000,
        "mechanism": "Directed Single-Target",
        "signature_radius": 2000,
        "cycle_time_s": 30,
        "cooldown_s": 300,
        "fuel_cost": "Strontium Clathrates x 5000"
    },
    "Aurora OMR (Leviathan)": {
        "damage_type": "Kinetic",
        "damage_amount": 2500000,
        "mechanism": "Directed Single-Target",
        "signature_radius": 2000,
        "cycle_time_s": 30,
        "cooldown_s": 300,
        "fuel_cost": "Strontium Clathrates x 5000"
    },
    "Oblivion (Erebus)": {
        "damage_type": "Thermal",
        "damage_amount": 2500000,
        "mechanism": "Directed Single-Target",
        "signature_radius": 2000,
        "cycle_time_s": 30,
        "cooldown_s": 300,
        "fuel_cost": "Strontium Clathrates x 5000"
    },
    "Gjallarhorn (Ragnarok)": {
        "damage_type": "Explosive",
        "damage_amount": 2500000,
        "mechanism": "Directed Single-Target",
        "signature_radius": 2000,
        "cycle_time_s": 30,
        "cooldown_s": 300,
        "fuel_cost": "Strontium Clathrates x 5000"
    },
    "Bosonic Field Generator (AoE)": {
        "damage_type": "Omni (25/25/25/25)",
        "damage_amount": 1200000,
        "mechanism": "Directional AoE Cone (30km width, 200km length)",
        "signature_radius": 500,
        "cycle_time_s": 30,
        "cooldown_s": 300,
        "fuel_cost": "Strontium Clathrates x 7500"
    }
}

SUPERCARRIER_HULLS = {
    "Aeon (Amarr)": {"fighter_tubes": 5, "heavy_fighter_slots": 3, "tank_ehp_m": 42.5, "dps": 4800},
    "Wyvern (Caldari)": {"fighter_tubes": 5, "heavy_fighter_slots": 3, "tank_ehp_m": 45.0, "dps": 4600},
    "Nyx (Gallente)": {"fighter_tubes": 5, "heavy_fighter_slots": 3, "tank_ehp_m": 38.0, "dps": 5400},
    "Hel (Minmatar)": {"fighter_tubes": 5, "heavy_fighter_slots": 3, "tank_ehp_m": 39.5, "dps": 5100}
}


def calculate_doomsday_applied_damage(
    doomsday_name: str,
    target_sig_radius: float,
    target_resist: float = 0.70,
    distance_km: float = 50.0
) -> Dict[str, Any]:
    """
    Calculate applied Doomsday damage after target signature scaling and resists.
    """
    dd = TITAN_DOOMSDAYS.get(doomsday_name, TITAN_DOOMSDAYS["Judgement (Avatar)"])
    base_dmg = dd["damage_amount"]
    weapon_sig = dd["signature_radius"]

    # Signature application factor
    sig_ratio = min(1.0, target_sig_radius / weapon_sig)
    applied_raw = base_dmg * sig_ratio
    applied_effective = applied_raw * (1.0 - target_resist)

    return {
        "doomsday": doomsday_name,
        "target_signature_m": target_sig_radius,
        "target_resist_percent": round(target_resist * 100, 1),
        "raw_doomsday_damage": base_dmg,
        "applied_raw_damage": round(applied_raw, 1),
        "effective_damage_taken": round(applied_effective, 1),
        "target_destroyed_subcapital": target_sig_radius < 500 and applied_effective > 150000
    }


def simulate_fax_triage_cycle(
    fax_type: str = "Apostle (Amarr)",
    triage_cycles: int = 3,
    hostile_neut_dps_gj: float = 1200.0,
    cap_booster_charges_3200: int = 12
) -> Dict[str, Any]:
    """
    Simulate Force Auxiliary (FAX) Triage capacitor stability under hostile heavy energy neutralizing pressure.
    """
    cycle_time_s = 300  # 5 minutes per Triage cycle
    total_time_s = cycle_time_s * triage_cycles

    # Base Apostle capacitor stats
    base_cap_gj = 75000.0
    cap_recharge_rate_s = 380.0
    remote_rep_cap_cost_gj_per_s = 180.0
    local_rep_cap_cost_gj_per_s = 140.0

    total_natural_recharge = cap_recharge_rate_s * total_time_s
    total_cap_injected = cap_booster_charges_3200 * 3200.0
    total_cap_drained = hostile_neut_dps_gj * total_time_s
    total_cap_consumed = (remote_rep_cap_cost_gj_per_s + local_rep_cap_cost_gj_per_s) * total_time_s

    net_cap_balance = base_cap_gj + total_natural_recharge + total_cap_injected - (total_cap_drained + total_cap_consumed)
    cap_stable = net_cap_balance > 0

    return {
        "fax_hull": fax_type,
        "triage_cycles": triage_cycles,
        "total_triage_duration_min": (total_time_s / 60.0),
        "base_capacitor_gj": base_cap_gj,
        "total_cap_injected_gj": total_cap_injected,
        "total_hostile_neut_drained_gj": total_cap_drained,
        "total_rep_cap_consumed_gj": total_cap_consumed,
        "net_capacitor_remaining_gj": round(max(0, net_cap_balance), 1),
        "triage_capacitor_stability": "STABLE" if cap_stable else "CAPACITOR_DEPLETED"
    }


def generate_supercapital_markdown() -> List[str]:
    """Generate Supercapital Warfare & Doomsday reference document."""
    os.makedirs(VAULT_SUPERCAP_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_SUPERCAP_DIR, "supercapital_doomsday_fighters.md")

    dd_titan_vs_dread = calculate_doomsday_applied_damage("Judgement (Avatar)", target_sig_radius=2200, target_resist=0.75)
    dd_boson_vs_fleet = calculate_doomsday_applied_damage("Bosonic Field Generator (AoE)", target_sig_radius=350, target_resist=0.60)
    fax_sim = simulate_fax_triage_cycle("Apostle (Amarr)", triage_cycles=2, hostile_neut_dps_gj=800.0, cap_booster_charges_3200=16)

    doc_md = f"""---
title: Autonomous EVE Online Supercapital Warfare & Doomsday AoE Engine
category: Supercapital Warfare
tags: [EVE, Supercapitals, Titans, Supercarriers, Doomsday, FAX, TriageMode, FleetEHP]
last_updated: 2026-08-14
---

# 👑 Autonomous Supercapital Warfare & Doomsday AoE Simulation Engine

This document provides the strategic combat equations, Doomsday signature scaling calculations, Supercarrier fighter wing DPS profiles, and FAX Triage capacitor stability models.

---

## ⚡ 1. Titan Doomsday Weapons Matrix

| Doomsday Device | Hull Class | Damage Type | Alpha Damage | Mechanism |
| :--- | :--- | :---: | :---: | :--- |
| **Judgement** | **Avatar (Amarr)** | **EM** | **2,500,000** | Directed Target Beam |
| **Aurora OMR** | **Leviathan (Caldari)** | **Kinetic** | **2,500,000** | Directed Kinetic Torpedo |
| **Oblivion** | **Erebus (Gallente)** | **Thermal** | **2,500,000** | Directed Plasma Blast |
| **Gjallarhorn** | **Ragnarok (Minmatar)** | **Explosive** | **2,500,000** | Directed Shockwave |
| **Bosonic Field Generator** | **All Titans** | **Omni** | **1,200,000** | **Directional AoE Cone (30km $\\times$ 200km)** |

---

## 🦅 2. Supercarrier Fleet Wings & Fighter Burst DPS

| Supercarrier | Empire | Fighter Tubes | Heavy Bomber Wings | Sustained DPS | Base Tank EHP |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Aeon** | Amarr | 5 Tubes | 3 Heavy Squadrons | **4,800 DPS** | **42.5M Armor EHP** |
| **Wyvern** | Caldari | 5 Tubes | 3 Heavy Squadrons | **4,600 DPS** | **45.0M Shield EHP** |
| **Nyx** | Gallente | 5 Tubes | 3 Heavy Squadrons | **5,400 DPS** | **38.0M Armor EHP** |
| **Hel** | Minmatar | 5 Tubes | 3 Heavy Squadrons | **5,100 DPS** | **39.5M Shield EHP** |

---

## 🚑 3. Force Auxiliary (FAX) Triage Mode Stability Benchmark
- **Hull**: `{fax_sim['fax_hull']}`
- **Triage Duration**: **{fax_sim['total_triage_duration_min']} Minutes ({fax_sim['triage_cycles']} Cycles)**
- **Hostile Energy Draining Pressure**: **{fax_sim['total_hostile_neut_drained_gj']:,} GJ**
- **Capacitor Boosters Injected**: **{fax_sim['total_cap_injected_gj']:,} GJ (16x Cap Booster 3200)**
- **Capacitor Stability Status**: **`{fax_sim['triage_capacitor_stability']}`** (Remaining: `{fax_sim['net_capacitor_remaining_gj']:,} GJ`)
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_supercapital_markdown()
    print(f"Generated supercapital document: {files}")
