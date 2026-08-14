"""
EVE Online Sovereign Anomalies, Capital Warfare, Jump Drive Navigation & Crimewatch Engine.

Exhaustive references for:
- Sovereign Nullsec Combat Anomalies (Havens, Sanctums, Forsaken Hubs, NPC Dread Spawns, I-Hub Upgrades)
- Capital & Supercapital Warfare (Dreadnought Siege, FAX Triage, Supercarrier Fighters, Titan Doomsdays)
- Jump Drive Physics, Cynosural Corridors & Jump Fatigue Physics
- Crimewatch 2.0, Concord Response Timers & Security Status Tag Economics

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

ANOMALY_DIR = os.path.join(VAULT_EVE_DIR, "Combat_Anomalies")
CAPITALS_DIR = os.path.join(VAULT_EVE_DIR, "Capitals")
NAV_DIR = os.path.join(VAULT_EVE_DIR, "Navigation")
COMBAT_DIR = os.path.join(VAULT_EVE_DIR, "Combat_Mechanics")


def generate_anomalies_capitals_markdown() -> list:
    created_files = []

    # 1. SOVEREIGN COMBAT & MINING ANOMALIES
    os.makedirs(ANOMALY_DIR, exist_ok=True)
    anom_file = os.path.join(ANOMALY_DIR, "sovereign_combat_mining_anomalies.md")
    anom_md = """# EVE Online: Sovereign Null-Sec Combat & Mining Anomalies Compendium

Tactical blueprints for sovereign anomaly farming, I-Hub upgrades, wave management, and capital escalation triggers.

---

## 🎯 Null-Sec Sovereign Combat Anomalies (Pirate Detection Array Level 5)
| Anomaly Type | Wave Count | Primary NPC Battleship Count | Bounty Yield / Tick (20 min) | Escalation Chance |
| :--- | :--- | :--- | :--- | :--- |
| **Haven (Stargate)** | 4 Waves | 12 - 16 Battleships | **22M – 35M ISK / tick** | **~5.0% (10/10 DED Complex)** |
| **Haven (Gas Nebula)**| 4 Waves | 12 - 16 Battleships | **22M – 35M ISK / tick** | **~5.0% (10/10 DED Complex)** |
| **Sanctum (Ring)** | 4 Waves | 14 - 18 Battleships | **25M – 40M ISK / tick** | **~5.0% (10/10 DED Complex)** |
| **Sanctum (Station)** | 4 Waves | 14 - 18 Battleships | **25M – 40M ISK / tick** | **~5.0% (10/10 DED Complex)** |
| **Forsaken Hub** | 3 Waves | 9 - 12 Battleships | **18M – 28M ISK / tick** | Rare Escalation |
| **Forsaken Rally Point**| 3 Waves | 6 - 9 Battleships | **15M – 22M ISK / tick** | Rare Escalation |

---

## ☠️ NPC Capital Spawns & Faction Commanders
- **Faction Commander Spawns** (*Dark Blood, Shadow Serpentis, Dread Guristas, True Sansha, Domination*):
  - Spawns in final wave with a **3% chance**.
  - Drops **Faction Ammo, Faction Modules, and Rare Ship Blueprints (Cynabal, Gila, Phantasm)**.
- **NPC Capital Dreadnought Spawns** (*Blood / Sansha / Guristas Dreadnought*):
  - Spawns randomly in Havens/Sanctums; deals massive capital turret/missile damage.
  - **Flat Bounty**: **60,000,000 ISK** + Capital Faction Modules.

---

## ⛏️ Sovereign Mining Anomalies (Ore Prospecting Array Level 5)
- **Colossal Asteroid Cluster**: Yields massive Spodumain, Arkonor, Bistot, and Crokite fields (**~1.5 Billion ISK total mineral value**).
- **Enormous Asteroid Cluster**: Spawns Gneiss, Dark Ochre, and Spodumain.
"""
    with open(anom_file, "w", encoding="utf-8") as f:
        f.write(anom_md)
    created_files.append(anom_file)

    # 2. CAPITAL & SUPERCAPITAL WARFARE VAULT
    os.makedirs(CAPITALS_DIR, exist_ok=True)
    cap_file = os.path.join(CAPITALS_DIR, "capital_supercapital_warfare_vault.md")
    cap_md = """# EVE Online: Capital, FAX, Supercarrier & Titan Warfare Vault

Tactical doctrine guide for capital-class fleet engagements and doomsday deployment mechanics.

---

## 💥 Capital Ship Class Architectures
| Capital Class | Operational Role | Key Tactical Module | Combat Capability |
| :--- | :--- | :--- | :--- |
| **Dreadnought** | Capital Anti-Structure & Anti-Cap | **Siege Module I / II** | +700% Turret/Missile DPS, 10,000 - 15,000 DPS output |
| **Force Auxiliary (FAX)** | Capital Remote Armor/Shield Logi | **Triage Module I / II** | 40,000 HP/sec remote repair, immune to EWAR in triage |
| **Carrier** | Sub-capital Fleet Suppression | **Networked Sensor Array** | Deploys 3 Light Fighter Squadrons (Attack/Air Superiority) |
| **Supercarrier** | Heavy Strike & Anti-Capital | **Burst Projector Modules** | Deploys 5 Squadrons (3 Light + 2 Heavy Torpedo Fighters) |
| **Titan** | Sovereign Flagship & Strategic Alpha | **Doomsday Device** | **Instant 1.5 Million to 2.5 Million Damage Strike** |

