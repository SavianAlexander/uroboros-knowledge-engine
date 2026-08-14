"""
EVE University (UniWiki) Complete Master Knowledge Vault & Mechanics Engine.

Exhaustive references derived from EVE University knowledge archives:
1. magic_14_and_epic_arcs.md: The Magic 14 Core Skills & Epic Arcs Curriculum
2. manual_piloting_mwd_cloak_vectors.md: Manual Piloting, MWD-Cloak Trick & Transversal Vectors
3. tanking_archetypes_command_bursts.md: Tanking Archetypes & Fleet Command Bursts
4. drones_and_stealth_bombing_runs.md: Drone Mechanics & Stealth Bombing Run Protocols
5. interdictor_bubbles_and_black_ops.md: Warp Bubbles, Interdictors, HIC Infinity Points & Black Ops Bridging
6. mission_blitzing_and_standing_repair.md: Mission Blitzing (L1-L5), LP Stores & Standing Repair
7. t3_reverse_engineering_subsystems.md: T3 Reverse Engineering, Ancient Relics & Subsystems

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
UNI_DIR = os.path.join(VAULT_EVE_DIR, "Eve_University")


def generate_uni_complete_markdown(output_dir: str = UNI_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. MAGIC 14 AND EPIC ARCS
    f1 = os.path.join(output_dir, "magic_14_and_epic_arcs.md")
    m1 = """# EVE University: The Magic 14 Core Skills & Epic Arcs Curriculum

The foundational skill blueprint and narrative epic arcs for every New Eden capsuleer.

---

## 🌟 The Magic 14 Universal Core Skills
These 14 skills apply to **every single ship hull** in EVE Online without exception:

| Category | Skill Name | Effect per Level | Priority |
| :--- | :--- | :--- | :--- |
| **Fitting** | **CPU Management** | `+5% Ship CPU Output` | Essential (Level 5) |
| **Fitting** | **Power Grid Management** | `+5% Ship Powergrid Output` | Essential (Level 5) |
| **Capacitor**| **Capacitor Management** | `+5% Capacitor Capacity` | Essential (Level 5) |
| **Capacitor**| **Capacitor Systems Operation**| `-5% Capacitor Recharge Time` | Essential (Level 5) |
| **Armor** | **Mechanics** | `+5% Hull Structure Hitpoints` | Core (Level 5) |
| **Armor** | **Hull Upgrades** | `+5% Armor Hitpoints` | Core (Level 5 - Unlocks T2 Plates) |
| **Shield** | **Shield Management** | `+5% Shield Capacity` | Core (Level 5) |
| **Shield** | **Shield Operation** | `-5% Shield Recharge Time` | Core (Level 5) |
| **Navigation**| **Spaceship Command** | `+2% Ship Agility` | Core (Level 5) |
| **Navigation**| **Navigation** | `+5% Sub-warp Max Velocity` | Core (Level 5) |
| **Navigation**| **Warp Drive Operation** | `-10% Capacitor needed to Warp`| Core (Level 4) |
| **Navigation**| **Evasive Maneuvering** | `+5% Ship Agility` | Essential (Level 5) |
| **Navigation**| **Acceleration Control** | `+5% Afterburner / MWD Speed` | Core (Level 4) |
| **Targeting** | **Signature Analysis** | `+5% Targeting Scan Resolution`| Core (Level 5) |

---

## 📜 Epic Arcs Compendium
1. **The Blood-Stained Stars (Sisters of EVE)**:
   - 50-mission Level 1 Epic Arc across all 4 empires.
   - Reward: **~25 Million ISK + +8.0% Base Faction Standing** to chosen empire with **zero negative derived standings** to other empires.
2. **Pirate Epic Arcs**:
   - **Guristas (*Smash and Grab*)** / **Angel Cartel (*Right Hand of Zorya*)**:
   - Level 3 Epic Arcs paying **Cynabal / Gila BPCs + massive Pirate LP + ~150M ISK**.
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created_files.append(f1)

    # 2. MANUAL PILOTING & MWD-CLOAK TRICK
    f2 = os.path.join(output_dir, "manual_piloting_mwd_cloak_vectors.md")
    m2 = """# EVE University: Manual Piloting, MWD-Cloak Trick & Transversal Vectors

Tactical flight mechanics for surviving gatecamps, controlling distance, and maximizing damage mitigation.

---

## 🛡️ The MWD + Cloak Trick (Step-by-Step Gatecamp Escape)
Enables heavy Industrials, Blockade Runners, and Battleships to escape bubbled or camped gates with near 100% survival:

```text
[Step 1] Click 'Align To' destination celestial.
[Step 2] IMMEDIATELY (within 0.5s) activate Improved Cloaking Device II.
[Step 3] IMMEDIATELY (within 0.5s) activate 500MN / 50MN Microwarpdrive.
[Step 4] Ship travels cloaked at full MWD speed for 10 seconds.
[Step 5] At 85% MWD cycle (~8.5 seconds), DE-CLOAK and SPAM 'Warp To'.
[Step 6] Ship enters warp instantly upon MWD cycle completion!
```

---

## 🕹️ Manual Piloting & Vector Mechanics
- **Transversal Velocity ($V_t$)**: Perpendicular speed relative to attacker ($V_t = V_{\\text{target}} \\times \\sin(\\theta)$). High transversal minimizes enemy turret hit probability.
- **Radial Velocity ($V_r$)**: Speed directly towards or away from attacker ($V_r = V_{\\text{target}} \\times \\cos(\\theta)$). Zero transversal maximizes weapon damage.
- **Instaundock Bookmarks**: Create bookmark `200km+` directly along the station undock vector. Warping immediately to this bookmark allows zero-alignment instant escape upon undocking.
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created_files.append(f2)

    # 3. TANKING ARCHETYPES & COMMAND BURSTS
    f3 = os.path.join(output_dir, "tanking_archetypes_command_bursts.md")
    m3 = """# EVE University: Tanking Archetypes & Fleet Command Bursts

