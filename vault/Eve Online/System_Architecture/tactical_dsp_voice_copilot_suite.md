---
title: Autonomous EVE Online Tactical DSP Voice Engine & Multi-Stem Radar Suite
category: System Architecture
tags: [EVE, VoiceAI, DSP, CockpitAcoustics, SpatialAudio, MultiStem, VoiceCommander, RadarDaemon]
last_updated: 2026-08-14
---

# 🎛️ Autonomous Tactical DSP Voice Engine & Multi-Stem Radar Suite

This document establishes the digital signal processing (DSP) acoustics rack, hands-free voice command lexicon, and multi-stem spatial audio radar dispatcher.

---

## 🎧 1. Spatial Stereo Panning & Character Voice Stems

| Operational Domain | Character Voice Code | Spatial Stereo Pan | Acoustic DSP Filter Preset |
| :--- | :---: | :---: | :--- |
| **AURA Ship AI (Primary)** | `bf_emma` | **Center ($0.0$)** | `AURA_COCKPIT` (30ms multi-tap bridge reverb) |
| **Threat & Combat Radar** | `af_sarah` | **Hard Right ($+1.0$)** | `TACTICAL_RADIO` (300-3400Hz VHF bandpass + start chirp) |
| **Mining Harvester Wing** | `af_bella` | **Hard Left ($-0.8$)** | `HARVESTER_COMMS` (Soft overdrive + industrial radio) |
| **Fleet Commander Broadcast** | `am_adam` | **Center ($0.0$)** | `TACTICAL_RADIO` (Authoritative military comms) |
| **Market & Refiner Lead** | `bm_george` | **Left Center ($-0.4$)** | `STUDIO_DIRECT` (Analytical clear speech) |

---

## ⚡ 2. Automated Event-to-Voice Dispatch Ledger

### Event 1: `mining_yield` (INFO Priority)
- **Spoken Message**: *"Harvester laser cycle complete: 4,800 units of Spodumain transferred to ore hold."*
- **Voice Stem**: `af_bella` (Pan: `-0.8`)
- **Acoustic Preset**: `HARVESTER_COMMS`

### Event 2: `chat_intel` (CRITICAL Priority)
- **Spoken Message**: *"Intel broadcast from delve.intel: G-EURJ * 1x Loki 14.3 AU D-Scan"*
- **Voice Stem**: `bf_emma` (Pan: `+0.0`)
- **Acoustic Preset**: `AURA_COCKPIT`

### Event 3: `combat_damage` (CRITICAL Priority)
- **Spoken Message**: *"Emergency alert. Thena Alexander taking 850 damage from Heavy Missile."*
- **Voice Stem**: `af_sarah` (Pan: `+1.0`)
- **Acoustic Preset**: `TACTICAL_RADIO`

