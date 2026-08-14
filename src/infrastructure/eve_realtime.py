"""
EVE Online Real-Time Universe Telemetry & Tactical Threat Radar Engine.

Fetches live, real-time universe streams directly from CCP ESI:
- Live Tranquility Server Status & Active Online Player Count (/status/)
- Active Sansha Incursions & Planetary Invasion States (/incursions/)
- Real-Time Solar System Kills (Ship kills, Pod kills, and NPC kills in the last 1h) (/universe/system_kills/)
- Real-Time Stargate Traffic & Jump Conduits in the last 1h (/universe/system_jumps/)
- Live Sovereignty Entosis Campaigns & Defense Vulnerability Timers (/sovereignty/campaigns/)

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
REALTIME_DIR = os.path.join(VAULT_EVE_DIR, "Realtime")

ESI_BASE = "https://esi.evetech.net/latest"
USER_AGENT = "Uroboros-Knowledge-Engine/5.0 (Realtime Telemetry; contact: admin@uroboros.local)"


def make_request(endpoint: str, method: str = "GET", payload: dict | list = None, timeout: int = 20) -> dict | list:
    """Make public rate-limited ESI request."""
    url = f"{ESI_BASE}{endpoint}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    data_bytes = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except Exception as ex:
        print(f"⚠️ Realtime ESI request error for {endpoint}: {ex}")
        return {} if method == "POST" else []


def resolve_names(ids: list) -> dict:
    """Resolve solar system, constellation, alliance IDs."""
    valid_ids = list({int(i) for i in ids if isinstance(i, (int, str)) and str(i).isdigit() and int(i) > 0})
    if not valid_ids:
        return {}

    name_map = {}
    for i in range(0, len(valid_ids), 1000):
        chunk = valid_ids[i : i + 1000]
        try:
            res = make_request("/universe/names/", method="POST", payload=chunk)
            if isinstance(res, list):
                for item in res:
                    name_map[item.get("id")] = item.get("name")
        except Exception:
            pass
    return name_map


def fetch_server_status() -> dict:
    """Get live Tranquility server status and player count."""
    data = make_request("/status/")
    return data if isinstance(data, dict) else {}


def fetch_incursions() -> list:
    """Get active Sansha Incursions."""
    data = make_request("/incursions/")
    return data if isinstance(data, list) else []


def fetch_system_kills() -> list:
    """Get ship, pod, and NPC kills in the last 1 hour."""
    data = make_request("/universe/system_kills/")
    return data if isinstance(data, list) else []


def fetch_system_jumps() -> list:
    """Get stargate jumps in the last 1 hour."""
    data = make_request("/universe/system_jumps/")
    return data if isinstance(data, list) else []


def fetch_sovereignty_campaigns() -> list:
    """Get live sovereignty entosis attack/defense campaigns."""
    data = make_request("/sovereignty/campaigns/")
    return data if isinstance(data, list) else []


def generate_realtime_markdown(output_dir: str = REALTIME_DIR) -> list:
    """Fetch all real-time universe streams and write structured intelligence documents."""
    os.makedirs(output_dir, exist_ok=True)
    created_files = []
    sync_time_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

    # 1. SERVER_STATUS.MD
    status = fetch_server_status()
    players_online = status.get("players", 0)
    server_ver = status.get("server_version", "Tranquility")
    start_time = status.get("start_time", "Unknown")
    vip_mode = "🔴 Active (VIP Only)" if status.get("vip") else "🟢 Open to All Pilots"

    status_file = os.path.join(output_dir, "server_status.md")
    status_md = f"""# EVE Online: Real-Time Tranquility Server Status

- **Live Players Online**: **{players_online:,} Pilots Active**
- **Cluster State**: **🟢 ONLINE**
- **VIP Mode**: {vip_mode}
- **Server Build Version**: `{server_ver}`
- **Cluster Start Time**: `{start_time}`
- **Last Telemetry Heartbeat**: `{sync_time_str}`
- **Tags**: #eveonline, #realtime, #serverstatus, #tranquility
"""
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(status_md)
    created_files.append(status_file)

    # 2. INCURSIONS_RADAR.MD
    incursions = fetch_incursions()
    inc_ids = []
    for inc in incursions:
        inc_ids.extend([inc.get("constellation_id"), inc.get("staging_solar_system_id")])
    resolved_inc = resolve_names(inc_ids)

    inc_rows = []
    for inc in incursions:
        c_name = resolved_inc.get(inc.get("constellation_id"), f"Constellation {inc.get('constellation_id')}")
        s_name = resolved_inc.get(inc.get("staging_solar_system_id"), f"System {inc.get('staging_solar_system_id')}")
        inf = inc.get("influence", 0.0) * 100.0
        state = inc.get("state", "Mobilizing").capitalize()
        boss = "⚔️ Active" if inc.get("has_boss") else "🛡️ Pending"
        inc_rows.append(f"| **{c_name}** | **{s_name}** | `{state}` | `{inf:.1f}%` | {boss} |")

    inc_table = "\n".join(inc_rows) if inc_rows else "*No active Incursions detected across New Eden.*"
    inc_file = os.path.join(output_dir, "incursions_radar.md")
    inc_md = f"""# Sansha Incursion Real-Time Tactical Radar

- **Active Incursion Constellations**: **{len(incursions)}**
- **Last Telemetry Poll**: `{sync_time_str}`

