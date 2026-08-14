"""
EVE Online Abyssal Deadspace, Upwell Structures, LP Store Arbitrage & Pochven Flashpoints Engine.

Exhaustive operational references for:
- Abyssal Deadspace T1-T6 (5 Weather Mutators, NPC Room Spawns, Mutaplasmid Rolling Matrix)
- Upwell Structures (Citadels, Engineering Complexes, Refineries, Moon Drilling, Damage Caps & Tethering)
- Universal Loyalty Point (LP) Store Arbitrage & Conversion Index
- Pochven Flashpoints (OFP 15-Man Fleets, 27-System Cartography & Standing Fixes)

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

ABYSS_DIR = os.path.join(VAULT_EVE_DIR, "Abyssal_Deadspace")
STRUCT_DIR = os.path.join(VAULT_EVE_DIR, "Structures")
MARKET_DIR = os.path.join(VAULT_EVE_DIR, "Market_Economics")
POCHVEN_DIR = os.path.join(VAULT_EVE_DIR, "Pochven")


def generate_advanced_ecosystems_markdown() -> list:
    created_files = []

    # 1. ABYSSAL DEADSPACE T1-T6 MATRIX
    os.makedirs(ABYSS_DIR, exist_ok=True)
    f1 = os.path.join(ABYSS_DIR, "abyssal_t1_t6_weather_mutaplasmids.md")
    m1 = """# EVE Online: Abyssal Deadspace T1-T6 Weather, Room Spawns & Mutaplasmids

Tactical matrix for solo cruiser, duo destroyer, and trio frigate abyssal runs.

---

## 🌪️ The 5 Abyssal Weather Environments
| Weather Type | Resistance Penalty | Environmental Bonus | Optimal Ship Archetypes |
| :--- | :--- | :--- | :--- |
| **Electrical** | `-30% to -70% EM Resistance` | `+50% Capacitor Recharge Rate` | Gila, Cerberus, Stormbringer |
| **Exotic** | `-30% to -70% Kinetic Resistance` | `+50% Targeting Scan Resolution`| Gila, Cerberus, Sacrilege |
| **Firestorm** | `-30% to -70% Thermal Resistance` | `+50% Armor Hitpoints` | Sacrilege, Zealot, Deimos |
| **Gamma** | `-30% to -70% Explosive Resistance`| `+50% Shield Hitpoints` | Gila, Vagabond, Muninn |
| **Dark** | `-30% to -70% Turret Optimal/Falloff`| `+50% Max Sub-warp Velocity` | Cerberus, Sacrilege (Missiles) |

---

## 🧬 Mutaplasmid Rolling & RNG Modification
- **Tiers**: *Decayed (T1-T3 Abyss)*, *Gravid (T4-T5 Abyss)*, *Unstable (T5-T6 Abyss)*.
- **Rollable Attributes**: Module CPU/Powergrid usage, Capacitor consumption, Cycle time, Damage multiplier, Shield/Armor repair amount, Warp scrambler range (`up to +40% range`).
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created_files.append(f1)

    # 2. UPWELL CITADEL & REFINERY ENGINEERING
    os.makedirs(STRUCT_DIR, exist_ok=True)
    f2 = os.path.join(STRUCT_DIR, "upwell_citadel_refinery_engineering.md")
    m2 = """# EVE Online: Upwell Citadel, Engineering Complex & Refinery Architecture

Engineering specifications, damage caps, vulnerability timers, and moon extraction mechanics.

---

## 🏰 Upwell Structure Classifications
| Structure Class | Medium Hull | Large Hull | Extra-Large (XL) Hull |
| :--- | :--- | :--- | :--- |
| **Citadel (Defense/HQ)** | **Astrahus** (5,000 DPS Cap) | **Fortizar** (15,000 DPS Cap) | **Keepstar** (75,000 DPS Cap + Supercapital Docking & Doomsday) |
| **Engineering (Industry)**| **Raitaru** | **Azbel** | **Sotiyo** (Titan & Supercarrier Shipyards) |
| **Refinery (Mining/Ore)** | **Atanor** | **Tatara** (90.6% Reprocessing + T2 Composite Reactions) | — |

---

## 🛡️ Reinforcement Timers & Quantum Cores
- **Quantum Cores**: Required for structure activation; guaranteed 100% drop upon hull destruction.
- **Anchoring Phase**: 24.0 Hours unanchored $\\rightarrow$ 15-minute vulnerability window.
- **Damage Caps**: Maximum incoming DPS accepted by structure shields/armor/hull (excess damage is nullified).
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created_files.append(f2)

    # 3. UNIVERSAL LP STORE ARBITRAGE
    os.makedirs(MARKET_DIR, exist_ok=True)
    f3 = os.path.join(MARKET_DIR, "universal_lp_store_arbitrage.md")
    m3 = """# EVE Online: Universal Loyalty Point (LP) Store Arbitrage & Redemption

High-yield LP conversion strategies across Empire Navies, FW Militias, CONCORD, and Pirate corporations.

---

## 💰 Top LP Conversion Ratios
| Loyalty Point Source | Optimal Store Redemption Item | Net ISK Yield per LP |
| :--- | :--- | :--- |
| **CONCORD LP (Incursions)** | High-Grade Ascendancy / Snake Implants | **2,200 – 2,800 ISK / LP** |
| **Faction Warfare Militias** | Faction Cruiser BPCs (Navy Omen, Osprey Navy) | **1,800 – 2,400 ISK / LP** |
| **Sisters of EVE (SOE LP)** | Astero / Stratios Blueprints + Sisters Probes | **2,000 – 2,500 ISK / LP** |
| **Pirate LP (Guristas/Angel)**| High-Grade Nirvana / Hydra Implants | **2,100 – 2,600 ISK / LP** |
| **Empire Navies (Caldari/Amarr)**| Caldari Navy Antimatter / Amarr Navy Crystals | **1,600 – 2,000 ISK / LP** |
"""
    with open(f3, "w", encoding="utf-8") as f:
        f.write(m3)
    created_files.append(f3)

    # 4. POCHVEN FLASHPOINTS & CLADE CARTOGRAPHY
    os.makedirs(POCHVEN_DIR, exist_ok=True)
    f4 = os.path.join(POCHVEN_DIR, "pochven_flashpoints_clade_cartography.md")
    m4 = """# EVE Online: Pochven 27-System Clade Cartography & Flashpoint Farming

Playbooks for Triglavian space navigation, standing mechanics, and Observatory Flashpoint (OFP) income.

---

## ⚡ Observatory Flashpoint (OFP) Fleet Mechanics
- **Fleet Size**: Exactly **15 Pilots** (Marauders, Drekavacs, Paladins, Nestors, Scimitars).
- **Completion Payout**: **255,000,000 ISK + 3,500 Red Ditanian LP per pilot** per site.
- **Earning Potential**: Running 5-7 sites/hour generates **1.2 Billion – 1.8 Billion ISK/hr per pilot**.

---

## 🗺️ Pochven Clade Geography
- **Krai Svarog** (9 Systems - Combat Focus)
- **Krai Perun** (9 Systems - Industrial Focus)
- **Krai Veles** (9 Systems - Bio-Adaptive Focus)
- **Stargate Safety**: Maintaining `+0.01 Standing` with Triglavian Collective and EDENCOM prevents NPC gate gun aggression.
"""
    with open(f4, "w", encoding="utf-8") as f:
        f.write(m4)
    created_files.append(f4)

    return created_files
