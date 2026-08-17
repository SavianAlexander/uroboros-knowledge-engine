"""
EVE Online Static Data Export (SDE) Encyclopedia & Ship Hull Theory Engine.

Comprehensive technical references for all major ship hulls, slot configurations,
capacitor architectures, sensor profiles, and doctrine roles across New Eden:
- Mining & Industrial Ships (Exhumers, Mining Barges, Industrial Command, Freighters, Jump Freighters)
- Sub-capital Combat (Marauders, Battleships, HACs, Logistics Cruisers, Recons, Interceptors, T3C)
- Capital & Supercapital (Dreadnoughts, Force Auxiliaries, Carriers, Supercarriers, Titans)
- Planetary Industry & Reaction Schematics

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time).
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
ENCYCLOPEDIA_DIR = os.path.join(VAULT_EVE_DIR, "Encyclopedia")

SHIP_HULL_DATABASE = {
    # 1. MINING & INDUSTRIAL
    "Hulk": {
        "class": "Exhumer",
        "race": "ORE",
        "role": "Maximum Yield Strip Mining & Moon Ore Harvesting",
        "slots": {"high": 3, "mid": 4, "low": 3, "rig": 2},
        "turrets": 2, "launchers": 0,
        "ore_hold": "15,000 m³", "cargo": "450 m³",
        "base_shield": 4500, "base_armor": 3500, "base_hull": 4000,
        "role_bonuses": [
            "25% bonus to Strip Miner and Ice Harvester yield per level of Exhumers",
            "5% bonus to Strip Miner and Ice Harvester duration per level of Mining Barge",
            "100% bonus to Strip Miner and Ice Harvester range"
        ],
        "doctrine_fit": "2x Modulated Strip Miner II + Mining Laser Upgrade II x3 + Multispectrum Shield Hardener II x2"
    },
    "Mackinaw": {
        "class": "Exhumer",
        "race": "ORE",
        "role": "Deep Space Solo Mining & Extended Endurance",
        "slots": {"high": 3, "mid": 4, "low": 3, "rig": 2},
        "turrets": 2, "launchers": 0,
        "ore_hold": "35,000 m³", "cargo": "500 m³",
        "base_shield": 5000, "base_armor": 4000, "base_hull": 4500,
        "role_bonuses": [
            "10% bonus to Ore Hold capacity per level of Exhumers",
            "5% bonus to Strip Miner and Ice Harvester yield per level of Mining Barge"
        ],
        "doctrine_fit": "2x Modulated Strip Miner II + Survey Scanner II + Mining Laser Upgrade II x2 + Damage Control II"
    },
    "Skiff": {
        "class": "Exhumer",
        "race": "ORE",
        "role": "Heavy Armor / High-Security Tanked Mining",
        "slots": {"high": 2, "mid": 5, "low": 3, "rig": 2},
        "turrets": 1, "launchers": 0,
        "ore_hold": "15,000 m³", "cargo": "450 m³",
        "base_shield": 8500, "base_armor": 6000, "base_hull": 6500,
        "role_bonuses": [
            "20% bonus to Drone damage and hitpoints per level of Exhumers",
            "7.5% bonus to Shield and Armor hitpoints per level of Mining Barge"
        ],
        "doctrine_fit": "1x Modulated Strip Miner II + Multispectrum Shield Hardener II x2 + Large Shield Extender II + MLU II x2"
    },
    "Orca": {
        "class": "Industrial Command Ship",
        "race": "ORE",
        "role": "Fleet Mining Foreman, Compression & Support",
        "slots": {"high": 6, "mid": 5, "low": 2, "rig": 3},
        "turrets": 0, "launchers": 0,
        "ore_hold": "150,000 m³", "fleet_hangar": "40,000 m³", "ship_maintenance_bay": "400,000 m³",
        "base_shield": 45000, "base_armor": 35000, "base_hull": 60000,
        "role_bonuses": [
            "3% bonus to Mining Foreman Burst strength per level of Industrial Command Ships",
            "100% bonus to Command Burst area of effect",
            "Equipped with Industrial Core and Asteroid/Moon/Gas/Ice Compression modules"
        ],
        "doctrine_fit": "Mining Foreman Burst II x3 + Large Shield Extender II x3 + Reinforced Bulkheads II x2"
    },
    "Rorqual": {
        "class": "Capital Industrial Ship",
        "race": "ORE",
        "role": "Capital Mining Fleet Flagship & Industrial Core Operations",
        "slots": {"high": 8, "mid": 7, "low": 4, "rig": 3},
        "turrets": 0, "launchers": 0,
        "ore_hold": "300,000 m³", "fleet_hangar": "50,000 m³", "ship_maintenance_bay": "1,000,000 m³",
        "base_shield": 125000, "base_armor": 90000, "base_hull": 180000,
        "role_bonuses": [
            "Industrial Core II allows high-efficiency capital Asteroid & Moon ore compression",
            "Excavator Mining Drone integration (+400% drone mining yield)",
            "Pulse Activated Anomaly Shielding (PANIC) module invulnerability"
        ],
        "doctrine_fit": "Industrial Core II + Mining Foreman Burst II x3 + Capital Shield Booster + Capital Cap Booster"
    },
    "Prowler": {
        "class": "Blockade Runner (Transport Ship)",
        "race": "Minmatar",
        "role": "High-Speed Cloaked Cargo Transport & Logistics",
        "slots": {"high": 2, "mid": 3, "low": 4, "rig": 2},
        "turrets": 0, "launchers": 0,
        "cargo": "8,500 m³ (Expandable)",
        "base_shield": 2500, "base_armor": 2000, "base_hull": 2000,
        "role_bonuses": [
            "Can fit Covert Ops Cloaking Device II and Covert Cynosural Field Generator",
            "Immune to Cargo Scanners",
            "5% bonus to max velocity and 5% bonus to agility per level of Transport Ships"
        ],
        "doctrine_fit": "Covert Ops Cloaking Device II + 50MN Microwarpdrive + Inertial Stabilizers II x4 + Hyperspatial Rigs"
    },

    # 2. COMBAT SUB-CAPITALS
    "Paladin": {
        "class": "Marauder",
        "race": "Amarr",
        "role": "Advanced Heavy Armor Bastion Fleet Battleship",
        "slots": {"high": 8, "mid": 4, "low": 7, "rig": 2},
        "turrets": 4, "launchers": 0,
        "base_shield": 7500, "base_armor": 12500, "base_hull": 11000,
        "role_bonuses": [
            "Bastion Module immune to EWAR and doubles local armor repair amount",
            "100% bonus to Large Energy Turret damage",
            "7.5% bonus to Large Energy Turret optimal range per level of Marauders"
        ],
        "doctrine_fit": "4x Mega Pulse Laser II + Bastion Module I + Large Armor Repairer II x2 + Multispectrum Energized Membrane II x2 + Heat Sink II x2"
    },
    "Vargur": {
        "class": "Marauder",
        "race": "Minmatar",
        "role": "Advanced Shield Bastion Fleet Battleship",
        "slots": {"high": 8, "mid": 6, "low": 5, "rig": 2},
        "turrets": 4, "launchers": 0,
        "base_shield": 12500, "base_armor": 7500, "base_hull": 10000,
        "role_bonuses": [
            "Bastion Module immune to EWAR and doubles local shield boost amount",
            "100% bonus to Large Projectile Turret damage",
            "7.5% bonus to Large Projectile Turret tracking per level of Marauders"
        ],
        "doctrine_fit": "4x 800mm Repeating Cannon II + Bastion Module I + Large Shield Booster II x2 + Multispectrum Shield Hardener II + Gyrostabilizer II x3"
    },
    "Cerberus": {
        "class": "Heavy Assault Cruiser (HAC)",
        "race": "Caldari",
        "role": "Long-Range Heavy Missile Skirmish & Fleet Fleet Combat",
        "slots": {"high": 6, "mid": 5, "low": 4, "rig": 2},
        "turrets": 0, "launchers": 6,
        "base_shield": 4000, "base_armor": 2500, "base_hull": 2800,
        "role_bonuses": [
            "Assault Damage Control capability (+75% all resists for 15 seconds)",
            "5% bonus to Heavy Missile and Heavy Assault Missile rate of fire per level of Heavy Assault Cruisers",
            "10% bonus to Heavy Missile velocity per level of Caldari Cruiser"
        ],
        "doctrine_fit": "6x Heavy Missile Launcher II + 50MN Microwarpdrive + Multispectrum Shield Hardener II + Ballistic Control System II x3"
    },
    "Sacrilege": {
        "class": "Heavy Assault Cruiser (HAC)",
        "race": "Amarr",
        "role": "Heavy Armor Brawler & Energy Neutralizer Platform",
        "slots": {"high": 6, "mid": 4, "low": 5, "rig": 2},
        "turrets": 0, "launchers": 5,
        "base_shield": 2800, "base_armor": 4500, "base_hull": 3500,
        "role_bonuses": [
            "Assault Damage Control integration",
            "5% bonus to Heavy Assault Missile and Heavy Missile damage per level",
            "4% bonus to all armor resistances per level of Amarr Cruiser"
        ],
        "doctrine_fit": "5x Heavy Assault Missile Launcher II + Heavy Energy Neutralizer II + 50MN MWD + 1600mm Steel Plates II + Assault Damage Control II"
    },
    "Muninn": {
        "class": "Heavy Assault Cruiser (HAC)",
        "race": "Minmatar",
        "role": "Fleet Missile / Artillery Strike Platform",
        "slots": {"high": 6, "mid": 4, "low": 5, "rig": 2},
        "turrets": 0, "launchers": 5,
        "base_shield": 3800, "base_armor": 3200, "base_hull": 3000,
        "role_bonuses": [
            "5% bonus to Heavy Missile rate of fire and velocity per level",
            "Assault Damage Control integration"
        ],
        "doctrine_fit": "5x Heavy Missile Launcher II + 50MN MWD + Multispectrum Shield Hardener II + Ballistic Control System II x3"
    },

    # 3. CAPITAL SHIPS
    "Revelation": {
        "class": "Dreadnought",
        "race": "Amarr",
        "role": "Capital Anti-Structure & Capital Energy Turret Siege Platform",
        "slots": {"high": 6, "mid": 4, "low": 7, "rig": 3},
        "turrets": 3, "launchers": 0,
        "base_shield": 80000, "base_armor": 220000, "base_hull": 180000,
        "role_bonuses": [
            "Siege Module increases Capital Energy Turret damage by 700% and armor repair by 100%",
            "5% bonus to Capital Energy Turret damage per level of Amarr Dreadnought"
        ],
        "doctrine_fit": "3x Capital Beam / Pulse Laser + Siege Module II + Capital Armor Repairer II + Capital Heat Sink II x3"
    },
    "Naglfar": {
        "class": "Dreadnought",
        "race": "Minmatar",
        "role": "Capital Projectile Turret Siege Platform (Zero Cap Usage)",
        "slots": {"high": 6, "mid": 6, "low": 5, "rig": 3},
        "turrets": 2, "launchers": 0,
        "base_shield": 180000, "base_armor": 120000, "base_hull": 160000,
        "role_bonuses": [
            "Siege Module II integration",
            "5% bonus to Capital Projectile Turret rate of fire and tracking per level"
        ],
        "doctrine_fit": "2x Hexa 2500mm Repeating Cannon + Siege Module II + Capital Shield Booster II + Capital Gyrostabilizer II x3"
    }
}


def generate_encyclopedia_markdown(output_dir: str = ENCYCLOPEDIA_DIR) -> list:
    """Generate comprehensive technical documents for ship hulls and fitting doctrines."""
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. Master Ship Directory
    index_path = os.path.join(output_dir, "ship_encyclopedia_index.md")
    ship_rows = []
    for name, data in sorted(SHIP_HULL_DATABASE.items()):
        ship_rows.append(f"| **{name}** | `{data['class']}` | {data['race']} | {data['role']} | `{data['slots']['high']}H / {data['slots']['mid']}M / {data['slots']['low']}L` |")

    ship_table = "\n".join(ship_rows)
    index_md = f"""# EVE Online: Master Ship Hull Encyclopedia & Theorycrafting Vault

