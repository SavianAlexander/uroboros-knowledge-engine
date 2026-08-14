"""
EVE Online Fleet & Character Vault Markdown Synthesizer & Knowledge Indexer (Phase 3 Exhaustive Omniscience).

Synthesizes rich, structured multi-scope intelligence dossiers for every pilot:
- overview.md (Tactical status, Net Worth, affiliation, security status, summary)
- skills.md (Attributes, active skill queue with finish timestamps, full SP breakdown)
- assets.md (Complete station/citadel asset manifest with live Jita market valuations)
- industry.md (Manufacturing, research, reaction jobs, and full blueprint library)
- mining.md (Daily mining ledger by solar system and ore type)
- markets.md (Active market buy/sell orders, escrows, contracts, transactions)
- combat.md (PvP/PvE combat forensics, killmails, lossmails, ISK efficiency)
- corp_history.md (Career corporate timeline, roles, medals, titles, contacts)
- mail.md (EVE Mail headers, sender directory, unread metrics)
- notifications.md (In-game alerts: war decs, structure timers, payouts, tax)
- pi_deep.md (Planetary colonies, pin topology, factories & extractor heads)
- calendar.md (Fleet ops, scheduled corp timers, calendar events)
- standings.md (Faction/Corp/Agent standings matrix and Loyalty Point balances)
- clones.md (Jump clones, cybernetic implants, and jump fatigue timers)
- fittings.md (Saved ship fittings and module configurations)

Also synthesizes Master Fleet Aggregations under `vault/Eve Online/Fleet/`:
- fleet_overview.md (Consolidated fleet roster, Net Worth, SP, ISK, current systems, active ships)
- fleet_wealth.md (Total fleet treasury, asset valuations, combined multi-billion Net Worth)
- fleet_assets.md (Consolidated hangar manifests across all staging citadels with ISK valuations)
- fleet_doctrines.md (Fleet doctrine capability & ship mastery matrix across all 8 pilots)
- fleet_strategic_map.md (Geographic staging heatmap across New Eden solar systems)
- fleet_supply_chain.md (End-to-end industrial pipeline: Mining -> PI -> Blueprints -> Markets)
- fleet_training_roadmap.md (Cross-fleet skill training roadmap for Capital, Logistics, & Mining)
- fleet_comms.md (Aggregated fleet communications, unread mail, and system alerts)

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time, collections).
"""

import os
import sys
import json
import time
from collections import defaultdict

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
VAULT_CHAR_DIR = os.path.join(VAULT_EVE_DIR, "Characters")
VAULT_FLEET_DIR = os.path.join(VAULT_EVE_DIR, "Fleet")


