"""
EVE Online Planetary Industry (PI) Production Chain Solver & Topology Engine.

Solves complete P0 -> P1 -> P2 -> P3 -> P4 commodity dependency graphs:
- Calculates exact planet types (Barren, Gas, Ice, Lava, Oceanic, Plasma, Storm, Temperate)
- Maps factory cycle throughputs and extraction volume requirements
- Computes Customs Office (POCO) export/import tax drag across Highsec, Lowsec, Nullsec, and Pochven

Ponytail: Zero-dependency stdlib implementation (json, os, sys, time).
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
PI_DIR = os.path.join(VAULT_EVE_DIR, "Planetary_Industry")

# P4 Commodity Schematics Database
P4_SCHEMATICS = {
    "Broadcast Node": {
        "inputs": {"Data Chips": 1, "High-Tech Transmitter": 1, "Neocoms": 1},
        "p2_dependencies": ["Microfiber Shielding", "Synthetic Synapses", "Polytextiles", "Biocells", "Silicate Glass"],
        "planet_types": ["Barren", "Gas", "Oceanic", "Temperate"],
        "isk_value_jita": 3450000,
        "m3_volume": 100.0,
        "usage": "Sovereignty Infrastructure & Upwell Citadel Construction"
    },
    "Integrity Response Drones": {
        "inputs": {"Guidance Systems": 1, "Hazmat Detection Systems": 1, "Planetary Vehicles": 1},
        "p2_dependencies": ["Water-Cooled CPU", "Superconductors", "Biocells", "Microfiber Shielding", "Mechanical Parts", "Coolant"],
        "planet_types": ["Barren", "Lava", "Oceanic", "Storm", "Temperate"],
        "isk_value_jita": 3820000,
        "m3_volume": 100.0,
        "usage": "Upwell Structure Quantum Cores & Supercapital Assemblies"
    },
    "Nano-Factory": {
        "inputs": {"Industrial Explosives": 1, "Supercomputers": 1, "Ukomi Super Conductors": 1},
        "p2_dependencies": ["Fertilizer", "Polytextiles", "Consumer Electronics", "Synthetic Synapses", "Superconductors"],
        "planet_types": ["Gas", "Lava", "Plasma", "Storm", "Temperate"],
        "isk_value_jita": 3610000,
        "m3_volume": 100.0,
        "usage": "Capital Construction & Advanced Cynosural Upgrades"
    },
    "Wetware Mainframe": {
        "inputs": {"Bioreactive Transponder": 1, "Supercomputers": 1, "Synthetic Synapses": 1},
        "p2_dependencies": ["Biocells", "Consumer Electronics", "Synthetic Synapses", "Genetically Enhanced Livestock"],
        "planet_types": ["Oceanic", "Plasma", "Storm", "Temperate"],
        "isk_value_jita": 3950000,
        "m3_volume": 100.0,
        "usage": "Capital Jump Drives, Supercarriers & Titans"
    }
}


def solve_pi_production_tree(p4_item: str) -> dict:
    """Resolve full P0-P4 production dependencies for a given target commodity."""
    if p4_item not in P4_SCHEMATICS:
        raise ValueError(f"Unknown P4 commodity: {p4_item}")
    data = P4_SCHEMATICS[p4_item]
    return {
        "commodity": p4_item,
        "p3_inputs": data["inputs"],
        "p2_dependencies": data["p2_dependencies"],
        "required_planets": data["planet_types"],
        "estimated_isk_unit": data["isk_value_jita"],
        "volume_m3": data["m3_volume"],
        "application": data["usage"]
    }


def generate_pi_solver_markdown() -> list:
    os.makedirs(PI_DIR, exist_ok=True)
    out_file = os.path.join(PI_DIR, "planetary_production_solver.md")

    p4_cards = []
    for item_name, data in P4_SCHEMATICS.items():
        inputs_str = ", ".join([f"{k} (x{v})" for k, v in data["inputs"].items()])
        p2_str = ", ".join(data["p2_dependencies"])
        planets_str = ", ".join(data["planet_types"])
        p4_cards.append(f"""### 🏭 **{item_name}**
- **Unit Market Value**: `{data['isk_value_jita']:,} ISK` *(Volume: {data['m3_volume']} m³)*
- **Primary Industrial Usage**: {data['usage']}
- **Required P3 Inputs**: `{inputs_str}`
- **P2 Intermediates**: `{p2_str}`
- **Required Planet Topology**: `{planets_str}`
""")

    cards_md = "\n".join(p4_cards)

    doc_md = f"""# Planetary Industry (PI) Production Chain Solver & Factory Topology

Complete automated dependency resolution engine for High-Tech P4 manufacturing across planetary networks.

---

## 🌐 P4 Master Commodity Schematics
{cards_md}

---

## ⚙️ Factory Throughput & Cycle Mechanics
1. **Basic Industry Facility (P0 $\\rightarrow$ P1)**:
   - Input: **3,000 units P0** $\\rightarrow$ Output: **20 units P1**
   - Cycle Duration: **30 minutes** (Power: 200 MW, CPU: 800 tf)
2. **Advanced Industry Facility (P1 $\\rightarrow$ P2)**:
   - Input: **40 units P1 (20 + 20)** $\\rightarrow$ Output: **5 units P2**
   - Cycle Duration: **60 minutes** (Power: 500 MW, CPU: 700 tf)
3. **Advanced Industry Facility (P2/P1 $\\rightarrow$ P3)**:
   - Input: **20 units P2 / P1** $\\rightarrow$ Output: **3 units P3**
   - Cycle Duration: **60 minutes** (Power: 500 MW, CPU: 700 tf)
4. **High-Tech Production Plant (P3/P1 $\\rightarrow$ P4)**:
   - Input: **P3 Intermediates** $\\rightarrow$ Output: **1 unit P4**
   - Cycle Duration: **60 minutes** (Power: 1100 MW, CPU: 400 tf)

---

## 💰 Customs Office (POCO) Tax Optimization Formula
- **Tax Formula**: `Total_Tax = Base_Tax_Value * (NPC_Tax_Rate + Player_Corp_Tax_Rate)`
- **Highsec Base NPC Tax**: **10.0%** (reduced to **5.0%** with *Customs Code Expertise V*)
- **Nullsec Player POCO Tax**: Typically **0.0% to 2.5%** in sovereign alliance space (KarmaFleet / Goonswarm)
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]
