"""
Autonomous EVE Online Industry & Composite Reaction Yield Matrix Engine.
Standard: Zero external dependencies (stdlib math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact canonical structure rigs and reaction multipliers.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAULT_INDUSTRY_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Industry_Reactions")


STRUCTURE_RIG_BONUSES = {
    "Tatara": {"reaction_me": 0.024, "reaction_te": 0.24, "category": "Refinery (Large)"},
    "Athanor": {"reaction_me": 0.020, "reaction_te": 0.20, "category": "Refinery (Medium)"},
    "Sotiyo": {"manuf_me": 0.024, "manuf_te": 0.30, "category": "Engineering Complex (X-Large)"},
    "Azbel": {"manuf_me": 0.020, "manuf_te": 0.24, "category": "Engineering Complex (Large)"},
    "Raitaru": {"manuf_me": 0.010, "manuf_te": 0.15, "category": "Engineering Complex (Medium)"}
}

SPACE_SECURITY_MULTIPLIERS = {
    "Highsec": 1.0,
    "Lowsec": 1.9,
    "Nullsec": 2.1,
    "Wormhole": 2.1
}

COMPOSITE_REACTION_CHAINS = {
    "Crystalline Carbonide": {
        "type": "Composite Reaction",
        "inputs": {"Carbon Polymers": 100, "Crystallite": 100},
        "fuel": {"Helium Isotopes": 5},
        "output_quantity": 200,
        "base_duration_s": 10800,
        "used_in": ["T2 Armor Plates", "T2 Transport Ships (Crane/Bustard)", "T2 Battleships (Paladin)"]
    },
    "Fermionic Condensates": {
        "type": "Composite Reaction",
        "inputs": {"Fermionic Solutions": 100, "Fullerene Intercalates": 100},
        "fuel": {"Nitrogen Isotopes": 5},
        "output_quantity": 200,
        "base_duration_s": 10800,
        "used_in": ["T3 Cruiser Subsystems (Tengu/Legion)", "T2 Logistics Cruisers (Guardian/Basilisk)"]
    },
    "Nanotransistors": {
        "type": "Composite Reaction",
        "inputs": {"Linearized Carbon Polymers": 100, "Tungsten Carbide": 100},
        "fuel": {"Hydrogen Isotopes": 5},
        "output_quantity": 200,
        "base_duration_s": 10800,
        "used_in": ["T2 Electronics", "Jump Drive Components", "Capital Jump Drives"]
    },
    "Sylramic Fibers": {
        "type": "Composite Reaction",
        "inputs": {"Silicon Diborite": 100, "Titanium Carbide": 100},
        "fuel": {"Oxygen Isotopes": 5},
        "output_quantity": 200,
        "base_duration_s": 10800,
        "used_in": ["T2 Exhumers (Hulk/Skiff/Mackinaw)", "T2 Covert Ops Frigates (Anathema)"]
    }
}


def calculate_manufacturing_materials(
    base_materials: Dict[str, int],
    bpo_me: int = 10,
    structure_type: str = "Sotiyo",
    security_space: str = "Nullsec"
) -> Dict[str, Any]:
    """
    Calculate required manufacturing materials factoring in Blueprint ME,
    Upwell Structure Rig bonuses, and Space Security Multipliers.
    """
    struct = STRUCTURE_RIG_BONUSES.get(structure_type, {"manuf_me": 0.020})
    sec_mult = SPACE_SECURITY_MULTIPLIERS.get(security_space, 2.1)
    effective_struct_me = struct.get("manuf_me", 0.020) * sec_mult
    bpo_me_mult = 1.0 - (bpo_me / 100.0)

    adjusted_materials = {}
    savings = {}

    for mat_name, base_qty in base_materials.items():
        if base_qty <= 1:
            req_qty = base_qty
        else:
            raw_req = base_qty * bpo_me_mult * (1.0 - effective_struct_me)
            req_qty = max(1, math.ceil(raw_req))

        adjusted_materials[mat_name] = req_qty
        savings[mat_name] = base_qty - req_qty

    return {
        "bpo_me": bpo_me,
        "structure": structure_type,
        "security": security_space,
        "effective_structure_me_bonus": round(effective_struct_me * 100, 2),
        "required_materials": adjusted_materials,
        "total_material_savings": savings
    }


def calculate_reaction_yield(
    reaction_name: str,
    runs: int = 10,
    structure_type: str = "Tatara",
    security_space: str = "Nullsec",
    system_cost_index: float = 0.015
) -> Dict[str, Any]:
    """
    Calculate composite reaction throughput, fuel requirements, cycle times, and estimated yields.
    """
    reaction = COMPOSITE_REACTION_CHAINS.get(reaction_name)
    if not reaction:
        return {"error": f"Unknown reaction: {reaction_name}"}

    struct = STRUCTURE_RIG_BONUSES.get(structure_type, {"reaction_me": 0.024, "reaction_te": 0.24})
    sec_mult = SPACE_SECURITY_MULTIPLIERS.get(security_space, 2.1)
    
    me_bonus = struct.get("reaction_me", 0.024) * sec_mult
    te_bonus = struct.get("reaction_te", 0.24) * sec_mult

    total_outputs = reaction["output_quantity"] * runs
    cycle_time_per_run_s = reaction["base_duration_s"] * (1.0 - te_bonus)
    total_duration_hours = (cycle_time_per_run_s * runs) / 3600.0

    total_inputs = {}
    for mat, qty in reaction["inputs"].items():
        total_inputs[mat] = max(1, math.ceil(qty * runs * (1.0 - me_bonus)))

    total_fuel = {}
    for fuel_name, qty in reaction["fuel"].items():
        total_fuel[fuel_name] = qty * runs

    return {
        "reaction_name": reaction_name,
        "runs": runs,
        "structure": structure_type,
        "security": security_space,
        "total_output_units": total_outputs,
        "total_duration_hours": round(total_duration_hours, 2),
        "cycle_time_per_run_min": round(cycle_time_per_run_s / 60.0, 1),
        "me_material_reduction_percent": round(me_bonus * 100, 2),
        "te_time_reduction_percent": round(te_bonus * 100, 2),
        "total_inputs": total_inputs,
        "total_fuel": total_fuel,
        "used_in_doctrines": reaction["used_in"]
    }


def generate_industry_matrix_markdown() -> List[str]:
    """Generate industry and composite reactions reference document."""
    os.makedirs(VAULT_INDUSTRY_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_INDUSTRY_DIR, "t2_reaction_manufacturing_matrix.md")

    # Sample Hulk Manufacturing calculation
    hulk_base_materials = {
        "Tritanium": 1250000,
        "Pyerite": 320000,
        "Mexallon": 85000,
        "Isogen": 18000,
        "Nocxium": 3500,
        "Zydrine": 1200,
        "Megacyte": 450,
        "Sylramic Fibers": 450,
        "Crystalline Carbonide": 600
    }
    hulk_mats = calculate_manufacturing_materials(hulk_base_materials, bpo_me=10, structure_type="Sotiyo", security_space="Nullsec")
    reaction_calc = calculate_reaction_yield("Crystalline Carbonide", runs=24, structure_type="Tatara", security_space="Nullsec")

    doc_md = f"""---
