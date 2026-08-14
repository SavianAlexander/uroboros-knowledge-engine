"""
Autonomous EVE Online Neural Voice Engine & Auditory Tactical AI Co-Pilot.
Standard: Pure Python Standard Library (os, sys, subprocess, json, time, urllib.request, urllib.parse).
Ponytail Senior Dev Principle: Seamless Docker container bridge + Windows SAPI hardware fallback, zero extra dependencies.
"""

import os
import sys
import subprocess
import json
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_SYS_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "System_Architecture")

# Environment endpoints
DEFAULT_CONTAINER_TTS_URL = os.getenv("TTS_ENGINE_URL", "http://127.0.0.1:5500/api/tts")
DEFAULT_VOICE_MODEL = os.getenv("VOICE_DEFAULT_VOICE", "piper:en_US-lessac-medium")

TACTICAL_VOICE_TEMPLATES = {
    "HOSTILE_LOCAL_FLASH": "Warning. Hostile pilot entered solar system {system}. Prepare fleet alignment.",
    "ORE_HOLD_FULL": "{character}'s cargo bay is full. Spooling Porpoise compression unit.",
    "SHIELD_UNDER_ATTACK": "Emergency alert. {character} is taking heavy shield damage.",
    "FLEET_ALIGN_COMMAND": "Fleet command broadcast: Aligning all vessels to safe citadel bookmark.",
    "CYNO_BEACON_LIT": "Cynosural field beacon lit in {system}. Capital jump transit clear."
}


class VoiceTacticalCopilot:
    """
    Dual-engine tactical voice synthesizer:
    - Tier 1: Containerized / Remote Neural TTS (OpenTTS / Piper / OpenedAI Speech)
    - Tier 2: Native Windows SAPI Hardware SpeechSynthesizer Fallback
    """

    def __init__(self, tts_url: Optional[str] = None, default_voice: Optional[str] = None):
        self.tts_url = tts_url or DEFAULT_CONTAINER_TTS_URL
        self.default_voice = default_voice or DEFAULT_VOICE_MODEL
        self.alert_history = []
        self.audio_cache: Dict[str, bytes] = {}

    def format_alert(self, template_key: str, **kwargs) -> str:
        """Format tactical alert message using template key."""
        template = TACTICAL_VOICE_TEMPLATES.get(template_key, "Tactical alert notification.")
        return template.format(**kwargs)

    def synthesize_neural_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Query containerized Neural TTS service to fetch binary PCM/WAV audio stream.
        """
        voice = voice or self.default_voice
        params = urllib.parse.urlencode({"voice": voice, "text": text})
        target_url = f"{self.tts_url}?{params}"

        try:
            req = urllib.request.Request(target_url, headers={"User-Agent": "NeuroAlexander-VoiceEngine/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    audio_data = resp.read()
                    self.audio_cache[text] = audio_data
                    return audio_data
        except Exception:
            # Neural container offline or unreachable; will fallback to OS SAPI
            pass
        return None

    def speak(self, text: str, priority: str = "HIGH", force_sapi: bool = False) -> Dict[str, Any]:
        """
        Dispatch tactical alert:
        Tries neural container synthesis first; falls back seamlessly to OS SAPI speech synthesizer.
        """
        audio_bytes = None
        engine_used = "Windows_SAPI"

        if not force_sapi:
            audio_bytes = self.synthesize_neural_audio(text)
            if audio_bytes:
                engine_used = "Neural_TTS_Container (Piper)"

        # Fallback to local desktop OS speech synthesizer
        if engine_used == "Windows_SAPI" and sys.platform == "win32":
            try:
                ps_cmd = f"Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('{text}')"
                subprocess.Popen(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        record = {
            "timestamp": time.time(),
            "priority": priority,
            "text": text,
            "engine": engine_used,
            "has_neural_audio": audio_bytes is not None,
            "neural_audio_bytes_len": len(audio_bytes) if audio_bytes else 0,
            "dispatched": True
        }
        self.alert_history.append(record)
        return record


def generate_voice_copilot_markdown() -> List[str]:
    """Generate Voice Tactical Co-Pilot Architecture reference document."""
    os.makedirs(VAULT_SYS_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_SYS_DIR, "voice_tactical_copilot_architecture.md")

    copilot = VoiceTacticalCopilot()
    sample_alert = copilot.format_alert("HOSTILE_LOCAL_FLASH", system="G-EURJ")
    record = copilot.speak(sample_alert, priority="CRITICAL")

    doc_md = f"""---
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
    Router --> Check{"Neural TTS Container Available? (port 5500)"}
    Check -- Yes --> Piper["Tier 1: Containerized Neural Voice (Piper / OpenTTS)<br>Studio-Grade PCM/WAV Audio Stream"]
    Check -- No / Timeout --> SAPI["Tier 2: Native Windows SAPI SpeechSynthesizer<br>Zero-Latency Local Desktop Spoken Output"]
    Piper --> Stream["Stream Audio to Web HUD / Playback Device"]
    SAPI --> Audio["Primary OS Audio Endpoint"]
```

---

## 📢 2. Canonical Voice Alert Catalog

| Alert Trigger Event | Spoken Message Syntax | Priority Level |
| :--- | :--- | :---: |
| **Hostile Local Entry** | *"Warning. Hostile pilot entered solar system `{{system}}`. Prepare fleet alignment."* | **CRITICAL** |
| **Incoming Damage Spike** | *"Emergency alert. `{{character}}` is taking heavy shield damage."* | **CRITICAL** |
| **Cargo Hold Depletion/Full** | *"`{{character}}`'s cargo bay is full. Spooling Porpoise compression unit."* | **URGENT** |
| **Fleet Alignment Broadcast** | *"Fleet command broadcast: Aligning all vessels to safe citadel bookmark."* | **URGENT** |
| **Cynosural Jump Beacon** | *"Cynosural field beacon lit in `{{system}}`. Capital jump transit clear."* | **INFO** |

---

## ⚡ 3. Active Alert Dispatch Ledger
- **Last Triggered Alert**: `{sample_alert}`
- **Active Engine**: `{record['engine']}`
- **Container Endpoint**: `{copilot.tts_url}` (Model: `{copilot.default_voice}`)
- **Fallback Engine**: Windows SAPI System.Speech Synthesis (Zero-Latency Local Execution)
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_voice_copilot_markdown()
    print(f"Generated voice copilot document: {files}")
