---
title: Sovereign Voice Studio, Awe DSP Mastering Rack & Full Persona Showcase Matrix
category: System Architecture
tags: [VoiceStudio, SovereignAwe, DSPMastering, Kokoro82M, TruePeak, HolographicAura, PersonaShowcase]
last_updated: 2026-08-14
---

# 👑 Sovereign Voice Studio & Awe DSP Mastering Matrix

This specification details the Sovereign Voice Studio architecture, Awe DSP mastering rack presets, and the 21-tool Model Context Protocol suite.

---

## 🏛️ 1. Studio Acoustic Architecture

```mermaid
graph TD
    Text["Spoken Text Input"] --> Normalizer["VoiceNormalizer (Phonetics & Breathing Cadence)"]
    Normalizer --> Kokoro["Kokoro-82M ONNX Neural Engine"]
    Kokoro --> DSP["VoiceDSP Awe Mastering Rack (Single-Pass Biquad)"]
    
    subgraph DSP_Presets["Acoustic DSP Presets"]
        Sovereign["SOVEREIGN_PRESENCE (180Hz Warmth + 3.8kHz Crystal Presence)"]
        Awe["AWE_STUDIO_MASTER (4.5kHz Broadcast Sheen)"]
        Tactical["COMMANDER_TACTICAL (2.8kHz Midrange Vocal Punch)"]
        Aura["TRANSCENDENTAL_AURA (3.4kHz & 8.5kHz Holographic Shimmer)"]
    end
    
    DSP --> DSP_Presets
    DSP_Presets --> Limiter["True-Peak Soft-Tanh Saturation (-1.0 dBFS)"]
    Limiter --> Output["Win32 In-Memory C-Level Streamer (<15ms)"]
```

---

## 🎭 2. Full Persona Showcase Matrix

| Persona Key | Voice Identifier | Acoustic DSP Preset | Sonic Aesthetic & Purpose |
|---|---|---|---|
| **`AURA_SHIP_AI`** | `bf_emma` | `TRANSCENDENTAL_AURA` | Ethereal holographic AI shipboard assistant. |
| **`TACTICAL_ADVISOR`** | `af_sarah` | `COMMANDER_TACTICAL` | High-intelligibility combat warnings and threat vectors. |
| **`FLEET_COMMANDER`** | `am_adam` | `SOVEREIGN_PRESENCE` | Commanding flagship fleet broadcasts and anchoring orders. |
| **`INDUSTRY_OVERSEER`** | `bm_george` | `AWE_STUDIO_MASTER` | Calm broadcast telemetry for mining and planetary reactions. |
| **`CALM_OPERATIONS`** | `af_bella` | `STUDIO_DIRECT` | Pristine linear speech for DevOps, CI/CD, and SQLite operations. |
| **`EXECUTIVE_DIRECTOR`** | `af_heart` | `SOVEREIGN_PRESENCE` | Executive briefings, business metrics, and stakeholder summaries. |
| **`WARP_NAVIGATOR`** | `bf_isabella` | `TRANSCENDENTAL_AURA` | Lowsec route plotting and safe transit coordinates. |
| **`SOVEREIGN_ORACLE`** | `af_sky` | `SOVEREIGN_PRESENCE` | Philosophical, cryptographic, and SOC 2 attestation memos. |

---

## 🎛️ 3. 21-Tool Model Context Protocol Matrix

1. **`antigravity_showcase_personas`**: Catalog exploration and persona auditions.
2. **`antigravity_apply_studio_master`**: Masters any text through Sovereign Awe DSP and speaks in-memory in $<15\text{ms}$.
