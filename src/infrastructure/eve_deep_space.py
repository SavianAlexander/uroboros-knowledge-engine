"""
EVE Online Deep Space Cartography, Wormhole Mechanics, Pochven & Abyssal Matrix Engine.

Synthesizes exhaustive technical references for:
- Wormhole Space (J-Space) Classifications C1-C6, Static Designations, System Effects
- Pochven (Triglavian Space) 27-System Cartography, Clade Systems & Flashpoints
- Abyssal Deadspace T1-T6 Weather Mutators, NPC Threat Archetypes & Mutaplasmids
- Planetary Interaction (PI) Complete P0->P4 Production Chains & Fuel Block Formulations

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


def generate_deep_space_markdown() -> list:
    created_files = []

    # 1. WORMHOLE SPACE (J-SPACE)
    wh_dir = os.path.join(VAULT_EVE_DIR, "Wormholes")
    os.makedirs(wh_dir, exist_ok=True)
    wh_file = os.path.join(wh_dir, "jspace_classification_statics.md")
    wh_md = """# EVE Online: Wormhole Space (J-Space) Cartography & Environmental Dynamics

Comprehensive intelligence on wormhole security classifications, mass thresholds, static designations, and system-wide environmental anomalies.

---

## 🌌 Wormhole Security Classes (C1 — C6 + Specialized)
| Class | Mass Limits | Allowed Ship Classes | Capital Escalation | Site Difficulty |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | Small / Medium | Frigates, Destroyers, Cruisers, Battlecruisers | ❌ None | Low (Solo Frigate / Cruiser) |
| **C2** | Medium / Large | Cruisers, Battlecruisers, Battleships | ❌ None | Moderate (Battlecruiser / T3C) |
| **C3** | Large | Battleships, Heavy Assault Cruisers | ❌ None | High (Solo Marauder / T3C) |
| **C4** | Large (Dual Static) | Battleships, Marauders, T3C | ❌ None | Very High (Duo Marauders / Fleet) |
| **C5** | Very Large (Capitals) | Dreadnoughts, Force Auxiliaries, Carriers | 🟢 Active Capital Spawns | Extreme (Capital Escalations / 1.5B/hr) |
| **C6** | Massive (Capitals) | Dreadnoughts, Titans (Theoretical) | 🟢 Active Capital Spawns | Maximum (Capital Fleets / 2.5B/hr) |
| **Thera** | Dynamic Multi-K-Space | Sub-capitals | ❌ None | 4+ Dynamic K-Space Statics |
| **C13 (Shattered)** | Small Ships Only | Frigates, Destroyers | ❌ Wolf-Rayet Effect | T3 Destroyers / Stealth Bombers |

---

## ⚡ Wormhole Environmental Anomaly Effects
| Environmental Anomaly | Buffs Applied | Penalties Applied | Tactical Optimization |
| :--- | :--- | :--- | :--- |
| **Wolf-Rayet** | +Small Weapon Damage, +Armor Hitpoints, -Signature Radius | -Shield Resists | Armor T3D / Assault Frigates |
| **Pulsar** | +Shield Hitpoints, +Capacitor Recharge | -Armor Resists, +Signature Radius | Shield Fleets (Cerberus, Basilisk) |
| **Magnetar** | +Weapon Damage, +Targeting Range | -Tracking Speed, -Explosion Velocity | Missile / High Alpha Fleets |
| **Black Hole** | +Missile Velocity, +Ship Max Velocity, +Inertia | -Targeting Range, -Stasis Web Strength | High-Speed Nano Cruisers |
| **Red Giant** | +Heat Damage Overload Bonuses, +Smartbomb Range/Damage | -Overheat Damage Tolerance | Overheated Heavy Armor Brawlers |
| **Cataclysmic Variable**| +Remote Repair Effectiveness, +Capacitor Capacity | -Local Repair Effectiveness | Heavy Logistics Core Fleets |
"""
    with open(wh_file, "w", encoding="utf-8") as f:
        f.write(wh_md)
    created_files.append(wh_file)

    # 2. POCHVEN (TRIGLAVIAN SPACE)
    pochven_dir = os.path.join(VAULT_EVE_DIR, "Pochven")
    os.makedirs(pochven_dir, exist_ok=True)
    pochven_file = os.path.join(pochven_dir, "pochven_cartography_mechanics.md")
    pochven_md = """# EVE Online: Pochven (Triglavian Space) Cartography & Warfare

Technical cartography of the 27 stellar systems severed from New Eden by the Triglavian Collective during the Third Invasion.

---

## 🔺 The Three Clade Domains (27 Star Systems)
- **Krai Svarog (10 Systems)**: Skarkon, Vale, Otela, Sakenta, Wirashoda, Archee, Angymonne, Arvasaras, Harva, Nalvula.
- **Krai Perun (9 Systems)**: Raravoss, Tunudan, Urhinichi, Niarja, Kino, Kaunid, Senda, Ahtila, Ignoitton.
- **Krai Veles (8 Systems)**: Komo, Konotoka, Ichoriya, Ala, Otanuomi, Krirald, Altracy, Kuharah.

---

