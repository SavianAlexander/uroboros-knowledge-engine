"""
Autonomous EVE Online Sovereign Evacuation & Asset Safety Fail-Safe Navigator.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact 0.5% in-system vs 15.0% Lowsec asset safety recovery math.
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

VAULT_NAV_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Navigation_Logistics")


def calculate_asset_safety_costs(
    total_asset_value_isk: float = 25000000000.0,  # 25 Billion ISK fleet assets
    in_system_recovery: bool = True,
    destination_lowsec_system: str = "Hophib (Aridia)"
) -> Dict[str, Any]:
    """
    Calculate asset safety recovery fees and emergency evacuation protocols.
    """
    tax_percent = 0.5 if in_system_recovery else 15.0
    recovery_tax_isk = total_asset_value_isk * (tax_percent / 100.0)

    # Evacuation Cyno Route from Delve to Lowsec Aridia
    evac_cyno_waypoints = [
        {"waypoint": 1, "system": "G-EURJ (Delve)", "action": "Stage in Astrahus Tether / Load Jump Freighter"},
        {"waypoint": 2, "system": "1DQ1-A (Delve)", "action": "Jump to 1DQ Keepstar staging"},
        {"waypoint": 3, "system": "KDF-GY (Period Basis)", "action": "Intermediate Jump Waypoint"},
        {"waypoint": 4, "system": "Hophib (Aridia - Lowsec)", "action": "Final Evac Destination: Dock in NPC Station"}
    ]

    return {
        "total_asset_value_isk": round(total_asset_value_isk, 2),
        "total_asset_value_billions": round(total_asset_value_isk / 1000000000.0, 2),
        "in_system_recovery": in_system_recovery,
        "asset_safety_tax_percent": tax_percent,
        "asset_safety_fee_isk": round(recovery_tax_isk, 2),
        "asset_safety_fee_billions": round(recovery_tax_isk / 1000000000.0, 2),
        "target_lowsec_npc_station": destination_lowsec_system,
        "evacuation_cyno_route": evac_cyno_waypoints,
        "evac_status": "LOW_COST_IN_SYSTEM" if in_system_recovery else "NPC_STATION_LOWSEC_ESCAPE"
    }


def generate_asset_safety_markdown() -> List[str]:
    """Generate Asset Safety Evacuation Protocols reference document."""
    os.makedirs(VAULT_NAV_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_NAV_DIR, "asset_safety_evacuation_protocols.md")

    safety_calc = calculate_asset_safety_costs(total_asset_value_isk=35000000000.0, in_system_recovery=False)

    doc_md = f"""---
title: Autonomous EVE Online Sovereign Evacuation & Asset Safety Fail-Safe Protocols
category: Logistics & Disaster Recovery
tags: [EVE, AssetSafety, Evacuation, JumpFreighter, Lowsec, Hophib, Delve, DisasterRecovery]
last_updated: 2026-08-14
---

# 🏰 Autonomous Sovereign Evacuation & Asset Safety Fail-Safe Protocols

This document establishes the contingency recovery mechanics, asset safety tax liabilities, and Jump Freighter emergency evacuation pathways.

---

## 💰 1. Asset Safety Recovery Matrix
- **Total Fleet Assets Assessed**: **{safety_calc['total_asset_value_billions']} Billion ISK**
- **Recovery Mode**: **Lowsec NPC Station Transfer** (to `{safety_calc['target_lowsec_npc_station']}`)
- **Asset Safety Tax (15.0%)**: **{safety_calc['asset_safety_fee_billions']} Billion ISK ({safety_calc['asset_safety_fee_isk']:,.2f} ISK)**
- *Note: In-system recovery to an allied Upwell structure incurs only a **0.5% fee** ({safety_calc['total_asset_value_billions'] * 0.005:.3f}B ISK).*

---

## 🌌 2. Emergency Jump Freighter Evacuation Highway (Delve $\\longrightarrow$ Aridia)

"""
    for wp in safety_calc["evacuation_cyno_route"]:
        doc_md += f"### Waypoint {wp['waypoint']}: `{wp['system']}`\n"
        doc_md += f"- **Action**: {wp['action']}\n\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_asset_safety_markdown()
    print(f"Generated asset safety document: {files}")
