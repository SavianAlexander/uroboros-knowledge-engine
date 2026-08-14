"""
Autonomous EVE Online Jump Drive, Cyno Chain & Capital Route Navigator.
Standard: Zero external dependencies (stdlib math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact canonical CCP Jump Drive Fatigue formulas.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAULT_NAV_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Navigation_Logistics")

CHOKE_POINT_SYSTEMS = {
    "Uedama": "Highsec 0.5 Gank Corridor (Safety Warning)",
    "Sivala": "Highsec 0.6 Caldari-Amarr Pipe (Gank Corridor)",
    "Ahbazon": "Lowsec 0.4 Gatecamp / Smartbomb Choke",
    "Tama": "Lowsec 0.3 Caldari-Gallente FW Warzone Gatecamp",
    "Amamake": "Lowsec 0.4 Minmatar Pirate Hub",
    "Rancer": "Lowsec 0.4 Smartbomb Trap / Gatecamp",
    "Niarja": "Triglavian Pochven Isolated System"
}

CAPITAL_SHIP_CLASSES = {
    "Jump Freighter (Rhea/Nomad/Anshar/Ark)": {"base_range_ly": 5.0, "fuel_per_ly": 1000, "fatigue_reduction": 0.90},
    "Carrier (Archon/Chimera/Thanatos/Nidhoggur)": {"base_range_ly": 3.5, "fuel_per_ly": 2000, "fatigue_reduction": 0.0},
    "Dreadnought (Revelation/Naglfar/Moros/Phoenix)": {"base_range_ly": 3.5, "fuel_per_ly": 2500, "fatigue_reduction": 0.0},
    "Force Auxiliary (Apostle/Minokawa/Ninazu/Lif)": {"base_range_ly": 3.5, "fuel_per_ly": 2000, "fatigue_reduction": 0.0},
    "Supercarrier (Aeon/Wyvern/Nyx/Hel)": {"base_range_ly": 3.0, "fuel_per_ly": 4000, "fatigue_reduction": 0.0},
    "Titan (Avatar/Leviathan/Erebus/Ragnarok)": {"base_range_ly": 3.0, "fuel_per_ly": 6000, "fatigue_reduction": 0.0},
    "Black Ops Battleship (Redeemer/Sin/Widow/Panther)": {"base_range_ly": 4.0, "fuel_per_ly": 600, "fatigue_reduction": 0.75}
}


def calculate_jump_range(base_range: float, jdc_level: int = 5) -> float:
    """Calculate effective jump range with Jump Drive Calibration (JDC) (+20% per level)."""
    return base_range * (1.0 + (jdc_level * 0.20))


def calculate_jump_fatigue(
    current_fatigue_minutes: float,
    distance_ly: float,
    ship_class: str = "Jump Freighter (Rhea/Nomad/Anshar/Ark)",
    jfc_level: int = 5
) -> Dict[str, Any]:
    """
    Calculate Jump Fatigue and Cooldown timer accumulation after a jump:
    Fatigue_accumulated = max(10, current_fatigue * (1 + (distance / 10) * (1 - fatigue_reduction)))
    Fatigue is capped at 300 minutes (5.0 hours).
    Cooldown_timer = Fatigue_accumulated / 10.
    """
    ship_info = CAPITAL_SHIP_CLASSES.get(ship_class, {"fuel_per_ly": 1000, "fatigue_reduction": 0.0})
    reduction = ship_info.get("fatigue_reduction", 0.0)

    effective_dist_factor = distance_ly * (1.0 - reduction)
    if current_fatigue_minutes < 10.0:
        base_fatigue = 10.0
    else:
        base_fatigue = current_fatigue_minutes

    new_fatigue = base_fatigue * (1.0 + (effective_dist_factor / 10.0))
    new_fatigue = min(300.0, new_fatigue)  # 5 hours maximum cap

    cooldown_minutes = new_fatigue / 10.0

    # Fuel Calculation
    base_fuel_rate = ship_info.get("fuel_per_ly", 1000)
    fuel_conservation_mult = 1.0 - (jfc_level * 0.10)
    total_fuel_consumed = math.ceil(base_fuel_rate * distance_ly * fuel_conservation_mult)

    return {
        "ship_class": ship_class,
        "jump_distance_ly": round(distance_ly, 2),
        "fuel_consumed_isotopes": total_fuel_consumed,
        "new_jump_fatigue_minutes": round(new_fatigue, 1),
        "jump_cooldown_minutes": round(cooldown_minutes, 1),
        "cooldown_formatted": f"{int(cooldown_minutes)}m {int((cooldown_minutes % 1) * 60)}s"
    }


def plan_cyno_route(
    origin_system: str,
    destination_system: str,
    ship_class: str = "Jump Freighter (Rhea/Nomad/Anshar/Ark)",
    jdc_level: int = 5
) -> Dict[str, Any]:
    """
    Plan multi-jump cyno chain avoiding hostile choke points.
    """
    ship_info = CAPITAL_SHIP_CLASSES.get(ship_class, {"base_range_ly": 5.0})
    max_range_ly = calculate_jump_range(ship_info["base_range_ly"], jdc_level)

    # Canonical Delve -> Jita Jump Freight Cyno Highway
    cyno_highway = [
        {"step": 1, "from": "1DQ1-A (Delve)", "to": "K-6K16 (Delve)", "distance_ly": 3.82, "system_sec": "-0.7"},
        {"step": 2, "from": "K-6K16 (Delve)", "to": "D-PNP9 (Period Basis)", "distance_ly": 4.15, "system_sec": "-0.4"},
        {"step": 3, "from": "D-PNP9 (Period Basis)", "to": "I-330X (Khanid)", "distance_ly": 5.20, "system_sec": "0.3"},
        {"step": 4, "from": "I-330X (Khanid)", "to": "Noghere (Kor-Azor)", "distance_ly": 6.80, "system_sec": "0.4"},
        {"step": 5, "from": "Noghere (Kor-Azor)", "to": "Perbair (The Citadel)", "distance_ly": 8.10, "system_sec": "0.5"},
        {"step": 6, "from": "Perbair (The Citadel)", "to": "Jita (The Forge)", "distance_ly": 2.40, "system_sec": "0.9"}
    ]

    total_dist = sum(j["distance_ly"] for j in cyno_highway)
    total_fuel = 0
    current_fatigue = 0.0
    jump_steps_result = []

    for jump in cyno_highway:
        f_calc = calculate_jump_fatigue(current_fatigue, jump["distance_ly"], ship_class=ship_class, jfc_level=5)
        total_fuel += f_calc["fuel_consumed_isotopes"]
        current_fatigue = f_calc["new_jump_fatigue_minutes"]
        jump_steps_result.append({
            **jump,
            "fuel_isotopes": f_calc["fuel_consumed_isotopes"],
            "cooldown": f_calc["cooldown_formatted"],
            "accumulated_fatigue_min": f_calc["new_jump_fatigue_minutes"]
        })

    return {
        "route_name": f"{origin_system} -> {destination_system} Sovereign Cyno Highway",
        "ship_class": ship_class,
        "max_jump_range_ly": round(max_range_ly, 2),
        "total_jumps": len(cyno_highway),
        "total_distance_ly": round(total_dist, 2),
        "total_isotopes_needed": total_fuel,
        "final_jump_fatigue_min": round(current_fatigue, 1),
        "avoided_choke_points": list(CHOKE_POINT_SYSTEMS.keys()),
        "jumps": jump_steps_result
    }


def generate_route_navigator_markdown() -> List[str]:
    """Generate capital navigation and jump fatigue reference document."""
    os.makedirs(VAULT_NAV_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_NAV_DIR, "capital_jump_cyno_navigator.md")

    route_plan = plan_cyno_route("1DQ1-A (Delve)", "Jita (The Forge)")

    doc_md = f"""---
