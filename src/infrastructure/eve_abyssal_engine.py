"""
Autonomous EVE Online Abyssal Deadspace T1-T6 & Mutaplasmid Simulation Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time, random).
Ponytail Senior Dev Principle: Zero external pip dependencies, exact canonical weather matrices.
"""

import os
import sys
import math
import json
import time
import random
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_ABYSSAL_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Abyssal_Deadspace")

ABYSSAL_WEATHER_MODIFIERS = {
    "Electrical": {
        "penalty_resist": "EM",
        "penalty_amount": -0.50,
        "bonus_attribute": "Capacitor Recharge Rate",
        "bonus_amount": +0.50,
        "recommended_ships": ["Gila", "Cerberus", "Sacrilege", "Phantasm"]
    },
    "Exotic": {
        "penalty_resist": "Kinetic",
        "penalty_amount": -0.50,
        "bonus_attribute": "Scan Resolution",
        "bonus_amount": +0.50,
        "recommended_ships": ["Gila", "Cerberus", "Ikitursa", "Vagabond"]
    },
    "Firestorm": {
        "penalty_resist": "Thermal",
        "penalty_amount": -0.50,
        "bonus_attribute": "Armor Hit Points",
        "bonus_amount": +0.50,
        "recommended_ships": ["Sacrilege", "Zealot", "Deimos", "Phantasm"]
    },
    "Gamma": {
        "penalty_resist": "Explosive",
        "penalty_amount": -0.50,
        "bonus_attribute": "Shield Hit Points",
        "bonus_amount": +0.50,
        "recommended_ships": ["Gila", "Cerberus", "Vagabond", "Muninn"]
    },
    "Dark": {
        "penalty_resist": "None",
        "penalty_amount": 0.0,
        "bonus_attribute": "Max Velocity",
        "bonus_amount": +0.50,
        "secondary_penalty": "Turret & Missile Range -50%",
        "recommended_ships": ["Cerberus (Heavy Missile)", "Gila (Drones)", "Sacrilege (Heavy Assault Missile)"]
    }
}

FILAMENT_TIERS = {
    1: {"name": "Calm", "danger_level": "Low", "loot_multiplier": 1.0, "avg_isk_per_run_m": 5.0},
    2: {"name": "Agitated", "danger_level": "Medium-Low", "loot_multiplier": 1.8, "avg_isk_per_run_m": 15.0},
    3: {"name": "Fierce", "danger_level": "Medium", "loot_multiplier": 3.2, "avg_isk_per_run_m": 35.0},
    4: {"name": "Raging", "danger_level": "High", "loot_multiplier": 6.5, "avg_isk_per_run_m": 85.0},
    5: {"name": "Chaotic", "danger_level": "Very High", "loot_multiplier": 12.0, "avg_isk_per_run_m": 180.0},
    6: {"name": "Abyssal", "danger_level": "Extreme / Lethal", "loot_multiplier": 24.0, "avg_isk_per_run_m": 450.0}
}


