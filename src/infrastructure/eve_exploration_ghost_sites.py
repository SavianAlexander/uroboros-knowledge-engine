"""
Autonomous EVE Online Exploration, Ghost Sites & Hacking Coherence Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time, random).
Ponytail Senior Dev Principle: Exact hacking minigame damage math and Ghost Site timers.
"""

import os
import sys
import math
import json
import time
import random
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_EXPLORE_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Exploration_Hacking")

DEFENSE_NODES = {
    "Firewall": {"hp": 60, "attack": 20, "priority": "High"},
    "Anti-Virus": {"hp": 40, "attack": 40, "priority": "Extreme (Eliminate First)"},
    "Restoration Node": {"hp": 60, "attack": 10, "special": "Repairs adjacent nodes +20 HP/turn", "priority": "Urgent"},
    "Virus Suppressor": {"hp": 50, "attack": 10, "special": "Reduces Player Virus Strength by -20", "priority": "Urgent"}
}


def simulate_hacking_attempt(
    character_skill_level: int = 5,
    analyzer_type: str = "Relic Analyzer II",
    rig_bonus: int = 10,
    site_difficulty: str = "Hard (Nullsec / C5 WH Relic)"
) -> Dict[str, Any]:
    """
    Simulate exploration hacking attempt calculating player virus coherence, strength, and node traversal.
    """
    base_virus_strength = 20 if "II" in analyzer_type else 10
    base_virus_coherence = 100 if "II" in analyzer_type else 60

    # Skill and rig bonuses
    total_strength = base_virus_strength + (character_skill_level * 2)
    total_coherence = base_virus_coherence + (character_skill_level * 10) + (rig_bonus * 2)

    current_coherence = total_coherence
    nodes_encountered = []
    
    # Encounter standard 3 defense nodes
    for node_name in ["Firewall", "Anti-Virus", "Restoration Node"]:
        node = DEFENSE_NODES[node_name]
        node_hp = node["hp"]
        node_dmg = node["attack"]

        # Number of hits required to break node
        hits_needed = math.ceil(node_hp / total_strength)
        damage_taken = (hits_needed - 1) * node_dmg
        current_coherence -= damage_taken

        nodes_encountered.append({
            "node": node_name,
            "node_hp": node_hp,
            "hits_required": hits_needed,
            "damage_taken": damage_taken,
            "coherence_after_combat": max(0, current_coherence)
        })

    hack_successful = current_coherence > 0

    return {
        "analyzer": analyzer_type,
        "site_difficulty": site_difficulty,
        "total_virus_strength": total_strength,
        "max_virus_coherence": total_coherence,
        "remaining_coherence": max(0, current_coherence),
        "hack_result": "SUCCESS (Core Extracted)" if hack_successful else "FAILED (Can Exploded)",
        "combat_log": nodes_encountered
    }


def calculate_ghost_site_risk(
    ship_ehp: float = 12500.0,
    site_tier: str = "Superior Covert Research Facility (Nullsec/C5)",
    time_spent_hacking_s: float = 45.0
) -> Dict[str, Any]:
    """
    Calculate Ghost Site explosion damage, detonation threshold, and survival odds.
    """
    detonation_window_s = 55.0  # Hostile pirate ambush threshold
    raw_explosion_dmg = 12000.0 if "Superior" in site_tier else 6000.0
    effective_taken = raw_explosion_dmg * 0.70  # Assuming 30% resist

    timer_expired = time_spent_hacking_s >= detonation_window_s
    ship_survives = ship_ehp > effective_taken

    return {
        "site_type": site_tier,
        "time_spent_s": time_spent_hacking_s,
        "detonation_limit_s": detonation_window_s,
        "timer_breached": timer_expired,
        "raw_explosion_damage": raw_explosion_dmg,
        "damage_taken_after_resists": round(effective_taken, 1),
        "ship_ehp": ship_ehp,
        "ship_survival_status": "SURVIVED (Warp Out Safe)" if (ship_survives or not timer_expired) else "SHIP_DESTROYED"
    }


def generate_exploration_markdown() -> List[str]:
    """Generate Exploration, Ghost Sites & Hacking reference document."""
    os.makedirs(VAULT_EXPLORE_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_EXPLORE_DIR, "exploration_ghost_sites_hacking.md")

    hack_sim = simulate_hacking_attempt(character_skill_level=5, analyzer_type="Relic Analyzer II", rig_bonus=10)
    ghost_calc = calculate_ghost_site_risk(ship_ehp=18500.0, site_tier="Superior Covert Research Facility (Nullsec/C5)")

    doc_md = f"""---
title: Autonomous EVE Online Exploration, Ghost Sites & Hacking Coherence Engine
category: Exploration & Hacking
tags: [EVE, Exploration, RelicAnalyzer, DataAnalyzer, GhostSites, SleeperCaches, HackingCoherence, Loot]
last_updated: 2026-08-14
---

# 🧭 Autonomous Exploration, Ghost Sites & Hacking Coherence Engine

This document details the mechanics governing Relic/Data hacking minigames, Covert Research Ghost Sites detonation timers, and Sleeper Cache puzzle mechanics.

---

## 💻 1. Hacking Minigame Coherence & Virus Calculus
- **Equipped Analyzer**: **{hack_sim['analyzer']} (with T2 Emission Scope Rig)**
- **Player Virus Strength**: **{hack_sim['total_virus_strength']} Damage / Click**
- **Player Max Virus Coherence**: **{hack_sim['max_virus_coherence']} Coherence HP**
- **Hack Outcome**: **`{hack_sim['hack_result']}`** (Remaining Coherence: `{hack_sim['remaining_coherence']}` HP)

### Defense Node Encounter Combat Ledger
"""
    for log in hack_sim["combat_log"]:
        doc_md += f"- **{log['node']}** (`{log['node_hp']} HP`): Defeated in `{log['hits_required']}` clicks | Took `{log['damage_taken']}` damage $\\rightarrow$ Remaining HP: `{log['coherence_after_combat']}`\n"

    doc_md += f"""
---

## 💥 2. Covert Research Ghost Sites (High-Risk Detonation Windows)
- **Site Type**: `{ghost_calc['site_type']}`
- **Detonation Timer Window**: **{ghost_calc['detonation_limit_s']} Seconds** before pirate cruisers warp in and self-destruct cans.
- **Detonation Explosive Shockwave**: **{ghost_calc['raw_explosion_damage']:,} Raw Explosive Damage**
- **Ship Tank Assessment**: `{ghost_calc['ship_survival_status']}` (Ship EHP: `{ghost_calc['ship_ehp']:,}` vs Applied `{ghost_calc['damage_taken_after_resists']:,}`)

---

## 🏛️ 3. Sleeper Cache Classification & Hazard Mitigation
1. **Limited Sleeper Cache (Frigates)**: Defense grid deactivation sequence; explosive proximity clouds.
2. **Standard Sleeper Cache (Cruisers / Astero)**: Spatial rift navigation; plasma defense matrix overrides.
3. **Superior Sleeper Cache (Stratios / T3C)**: Multi-chamber defense grid; Tractor Unit puzzle; **150M to 400M ISK in high-tier blueprints**.
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_exploration_markdown()
    print(f"Generated exploration document: {files}")