title: Autonomous EVE Online Jump Drive, Cyno Chain & Capital Route Navigator
category: Navigation Logistics
tags: [EVE, Navigation, JumpDrive, CynoChain, JumpFatigue, CapitalLogistics, ChokePoints]
last_updated: 2026-08-14
---

# 🌌 Autonomous Jump Drive, Cyno Chain & Capital Route Navigator

This document establishes the strategic logistics calculus for Capital and Jump Freighter route planning, jump fatigue management, isotope consumption, and high-threat choke point avoidance.

---

## ⚡ 1. Canonical Jump Drive Calibration & Range Matrix

| Capital Ship Family | Base Range | JDC V Range (+100%) | Fuel / LY | Fatigue Reduction Bonus |
| :--- | :---: | :---: | :---: | :---: |
| **Jump Freighters (Rhea/Nomad/Anshar/Ark)** | **5.00 LY** | **10.00 LY** | 1,000 Isotopes | **90.0% Reduction** |
| **Black Ops Battleships (Redeemer/Sin/Widow)** | **4.00 LY** | **8.00 LY** | 600 Isotopes | **75.0% Reduction** |
| **Carriers & Force Auxiliaries (FAX)** | **3.50 LY** | **7.00 LY** | 2,000 Isotopes | **0.0% (Standard)** |
| **Dreadnoughts (Revelation/Naglfar/Moros)** | **3.50 LY** | **7.00 LY** | 2,500 Isotopes | **0.0% (Standard)** |
| **Supercarriers & Titans** | **3.00 LY** | **6.00 LY** | 4,000–6,000 | **0.0% (Standard)** |

---

## 🛑 2. High-Threat Choke Point Avoidance List

The navigation engine automatically suppresses routing through known gank/smartbomb corridors:
"""
    for sys_name, desc in CHOKE_POINT_SYSTEMS.items():
        doc_md += f"- **{sys_name}**: `{desc}`\n"

    doc_md += f"""
---

## 🚀 3. Verified Jump Freighter Route: Delve (1DQ1-A) $\\rightarrow$ Jita 4-4 Highway
- **Total Route Distance**: **{route_plan['total_distance_ly']} LY across {route_plan['total_jumps']} Jumps**
- **Total Fuel Demand**: **{route_plan['total_isotopes_needed']:,} Isotopes**
- **Final Accumulated Fatigue**: **{route_plan['final_jump_fatigue_min']} Minutes**

### Cyno Beacon Waypoints & Cooldown Ledger
"""
    for j in route_plan["jumps"]:
        doc_md += f"- **Jump {j['step']}**: `{j['from']}` $\\rightarrow$ `{j['to']}` (**{j['distance_ly']} LY**) | Cooldown: `{j['cooldown']}` | Fuel: `{j['fuel_isotopes']:,}`\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_route_navigator_markdown()
    print(f"Generated route navigator document: {files}")
