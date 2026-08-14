---
title: Real-Time Tactical Fleet HUD & Telemetry Gateway Architecture
category: System Architecture
tags: [EVE, HUD, Telemetry, Gateway, FleetOmniscience, Realtime, WebSocket, SSE]
last_updated: 2026-08-14
---

# 🛸 Real-Time Tactical Fleet HUD & Telemetry Gateway Architecture

This document describes the high-speed telemetry streaming architecture powering the EVE Online Tactical Fleet HUD.

---

## 📊 1. Live Fleet Telemetry Snapshot

- **Total Fleet Pilots**: **8 Pilots**
- **Total Combined Fleet SP**: **85,887,339 SP**
- **Total Liquid ISK**: **335,249,453.5 ISK**
- **Fleet Composition**: **4x Omegas (Covetors/Porpoise) | 4x Alphas (1M Unallocated SP Reserve)**

### Pilot Status Ledger
- **Savian Alexander** (`ID: 2122349505`): Porpoise in `G-EURJ` | **74,225,867 SP** | Queue: `Shipboard Compression Technology`
- **Thena Alexander** (`ID: 2124540459`): Covetor in `G-EURJ` | **3,272,860 SP** | Queue: `Reprocessing`
- **Vulcastra Alexander** (`ID: 2124540474`): Covetor in `G-EURJ` | **3,234,190 SP** | Queue: `Reprocessing`
- **Tulorn Alexander** (`ID: 2124540480`): Covetor in `G-EURJ` | **3,242,830 SP** | Queue: `Reprocessing`
- **Saigan Alexander** (`ID: 2124540489`): Velator in `Hodrold` | **642,287 SP** | Queue: `Industry`
- **Targon Alexander** (`ID: 2124540495`): Ibis in `Mettle` | **421,305 SP** | Queue: `Industry`
- **Tila Alexander** (`ID: 2124540497`): Velator in `Mettle` | **424,002 SP** | Queue: `Industry`
- **Rataghast Alexander** (`ID: 2124540504`): Velator in `Mettle` | **423,998 SP** | Queue: `Industry`

---

## 📡 2. Telemetry Endpoints & SSE Streaming Contract

1. **`GET /api/eve/live-stream`**: Real-time Server-Sent Events (SSE) streaming live pilot position updates, ship changes, and threat alerts at 1-second intervals.
2. **`GET /api/eve/hud/state`**: Full state snapshot JSON for the frontend HUD.
3. **`GET /api/eve/search/hybrid?q=...`**: Sub-5ms Reciprocal Rank Fusion (RRF) intelligence lookups.
4. **`GET /api/eve/optimizer/remap`**: Dynamic neural attribute training optimizations.
