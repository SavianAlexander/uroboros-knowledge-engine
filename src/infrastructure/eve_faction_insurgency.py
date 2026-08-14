"""
Autonomous EVE Online Faction Warfare Insurgencies & Corruption Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact Havoc Corruption/Suppression mechanics.
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

VAULT_FW_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Faction_Warfare")

CORRUPTION_STAGES = {
    1: {"name": "Pirate Presence", "effect": "Pirate Sentries spawn on warp gates", "law_level": "Standard"},
    2: {"name": "Law Breakdown", "effect": "Gate Sentry guns offline; Security status penalties reduced", "law_level": "Compromised"},
    3: {"name": "Anarchy Rising", "effect": "Warp Interdiction Bubbles enabled in Lowsec systems", "law_level": "Anarchic"},
    4: {"name": "Concord Paralysis", "effect": "Concord / Empire response times delayed by 300%", "law_level": "Severe Lawlessness"},
    5: {"name": "Total Pirate Haven", "effect": "Full Nullsec Rules: Bubbles, Bombs & Capital Escalations Unlocked", "law_level": "Lawless Nullsec State"}
}

SUPPRESSION_STAGES = {
    1: {"name": "Empire Patrols", "effect": "Empire Navy scout frigates deployed", "safety_level": "Elevated Patrols"},
    2: {"name": "Fortified Gates", "effect": "Gate sentry guns gain +50% tracking and +50% range", "safety_level": "Fortified"},
    3: {"name": "Active Police Grid", "effect": "Empire police point defense wipes light pirate drones", "safety_level": "High Security Patrol"},
    4: {"name": "FOB Bombardment", "effect": "Empire capital dreadnoughts bombard pirate FOB", "safety_level": "Heavy Suppression"},
    5: {"name": "Total Law Enforcement", "effect": "Insurgency completely suppressed; Pirate FOB collapses", "safety_level": "Absolute Empire Dominance"}
}


def calculate_insurgency_state(
    current_corruption_points: int = 4200,
    current_suppression_points: int = 1800,
    points_per_stage: int = 1000
) -> Dict[str, Any]:
    """
    Calculate active Insurgency stage, rule modifiers, and winning faction.
    """
    corr_stage = min(5, max(0, current_corruption_points // points_per_stage))
    supp_stage = min(5, max(0, current_suppression_points // points_per_stage))

    corr_info = CORRUPTION_STAGES.get(corr_stage, {"name": "Nominal", "effect": "Normal Empire Space", "law_level": "Highsec/Lowsec"})
    supp_info = SUPPRESSION_STAGES.get(supp_stage, {"name": "Nominal", "effect": "Normal Empire Space", "safety_level": "Standard"})

    bubbles_enabled = corr_stage >= 3
    gate_guns_offline = corr_stage >= 2

    return {
        "corruption_points": current_corruption_points,
        "corruption_stage": corr_stage,
        "corruption_name": corr_info["name"],
        "corruption_effect": corr_info["effect"],
        "suppression_points": current_suppression_points,
        "suppression_stage": supp_stage,
        "suppression_name": supp_info["name"],
        "suppression_effect": supp_info["effect"],
        "tactical_rules": {
            "warp_bubbles_in_lowsec": bubbles_enabled,
            "gate_sentries_offline": gate_guns_offline,
            "capital_escalations_allowed": corr_stage == 5
        },
        "insurgency_winner": "Pirates (Guristas / Angels)" if corr_stage > supp_stage else "Empire Militias"
    }


def generate_insurgency_markdown() -> List[str]:
    """Generate Faction Warfare Insurgencies reference document."""
    os.makedirs(VAULT_FW_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_FW_DIR, "pirate_insurgency_corruption_suppression.md")

    insurg_state = calculate_insurgency_state(current_corruption_points=3500, current_suppression_points=1200)

    doc_md = f"""---
title: Autonomous EVE Online Faction Warfare Insurgencies & Corruption Engine
category: Faction Warfare
tags: [EVE, FactionWarfare, Insurgency, Corruption, Suppression, Guristas, AngelCartel, Zarzakh, Lowsec]
last_updated: 2026-08-14
---

# 🏴‍☠️ Autonomous Faction Warfare Insurgencies & Corruption Engine

This document details the mechanics, corruption/suppression progression curves, and tactical environmental changes of Pirate Insurgencies introduced in EVE Online: Havoc.

---

## 💀 1. Corruption Progression & Law Breakdown (Stage 1 to 5)

| Corruption Stage | Stage Name | Tactical Rule & Environmental Impact |
| :---: | :--- | :--- |
| **Stage 1** | **Pirate Presence** | Pirate Sentries spawn on warp gates |
| **Stage 2** | **Law Breakdown** | **Gate Sentry guns go offline** (Safe to engage on gates without sentry agro) |
| **Stage 3** | **Anarchy Rising** | **Warp Interdiction Bubbles become active in Lowsec systems** |
| **Stage 4** | **Concord Paralysis** | Concord / Empire reaction times delayed by +300% |
| **Stage 5** | **Total Pirate Haven** | **Full Nullsec Rules**: Stealth Bombers, Bubbles & Capital Escalations |

---

## 🛡️ 2. Suppression Progression & Empire Law Enforcement (Stage 1 to 5)

| Suppression Stage | Stage Name | Empire Defense Impact |
| :---: | :--- | :--- |
| **Stage 1** | **Empire Patrols** | Navy scout frigates deployed |
| **Stage 2** | **Fortified Gates** | Gate sentry guns gain +50% tracking and +50% range |
| **Stage 3** | **Active Police Grid** | Police point defense wipes light pirate drones |
| **Stage 4** | **FOB Bombardment** | Empire capital dreadnoughts bombard pirate FOB |
| **Stage 5** | **Total Suppression** | **Insurgency completely suppressed; Pirate FOB collapses** |

---

## 🎯 3. Live Insurgency Warzone State
- **Current Corruption Level**: **Stage {insurg_state['corruption_stage']} ({insurg_state['corruption_name']})**
- **Current Suppression Level**: **Stage {insurg_state['suppression_stage']} ({insurg_state['suppression_name']})**
- **Warp Bubbles in Lowsec**: **`{insurg_state['tactical_rules']['warp_bubbles_in_lowsec']}`**
- **Gate Sentry Guns Disabled**: **`{insurg_state['tactical_rules']['gate_sentries_offline']}`**
- **Current Advantage**: **`{insurg_state['insurgency_winner']}`**
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_insurgency_markdown()
    print(f"Generated insurgency document: {files}")