def simulate_mutaplasmid_roll(
    module_name: str,
    mutaplasmid_tier: str = "Unstable",
    attributes: Dict[str, Tuple[float, float, float]] = None,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Simulate Mutaplasmid stat mutation roll.
    Attributes dictionary maps attr_name -> (base_val, min_mult, max_mult).
    """
    rng = random.Random(seed) if seed is not None else random

    if not attributes:
        # Default: Unstable 50MN Microwarpdrive mutation attributes
        attributes = {
            "Speed Boost Multiplier": (5.0, 0.85, 1.35),
            "Capacitor Need (GJ)": (145.0, 0.70, 1.40),
            "Activation Cost (MW)": (125.0, 0.75, 1.30),
            "CPU Usage (tf)": (35.0, 0.75, 1.30),
            "Signature Radius Penalty (%)": (500.0, 0.75, 1.30)
        }

    rolls = {}
    total_rating = 0.0

    for attr, (base, min_m, max_m) in attributes.items():
        roll_mult = rng.uniform(min_m, max_m)
        mutated_val = base * roll_mult
        percent_change = (roll_mult - 1.0) * 100.0
        rolls[attr] = {
            "base_value": base,
            "mutated_value": round(mutated_val, 2),
            "multiplier": round(roll_mult, 4),
            "percent_change": f"{percent_change:+.1f}%"
        }
        total_rating += roll_mult

    avg_roll = total_rating / len(attributes)
    quality = "God Roll" if avg_roll > 1.15 else "Brick Roll" if avg_roll < 0.90 else "Usable Mutation"

    return {
        "module_name": module_name,
        "mutaplasmid_tier": mutaplasmid_tier,
        "mutation_quality": quality,
        "average_multiplier": round(avg_roll, 4),
        "attribute_rolls": rolls
    }


def calculate_abyssal_isk_yield(
    tier: int = 6,
    weather: str = "Gamma",
    runs_per_hour: float = 3.0
) -> Dict[str, Any]:
    """Calculate hourly ISK, filament cost, and net profit for Abyssal Deadspace operations."""
    tier_info = FILAMENT_TIERS.get(tier, FILAMENT_TIERS[6])
    weather_info = ABYSSAL_WEATHER_MODIFIERS.get(weather, ABYSSAL_WEATHER_MODIFIERS["Gamma"])

    gross_loot_per_run_m = tier_info["avg_isk_per_run_m"]
    filament_cost_m = 15.0 if tier == 6 else 8.0 if tier == 5 else 3.0
    net_profit_per_run_m = gross_loot_per_run_m - filament_cost_m

    hourly_gross_m = gross_loot_per_run_m * runs_per_hour
    hourly_net_m = net_profit_per_run_m * runs_per_hour

    return {
        "tier": tier,
        "tier_name": tier_info["name"],
        "weather_type": weather,
        "danger_level": tier_info["danger_level"],
        "penalty_resist": weather_info["penalty_resist"],
        "bonus_attribute": weather_info["bonus_attribute"],
        "runs_per_hour": runs_per_hour,
        "gross_per_run_m": gross_loot_per_run_m,
        "net_profit_per_run_m": net_profit_per_run_m,
        "hourly_net_profit_m": round(hourly_net_m, 1),
        "hourly_net_profit_b": round(hourly_net_m / 1000.0, 2),
        "recommended_ships": weather_info["recommended_ships"]
    }


def generate_abyssal_markdown() -> List[str]:
    """Generate Abyssal Deadspace mechanics and Mutaplasmid reference document."""
    os.makedirs(VAULT_ABYSSAL_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_ABYSSAL_DIR, "abyssal_tier_weather_mutaplasmids.md")

    t6_calc = calculate_abyssal_isk_yield(tier=6, weather="Gamma", runs_per_hour=3.0)
    muta_sample = simulate_mutaplasmid_roll("50MN Digital Booster Microwarpdrive", "Unstable")

    doc_md = f"""---
title: Autonomous EVE Online Abyssal Deadspace T1-T6 & Mutaplasmid Matrix
category: Abyssal Deadspace
tags: [EVE, AbyssalDeadspace, Filaments, Weather, Mutaplasmids, T6Abyss, Triglavian, ISK]
last_updated: 2026-08-14
---

# 🌀 Autonomous Abyssal Deadspace T1-T6 & Mutaplasmid Simulation Engine

This document establishes the tactical rules, environmental weather modifiers, pocket spawns, and Mutaplasmid RNG mechanics for Abyssal Deadspace operations.

---

## ⚡ 1. Environmental Weather Matrix

| Weather Type | Primary Resist Penalty | Environmental Buff Multiplier | Top Recommended Hulls |
| :--- | :---: | :---: | :--- |
| **Electrical** | **-50.0% EM Resist** | **+50% Capacitor Recharge** | Gila, Cerberus, Sacrilege, Phantasm |
| **Exotic** | **-50.0% Kinetic Resist** | **+50% Scan Resolution** | Gila, Cerberus, Ikitursa, Vagabond |
| **Firestorm** | **-50.0% Thermal Resist** | **+50% Armor Hit Points** | Sacrilege, Zealot, Deimos, Phantasm |
| **Gamma** | **-50.0% Explosive Resist** | **+50% Shield Hit Points** | Gila, Cerberus, Vagabond, Muninn |
| **Dark** | **0.0% (None)** | **+50% Max Velocity** (-50% Range) | Cerberus (HML), Sacrilege (HAM), Gila |

---

## 💎 2. Filament Tiers & Economics (20-Minute Hard Timer)

| Tier | Name | Threat Level | Gross Loot / Run | Net Hourly Profit (3 Runs/hr) |
| :---: | :--- | :--- | :---: | :---: |
| **T1** | **Calm** | Low | 5.0M ISK | ~15.0M ISK/hr |
| **T2** | **Agitated** | Medium-Low | 15.0M ISK | ~45.0M ISK/hr |
| **T3** | **Fierce** | Medium | 35.0M ISK | ~100.0M ISK/hr |
| **T4** | **Raging** | High | 85.0M ISK | ~240.0M ISK/hr |
| **T5** | **Chaotic** | Very High | 180.0M ISK | ~515.0M ISK/hr |
| **T6** | **Abyssal** | Extreme / Lethal | **450.0M ISK** | **~1.305 Billion ISK/hr** |

---

## 🧬 3. Mutaplasmid RNG Mutation Model (Sample Unstable Roll)
- **Module**: `{muta_sample['module_name']}`
- **Mutaplasmid Tier**: `{muta_sample['mutaplasmid_tier']}`
- **Outcome Assessment**: `{muta_sample['mutation_quality']}` (Score: `{muta_sample['average_multiplier']}`)

### Mutated Attribute Breakdown
"""
    for attr, r in muta_sample["attribute_rolls"].items():
        doc_md += f"- **{attr}**: Base `{r['base_value']}` $\\rightarrow$ Mutated **`{r['mutated_value']}`** (`{r['percent_change']}`)\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_abyssal_markdown()
    print(f"Generated abyssal document: {files}")