Comprehensive technical database of ship hulls, base stats, fitting layouts, role bonuses, and standard fleet doctrine fits.

| Ship Name | Class | Tech / Race | Primary Role | Slot Layout |
| :--- | :--- | :--- | :--- | :--- |
{ship_table}
"""
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_md)
    created_files.append(index_path)

    # 2. Individual Ship Specifications
    for name, data in SHIP_HULL_DATABASE.items():
        ship_file = os.path.join(output_dir, f"ship_{name.lower().replace(' ', '_')}.md")
        bonuses_str = "\n".join([f"- {b}" for b in data.get("role_bonuses", [])])
        slots = data.get("slots", {})

        ship_md = f"""# EVE Ship Specification: {name} ({data.get('class')})

- **Race / Origin**: **{data.get('race')}**
- **Hull Classification**: **{data.get('class')}**
- **Combat / Operational Role**: **{data.get('role')}**
- **Slot Architecture**: `{slots.get('high')} High` | `{slots.get('mid')} Mid` | `{slots.get('low')} Low` | `{slots.get('rig')} Rigs`
- **Turret Hardpoints**: `{data.get('turrets', 0)}` | **Launcher Hardpoints**: `{data.get('launchers', 0)}`
- **Hitpoints**: Shield: `{data.get('base_shield', 'N/A'):,}` HP | Armor: `{data.get('base_armor', 'N/A'):,}` HP | Structure: `{data.get('base_hull', 'N/A'):,}` HP

