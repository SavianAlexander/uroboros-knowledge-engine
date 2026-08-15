"""
Autonomous EVE Online Multi-Boxing Mind & Tactical Role-Thinking Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Zero external pip dependencies, deep empirical introspection.
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

VAULT_FLEET_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Fleet_Operations")

FLEET_MIND_STATE = {
    2122349505: {
        "name": "Savian Alexander",
        "sp": 74225867,
        "unallocated_sp": 241152,
        "location": "G-EURJ",
        "active_ship": "Porpoise (Pillar of Autumn)",
        "role": "Fleet Commander & Industrial Booster Lead",
        "current_operational_intent": "Leading G-EURJ mining operation with Porpoise Industrial Command Burst II; providing -28.5% cycle time reduction and +38% laser range to Covetor wing; compressing ore in fleet hangar.",
        "role_thinking": {
            "mindset": "Tactical Fleet Commander & Sovereign Protector",
            "active_responsibilities": [
                "Maintain active Mining Foreman Burst II (Mining Laser Optimization Charge) cycle",
                "Spool Fleet Hangar Ore Compression Unit for immediate mineral density compaction",
                "Active D-Scan (14.3 AU, 360 degrees) monitoring for hostile combat probes or neut ships",
                "Lock and monitor shield buffers of Thena, Vulcastra, and Tulorn"
            ]
        },
        "proactive_next_actions": [
            "Inject 241,152 unallocated SP into Capital Industrial Ships or Black Ops V",
            "Prepare Paladin Marauder refit for Nullsec Level 5 / Blood Raider combat escalations",
            "Stage Ansiblex Jump Gate bookmark for instant fleet extraction"
        ],
        "protective_defense_protocols": [
            "Keep 5x Valkyrie II / Infiltrator II combat drones assigned to defend Covetor wing",
            "Pre-align Porpoise to Safe Citadel Tether Bookmark (0 m/s alignment)",
            "Trigger Fleet Broadcast 'Warp to Bookmark: Safe 1' upon hostile local flash"
        ]
    },
    2124540459: {
        "name": "Thena Alexander",
        "sp": 3272860,
        "unallocated_sp": 0,
        "location": "G-EURJ",
        "active_ship": "Covetor (Vintage Prowler)",
        "role": "High-Yield Strip Mining Harvester Wing 1",
        "current_operational_intent": "Strip mining high-grade Moon Ore / Spodumain in G-EURJ asteroid belt; depositing uncompressed ore directly into Savian's Porpoise fleet hangar; training Reprocessing V (completes Aug 17).",
        "role_thinking": {
            "mindset": "Precision Extraction & Skill Acquisition",
            "active_responsibilities": [
                "Lock and cycle 2x Modulated Strip Miner II on highest density moon rock",
                "Synchronize laser cycles with Vulcastra and Tulorn to prevent depleted rock cycle waste",
                "Continuously drag mined ore into Savian's Porpoise Fleet Hangar"
            ]
        },
        "proactive_next_actions": [
            "Upon Reprocessing V completion (Aug 17), immediately inject Reprocessing Efficiency V -> Moon Ore IV",
            "Train Exhumers V to upgrade hull from Covetor -> Hulk (+45% m3/s yield enhancement)",
            "Fit Mining Laser Upgrade II in low slots to optimize m3 extraction rate"
        ],
        "protective_defense_protocols": [
            "Maintain Keep at Range 2,500m on Savian's Porpoise",
            "Deploy 5x Hobgoblin II light drones to form combined fleet anti-frigate ball",
            "Set Watchlist on Savian Alexander for instant fleet warp command"
        ]
    },
    2124540474: {
        "name": "Vulcastra Alexander",
        "sp": 3234190,
        "unallocated_sp": 0,
        "location": "G-EURJ",
        "active_ship": "Covetor (Vintage Prowler)",
        "role": "High-Yield Strip Mining Harvester Wing 2",
        "current_operational_intent": "Strip mining Moon Ore / Mercoxit in G-EURJ asteroid belt; training Reprocessing V (completes Aug 17).",
        "role_thinking": {
            "mindset": "Laser Synchronization & Production Throughput",
            "active_responsibilities": [
                "Target distinct asteroid chunk from Thena to maximize dual-laser efficiency",
                "Verify crystal damage levels and swap T2 crystals when wear exceeds 80%",
                "Maintain constant fleet hangar feed"
            ]
        },
        "proactive_next_actions": [
            "Complete Reprocessing V -> Reprocessing Efficiency V skill progression",
            "Prepare Hulk hull procurement in 1DQ1-A / Jita trade hubs",
            "Train Metallurgy V for T2 BPO research and manufacturing"
        ],
        "protective_defense_protocols": [
            "Maintain Keep at Range 2,500m on Savian's Porpoise",
            "Align to emergency safe citadel beacon",
            "Emergency warp on fleet broadcast"
        ]
    },
    2124540480: {
        "name": "Tulorn Alexander",
        "sp": 3242830,
        "unallocated_sp": 0,
        "location": "G-EURJ",
        "active_ship": "Covetor (Vintage Prowler)",
        "role": "High-Yield Strip Mining Harvester Wing 3",
        "current_operational_intent": "Strip mining Moon Ore in G-EURJ; training Reprocessing V (completes Aug 17).",
        "role_thinking": {
            "mindset": "Yield Maximization & Defensive Cohesion",
            "active_responsibilities": [
                "Maintain third strip miner wing on secondary moon ore cluster",
                "Monitor Porpoise fleet compression state",
                "Maintain shared drone swarm"
            ]
        },
        "proactive_next_actions": [
            "Complete Reprocessing V -> Reprocessing Efficiency V",
            "Train Exhumers V for Hulk upgrade",
            "Train Gas Cloud Mining V for high-value wormhole/null gas harvesting"
        ],
        "protective_defense_protocols": [
            "Keep at Range 2,500m on Savian's Porpoise",
            "Follow fleet align broadcast commands instantly",
            "Engage rat frigate aggressors with light drones"
        ]
    },
    2124540489: {
        "name": "Saigan Alexander",
        "sp": 642287,
        "unallocated_sp": 1000000,
        "location": "Hodrold",
        "active_ship": "Velator",
        "role": "Planetary Industry & Industrial Logistics Specialist (1M SP Reserve)",
        "current_operational_intent": "Staged in Metropolis NPC station; holding 1,000,000 Unallocated SP reserve ready for specialized industrial deployment.",
        "role_thinking": {
            "mindset": "Passive Wealth Generation & Supply Chain Expansion",
            "active_responsibilities": [
                "Safely docked in Hodrold station",
                "Evaluating 6-planet PI network setup across Heimatar / Metropolis",
                "Ready for instant SP injection"
            ]
        },
        "proactive_next_actions": [
            "Inject 1M Unallocated SP into: Command Center Upgrades V + Interplanetary Consolidation V (6 Planets) + Transport Ships IV (Epithal PI Hauler)",
            "Deploy 6x High-Yield PI Factory extraction setups producing P2/P3 Robotics & Guidance Systems (+600M ISK/month passive)",
            "Stage Epithal hauler with Inertial Stabilizers and Cloak"
        ],
        "protective_defense_protocols": [
            "Operate exclusively within NPC stations or insta-dock citadel perches",
            "Use Epithal MWD-Cloak trick for all planetary customs office pickups"
        ]
    },
    2124540495: {
        "name": "Targon Alexander",
        "sp": 421305,
        "unallocated_sp": 1000000,
        "location": "Mettle",
        "active_ship": "Ibis",
        "role": "Dedicated Cynosural Beacon & Covert Scout Specialist (1M SP Reserve)",
        "current_operational_intent": "Staged in Metropolis; holding 1,000,000 Unallocated SP reserve.",
        "role_thinking": {
            "mindset": "Capital Jump Navigator & Waypoint Beacon Specialist",
            "active_responsibilities": [
                "Docked in Mettle station",
                "Ready to position at Delve -> Jita Cyno Waypoint"
            ]
        },
        "proactive_next_actions": [
            "Inject 1M Unallocated SP into: Cynosural Field Theory V + Cloaking IV + Recon Ships / Blockade Runners (Falcon/Araphel)",
            "Deploy to Cyno Waypoint System (e.g. 31-MLU or Hophib) with Liquid Ozone reserves to light beacons for Savian's Jump Freight runs",
            "Create Safe Cyno Perches 1,000km off stations"
        ],
        "protective_defense_protocols": [
            "Light cyno beacons strictly on Upwell structure docking tethers",
            "Pre-dock before cyno module burn ends"
        ]
    },
    2124540497: {
        "name": "Tila Alexander",
        "sp": 424002,
        "unallocated_sp": 1000000,
        "location": "Mettle",
        "active_ship": "Velator",
        "role": "Deep Space Transport & Blockade Runner Specialist (1M SP Reserve)",
        "current_operational_intent": "Staged in Metropolis; holding 1,000,000 Unallocated SP reserve.",
        "role_thinking": {
            "mindset": "Secure High-Value Transit & Smuggling Logistics",
            "active_responsibilities": [
                "Docked in Mettle station",
                "Evaluating Highsec -> Lowsec route security"
            ]
        },
        "proactive_next_actions": [
            "Inject 1M Unallocated SP into: Minmatar Hauler V + Transport Ships IV (Prowler Blockade Runner / Mastodon DST)",
            "Fit Prowler with Covert Ops Cloak II + 50MN MWD (Sub-2s align time, completely immune to gate cargo scanners)",
            "Execute compressed moon mineral transport from G-EURJ to Jita 4-4"
        ],
        "protective_defense_protocols": [
            "Never haul without Covert Cloak active",
            "Use Insta-Undock and Insta-Dock bookmarks at all trade hubs"
        ]
    },
    2124540504: {
        "name": "Rataghast Alexander",
        "sp": 423998,
        "unallocated_sp": 1000000,
        "location": "Mettle",
        "active_ship": "Velator",
        "role": "Regional Trade Hub Tycoon & Planetary Industry Specialist (1M SP Reserve)",
        "current_operational_intent": "Staged in Metropolis; holding 1,000,000 Unallocated SP reserve.",
        "role_thinking": {
            "mindset": "Market Arbitrage & Capital Accumulation",
            "active_responsibilities": [
                "Docked in Mettle station",
                "Evaluating regional price spreads between Jita 4-4 and Rens/Amarr"
            ]
        },
        "proactive_next_actions": [
            "Inject 1M Unallocated SP into: Trade V + Retail V + Wholesale V + Accounting V + Broker Relations V",
            "Establish 100+ automated buy/sell orders in Jita 4-4 and local alliance market hubs",
            "Setup secondary 6-planet PI factory colony"
        ],
        "protective_defense_protocols": [
            "Station trader profile: 0 undock exposure; immune to PvP and gank mechanics"
        ]
    }
}


def get_multibox_mind_state() -> Dict[str, Any]:
    """Retrieve the entire multi-boxing fleet operational mindset and tactical intent."""
    return {
        "timestamp": time.time(),
        "active_pilots_count": len(FLEET_MIND_STATE),
        "fleet_topology": "Master-Follower (Savian Command Porpoise + 3x Covetor Strippers + 4x Alpha Reserves)",
        "pilots": FLEET_MIND_STATE
    }


def get_pilot_action_recommendations(character_id: int) -> Dict[str, Any]:
    """Retrieve actionable next steps and protective protocols for a specific pilot."""
    pilot = FLEET_MIND_STATE.get(character_id)
    if not pilot:
        return {"status": "error", "message": f"Character {character_id} not found in fleet roster"}
    return {
        "character_id": character_id,
        "name": pilot["name"],
        "role": pilot["role"],
        "location": pilot["location"],
        "active_ship": pilot["active_ship"],
        "role_thinking": pilot["role_thinking"],
        "proactive_next_actions": pilot["proactive_next_actions"],
        "protective_defense_protocols": pilot["protective_defense_protocols"]
    }


def generate_multibox_doctrine_markdown() -> List[str]:
    """Generate Multi-Boxing Fleet Synchronization & Role-Thinking doctrine document."""
    os.makedirs(VAULT_FLEET_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_FLEET_DIR, "multibox_fleet_synchronization_doctrine.md")

    mind = get_multibox_mind_state()

    doc_md = f"""---
