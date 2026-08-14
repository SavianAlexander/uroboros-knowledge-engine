"""
EVE Online Sansha Incursions & Pochven Flashpoint Multi-Box Blueprints.

Comprehensive high-income multi-box operational doctrines:
- Sansha Incursions (Vanguard 10-man, Assault 20-man, Headquarters 40-man)
- Pochven Observatory Flashpoint (OFP) 15-man Marauder / Nestor fleets
- Income velocity models (250M - 1.2B ISK/hr per pilot)

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
FLEET_OPS_DIR = os.path.join(VAULT_EVE_DIR, "Fleet_Operations")


def generate_incursions_pochven_markdown() -> list:
    os.makedirs(FLEET_OPS_DIR, exist_ok=True)
    created = []

    # 1. Incursions
    f1 = os.path.join(FLEET_OPS_DIR, "sansha_incursions_blueprint.md")
    m1 = """# Sansha Incursions Fleet Doctrine & Payout Mechanics

Highsec / Lowsec PvE fleet operations countering Nation Incursions across New Eden.

---

## 🌐 Incursion Site Tiers & Fleet Sizes
| Site Tier | Fleet Size | Completion Time | Payout per Pilot | ISK / Hour Potential |
| :--- | :---: | :---: | :---: | :---: |
| **Vanguard (VG)** | **10 Pilots** | **6 – 9 Minutes** | **15.0M ISK + 2,000 CONCORD LP** | **~120M – 180M ISK/hr** |
| **Assault (AS)** | **20 Pilots** | **12 – 18 Minutes** | **20.5M ISK + 3,500 CONCORD LP** | **~150M – 200M ISK/hr** |
| **Headquarters (HQ)**| **40 Pilots** | **15 – 25 Minutes** | **31.5M ISK + 7,000 CONCORD LP** | **~250M – 350M ISK/hr** |

---

## 🛡️ Standard Incursion Line Fleet Composition (Shield Meta)
- **Primary Line Battleships**:
  - **Nightmare**: Tachyon Beam Lasers (EM / Thermal damage matching Sansha weakness).
  - **Vindicator**: Neutron Blaster Cannons + 90% Fed Navy Stasis Webifiers (Web anchor).
  - **Machariel**: 800mm Repeating Cannons (High warp speed, rapid target switching).
- **Logistics Core**:
  - **Basilisk** (Cap-transfer chain) / **Scimitar** (Cap-stable remote shield boost).
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created.append(f1)

    # 2. Pochven Flashpoints
    f2 = os.path.join(FLEET_OPS_DIR, "pochven_flashpoint_multibox.md")
    m2 = """# Pochven Observatory Flashpoint (OFP) Multi-Box Blueprint

The highest liquid ISK printing PvE engine in EVE Online (3.5 Billion ISK per site payout).

---

## 💰 Observatory Flashpoint (OFP) Metrics
- **Target Fleet Size**: **Exactly 15 Pilots** (Payout drops if > 15 pilots on grid).
- **Site Payout**: **3.5 Billion ISK Total** ($\approx$ **233.3 Million ISK per pilot** per site).
- **Site Clear Duration**: **12 – 15 Minutes**.
- **Net Hourly Yield**: **~850 Million to 1.1 Billion ISK/hr per pilot**.

---

## 🚀 15-Box Optimal Fleet Archetype
```mermaid
graph TD
    subgraph "15-Man Multi-Box OFP Fleet Composition"
        D1["👑 4x Paladin (Mega Pulse Laser II + Conflagration M)"]
        D2["💥 4x Kronos (Neutron Blaster Cannon II + Void M)"]
        D3["🎯 4x Vargur (800mm Repeating Cannon II + Hail M)"]
        Logi["🛡️ 3x Nestor (Spider-Tanking Remote Armor Reps + Cap Chain)"]

        D1 -->|Bastion Firepower| Boss["Triglavian Stellar Transmuter Boss"]
        D2 -->|Point-Blank DPS| Boss
        D3 -->|Web & Tracking| Boss
        Logi -->|Cross-Remote Reps| D1
        Logi -->|Cross-Remote Reps| D2
        Logi -->|Cross-Remote Reps| D3
    end
```
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created.append(f2)

    return created
