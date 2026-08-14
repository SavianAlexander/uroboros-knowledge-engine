---
title: Autonomous EVE Online Kokoro-82M Neural Voice Engine & Streaming Conversational Pipeline
category: System Architecture
tags: [EVE, VoiceAI, Kokoro82M, NeuralTTS, AMD, DirectML, SAPI, AuditoryRadar, MultiBoxing, ConversationalFlow]
last_updated: 2026-08-14
---

# 🎙️ Autonomous Kokoro-82M Neural Voice Engine & Streaming Conversational Pipeline

This document establishes the Kokoro-82M ONNX neural voice architecture, combining OpenAI-compatible `/v1/audio/speech` streaming with native Windows SAPI hardware speech synthesis.

---

## 🏗️ 1. Multi-Tiered Neural Speech Topology

```mermaid
graph TD
    Alert["Tactical Event Triggered (e.g., Hostile in G-EURJ)"] --> Router["Kokoro Voice Tactical Co-Pilot Router"]
    Router --> CheckKokoro-FastAPI Container Available? (port 8880)
    Check -- Yes --> Kokoro["Tier 1: Kokoro-82M ONNX Neural Voice (bf_emma)<br>Studio-Grade 24kHz Audio Stream (< 40ms Latency)"]
    Check -- No / Timeout --> SAPI["Tier 2: Native Windows SAPI SpeechSynthesizer<br>Zero-Latency Local Desktop Spoken Output"]
    Kokoro --> Stream["Stream Audio to Web HUD / Playback Device"]
    SAPI --> Audio["Primary OS Audio Endpoint"]
```

---

## 🎭 2. Canonical Voice Persona Catalog

| Persona Role | Voice Code | Accent / Gender | Characteristic Tone |
| :--- | :---: | :---: | :--- |
| **AURA Ship AI (Primary)** | `bf_emma` | British Female | Calm, authoritative, crystalline ship computer |
| **Tactical Combat Advisor** | `af_sarah` | American Female | Urgent, rapid, crisp tactical commands |
| **Fleet Commander Anchor** | `am_adam` | American Male | Deep, resonant, military broadcast tone |
| **Industry & Refiner Lead** | `bm_george` | British Male | Measured, precise, analytical industrialist |
| **Fluid Conversational AI** | `af_bella` | American Female | Natural prosody, conversational breathing & flow |

---

## ⚡ 3. Active Alert Dispatch Ledger
- **Last Triggered Alert**: `Warning. Hostile pilot entered solar system G-EURJ. Prepare fleet alignment.`
- **Active Engine**: `Windows_SAPI`
- **Container Endpoint**: `http://127.0.0.1:8880/v1/audio/speech` (Model: `kokoro`, Voice: `bf_emma`)
- **Fallback Engine**: Windows SAPI System.Speech Synthesis (Zero-Latency Local Execution)
