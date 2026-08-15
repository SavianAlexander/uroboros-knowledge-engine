"""
EVE Online Tech 3 Strategic Cruiser (T3C) Subsystems & Command Ships Matrix.

Comprehensive structural schematics for modular strategic hulls:
- Tengu (Caldari), Legion (Amarr), Proteus (Gallente), Loki (Minmatar)
- 4 Subsystem Families (Core, Defensive, Offensive, Propulsion)
- Command Ships Warfare Links & Fleet Burst Stacking Matrix (Eos, Damnation, Astarte, Sleipnir)

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
DOCTRINES_DIR = os.path.join(VAULT_EVE_DIR, "Ship_Doctrines")

T3C_HULLS = {
    "Tengu (Caldari T3C)": {
        "bonuses": "Heavy Missile / Kinetic Missile Damage & Shield Boost Multipliers",
        "covert_fit": "Covert Reconfiguration + Interdiction Nullifier (Instawarp Hunter)",
        "missile_dps": "750 - 900 DPS",
        "tank": "85,000 EHP Shield / Active Pith X-Type Booster"
    },
    "Legion (Amarr T3C)": {
        "bonuses": "Heavy Energy Laser / Heavy Assault Missile (HAM) & Armor Resistances",
        "covert_fit": "Covert Reconfiguration + Dissolution Sequencer (100% Armor Resists)",
        "laser_dps": "650 - 850 DPS",
        "tank": "120,000 EHP Armor / Dual Medium Centii A-Type Reps"
    },
    "Proteus (Gallente T3C)": {
        "bonuses": "Heavy Blaster Hybrid Turrets / Drone Interfacing / Point Blank Scram Range",
        "covert_fit": "Covert Reconfiguration + Drone Synthesis Projector",
        "hybrid_dps": "1,150+ DPS (Void M)",
        "tank": "110,000 EHP Armor Buffer"
    },
    "Loki (Minmatar T3C)": {
        "bonuses": "Medium Projectile Turrets / Heavy Missiles / Stasis Web Range (42km Webs)",
        "covert_fit": "Covert Reconfiguration + Interdiction Nullifier",
        "arty_dps": "720 DPS (Auto-cannon / Artillery)",
        "tank": "95,000 EHP Active Shield / Fleet Web Support"
    }
}


def generate_t3c_markdown() -> list:
    os.makedirs(DOCTRINES_DIR, exist_ok=True)
    created = []

    # 1. T3 Strategic Cruiser Subsystem Matrix
    f1 = os.path.join(DOCTRINES_DIR, "t3c_strategic_cruisers.md")
    t3c_cards = []
    for hull, data in T3C_HULLS.items():
        t3c_cards.append(f"""### 🚀 **{hull}**
- **Doctrine Role**: {data['bonuses']}
- **Covert Hunter Configuration**: `{data['covert_fit']}`
- **DPS Output**: `{data['dps'] if 'dps' in data else data.get('missile_dps') or data.get('laser_dps') or data.get('hybrid_dps') or data.get('arty_dps')}`
- **Defensive Profile**: `{data['tank']}`
""")

    cards_str = "\n".join(t3c_cards)

    m1 = f"""# Tech 3 Strategic Cruiser (T3C) Subsystem & Covert Matrix

Modular strategic cruiser configurations engineered for covert black ops drops, bubble-immune scouting, and wormhole dominance.

---

## 🌐 The 4 Empire Strategic Cruisers
{cards_str}

---

## ⚙️ The 4 Subsystem Families
1. **Core Subsystem**: Determines capacitor capacity, CPU output, and sensor booster effectiveness.
2. **Defensive Subsystem**: Dictates Armor / Shield hitpoints and unlocks **Covert Cloak** capabilities.
3. **Offensive Subsystem**: Dictates high-slot weapon counts (Missile hardpoints, Turret hardpoints, Drone bandwidth).
4. **Propulsion Subsystem**: Determines agility, warp speed, and unlocks **Interdiction Nullification**.
"""
    with open(f1, "w", encoding="utf-8") as f:
        f.write(m1)
    created.append(f1)

    # 2. Command Ships
    f2 = os.path.join(DOCTRINES_DIR, "command_ships_warfare_links.md")
    m2 = """# Command Ships & Fleet Warfare Link Stacking Matrix

Fleet Command Battlecruisers engineered to broadcast multi-squadron defensive and offensive combat buffs.

---

## 🛡️ Sovereign Command Ship Archetypes
| Command Ship | Race | Primary Burst Link | Combat Role |
| :--- | :--- | :--- | :--- |
| **Eos** | Gallente | **Armor & Skirmish Links** | Heavy Drone Brawler & Armor Logistics Anchor |
| **Damnation** | Amarr | **Armor & Information Links** | 350,000+ EHP Fleet Tank Flagship (Brick Tank) |
| **Astarte** | Gallente | **Armor & Skirmish Links** | Point-blank High DPS Blaster Brawler |
| **Sleipnir** | Minmatar | **Shield & Skirmish Links** | Shield Fleet Anchor & 1,100+ DPS Projectile Platform |
| **Vulture** | Caldari | **Shield & Information Links** | 150km Railgun Sniper & Fleet Shield Link Hub |
| **Nighthawk** | Caldari | **Shield & Information Links** | Heavy Missile Assault & Shield Link Buffer |

---

## 📐 Command Burst Stacking Rules
- **Stacking Limit**: Maximum **3 active Command Bursts** per Command Ship with *Wing Command V* and *Fleet Command IV*.
- **Burst Range**: Standard **45km** base, expandable to **75km+** with *Command Burst Specialist V*.
"""
    with open(f2, "w", encoding="utf-8") as f:
        f.write(m2)
    created.append(f2)

    return created
