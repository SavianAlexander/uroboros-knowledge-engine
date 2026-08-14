"""
EVE Online Wormhole Operations, J-Space Statics & Space Weather Engine.

Comprehensive technical guide to Anoikis (Wormhole Space):
- Classes C1 through C6, Thera, and Drifter / Shattered wormholes
- Mass Limits & Jump Restrictions (Frigate, Medium, Large, Capital)
- Space Weather Phenomona (Wolf-Rayet, Pulsar, Magnetar, Cataclysmic, Red Giant, Black Hole)
- Polarization timer (5 minutes) and Collapse Thresholds (Stage 1 / Stage 2 / Critical)

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
WH_DIR = os.path.join(VAULT_EVE_DIR, "Wormhole_Operations")

WEATHER_EFFECTS = {
    "Wolf-Rayet Star": {
        "buffs": "+100% Small Weapon Damage, +100% Armor HP, +50% Small Remote Rep",
        "debuffs": "-50% Shield Resistances, +50% Signature Radius",
        "doctrine": "Confessor / Kikimora / T3D Small Brawler Wolfpack"
    },
    "Pulsar": {
        "buffs": "+100% Shield HP, +50% Capacitor Recharge Rate",
        "debuffs": "-50% Armor Resistances, +100% Signature Radius",
        "doctrine": "Shield Marauders (Golem) / Shield Battleships (Rokh / Cerberus)"
    },
    "Magnetar": {
        "buffs": "+100% Turret & Missile Damage, +100% Target Painter Effectiveness",
        "debuffs": "-50% Turret Tracking, -50% Missile Explosion Velocity, -50% Drone Tracking",
        "doctrine": "Alpha Strike Artillery / Heavy Missile Kite Fleets"
    },
    "Cataclysmic Variable": {
        "buffs": "+100% Remote Armor & Remote Shield Repair Amount",
        "debuffs": "-50% Local Repair Effectiveness, -50% Capacitor Recharge Rate",
        "doctrine": "Heavy Spider-Tanking Battleship / Triage Dreadnought Cap Chain"
    },
    "Red Giant": {
        "buffs": "+100% Smartbomb Damage & Range, +100% Overheat Bonus",
        "debuffs": "+100% Heat Damage Taken",
        "doctrine": "Smartbombing Battleship Pipebombs & Assault Frigates"
    },
    "Black Hole": {
        "buffs": "+100% Ship Sub-warp Velocity, +50% Missile Velocity",
        "debuffs": "+50% Inertia (Slower Align), -50% Targeting Range",
        "doctrine": "Fast Nano-Cruisers (Vagabond, Orthrus, Cynabal)"
    }
}


def generate_wormhole_markdown() -> list:
    os.makedirs(WH_DIR, exist_ok=True)
    created = []

    # 1. J-Space Mechanics
    f1 = os.path.join(WH_DIR, "jspace_wormhole_mechanics.md")
    m1 = """# Wormhole Operations: J-Space Classifications & Statics

Complete navigation and mass transit doctrine across J-Space system classes (C1 through C6).

---

## 🌐 Wormhole System Classes
| System Class | Maximum Ship Size Allowed | Native Statics | Capital Escalation Sites |
| :--- | :--- | :--- | :---: |
| **C1 (Class 1)** | Battlecruisers / Industrials (Medium Holes) | Highsec / Lowsec | ❌ No |
| **C2 (Class 2)** | Battleships / Orcas (Large Holes) | Dual Statics (e.g. C5 / Highsec)| ❌ No |
| **C3 (Class 3)** | Battleships / Marauders (Large Holes) | Lowsec / Nullsec | ❌ No |
| **C4 (Class 4)** | Battleships / Marauders (Large Holes) | Dual Wormhole Statics (e.g. C3/C5)| ❌ No |
| **C5 (Class 5)** | Capital Ships (Dreadnoughts, Carriers) | C5 Static (High-End Blue Loot)| ✅ Yes (Drifter Bosses) |
| **C6 (Class 6)** | Supercapitals / Titans (Theoretical) | C6 Static (Apex Farm Worlds) | ✅ Yes (10B+ ISK/hr) |

---

## ⚖️ Wormhole Mass Limits & Collapse Stages
1. **Initial State (Stage 1)**: Greater than **50% maximum mass** remaining.
2. **First Shrink (Stage 2)**: *"This wormhole has had its stability reduced by ships passing through it, but not to a critical level."* (**50% to 10% mass remaining**).
3. **Critical State (Stage 3)**: *"This wormhole is on the verge of collapse."* (**Less than 10% mass remaining**).
4. **Polarization Timer**: **5 minutes** cooldown preventing a ship from re-jumping the exact same wormhole.
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created.append(f1)

    # 2. Space Weather
    f2 = os.path.join(WH_DIR, "wormhole_space_weather.md")
    weather_cards = []
    for wname, wdata in WEATHER_EFFECTS.items():
        weather_cards.append(f"""### 🌌 **{wname}**
- **Tactical Buffs**: `{wdata['buffs']}`
- **System Debuffs**: `{wdata['debuffs']}`
- **Recommended Doctrine**: **{wdata['doctrine']}**
""")

    w_cards_str = "\n".join(weather_cards)

    m2 = f"""# Wormhole Space Weather Anomalies & Environmental Effects

Environmental tactical modifiers dictating fleet compositions and weapon choices across Anoikis.

---

## 🛰️ Space Weather Phenomona Matrix
{w_cards_str}
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created.append(f2)

    return created