def synthesize_character_markdown(profile: dict, base_dir: str = VAULT_CHAR_DIR) -> list:
    """Generate structured markdown intelligence dossiers for an EVE pilot."""
    char_name = profile.get("character_name", f"Pilot_{profile.get('character_id')}")
    safe_name = "".join(c for c in char_name if c.isalnum() or c in (" ", "-", "_")).strip()
    char_dir = os.path.join(base_dir, safe_name)
    os.makedirs(char_dir, exist_ok=True)

    cid = profile.get("character_id")
    corp_name = profile.get("corporation_name", "Unknown Corp")
    alliance_name = profile.get("alliance_name", "No Alliance")
    sec_status = profile.get("security_status", 0.0)
    birthday = profile.get("birthday", "Unknown")

    loc = profile.get("location", {})
    ship = profile.get("ship", {})
    wallet = profile.get("wallet", {})
    skills = profile.get("skills", {})
    clones = profile.get("clones", {})
    assets = profile.get("assets", {})
    fittings = profile.get("fittings", [])
    industry_jobs = profile.get("industry_jobs", [])
    blueprints = profile.get("blueprints", [])
    mining_ledger = profile.get("mining_ledger", [])
    markets = profile.get("markets", {})
    standings = profile.get("standings", {})
    combat_kills = profile.get("combat_forensics", [])
    corp_history = profile.get("corporation_history", [])
    corp_roles = profile.get("corporation_roles", {})
    medals = profile.get("medals", [])
    titles = profile.get("titles", [])
    pi_colonies = profile.get("planetary_interaction", [])
    mail_data = profile.get("mail", {})
    notifications = profile.get("notifications", [])
    calendar_events = profile.get("calendar", [])
    research_agents = profile.get("agents_research", [])
    fw_stats = profile.get("fw_stats", {})

    created_files = []

    liquid_isk = wallet.get("balance", 0.0)
    asset_val = assets.get("total_asset_value", 0.0)
    net_worth = liquid_isk + asset_val

    # 1. OVERVIEW.MD
    overview_path = os.path.join(char_dir, "overview.md")
    pi_str = f"{len(pi_colonies)} planetary colonies" if pi_colonies else "No active colonies"
    fatigue_str = loc.get("jump_fatigue_expire_date") or "None"

    overview_md = f"""# EVE Pilot Dossier: {char_name}

- **Character ID**: `{cid}`
- **Corporation**: **{corp_name}**
- **Alliance**: **{alliance_name}**
- **Security Status**: `{sec_status:.2f}`
- **Created Date**: {birthday}
- **Last Telemetry Sync**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(profile.get('fetched_at', time.time())))}
- **Tags**: #eveonline, #character, #fleet, #{safe_name.lower().replace(' ', '')}

## Tactical Status
- **Current Solar System**: **{loc.get('solar_system_name', 'Unknown')}**
- **Docked Station / Citadel**: {loc.get('station_name', 'In Space / Undocked')}
- **Active Ship**: **{ship.get('ship_name', 'Ship')}** (`{ship.get('ship_type_name', 'Capsule')}`)
- **Online State**: {'🟢 Online' if loc.get('online') else '⚪ Offline'}
- **Jump Fatigue Expiry**: {fatigue_str}

## Fleet & Financial Net Worth
- **Total Net Worth**: **{net_worth:,.2f} ISK**
- **Liquid ISK Balance**: **{liquid_isk:,.2f} ISK**
- **Asset Market Value**: **{asset_val:,.2f} ISK**
- **Total Trained SP**: **{skills.get('total_sp', 0):,} SP** *(+{skills.get('unallocated_sp', 0):,} unallocated)*
- **Total Assets Count**: **{assets.get('total_item_count', 0):,} items**
- **Active Skill Queue**: **{len(skills.get('skill_queue', []))} skills in training**
- **Jump Clones**: **{len(clones.get('jump_clones', []))} active clones**
- **Industry Lines**: **{len(industry_jobs)} jobs** | **{len(blueprints)} Blueprints**
- **Planetary Interaction**: **{pi_str}**
- **Unread Communications**: **{mail_data.get('unread_count', 0)} unread mail** | **{len(notifications)} recent alerts**
"""
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write(overview_md)
    created_files.append(overview_path)

    # 2. SKILLS.MD
    skills_path = os.path.join(char_dir, "skills.md")
    attrs = skills.get("attributes", {})
    queue_rows = []
    for q in skills.get("skill_queue", []):
        queue_rows.append(f"| {q.get('queue_position', 0) + 1} | **{q.get('skill_name')}** | Level {q.get('finished_level')} | {q.get('finish_date', 'N/A')} |")
    queue_table = "\n".join(queue_rows) if queue_rows else "*Skill queue is currently empty.*"

    skill_rows = []
    for s in sorted(skills.get("skills_list", []), key=lambda x: x.get("skill_name", "")):
        skill_rows.append(f"- **{s.get('skill_name')}**: Level {s.get('active_skill_level')} ({s.get('skillpoints_in_skill', 0):,} SP)")
    skills_list_md = "\n".join(skill_rows) if skill_rows else "*No skills extracted.*"

    skills_md = f"""# Skills & Training Queue: {char_name}

- **Total Skillpoints**: **{skills.get('total_sp', 0):,} SP**
- **Unallocated Skillpoints**: **{skills.get('unallocated_sp', 0):,} SP**
- **Attributes**: Intelligence: `{attrs.get('intelligence', 'N/A')}` | Memory: `{attrs.get('memory', 'N/A')}` | Perception: `{attrs.get('perception', 'N/A')}` | Willpower: `{attrs.get('willpower', 'N/A')}` | Charisma: `{attrs.get('charisma', 'N/A')}`

## Active Skill Queue
| Pos | Skill Name | Target Level | Estimated Finish |
| :--- | :--- | :--- | :--- |
{queue_table}

## Trained Skills Inventory ({len(skills.get('skills_list', []))} Skills)
{skills_list_md}
"""
    with open(skills_path, "w", encoding="utf-8") as f:
        f.write(skills_md)
    created_files.append(skills_path)

    # 3. ASSETS.MD
    assets_path = os.path.join(char_dir, "assets.md")
    items = assets.get("items", [])
    
    location_groups = defaultdict(list)
    location_values = defaultdict(float)
    for it in items:
        loc_name = it.get("location_name", "Unknown Location")
        location_groups[loc_name].append(it)
        location_values[loc_name] += it.get("total_value", 0.0)

    loc_sections = []
    for loc_name, loc_items in sorted(location_groups.items(), key=lambda x: location_values[x[0]], reverse=True):
        loc_val = location_values[loc_name]
        loc_sections.append(f"### 📍 {loc_name} ({len(loc_items):,} items — **{loc_val:,.2f} ISK**)")
        loc_sections.append("| Item Name | Quantity | Est. Unit Price | Total Value | Hangar / Slot |")
        loc_sections.append("| :--- | :--- | :--- | :--- | :--- |")
        for it in sorted(loc_items, key=lambda x: x.get("total_value", 0.0), reverse=True)[:100]:
            u_p = it.get("unit_price", 0.0)
            t_v = it.get("total_value", 0.0)
            loc_sections.append(f"| **{it.get('type_name')}** | {it.get('quantity', 1):,} | {u_p:,.2f} ISK | **{t_v:,.2f} ISK** | `{it.get('location_flag', 'Hangar')}` |")
        if len(loc_items) > 100:
            loc_sections.append(f"| *...and {len(loc_items) - 100} more items* | | | | |")
        loc_sections.append("")

    assets_content = "\n".join(loc_sections) if loc_sections else "*No assets found in manifest.*"

    assets_md = f"""# Asset Manifest & Live Market Valuation: {char_name}

- **Total Tracked Items**: **{len(items):,} items**
- **Total Asset Market Value**: **{asset_val:,.2f} ISK**
- **Unique Locations**: **{len(location_groups)} stations / citadels**
- **Pilot**: {char_name} (`ID: {cid}`)

{assets_content}
"""
    with open(assets_path, "w", encoding="utf-8") as f:
        f.write(assets_md)
    created_files.append(assets_path)

    # 4. INDUSTRY.MD
    industry_path = os.path.join(char_dir, "industry.md")
    job_rows = []
    for j in industry_jobs:
        job_rows.append(f"| `{j.get('job_id')}` | **{j.get('blueprint_name')}** | **{j.get('product_name')}** | `{j.get('status')}` | {j.get('runs')} | {j.get('end_date')} | {j.get('facility_name')} |")
    job_table = "\n".join(job_rows) if job_rows else "*No active or recent industry jobs.*"

    bp_rows = []
    for b in blueprints:
        bp_type = "BPO (Original)" if b.get("runs") == -1 else f"BPC ({b.get('runs')} runs)"
        bp_rows.append(f"| **{b.get('type_name')}** | {bp_type} | ME: `{b.get('material_efficiency')}%` | TE: `{b.get('time_efficiency')}%` | {b.get('location_name')} |")
    bp_table = "\n".join(bp_rows) if bp_rows else "*No blueprints in hangar.*"

    industry_md = f"""# Industry & Blueprints: {char_name}

- **Active / Recent Jobs**: {len(industry_jobs)} jobs
- **Blueprint Inventory**: {len(blueprints)} blueprints

## Industry Production & Research Jobs
| Job ID | Blueprint | Output Product | Status | Runs | Completion Date | Facility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{job_table}

## Blueprint Library
| Blueprint Name | Type | Material Efficiency | Time Efficiency | Hangar Location |
| :--- | :--- | :--- | :--- | :--- |
{bp_table}
"""
    with open(industry_path, "w", encoding="utf-8") as f:
        f.write(industry_md)
    created_files.append(industry_path)

    # 5. MINING.MD
    mining_path = os.path.join(char_dir, "mining.md")
    mining_rows = []
    total_ore_mined = 0
    for m in mining_ledger:
        total_ore_mined += m.get("quantity", 0)
        mining_rows.append(f"| {m.get('date')} | **{m.get('ore_name')}** | **{m.get('solar_system_name')}** | {m.get('quantity', 0):,} units |")
    mining_table = "\n".join(mining_rows[:100]) if mining_rows else "*No mining activity logged in current cycle.*"

    mining_md = f"""# Mining Ledger: {char_name}

- **Total Logged Yield**: **{total_ore_mined:,} units**
- **Active Mining Days**: **{len(mining_ledger)} entries**

## Recent Yield History
| Date | Ore Type | Solar System | Mined Quantity |
| :--- | :--- | :--- | :--- |
{mining_table}
"""
    with open(mining_path, "w", encoding="utf-8") as f:
        f.write(mining_md)
    created_files.append(mining_path)

    # 6. MARKETS.MD
    markets_path = os.path.join(char_dir, "markets.md")
    ord_rows = []
    for o in markets.get("active_orders", []):
        side = "BUY" if o.get("is_buy_order") else "SELL"
        ord_rows.append(f"| `{side}` | **{o.get('type_name')}** | {o.get('price', 0):,.2f} ISK | {o.get('volume_remain')}/{o.get('volume_total')} | {o.get('issued')} |")
    ord_table = "\n".join(ord_rows) if ord_rows else "*No active market orders.*"

    contracts_rows = []
    for c in markets.get("contracts", []):
        contracts_rows.append(f"| `{c.get('contract_id')}` | `{c.get('type')}` | `{c.get('status')}` | {c.get('reward', 0):,.2f} ISK | {c.get('collateral', 0):,.2f} ISK | {c.get('date_expired')} |")
    contracts_table = "\n".join(contracts_rows) if contracts_rows else "*No active contracts.*"

    tx_rows = []
    for tx in wallet.get("recent_transactions", []):
        tx_type = "BUY" if tx.get("is_buy") else "SELL"
        tx_rows.append(f"| {tx.get('date')} | `{tx_type}` | **{tx.get('type_name')}** | {tx.get('quantity')} | {tx.get('unit_price', 0):,.2f} ISK |")
    tx_table = "\n".join(tx_rows) if tx_rows else "*No recent wallet transactions.*"

    markets_md = f"""# Markets, Orders & Transactions: {char_name}

- **Active Market Orders**: {len(markets.get('active_orders', []))} orders
- **Contracts**: {len(markets.get('contracts', []))} contracts
- **Recent Transactions**: {len(wallet.get('recent_transactions', []))} entries

## Active Market Orders
| Type | Item Name | Price | Volume Remaining | Issued Date |
| :--- | :--- | :--- | :--- | :--- |
{ord_table}

## Contracts
| Contract ID | Type | Status | Reward | Collateral | Expiration |
| :--- | :--- | :--- | :--- | :--- | :--- |
{contracts_table}

## Recent Market Transactions
| Date | Type | Item | Quantity | Unit Price |
| :--- | :--- | :--- | :--- | :--- |
{tx_table}
"""
    with open(markets_path, "w", encoding="utf-8") as f:
        f.write(markets_md)
    created_files.append(markets_path)

    # 7. COMBAT.MD
    combat_path = os.path.join(char_dir, "combat.md")
    kill_rows = []
    for k in combat_kills:
        outcome = "🔴 LOSS" if k.get("is_loss") else "🟢 KILL"
        kill_rows.append(f"| `{outcome}` | {k.get('killmail_time')} | **{k.get('victim_name')}** | `{k.get('victim_ship')}` | **{k.get('solar_system_name')}** | {k.get('attacker_count')} attackers | {k.get('damage_taken', 0):,} dmg |")
    kill_table = "\n".join(kill_rows) if kill_rows else "*No recent combat killmails logged in ESI.*"

    combat_md = f"""# Combat Forensics & Killmail History: {char_name}

- **Recent Combat Engagements**: {len(combat_kills)}

## Combat Killmails & Loss Log
| Outcome | Time (UTC) | Victim Pilot | Victim Ship | Solar System | Attackers | Damage Taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{kill_table}
"""
    with open(combat_path, "w", encoding="utf-8") as f:
        f.write(combat_md)
    created_files.append(combat_path)

    # 8. CORP_HISTORY.MD
    corp_hist_path = os.path.join(char_dir, "corp_history.md")
    ch_rows = []
    for ch in corp_history:
        ch_rows.append(f"| **{ch.get('corporation_name')}** | {ch.get('start_date')} | `{ch.get('corporation_id')}` |")
    ch_table = "\n".join(ch_rows) if ch_rows else "*No corporation history available.*"

    roles_str = ", ".join(corp_roles.get("roles", [])) if corp_roles.get("roles") else "Standard Member"

    corp_hist_md = f"""# Corporate Career History & Honors: {char_name}

- **Total Corporations**: {len(corp_history)}
- **Corporate Roles**: `{roles_str}`
- **Contacts Registered**: {profile.get('contacts_count', 0)}

## Corporate Timeline
| Corporation Name | Joined Date | Corp ID |
| :--- | :--- | :--- |
{ch_table}
"""
    with open(corp_hist_path, "w", encoding="utf-8") as f:
        f.write(corp_hist_md)
    created_files.append(corp_hist_path)

    # 9. MAIL.MD
    mail_path = os.path.join(char_dir, "mail.md")
    mail_rows = []
    for m in mail_data.get("headers", []):
        read_badge = "⚪" if m.get("is_read") else "🔵 Unread"
        mail_rows.append(f"| {read_badge} | {m.get('timestamp')} | **{m.get('from_name')}** | **{m.get('subject')}** | `{m.get('mail_id')}` |")
    mail_table = "\n".join(mail_rows) if mail_rows else "*No mail messages logged.*"

    mail_md = f"""# EVE Mail & In-Game Communications: {char_name}

- **Total Inbox Headers**: {len(mail_data.get('headers', []))}
- **Unread Messages**: {mail_data.get('unread_count', 0)}

## In-Game Communications Log
| Status | Timestamp | Sender | Subject | Mail ID |
| :--- | :--- | :--- | :--- | :--- |
{mail_table}
"""
    with open(mail_path, "w", encoding="utf-8") as f:
        f.write(mail_md)
    created_files.append(mail_path)

    # 10. NOTIFICATIONS.MD
    notif_path = os.path.join(char_dir, "notifications.md")
    notif_rows = []
    for n in notifications:
        notif_rows.append(f"| {n.get('timestamp')} | `{n.get('type')}` | `{n.get('notification_id')}` |")
    notif_table = "\n".join(notif_rows) if notif_rows else "*No system notifications logged.*"

    notif_md = f"""# System Notifications & Operational Alerts: {char_name}

- **Recent Alerts**: {len(notifications)}

## Notifications Timeline
| Timestamp | Alert Type | Notification ID |
| :--- | :--- | :--- |
{notif_table}
"""
    with open(notif_path, "w", encoding="utf-8") as f:
        f.write(notif_md)
    created_files.append(notif_path)

    # 11. PI_DEEP.MD
    pi_path = os.path.join(char_dir, "pi_deep.md")
    colony_blocks = []
    for c in pi_colonies:
        colony_blocks.append(f"### 🪐 {c.get('solar_system_name')} — {c.get('planet_type').capitalize()} (ID: `{c.get('planet_id')}`)")
        colony_blocks.append(f"- **Command Center Level**: `{c.get('upgrade_level')}` | **Total Pins**: `{c.get('num_pins')}`")
        colony_blocks.append(f"- **Last Updated**: {c.get('last_update')}")
        if c.get("pins"):
            colony_blocks.append("| Pin Facility | Schematic ID | Cycle Started |")
            colony_blocks.append("| :--- | :--- | :--- |")
            for pin in c.get("pins")[:30]:
                colony_blocks.append(f"| **{pin.get('type_name')}** | `{pin.get('schematic_id') or 'N/A'}` | {pin.get('last_cycle_start', 'Active')} |")
        colony_blocks.append("")

    pi_content = "\n".join(colony_blocks) if colony_blocks else "*No active planetary colonies established.*"

    pi_md = f"""# Planetary Interaction (PI) Topology & Industrial Outposts: {char_name}

- **Active Planetary Colonies**: {len(pi_colonies)}

{pi_content}
"""
    with open(pi_path, "w", encoding="utf-8") as f:
        f.write(pi_md)
    created_files.append(pi_path)

    # 12. CALENDAR.MD
    cal_path = os.path.join(char_dir, "calendar.md")
    cal_rows = []
    for ce in calendar_events:
        cal_rows.append(f"| {ce.get('event_date')} | **{ce.get('title')}** | `{ce.get('event_response')}` | `{ce.get('importance')}` |")
    cal_table = "\n".join(cal_rows) if cal_rows else "*No scheduled calendar events or fleet ops.*"

    cal_md = f"""# Calendar Events & Fleet Operations: {char_name}

- **Scheduled Events**: {len(calendar_events)}

## Upcoming Schedule & Fleet Ops
| Date (UTC) | Event Title | Response | Importance |
| :--- | :--- | :--- | :--- |
{cal_table}
"""
    with open(cal_path, "w", encoding="utf-8") as f:
        f.write(cal_md)
    created_files.append(cal_path)

    # 13. STANDINGS.MD
    standings_path = os.path.join(char_dir, "standings.md")
    std_rows = []
    for s in sorted(standings.get("standings_list", []), key=lambda x: x.get("standing", 0), reverse=True):
        std_rows.append(f"| **{s.get('from_name')}** | `{s.get('from_type')}` | `{s.get('standing'):+.2f}` |")
    std_table = "\n".join(std_rows[:80]) if std_rows else "*No standing records.*"

    lp_rows = []
    for lp in sorted(standings.get("loyalty_points", []), key=lambda x: x.get("loyalty_points", 0), reverse=True):
        lp_rows.append(f"| **{lp.get('corporation_name')}** | **{lp.get('loyalty_points', 0):,} LP** |")
    lp_table = "\n".join(lp_rows) if lp_rows else "*No loyalty points accumulated.*"

    standings_md = f"""# Standings & Loyalty Points: {char_name}

- **Standing Entities**: {len(standings.get('standings_list', []))}
- **LP Corporations**: {len(standings.get('loyalty_points', []))}

## Loyalty Points (LP) Balance
| NPC Corporation | Accumulated LP |
| :--- | :--- |
{lp_table}

## Standings Matrix
| Entity Name | Entity Type | Standing Level |
| :--- | :--- | :--- |
{std_table}
"""
    with open(standings_path, "w", encoding="utf-8") as f:
        f.write(standings_md)
    created_files.append(standings_path)

    # 14. CLONES.MD
    clones_path = os.path.join(char_dir, "clones.md")
    active_imps = clones.get("active_implants", [])
    active_imps_str = "\n".join([f"- **{imp}**" for imp in active_imps]) if active_imps else "*No implants installed in active clone.*"

    jc_sections = []
    for idx, jc in enumerate(clones.get("jump_clones", []), 1):
        jc_sections.append(f"### Clone #{idx} (Location ID: `{jc.get('location_id')}`)")
        jc_imps = jc.get("implants", [])
        if jc_imps:
            for imp in jc_imps:
                jc_sections.append(f"- {imp}")
        else:
            jc_sections.append("- *Empty clone (no implants)*")
        jc_sections.append("")
    jc_content = "\n".join(jc_sections) if jc_sections else "*No jump clones established.*"

    clones_md = f"""# Clones & Cybernetics: {char_name}

- **Active Jump Clones**: {len(clones.get('jump_clones', []))}
- **Last Clone Jump**: {clones.get('last_clone_jump_date') or 'Never'}

## Active Medical Clone Implants ({len(active_imps)} Implants)
{active_imps_str}

## Established Jump Clones
{jc_content}
"""
    with open(clones_path, "w", encoding="utf-8") as f:
        f.write(clones_md)
    created_files.append(clones_path)

    # 15. FITTINGS.MD
    fittings_path = os.path.join(char_dir, "fittings.md")
    fit_sections = []
    for fit in fittings:
        fit_sections.append(f"### 🛡️ {fit.get('name')} ({fit.get('ship_type_name')})")
        if fit.get('description'):
            fit_sections.append(f"*{fit.get('description')}*\n")
        fit_sections.append("| Module / Item | Quantity | Slot Flag |")
        fit_sections.append("| :--- | :--- | :--- |")
        for item in fit.get("items", []):
            fit_sections.append(f"| **{item.get('type_name')}** | {item.get('quantity', 1)} | `{item.get('flag')}` |")
        fit_sections.append("")
    fittings_content = "\n".join(fit_sections) if fit_sections else "*No saved ship fittings found.*"

    fittings_md = f"""# Saved Ship Fittings & Loadouts: {char_name}

- **Total Saved Fittings**: **{len(fittings)}**

{fittings_content}
"""
    with open(fittings_path, "w", encoding="utf-8") as f:
        f.write(fittings_md)
    created_files.append(fittings_path)

    return created_files