---

## ⚡ Titan Doomsday Weapons Matrix
- **Directed Energy Doomsdays** (*Judgement, Gjallarhorn, Oblivion, Aurora*): Single-target ray dealing **1,500,000 HP raw damage** (instantly obliterates Dreadnoughts/Carriers without buffer).
- **Lance Weapons**: Area-of-effect directional beam dealing massive multi-target thermal/EM damage.
- **Bosonic Field Generator**: Frontal AoE energy field evaporating entire sub-capital battlecruiser/cruiser fleets in seconds.
"""
    with open(cap_file, "w", encoding="utf-8") as f:
        f.write(cap_md)
    created_files.append(cap_file)

    # 3. JUMP DRIVE NAVIGATION & FATIGUE
    os.makedirs(NAV_DIR, exist_ok=True)
    nav_file = os.path.join(NAV_DIR, "jump_drive_cyno_navigation.md")
    nav_md = """# EVE Online: Jump Drive Navigation, Cyno Corridors & Jump Fatigue Physics

Mathematical formulas and logistics planning for Capital Ships, Jump Freighters, and Black Ops.

---

## 📐 Jump Distance & Range Physics
$$\\text{Distance (LY)} = \\sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2 + (Z_2 - Z_1)^2} \\times \\text{Scale}$$

### Maximum Jump Range by Class (with Jump Drive Calibration V):
- **Jump Freighters (Nomad, Ark, Rhea, Anshar)**: **10.0 Light Years**
- **Black Ops Battleships (Redeemer, Panther, Widow, Sin)**: **10.0 Light Years**
- **Capitals (Dreadnoughts, FAX, Carriers, Titans)**: **7.0 Light Years**

---

## ⏳ Jump Fatigue Mathematics
$$\\text{New Fatigue} = \\max(10 \\text{ minutes}, \\text{Current Fatigue} \\times (1 + \\text{Distance Travelled in LY}))$$

$$\\text{Jump Activation Cooldown} = \\frac{\\text{Jump Fatigue}}{10}$$

- **Fatigue Cap**: Maximum fatigue is capped at **5.0 Hours** (300 minutes), ensuring maximum jump cooldown never exceeds **30 minutes**.
- **Jump Freighter / Industrial Bonus**: Jump Freighters receive a **90% reduction to Jump Fatigue accumulation**.

---

## 🛰️ Cynosural Field Generator Types
- **Standard Cyno**: Fits on Force Recon Ships and Heavy Industrials; lights beacon for all capital ships.
- **Covert Cyno**: Fits on Covert Ops, Blockade Runners, T3C; undetectable on overview; allows Black Ops and covert bridges.
- **Industrial Cyno**: Fits on standard T1 Haulers and Ventures; lights beacon exclusively for Jump Freighters.
"""
    with open(nav_file, "w", encoding="utf-8") as f:
        f.write(nav_md)
    created_files.append(nav_file)

    # 4. CRIMEWATCH 2.0 & CONCORD RESPONSE
    os.makedirs(COMBAT_DIR, exist_ok=True)
    crime_file = os.path.join(COMBAT_DIR, "crimewatch_security_status_guide.md")
    crime_md = """# EVE Online: Crimewatch 2.0, Concord Response Timers & Security Economics

Legal flag mechanics, highsec response timers, and security status restoration calculations.

---

## ⏱️ CONCORD Response Times in High-Sec
When an illegal criminal act occurs (e.g. ganking a hauler in highsec):

| System Security Level | CONCORD Response Time (Un-pre-spawned) | CONCORD Response Time (Pre-spawned on Grid) |
| :--- | :--- | :--- |
| **1.0 Security** | **6 Seconds** | **Zero / Instant** |
| **0.9 Security** | **6 Seconds** | **Zero / Instant** |
| **0.8 Security** | **8 Seconds** | **Zero / Instant** |
| **0.7 Security** | **11 Seconds** | **Zero / Instant** |
| **0.6 Security** | **14 Seconds** | **Zero / Instant** |
| **0.5 Security** | **19 Seconds (Maximum window for suicide ganks)**| **Zero / Instant** |

---

## 🏷️ Tags for Security Status Restoration (CONCORD Stations)
| Security Status Range | Required Tag | Tags Needed per 0.5 Status Gain |
| :--- | :--- | :--- |
| **-10.0 to -8.0** | **Clone Soldier Trainer Tag** | 1 Tag per +0.5 Status |
| **-8.0 to -5.0** | **Clone Soldier Recruiter Tag** | 1 Tag per +0.5 Status |
| **-5.0 to -2.0** | **Clone Soldier Hunter Tag** | 1 Tag per +0.5 Status |
| **-2.0 to 0.0** | **Clone Soldier Executive Tag** | 1 Tag per +0.5 Status |
"""
    with open(crime_file, "w", encoding="utf-8") as f:
        f.write(crime_md)
    created_files.append(crime_file)

    return created_files