title: Autonomous EVE Online Industry & Composite Reaction Yield Matrix
category: Industry & Reactions
tags: [EVE, Industry, CompositeReactions, T2Manufacturing, UpwellRigs, ISK]
last_updated: 2026-08-14
---

# 🏭 Autonomous Industry & Composite Reaction Yield Matrix

This matrix details the engineering calculus for high-yield Moon Composite Reactions, Tech 2 component manufacturing, and Upwell structure rig optimization across sovereign nullsec and wormhole space.

---

## 🏛️ 1. Upwell Structure Rigs & Security Multipliers

| Structure | Role | Base ME Rig | Base TE Rig | Null/WH ME (2.1x) | Null/WH TE (2.1x) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Tatara** | Composite / Biochemical Reactions | **2.40%** | **24.0%** | **5.04%** | **50.40%** |
| **Athanor** | Medium Refinery Reactions | **2.00%** | **20.0%** | **4.20%** | **42.00%** |
| **Sotiyo** | Capital / Supercapital Manufacturing | **2.40%** | **30.0%** | **5.04%** | **63.00%** |
| **Azbel** | Large Component Manufacturing | **2.00%** | **24.0%** | **4.20%** | **50.40%** |
| **Raitaru** | Medium Subcapital Manufacturing | **1.00%** | **15.0%** | **2.10%** | **31.50%** |

---

## ⚗️ 2. High-Yield Composite Reaction Chains

| Composite Output | Primary Inputs | Fuel Block Demand | Base Cycle | Primary Doctrine Demand |
| :--- | :--- | :---: | :---: | :--- |
| **Crystalline Carbonide** | Carbon Polymers + Crystallite | 5x Helium Isotopes | 3.0 Hours | T2 Battleships (Paladin), T2 Deep Space Transports |
| **Fermionic Condensates** | Fermionic Solutions + Fullerene | 5x Nitrogen Isotopes | 3.0 Hours | T3 Strategic Cruisers (Tengu/Legion), Logi Cruisers |
| **Nanotransistors** | Linearized Polymers + Tungsten | 5x Hydrogen Isotopes | 3.0 Hours | Capital Jump Drives, T2 Electronic Warfare |
| **Sylramic Fibers** | Silicon Diborite + Titanium | 5x Oxygen Isotopes | 3.0 Hours | T2 Exhumers (Hulk/Skiff), Covert Ops Frigates |

---

## 🚀 3. Verified Manufacturing Example: Tech 2 Exhumer (Hulk)
- **Base BPO ME**: **10%**
- **Production Facility**: **Sotiyo in Sovereign Nullsec (KarmaFleet / Goonswarm)**
- **Effective Structure ME Bonus**: **{hulk_mats['effective_structure_me_bonus']}%**

### Material Demand & Rig Savings Breakdown
"""
    for mat, qty in hulk_mats["required_materials"].items():
        base = hulk_base_materials[mat]
        saved = hulk_mats["total_material_savings"][mat]
        doc_md += f"- **{mat}**: **{qty:,} units** (Saved: `{saved:,}` units vs unresearched)\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_industry_matrix_markdown()
    print(f"Generated industry matrix document: {files}")
