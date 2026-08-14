"""
EVE Online DED Combat Complexes & Burner Mission Tactical Engine.

Exhaustive operational references for:
- DED Combat Complexes (1/10 to 10/10) & Unrated Escalations across New Eden
- Damage Profiles, Primary NPC Weaknesses, Overseer Bosses & Deadspace Loot Tables (A-Type, X-Type, Officer)
- Level 4 Security Burner Missions (Anomic Agent, Team, Base) Tactical Blitz Guides & Counter-Fitting

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time).
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
ANOMALY_DIR = os.path.join(VAULT_EVE_DIR, "Combat_Anomalies")

DED_COMPLEX_DATABASE = [
    {
        "ded_level": "1/10",
        "name": "Guristas Hideout / Blood Lookout",
        "security": "Highsec (0.9 - 1.0)",
        "ship_class": "Frigates Only",
        "dmg_dealt": "Kinetic / Thermal (Guristas) or EM / Thermal (Blood)",
        "optimal_resist": "Kinetic / Thermal",
        "top_drops": "Pithi C-Type Modules, Small Deadspace Boosters"
    },
    {
        "ded_level": "2/10",
        "name": "Guristas Guerrilla Grounds / Angel Drama",
        "security": "Highsec (0.8 - 0.9)",
        "ship_class": "Frigates & Destroyers",
        "dmg_dealt": "Kin / Therm or Exp / Kin",
        "optimal_resist": "Kinetic / Explosive",
        "top_drops": "Coreli C-Type / Pithi B-Type Modules"
    },
    {
        "ded_level": "3/10",
        "name": "Sansha Annex / Guristas Hall",
        "security": "Highsec (0.7 - 0.8)",
        "ship_class": "Frigates, Destroyers, Cruisers",
        "dmg_dealt": "EM / Thermal (Sansha) / Kin / Therm",
        "optimal_resist": "EM / Thermal",
        "top_drops": "Centii A-Type Modules, Faction Cruiser BPCs (Worm, Succubus)"
    },
    {
        "ded_level": "4/10",
        "name": "Guristas Scout Outpost / Mul-Zatah Monastery",
        "security": "Highsec (0.5 - 0.6)",
        "ship_class": "Cruisers, Battlecruisers",
        "dmg_dealt": "Kin / Therm or EM / Therm",
        "optimal_resist": "Kinetic / Thermal / EM",
        "top_drops": "Pithum C-Type / Centum C-Type Modules, Gila / Phantasm BPCs"
    },
    {
        "ded_level": "5/10",
        "name": "Angel Red Light District / Blood Raider Facility",
        "security": "Lowsec (0.3 - 0.4)",
        "ship_class": "Cruisers, Battlecruisers, Heavy Assault Cruisers",
        "dmg_dealt": "Explosive / Kinetic or EM / Thermal",
        "optimal_resist": "Explosive / EM",
        "top_drops": "Corelum A-Type / Corpum A-Type Modules, Cynabal / Ashimmu BPCs"
    },
    {
        "ded_level": "6/10",
        "name": "Guristas Troop Requisition / Sansha Command Relay",
        "security": "Lowsec (0.1 - 0.3)",
        "ship_class": "Cruisers, Battleships, T3C, Marauders",
        "dmg_dealt": "Kinetic / Thermal / EM",
        "optimal_resist": "Kinetic / EM",
        "top_drops": "Pithum A-Type / Centum A-Type, Faction Battleship BPCs"
    },
    {
        "ded_level": "10/10",
        "name": "The Maze (Guristas) / Fleet Staging Point (Angel Cartel)",
        "security": "Null-sec (-0.1 to -1.0)",
        "ship_class": "Battleships, Marauders, T3C, Capital Ships",
        "dmg_dealt": "Massive Kinetic / Thermal (The Maze) or Explosive / Kinetic (Angel 10/10)",
        "optimal_resist": "Specific 85%+ Hardened Resist (Marauder Bastion)",
        "top_drops": "Pith X-Type / Core X-Type Modules, Faction Capital Blueprints, 1.2B+ ISK/site"
    }
]


def generate_anomalies_markdown(output_dir: str = ANOMALY_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. DED Complex Matrix
    ded_rows = []
    for d in DED_COMPLEX_DATABASE:
        ded_rows.append(f"| **{d['ded_level']}** | **{d['name']}** | `{d['security']}` | `{d['ship_class']}` | {d['dmg_dealt']} | **{d['top_drops']}** |")

    ded_table = "\n".join(ded_rows)
    ded_file = os.path.join(output_dir, "ded_complex_matrix.md")
    ded_md = f"""# EVE Online: Master DED Combat Complex Matrix (1/10 to 10/10)

Comprehensive guide to combat complex escalations, ship class restrictions, incoming damage profiles, and deadspace loot yields.

| Tier | Complex Name | Security Class | Max Ship Class Allowed | Damage Dealt | High-Value Deadspace Drops |
| :--- | :--- | :--- | :--- | :--- | :--- |
{ded_table}
"""
    with open(ded_file, "w", encoding="utf-8") as f:
        f.write(ded_md)
    created_files.append(ded_file)

    # 2. Burner Missions Blitz Guide
    burner_file = os.path.join(output_dir, "burner_missions_guide.md")
    burner_md = """# EVE Online: Level 4 Anomic Security Burner Blitz Guide

High-yield tactical counter-fitting guides for Level 4 Security Agent Burner missions (Anomic Agent, Team, Base).

---

## 🎯 Anomic Agent Profiles & Counter-Fits
| Burner Target | Enemy Ship Class | Primary Threats | Optimal Counter Ship | Engagement Doctrine |
| :--- | :--- | :--- | :--- | :--- |
| **Burner Daredevil** | Pirate Frigate | 90% Stasis Web, High Blaster DPS | **Daredevil / Nergal** | High tracking blasters, Thermal/Kinetic hardeners, Overheated Web |
| **Burner Succubus** | Pirate Frigate | High Speed (4500 m/s), EM/Therm Beam Lasers | **Nergal / Hawk** | EM Shield Resist, Tracking Disruption / Heavy Missiles |
| **Burner Dramiel** | Pirate Frigate | High Autocannon Alpha, Dual Small TD | **Daredevil / Jaguar** | Explosive tank, scrambler + webs to negate speed |
| **Burner Cruor** | Pirate Frigate | Heavy Energy Neutralization, Armor Tank | **Wolf / Hawk** | Capacitor Booster injection, long-range kiting artillery |
| **Burner Worm** | Pirate Frigate | Massive Drone DPS (Kinetic/Thermal), Shield Tank | **Garmur / Nergal** | Precision Light Missiles at 45km range |

---

## 💰 Economic Yield
- **Average Blitz Time per Burner**: **90 seconds to 3 minutes**
- **LP & Bounty Yield**: **15,000 - 25,000 LP + 5M ISK bounty + 5M reward per mission** (~**250M - 450M ISK/hr**).
"""
    with open(burner_file, "w", encoding="utf-8") as f:
        f.write(burner_md)
    created_files.append(burner_file)

    return created_files