Comprehensive theory of defense systems and fleet warfare command burst enhancement.

---

## 🛡️ The 6 Tanking Archetypes
1. **Shield Buffer**: Large Shield Extenders + Multispectrum Shield Hardeners (Maximum EHP for fleet alpha protection).
2. **Active Shield**: Shield Boosters + Boost Amplifiers (Sustained local repair for solo/PVE).
3. **Passive Shield**: Shield Power Relays + Shield Rechargers + Purger Rigs (Passive regen without capacitor consumption).
4. **Armor Buffer**: 1600mm / 800mm Steel Plates + Energized Membranes (Compact signature, massive armor pool).
5. **Active Armor**: Armor Repairers + Auxiliary Nano Pumps (Fast repair cycles, high overheat potential).
6. **Hull Tank**: Reinforced Bulkheads + Transverse Bulkheads (Maximum raw structure hitpoints — classic bait tank).

---

## 📢 Fleet Command Bursts Matrix
| Command Burst Category | Primary Modules | Tactical Effect on Fleet |
| :--- | :--- | :--- |
| **Shield Bursts** | Active Shielding, Shield Extension, Shield Resistance | `+Shield HP, +Shield Boost Amount, +All Shield Resists` |
| **Armor Bursts** | Rapid Repair, Armor Reinforcement, Armor Resistance | `+Armor HP, +Armor Rep Amount, +All Armor Resists` |
| **Skirmish Bursts** | Evasive Maneuvers, Interdiction Maneuvers, Rapid Deployment | `+Ship Agility, +Point/Scram Range, +Afterburner/MWD Speed` |
| **Information Bursts**| Electronic Hardening, Sensor Clarification, Electronic Superiority | `+Scan Resolution, +Lock Range, +EWAR Optimal Range` |
| **Mining Bursts** | Laser Optimization, Mining Equipment Preservation | `-Mining Laser Duration (Yield+), -Capacitor Usage` |
"""
    with open(f3, "w", encoding="utf-8") as f:
        f.write(m3)
    created_files.append(f3)

    # 4. DRONES & STEALTH BOMBING RUNS
    f4 = os.path.join(output_dir, "drones_and_stealth_bombing_runs.md")
    m4 = """# EVE University: Drone Mechanics & Stealth Bombing Protocols

Mastery of autonomous drone combat systems and stealth bomber fleet bombing runs.

---

## 🐝 Drone Classes & Bandwidth Architecture
| Drone Tier | Bandwidth per Drone | Max Active (5 Drones) | Tracking Profile | Primary Application |
| :--- | :--- | :--- | :--- | :--- |
| **Light Drones** (*Hobgoblin, Warrior*) | `5 Mbit/s` | `25 Mbit/s` | Extreme Tracking | Frigate & Interceptor elimination |
| **Medium Drones** (*Hammerhead, Valkyrie*)| `10 Mbit/s` | `50 Mbit/s` | Balanced Tracking | Cruiser & Battlecruiser combat |
| **Heavy Drones** (*Ogre, Berserker*) | `25 Mbit/s` | `125 Mbit/s` | Slow Tracking, Huge Alpha| Battleships & Structures |
| **Sentry Drones** (*Garde, Bouncer, Warden*)| `25 Mbit/s` | `125 Mbit/s` | Stationary Long-Range | Extreme range sniper fleets (0-100km) |

---

## 💣 Stealth Bomber Bombing Runs
- **Flight Physics**: Bombs travel in a straight line for **30 km** over **12.0 seconds**, detonating in a **15 km radius**.
- **Bomb Archetypes**:
  - *Scorch (Thermal), Shrapnel (Explosive), Concussion (Kinetic), Electron (EM)*: Deals **6,400 raw damage per bomb**.
  - *Void Bomb*: Drains **1,800 GJ capacitor** instantly from all ships in radius.
  - *Lockbreaker Bomb*: Breaks target locks on all affected fleet vessels.
