---
title: "CCP Games EVE Online Static Data Export (SDE) Relational Schema DDL"
source_authority: "CCP Games Developer Resources / Fuzzwork SDE Conversion"
database_type: "SQLite 3 Relational Architecture"
harvested_at: "2026-08-17T16:30:04Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_SDE_RELATIONAL_SCHEMA_VERIFIED"
---

# CCP Games Static Data Export (SDE) Relational Schema

## 1. Inventory & Item Taxonomy Tables

```sql
CREATE TABLE invTypes (
    typeID INTEGER PRIMARY KEY,
    groupID INTEGER,
    typeName TEXT NOT NULL,
    description TEXT,
    mass REAL,
    volume REAL,
    capacity REAL,
    portionSize INTEGER,
    raceID INTEGER,
    basePrice REAL,
    published INTEGER,
    marketGroupID INTEGER,
    iconID INTEGER,
    soundID INTEGER,
    graphicID INTEGER
);

CREATE TABLE invGroups (
    groupID INTEGER PRIMARY KEY,
    categoryID INTEGER,
    groupName TEXT NOT NULL,
    iconID INTEGER,
    useBasePrice INTEGER,
    anchored INTEGER,
    anchorable INTEGER,
    fittableNonSingleton INTEGER,
    published INTEGER
);

CREATE TABLE invCategories (
    categoryID INTEGER PRIMARY KEY,
    categoryName TEXT NOT NULL,
    iconID INTEGER,
    published INTEGER
);
```

## 2. Dogma Attributes & Ship Fitting Physics Tables

```sql
CREATE TABLE dgmTypeAttributes (
    typeID INTEGER NOT NULL,
    attributeID INTEGER NOT NULL,
    valueInt INTEGER,
    valueFloat REAL,
    PRIMARY KEY (typeID, attributeID)
);

CREATE TABLE dgmAttributeTypes (
    attributeID INTEGER PRIMARY KEY,
    attributeName TEXT NOT NULL,
    description TEXT,
    iconID INTEGER,
    defaultValue REAL,
    published INTEGER,
    displayName TEXT,
    unitID INTEGER,
    stackable INTEGER,
    highIsGood INTEGER,
    categoryID INTEGER
);
```

## 3. Celestial Map & Solar System Navigation Tables

```sql
CREATE TABLE mapSolarSystems (
    regionID INTEGER,
    constellationID INTEGER,
    solarSystemID INTEGER PRIMARY KEY,
    solarSystemName TEXT NOT NULL,
    x REAL,
    y REAL,
    z REAL,
    xMin REAL,
    xMax REAL,
    yMin REAL,
    yMax REAL,
    zMin REAL,
    zMax REAL,
    luminosity REAL,
    border INTEGER,
    fringe INTEGER,
    corridor INTEGER,
    hub INTEGER,
    international INTEGER,
    regional INTEGER,
    constellation INTEGER,
    security REAL,
    factionID INTEGER,
    radius REAL,
    sunTypeID INTEGER,
    securityClass TEXT
);
```

## 4. Planetary Industry Schematics Tables

```sql
CREATE TABLE planetSchematics (
    schematicID INTEGER PRIMARY KEY,
    schematicName TEXT NOT NULL,
    cycleTime INTEGER
);

CREATE TABLE planetSchematicsTypeMap (
    schematicID INTEGER NOT NULL,
    typeID INTEGER NOT NULL,
    quantity INTEGER,
    isInput INTEGER,
    PRIMARY KEY (schematicID, typeID, isInput)
);
```
