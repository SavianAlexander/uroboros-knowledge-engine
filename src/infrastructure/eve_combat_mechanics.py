"""
EVE Online Combat Mechanics, Implant Sets, Damage Mathematics & EWAR Engine.

Exhaustive references for:
- Pirate Implant Sets (High-Grade / Mid-Grade / Low-Grade) & Combat Synapse Boosters
- Gun Turret Tracking & Missile Explosion Velocity / Signature Radius Damage Mathematics
- Electronic Warfare (EWAR) Systems (ECM, Sensor Dampeners, Tracking Disruptors, Target Painters, Neut/Nos)

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time).
"""

import os
import sys
import json
import time

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
COMBAT_DIR = os.path.join(VAULT_EVE_DIR, "Combat_Mechanics")

IMPLANT_SETS = [
    {"name": "High-Grade Snake", "bonus": "+24.7% Sub-warp Velocity", "set_effect": "Increases ship max velocity", "primary_use": "Kiting Cruisers, Fast Interceptors, Nanogang"},
    {"name": "High-Grade Nirvana", "bonus": "+53.6% Shield Hitpoints", "set_effect": "Massive shield pool scaling", "primary_use": "Shield Capitals, Caldari Heavy Assault Cruisers, Rorqual"},
    {"name": "High-Grade Amulet", "bonus": "+53.6% Armor Hitpoints", "set_effect": "Massive armor buffer scaling", "primary_use": "Armor Capitals, Marauders, Heavy Armor Fleet Doctrines"},
    {"name": "High-Grade Ascendancy", "bonus": "+62.5% Warp Speed & Acceleration", "set_effect": "Drastically increases warp velocity", "primary_use": "Blockade Runners, Jump Freighters, Interceptors, Travel Clones"},
    {"name": "High-Grade Hydra", "bonus": "+15.3% Drone & Missile Damage / Range", "set_effect": "Dual weapon system optimization", "primary_use": "Gila, Cerberus, Rattlesnake, Worm"},
    {"name": "High-Grade Talisman", "bonus": "-27.1% Energy Neutralizer Duration", "set_effect": "Rapid capacitor neut cycle rate", "primary_use": "Bhaalgorn, Curse, Armageddon, Energy Warfare"},
    {"name": "High-Grade Virtue", "bonus": "+44.1% Scan Probe Strength", "set_effect": "Pinpoints combat targets instantly", "primary_use": "Combat Probing, Covert Ops, Fleet Scout Hunters"}
]

COMBAT_DRUGS = [
    {"name": "Synth / Standard / Strong Exile", "boost": "+20% to +30% Armor Repair Amount", "penalty": "Capacitor capacity / Turret tracking penalty", "optimal_use": "Active Armor Marauders & Brawlers"},
    {"name": "Synth / Standard / Strong Blue Pill", "boost": "+20% to +30% Shield Boost Amount", "penalty": "Shield capacity / Missile explosion radius penalty", "optimal_use": "Active Shield Marauders & Logi"},
    {"name": "Synth / Standard / Strong Crash", "boost": "-20% to -30% Missile Explosion Radius", "penalty": "Armor hitpoints / Shield boost penalty", "optimal_use": "Heavy Missile & HAM Cruisers"},
    {"name": "Synth / Standard / Strong Drop", "boost": "+25% to +37% Turret Tracking Speed", "penalty": "Armor repair amount / Falloff penalty", "optimal_use": "Blaster / Autocannon Gunships"},
    {"name": "Synth / Standard / Strong Mindflood", "boost": "+20% to +30% Capacitor Capacity", "penalty": "Armor resist / Explosion velocity penalty", "optimal_use": "Logistics Cruisers & Capital FAX"}
]


