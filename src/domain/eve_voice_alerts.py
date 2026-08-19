"""
Autonomous EVE Online Tactical Voice Alerts & Dogma Warning Templates.
Standard: Pure Python Standard Library (re, json, os, sys, time).
Ponytail Senior Dev Principle: Isolated domain templates and formatting rules for high-stakes cockpit alerts.
"""

import os
import sys
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer


TACTICAL_VOICE_TEMPLATES = {
    "WARP_DRIVE_ACTIVE": "Warp drive active. Destination: {destination}.",
    "DOCKING_ACCEPTED": "Docking request accepted. Welcome to {station}.",
    "SHIELD_WARNING": "Warning! Shield integrity at {percent} percent.",
    "ARMOR_WARNING": "Warning! Armor integrity at {percent} percent.",
    "HULL_CRITICAL": "Emergency! Structural integrity compromised. Hull at {percent} percent.",
    "HOSTILE_DETECTED": "Hostile contact detected in local space. Pilot: {pilot}.",
    "FLEET_WARP": "Fleet warp initiated to {target}.",
    "CARGO_FULL": "Mining hold capacity reached at {percent} percent.",
    "CYNO_BEACON_LIT": "Cynosural field beacon lit in {system}. Capital jump transit clear."
}


class EVEVoiceAlertManager:
    """Formats and dispatches specialized EVE tactical voice alerts."""

    @classmethod
    def format_alert(cls, template_key: str, **kwargs) -> str:
        """Format tactical alert message using template key with safe kwargs fallback."""
        template = TACTICAL_VOICE_TEMPLATES.get(template_key, "Tactical alert notification.")
        try:
            return template.format(**kwargs)
        except KeyError:
            msg = template
            for k, v in kwargs.items():
                msg = msg.replace(f"{{{k}}}", str(v))
            import re
            return re.sub(r'\{[a-zA-Z0-9_]+\}', 'designated target', msg)


    @classmethod
    def speak_alert(
        cls,
        template_key: str,
        priority: str = "HIGH",
        persona: str = "AURA_SHIP_AI",
        sfx_intro: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Format and speak a tactical alert through the voice bridge."""
        raw_msg = cls.format_alert(template_key, **kwargs)
        clean_msg = VoiceNormalizer.normalize_for_speech(raw_msg)
        voice = KOKORO_PERSONAS.get(persona, "bf_emma")
        return VoiceBridge.speak(
            text=clean_msg,
            domain="TACTICAL_COCKPIT",
            priority=priority,
            voice=voice,
            dsp_preset="COCKPIT_ACOUSTIC",
            sfx_intro=sfx_intro
        )