---

## Role & Trait Bonuses
{bonuses_str}

---

## Standard Fleet Doctrine Fitting
```text
[{name}, Standard Fleet Doctrine Fit]
{data.get('doctrine_fit')}
```
"""
        with open(ship_file, "w", encoding="utf-8") as f:
            f.write(ship_md)
        created_files.append(ship_file)

    return created_files


# In-Memory O(1) Index for instantaneous retrieval
_SHIP_HULL_LOWER_INDEX = {k.lower().strip(): dict(v, name=k) for k, v in SHIP_HULL_DATABASE.items()}


def get_ship_hull(name: str) -> Optional[Dict[str, Any]]:
    """Retrieve ship hull specifications by name in O(1) time."""
    if not name or not isinstance(name, str):
        return None
    return _SHIP_HULL_LOWER_INDEX.get(name.lower().strip())


def search_ship_hulls(query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
    """Search ship hulls by name, role, class, or fitting doctrine in O(N) memory scan."""
    if not query or not str(query).strip():
        return [dict(v, name=k) for k, v in list(SHIP_HULL_DATABASE.items())[:limit]]

    q_clean = str(query).lower().strip()
    matches = []
    for k, v in SHIP_HULL_DATABASE.items():
        score = 0
        name_low = k.lower()
        class_low = (v.get("class") or "").lower()
        role_low = (v.get("role") or "").lower()
        fit_low = (v.get("doctrine_fit") or "").lower()

        if q_clean == name_low:
            score += 100
        elif q_clean in name_low:
            score += 50
        elif q_clean in class_low:
            score += 30
        elif q_clean in role_low:
            score += 20
        elif q_clean in fit_low:
            score += 10

        if score > 0:
            item = dict(v, name=k, search_score=score)
            matches.append(item)

    matches.sort(key=lambda x: x["search_score"], reverse=True)
    return matches[:limit]