| Target Constellation | Staging Solar System | Invasion State | Sansha Influence | Mothership / Boss |
| :--- | :--- | :--- | :--- | :--- |
{inc_table}
"""
    with open(inc_file, "w", encoding="utf-8") as f:
        f.write(inc_md)
    created_files.append(inc_file)

    # 3. SYSTEM_DANGER_HEATMAP.MD (Top 35 deadliest solar systems in the last 1h)
    kills_data = fetch_system_kills()
    deadliest = sorted(kills_data, key=lambda x: (x.get("ship_kills", 0) + x.get("pod_kills", 0) * 2), reverse=True)[:35]
    sys_ids = [k.get("system_id") or k.get("solar_system_id") for k in deadliest]
    resolved_systems = resolve_names(sys_ids)

    danger_rows = []
    for k in deadliest:
        sid = k.get("system_id") or k.get("solar_system_id")
        s_name = resolved_systems.get(sid, f"System {sid}")
        s_kills = k.get("ship_kills", 0)
        p_kills = k.get("pod_kills", 0)
        npc_kills = k.get("npc_kills", 0)
        threat_tag = "🔴 HIGH DANGER" if (s_kills > 5 or p_kills > 3) else ("🟡 ELEVATED" if s_kills > 0 else "⚪ RATTERY")
        danger_rows.append(f"| **{s_name}** | `{threat_tag}` | **{s_kills}** | **{p_kills}** | {npc_kills:,} |")

    danger_table = "\n".join(danger_rows) if danger_rows else "*No system kills reported in current cycle.*"
    danger_file = os.path.join(output_dir, "system_danger_heatmap.md")
    danger_md = f"""# New Eden Real-Time Solar System Danger Heatmap (Last 60 Minutes)

Live combat telemetry tracking player ship destructions, pod ganks, and NPC ratting volume across all 5,000+ star systems.

| Solar System | Threat Profile | Ship Kills (1h) | Pod Kills (1h) | NPC Rattery Kills (1h) |
| :--- | :--- | :--- | :--- | :--- |
{danger_table}
"""
    with open(danger_file, "w", encoding="utf-8") as f:
        f.write(danger_md)
    created_files.append(danger_file)

    # 4. SYSTEM_TRAFFIC_HEATMAP.MD (Top 35 highest traffic jump gates in the last 1h)
    jumps_data = fetch_system_jumps()
    highest_traffic = sorted(jumps_data, key=lambda x: x.get("ship_jumps", 0), reverse=True)[:35]
    jump_sys_ids = [j.get("system_id") or j.get("solar_system_id") for j in highest_traffic]
    resolved_jumps = resolve_names(jump_sys_ids)

    traffic_rows = []
    for j in highest_traffic:
        sid = j.get("system_id") or j.get("solar_system_id")
        s_name = resolved_jumps.get(sid, f"System {sid}")
        j_count = j.get("ship_jumps", 0)
        density = "⚡ ULTRA CONDUIT" if j_count > 500 else ("🔵 HIGH FLOW" if j_count > 200 else "🟢 MODERATE")
        traffic_rows.append(f"| **{s_name}** | **{j_count:,} jumps** | `{density}` |")

    traffic_table = "\n".join(traffic_rows) if traffic_rows else "*No jump telemetry reported in current cycle.*"
    traffic_file = os.path.join(output_dir, "system_traffic_heatmap.md")
    traffic_md = f"""# New Eden Real-Time Stargate Traffic & Logistics Flow (Last 60 Minutes)

Hourly conduit throughput tracking fleet migrations, trade haulers, and gate activity across New Eden.

| Solar System | Stargate Jumps (1h) | Flow Classification |
| :--- | :--- | :--- |
{traffic_table}
"""
    with open(traffic_file, "w", encoding="utf-8") as f:
        f.write(traffic_md)
    created_files.append(traffic_file)

    # 5. SOVEREIGNTY_CAMPAIGNS.MD (Active Sov Battles & Entosis Timers)
    sov_campaigns = fetch_sovereignty_campaigns()
    sov_ids = []
    for sc in sov_campaigns:
        sov_ids.extend([sc.get("solar_system_id"), sc.get("defender_id")])
    resolved_sov = resolve_names(sov_ids)

    sov_rows = []
    for sc in sov_campaigns[:40]:
        s_name = resolved_sov.get(sc.get("solar_system_id"), f"System {sc.get('solar_system_id')}")
        def_name = resolved_sov.get(sc.get("defender_id"), "Defender")
        ctype = sc.get("event_type", "structure").replace("_", " ").title()
        def_score = sc.get("defender_score", 0.0) * 100.0
        att_score = sc.get("attackers_score", 0.0) * 100.0
        start = sc.get("start_time", "Active")
        sov_rows.append(f"| **{s_name}** | **{ctype}** | **{def_name}** | `{def_score:.0f}% / {att_score:.0f}%` | `{start}` |")

    sov_table = "\n".join(sov_rows) if sov_rows else "*No active sovereignty campaigns in progress.*"
    sov_file = os.path.join(output_dir, "sovereignty_campaigns.md")
    sov_md = f"""# Real-Time Sovereignty War Theater & Entosis Campaigns

Active Territorial Claim Units (TCU), Infrastructure Hubs (I-Hub), and Station Defense/Attack campaign windows.

- **Active Sov Battles**: **{len(sov_campaigns)}**
- **Last Polled**: `{sync_time_str}`

| Target Solar System | Structure Type | Defending Coalition | Control Score (Def/Att) | Entosis Window Open |
| :--- | :--- | :--- | :--- | :--- |
{sov_table}
"""
    with open(sov_file, "w", encoding="utf-8") as f:
        f.write(sov_md)
    created_files.append(sov_file)

    return created_files
