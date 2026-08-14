"""
Autonomous EVE Online Procedural Tactical SFX Soundboard & Soundscape Generator.
Standard: Pure Python Standard Library + NumPy.
Ponytail Senior Dev Principle: 100% procedural synthesis of cockpit alarms, warp drives, target lock pings, and ambient reactor drones with zero external audio assets.
"""

import os
import sys
import math
import io
import time
try:
    import numpy as np
except ImportError:
    np = None
try:
    import soundfile as sf
except ImportError:
    sf = None
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def generate_warp_drive_spool(sample_rate: int = 24000, duration_s: float = 2.5) -> np.ndarray:
    """Procedural Warp Drive Spool: Exponential sub-bass sweep with phase modulation."""
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    # Exponential frequency sweep from 55Hz to 330Hz
    freqs = 55.0 * np.exp(t * 0.75)
    phase = 2 * np.pi * np.cumsum(freqs) / sample_rate
    carrier = 0.4 * np.sin(phase)

    # Sub-harmonic rumble
    sub = 0.25 * np.sin(phase * 0.5)
    # Flanger / Chorus oscillation (3Hz LFO)
    lfo = 1.0 + 0.3 * np.sin(2 * np.pi * 3.0 * t)

    warp_signal = (carrier + sub) * lfo
    # Envelope
    env = np.sin(np.pi * t / duration_s)
    return (warp_signal * env).astype(np.float32)


def generate_shield_critical_siren(sample_rate: int = 24000, duration_s: float = 1.8) -> np.ndarray:
    """Procedural Shield Critical Siren: Rapid dual-tone frequency modulation (1200Hz <-> 850Hz)."""
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    # 5 Hz modulation between 850Hz and 1250Hz
    mod_freq = 1050.0 + 200.0 * np.sin(2 * np.pi * 5.0 * t)
    phase = 2 * np.pi * np.cumsum(mod_freq) / sample_rate
    siren = 0.35 * np.sin(phase) + 0.15 * np.sin(phase * 2.0)
    # Envelope
    env = np.minimum(1.0, t * 10.0) * np.minimum(1.0, (duration_s - t) * 5.0)
    return (siren * env).astype(np.float32)


def generate_armor_bleed_klaxon(sample_rate: int = 24000, duration_s: float = 1.2) -> np.ndarray:
    """Procedural Armor Bleed Alarm: Staccato alarm bursts (550Hz & 880Hz)."""
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    # 4 pulses per second
    pulse = np.sin(2 * np.pi * 4.0 * t) > 0.0
    tone = 0.3 * np.sin(2 * np.pi * 550.0 * t) + 0.2 * np.sin(2 * np.pi * 880.0 * t)
    return (tone * pulse).astype(np.float32)


def generate_hull_breach_alarm(sample_rate: int = 24000, duration_s: float = 2.0) -> np.ndarray:
    """Procedural Hull Breach Critical Alarm: Deep dissonant emergency klaxon (110Hz + 155Hz)."""
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    pulse = np.sin(2 * np.pi * 2.0 * t) > 0.0
    dissonance = 0.4 * np.sin(2 * np.pi * 110.0 * t) + 0.3 * np.sin(2 * np.pi * 155.5 * t)
    return (dissonance * pulse).astype(np.float32)


def generate_target_lock_acquired(sample_rate: int = 24000) -> np.ndarray:
    """Procedural Target Lock Acquired Tone: Ascending high-tech tri-tone ping."""
    freqs = [1760.0, 2200.0, 3520.0]
    duration_per_tone = 0.08
    tones = []
    for f in freqs:
        n = int(sample_rate * duration_per_tone)
        t = np.linspace(0, duration_per_tone, n, endpoint=False)
        tone = 0.25 * np.sin(2 * np.pi * f * t) * np.hanning(n)
        tones.append(tone)
    return np.concatenate(tones).astype(np.float32)


def generate_cockpit_ambient_hum(sample_rate: int = 24000, duration_s: float = 5.0) -> np.ndarray:
    """Procedural Cockpit Starship Reactor Drone: 60Hz hum + 120Hz harmonic + filtered air noise."""
    n_samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    hum = 0.12 * np.sin(2 * np.pi * 60.0 * t) + 0.06 * np.sin(2 * np.pi * 120.0 * t)
    noise = np.random.uniform(-0.02, 0.02, n_samples)
    ambient = (hum + noise)
    return ambient.astype(np.float32)


