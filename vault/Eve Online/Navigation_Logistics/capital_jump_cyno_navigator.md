---
title: Autonomous EVE Online Jump Drive, Cyno Chain & Capital Route Navigator
category: Navigation Logistics
tags: [EVE, Navigation, JumpDrive, CynoChain, JumpFatigue, CapitalLogistics, ChokePoints]
last_updated: 2026-08-14
---

# 🌌 Autonomous Jump Drive, Cyno Chain & Capital Route Navigator

This document establishes the strategic logistics calculus for Capital and Jump Freighter route planning, jump fatigue management, isotope consumption, and high-threat choke point avoidance.

---

## ⚡ 1. Canonical Jump Drive Calibration & Range Matrix

| Capital Ship Family | Base Range | JDC V Range (+100%) | Fuel / LY | Fatigue Reduction Bonus |
| :--- | :---: | :---: | :---: | :---: |
| **Jump Freighters (Rhea/Nomad/Anshar/Ark)** | **5.00 LY** | **10.00 LY** | 1,000 Isotopes | **90.0% Reduction** |
| **Black Ops Battleships (Redeemer/Sin/Widow)** | **4.00 LY** | **8.00 LY** | 600 Isotopes | **75.0% Reduction** |
| **Carriers & Force Auxiliaries (FAX)** | **3.50 LY** | **7.00 LY** | 2,000 Isotopes | **0.0% (Standard)** |
| **Dreadnoughts (Revelation/Naglfar/Moros)** | **3.50 LY** | **7.00 LY** | 2,500 Isotopes | **0.0% (Standard)** |
| **Supercarriers & Titans** | **3.00 LY** | **6.00 LY** | 4,000–6,000 | **0.0% (Standard)** |

---

## 🛑 2. High-Threat Choke Point Avoidance List

The navigation engine automatically suppresses routing through known gank/smartbomb corridors:
- **Uedama**: `Highsec 0.5 Gank Corridor (Safety Warning)`
- **Sivala**: `Highsec 0.6 Caldari-Amarr Pipe (Gank Corridor)`
- **Ahbazon**: `Lowsec 0.4 Gatecamp / Smartbomb Choke`
- **Tama**: `Lowsec 0.3 Caldari-Gallente FW Warzone Gatecamp`
- **Amamake**: `Lowsec 0.4 Minmatar Pirate Hub`
- **Rancer**: `Lowsec 0.4 Smartbomb Trap / Gatecamp`
- **Niarja**: `Triglavian Pochven Isolated System`

---

## 🚀 3. Verified Jump Freighter Route: Delve (1DQ1-A) $\rightarrow$ Jita 4-4 Highway
- **Total Route Distance**: **30.47 LY across 6 Jumps**
- **Total Fuel Demand**: **15,235 Isotopes**
- **Final Accumulated Fatigue**: **13.5 Minutes**

### Cyno Beacon Waypoints & Cooldown Ledger
- **Jump 1**: `1DQ1-A (Delve)` $\rightarrow$ `K-6K16 (Delve)` (**3.82 LY**) | Cooldown: `1m 2s` | Fuel: `1,910`
- **Jump 2**: `K-6K16 (Delve)` $\rightarrow$ `D-PNP9 (Period Basis)` (**4.15 LY**) | Cooldown: `1m 4s` | Fuel: `2,075`
- **Jump 3**: `D-PNP9 (Period Basis)` $\rightarrow$ `I-330X (Khanid)` (**5.2 LY**) | Cooldown: `1m 8s` | Fuel: `2,600`
- **Jump 4**: `I-330X (Khanid)` $\rightarrow$ `Noghere (Kor-Azor)` (**6.8 LY**) | Cooldown: `1m 13s` | Fuel: `3,400`
- **Jump 5**: `Noghere (Kor-Azor)` $\rightarrow$ `Perbair (The Citadel)` (**8.1 LY**) | Cooldown: `1m 19s` | Fuel: `4,050`
- **Jump 6**: `Perbair (The Citadel)` $\rightarrow$ `Jita (The Forge)` (**2.4 LY**) | Cooldown: `1m 21s` | Fuel: `1,200`
