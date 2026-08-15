"""
EVE Fleet Tactical Voice Broadcast Matrix & Combat Comms Synthesizer.
Standard: Pure Python Standard Library (json, os, sys, time, typing).
Ponytail Senior Dev Principle: Generates tactical combat, cyno, warp bubble, and fleet compression voice alerts with acoustic DSP mastering.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, KOKORO_PERSONAS
from src.core.voice_dsp import VoiceDSP
from src.core.voice_normalizer import VoiceNormalizer
from src.core.audit_hashchain import GLOBAL_AUDIT_HASHCHAIN

FLEET_TACTICAL_TEMPLATES = {
    "CYNO_BEACON_ACTIVE": {
        "text": "Alert. Cynosural beacon lit in solar system {system}. Hostile capital jump bridge signature detected.",
        "persona": "TACTICAL_ADVISOR",
        "dsp": "COMMANDER_TACTICAL",
        "priority": "CRITICAL"
    },
    "INTERDICTOR_BUBBLE_DROP": {
        "text": "Warp disruption field deployed. Bubble radius 20 kilometers. Align to celestial exit vector.",
        "persona": "TACTICAL_ADVISOR",
        "dsp": "COMMANDER_TACTICAL",
        "priority": "CRITICAL"
    },
    "MINING_COMPRESSION_CYCLE": {
        "text": "Pillar of Autumn industrial core active in G-EURJ. Asteroid ore compression cycle complete. Capacity available.",
        "persona": "INDUSTRY_OVERSEER",
        "dsp": "AWE_STUDIO_MASTER",
        "priority": "NORMAL"
    },
    "FLEET_ANCHOR_COMMAND": {
        "text": "All fleet wings: anchor on Fleet Commander flagship. Overheat propulsion modules and lock primary broadcast target.",
        "persona": "FLEET_COMMANDER",
        "dsp": "SOVEREIGN_PRESENCE",
        "priority": "HIGH"
    },
    "GATECAMP_THREAT_INTERCEPT": {
        "text": "Directional scan warning in {system}. Heavy interdictor and recon cruiser signatures at stargate perimeter.",
        "persona": "AURA_SHIP_AI",
        "dsp": "TRANSCENDENTAL_AURA",
        "priority": "HIGH"
    }
}


class EVEFleetTacticalVoice:
    """Dispatches tactical combat broadcasts and fleet status voice communications."""

    @classmethod
    def get_tactical_templates(cls) -> Dict[str, Any]:
        """Return catalog of tactical fleet broadcast templates."""
        return FLEET_TACTICAL_TEMPLATES

    @classmethod
    def broadcast_tactical_alert(
        cls,
        alert_type: str,
        system: str = "G-EURJ",
        speak_now: bool = True
    ) -> Dict[str, Any]:
        """Synthesize and broadcast tactical voice alert with tailored DSP mastering."""
        template = FLEET_TACTICAL_TEMPLATES.get(alert_type.upper(), FLEET_TACTICAL_TEMPLATES["CYNO_BEACON_ACTIVE"])
        raw_text = template["text"].format(system=system)
        clean_text = VoiceNormalizer.normalize_for_speech(raw_text)
        
        voice_id = KOKORO_PERSONAS.get(template["persona"], "af_sarah")
        dsp_preset = template["dsp"]
        priority = template["priority"]

        t0 = time.time()
        dispatch_res = {}
        if speak_now:
            dispatch_res = VoiceBridge.speak(
                text=clean_text,
                domain="EVE_TACTICAL",
                priority=priority,
                voice=voice_id,
                dsp_preset=dsp_preset
            )

        GLOBAL_AUDIT_HASHCHAIN.append_event(
            event_type="EVE_TACTICAL_BROADCAST",
            payload={"alert_type": alert_type, "system": system, "text": clean_text},
            actor="FLEET_TACTICAL_VOICE"
        )

        return {
            "status": "tactical_alert_broadcast",
            "alert_type": alert_type,
            "system": system,
            "text": clean_text,
            "persona": template["persona"],
            "dsp_preset": dsp_preset,
            "priority": priority,
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "dispatch": dispatch_res
        }
