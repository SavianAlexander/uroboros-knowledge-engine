"""
EVE Online Official Expansions, Dogma Physics, Equinox Sovereignty & Asset Safety RAG Engine.

Exhaustive official references for:
- Expansion Blueprints (Equinox Orbital Skyhooks, Havoc Insurgencies, Viridian Lancer Dreads, Uprising Frontlines)
- Official Dogma Stacking Penalty Calculus: S(n) = e^(-(n-1)^2 / 7.1289)
- Equinox Sovereignty Infrastructure Grid (Power, Workforce, Magmatic Gas & Superionic Ice Topology)
- Official Asset Safety Governance, Corporation Projects & War Declarations

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

EXP_DIR = os.path.join(VAULT_EVE_DIR, "Expansions")
COMBAT_DIR = os.path.join(VAULT_EVE_DIR, "Combat_Mechanics")
SOV_DIR = os.path.join(VAULT_EVE_DIR, "Sovereignty")
CORP_DIR = os.path.join(VAULT_EVE_DIR, "Corporate_Governance")


def generate_official_rag_markdown() -> list:
    created_files = []

    # 1. EXPANSIONS (EQUINOX, HAVOC, VIRIDIAN, UPRISING)
    os.makedirs(EXP_DIR, exist_ok=True)
    f1 = os.path.join(EXP_DIR, "official_expansions_equinox_havoc_viridian.md")
    m1 = """# EVE Online: Official Expansion Compendium (Equinox, Havoc, Viridian, Uprising)

Technical analysis of modern major expansions reshaping New Eden's sovereignty, warfare, and industrial supply chains.

---

## 🌌 EVE Online: Equinox Expansion (2024 - 2026)
- **Sovereignty Hubs**: Replaces legacy I-Hubs and Territorial Claim Units (TCUs) with unified planetary resource grids.
- **Orbital Skyhooks**: Structures anchored above planets extracting **Power, Workforce, Magmatic Gas, and Superionic Ice**.
- **Upwell Transport Ships**: Specialized freighters and haulers for liquid gas and reagent hauling (*Avalanche, Squall, Deluge, Torrent*).

---

## 🏴‍☠️ EVE Online: Havoc Expansion
- **Pirate Insurgencies**: Angel Cartel and Guristas pirate factions invade Faction Warfare warzones and Zarzakh.
- **Corruption vs Suppression Mechanics**:
  - **Corruption Level 5**: Removes gate guns, enables warp bubbles in Lowsec, and spawns pirate sentry guns.
  - **Suppression Level 5**: Upgrades empire police response, installs automated defense webs and gate turrets.
- **Pirate Faction Capital Ships**:
  - **Azariel** (Angel Cartel Titan) & **Caiman** (Guristas Dreadnought).
  - **Khizriel** (Angel Battlecruiser) & **Alligator** (Guristas Battlecruiser).

---

## 🛡️ EVE Online: Viridian & Uprising Expansions
- **Tech II Lancer Dreadnoughts** (*Bane, Karura, Hubris, Valravn*): Equipped with **Disruptive Lance Weapons** that disable target jump drives and tethering.
- **Corporation Projects**: Automated task creation rewarding member pilots with liquid ISK upon milestone completion.
- **FW Frontlines**: Divides warzones into Frontlines (highest LP rewards), Command Operations, and Rearguards.
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created_files.append(f1)

    # 2. OFFICIAL DOGMA STACKING PENALTY CALCULUS
    os.makedirs(COMBAT_DIR, exist_ok=True)
    f2 = os.path.join(COMBAT_DIR, "official_dogma_stacking_penalty_math.md")
    m2 = """# EVE Online: Official Dogma Engine & Module Stacking Penalty Calculus

The exact mathematical formulation utilized by the CCP Dogma game engine for diminishing returns on module stacking.

---

## 📐 The Dogma Stacking Penalty Equation
For the $n$-th module affecting the same statistic ($n \\ge 1$):

$$S(n) = e^{-\\frac{(n - 1)^2}{7.1289}} = e^{-\\frac{(n - 1)^2}{2 \\times (1.8879)^2}}$$

### 📊 Exact Efficiency Multipliers per Module:
| Module Rank ($n$) | Theoretical Formula | Exact Multiplier | Relative Effectiveness |
| :--- | :--- | :--- | :--- |
| **1st Module** | $S(1) = e^0$ | **1.000000** | **100.00%** |
| **2nd Module** | $S(2) = e^{-1/7.1289}$ | **0.869119** | **86.91%** |
| **3rd Module** | $S(3) = e^{-4/7.1289}$ | **0.571028** | **57.10%** |
| **4th Module** | $S(4) = e^{-9/7.1289}$ | **0.282956** | **28.30%** |
| **5th Module** | $S(5) = e^{-16/7.1289}$ | **0.105999** | **10.60%** |
| **6th Module** | $S(6) = e^{-25/7.1289}$ | **0.029991** | **3.00%** |
| **7th Module+**| $S(7) = e^{-36/7.1289}$ | **0.006408** | **< 0.64% (Hard Floor)**|

---

## 🛡️ Penalized vs Non-Penalized Modules
- **Penalized Modules**: Gyrostabilizers, Magnetic Field Stabilizers, Heat Sinks, Ballistic Control Systems, Magnetic/Shield/Armor Hardeners, Inertial Stabilizers, Overdrive Injectors, Tracking Enhancers.
- **Non-Penalized Modules**: Damage Control II, Reactive Armor Hardener, Reinforced Bulkheads, 1600mm Steel Plates, Large Shield Extenders, Ancillary Armor Repairers.
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created_files.append(f2)

    # 3. EQUINOX SOVEREIGNTY POWER & REAGENT TOPOLOGY
    os.makedirs(SOV_DIR, exist_ok=True)
    f3 = os.path.join(SOV_DIR, "equinox_sovereignty_hub_power_reagents.md")
    m3 = """# EVE Online: Equinox Sovereignty Topology — Power, Workforce & Reagents

