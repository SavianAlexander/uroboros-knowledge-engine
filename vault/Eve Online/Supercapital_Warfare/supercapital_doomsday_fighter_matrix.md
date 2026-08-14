---
title: Autonomous EVE Online Supercapital Warfare & Doomsday AoE Engine
category: Supercapital Warfare
tags: [EVE, Supercapitals, Titans, Supercarriers, Doomsday, FAX, TriageMode, FleetEHP]
last_updated: 2026-08-14
---

# 👑 Autonomous Supercapital Warfare & Doomsday AoE Simulation Engine

This document provides the strategic combat equations, Doomsday signature scaling calculations, Supercarrier fighter wing DPS profiles, and FAX Triage capacitor stability models.

---

## ⚡ 1. Titan Doomsday Weapons Matrix

| Doomsday Device | Hull Class | Damage Type | Alpha Damage | Mechanism |
| :--- | :--- | :---: | :---: | :--- |
| **Judgement** | **Avatar (Amarr)** | **EM** | **2,500,000** | Directed Target Beam |
| **Aurora OMR** | **Leviathan (Caldari)** | **Kinetic** | **2,500,000** | Directed Kinetic Torpedo |
| **Oblivion** | **Erebus (Gallente)** | **Thermal** | **2,500,000** | Directed Plasma Blast |
| **Gjallarhorn** | **Ragnarok (Minmatar)** | **Explosive** | **2,500,000** | Directed Shockwave |
| **Bosonic Field Generator** | **All Titans** | **Omni** | **1,200,000** | **Directional AoE Cone (30km $\times$ 200km)** |

---

## 🦅 2. Supercarrier Fleet Wings & Fighter Burst DPS

| Supercarrier | Empire | Fighter Tubes | Heavy Bomber Wings | Sustained DPS | Base Tank EHP |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Aeon** | Amarr | 5 Tubes | 3 Heavy Squadrons | **4,800 DPS** | **42.5M Armor EHP** |
| **Wyvern** | Caldari | 5 Tubes | 3 Heavy Squadrons | **4,600 DPS** | **45.0M Shield EHP** |
| **Nyx** | Gallente | 5 Tubes | 3 Heavy Squadrons | **5,400 DPS** | **38.0M Armor EHP** |
| **Hel** | Minmatar | 5 Tubes | 3 Heavy Squadrons | **5,100 DPS** | **39.5M Shield EHP** |

---

## 🚑 3. Force Auxiliary (FAX) Triage Mode Stability Benchmark
- **Hull**: `Apostle (Amarr)`
- **Triage Duration**: **10.0 Minutes (2 Cycles)**
- **Hostile Energy Draining Pressure**: **480,000.0 GJ**
- **Capacitor Boosters Injected**: **51,200.0 GJ (16x Cap Booster 3200)**
- **Capacitor Stability Status**: **`CAPACITOR_DEPLETED`** (Remaining: `0 GJ`)