- **Wave Limit Rule**: Maximum **7 bombs of the exact same damage type** per wave (an 8th bomb will destroy friendly bombs in flight).
"""
    with open(f4, "w", encoding="utf-8") as f:
        f.write(m4)
    created_files.append(f4)

    # 5. INTERDICTOR BUBBLES & BLACK OPS
    f5 = os.path.join(output_dir, "interdictor_bubbles_and_black_ops.md")
    m5 = """# EVE University: Warp Bubbles, Interdictors & Black Ops Bridging

Null-sec area denial, warp mechanics traps, and covert black ops bridging operations.

---

## 🫧 Warp Disruption Bubbles & Interdictors
- **Interdictor Probes (Sabre, Flycatcher, Heretic, Eris)**: Launches warp bubble with **20 km radius** lasting **120 seconds**.
- **Heavy Interdictors (HICs: Broadsword, Onyx, Devoter, Phobos)**:
  - *Warp Disruption Field Generator*: Generates a mobile bubble following the ship.
  - *Focused Script (Infinity Point)*: Concentrates the field into a single-target scram with **infinite point strength**, capable of tackling Supercarriers and Titans through warp core stabilizers.
- **Drag Bubbles & Stop Bubbles**: Anchored in-line with warp gates to pull warping ships out of warp 50-100km short or drag them 50-100km past the gate into ambush webs.

---

## 🥷 Black Ops Bridging & Conduit Jumps
- **Covert Jump Portal Generator**: Consumes Liquid Ozone to bridge covert ships (*Stealth Bombers, Covert Ops, Force Recons, T3C, Blockade Runners*).
- **Conduit Jump**: Transports the Black Ops battleship and up to 30 fleet members directly to a Covert Cyno beacon in a single click.
"""
    with open(f5, "w", encoding="utf-8") as f:
        f.write(m5)
    created_files.append(f5)

    # 6. MISSION BLITZING & STANDING REPAIR
    f6 = os.path.join(output_dir, "mission_blitzing_and_standing_repair.md")
    m6 = """# EVE University: Mission Blitzing (L1 - L5), LP Stores & Standing Repair

Economic optimization of security mission running and diplomatic standings repair.

---

## 🎯 Level 4 / 5 Mission Blitzing Strategy
- **The Blitz Principle**: Complete only fast objective missions (kill target commander / destroy structure) in 2-4 minutes; decline slow full-clear missions.
- **Loyalty Point (LP) Conversion**:
  - Security missions award **15,000 - 30,000 LP per mission**.
  - LP Store items (*Faction Ammo, Pirate Implants, Faction Cruisers*) convert LP at **1,800 – 2,500 ISK per LP** (~**300M – 600M ISK/hr**).

---

## 🤝 Standing Repair & Social Skills
- **Diplomacy**: Increases effective standing with factions that hate you (+4% per level applied to negative standing floor).
- **Connections**: Increases effective standing with friendly factions (+4% per level).
- **Derived Standings**: Gaining standing with one faction impacts other empires based on the geopolitical matrix.
"""
    with open(f6, "w", encoding="utf-8") as f:
        f.write(m6)
    created_files.append(f6)

    # 7. T3 REVERSE ENGINEERING & SUBSYSTEMS
    f7 = os.path.join(output_dir, "t3_reverse_engineering_subsystems.md")
    m7 = """# EVE University: Tech 3 Reverse Engineering, Ancient Relics & Subsystems

Manufacturing pipelines for Tech 3 Strategic Cruisers (Legion, Tengu, Proteus, Loki) and Tactical Destroyers.

---

## 🔬 Tech 3 Reverse Engineering Pipeline
$$\\text{Ancient Relic (Wormholes)} + \\text{Hybrid Decryptor} + \\text{Datacores} \\longrightarrow \\text{T3 Subsystem BPC (3-Run)}$$

### Ancient Relic Quality Grades:
- **Intact Relics**: `50% Base Success Chance` | 3-run BPC output
- **Malfunctioning Relics**: `30% Base Success Chance` | 2-run BPC output
- **Wrecked Relics**: `20% Base Success Chance` | 1-run BPC output

---

## 🛠️ The 4 Modular Subsystem Slots
1. **Core Subsystem**: Capacitor pool, drone bandwidth, or probe launcher bonuses.
2. **Defensive Subsystem**: Armor buffer, shield buffer, or covert cloak reconfiguration.
3. **Offensive Subsystem**: Turret/Missile damage multipliers, drone bay expansion.
4. **Propulsion Subsystem**: Interdiction nullification, agility bonuses, or warp velocity scaling.
"""
    with open(f7, "w", encoding="utf-8") as f:
        f.write(m7)
    created_files.append(f7)

    return created_files
