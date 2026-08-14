"""
EVE Online Moon Ore Classification & T2 Reaction Chemistry Engine.

Exhaustive references for:
- Moon Ore Tiers: Ubiquitous (R4), Common (R8), Uncommon (R16), Rare (R32), Exceptional (R64)
- Intermediate Chemical Reactions & Advanced T2 Composite Material Manufacturing Chains
- Refinery & Reaction Facility Optimization (Athanor / Tatara Reactor Rig bonuses)

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
MOON_DIR = os.path.join(VAULT_EVE_DIR, "Moon_Mining")

MOON_ORES = {
    "R64 (Exceptional)": [
        {"name": "Monazite", "elements": "Promethium, Neodymium, Hydrocarbons", "rarity": "Exceptional R64"},
        {"name": "Loparite", "elements": "Promethium, Hydrocarbons, Platinum", "rarity": "Exceptional R64"},
        {"name": "Xenotime", "elements": "Dysprosium, Neodymium, Silicates", "rarity": "Exceptional R64"},
        {"name": "Ytterbite", "elements": "Thulium, Dysprosium, Titanium", "rarity": "Exceptional R64"},
    ],
    "R32 (Rare)": [
        {"name": "Carnotite", "elements": "Atmospheric Gases, Cobalt, Silicates", "rarity": "Rare R32"},
        {"name": "Cinnabar", "elements": "Cadmium, Mercury, Tungsten", "rarity": "Rare R32"},
        {"name": "Pollucite", "elements": "Caesium, Scandium, Platinum", "rarity": "Rare R32"},
        {"name": "Zircon", "elements": "Hafnium, Titanium, Scandium", "rarity": "Rare R32"},
    ],
    "R16 (Uncommon)": [
        {"name": "Chromite", "elements": "Chromium, Hydrocarbons", "rarity": "Uncommon R16"},
        {"name": "Otavite", "elements": "Cadmium, Platinum", "rarity": "Uncommon R16"},
        {"name": "Sperrylite", "elements": "Platinum, Evaporite Deposits", "rarity": "Uncommon R16"},
        {"name": "Vanadinite", "elements": "Vanadium, Chromium", "rarity": "Uncommon R16"},
    ],
    "R8 (Common)": [
        {"name": "Cobaltite", "elements": "Cobalt, Silicates", "rarity": "Common R8"},
        {"name": "Euxenite", "elements": "Titanium, Scandium", "rarity": "Common R8"},
        {"name": "Scheelite", "elements": "Tungsten, Evaporites", "rarity": "Common R8"},
        {"name": "Titanite", "elements": "Titanium, Hydrocarbons", "rarity": "Common R8"},
    ],
    "R4 (Ubiquitous)": [
        {"name": "Bitumens", "elements": "Hydrocarbons", "rarity": "Ubiquitous R4"},
        {"name": "Coesite", "elements": "Silicates", "rarity": "Ubiquitous R4"},
        {"name": "Sylvite", "elements": "Evaporite Deposits", "rarity": "Ubiquitous R4"},
        {"name": "Zeolites", "elements": "Atmospheric Gases", "rarity": "Ubiquitous R4"},
    ]
}


def generate_moon_reactions_markdown(output_dir: str = MOON_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. Moon Ore Classifications
    ore_rows = []
    for tier, ores in MOON_ORES.items():
        for o in ores:
            ore_rows.append(f"| **{o['name']}** | `{tier}` | {o['elements']} |")

    ore_table = "\n".join(ore_rows)
    ore_file = os.path.join(output_dir, "moon_ore_classifications.md")
    ore_md = f"""# EVE Online: Master Moon Ore Classification & Rarity Matrix

Comprehensive geological index of raw moon ores, rarity classifications (R4 to R64), and elemental refining yield profiles.

| Moon Ore Name | Rarity Tier | Primary Moon Elements Extracted |
| :--- | :--- | :--- |
{ore_table}
"""
    with open(ore_file, "w", encoding="utf-8") as f:
        f.write(ore_md)
    created_files.append(ore_file)

    # 2. T2 Composite Reaction Chains
    react_file = os.path.join(output_dir, "reaction_chemistry_chains.md")
    react_md = """# EVE Online: Advanced T2 Composite Reaction Chemistry

Formulas and chemical reaction pipelines for Tech II component production and capital construction.

---

## 🔬 Core Composite Chemical Formulas
| T2 Composite Material | Reaction Input 1 | Reaction Input 2 | Primary Application |
| :--- | :--- | :--- | :--- |
| **Fernite Carbide** | Fernite Alloy (Purified) | Ceramic Powder | Minmatar & Caldari T2 Armor / Structure |
| **Crystalline Carbonide** | Carbon Fiber | Crystallite Armor Plate | Amarr & Gallente T2 Armor Plating |
| **Nanotransistors** | Sulfuric Acid | Platinum Technetite | Electronic Systems & Radar Rigs |
| **Phenolic Composites** | Caesium | Silicates | Sensor Arrays & Warp Drives |
| **Photonic Metamaterials** | Thulium Dioxide | Lanthanum | T2 Shield Boosters & Optical Lasers |
| **Tenser Magnets** | Neodymium | Cobalt | Mag-Seals & Turret Accelerators |

---

## 🏭 Industrial Reactor Optimization
- **Athanor (Medium Refinery)**: Base 1.0x Reaction Speed | Medium Powergrid
- **Tatara (Large Refinery)**: **-25% Reaction Duration** | **-20% Fuel Block Consumption** with T2 Reaction Rigs
"""
    with open(react_file, "w", encoding="utf-8") as f:
        f.write(react_md)
    created_files.append(react_file)

    return created_files