Architectural planning for sovereign Nullsec solar systems under the Equinox resource paradigm.

---

## ⚡ The 3 Sovereignty Currencies
1. **Power (Megawatts - MW)**: Generated by solar radiation and planetary magnetic fields; fuels defensive cyno beacons, jammer systems, and industrial arrays.
2. **Workforce (Citizens)**: Harvested from Temperate, Oceanic, and Barren planets via Skyhooks; operates anomaly detection and mining prospecting arrays.
3. **Reagents (Magmatic Gas & Superionic Ice)**:
   - **Magmatic Gas**: Extracted from Lava planets; required for military anomaly upgrade sustainment.
   - **Superionic Ice**: Extracted from Ice planets; required for capital shipyard and industry array sustainment.

---

## 🛰️ Sovereign Upgrade Power Grids
- **Cynosural Jammer**: Consumes **1,200 MW Power** + constant reagent upkeep.
- **Supercapital Construction Facilities**: Consumes **2,500 MW Power + 1,000 Workforce**.
- **Pirate Detection Array Level 5**: Consumes **800 MW Power + 600 Workforce + 100 Magmatic Gas / hr**.
"""
    with open(f3, "w", encoding="utf-8") as f:
        f.write(m3)
    created_files.append(f3)

    # 4. OFFICIAL ASSET SAFETY & WAR DECLARATION GOVERNANCE
    os.makedirs(CORP_DIR, exist_ok=True)
    f4 = os.path.join(CORP_DIR, "official_asset_safety_wardec_protocols.md")
    m4 = """# EVE Online: Official Asset Safety Governance & War Declaration Protocols

Regulatory mechanics for hangar preservation, station destruction, and corporate warfare.

---

## 📦 Official Asset Safety Protocols
When an Upwell Citadel is destroyed or unanchored in Highsec, Lowsec, or Nullsec:

1. **Asset Safety Wrap**: All personal and corporate hangar items are instantly placed into an unraidable Asset Safety Container.
2. **Delivery Timelines**:
   - **Manual Release**: Can be triggered after **5 Days** to same system station.
   - **Automated Delivery**: After **21 Days**, automatically transferred to the nearest NPC Lowsec station.
3. **Recovery Fees**:
   - **0.5% Fee**: If recovered in the same solar system.
   - **15.0% Fee**: If recovered from the nearest Lowsec NPC station.
4. **⚠️ The Wormhole Exception**: In **J-Space (C1 - C6 Wormholes)**, **Asset Safety is completely DISABLED**. 100% of all hangar items drop as lootable wrecks upon citadel destruction.

---

## ⚔️ Corporate War Declarations (War HQ System)
- **War Eligibility**: Corporations/Alliances must own an anchored Upwell Structure to declare or be declared war upon.
- **War HQ**: The attacking corporation must designate a specific structure as their **War HQ**. Destroying the War HQ immediately terminates the war.
- **Warm-Up Period**: Exactly **24.0 Hours** from war declaration until CONCORD authorizes legal open PvP.
"""
    with open(f4, "w", encoding="utf-8") as f:
        f.write(m4)
    created_files.append(f4)

    return created_files
