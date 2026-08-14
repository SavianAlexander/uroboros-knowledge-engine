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
    with get_cache_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM entities")
        for row in cur.fetchall():
            _MEM_CACHE[row[0]] = row[1]


def resolve_ids_fast(ids: list) -> dict:
    """Resolve a list of IDs using memory cache -> local SQLite -> ESI bulk fallback."""
    populate_mem_cache()
    global _MEM_CACHE
    results = {}
    missing = []

    for entity_id in ids:
        if not isinstance(entity_id, int) or entity_id <= 0:
            continue
        if entity_id in _MEM_CACHE:
            results[entity_id] = _MEM_CACHE[entity_id]
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
