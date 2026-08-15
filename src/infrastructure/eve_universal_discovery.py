"""
Autonomous EVE Online Universal Player Portability & Fleet Discovery DAG.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Dynamic character DAG compilation for 1 to 50 arbitrary pilots.
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

VAULT_SYS_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "System_Architecture")


def build_universal_fleet_dag(pilots_roster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Dynamically analyze arbitrary pilot roster and allocate optimal role hierarchy.
    """
    if not pilots_roster:
        return {"status": "error", "message": "Empty pilot roster"}

    # Sort pilots descending by SP
    sorted_pilots = sorted(pilots_roster, key=lambda p: p.get("sp", 0), reverse=True)

    command_lead = sorted_pilots[0]
    harvesters = []
    logistics = []
    scouts_cynos = []

    for idx, p in enumerate(sorted_pilots[1:], 1):
        sp = p.get("sp", 0)
        unallocated = p.get("unallocated_sp", 0)
        total = sp + unallocated

        if idx <= 3 and total > 2000000:
            harvesters.append({"pilot": p["name"], "id": p["id"], "assigned_role": "High-Yield Strip Harvester (Exhumer / Barge)"})
        elif total > 1000000:
            logistics.append({"pilot": p["name"], "id": p["id"], "assigned_role": "Industrial Transport & Planetary Industry Lead"})
        else:
            scouts_cynos.append({"pilot": p["name"], "id": p["id"], "assigned_role": "Cynosural Beacon / Covert Scout Specialist"})

    return {
        "status": "success",
        "total_pilots_discovered": len(pilots_roster),
        "fleet_commander": {"name": command_lead["name"], "id": command_lead["id"], "sp": command_lead.get("sp", 0)},
        "mining_wing_count": len(harvesters),
        "mining_harvesters": harvesters,
        "logistics_wing_count": len(logistics),
        "logistics_pilots": logistics,
        "scout_cyno_wing_count": len(scouts_cynos),
        "scouts_and_cynos": scouts_cynos
    }


import re

def discover_local_roster() -> List[Dict[str, Any]]:
    """Dynamically scan character overview dossiers in the vault."""
    char_root = os.path.join(BASE_DIR, "vault", "Eve Online", "Characters")
    roster = []
    if os.path.isdir(char_root):
        try:
            for entry in sorted(os.listdir(char_root)):
                p = os.path.join(char_root, entry, "overview.md")
                if os.path.isfile(p):
                    with open(p, "r", encoding="utf-8") as f:
                        text = f.read()
                    sp_match = re.search(r'Total Trained SP\*\*:\s*\*\*([\d,]+)\s*SP\*\*(?:\s*\*\(\+([\d,]+)\s*unallocated\*\))?', text)
                    sp = int(sp_match.group(1).replace(",", "")) if sp_match else 0
                    unallocated = int(sp_match.group(2).replace(",", "")) if sp_match and sp_match.group(2) else 0
                    id_match = re.search(r'Character ID\*\*:\s*[`\*]?(\d+)[`\*]?', text)
                    char_id = int(id_match.group(1)) if id_match else 0
                    roster.append({
                        "name": entry,
                        "id": char_id,
                        "sp": sp,
                        "unallocated_sp": unallocated
                    })
        except Exception:
            pass
    return roster


def generate_universal_discovery_markdown() -> List[str]:
    """Generate Universal Player Portability DAG reference document."""
    os.makedirs(VAULT_SYS_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_SYS_DIR, "universal_player_portability_dag.md")

    # Discover local character dossiers dynamically with sample fallback
    local_roster = discover_local_roster()
    active_roster = local_roster if local_roster else [
        {"name": "Savian Alexander", "id": 2122349505, "sp": 74225867, "unallocated_sp": 241613},
        {"name": "Thena Alexander", "id": 2124540459, "sp": 3272860, "unallocated_sp": 0},
        {"name": "Vulcastra Alexander", "id": 2124540474, "sp": 3234190, "unallocated_sp": 0},
        {"name": "Tulorn Alexander", "id": 2124540480, "sp": 3242830, "unallocated_sp": 0},
        {"name": "Saigan Alexander", "id": 2124540489, "sp": 642287, "unallocated_sp": 1000000},
        {"name": "Targon Alexander", "id": 2124540495, "sp": 421305, "unallocated_sp": 1000000},
        {"name": "Tila Alexander", "id": 2124540497, "sp": 424002, "unallocated_sp": 1000000},
        {"name": "Rataghast Alexander", "id": 2124540504, "sp": 423998, "unallocated_sp": 1000000}
    ]
    dag = build_universal_fleet_dag(active_roster)

    doc_md = f"""---
title: Autonomous EVE Online Universal Player Portability & Fleet Discovery DAG
category: System Architecture
tags: [EVE, UniversalPortability, DynamicDiscovery, FleetDAG, RosterAllocation, MultiUser, OpenSource]
last_updated: 2026-08-14
---

# 🌐 Autonomous Universal Player Portability & Fleet Discovery DAG

This document establishes the dynamic auto-discovery architecture enabling Neuro Alexander to ingest any player's roster (1 to 50 characters) and compile customized tactical topologies.

---

## 👑 1. Dynamic Roster Allocation Hierarchy
- **Discovered Pilots**: **{dag['total_pilots_discovered']} Characters**
- **Designated Fleet Commander**: **{dag['fleet_commander']['name']}** (`{dag['fleet_commander']['sp']:,} SP`)

### Mining Harvester Wing ({dag['mining_wing_count']} Pilots)
"""
    for h in dag["mining_harvesters"]:
        doc_md += f"- **{h['pilot']}** (`ID: {h['id']}`): `{h['assigned_role']}`\n"

    doc_md += f"\n### Logistics & Industrial Wing ({dag['logistics_wing_count']} Pilots)\n"
    for l in dag["logistics_pilots"]:
        doc_md += f"- **{l['pilot']}** (`ID: {l['id']}`): `{l['assigned_role']}`\n"

    doc_md += f"\n### Cynosural & Forward Recon Wing ({dag['scout_cyno_wing_count']} Pilots)\n"
    for s in dag["scouts_and_cynos"]:
        doc_md += f"- **{s['pilot']}** (`ID: {s['id']}`): `{s['assigned_role']}`\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_universal_discovery_markdown()
    print(f"Generated universal discovery document: {files}")
