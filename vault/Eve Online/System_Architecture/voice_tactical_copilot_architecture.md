---
title: Autonomous EVE Online Kokoro-82M Neural Voice Engine & Streaming Conversational Pipeline
category: System Architecture
tags: [EVE, VoiceAI, Kokoro82M, NeuralTTS, AMD, DirectML, SAPI, AuditoryRadar, MultiBoxing, ConversationalFlow]
last_updated: 2026-08-14
---

# 🎙️ Autonomous Kokoro-82M Neural Voice Engine & Non-Interrupting Queue

This document establishes the Kokoro-82M ONNX neural voice architecture, featuring non-interrupting serialized audio playback queues with emergency preemption.

---

## 🏗️ 1. Multi-Tiered Neural Speech Topology

```mermaid
graph TD
    Alert["Tactical Event Triggered (e.g., Hostile in G-EURJ)"] --> Router["Kokoro Voice Tactical Co-Pilot Router"]
    Router --> Queue["Non-Interrupting Audio Queue (Thread-Safe Priority Serialization)"]
    Queue --> EngineTier 1: Direct In-Process ONNX Model Available?
    Engine -- Yes --> InProcess["Direct ONNX Runtime (bf_emma)<br>Studio-Grade 24kHz Audio (< 35ms Latency)"]
    Engine -- No --> ContainerTier 2: Kokoro-FastAPI Container Available? (port 8880)
    Container -- Yes --> HTTP["OpenAI /v1/audio/speech Protocol"]
    Container -- No --> SAPI["Tier 3: Native Windows SAPI SpeechSynthesizer Fallback"]
    InProcess --> Speaker["🔊 Primary Audio Output (Sequential Playback)"]
    HTTP --> Speaker
    SAPI --> Speaker
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