title: Autonomous EVE Online Multi-Boxing Mind & Tactical Role-Thinking Doctrine
category: Fleet Operations
tags: [EVE, MultiBoxing, FleetMind, RoleThinking, Synchronization, Porpoise, Covetor, SPAllocation, CynoChain, Defense]
last_updated: 2026-08-14
---

# 🧠 Autonomous Multi-Boxing Mind & Tactical Role-Thinking Doctrine

This document establishes the multi-boxing operational protocols, real-time role-thinking logic, proactive progression roadmaps, and protective defensive procedures across the entire 8-character fleet.

---

## 👥 1. Fleet Operational Introspection (8 Characters)

"""
    for cid, p in mind["pilots"].items():
        doc_md += f"""### 🎖️ {p['name']} (`ID: {cid}`) — **{p['role']}**
- **Location**: `{p['location']}` | **Active Ship**: `{p['active_ship']}`
- **Skill Points**: **{p['sp']:,} SP** (Unallocated: `{p['unallocated_sp']:,} SP`)
- **Current Operational Intent**: {p['current_operational_intent']}

#### 💭 Active Role Thinking:
"""
        for resp in p["role_thinking"]["active_responsibilities"]:
            doc_md += f"- {resp}\n"

        doc_md += "\n#### ⚡ Proactive Next Steps (Yield & Progression):\n"
        for act in p["proactive_next_actions"]:
            doc_md += f"- {act}\n"

        doc_md += "\n#### 🛡️ Protective Defense Protocols:\n"
        for prot in p["protective_defense_protocols"]:
            doc_md += f"- {prot}\n"

        doc_md += "\n---\n\n"

    doc_md += """
