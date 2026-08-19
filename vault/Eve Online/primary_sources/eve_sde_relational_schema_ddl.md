---
title: "CCP Games Static Data Export (SDE) Official Relational Schema DDL"
source_authority: "CCP Games SDE Release / Fuzzwork Enterprise Mirror"
spec_version: "SDE Equinox Release (Latest)"
harvested_at: "2026-08-19T14:35:14Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_SDE_DDL_VERIFIED"
---

# CCP Games Static Data Export (SDE) Relational Schema DDL

## 1. Inventory & Types DDL

```sql
-- invTypes: Master item taxonomy table
CREATE TABLE invTypes (
    typeID INTEGER PRIMARY KEY,
    groupID INTEGER NOT NULL,
    typeName VARCHAR(100) NOT NULL,
    description TEXT,
    mass DOUBLE,
    volume DOUBLE,
    capacity DOUBLE,
    portionSize INTEGER,
    raceID INTEGER,
    basePrice DECIMAL(19, 4),
    published BOOLEAN NOT NULL,
    marketGroupID INTEGER,
    iconID INTEGER,
    soundID INTEGER,
    graphicID INTEGER
);

-- dgmTypeAttributes: Canonical Dogma Attributes for all items & ships
CREATE TABLE dgmTypeAttributes (
    typeID INTEGER NOT NULL,
    attributeID INTEGER NOT NULL,
    valueInt INTEGER,
    valueFloat DOUBLE,
    PRIMARY KEY (typeID, attributeID)
);

-- mapSolarSystems: Universe topology and security status
CREATE TABLE mapSolarSystems (
    solarSystemID INTEGER PRIMARY KEY,
    regionID INTEGER NOT NULL,
    constellationID INTEGER NOT NULL,
    solarSystemName VARCHAR(100) NOT NULL,
    x DOUBLE NOT NULL,
    y DOUBLE NOT NULL,
    z DOUBLE NOT NULL,
    security DOUBLE NOT NULL,
    securityClass VARCHAR(10)
);

-- planetSchematics: Planetary Industry Transformation Rules
CREATE TABLE planetSchematics (
    schematicID INTEGER PRIMARY KEY,
    schematicName VARCHAR(255) NOT NULL,
    cycleTime INTEGER NOT NULL
);
```
