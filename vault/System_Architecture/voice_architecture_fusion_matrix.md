---
title: Voice Architecture Fusion & Fragmentation Optimization Matrix
category: System Architecture
tags: [CleanArchitecture, VoiceDSP, VoiceEngine, AudioMastering, Decoupling, BiquadEQ, Kokoro82M]
last_updated: 2026-08-14
---

# 🎼 Voice Architecture Fusion & Fragmentation Optimization Matrix

This document defines the consolidated, clean-architecture voice subsystems for the Uroboros Knowledge Engine and Antigravity.

---

## 🏛️ 1. Architecture Topology (Post-Fusion)

```mermaid
graph TD
    subgraph Linguistic_Layer["1. Linguistic Normalization Layer"]
        Normalizer["voice_normalizer.py (Phonetic Lexicon, Cadence, Markdown Stripper)"]
    end

    subgraph Core_Engine_Layer["2. Neural Engine & Intercom Layer"]
        Engine["voice_engine.py (Kokoro-82M ONNX, NonInterruptingAudioQueue)"]
        Call["voice_call_intercom.py (DTMF, Roger Beeps, Full-Duplex Intercom)"]
        VAD["voice_vad_interrupter.py (Sub-0.5ms Barge-In Cutoff)"]
    end

    subgraph Unified_DSP_Layer["3. Unified DSP & Mastering Layer (Single-Pass)"]
        DSP["voice_dsp.py (Biquad EQ, Audio Ducking, True-Peak Limiter, 32-Band FFT)"]
    end

    subgraph Domain_Alerts["4. Domain Tactical Alerts"]
        EVEAlerts["eve_voice_alerts.py (EVE Dogma Warnings & Cockpit Templates)"]
    end

    Linguistic_Layer --> Core_Engine_Layer
    Core_Engine_Layer --> Unified_DSP_Layer
    Domain_Alerts --> Core_Engine_Layer
```

---

## 🧬 2. Fusion & Decoupling Benefits

1. **Unified DSP Pipeline (`src/core/voice_dsp.py`)**:
   - Single-pass processing: Parametric Biquad EQ $\rightarrow$ Dynamic Ducking (-14dB) $\rightarrow$ True-Peak Limiter (-1.0 dBFS) $\rightarrow$ 32-Band FFT.
   - Eliminates redundant array copies and memory allocations.
2. **Universal Neural Audio Engine (`src/core/voice_engine.py`)**:
   - Fully decoupled from game domain specifics.
   - Houses in-memory C Win32 `winsound` buffer queue with monotonic sequence counter and sub-0.5ms barge-in audio purge (`SND_PURGE`).
3. **Dedicated Linguistic Normalizer (`src/core/voice_normalizer.py`)**:
   - Strictly handles phonetic acronym expansion, tech terms, and breath pauses.
