---
title: Autonomous EVE Online Auditory Voice Tactical AI Co-Pilot & Neural TTS Bridge
category: System Architecture
tags: [EVE, VoiceAI, TextToSpeech, NeuralTTS, Piper, OpenTTS, Docker, SAPI, AuditoryRadar, MultiBoxing]
last_updated: 2026-08-14
---

# 🎙️ Autonomous Auditory Voice Tactical AI Co-Pilot & Neural TTS Bridge

This document establishes the dual-engine auditory tactical alert synthesis architecture, unifying containerized Neural TTS with native Windows SAPI hardware speech synthesis.

---

## 🏗️ 1. Multi-Tiered Neural Speech Topology

```mermaid
graph TD
    Alert["Tactical Event Triggered (e.g., Hostile in G-EURJ)"] --> Router["Voice Tactical Co-Pilot Engine"]
    Router --> CheckNeural TTS Container Available? (port 5500)
    Check -- Yes --> Piper["Tier 1: Containerized Neural Voice (Piper / OpenTTS)<br>Studio-Grade PCM/WAV Audio Stream"]
    Check -- No / Timeout --> SAPI["Tier 2: Native Windows SAPI SpeechSynthesizer<br>Zero-Latency Local Desktop Spoken Output"]
    Piper --> Stream["Stream Audio to Web HUD / Playback Device"]
    SAPI --> Audio["Primary OS Audio Endpoint"]
```

---

## 📢 2. Canonical Voice Alert Catalog

| Alert Trigger Event | Spoken Message Syntax | Priority Level |
| :--- | :--- | :---: |
| **Hostile Local Entry** | *"Warning. Hostile pilot entered solar system `{system}`. Prepare fleet alignment."* | **CRITICAL** |
| **Incoming Damage Spike** | *"Emergency alert. `{character}` is taking heavy shield damage."* | **CRITICAL** |
| **Cargo Hold Depletion/Full** | *"`{character}`'s cargo bay is full. Spooling Porpoise compression unit."* | **URGENT** |
| **Fleet Alignment Broadcast** | *"Fleet command broadcast: Aligning all vessels to safe citadel bookmark."* | **URGENT** |
| **Cynosural Jump Beacon** | *"Cynosural field beacon lit in `{system}`. Capital jump transit clear."* | **INFO** |

---

## ⚡ 3. Active Alert Dispatch Ledger
- **Last Triggered Alert**: `Warning. Hostile pilot entered solar system G-EURJ. Prepare fleet alignment.`
- **Active Engine**: `Windows_SAPI`
- **Container Endpoint**: `http://127.0.0.1:5500/api/tts` (Model: `piper:en_US-lessac-medium`)
- **Fallback Engine**: Windows SAPI System.Speech Synthesis (Zero-Latency Local Execution)
