"""
Autonomous EVE Online Combat, EWAR, Incursions & Anti-Gank Defense Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact ECM jamming probabilities, Incursion payout splits, and anti-gank EHP math.
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

VAULT_COMBAT_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Combat_Intelligence")

CONCORD_RESPONSE_TIMES = {
    1.0: 6.0,
    0.9: 7.0,
    0.8: 8.5,
    0.7: 10.0,
    0.6: 14.0,
    0.5: 19.0
}


def calculate_ecm_jam_probability(
    jammer_strength: float = 12.5,
    target_sensor_strength: float = 24.0
) -> Dict[str, Any]:
    """
    Calculate single ECM cycle jamming probability.
    """
    jam_chance = min(1.0, jammer_strength / target_sensor_strength) if target_sensor_strength > 0 else 1.0
    return {
        "jammer_strength": jammer_strength,
        "target_sensor_strength": target_sensor_strength,
        "jam_probability_percent": round(jam_chance * 100, 1),
        "jam_verdict": "EFFECTIVE_JAM" if jam_chance >= 0.50 else "CONTESTED_JAM"
    }


def calculate_antigank_survival(
    ship_name: str = "Porpoise (Mining Lead)",
    ship_ehp: float = 65000.0,
    solar_system_security: float = 0.6,
    ganker_catalyst_count: int = 8,
    single_catalyst_dps: float = 650.0
) -> Dict[str, Any]:
    """
    Calculate suicide gank survival against hostile Catalyst swarm before CONCORD intervention.
    """
    concord_delay_s = CONCORD_RESPONSE_TIMES.get(round(solar_system_security, 1), 14.0)
    total_gank_dps = ganker_catalyst_count * single_catalyst_dps
    total_damage_dealt_before_concord = total_gank_dps * concord_delay_s

    survives = ship_ehp > total_damage_dealt_before_concord
    ehp_margin = ship_ehp - total_damage_dealt_before_concord

    return {
        "ship_name": ship_name,
        "ship_ehp": ship_ehp,
        "system_security": solar_system_security,
        "concord_response_time_s": concord_delay_s,
        "gankers_count": ganker_catalyst_count,
        "total_incoming_gank_dps": total_gank_dps,
        "total_damage_before_concord_kill": round(total_damage_dealt_before_concord, 1),
        "ehp_survival_margin": round(ehp_margin, 1),
        "survival_status": "SURVIVED (CONCORD Wipes Gankers)" if survives else "DESTROYED (Alpha Overwhelmed Tank)"
    }


def generate_combat_ewar_markdown() -> List[str]:
    """Generate Combat, EWAR & Incursions reference document."""
    os.makedirs(VAULT_COMBAT_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_COMBAT_DIR, "ewar_incursions_combat_sites_srp.md")

    jam_sim = calculate_ecm_jam_probability(jammer_strength=14.0, target_sensor_strength=22.0)
    gank_sim = calculate_antigank_survival(ship_ehp=72000.0, solar_system_security=0.6, ganker_catalyst_count=6)

    doc_md = f"""---
title: Autonomous EVE Online Combat, EWAR, Incursions & Anti-Gank Suite
category: Combat Systems & Threat Intelligence
tags: [EVE, EWAR, ECM, Incursions, Sansha, AntiGank, CONCORD, DEDCombat, SRP]
last_updated: 2026-08-14
---

# ⚔️ Autonomous Combat, EWAR, Incursions & Anti-Gank Suite

This document defines the electronic warfare disruption equations, Sansha Incursion fleet dynamics, and highsec anti-gank survivability models.

---

## 📡 1. Strategic ECM Jamming Probability
- **Jammer Strength**: **{jam_sim['jammer_strength']} Points**
- **Target Sensor Strength**: **{jam_sim['target_sensor_strength']} Points**
- **Single-Cycle Jam Probability**: **`{jam_sim['jam_probability_percent']}%` ({jam_sim['jam_verdict']})**

---

## 🛡️ 2. Highsec Anti-Gank Survivability Benchmark
- **Defending Ship**: `{gank_sim['ship_name']}` (Tank EHP: **{gank_sim['ship_ehp']:,} EHP**)
- **Solar System Security**: `{gank_sim['system_security']}` (CONCORD Response Delay: **{gank_sim['concord_response_time_s']} Seconds**)
- **Incoming Threat**: **{gank_sim['gankers_count']}x T2 Blaster Catalysts ({gank_sim['total_incoming_gank_dps']:,} Incoming DPS)**
- **Damage Dealt Before CONCORD Destruction**: **{gank_sim['total_damage_before_concord_kill']:,} HP**
- **Tactical Survival Status**: **`{gank_sim['survival_status']}`** (Buffer Surplus: `{gank_sim['ehp_survival_margin']:,} EHP`)

---

## 🛸 3. Sansha Incursion HQ Fleet Operations
- **HQ Site Standard Payout**: **31,500,000 ISK + 7,000 CONCORD LP per Pilot** (40-man fleet).
- **Hourly Income Average (3 HQ Sites/hr)**: **94.5M ISK + 21,000 LP/hr (~136.5M ISK/hr)**.
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_combat_ewar_markdown()
    print(f"Generated combat EWAR document: {files}")