## 🛰️ Standing Requirements & Conduit Transit
- **+0.00 Triglavian Standing**: Neutral passage through systems (avoiding Triglavian gun emplacements).
- **+3.00 Triglavian Standing**: Unlocks Stargate Conduits between adjacent systems within the same Clade.
- **+7.00 Triglavian Standing**: Unlocks Home System Conduits and Capital ship transit.

---

## 💰 High-Value Operational Activities
- **Observatory Flashpoints**: 15-pilot fleet combat sites paying **3.5 Billion ISK per site + Triglavian Survey Databases**.
- **Beacons & Extraction Sites**: Rich Spodumain, Bezdnacine, and Talassonite ore anomaly harvesting.
- **Filament Extraction**: 'Glorification' and 'Extraction' filaments for instant travel back to Highsec/Lowsec.
"""
    with open(pochven_file, "w", encoding="utf-8") as f:
        f.write(pochven_md)
    created_files.append(pochven_file)

    # 3. ABYSSAL DEADSPACE
    abyssal_dir = os.path.join(VAULT_EVE_DIR, "Abyssal")
    os.makedirs(abyssal_dir, exist_ok=True)
    abyssal_file = os.path.join(abyssal_dir, "abyssal_deadspace_guide.md")
    abyssal_md = """# EVE Online: Abyssal Deadspace Tiers, Weathers, and Optimal Cruiser Fits Theory

Survival protocols, environmental mutators, and ship fitting doctrines for solo cruiser and frigate abyssal runs.

---

## 🌪️ Abyssal Weather Mutators
| Weather Type | Environmental Buff | Environmental Penalty | Optimal Resist / Damage Type |
| :--- | :--- | :--- | :--- |
| **Electrical** | +Capacitor Recharge Rate | -EM Resistance | EM / Thermal (Amarr / Guristas) |
| **Dark** | +Ship Max Velocity | -Turret & Missile Range | High-Speed Close Range Brawlers |
| **Exotic** | +Scan Resolution | -Kinetic Resistance | Kinetic / Thermal (Caldari / Gallente) |
| **Firestorm** | +Armor Hitpoints | -Thermal Resistance | Thermal / Explosive (Armor Tanks) |
| **Gamma** | +Shield Hitpoints | -Explosive Resistance | Explosive / Kinetic (Shield Tanks) |

---

## ⚡ Tier Scaling & Rewards
- **T1 (Calm) / T2 (Agitated)**: Training tiers (T1/T2 Cruisers) — 15M - 35M ISK/hr.
- **T3 (Fierce) / T4 (Raging)**: Mid-tier (HACs / Gila) — 80M - 180M ISK/hr.
- **T5 (Chaotic) / T6 (Cataclysmic)**: High-end (Sacrilege, Cerberus, Ikitursa, Cerberus, Cruiser Duo/Trio) — **350M - 900M ISK/hr + Mutaplasmids**.
"""
    with open(abyssal_file, "w", encoding="utf-8") as f:
        f.write(abyssal_md)
    created_files.append(abyssal_file)

    # 4. INDUSTRY SCHEMATICS & PI RECIPES
    pi_dir = os.path.join(VAULT_EVE_DIR, "Industry_Schematics")
    os.makedirs(pi_dir, exist_ok=True)
    pi_file = os.path.join(pi_dir, "pi_schematics_recipes.md")
    pi_md = """# EVE Online: Planetary Interaction (PI) Complete P0 $\rightarrow$ P4 Schematics

Complete chemical formulas, input ratios, and manufacturing recipes for high-tech planetary commodities and POS fuel blocks.

---

## 🧪 High-Tier Planetary Commodities (P4 Products)
| Commodity (P4) | Output | Primary Inputs (P3 Components) | Applications |
| :--- | :--- | :--- | :--- |
| **Broadcast Node** | 1 unit | Data Chips (P3) + High-Tech Transmitters (P3) + Neocoms (P3) | T2 Citadel Modules / Sovereignty Upgrades |
| **Integrity Response Drones** | 1 unit | Gel-Matrix Biopaste (P3) + Hazardous Waste (P3) + Supercomputers (P3) | Upwell Structures & Capital Components |
| **Nano-Factory** | 1 unit | Industrial Explosives (P3) + Ukomi Superconductors (P3) | Jump Gate Construction / T2 Hulls |
| **Wetware Mainframe** | 1 unit | Biotech Research Reports (P3) + Cryoprotectant Fluid (P3) + Supercomputers (P3) | Supercarrier / Titan Construction |

---

## ⛽ POS & Citadel Fuel Block Recipes (40 Blocks / Run)
- **Inputs Required**:
  - Enriched Uranium (P2): `4 units`
  - Oxygen (P1): `22 units`
  - Mechanical Parts (P2): `4 units`
  - Coolant (P2): `9 units`
  - Heavy Water: `170 units`
  - Liquid Ozone: `350 units`
  - Racial Isotope (Helium / Nitrogen / Hydrogen / Oxygen): `450 units`
"""
    with open(pi_file, "w", encoding="utf-8") as f:
        f.write(pi_md)
    created_files.append(pi_file)

    return created_files
