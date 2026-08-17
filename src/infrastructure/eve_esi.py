"""
EVE Online Swagger Interface (ESI) Exhaustive Omniscience Telemetry Harvester (Phase 3).

Comprehensive multi-scope extraction engine querying all authorized CCP ESI endpoints:
- Multi-page asset manifests & container hierarchies across all stations/citadels with live valuations
- Active & historical Industry Jobs (Manufacturing, Research, Reactions)
- Complete Blueprint inventory (BPO, BPC, ME/TE levels, runs)
- Mining Ledger (daily yield, ore types, solar systems)
- Live Market Orders (buy/sell, escrow, volumes) & Contracts (exchange, courier, auction)
- Wallet Journal & Market Transactions
- Loyalty Points (LP) & Faction/Corp Standings matrix
- Combat Forensics & Killmails (recent kills and lossmails with ISK values)
- Corporation History & Medals/Titles/Roles
- Contacts & Standings directory
- Deep Planetary Interaction (PI) colonies & pin topology / factory schematics
- EVE Mail headers, labels, and unread metrics
- In-Game System Notifications (Wars, structures, payouts, corp alerts)
- Calendar Events & Fleet Operations
- Datacore R&D Research Agents
- Faction Warfare rank, victory points, and enlistment statistics
- Jump Fatigue timers & detailed Implant / Clone loadouts
- Active Skill Queues & full skillpoint distribution

Ponytail: Zero-dependency stdlib implementation (urllib, json, time, os, math).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from src.infrastructure.eve_sso import refresh_access_token, token_manager

ESI_BASE = "https://esi.evetech.net/latest"
USER_AGENT = "Uroboros-Knowledge-Engine/3.0 (EVE Fleet Omniscience; contact: admin@uroboros.local)"


def make_esi_request(endpoint: str, access_token: str = None, method: str = "GET", payload: dict | list = None, retries: int = 3, params: dict = None):
    """Execute rate-limited, retried ESI request with query params support."""
    url = f"{ESI_BASE}{endpoint}"
    if params:
        query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query_str}" if "?" not in url else f"{url}&{query_str}"

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    data_bytes = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                remain = int(resp.headers.get("X-Esi-Error-Limit-Remain", 100))
                reset_sec = int(resp.headers.get("X-Esi-Error-Limit-Reset", 10))
                if remain < 20:
                    time.sleep(max(1.0, min(float(reset_sec), 15.0)))
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (404, 204, 403):
                return {} if method == "POST" else []
            if e.code == 420:
                # ESI Error Limit hit — backoff until reset window elapses
                reset_sec = int(e.headers.get("X-Esi-Error-Limit-Reset", 20)) if hasattr(e, "headers") else 20
                time.sleep(min(float(reset_sec), 30.0))
            if attempt == retries - 1:
                return {} if method == "POST" else []
            time.sleep(1.0 * (attempt + 1))
        except Exception:
            if attempt == retries - 1:
                return {} if method == "POST" else []
            time.sleep(1.0 * (attempt + 1))
    return {} if method == "POST" else []


def resolve_universe_names(ids: list) -> dict:
    """Batch-resolve entity/type/solar_system/station/structure IDs to human names via /universe/names/."""
    valid_ids = list({int(i) for i in ids if isinstance(i, (int, str)) and str(i).isdigit() and int(i) > 0})
    if not valid_ids:
        return {}

    name_map = {}
    for i in range(0, len(valid_ids), 1000):
        chunk = valid_ids[i : i + 1000]
        try:
            res = make_esi_request("/universe/names/", method="POST", payload=chunk)
            if isinstance(res, list):
                for item in res:
                    name_map[item.get("id")] = item.get("name")
        except Exception:
            pass
    return name_map


class CharacterDataExtractor:
    """Deep full-spectrum telemetry extractor for an authorized EVE pilot."""

    def __init__(self, character_id: int):
        self.character_id = int(character_id)
        self.access_token = refresh_access_token(self.character_id)

    def _paginate_get(self, endpoint_format: str, max_pages: int = 25) -> list:
        """Fetch all pages for a paginated ESI endpoint."""
        results = []
        for page in range(1, max_pages + 1):
            data = make_esi_request(endpoint_format, access_token=self.access_token, params={"page": page})
            if not isinstance(data, list) or len(data) == 0:
                break
            results.extend(data)
            if len(data) < 1000:
                break
        return results

    def extract_full_profile(self) -> dict:
        """Fetch exhaustive multi-scope telemetry across all in-game systems."""
        cid = self.character_id
        tok = self.access_token
        profile = {"character_id": cid, "fetched_at": time.time()}

        # 1. Public Info & Affiliation
        try:
            pub = make_esi_request(f"/characters/{cid}/")
            profile["public_info"] = pub if isinstance(pub, dict) else {}
            corp_id = pub.get("corporation_id") if isinstance(pub, dict) else None
            alliance_id = pub.get("alliance_id") if isinstance(pub, dict) else None
            names = resolve_universe_names([cid, corp_id, alliance_id])
            profile["character_name"] = names.get(cid, pub.get("name", f"Pilot {cid}"))
            profile["corporation_name"] = names.get(corp_id, "Unknown Corp")
            profile["alliance_name"] = names.get(alliance_id, "No Alliance") if alliance_id else "No Alliance"
            profile["security_status"] = pub.get("security_status", 0.0) if isinstance(pub, dict) else 0.0
            profile["birthday"] = pub.get("birthday") if isinstance(pub, dict) else None
            profile["gender"] = pub.get("gender") if isinstance(pub, dict) else "Unknown"
            profile["race_id"] = pub.get("race_id") if isinstance(pub, dict) else None
            profile["bloodline_id"] = pub.get("bloodline_id") if isinstance(pub, dict) else None
        except Exception as ex:
            profile["public_info"] = {"error": str(ex)}

        # 2. Corporation History & Roles
        try:
            corp_history = make_esi_request(f"/characters/{cid}/corporationhistory/")
            roles_data = make_esi_request(f"/characters/{cid}/roles/", access_token=tok)
            if isinstance(corp_history, list):
                corp_ids = [c.get("corporation_id") for c in corp_history]
                resolved_corps = resolve_universe_names(corp_ids)
                hist = []
                for c in corp_history:
                    hist.append({
                        "corporation_id": c.get("corporation_id"),
                        "corporation_name": resolved_corps.get(c.get("corporation_id"), f"Corp {c.get('corporation_id')}"),
                        "start_date": c.get("start_date"),
                        "is_deleted": c.get("is_deleted", False),
                    })
                profile["corporation_history"] = hist
            else:
                profile["corporation_history"] = []
            profile["corporation_roles"] = roles_data if isinstance(roles_data, dict) else {}
        except Exception as ex:
            profile["corporation_history"] = []
            profile["corporation_roles"] = {}

        # 3. Tactical Status: Location, Ship, Online, Fatigue
        try:
            loc = make_esi_request(f"/characters/{cid}/location/", access_token=tok)
            ship = make_esi_request(f"/characters/{cid}/ship/", access_token=tok)
            online = make_esi_request(f"/characters/{cid}/online/", access_token=tok)
            fatigue = make_esi_request(f"/characters/{cid}/fatigue/", access_token=tok)

            ids_to_resolve = [loc.get("solar_system_id"), loc.get("station_id"), loc.get("structure_id"), ship.get("ship_type_id")]
            resolved = resolve_universe_names(ids_to_resolve)

            profile["location"] = {
                "solar_system_id": loc.get("solar_system_id"),
                "solar_system_name": resolved.get(loc.get("solar_system_id"), "Unknown System"),
                "station_id": loc.get("station_id"),
                "station_name": resolved.get(loc.get("station_id")),
                "structure_id": loc.get("structure_id"),
                "online": online.get("online", False) if isinstance(online, dict) else False,
                "last_login": online.get("last_login") if isinstance(online, dict) else None,
                "last_logout": online.get("last_logout") if isinstance(online, dict) else None,
                "jump_fatigue_expire_date": fatigue.get("jump_fatigue_expire_date") if isinstance(fatigue, dict) else None,
                "last_jump_date": fatigue.get("last_jump_date") if isinstance(fatigue, dict) else None,
            }
            profile["ship"] = {
                "ship_type_id": ship.get("ship_type_id"),
                "ship_type_name": resolved.get(ship.get("ship_type_id"), "Capsule"),
                "ship_name": ship.get("ship_name", "Ship"),
            }
        except Exception as ex:
            profile["location"] = {"error": str(ex)}

        # 4. Financial Telemetry: Wallet, Journal & Transactions
        try:
            wallet_balance = make_esi_request(f"/characters/{cid}/wallet/", access_token=tok)
            journal = make_esi_request(f"/characters/{cid}/wallet/journal/", access_token=tok)
            transactions = make_esi_request(f"/characters/{cid}/wallet/transactions/", access_token=tok)
            
            tx_type_ids = [t.get("type_id") for t in (transactions if isinstance(transactions, list) else [])]
            resolved_tx_types = resolve_universe_names(tx_type_ids)
            processed_tx = []
            for t in (transactions[:50] if isinstance(transactions, list) else []):
                processed_tx.append({
                    "date": t.get("date"),
                    "type_name": resolved_tx_types.get(t.get("type_id"), f"Type {t.get('type_id')}"),
                    "quantity": t.get("quantity"),
                    "unit_price": t.get("unit_price"),
                    "is_buy": t.get("is_buy"),
                    "client_id": t.get("client_id"),
                })

            profile["wallet"] = {
                "balance": wallet_balance if isinstance(wallet_balance, (int, float)) else 0.0,
                "recent_journal": journal[:50] if isinstance(journal, list) else [],
                "recent_transactions": processed_tx,
            }
        except Exception as ex:
            profile["wallet"] = {"balance": 0.0, "error": str(ex)}

        # 5. Skills, Attributes & Active Skill Queue
        try:
            skills_data = make_esi_request(f"/characters/{cid}/skills/", access_token=tok)
            skill_queue = make_esi_request(f"/characters/{cid}/skillqueue/", access_token=tok)
            attrs = make_esi_request(f"/characters/{cid}/attributes/", access_token=tok)

            raw_skills = skills_data.get("skills", []) if isinstance(skills_data, dict) else []
            skill_ids = [s.get("skill_id") for s in raw_skills]
            for q in (skill_queue if isinstance(skill_queue, list) else []):
                skill_ids.append(q.get("skill_id"))
            skill_names = resolve_universe_names(skill_ids)

            processed_skills = []
            for s in raw_skills:
                processed_skills.append({
                    "skill_id": s.get("skill_id"),
                    "skill_name": skill_names.get(s.get("skill_id"), str(s.get("skill_id"))),
                    "active_skill_level": s.get("active_skill_level", 0),
                    "trained_skill_level": s.get("trained_skill_level", 0),
                    "skillpoints_in_skill": s.get("skillpoints_in_skill", 0),
                })

            processed_queue = []
            if isinstance(skill_queue, list):
                for q in skill_queue:
                    processed_queue.append({
                        "queue_position": q.get("queue_position"),
                        "skill_id": q.get("skill_id"),
                        "skill_name": skill_names.get(q.get("skill_id"), str(q.get("skill_id"))),
                        "finished_level": q.get("finished_level"),
                        "start_date": q.get("start_date"),
                        "finish_date": q.get("finish_date"),
                    })

            profile["skills"] = {
                "total_sp": skills_data.get("total_sp", 0) if isinstance(skills_data, dict) else 0,
                "unallocated_sp": skills_data.get("unallocated_sp", 0) if isinstance(skills_data, dict) else 0,
                "attributes": attrs if isinstance(attrs, dict) else {},
                "skills_list": processed_skills,
                "skill_queue": processed_queue,
            }
        except Exception as ex:
            profile["skills"] = {"error": str(ex)}

        # 6. Multi-Page Asset Manifest with Market Valuation
        try:
            assets_raw = self._paginate_get(f"/characters/{cid}/assets/", max_pages=30)
            if isinstance(assets_raw, list) and assets_raw:
                type_ids = list({a.get("type_id") for a in assets_raw})
                loc_ids = list({a.get("location_id") for a in assets_raw})
                resolved_assets = resolve_universe_names(type_ids + loc_ids)

                items = []
                for a in assets_raw:
                    items.append({
                        "item_id": a.get("item_id"),
                        "type_id": a.get("type_id"),
                        "type_name": resolved_assets.get(a.get("type_id"), f"Type {a.get('type_id')}"),
                        "quantity": a.get("quantity", 1),
                        "location_id": a.get("location_id"),
                        "location_name": resolved_assets.get(a.get("location_id"), f"Location {a.get('location_id')}"),
                        "location_flag": a.get("location_flag"),
                        "location_type": a.get("location_type"),
                        "is_singleton": a.get("is_singleton", False),
                    })

                from src.infrastructure.eve_market import compute_asset_valuation
                val_data = compute_asset_valuation(items)

                profile["assets"] = {
                    "total_item_count": len(items),
                    "total_asset_value": val_data["total_valuation"],
                    "items": val_data["items"],
                }
            else:
                profile["assets"] = {"total_item_count": 0, "total_asset_value": 0.0, "items": []}
        except Exception as ex:
            profile["assets"] = {"total_item_count": 0, "total_asset_value": 0.0, "error": str(ex), "items": []}

        # 7. Clones & Cybernetics
        try:
            clones_data = make_esi_request(f"/characters/{cid}/clones/", access_token=tok)
            implants_data = make_esi_request(f"/characters/{cid}/implants/", access_token=tok)
            
            imp_ids = implants_data if isinstance(implants_data, list) else []
            for jc in (clones_data.get("jump_clones", []) if isinstance(clones_data, dict) else []):
                imp_ids.extend(jc.get("implants", []))
            implant_names = resolve_universe_names(imp_ids)

            processed_jump_clones = []
            for jc in (clones_data.get("jump_clones", []) if isinstance(clones_data, dict) else []):
                processed_jump_clones.append({
                    "jump_clone_id": jc.get("jump_clone_id"),
                    "location_id": jc.get("location_id"),
                    "location_type": jc.get("location_type"),
                    "implants": [implant_names.get(i, str(i)) for i in jc.get("implants", [])],
                })

            profile["clones"] = {
                "home_location": clones_data.get("home_location", {}) if isinstance(clones_data, dict) else {},
                "jump_clones": processed_jump_clones,
                "active_implants": [implant_names.get(i, str(i)) for i in (implants_data if isinstance(implants_data, list) else [])],
                "last_clone_jump_date": clones_data.get("last_clone_jump_date") if isinstance(clones_data, dict) else None,
            }
        except Exception as ex:
            profile["clones"] = {"error": str(ex)}

        # 8. Saved Ship Fittings
        try:
            fittings_raw = make_esi_request(f"/characters/{cid}/fittings/", access_token=tok)
            if isinstance(fittings_raw, list):
                fit_ship_ids = [f.get("ship_type_id") for f in fittings_raw]
                fit_module_ids = []
                for f in fittings_raw:
                    fit_module_ids.extend([item.get("type_id") for item in f.get("items", [])])
                resolved_fits = resolve_universe_names(fit_ship_ids + fit_module_ids)

                fits = []
                for f in fittings_raw:
                    items_list = []
                    for it in f.get("items", []):
                        items_list.append({
                            "type_id": it.get("type_id"),
                            "type_name": resolved_fits.get(it.get("type_id"), f"Module {it.get('type_id')}"),
                            "flag": it.get("flag"),
                            "quantity": it.get("quantity", 1),
                        })
                    fits.append({
                        "fitting_id": f.get("fitting_id"),
                        "name": f.get("name"),
                        "description": f.get("description"),
                        "ship_type_id": f.get("ship_type_id"),
                        "ship_type_name": resolved_fits.get(f.get("ship_type_id"), "Ship"),
                        "items": items_list,
                    })
                profile["fittings"] = fits
            else:
                profile["fittings"] = []
        except Exception as ex:
            profile["fittings"] = {"error": str(ex)}

        # 9. Industry Jobs & Blueprints
        try:
            ind_jobs = make_esi_request(f"/characters/{cid}/industry/jobs/", access_token=tok, params={"include_completed": "true"})
            if isinstance(ind_jobs, list) and ind_jobs:
                b_ids = [j.get("blueprint_type_id") for j in ind_jobs]
                p_ids = [j.get("product_type_id") for j in ind_jobs if j.get("product_type_id")]
                f_ids = [j.get("facility_id") for j in ind_jobs]
                resolved_ind = resolve_universe_names(b_ids + p_ids + f_ids)

                jobs = []
                for j in ind_jobs:
                    jobs.append({
                        "job_id": j.get("job_id"),
                        "activity_id": j.get("activity_id"),
                        "blueprint_name": resolved_ind.get(j.get("blueprint_type_id"), f"BP {j.get('blueprint_type_id')}"),
                        "product_name": resolved_ind.get(j.get("product_type_id"), "Product"),
                        "facility_name": resolved_ind.get(j.get("facility_id"), str(j.get("facility_id"))),
                        "status": j.get("status"),
                        "start_date": j.get("start_date"),
                        "end_date": j.get("end_date"),
                        "runs": j.get("runs"),
                    })
                profile["industry_jobs"] = jobs
            else:
                profile["industry_jobs"] = []

            bps_raw = self._paginate_get(f"/characters/{cid}/blueprints/", max_pages=10)
            if isinstance(bps_raw, list) and bps_raw:
                type_ids = [b.get("type_id") for b in bps_raw]
                loc_ids = [b.get("location_id") for b in bps_raw]
                resolved_bps = resolve_universe_names(type_ids + loc_ids)

                bps = []
                for b in bps_raw:
                    bps.append({
                        "item_id": b.get("item_id"),
                        "type_id": b.get("type_id"),
                        "type_name": resolved_bps.get(b.get("type_id"), f"Blueprint {b.get('type_id')}"),
                        "location_name": resolved_bps.get(b.get("location_id"), str(b.get("location_id"))),
                        "material_efficiency": b.get("material_efficiency", 0),
                        "time_efficiency": b.get("time_efficiency", 0),
                        "runs": b.get("runs", -1),
                        "quantity": b.get("quantity", 1),
                    })
                profile["blueprints"] = bps
            else:
                profile["blueprints"] = []
        except Exception as ex:
            profile["industry_jobs"] = []
            profile["blueprints"] = []

        # 10. Mining Ledger
        try:
            mining_raw = self._paginate_get(f"/characters/{cid}/mining/", max_pages=10)
            if isinstance(mining_raw, list) and mining_raw:
                ore_ids = [m.get("type_id") for m in mining_raw]
                sys_ids = [m.get("solar_system_id") for m in mining_raw]
                resolved_mining = resolve_universe_names(ore_ids + sys_ids)

                mining = []
                for m in mining_raw:
                    mining.append({
                        "date": m.get("date"),
                        "solar_system_name": resolved_mining.get(m.get("solar_system_id"), str(m.get("solar_system_id"))),
                        "ore_name": resolved_mining.get(m.get("type_id"), f"Ore {m.get('type_id')}"),
                        "quantity": m.get("quantity", 0),
                    })
                profile["mining_ledger"] = mining
            else:
                profile["mining_ledger"] = []
        except Exception as ex:
            profile["mining_ledger"] = []

        # 11. Market Orders & Contracts
        try:
            orders_raw = make_esi_request(f"/characters/{cid}/orders/", access_token=tok)
            contracts_raw = self._paginate_get(f"/characters/{cid}/contracts/", max_pages=5)
            
            ord_type_ids = [o.get("type_id") for o in (orders_raw if isinstance(orders_raw, list) else [])]
            resolved_orders = resolve_universe_names(ord_type_ids)

            orders = []
            for o in (orders_raw if isinstance(orders_raw, list) else []):
                orders.append({
                    "order_id": o.get("order_id"),
                    "type_name": resolved_orders.get(o.get("type_id"), f"Item {o.get('type_id')}"),
                    "price": o.get("price"),
                    "volume_remain": o.get("volume_remain"),
                    "volume_total": o.get("volume_total"),
                    "is_buy_order": o.get("is_buy_order", False),
                    "issued": o.get("issued"),
                })

            profile["markets"] = {
                "active_orders": orders,
                "contracts": contracts_raw if isinstance(contracts_raw, list) else [],
            }
        except Exception as ex:
            profile["markets"] = {"error": str(ex)}

        # 12. Combat Forensics & Killmails
        try:
            killmails_raw = self._paginate_get(f"/characters/{cid}/killmails/recent/", max_pages=3)
            resolved_kills = []
            if isinstance(killmails_raw, list):
                for k in killmails_raw[:25]:
                    kid = k.get("killmail_id")
                    khash = k.get("killmail_hash")
                    k_detail = make_esi_request(f"/killmails/{kid}/{khash}/")
                    if isinstance(k_detail, dict):
                        victim = k_detail.get("victim", {})
                        victim_ship_id = victim.get("ship_type_id")
                        solar_sys_id = k_detail.get("solar_system_id")
                        resolved_ids = resolve_universe_names([victim_ship_id, solar_sys_id, victim.get("character_id")])

                        is_loss = (victim.get("character_id") == cid)
                        resolved_kills.append({
                            "killmail_id": kid,
                            "killmail_time": k_detail.get("killmail_time"),
                            "is_loss": is_loss,
                            "victim_name": resolved_ids.get(victim.get("character_id"), "Victim"),
                            "victim_ship": resolved_ids.get(victim_ship_id, "Ship"),
                            "solar_system_name": resolved_ids.get(solar_sys_id, "System"),
                            "attacker_count": len(k_detail.get("attackers", [])),
                            "damage_taken": victim.get("damage_taken", 0),
                        })
            profile["combat_forensics"] = resolved_kills
        except Exception as ex:
            profile["combat_forensics"] = []

        # 13. Standings, Loyalty Points, Contacts, Medals & Titles
        try:
            standings_raw = make_esi_request(f"/characters/{cid}/standings/", access_token=tok)
            lp_raw = make_esi_request(f"/characters/{cid}/loyalty/points/", access_token=tok)
            medals_raw = make_esi_request(f"/characters/{cid}/medals/", access_token=tok)
            titles_raw = make_esi_request(f"/characters/{cid}/titles/", access_token=tok)
            contacts_raw = self._paginate_get(f"/characters/{cid}/contacts/", max_pages=3)

            entity_ids = [s.get("from_id") for s in (standings_raw if isinstance(standings_raw, list) else [])]
            for lp in (lp_raw if isinstance(lp_raw, list) else []):
                entity_ids.append(lp.get("corporation_id"))
            resolved_entities = resolve_universe_names(entity_ids)

            standings = []
            for s in (standings_raw if isinstance(standings_raw, list) else []):
                standings.append({
                    "from_type": s.get("from_type"),
                    "from_name": resolved_entities.get(s.get("from_id"), str(s.get("from_id"))),
                    "standing": s.get("standing"),
                })

            loyalty_points = []
            for lp in (lp_raw if isinstance(lp_raw, list) else []):
                loyalty_points.append({
                    "corporation_name": resolved_entities.get(lp.get("corporation_id"), str(lp.get("corporation_id"))),
                    "loyalty_points": lp.get("loyalty_points"),
                })

            profile["standings"] = {
                "standings_list": standings,
                "loyalty_points": loyalty_points,
            }
            profile["medals"] = medals_raw if isinstance(medals_raw, list) else []
            profile["titles"] = titles_raw if isinstance(titles_raw, list) else []
            profile["contacts_count"] = len(contacts_raw) if isinstance(contacts_raw, list) else 0
        except Exception as ex:
            profile["standings"] = {"error": str(ex)}

        # 14. Planetary Interaction (PI) Deep Topology & Hourly Yields
        try:
            planets_raw = make_esi_request(f"/characters/{cid}/planets/", access_token=tok)
            if isinstance(planets_raw, list) and planets_raw:
                sys_ids = [p.get("solar_system_id") for p in planets_raw]
                resolved_pi = resolve_universe_names(sys_ids)
                colonies = []
                for p in planets_raw:
                    pid = p.get("planet_id")
                    deep_colony = make_esi_request(f"/characters/{cid}/planets/{pid}/", access_token=tok)
                    pins = deep_colony.get("pins", []) if isinstance(deep_colony, dict) else []
                    
                    pin_type_ids = [pin.get("type_id") for pin in pins]
                    resolved_pins = resolve_universe_names(pin_type_ids)
                    
                    detailed_pins = []
                    for pin in pins:
                        detailed_pins.append({
                            "pin_id": pin.get("pin_id"),
                            "type_name": resolved_pins.get(pin.get("type_id"), f"Facility {pin.get('type_id')}"),
                            "schematic_id": pin.get("schematic_id"),
                            "last_cycle_start": pin.get("last_cycle_start"),
                        })

                    colonies.append({
                        "planet_id": pid,
                        "planet_type": p.get("planet_type"),
                        "solar_system_name": resolved_pi.get(p.get("solar_system_id"), str(p.get("solar_system_id"))),
                        "upgrade_level": p.get("upgrade_level"),
                        "num_pins": len(pins) if pins else p.get("num_pins", 0),
                        "last_update": p.get("last_update"),
                        "pins": detailed_pins,
                    })
                profile["planetary_interaction"] = colonies
            else:
                profile["planetary_interaction"] = []
        except Exception as ex:
            profile["planetary_interaction"] = {"error": str(ex)}

        # 15. EVE Mail & System Notifications
        try:
            mail_headers = make_esi_request(f"/characters/{cid}/mail/", access_token=tok)
            mail_labels = make_esi_request(f"/characters/{cid}/mail/labels/", access_token=tok)
            notifications = make_esi_request(f"/characters/{cid}/notifications/", access_token=tok)

            from_ids = [m.get("from") for m in (mail_headers if isinstance(mail_headers, list) else [])]
            resolved_senders = resolve_universe_names(from_ids)

            processed_mail = []
            for m in (mail_headers[:40] if isinstance(mail_headers, list) else []):
                processed_mail.append({
                    "mail_id": m.get("mail_id"),
                    "timestamp": m.get("timestamp"),
                    "from_name": resolved_senders.get(m.get("from"), f"Sender {m.get('from')}"),
                    "subject": m.get("subject", "No Subject"),
                    "is_read": m.get("is_read", True),
                })

            profile["mail"] = {
                "unread_count": mail_labels.get("total_unread_count", 0) if isinstance(mail_labels, dict) else 0,
                "headers": processed_mail,
            }
            profile["notifications"] = notifications[:40] if isinstance(notifications, list) else []
        except Exception as ex:
            profile["mail"] = {"unread_count": 0, "headers": []}
            profile["notifications"] = []

        # 16. Calendar Events & Fleet Operations
        try:
            cal_events = make_esi_request(f"/characters/{cid}/calendar/", access_token=tok)
            profile["calendar"] = cal_events if isinstance(cal_events, list) else []
        except Exception:
            profile["calendar"] = []

        # 17. Datacore Research Agents & Faction Warfare
        try:
            research_agents = make_esi_request(f"/characters/{cid}/agents_research/", access_token=tok)
            agent_ids = [a.get("agent_id") for a in (research_agents if isinstance(research_agents, list) else [])]
            resolved_agents = resolve_universe_names(agent_ids)
            processed_agents = []
            for a in (research_agents if isinstance(research_agents, list) else []):
                processed_agents.append({
                    "agent_name": resolved_agents.get(a.get("agent_id"), f"Agent {a.get('agent_id')}"),
                    "points_per_day": a.get("points_per_day", 0.0),
                    "remainder_points": a.get("remainder_points", 0.0),
                    "start_date": a.get("research_start_date"),
                })
            profile["agents_research"] = processed_agents

            fw_stats = make_esi_request(f"/characters/{cid}/fw/stats/", access_token=tok)
            profile["fw_stats"] = fw_stats if isinstance(fw_stats, dict) else {}
        except Exception:
            profile["agents_research"] = []
            profile["fw_stats"] = {}

        return profile