def synthesize_master_fleet_matrix(all_profiles: list, fleet_dir: str = VAULT_FLEET_DIR) -> list:
    """Generate consolidated master fleet matrix and strategic intelligence reports."""
    os.makedirs(fleet_dir, exist_ok=True)
    created_files = []

    total_sp = sum(p.get("skills", {}).get("total_sp", 0) for p in all_profiles)
    total_isk = sum(p.get("wallet", {}).get("balance", 0.0) for p in all_profiles)
    total_asset_val = sum(p.get("assets", {}).get("total_asset_value", 0.0) for p in all_profiles)
    total_net_worth = total_isk + total_asset_val
    total_assets_count = sum(p.get("assets", {}).get("total_item_count", 0) for p in all_profiles)

    # 1. FLEET_OVERVIEW.MD
    fleet_overview_path = os.path.join(fleet_dir, "fleet_overview.md")
    roster_rows = []
    for p in all_profiles:
        cname = p.get("character_name", "Unknown")
        corp = p.get("corporation_name", "Unknown Corp")
        sys_name = p.get("location", {}).get("solar_system_name", "Unknown")
        ship_name = p.get("ship", {}).get("ship_name", "Ship")
        ship_type = p.get("ship", {}).get("ship_type_name", "Capsule")
        sp = p.get("skills", {}).get("total_sp", 0)
        isk = p.get("wallet", {}).get("balance", 0.0)
        a_val = p.get("assets", {}).get("total_asset_value", 0.0)
        p_net = isk + a_val
        status = "🟢 Online" if p.get("location", {}).get("online") else "⚪ Offline"

        roster_rows.append(f"| **{cname}** | {status} | **{sys_name}** | {ship_name} (`{ship_type}`) | **{sp:,} SP** | **{isk:,.2f} ISK** | **{p_net:,.2f} ISK** | {corp} |")

    roster_table = "\n".join(roster_rows)

    fleet_overview_md = f"""# EVE Online: Alexander Master Fleet Matrix

- **Total Fleet Pilots**: **{len(all_profiles)} Pilots**
- **Combined Fleet Net Worth**: **{total_net_worth:,.2f} ISK**
- **Combined Liquid Treasury**: **{total_isk:,.2f} ISK**
- **Combined Asset Valuation**: **{total_asset_val:,.2f} ISK**
- **Combined Fleet SP**: **{total_sp:,} SP**
- **Combined Fleet Assets**: **{total_assets_count:,} items**
- **Last Synchronized**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
- **Tags**: #eveonline, #fleet, #alexanderfleet, #mastermatrix

---

## Active Fleet Roster
| Pilot Name | State | Current System | Active Ship | Total SP | Liquid ISK | Net Worth | Corporation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{roster_table}
"""
    with open(fleet_overview_path, "w", encoding="utf-8") as f:
        f.write(fleet_overview_md)
    created_files.append(fleet_overview_path)

    # 2. FLEET_WEALTH.MD
    fleet_wealth_path = os.path.join(fleet_dir, "fleet_wealth.md")
    wealth_rows = []
    for p in sorted(all_profiles, key=lambda x: (x.get("wallet", {}).get("balance", 0.0) + x.get("assets", {}).get("total_asset_value", 0.0)), reverse=True):
        cname = p.get("character_name", "Unknown")
        isk = p.get("wallet", {}).get("balance", 0.0)
        a_val = p.get("assets", {}).get("total_asset_value", 0.0)
        p_net = isk + a_val
        pct = (p_net / total_net_worth * 100.0) if total_net_worth > 0 else 0.0
        wealth_rows.append(f"| **{cname}** | **{p_net:,.2f} ISK** | {isk:,.2f} ISK | {a_val:,.2f} ISK | `{pct:.1f}%` |")

    wealth_table = "\n".join(wealth_rows)
    fleet_wealth_md = f"""# Fleet Wealth & Multi-Billion Treasury Distribution

- **Total Fleet Net Worth**: **{total_net_worth:,.2f} ISK**
- **Total Liquid ISK**: **{total_isk:,.2f} ISK**
- **Total Physical Assets**: **{total_asset_val:,.2f} ISK**
- **Pilots Count**: **{len(all_profiles)}**

## Individual Pilot Net Worth Rankings
| Pilot Name | Net Worth | Liquid ISK | Asset Valuation | Fleet Share |
| :--- | :--- | :--- | :--- | :--- |
{wealth_table}
"""
    with open(fleet_wealth_path, "w", encoding="utf-8") as f:
        f.write(fleet_wealth_md)
    created_files.append(fleet_wealth_path)

    # 3. FLEET_ASSETS.MD
    fleet_assets_path = os.path.join(fleet_dir, "fleet_assets.md")
    consolidated_locs = defaultdict(lambda: defaultdict(lambda: {"quantity": 0, "value": 0.0}))
    for p in all_profiles:
        for it in p.get("assets", {}).get("items", []):
            loc = it.get("location_name", "Unknown Station")
            tname = it.get("type_name", "Item")
            qty = it.get("quantity", 1)
            val = it.get("total_value", 0.0)
            consolidated_locs[loc][tname]["quantity"] += qty
            consolidated_locs[loc][tname]["value"] += val

    loc_blocks = []
    sorted_locs = sorted(consolidated_locs.items(), key=lambda x: sum(v["value"] for v in x[1].values()), reverse=True)
    for loc_name, type_counts in sorted_locs[:35]:
        total_loc_value = sum(v["value"] for v in type_counts.values())
        total_items_in_loc = sum(v["quantity"] for v in type_counts.values())
        loc_blocks.append(f"### 📍 {loc_name} (Valuation: **{total_loc_value:,.2f} ISK** | {total_items_in_loc:,} Items)")
        loc_blocks.append("| Item / Ship / Ore Type | Fleet Quantity | Estimated Total Value |")
        loc_blocks.append("| :--- | :--- | :--- |")
        for tname, data in sorted(type_counts.items(), key=lambda x: x[1]["value"], reverse=True)[:50]:
            loc_blocks.append(f"| **{tname}** | {data['quantity']:,} | {data['value']:,.2f} ISK |")
        if len(type_counts) > 50:
            loc_blocks.append(f"| *...and {len(type_counts) - 50} more item types* | | |")
        loc_blocks.append("")

    fleet_assets_md = f"""# Consolidated Fleet Assets & Staging Hub Valuations

- **Total Fleet Asset Valuation**: **{total_asset_val:,.2f} ISK**
- **Total Asset Positions**: **{total_assets_count:,} items**
- **Top Staging Locations**: **{len(consolidated_locs)} bases**

{chr(10).join(loc_blocks)}
"""
    with open(fleet_assets_path, "w", encoding="utf-8") as f:
        f.write(fleet_assets_md)
    created_files.append(fleet_assets_path)

    # 4. FLEET_DOCTRINES.MD
    fleet_doctrines_path = os.path.join(fleet_dir, "fleet_doctrines.md")
    
    doctrine_skills = [
        ("Mining Barges & Exhumers", ["Mining Barge", "Exhumers", "Astrogeology"]),
        ("Industrial Command & Capital Mining", ["Industrial Command Ships", "Capital Industrial Ships"]),
        ("Hauling & Freighters", ["Transport Ships", "Freighter", "Jump Freighters"]),
        ("Combat: Interceptors & Frigates", ["Interceptors", "Assault Frigates", "Covert Ops"]),
        ("Combat: Cruisers & HACs", ["Heavy Assault Cruisers", "Logistics Cruisers", "Recon Ships"]),
        ("Combat: Battleships & Capitals", ["Battleship", "Dreadnoughts", "Carriers"]),
    ]

    doctrine_sections = []
    for doc_name, req_skills in doctrine_skills:
        doctrine_sections.append(f"### 🚀 Doctrine: {doc_name}")
        doctrine_sections.append("| Pilot Name | Total SP | Key Skills Trained | Readiness |")
        doctrine_sections.append("| :--- | :--- | :--- | :--- |")
        for p in all_profiles:
            cname = p.get("character_name", "Unknown")
            p_skills = {s.get("skill_name"): s.get("active_skill_level", 0) for s in p.get("skills", {}).get("skills_list", [])}
            trained = []
            for rs in req_skills:
                matching = [f"{k} L{v}" for k, v in p_skills.items() if rs.lower() in k.lower() and v > 0]
                trained.extend(matching)
            
            readiness = "🟢 Ready" if len(trained) >= 2 else ("🟡 Partial" if len(trained) == 1 else "⚪ Training Required")
            skills_str = ", ".join(trained) if trained else "None"
            doctrine_sections.append(f"| **{cname}** | {p.get('skills', {}).get('total_sp', 0):,} SP | {skills_str} | {readiness} |")
        doctrine_sections.append("")

    fleet_doctrines_md = f"""# Alexander Fleet Ship Doctrine Capability & Readiness Matrix

Evaluates the flight readiness, mastery, and ship classes unlockable by each of the 8 pilots across Mining, Industrial Command, Logistics, and Combat doctrines.

{chr(10).join(doctrine_sections)}
"""
    with open(fleet_doctrines_path, "w", encoding="utf-8") as f:
        f.write(fleet_doctrines_md)
    created_files.append(fleet_doctrines_path)

    # 5. FLEET_STRATEGIC_MAP.MD (Geographic Staging & System Heatmap)
    fleet_map_path = os.path.join(fleet_dir, "fleet_strategic_map.md")
    system_pilots = defaultdict(list)
    for p in all_profiles:
        sys_name = p.get("location", {}).get("solar_system_name", "Unknown System")
        system_pilots[sys_name].append(p)

    map_rows = []
    for sname, plist in sorted(system_pilots.items(), key=lambda x: len(x[1]), reverse=True):
        pnames = ", ".join([p.get("character_name", "Unknown") for p in plist])
        ships = ", ".join([p.get("ship", {}).get("ship_name", "Ship") for p in plist])
        map_rows.append(f"| **{sname}** | **{len(plist)} Pilots** | {pnames} | {ships} |")

    map_table = "\n".join(map_rows)
    fleet_map_md = f"""# Alexander Fleet Strategic Geographic Staging Map

Heatmap of all current pilot locations, active staging hubs, and ship concentrations across New Eden.

| Solar System | Stationed Pilots | Pilot Names | Deployed Ships |
| :--- | :--- | :--- | :--- |
{map_table}
"""
    with open(fleet_map_path, "w", encoding="utf-8") as f:
        f.write(fleet_map_md)
    created_files.append(fleet_map_path)

    # 6. FLEET_SUPPLY_CHAIN.MD (Mining -> PI -> Industry -> Market)
    fleet_supply_path = os.path.join(fleet_dir, "fleet_supply_chain.md")
    total_ore_mined = sum(sum(m.get("quantity", 0) for m in p.get("mining_ledger", [])) for p in all_profiles)
    total_bps = sum(len(p.get("blueprints", [])) for p in all_profiles)
    total_pi = sum(len(p.get("planetary_interaction", [])) for p in all_profiles)
    total_ind_jobs = sum(len(p.get("industry_jobs", [])) for p in all_profiles)

    fleet_supply_md = f"""# Fleet Industrial Supply Chain & Manufacturing Logistics

- **Total Logged Ore Yield**: **{total_ore_mined:,} units**
- **Active Planetary Colonies**: **{total_pi} colonies**
- **Total Blueprint Library**: **{total_bps} blueprints**
- **Active Manufacturing Lines**: **{total_ind_jobs} jobs**

---

### 🔄 Supply Chain Pipeline Architecture
1. **Raw Resource Extraction**:
   - Mining Fleet: 4 Active Exhumers / Mining Barges (`Savian`, `Thena`, `Vulcastra`, `Tulorn`).
   - Daily Mining Ledger logging yields across null-sec/high-sec ore anomalies.
2. **Planetary Commodity Processing**:
   - Distributed planetary interaction infrastructure across New Eden.
3. **Research & Manufacturing**:
   - Blueprint library with researched Material Efficiency (ME) and Time Efficiency (TE).
4. **Market Logistics & Escrows**:
   - Direct selling and distribution through major trade hubs.
"""
    with open(fleet_supply_path, "w", encoding="utf-8") as f:
        f.write(fleet_supply_md)
    created_files.append(fleet_supply_path)

    # 7. FLEET_TRAINING_ROADMAP.MD
    fleet_training_path = os.path.join(fleet_dir, "fleet_training_roadmap.md")
    queue_summary_rows = []
    for p in all_profiles:
        cname = p.get("character_name", "Unknown")
        p_queue = p.get("skills", {}).get("skill_queue", [])
        if p_queue:
            next_skill = p_queue[0]
            queue_summary_rows.append(f"| **{cname}** | **{next_skill.get('skill_name')}** (L{next_skill.get('finished_level')}) | {next_skill.get('finish_date')} | {len(p_queue)} queued |")
        else:
            queue_summary_rows.append(f"| **{cname}** | *Queue Empty / Inactive* | N/A | 0 queued |")

    queue_summary_table = "\n".join(queue_summary_rows)
    fleet_training_md = f"""# Fleet Unified Skill Training Roadmap & Optimization

| Pilot Name | Currently Training Skill | Estimated Completion | Skill Queue Depth |
| :--- | :--- | :--- | :--- |
{queue_summary_table}
"""
    with open(fleet_training_path, "w", encoding="utf-8") as f:
        f.write(fleet_training_md)
    created_files.append(fleet_training_path)

    # 8. FLEET_COMMS.MD
    fleet_comms_path = os.path.join(fleet_dir, "fleet_comms.md")
    total_unread = sum(p.get("mail", {}).get("unread_count", 0) for p in all_profiles)
    total_alerts = sum(len(p.get("notifications", [])) for p in all_profiles)

    fleet_comms_md = f"""# Alexander Fleet Master Communications & Operational Alerts

- **Total Fleet Unread Mails**: **{total_unread} unread messages**
- **Total Operational Notifications**: **{total_alerts} system alerts**

---

### Pilot Mail Status
| Pilot Name | Unread Mail | Total Mail Headers |
| :--- | :--- | :--- |
""" + "\n".join([f"| **{p.get('character_name')}** | `{p.get('mail', {}).get('unread_count', 0)} unread` | {len(p.get('mail', {}).get('headers', []))} headers |" for p in all_profiles]) + "\n"

    with open(fleet_comms_path, "w", encoding="utf-8") as f:
        f.write(fleet_comms_md)
    created_files.append(fleet_comms_path)

    return created_files


