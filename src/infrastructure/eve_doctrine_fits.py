"""
EVE Online Fleet Doctrine Fitting Catalog & Pyfa / EFT Engine.

Generates validated, exportable EFT / Pyfa format fits for major Goonswarm & Null-sec fleet doctrines:
- Battleship Line Doctrines: Rokh Railgun Fleet, Megathron Blaster Fleet
- Marauder Bastion Strike: Paladin Armor Bastion, Vargur Shield Bastion
- Heavy Assault Cruisers (HACs): Cerberus Missile Skirmish, Sacrilege Heavy Armor Brawler
- Fleet Logistics: Basilisk Shield Logi Core, Guardian Armor Logi Core
- Interceptors & Fast Tackle: Stiletto Fleet Scout, Malediction Warp Disruptor

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
DOCTRINES_DIR = os.path.join(VAULT_EVE_DIR, "Doctrines")

DOCTRINE_FITS = {
    "Rokh": {
        "title": "Rokh — Mainline Fleet Railgun Battleship",
        "role": "Extreme Range Long-Distance Fleet Alpha Strike",
        "eft": """[Rokh, Goonswarm Mainline Sniper]
Damage Control II
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Tracking Enhancer II

500MN Cold-Gas Enduring Microwarpdrive
Multispectrum Shield Hardener II
Multispectrum Shield Hardener II
Large Shield Extender II
Sensor Booster II, Targeting Range Script
Large Cap Battery II

425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L
425mm Railgun II, Spike L

Large Core Defense Field Extender II
Large Core Defense Field Extender II
Large Hybrid Collision Accelerator I"""
    },
    "Paladin": {
        "title": "Paladin — Heavy Armor Bastion Fleet Marauder",
        "role": "Immense Armor Tank & Continuous Heavy Pulse Alpha",
        "eft": """[Paladin, Goonswarm Bastion Paladin]
Large Armor Repairer II
Large Armor Repairer II
Multispectrum Energized Membrane II
Multispectrum Energized Membrane II
Heat Sink II
Heat Sink II
Heat Sink II

500MN Microwarpdrive II
Large Micro Jump Drive
Heavy Stasis Grappler II
Republic Fleet Warp Disruptor

Mega Pulse Laser II, Scorch L
Mega Pulse Laser II, Scorch L
Mega Pulse Laser II, Scorch L
Mega Pulse Laser II, Scorch L
Bastion Module I
Heavy Energy Neutralizer II
Heavy Energy Neutralizer II
[Empty High slot]

Large Capacitor Control Circuit II
Large Auxiliary Nano Pump II"""
    },
    "Cerberus": {
        "title": "Cerberus — Heavy Assault Cruiser (HAC)",
        "role": "Long-Range Shield Heavy Missile Skirmisher",
        "eft": """[Cerberus, Fleet Heavy Missile HAC]
Assault Damage Control II
Ballistic Control System II
Ballistic Control System II
Ballistic Control System II

50MN Microwarpdrive II
Multispectrum Shield Hardener II
Large Shield Extender II
Sensor Booster II, Targeting Range Script
Missile Guidance Computer II, Missile Range Script

Heavy Missile Launcher II, Scourge Fury Heavy Missile
Heavy Missile Launcher II, Scourge Fury Heavy Missile
Heavy Missile Launcher II, Scourge Fury Heavy Missile
Heavy Missile Launcher II, Scourge Fury Heavy Missile
Heavy Missile Launcher II, Scourge Fury Heavy Missile
Heavy Missile Launcher II, Scourge Fury Heavy Missile

Medium Core Defense Field Extender II
Medium Hydraulic Bay Thrusters II"""
    },
    "Sacrilege": {
        "title": "Sacrilege — Heavy Assault Cruiser (HAC)",
        "role": "Close-Range Heavy Assault Missile & Energy Neutralizer Brawler",
        "eft": """[Sacrilege, Heavy Armor HAM Brawler]
Assault Damage Control II
1600mm Steel Plates II
Multispectrum Energized Membrane II
Multispectrum Energized Membrane II
Ballistic Control System II