## 🔄 2. Multi-Box Synchronization & Macro Topologies

### Topology A: Moon Harvester Grid (Porpoise + 3x Covetor)
1. **Master Lead (Savian)**: Warps fleet to moon anomaly; pulses Mining Foreman Burst II; locks all 3 Covetors.
2. **Follower Harvesters (Thena, Vulcastra, Tulorn)**: Keep at Range 2,500m on Porpoise; split strip lasers across 6 high-yield rock chunks; continuous drag-and-drop into Porpoise Fleet Hangar.
3. **Emergency Panic Response**: If hostile neut enters local or D-Scan $<14.3\\text{ AU}$, Savian triggers Fleet Align to Safe Citadel Tether; all ships recall drones and warp in unison.

### Topology B: 48-Planet Factory Network (Passive ISK Engine)
- **8 Pilots $\\times$ 6 Planets = 48 Planetary Hubs**
- Saigan, Targon, Tila, and Rataghast inject 1M SP into Command Center Upgrades V -> Produce P4 Broadcast Nodes -> **+4.8 Billion ISK / Month passive revenue**.

### Topology C: Capital Cyno Chain Highway (Delve -> Jita)
- **Waypoints**: 1DQ1-A -> KDF-GY -> 31-MLU -> 0SHT-A -> Hophib -> Ignoitton -> Jita 4-4.
- Targon and Saigan light cyno beacons on station tethers, allowing Savian's Jump Freighter to transit 30.47 LY in $<12$ minutes with zero fatigue penalty.
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_multibox_doctrine_markdown()
    print(f"Generated multibox doctrine document: {files}")
