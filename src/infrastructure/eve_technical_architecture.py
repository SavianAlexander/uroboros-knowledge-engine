"""
EVE Online Low-Level Technical Architecture, Server Simulation & Mathematical Engines.

Exhaustive references for:
- 1-Hz Server Tick Micro-Phase Scheduling & Time Dilation (TiDi) Simulation Engine
- Cosmic Scanning Probe Deviation & Relic/Data Hacking Virus Calculus
- Dynamic System Cost Index (SCI) & Industrial Job Duration Formulation
- Smartbomb Spherical AoE Physics & Ship Collision Momentum Bump Dynamics

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
TECH_DIR = os.path.join(VAULT_EVE_DIR, "Technical_Architecture")


def generate_technical_architecture_markdown() -> list:
    os.makedirs(TECH_DIR, exist_ok=True)
    created_files = []

    # 1. 1-HZ SERVER TICK & TIDI ENGINE
    f1 = os.path.join(TECH_DIR, "server_tick_1hz_tidi_simulation.md")
    m1 = """# EVE Online: 1-Hz Server Tick Scheduling & Time Dilation (TiDi) Engine

Low-level architecture of Tranquility's simulation loop, tick phases, and load-shedding mechanisms.

---

## ⏱️ The 1000ms (1-Hz) Server Heartbeat Loop
Every single solar system simulation node executes a discrete 1.0-second loop partitioned into 5 micro-phases:

```mermaid
graph TD
    P1["Phase 1: Inbound Command Queuing (Lock requests, Module clicks, Warp commands)"]
    P2["Phase 2: Spatial Physics Simulation (Velocity integration, Align vectors, Collisions)"]
    P3["Phase 3: Dogma Module State Processing (Capacitor deductions, Gun cycle completions, EWAR)"]
    P4["Phase 4: Damage Calculation & Hull Depletion (Wreck instantiation, Pod ejection)"]
    P5["Phase 5: World State Delta Broadcast (UDP/TCP packet transmission to all grid clients)"]

    P1 --> P2 --> P3 --> P4 --> P5
```

---

## ⏳ Time Dilation (TiDi) Mechanics
- **Trigger**: When total compute time for a 1.0-second tick exceeds **850ms**, the simulation slows down proportionally.
- **TiDi Floor (10%)**: Minimum clock speed is **10%** (1 real-world second = 10 game seconds).
- **Benefit**: Completely eliminates packet dropping and desync, preserving 100% deterministic combat accuracy in 5,000+ player fleet battles (*e.g. M2-XFE, FWST-8*).
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created_files.append(f1)

    # 2. SCANNING PROBE DEVIATION & HACKING CALCULUS
    f2 = os.path.join(TECH_DIR, "scanning_probe_hacking_calculus.md")
    m2 = """# EVE Online: Cosmic Scanning Probe Mathematics & Hacking Calculus

Mathematical models for signature triangulation, probe deviation radii, and virus subroutines.

---

## 📡 Scanning Probe Deviation Radius Formula
$$\\text{Deviation (km)} = \\frac{D_{\\text{base}}}{\\text{Total Scan Strength}} \\times (1 - 0.05 \\times \\text{Astrometric Pinpointing})$$

- **Signal Lock Equation**: A signature reaches **100% lock (Warpable)** when the composite signal strength across all 8 overlapping probe spheres reaches $\\ge 1.00$.

---

## 💻 Relic & Data Hacking Virus Architecture
- **Virus Coherence (Hitpoints)**: `Coherence = Base + (Hacking Skill × 10) + Rig Bonuses`.
- **Virus Strength (Attack)**: Standard Data/Relic analyzer delivers **20 to 40 Attack** per strike.
- **Defensive Subroutines Matrix**:
  - *Restoral Node*: Regenerates **+20 HP** to all un-hacked nodes each turn (Kill Priority #1).
  - *Virus Suppressor*: Reduces player Virus Attack by **-10 Attack** (Kill Priority #2).
  - *Firewall*: High hitpoint obstacle (80 HP, 10 Attack).
  - *Anti-Virus*: High strike obstacle (40 HP, 40 Attack).
- **The Rule of 6**: Safe nodes located 6 steps away from core data structures are guaranteed free of defensive traps.
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created_files.append(f2)

    # 3. SYSTEM COST INDICES & MANUFACTURING FORMULAS
    f3 = os.path.join(TECH_DIR, "system_cost_indices_manufacturing_math.md")
    m3 = """# EVE Online: Dynamic System Cost Index (SCI) & Manufacturing Calculus

Formulation of industrial manufacturing job fees, duration scaling, and material efficiency.

---

## 💰 Dynamic System Cost Index (SCI) Formula
$$\\text{SCI}_{\\text{activity}} = \\sqrt{\\frac{\\text{Gross System Production (28 Days)}}{\\text{Universe Gross Production (28 Days)}}}$$

### Exact Job Installation Fee Equation:
$$\\text{Job Fee} = \\text{Estimated Item Value (EIV)} \\times \\text{SCI} \\times \\text{Facility Cost Multiplier} \\times (1 + \\text{Facility Tax})$$

---

## ⏱️ Industrial Job Duration Scaling
$$\\text{Job Duration} = T_{\\text{base}} \\times (1 - \\text{TE}_{\\text{Blueprint}}) \\times (1 - 0.04 \\times \\text{Industry Skill}) \\times \\text{Structure Time Rig Multiplier}$$

- **Material Efficiency (ME 10)**: Conserves **10.0% of raw minerals/components**.
- **Time Efficiency (TE 20)**: Reduces base production duration by **20.0%**.
"""
    with open(f3, "w", encoding="utf-8") as f:
        f.write(m3)
    created_files.append(f3)

    # 4. SMARTBOMB AOE & SHIP BUMP PHYSICS
    f4 = os.path.join(TECH_DIR, "smartbomb_aoe_bump_physics.md")
    m4 = """# EVE Online: Smartbomb Spherical AoE Physics & Ship Collision Bump Mechanics

Instantaneous area-of-effect damage propagation and momentum transfer mechanics.

---

## 💥 Smartbomb Spherical AoE Matrix
| Module Size | Blast Radius | Raw Damage per Cycle | Cycle Duration | Tracking Check |
| :--- | :--- | :--- | :--- | :--- |
| **Small Smartbomb** | **2,500 m** | 75 HP | 5.0 Seconds | **Zero / Instant (100% Hit)** |
| **Medium Smartbomb**| **5,000 m** | 150 HP | 7.5 Seconds | **Zero / Instant (100% Hit)** |
| **Large Smartbomb** | **7,500 m** | 300 - 375 HP | 10.0 Seconds | **Zero / Instant (100% Hit)** |
| **Officer Smartbomb**| **10,000 m** | 450 HP | 10.0 Seconds | **Zero / Instant (100% Hit)** |

- **Pipebombing Protocol**: Rokh / Megathron battleships light smartbombs simultaneously on warp-in vectors, vaporizing whole Cruiser/Battlecruiser fleets in a single server tick.

---

## 🚀 Ship Collision & Momentum Bump Physics
Momentum is conserved during ship collisions:

$$m_1 \\vec{v}_1 + m_2 \\vec{v}_2 = m_1 \\vec{v}_1' + m_2 \\vec{v}_2'$$

- **The Machariel Bump Tactic**: A 3,000 m/s 500MN MWD Machariel colliding with an aligned Freighter transfers massive momentum, knocking the target **20-30 km off its warp vector** and resetting the 75% alignment threshold.
"""
    with open(f4, "w", encoding="utf-8") as f:
        f.write(m4)
    created_files.append(f4)

    return created_files