def generate_combat_mechanics_markdown(output_dir: str = COMBAT_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. IMPLANTS & BOOSTERS MATRIX
    imp_rows = []
    for imp in IMPLANT_SETS:
        imp_rows.append(f"| **{imp['name']}** | `{imp['bonus']}` | {imp['set_effect']} | **{imp['primary_use']}** |")

    drug_rows = []
    for d in COMBAT_DRUGS:
        drug_rows.append(f"| **{d['name']}** | `{d['boost']}` | {d['penalty']} | **{d['optimal_use']}** |")

    imp_table = "\n".join(imp_rows)
    drug_table = "\n".join(drug_rows)

    imp_file = os.path.join(output_dir, "implants_boosters_matrix.md")
    imp_md = f"""# EVE Online: Master Pirate Implant Sets & Combat Boosters Matrix

Comprehensive guide to cybernetic implant sets (Slots 1-6 set effects + Slots 7-10 hardwirings) and combat drugs.

---

## 🧬 Pirate Implant Sets (High-Grade 6-Piece Sets)
| Implant Set Name | Cumulative Bonus | Set Mechanical Effect | Optimal Doctrine / Role |
| :--- | :--- | :--- | :--- |
{imp_table}

---

## 💊 Combat Booster Drugs & Side-Effect Mitigation
| Booster Drug | Primary Combat Attribute Boost | Potential Side Effects | Optimal Doctrine |
| :--- | :--- | :--- | :--- |
{drug_table}

> **Neurotoxin Recovery & Biology Skills**: Train `Biology 5` (doubles booster duration) and `Neurotoxin Recovery 5` / `Neurotoxin Control 5` (reduces side-effect chance and severity by 50%).
"""
    with open(imp_file, "w", encoding="utf-8") as f:
        f.write(imp_md)
    created_files.append(imp_file)

    # 2. TRACKING & DAMAGE MATH
    math_file = os.path.join(output_dir, "tracking_missile_damage_math.md")
    math_md = """# EVE Online: Master Gun Turret Tracking & Missile Explosion Mathematics

Complete physics equations governing hit probabilities, angular velocities, explosion velocity scaling, and signature radius damage application.

---

## 🎯 The Gun Turret Tracking Equation
The exact chance to hit a moving target ($P_{\\text{hit}}$):

$$P_{\\text{hit}} = 0.5^{\\left( \\left( \\frac{\\text{Angular Velocity} \\times \\text{Signature Resolution}}{\\text{Tracking Speed} \\times \\text{Target Signature Radius}} \\right)^2 + \\left( \\frac{\\max(0, \\text{Range} - \\text{Optimal})}{\\text{Falloff}} \\right)^2 \\right)}$$

### Critical Insights:
- **Wrecking Hits (300% Damage)**: Occur on rolls between `0.00` and `0.01` (1% chance when $P_{\\text{hit}} > 0.01$).
- **Signature Resolution**: Small turrets = `40m` | Medium turrets = `125m` | Large turrets = `400m`. Larger guns deal negligible damage to small, fast-orbiting targets without webifiers/target painters.

---

## 🚀 The Missile Explosion Damage Formula
Missiles always hit, but damage scales based on target speed and signature radius:

$$\\text{Damage Applied} = \\text{Base Damage} \\times \\min\\left(1, \\frac{\\text{Sig}_{\\text{target}}}{\\text{Sig}_{\\text{exp}}}, \\left( \\frac{\\text{Sig}_{\\text{target}}}{\\text{Sig}_{\\text{exp}}} \\times \\frac{V_{\\text{exp}}}{V_{\\text{target}}} \\right)^{\\frac{\\ln(S)}{\\ln(5.5)}} \\right)$$

- **Missile Signature Ratio**: $\\frac{\\text{Sig}_{\\text{target}}}{\\text{Sig}_{\\text{exp}}}$ — Target Painters increase applied damage directly.
- **Velocity Ratio**: $\\frac{V_{\\text{exp}}}{V_{\\text{target}}}$ — Stasis Webifiers slow the target, forcing maximum missile alpha.
"""
    with open(math_file, "w", encoding="utf-8") as f:
        f.write(math_md)
    created_files.append(math_file)

    # 3. EWAR DISRUPTION GUIDE
    ewar_file = os.path.join(output_dir, "ewar_disruption_guide.md")
    ewar_md = """# EVE Online: Electronic Warfare (EWAR) & Fleet Disruption Guide

Tactical operation profiles for ECM, Sensor Dampening, Tracking Disruption, Target Painting, and Energy Warfare.

---

## ⚡ EWAR Systems Comparison Matrix
| EWAR System | Primary Ship Hulls | Mechanical Effect | Hard Counter |
| :--- | :--- | :--- | :--- |
| **ECM (Jamming)** | Falcon, Rook, Scorpion, Widow | Forces target to only lock the jamming ship | Sensor Boosters / ECCM Scripts |
| **Sensor Dampening** | Celestis, Arazu, Lachesis, Maulus | Reduces lock range by up to -75% or slows lock time by 75% | Sensor Boosters (Range script) |
| **Tracking Disruption** | Crucifier, Pilgrim, Curse, Sentinel | Penalizes turret tracking speed or optimal/falloff by up to -65% | Tracking Computers / Tracking Scripts |
| **Target Painting** | Vigil, Bellicose, Huginn, Rapier | Inflates target signature radius by up to +60% | Signature radius reduction / Small hulls |
| **Stasis Webifiers** | Daredevil, Ashimmu, Bhaalgorn, Huginn | Slows target velocity by up to **-90%** | Warp out / Web range avoidance (Overclocker) |
| **Energy Neutralizers**| Armageddon, Bhaalgorn, Curse, Pilgrim | Drains capacitor dry in 1-2 cycles | Capacitor Booster injectors / Batteries |
"""
    with open(ewar_file, "w", encoding="utf-8") as f:
        f.write(ewar_md)
    created_files.append(ewar_file)

    return created_files
