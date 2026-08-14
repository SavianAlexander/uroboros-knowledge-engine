"""
Autonomous EVE Online Equinox Sovereignty Hub & Upwell Skyhook Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact Equinox power/workforce/reagent budget algorithms.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_EQUINOX_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Equinox_Sovereignty")

SOV_HUB_UPGRADES = {
    "Major Mining Prospecting Array": {"power_cost": 450, "workforce_cost": 300, "reagent_cost": {"Superionic Ice": 250}, "ore_anomalies": "+3 Colossal/Enormous Moon Belts"},
    "Supercarrier Construction Plant": {"power_cost": 800, "workforce_cost": 600, "reagent_cost": {"Magmatic Gas": 500}, "capital_bonus": "Enables Titan/Supercarrier Hull Assembly"},
    "Strategic Cynosural Jammer": {"power_cost": 1200, "workforce_cost": 400, "reagent_cost": {"Liquid Ozone": 1000}, "defense_bonus": "Blocks all Hostile Cynosural Fields in System"},
    "Ansiblex Jump Gate Network": {"power_cost": 650, "workforce_cost": 250, "reagent_cost": {"Liquid Ozone": 500}, "logistics_bonus": "Enables Fast Intra-Alliance Subcapital Travel"}
}


def calculate_system_equinox_budget(
    star_type: str = "Blue Star (O0)",
    planet_count: int = 8,
    lava_planets: int = 2,
    ice_planets: int = 2,
    gas_planets: int = 2,
    installed_upgrades: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate solar system Equinox resource generation and upgrade budget.
    """
    if installed_upgrades is None:
        installed_upgrades = ["Major Mining Prospecting Array", "Ansiblex Jump Gate Network", "Strategic Cynosural Jammer"]

    # Resource Generation Calculations
    base_power = 2500 if "Blue" in star_type else 1800 if "Yellow" in star_type else 1200
    base_workforce = planet_count * 150

    # Planetary Skyhook Reagent Harvest Rates (units / day)
    magmatic_gas_daily = lava_planets * 1200
    superionic_ice_daily = ice_planets * 1400

    # Total Upgrades Demand
    total_power_used = sum(SOV_HUB_UPGRADES.get(u, {}).get("power_cost", 0) for u in installed_upgrades)
    total_workforce_used = sum(SOV_HUB_UPGRADES.get(u, {}).get("workforce_cost", 0) for u in installed_upgrades)

    power_surplus = base_power - total_power_used
    workforce_surplus = base_workforce - total_workforce_used

    return {
        "system_star_type": star_type,
        "total_system_power": base_power,
        "used_system_power": total_power_used,
        "surplus_power": power_surplus,
        "total_system_workforce": base_workforce,
        "used_system_workforce": total_workforce_used,
        "surplus_workforce": workforce_surplus,
        "daily_magmatic_gas_harvest": magmatic_gas_daily,
        "daily_superionic_ice_harvest": superionic_ice_daily,
        "installed_upgrades_count": len(installed_upgrades),
        "system_status": "SOVEREIGNTY_OPTIMAL" if power_surplus >= 0 and workforce_surplus >= 0 else "RESOURCE_DEFICIT"
    }


def generate_equinox_markdown() -> List[str]:
    """Generate Equinox Sovereignty Hub & Upwell Skyhook reference document."""
    os.makedirs(VAULT_EQUINOX_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_EQUINOX_DIR, "equinox_hub_skyhooks_reagents.md")

    # Sample G-EURJ / 1DQ1-A sovereign budget
    sov_calc = calculate_system_equinox_budget(
        star_type="Blue Star (O0)", planet_count=11, lava_planets=3, ice_planets=2, gas_planets=4
    )

    doc_md = f"""---
title: Autonomous EVE Online Equinox Sovereignty Hub & Skyhook Reagents Engine
category: Sovereignty & Infrastructure
tags: [EVE, Equinox, Sovereignty, UpwellSkyhooks, Power, Workforce, Reagents, Ansiblex, CynoJammer]
last_updated: 2026-08-14
---

# 👑 Autonomous Equinox Sovereignty Hub & Skyhook Reagents Engine

This document outlines the resource calculus, Skyhook planetary reagent yields, and Sovereignty Hub upgrade topologies introduced in the Equinox expansion.

---

## ⚡ 1. Equinox Solar System Resource Generation
- **Star System**: Blue Star (O0) Core Solar System
- **Total System Power Generated**: **{sov_calc['total_system_power']} MW**
- **Total System Workforce**: **{sov_calc['total_system_workforce']} Personnel**
- **Surplus Power Reserve**: **{sov_calc['surplus_power']} MW**
- **Surplus Workforce Reserve**: **{sov_calc['surplus_workforce']} Personnel**
- **System Sovereign Status**: **`{sov_calc['system_status']}`**

---

## 🛰️ 2. Upwell Orbital Skyhook Harvest & Siphon Defenses
- **Magmatic Gas Daily Production**: **{sov_calc['daily_magmatic_gas_harvest']:,} Units/Day** (from 3 Lava Worlds)
- **Superionic Ice Daily Production**: **{sov_calc['daily_superionic_ice_harvest']:,} Units/Day** (from 2 Ice Worlds)
- **Siphon Defense Timer**: 10-Minute Vulnerability Warning window with automatic alliance defense fleet pings.

---

## 🏗️ 3. Sovereignty Hub Upgrade Catalog & Upkeep

| Sovereignty Hub Upgrade | Power Demand | Workforce Demand | Primary Strategic Benefit |
| :--- | :---: | :---: | :--- |
| **Strategic Cynosural Jammer** | **1,200 MW** | 400 | Complete system-wide hostile cyno suppression |
| **Supercarrier Construction** | **800 MW** | 600 | Sovereign Titan/Supercarrier manufacturing |
| **Ansiblex Jump Gate Network** | **650 MW** | 250 | Instant subcapital alliance jump transit |
| **Major Mining Prospecting** | **450 MW** | 300 | Massive Colossal/Enormous moon belt spawns |
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_equinox_markdown()
    print(f"Generated equinox document: {files}")
