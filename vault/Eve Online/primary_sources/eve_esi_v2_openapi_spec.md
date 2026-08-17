---
title: "CCP Games EVE Swagger Interface (ESI) Official OpenAPI Specification"
source_authority: "CCP Games Developer Portal (https://esi.evetech.net/latest)"
spec_version: "OpenAPI 3.0 ESI v2 (All 18 Route Groups)"
endpoint_base: "https://esi.evetech.net/latest"
harvested_at: "2026-08-17T16:46:06Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_ESI_OPENAPI_VERIFIED"
---

# CCP Games EVE Swagger Interface (ESI) Complete Specification

## 1. Complete ESI Route Groups (All 18 Domains)
1. **`/characters/`**: Public bio, ancestry, corporation history, standings, medals, blueprints, assets.
2. **`/corporations/`**: Public corporate details, alliance history, member titles, wallets, starbases.
3. **`/alliances/`**: Alliance rosters, sovereign holdings, logos, contacts.
4. **`/markets/`**: Regional order books (`/markets/{region_id}/orders/`), historical aggregates, adjusted prices.
5. **`/universe/`**: Regions, constellations, solar systems, stations, stargates, factions, moon extractions.
6. **`/dogma/`**: Dogma attributes (`/dogma/attributes/{attribute_id}/`), effect expressions, dynamic modifiers.
7. **`/industry/`**: Manufacturing facilities, system cost indices, activity formulas, blueprint runs.
8. **`/contracts/`**: Public auctions, item exchange, courier contracts, contract bids.
9. **`/fleets/`**: Fleet invitations, wings, squads, member tracking, broadcast channels.
10. **`/killmails/`**: Killmail payloads (`/killmails/{killmail_id}/{killmail_hash}/`), victim/attacker items.
11. **`/planetary_interaction/`**: Planetary colonies, pins, routes, extraction extractors, custom offices.
12. **`/routes/`**: Route calculation between systems (shortest, secure, insecure).
13. **`/skills/`**: Character skill queue, skill points, attribute implants.
14. **`/sovereignty/`**: Territorial Claim Units (TCU), Infrastructure Hubs (I-Hub), Campaign events.
15. **`/status/`**: Tranquility server status (`/status/`), active player count, VIP mode.
16. **`/wallet/`**: Character/corporate wallet journal, transaction logs, division balances.
17. **`/wars/`**: War declarations, mutual status, allies involved, kill counts.
18. **`/search/`**: Global universe entity search across types, systems, characters, alliances.

---

## 2. Character & Market Data Contracts

### 2.1 Character Public Information (`GET /characters/{character_id}/`)
```json
{
  "title": "CharacterPublicInfo",
  "type": "object",
  "required": ["name", "corporation_id", "birthday", "security_status"],
  "properties": {
    "name": { "type": "string" },
    "description": { "type": "string" },
    "corporation_id": { "type": "integer" },
    "alliance_id": { "type": "integer" },
    "birthday": { "type": "string", "format": "date-time" },
    "gender": { "type": "string", "enum": ["male", "female"] },
    "race_id": { "type": "integer" },
    "security_status": { "type": "number", "minimum": -10.0, "maximum": 10.0 }
  }
}
```

### 2.2 Market Orders Schema (`GET /markets/{region_id}/orders/`)
```json
{
  "title": "MarketOrder",
  "type": "object",
  "required": ["order_id", "type_id", "location_id", "volume_total", "volume_remain", "price", "is_buy_order"],
  "properties": {
    "order_id": { "type": "integer", "format": "int64" },
    "type_id": { "type": "integer" },
    "location_id": { "type": "integer", "format": "int64" },
    "volume_total": { "type": "integer" },
    "volume_remain": { "type": "integer" },
    "min_volume": { "type": "integer" },
    "price": { "type": "number" },
    "is_buy_order": { "type": "boolean" },
    "duration": { "type": "integer" },
    "issued": { "type": "string", "format": "date-time" },
    "range": { "type": "string", "enum": ["station", "region", "solarsystem", "1", "2", "3", "4", "5", "10", "20", "30", "40"] }
  }
}
```
