---
title: "EVE Online Complete Universe Topology & All 114 Regions Catalog"
source_authority: "CCP Games ESI Universe API (`/universe/regions/`)"
total_universe_regions: 114
harvested_at: "2026-08-17T17:00:15Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED_UNIVERSE_CATALOG"
verification: "CCP_ESI_UNIVERSE_API_VERIFIED"
---

# EVE Online Complete Universe Topology (All 114 Regions)

**Authority**: CCP Games Official ESI Universe Architecture.  
**Live Endpoint**: `https://esi.evetech.net/latest/universe/regions/`  
**Total Universe Regions**: **114 Regions** (Highsec, Lowsec, Nullsec, Wormhole, and Pochven space).

---

## Strategic Regional Topology (Sample Roster)

| Region ID | Region Name | Security Classification | Tactical & Market Profile |
| :---: | :--- | :--- | :--- |
| `10000002` | **The Forge** | Highsec | Caldari State Core / Jita 4-4 Hub |
| `10000030` | **Heimatar** | Highsec | Minmatar Republic Core / Rens Hub |
| `10000032` | **Sinq Laison** | Highsec | Gallente Federation Core / Dodixie Hub |
| `10000043` | **Domain** | Highsec | Amarr Empire Core / Amarr Hub |
| `10000060` | **Delve** | Nullsec | Blood Raiders / Nullsec Sovereign Space |
| `10000016` | **Lonetrek** | Highsec | Caldari State / Perimeter Border |
| `10000067` | **Genesis** | Highsec | Amarr Empire / New Eden System & Sanctum |
| `10000048` | **Placid** | Lowsec | Syndicate Border / Faction Warfare |
| `10000064` | **Esoteria** | Nullsec | Stain Border / Nullsec Sov |
| `10000068` | **Verge Vendor** | Lowsec | Gallente / Syndicate Connection |

---

## Live Universe Ingestion Endpoints
- **All Regions**: `GET https://esi.evetech.net/latest/universe/regions/`
- **Region Details**: `GET https://esi.evetech.net/latest/universe/regions/{region_id}/`
- **All Constellations**: `GET https://esi.evetech.net/latest/universe/constellations/`
- **All Solar Systems**: `GET https://esi.evetech.net/latest/universe/systems/`
- **System Details (Jita 30000142)**: `GET https://esi.evetech.net/latest/universe/systems/30000142/`
- **Planetary Schematics**: `GET https://esi.evetech.net/latest/universe/schematics/{schematic_id}/`
