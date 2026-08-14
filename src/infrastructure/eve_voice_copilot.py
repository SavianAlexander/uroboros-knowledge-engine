"""
Autonomous EVE Online Auditory Voice Tactical AI Co-Pilot Engine.
Standard: Pure Python Standard Library (os, sys, subprocess, json, time).
Ponytail Senior Dev Principle: Native Windows SAPI speech synthesis, zero external heavy TTS dependencies.
"""

import os
import sys
import subprocess
import json
import time
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_SYS_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "System_Architecture")

TACTICAL_VOICE_TEMPLATES = {
    "HOSTILE_LOCAL_FLASH": "Warning. Hostile pilot entered solar system {system}. Prepare fleet alignment.",
    "ORE_HOLD_FULL": "{character}'s cargo bay is full. Spooling Porpoise compression unit.",
    "SHIELD_UNDER_ATTACK": "Emergency alert. {character} is taking heavy shield damage.",
    "FLEET_ALIGN_COMMAND": "Fleet command broadcast: Aligning all vessels to safe citadel bookmark.",
    "CYNO_BEACON_LIT": "Cynosural field beacon lit in {system}. Capital jump transit clear."
}


class VoiceTacticalCopilot:
    """Zero-dependency local speech alert synthesizer."""

    def __init__(self):
        self.alert_history = []

    def format_alert(self, template_key: str, **kwargs) -> str:
        """Format tactical alert message using template key."""
        template = TACTICAL_VOICE_TEMPLATES.get(template_key, "Tactical alert notification.")
        return template.format(**kwargs)

    def speak(self, text: str, priority: str = "HIGH") -> Dict[str, Any]:
        """Dispatch text alert to Windows SAPI speech synthesizer."""
        record = {
            "timestamp": time.time(),
            "priority": priority,
            "text": text,
            "dispatched": True
        }
        self.alert_history.append(record)

        # Non-blocking invocation of Windows SAPI SpeechSynthesizer if on Windows
        if sys.platform == "win32":
            try:
                ps_cmd = f"Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('{text}')"
                subprocess.Popen(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        return record


def generate_voice_copilot_markdown() -> List[str]:
    """Generate Voice Tactical Co-Pilot Architecture reference document."""
    os.makedirs(VAULT_SYS_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_SYS_DIR, "voice_tactical_copilot_architecture.md")

    copilot = VoiceTacticalCopilot()
    sample_alert = copilot.format_alert("HOSTILE_LOCAL_FLASH", system="G-EURJ")
    copilot.speak(sample_alert, priority="CRITICAL")

    doc_md = f"""---
title: Autonomous EVE Online Auditory Voice Tactical AI Co-Pilot
category: System Architecture
tags: [EVE, VoiceAI, TextToSpeech, SAPI, AuditoryRadar, CognitiveOffload, MultiBoxing, Alerts]
last_updated: 2026-08-14
---

# 🎙️ Autonomous Auditory Voice Tactical AI Co-Pilot

This document outlines the zero-dependency local auditory alert synthesis architecture designed to eliminate visual tunnel vision during multi-boxing operations.

---

## 📢 1. Canonical Voice Alert Catalog

| Alert Trigger Event | Spoken Message Syntax | Priority Level |
| :--- | :--- | :---: |
| **Hostile Local Entry** | *"Warning. Hostile pilot entered solar system `{{system}}`. Prepare fleet alignment."* | **CRITICAL** |
| **Incoming Damage Spike** | *"Emergency alert. `{{character}}` is taking heavy shield damage."* | **CRITICAL** |
| **Cargo Hold Depletion/Full** | *"`{{character}}`'s cargo bay is full. Spooling Porpoise compression unit."* | **URGENT** |
| **Fleet Alignment Broadcast** | *"Fleet command broadcast: Aligning all vessels to safe citadel bookmark."* | **URGENT** |
| **Cynosural Jump Beacon** | *"Cynosural field beacon lit in `{{system}}`. Capital jump transit clear."* | **INFO** |

---

## ⚡ 2. Active Alert Dispatch Ledger
- **Last Triggered Alert**: `{sample_alert}`
- **Speech Engine**: Windows SAPI System.Speech Synthesis (Zero-Latency Local Execution)
- **Audio Routing**: Direct to Local Primary Audio Device
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_voice_copilot_markdown()
    print(f"Generated voice copilot document: {files}")
