"""
EVE Online Master Blueprint Tech Tree, Invention & Manufacturing Engine.

Exhaustive references for:
- Universal Blueprint Library (T1, T2, T3, Capital, Upwell Citadels, Rigs, Faction Ammo, Drones)
- Material Efficiency (ME) & Time Efficiency (TE) Mathematical Cost Equations
- Invention Mechanics, Datacore Requirements, Base Probabilities & Decryptor Modifiers
- Consolidated Fleet Blueprint Asset Portfolio

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
INDUSTRY_DIR = os.path.join(VAULT_EVE_DIR, "Industry")

BLUEPRINT_CATEGORIES = [
    {
        "category": "Mining & Industrial Ships",
        "examples": "Procurer, Retriever, Covetor, Hulk, Mackinaw, Skiff, Orca, Rorqual",
        "inputs": "Tritanium, Pyerite, Mexallon, Isogen, Megacyte, Capital Construction Parts",
        "me10_savings": "-10.0% Raw Mineral Requirements"
    },
    {
        "category": "Sub-capital Combat Ships",
        "examples": "Cruisers (Cerberus, Sacrilege, Muninn), Marauders (Paladin, Vargur), Battleships (Rokh, Megathron)",
        "inputs": "Minerals, Morphite, Planetary Robotics, Construction Components",
        "me10_savings": "-10.0% Base Materials"
    },
    {
        "category": "Capital & Supercapital Ships",
        "examples": "Revelation, Naglfar, Phoenix, Moros, Wyvern, Aeon, Erebus, Avatar",
        "inputs": "Capital Armor Plates, Capital Propulsion Engine, Capital Sensor Cluster, Capital Turret Hardpoints",
        "me10_savings": "-10.0% Capital Components (Saves 400M - 2.5B ISK per hull)"
    },
    {
        "category": "Upwell Structures & Citadels",
        "examples": "Astrahus, Fortizar, Keepstar, Raitaru, Azbel, Sotiyo, Athanor, Tatara",
        "inputs": "Structure Construction Blocks, Superconductors, Robotics, P4 Planetary Goods",
        "me10_savings": "-10.0% Structure Components"
    },
    {
        "category": "Ammunition & Missiles",
        "examples": "Caldari Navy Scourge Heavy Missile, Scorch L, Void L, Tremor L",
        "inputs": "Tritanium, Pyerite, Mexallon, Isogen + Faction LP tags",
        "me10_savings": "High-volume mass production (-10% cost per million rounds)"
    },
    {
        "category": "Combat & Mining Drones",
        "examples": "Hobgoblin II, Hammerhead II, Ogre II, Mining Drone II, Excavator Drone",
        "inputs": "Fernite Carbide, Nanotransistors, T2 Components, Morphite",
        "me10_savings": "-10.0% T2 Component consumption"
    }
]


def generate_blueprints_markdown(output_dir: str = INDUSTRY_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. Master Blueprint Tech Tree
    bp_rows = []
    for b in BLUEPRINT_CATEGORIES:
        bp_rows.append(f"| **{b['category']}** | `{b['examples']}` | {b['inputs']} | **{b['me10_savings']}** |")

    bp_table = "\n".join(bp_rows)
    bp_file = os.path.join(output_dir, "master_blueprint_tech_tree.md")
    bp_md = f"""# EVE Online: Master Blueprint Manufacturing Tech Tree

Comprehensive blueprint categorization, required industrial inputs, and Material Efficiency (ME 10 / TE 20) profit optimizations.

| Manufacturing Category | Representative Hulls / Blueprints | Primary Input Dependencies | ME 10 Value Advantage |
| :--- | :--- | :--- | :--- |
{bp_table}
"""
    with open(bp_file, "w", encoding="utf-8") as f:
        f.write(bp_md)
    created_files.append(bp_file)

    # 2. Manufacturing & Invention Guide
    inv_file = os.path.join(output_dir, "manufacturing_invention_guide.md")
    inv_md = """# EVE Online: Advanced T2 Invention & Manufacturing Guide

Mathematical equations for T2 blueprint invention probabilities, decryptor modifiers, and facility job run costs.

---

## 🎲 The T2 Invention Formula
$$\\text{Invention Chance} = \\text{Base Chance} \\times \\left(1 + \\frac{\\text{Encryption Skill Level}}{40} + \\frac{\\text{Datacore 1 Level} + \\text{Datacore 2 Level}}{30}\\right) \\times \\text{Decryptor Mod}$$

### Base Chances by Hull Class:
- **Frigates / Destroyers**: `40.0% Base Chance`
- **Cruisers / Battlecruisers / Industrials**: `34.0% Base Chance`
- **Battleships**: `30.0% Base Chance`

---

## 🧮 Decryptor Modifiers Matrix
| Decryptor Type | Success Probability Mod | Max Runs Modifier | ME Modifier | TE Modifier | Optimal Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Accelerant** | `+20.0%` | `+1 Run` | `+2 ME` | `+10 TE` | T2 Cruisers & HACs |
| **Attainment** | `+80.0%` | `+4 Runs` | `-1 ME` | `-2 TE` | High-volume Ammo / Drones |
| **Augmentation** | `+60.0%` | `+9 Runs` | `-2 ME` | `+2 TE` | Mass Drone Production |
| **Parity** | `+50.0%` | `+3 Runs` | `+1 ME` | `-2 TE` | T2 Modules & Hulls |
| **Process** | `+10.0%` | `+0 Runs` | `+3 ME` | `+6 TE` | High-cost T2 Hulls |
| **Symmetry** | `+0.0%` | `+2 Runs` | `+1 ME` | `+8 TE` | Balanced Production |
"""
    with open(inv_file, "w", encoding="utf-8") as f:
        f.write(inv_md)
    created_files.append(inv_file)

    # 3. Fleet Blueprint Portfolio
    fleet_bp_file = os.path.join(output_dir, "fleet_blueprint_portfolio.md")
    fleet_bp_md = """# Alexander Fleet: Consolidated Blueprint Portfolio & Industrial Assets

Itemized blueprint inventory, research levels (ME/TE), and active industrial manufacturing lines across the fleet.

---

## 📜 High-Value Blueprint Originals (BPO) & Copies (BPC)
| Blueprint Name | Type | Research Level | Location / Hangar | Current Status |
| :--- | :--- | :--- | :--- | :--- |
| **Procurer Blueprint** | `BPO (Original)` | `ME 10 / TE 20` | Staging Citadel Hangar | Ready for Batch Production |
| **Mining Laser Upgrade II Blueprint** | `BPC (10 Runs)` | `ME 2 / TE 4` | Staging Citadel Hangar | In Reserve |
| **Nanite Repair Paste Blueprint** | `BPO (Original)` | `ME 10 / TE 20` | Industrial Workshop | Continuous Production |
| **Scourge Fury Heavy Missile Blueprint** | `BPC (100 Runs)`| `ME 2 / TE 4` | Ammo Facility | Fleet Resupply |
| **Large Shield Extender II Blueprint** | `BPC (10 Runs)` | `ME 2 / TE 4` | Industrial Workshop | Doctrine Reserve |
"""
    with open(fleet_bp_file, "w", encoding="utf-8") as f:
        f.write(fleet_bp_md)
    created_files.append(fleet_bp_file)

    return created_files
