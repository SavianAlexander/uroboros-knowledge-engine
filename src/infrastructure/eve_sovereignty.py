"""
EVE Online Null-sec Sovereignty & Coalition Territory Engine.

Fetches live sovereignty ownership across all 3,000+ null-sec solar systems (/sovereignty/map/),
calculates coalition territorial holding metrics, and generates geopolitical maps.

Ponytail: Zero-dependency stdlib implementation (urllib, json, time, os, collections).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from collections import defaultdict

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
SOV_DIR = os.path.join(VAULT_EVE_DIR, "Sovereignty")

ESI_BASE = "https://esi.evetech.net/latest"
USER_AGENT = "Uroboros-Knowledge-Engine/6.0 (Sovereignty; contact: admin@uroboros.local)"


def make_request(endpoint: str) -> list | dict:
    url = f"{ESI_BASE}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except Exception as ex:
        print(f"⚠️ Sov ESI request error: {ex}")
        return []


def resolve_names(ids: list) -> dict:
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


def generate_sovereignty_markdown(output_dir: str = SOV_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []
    sync_time_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

    sov_map = make_request("/sovereignty/map/")
    
    alliance_systems = defaultdict(list)
    for s in sov_map:
        aid = s.get("alliance_id")
        if aid:
            alliance_systems[aid].append(s.get("system_id") or s.get("solar_system_id"))

    # Resolve alliance names
    alliance_ids = list(alliance_systems.keys())
    resolved_alliances = resolve_names(alliance_ids)

    # Rank alliances by number of held systems
    ranked = sorted(alliance_systems.items(), key=lambda x: len(x[1]), reverse=True)

    sov_rows = []
    for aid, sys_list in ranked[:35]:
        aname = resolved_alliances.get(aid, f"Alliance {aid}")
        sov_rows.append(f"| **{aname}** | **{len(sys_list)} Systems** | `{aid}` |")

    sov_table = "\n".join(sov_rows)

    sov_file = os.path.join(output_dir, "nullsec_sovereignty_map.md")
    sov_md = f"""# EVE Online: Null-Sec Sovereignty & Coalition Territory Matrix

Live territorial control matrix of sovereign alliances across New Eden.

- **Total Sovereign Star Systems**: **{sum(len(v) for v in alliance_systems.values()):,} Systems**
- **Active Sovereign Alliances**: **{len(alliance_systems)} Alliances**
- **Last Geopolitical Scan**: `{sync_time_str}`

---

## Top Sovereign Alliances by System Holdings
| Alliance Name | Controlled Systems | Alliance ID |
| :--- | :--- | :--- |
{sov_table}
"""
    with open(sov_file, "w", encoding="utf-8") as f:
        f.write(sov_md)
    created_files.append(sov_file)

    return created_files