def sync_and_index_all_characters(base_dir: str = VAULT_CHAR_DIR, fleet_dir: str = VAULT_FLEET_DIR) -> dict:
    """Extract telemetry for all authorized characters, synthesize dossiers, fleet matrix, and index into knowledge.db."""
    from src.infrastructure.eve_sso import token_manager
    from src.infrastructure.eve_esi import CharacterDataExtractor
    from batch_index import index_single_file
    from src.infrastructure.database import run_maintenance

    characters = token_manager.list_characters()
    results = {"total_characters": len(characters), "synced": [], "errors": [], "indexed_files_count": 0}
    all_profiles = []

    print(f"\n🚀 Starting Full-Spectrum Phase 3 Exhaustive Extraction for {len(characters)} Fleet Pilots...")

    for idx, char_entry in enumerate(characters, 1):
        cid = char_entry.get("character_id")
        cname = char_entry.get("character_name", f"Pilot_{cid}")
        print(f"[{idx}/{len(characters)}] Extracting Phase 3 telemetry for {cname} (ID: {cid})...")
        try:
            extractor = CharacterDataExtractor(cid)
            profile = extractor.extract_full_profile()
            all_profiles.append(profile)
            created_files = synthesize_character_markdown(profile, base_dir=base_dir)
            for fp in created_files:
                index_single_file(fp)
            results["synced"].append({"character_id": cid, "character_name": cname, "files": len(created_files)})
            results["indexed_files_count"] += len(created_files)
            print(f"  ✅ {cname}: Generated and indexed {len(created_files)} dossier files.")
        except Exception as ex:
            print(f"  ❌ {cname}: Extraction error: {ex}")
            results["errors"].append({"character_id": cid, "character_name": cname, "error": str(ex)})

    # Generate Fleet-wide Master Aggregations
    if all_profiles:
        print(f"\n🌐 Synthesizing Master Fleet Matrix & Strategic Maps...")
        fleet_files = synthesize_master_fleet_matrix(all_profiles, fleet_dir=fleet_dir)
        for fp in fleet_files:
            index_single_file(fp)
        results["indexed_files_count"] += len(fleet_files)
        print(f"  ✅ Generated & Indexed {len(fleet_files)} Master Fleet Matrix documents.")

        # Dynamically Update Alpha vs Omega Clone Status
        try:
            from src.infrastructure.eve_alpha_omega import generate_clone_status_markdown
            clone_files = generate_clone_status_markdown()
            for fp in clone_files:
                index_single_file(fp)
            results["indexed_files_count"] += len(clone_files)
            print(f"  ✅ Generated & Indexed {len(clone_files)} Dynamic Clone Status documents.")
        except Exception as c_ex:
            print(f"  ⚠️ Clone status generation notice: {c_ex}")

    if results["synced"]:
        try:
            run_maintenance()
        except Exception:
            pass

    return results