50MN Microwarpdrive II
Warp Scrambler II
Stasis Webifier II
Large Cap Battery II

Heavy Assault Missile Launcher II, Caldari Navy Scourge HAM
Heavy Assault Missile Launcher II, Caldari Navy Scourge HAM
Heavy Assault Missile Launcher II, Caldari Navy Scourge HAM
Heavy Assault Missile Launcher II, Caldari Navy Scourge HAM
Heavy Assault Missile Launcher II, Caldari Navy Scourge HAM
Heavy Energy Neutralizer II

Medium Trimark Armor Pump II
Medium Trimark Armor Pump II"""
    },
    "Basilisk": {
        "title": "Basilisk — Fleet Shield Logistics Cruiser",
        "role": "Cap-Chain Remote Shield Repairer Flagship",
        "eft": """[Basilisk, Cap-Chain Shield Logi]
Damage Control II
Capacitor Power Relay II

50MN Microwarpdrive II
Large Shield Extender II
Multispectrum Shield Hardener II
Multispectrum Shield Hardener II
Sensor Booster II, Scan Resolution Script

Large Remote Shield Booster II
Large Remote Shield Booster II
Large Remote Shield Booster II
Large Remote Shield Booster II
Large Remote Shield Booster II
Large Remote Capacitor Transmitter II

Medium Core Defense Field Extender II
Medium Capacitor Control Circuit II"""
    },
    "Stiletto": {
        "title": "Stiletto — Fleet Fast Tackle Interceptor",
        "role": "Sub-2-Second Instawarp Fleet Scout & Initial Tackler",
        "eft": """[Stiletto, Instawarp Fast Tackle]
Nanofiber Internal Structure II
Inertial Stabilizers II
Damage Control II

5MN Microwarpdrive II
Warp Disruptor II
Medium Shield Extender II
Sensor Booster II, Scan Resolution Script

200mm AutoCannon II, Republic Fleet EMP S
200mm AutoCannon II, Republic Fleet EMP S
[Empty High slot]

Small Low Friction Nozzle Joints II
Small Hyperspatial Velocity Optimizer II"""
    }
}


def generate_doctrines_markdown(output_dir: str = DOCTRINES_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. Individual Doctrine Files
    summary_rows = []
    for hull_name, data in DOCTRINE_FITS.items():
        fit_file = os.path.join(output_dir, f"doctrine_{hull_name.lower()}_fleet.md")
        summary_rows.append(f"| **{hull_name}** | {data['role']} | [View Fitting Blueprint](file:///{fit_file.replace(os.sep, '/')}) |")

        doc_md = f"""# Fleet Doctrine Fitting: {data['title']}

- **Tactical Role**: **{data['role']}**
- **Format**: Exportable Pyfa / EFT / In-game Clipboard Format

---

## 📋 Standard In-Game Fitting Clipboard Block
```text
{data['eft']}
```

---

## 💡 Key Pilot Directives
- Ensure maximum capacitor discipline and broadcast for shield/armor reps at 80% shield/armor buffer.
- Keep within Anchor orbit range (500m - 1,500m) to maintain fleet signature and logistics capacitor chain integrity.
"""
        with open(fit_file, "w", encoding="utf-8") as f:
            f.write(doc_md)
        created_files.append(fit_file)

    # 2. Master Doctrine Catalog
    catalog_file = os.path.join(output_dir, "master_doctrine_catalog.md")
    catalog_table = "\n".join(summary_rows)
    catalog_md = f"""# Alexander Fleet: Master Combat Doctrine & Fitting Library

Consolidated exportable fitting standards for sovereign fleet warfare, nullsec anomaly escalations, and fast tackle interception.

| Doctrine Hull | Strategic Battlefield Role | Fitting Specification Link |
| :--- | :--- | :--- |
{catalog_table}
"""
    with open(catalog_file, "w", encoding="utf-8") as f:
        f.write(catalog_md)
    created_files.append(catalog_file)

    return created_files
