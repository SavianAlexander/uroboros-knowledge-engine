"""
EVE Online Faction Warfare (FW) Warzone & System Contestation Engine.

Fetches live system contestation status, victory points, and occupier factions across
all Caldari vs Gallente and Amarr vs Minmatar warzones from ESI (/fw/systems/ and /fw/wars/).

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
FW_DIR = os.path.join(VAULT_EVE_DIR, "Faction_Warfare")

ESI_BASE = "https://esi.evetech.net/latest"
USER_AGENT = "Uroboros-Knowledge-Engine/6.0 (Faction Warfare; contact: admin@uroboros.local)"

FACTION_NAMES = {
    500001: "Caldari State",
    500002: "Minmatar Republic",
    500003: "Amarr Empire",
    500004: "Gallente Federation",
    500020: "Guristas Pirates",
    500024: "Angel Cartel",
}


def make_request(endpoint: str) -> list | dict:
    url = f"{ESI_BASE}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except Exception as ex:
        print(f"⚠️ FW ESI request error: {ex}")
        return []


def resolve_systems(ids: list) -> dict:
    valid_ids = list({int(i) for i in ids if isinstance(i, (int, str)) and str(i).isdigit() and int(i) > 0})
    if not valid_ids:
        return {}
    name_map = {}
    for i in range(0, len(valid_ids), 1000):
        chunk = valid_ids[i : i + 1000]
        try:
            req = urllib.request.Request(f"{ESI_BASE}/universe/names/", data=json.dumps(chunk).encode("utf-8"), headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if isinstance(res, list):
                    for item in res:
                        name_map[item.get("id")] = item.get("name")
        except Exception:
            pass
    return name_map


def generate_fw_markdown(output_dir: str = FW_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []
    sync_time_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

    fw_systems = make_request("/fw/systems/")
    fw_wars = make_request("/fw/wars/")

    sys_ids = [s.get("solar_system_id") for s in fw_systems]
    resolved_sys = resolve_systems(sys_ids)

    # 1. Contested Systems Matrix (Sorted by contest percentage)
    contested_rows = []
    highly_contested = sorted(fw_systems, key=lambda x: (x.get("victory_points", 0) / max(1, x.get("victory_points_threshold", 1))), reverse=True)

    for s in highly_contested[:40]:
        sname = resolved_sys.get(s.get("solar_system_id"), f"System {s.get('solar_system_id')}")
        owner = FACTION_NAMES.get(s.get("owner_faction_id"), f"Faction {s.get('owner_faction_id')}")
        occupier = FACTION_NAMES.get(s.get("occupier_faction_id"), f"Faction {s.get('occupier_faction_id')}")
        vp = s.get("victory_points", 0)
        vp_thresh = s.get("victory_points_threshold", 1)
        contest_pct = (vp / max(1, vp_thresh)) * 100.0
        status = "🔴 VULNERABLE" if contest_pct >= 100 else ("🟡 CONTESTED" if contest_pct > 20 else "🟢 STABLE")

        contested_rows.append(f"| **{sname}** | **{occupier}** | {owner} | **`{contest_pct:.1f}%`** | `{status}` | {vp:,} / {vp_thresh:,} VP |")

    table_md = "\n".join(contested_rows)
    fw_file = os.path.join(output_dir, "fw_warzone_overview.md")
    fw_md = f"""# EVE Online: Faction Warfare Direct Enlistment & Warzone Overview

Live tactical intelligence across the Caldari/Gallente, Amarr/Minmatar, and Pirate Insurgency warzones.

- **Total FW Contested Systems**: **{len(fw_systems)} Systems**
- **Last Synchronized**: `{sync_time_str}`

| Solar System | Current Occupier | Original Owner | Contested % | Combat Status | Victory Points |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_md}
"""
    with open(fw_file, "w", encoding="utf-8") as f:
        f.write(fw_md)
    created_files.append(fw_file)

    return created_files
