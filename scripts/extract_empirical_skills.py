"""
Fast Empirical Skill and Character Extractor using bulk ESI /universe/names/ resolution.

Extracts:
1. Exact total SP and list of all skills.
2. Reprocessing, Mining, Industrial, Combat, Science, Leadership skills.
3. Active Ship, Location, Wallet, Clones, Implants.
4. Active Skill Queue.

Ponytail: Zero-dependency stdlib implementation (urllib.request, json, os, sys).
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_sso import token_manager, refresh_access_token

ESI_BASE = "https://esi.evetech.net/latest"


def get_authenticated_esi(endpoint: str, access_token: str):
    url = f"{ESI_BASE}{endpoint}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "Uroboros Knowledge Engine / savianalexander@pm.me"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def resolve_names_bulk(ids: list) -> dict:
    """Resolve up to 1000 IDs to names in a single ESI POST call."""
    if not ids:
        return {}
    unique_ids = list(set([i for i in ids if isinstance(i, int) and i > 0]))
    id_name_map = {}
    
    # Process in chunks of 500
    for chunk_start in range(0, len(unique_ids), 500):
        chunk = unique_ids[chunk_start:chunk_start + 500]
        req = urllib.request.Request(
            f"{ESI_BASE}/universe/names/",
            data=json.dumps(chunk).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Uroboros Knowledge Engine / savianalexander@pm.me"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data:
                    id_name_map[item["id"]] = item["name"]
        except Exception as e:
            print(f"  ⚠️ Warning resolving names chunk: {e}")
            
    return id_name_map


def extract_all_pilots():
    chars = token_manager.list_characters()
    print(f"=================================================================")
    print(f"🌐 EXTRACTING EMPIRICAL ESI DATA FOR {len(chars)} PILOTS...")
    print(f"=================================================================")

    raw_pilot_data = {}
    all_type_ids = set()

    for c in chars:
        cid = c["character_id"]
        cname = c["character_name"]
        try:
            tok = refresh_access_token(cid)
        except Exception as ex:
            print(f"❌ Error refreshing token for {cname}: {ex}")
            continue

        skills = get_authenticated_esi(f"/characters/{cid}/skills/", tok)
        queue = get_authenticated_esi(f"/characters/{cid}/skillqueue/", tok)
        loc = get_authenticated_esi(f"/characters/{cid}/location/", tok)
        ship = get_authenticated_esi(f"/characters/{cid}/ship/", tok)
        wallet = get_authenticated_esi(f"/characters/{cid}/wallet/", tok)
        clones = get_authenticated_esi(f"/characters/{cid}/clones/", tok)

        # Collect IDs for bulk name resolution
        if isinstance(skills, dict):
            for s in skills.get("skills", []):
                all_type_ids.add(s.get("skill_id"))
        if isinstance(queue, list):
            for q in queue:
                all_type_ids.add(q.get("skill_id"))
        if isinstance(ship, dict) and "ship_type_id" in ship:
            all_type_ids.add(ship["ship_type_id"])
        if isinstance(loc, dict) and "solar_system_id" in loc:
            all_type_ids.add(loc["solar_system_id"])

        raw_pilot_data[cname] = {
            "id": cid,
            "skills_raw": skills,
            "queue_raw": queue,
            "loc_raw": loc,
            "ship_raw": ship,
            "wallet_raw": wallet,
            "clones_raw": clones
        }

    print(f"  • Collected {len(all_type_ids)} unique type/system IDs across fleet.")
    print("  • Resolving names via bulk ESI endpoint...")
    name_map = resolve_names_bulk(list(all_type_ids))
    print(f"  • Successfully resolved {len(name_map)} entity names.\n")

    # Now print formatted empirical findings
    empirical_results = {}

    for cname, pdata in raw_pilot_data.items():
        cid = pdata["id"]
        skills_raw = pdata["skills_raw"]
        total_sp = skills_raw.get("total_sp", 0) if isinstance(skills_raw, dict) else 0
        unalloc_sp = skills_raw.get("unallocated_sp", 0) if isinstance(skills_raw, dict) else 0
        wallet = pdata["wallet_raw"]
        ship = pdata["ship_raw"]
        loc = pdata["loc_raw"]
        queue = pdata["queue_raw"]

        ship_name = name_map.get(ship.get("ship_type_id"), f"Type {ship.get('ship_type_id')}") if isinstance(ship, dict) else "Unknown"
        sys_name = name_map.get(loc.get("solar_system_id"), f"System {loc.get('solar_system_id')}") if isinstance(loc, dict) else "Unknown"

        # Build skill map
        skills_list = skills_raw.get("skills", []) if isinstance(skills_raw, dict) else []
        pilot_skill_map = {}
        for s in skills_list:
            s_id = s.get("skill_id")
            s_name = name_map.get(s_id, f"Skill_{s_id}")
            lvl = s.get("active_skill_level", s.get("trained_skill_level", 0))
            sp = s.get("skillpoints_in_skill", 0)
            pilot_skill_map[s_name] = {"level": lvl, "sp": sp, "id": s_id}

        print(f"=================================================================")
        print(f"👤 {cname} (ID: {cid})")
        print(f"=================================================================")
        print(f"  • Total Skillpoints: {total_sp:,} SP (Unallocated: {unalloc_sp:,} SP)")
        print(f"  • Total Skills Trained: {len(pilot_skill_map)}")
        if isinstance(wallet, (int, float)):
            print(f"  • Liquid Wallet: {wallet:,.2f} ISK")
        print(f"  • Active Ship: '{ship.get('ship_name') if isinstance(ship, dict) else 'Ship'}' ({ship_name})")
        print(f"  • Current Solar System: {sys_name}")

        # Search for industry & refining skills
        target_skills = [
            "Reprocessing", "Reprocessing Efficiency", "Scrapmetal Processing",
            "Simple Ore Processing", "Coherent Ore Processing", "Variegated Ore Processing",
            "Complex Ore Processing", "Abundant Ore Processing", "Moon Ore Processing",
            "Ice Processing", "Gas Cloud Harvesting", "Mining", "Mining Barge", "Exhumers",
            "Mining Director", "Industrial Reconfiguration", "Industry", "Advanced Industry",
            "Mass Production", "Advanced Mass Production", "Supply Chain Management",
            "Laboratory Operation", "Advanced Laboratory Operation", "Research", "Metallurgy",
            "Command Center Upgrades", "Interplanetary Consolidation", "Planetology",
            "Marauders", "Black Ops", "Large Energy Turret", "Large Hybrid Turret",
            "Large Projectile Turret", "Transport Ships", "Freighter", "Jump Freighters",
            "Capital Ships", "Caldari Battleship", "Gallente Battleship", "Amarr Battleship",
            "Minmatar Battleship"
        ]

        print("\n  🔍 Key Empirical Skills Trained:")
        found_any = False
        for ts in target_skills:
            if ts in pilot_skill_map:
                info = pilot_skill_map[ts]
                print(f"    ⭐ {ts:<34} : Level {info['level']} ({info['sp']:,} SP)")
                found_any = True
        if not found_any:
            print("    (No advanced industrial/combat specialization trained)")

        # Print Top 8 Skills by SP
        top_skills = sorted(pilot_skill_map.items(), key=lambda x: x[1]["sp"], reverse=True)[:8]
        print("\n  🏆 Top 8 Skills by SP:")
        for s_name, s_info in top_skills:
            print(f"    • {s_name:<34} : Level {s_info['level']} ({s_info['sp']:,} SP)")

        # Print Queue
        if isinstance(queue, list) and len(queue) > 0:
            print(f"\n  ⏳ Active Skill Queue ({len(queue)} items):")
            for idx, qitem in enumerate(queue[:5]):
                qs_name = name_map.get(qitem.get("skill_id"), f"Skill_{qitem.get('skill_id')}")
                print(f"    [{idx+1}] {qs_name} Level {qitem.get('finished_level')} (Finish: {qitem.get('finish_date')})")
        else:
            print("  ⏳ Skill Queue: Inactive / Empty")

        print("")

        empirical_results[cname] = {
            "id": cid,
            "total_sp": total_sp,
            "unallocated_sp": unalloc_sp,
            "wallet_isk": wallet,
            "active_ship": ship_name,
            "ship_custom_name": ship.get("ship_name") if isinstance(ship, dict) else "",
            "system_name": sys_name,
            "skills": pilot_skill_map,
            "queue": [
                {
                    "skill_name": name_map.get(q.get("skill_id")),
                    "level": q.get("finished_level"),
                    "finish_date": q.get("finish_date")
                } for q in (queue if isinstance(queue, list) else [])
            ]
        }

    # Save to empirical audit json
    out_path = os.path.join(BASE_DIR, "vault", "Eve Online", "Fleet", "empirical_esi_audit.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(empirical_results, f, indent=2, default=str)
    print(f"=================================================================")
    print(f"✅ Empirical ESI audit saved to: {out_path}")
    print(f"=================================================================")


if __name__ == "__main__":
    extract_all_pilots()