SFX_LIBRARY = {
    "warp_spool": generate_warp_drive_spool,
    "shield_critical": generate_shield_critical_siren,
    "armor_bleed": generate_armor_bleed_klaxon,
    "hull_breach": generate_hull_breach_alarm,
    "target_lock": generate_target_lock_acquired,
    "cockpit_ambient": generate_cockpit_ambient_hum
}


def render_sfx_to_wav_bytes(sfx_name: str, sample_rate: int = 24000) -> Optional[bytes]:
    """Render procedural SFX to raw WAV bytes."""
    if sf is None or np is None:
        return None
    generator = SFX_LIBRARY.get(sfx_name)
    if not generator:
        return None
    try:
        samples = generator(sample_rate=sample_rate)
        buf = io.BytesIO()
        sf.write(buf, samples, sample_rate, format="WAV")
        return buf.getvalue()
    except Exception:
        return None


def generate_soundscape_markdown() -> List[str]:
    """Generate Full-Duplex Soundscape & Voice Matrix architecture reference document."""
    vault_sys_dir = os.path.join(BASE_DIR, "vault", "Eve Online", "System_Architecture")
    os.makedirs(vault_sys_dir, exist_ok=True)
    out_file = os.path.join(vault_sys_dir, "full_duplex_soundscape_voice_matrix.md")

    doc_md = """---
title: Autonomous EVE Online Full-Duplex VAD Voice Loop & Tactical Soundscape Matrix
category: System Architecture
tags: [EVE, VoiceAI, Soundboard, ProceduralAudio, VAD, FullDuplex, AudioDucking, CockpitAcoustics]
last_updated: 2026-08-14
---

# 🛸 Autonomous Full-Duplex VAD Voice Loop & Procedural Soundscape Matrix

This document establishes the procedural tactical sound effects generator, mathematical audio ducking engine, and full-duplex voice activity detection (VAD) state machine.

---

## 🔊 1. Procedural Cockpit Soundboard SFX Catalog (100% Pure NumPy)

| Sound Effect Key | Acoustic Formulation | Default Duration | Operational Purpose |
| :--- | :--- | :---: | :--- |
| `warp_spool` | Exponential sub-bass sweep ($55\\text{Hz} \\to 330\\text{Hz}$) + phase chorus | **$2.5\\text{s}$** | Spooling warp drive & cynosural jump transition |
| `shield_critical` | Pulsing dual-tone FM modulation ($1200\\text{Hz} \\leftrightarrow 850\\text{Hz}$) | **$1.8\\text{s}$** | Emergency shield collapse alarm |
| `armor_bleed` | Staccato dual-burst pulses ($550\\text{Hz} \\& 880\\text{Hz}$) | **$1.2\\text{s}$** | Armor layer penetration warning |
| `hull_breach` | Low dissonant square/sine drone ($110\\text{Hz} + 155.5\\text{Hz}$) | **$2.0\\text{s}$** | Catastrophic structural hull breach klaxon |
| `target_lock` | Ascending high-tech tri-tone ping ($1760\\text{Hz} \\to 3520\\text{Hz}$) | **$0.4\\text{s}$** | Fire-control radar lock acquisition |
| `cockpit_ambient` | Sub-bass reactor hum ($60\\text{Hz} + 120\\text{Hz}$) + ambient noise | **$5.0\\text{s}$ (Loop)** | Starship bridge background ambient atmosphere |

---

## 📉 2. Dynamic Audio Ducking Mathematics ($-14\\text{dB}$ Attenuation)

When AURA or fleet commanders speak, the ambient reactor hum is ducked via convolution smoothing:
$$\\text{Gain}(t) = 1.0 - 0.75 \\cdot \\mathbb{I}_{\\text{voice}}(t)$$
Smooth ramp transitions over $200\\text{ms}$ prevent digital clicks and acoustic clipping.

---

## 🎙️ 3. Full-Duplex Voice Activity Detection (VAD) State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> USER_SPEAKING : RMS > 0.015 & ZCR > 0.01 (>= 3 frames)
    IDLE --> AI_SPEAKING : TTS Audio Output Active
    AI_SPEAKING --> BARGE_IN_TRIGGERED : User Speaks (>= 3 frames)
    BARGE_IN_TRIGGERED --> USER_SPEAKING : Flush Audio Queue & Listen
    USER_SPEAKING --> IDLE : Silence (>= 8 frames)
    AI_SPEAKING --> IDLE : TTS Finished
```
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_soundscape_markdown()
    print(f"Generated soundscape document: {files}")

