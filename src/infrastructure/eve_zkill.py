"""
EVE Online zKillboard Public Threat Intelligence & Combat Forensics Engine.

Fetches public killboard metrics, all-time danger rankings, gang vs solo efficiency ratios,
and target destruction histories from zKillboard API:
- Pilot combat profile: Savian Alexander (ID: 2122349505)
- Corporation threat profile: KarmaFleet (ID: 98370861)
- Alliance threat profile: Goonswarm Federation (ID: 1354830081)
- Hostile / Rival profile: Pandemic Horde Inc. (ID: 98388312)

Ponytail: Zero-dependency stdlib implementation (urllib, json, time, os).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
THREAT_DIR = os.path.join(VAULT_EVE_DIR, "Threat_Intel")

ZKILL_BASE = "https://zkillboard.com/api"
USER_AGENT = "Uroboros-Knowledge-Engine/4.0 (Threat Intelligence; contact: admin@uroboros.local)"


def fetch_zkill_stats(entity_type: str, entity_id: int) -> dict:
    """Fetch aggregated killboard statistics for a character/corporation/alliance."""
    url = f"{ZKILL_BASE}/stats/{entity_type}ID/{entity_id}/"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception as ex:
        print(f"⚠️ zKillboard fetch notice for {entity_type} {entity_id}: {ex}")
        return {}


def generate_threat_intel_markdown(output_dir: str = THREAT_DIR) -> list:
    """Generate comprehensive threat profiles and killboard forensics."""
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    targets = [
        ("character", 2122349505, "Savian Alexander", "Fleet Commander / Main Pilot"),
        ("corporation", 98370861, "KarmaFleet", "Primary Fleet Corporation (Goonswarm)"),
        ("alliance", 1354830081, "Goonswarm Federation", "Primary Null-sec Sovereign Alliance"),
        ("corporation", 98388312, "Pandemic Horde Inc.", "Major Null-sec Hostile / Rival Coalition"),
    ]

    summary_rows = []

    for etype, eid, ename, desc in targets:
        stats = fetch_zkill_stats(etype, eid)
        
        isk_destroyed = stats.get("iskDestroyed", 0.0) or 0.0
        isk_lost = stats.get("iskLost", 0.0) or 0.0
        ships_destroyed = stats.get("shipsDestroyed", 0) or 0
        ships_lost = stats.get("shipsLost", 0) or 0
        danger_ratio = stats.get("dangerRatio", 0) or 0
        gang_ratio = stats.get("gangRatio", 0) or 0

        # Efficiency calculation
        total_isk = isk_destroyed + isk_lost
        eff = (isk_destroyed / total_isk * 100.0) if total_isk > 0 else 0.0

        summary_rows.append(f"| **{ename}** | `{etype.capitalize()}` | **{isk_destroyed:,.2f} ISK** | {ships_destroyed:,} kills | {ships_lost:,} losses | `{eff:.1f}%` | `{danger_ratio}%` |")

        # Individual threat dossier
        file_path = os.path.join(output_dir, f"threat_{ename.lower().replace(' ', '_').replace('.', '')}.md")
        top_lists = stats.get("topLists", [])
        top_ships = []
        for tl in top_lists:
            if tl.get("type") == "shipType":
                for item in tl.get("values", [])[:5]:
                    top_ships.append(f"- **{item.get('shipName', 'Ship')}**: {item.get('kills', 0)} kills")

        top_ships_str = "\n".join(top_ships) if top_ships else "*No top ship breakdown available.*"

        doc_md = f"""# zKillboard Threat & Combat Profile: {ename}

- **Entity Type**: `{etype.capitalize()}` (ID: `{eid}`)
- **Description**: {desc}
- **Last Sync**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}

---

## Combat Efficiency & Killboard Statistics
- **Total ISK Destroyed**: **{isk_destroyed:,.2f} ISK**
- **Total ISK Lost**: **{isk_lost:,.2f} ISK**
- **ISK Efficiency**: **{eff:.1f}%**
- **Confirmed Kills**: **{ships_destroyed:,} ships destroyed**
- **Combat Losses**: **{ships_lost:,} ships lost**
- **Danger Rating**: **{danger_ratio}%**
- **Gang / Fleet Combat Ratio**: **{gang_ratio}%**

---

## Top Ships Deployed
{top_ships_str}
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc_md)
        created_files.append(file_path)

    # Master Threat Overview
    summary_path = os.path.join(output_dir, "fleet_threat_summary.md")
    summary_table = "\n".join(summary_rows)
    summary_md = f"""# Alexander Fleet & Coalition Threat Intelligence Matrix

Comprehensive combat intelligence, killboard efficiency, and hostile threat ratings across allied and rival entities.

| Entity Name | Classification | ISK Destroyed | Kills | Losses | ISK Efficiency | Danger Rating |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{summary_table}
"""
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    created_files.append(summary_path)

    return created_files
