---
title: "CCP Games EVE Swagger Interface (ESI) Official OpenAPI Specification"
source_authority: "CCP Games Developer Portal (https://esi.evetech.net/latest/swagger.json)"
spec_version: "OpenAPI 2.0 / 3.0 ESI v2"
endpoint_base: "https://esi.evetech.net/latest"
harvested_at: "2026-08-17T16:14:42Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_ESI_OPENAPI_VERIFIED"
---

# CCP Games EVE Swagger Interface (ESI) Official Specification

## 1. Core Endpoints & Data Contracts

### 1.1 Character Public Information (`GET /characters/{character_id}/`)
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
    "bloodline_id": { "type": "integer" },
    "security_status": { "type": "number", "minimum": -10.0, "maximum": 10.0 }
  }
}
```

### 1.2 Market Orders in Region (`GET /markets/{region_id}/orders/`)
```json
{
  "title": "MarketOrderList",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["order_id", "type_id", "location_id", "volume_total", "volume_remain", "price", "is_buy_order", "duration", "issued", "range"],
    "properties": {
      "order_id": { "type": "integer", "format": "int64" },
      "type_id": { "type": "integer" },
      "location_id": { "type": "integer", "format": "int64" },
      "volume_total": { "type": "integer" },
      "volume_remain": { "type": "integer" },
      "price": { "type": "number" },
      "is_buy_order": { "type": "boolean" },
      "duration": { "type": "integer" },
      "issued": { "type": "string", "format": "date-time" },
      "range": { "type": "string", "enum": ["station", "region", "solarsystem", "1", "2", "3", "4", "5", "10", "20", "30", "40"] }
    }
  }
}
```

### 1.3 Planetary Colonies Layout (`GET /characters/{character_id}/planets/{planet_id}/`)
```json
{
  "title": "PlanetaryColonyLayout",
  "type": "object",
  "required": ["links", "pins", "routes"],
  "properties": {
    "links": { "type": "array" },
    "pins": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pin_id", "type_id", "latitude", "longitude"],
        "properties": {
          "pin_id": { "type": "integer", "format": "int64" },
          "type_id": { "type": "integer" },
          "schematic_id": { "type": "integer" },
          "extractor_details": {
            "type": "object",
            "properties": {
              "cycle_time": { "type": "integer" },
              "head_radius": { "type": "number" },
              "heads": { "type": "array" },
              "product_type_id": { "type": "integer" }
            }
          }
        }
      }
    },
    "routes": { "type": "array" }
  }
}
```
