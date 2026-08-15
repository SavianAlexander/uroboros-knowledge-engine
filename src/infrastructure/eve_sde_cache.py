"""
Persistent SQLite SDE Cache & Sub-Millisecond Entity Resolver.

Provides ultra-fast local resolution for all New Eden entity IDs (types, solar systems, stations, alliances, corps):
- In-memory LRU dict cache for sub-1ms lookups
- Persistent SQLite table `entities` backing the cache across process restarts
- Automatic bulk ESI fallback for newly discovered IDs

Ponytail: Zero-dependency stdlib implementation (sqlite3, json, os, sys, time, urllib.request).
"""

import os
import sys
import json
import sqlite3
import time
import urllib.request

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
CACHE_DB_PATH = os.path.join(VAULT_EVE_DIR, "sde_cache.sqlite")
ESI_BASE = "https://esi.evetech.net/latest"

_MEM_CACHE = {}


_STATIC_SDE_LOOKUP = {
    # Core Solar Systems & Trade Hubs
    30000142: "Jita",
    30002187: "Amarr",
    30002659: "Dodixie",
    30002510: "Rens",
    30002053: "Hek",
    30004759: "1DQ1-A",
    30000144: "Perimeter",
    30000137: "New Caldari",
    30002700: "Alikvita",
    30002661: "Villore",
    30002188: "Hedion",
    30000001: "Taisy",
    30000180: "Uedama",
    30002768: "Ahbazon",
    30003001: "Tama",
    30003429: "Rancer",
    30000141: "Muvolailen",
    # Factions & Major NPC Entities
    500001: "Caldari State",
    500002: "Minmatar Republic",
    500003: "Amarr Empire",
    500004: "Gallente Federation",
    500010: "Guristas Pirates",
    500011: "Blood Raiders",
    500012: "Angel Cartel",
    500013: "Sansha's Nation",
    500014: "Serpentis",
    500020: "Triglavian Collective",
    500021: "EDENCOM",
    1000002: "Caldari Navy",
    1000084: "CONCORD Police Division",
    # Popular Ships & Mining Vessels
    587: "Rifter",
    621: "Caracal",
    645: "Dominix",
    12005: "Ishtar",
    17918: "Gila",
    28661: "Kronos",
    28659: "Paladin",
    28665: "Vargur",
    28667: "Golem",
    28352: "Rorqual",
    11567: "Hulk",
    12044: "Mackinaw",
    12042: "Skiff",
    17478: "Retriever",
    17476: "Covetor",
    17480: "Procurer",
    29984: "Tengu",
    29986: "Loki",
    29988: "Legion",
    29990: "Proteus",
}


def get_cache_db():
    os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY,
            category TEXT,
            name TEXT,
            updated_at REAL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
    return conn


def populate_mem_cache():
    global _MEM_CACHE
    if _MEM_CACHE:
        return
    # Pre-populate from static SDE dictionary
    _MEM_CACHE.update(_STATIC_SDE_LOOKUP)
    with get_cache_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM entities")
        for row in cur.fetchall():
            _MEM_CACHE[row[0]] = row[1]


def resolve_ids_fast(ids: list) -> dict:
    """Resolve a list of IDs using memory cache -> static SDE -> local SQLite -> ESI bulk fallback."""
    populate_mem_cache()
    global _MEM_CACHE
    results = {}
    missing = []

    for entity_id in ids:
        if not isinstance(entity_id, int) or entity_id <= 0:
            continue
        if entity_id in _MEM_CACHE:
            results[entity_id] = _MEM_CACHE[entity_id]
        elif entity_id in _STATIC_SDE_LOOKUP:
            results[entity_id] = _STATIC_SDE_LOOKUP[entity_id]
            _MEM_CACHE[entity_id] = _STATIC_SDE_LOOKUP[entity_id]
        else:
            missing.append(entity_id)

    if not missing:
        return results

    # Fetch missing from ESI bulk /universe/names/
    unique_missing = list(set(missing))
    newly_resolved = []
    
    for chunk_start in range(0, len(unique_missing), 500):
        chunk = unique_missing[chunk_start:chunk_start + 500]
        req = urllib.request.Request(
            f"{ESI_BASE}/universe/names/",
            data=json.dumps(chunk).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Uroboros Knowledge Engine / savianalexander@pm.me"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data:
                    item_id = item["id"]
                    item_name = item["name"]
                    item_cat = item.get("category", "unknown")
                    results[item_id] = item_name
                    _MEM_CACHE[item_id] = item_name
                    newly_resolved.append((item_id, item_cat, item_name, time.time()))
        except Exception as e:
            # Fallback placeholder
            for mid in chunk:
                if mid not in results:
                    results[mid] = f"Entity_{mid}"

    if newly_resolved:
        with get_cache_db() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO entities (id, category, name, updated_at) VALUES (?, ?, ?, ?)",
                newly_resolved
            )

    return results


def resolve_id_fast(entity_id: int) -> str:
    return resolve_ids_fast([entity_id]).get(entity_id, f"Entity_{entity_id}")
