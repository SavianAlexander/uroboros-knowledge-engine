"""
Universal Polyglot Neural Voice Bridge & Multi-Domain Audio Dispatcher.
Standard: Pure Python Standard Library (os, sys, json, time, threading).
Ponytail Senior Dev Principle: Domain-agnostic unified bridge serving DevOps, Tududi Productivity, Executive Briefs, and Gaming with zero overhead.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_voice_copilot import KokoroVoiceCopilot, KOKORO_PERSONAS
from src.infrastructure.eve_voice_dsp import process_tactical_dsp_pipeline
from src.infrastructure.eve_voice_soundboard import SFX_LIBRARY, render_sfx_to_wav_bytes
from src.infrastructure.eve_voice_mixer import composite_tactical_soundscape


DOMAIN_PROFILES = {
    "DEV_OPS": {
        "voice": "bm_george",
        "speed": 1.05,
        "dsp_preset": "STUDIO_DIRECT",
        "description": "Concise Developer & CI/CD Terminal Broadcaster"
    },
    "DAILY_BRIEF": {
        "voice": "af_bella",
        "speed": 1.00,
        "dsp_preset": "AURA_COCKPIT",
        "description": "Warm, engaging Task Master & Tududi Productivity Speaker"
    },
    "EXECUTIVE_ASSISTANT": {
        "voice": "bf_emma",
        "speed": 1.00,
        "dsp_preset": "AURA_COCKPIT",
        "description": "Authoritative, crystalline Executive Intelligence Voice"
    },
    "TACTICAL_COCKPIT": {
        "voice": "af_sarah",
        "speed": 1.10,
        "dsp_preset": "TACTICAL_RADIO",
        "description": "Military-grade Tactical Radar & Combat Alert Voice"
    },
    "GENERAL": {
        "voice": "bf_emma",
        "speed": 1.00,
        "dsp_preset": "STUDIO_DIRECT",
        "description": "Universal Multi-Purpose Neural Synthesizer"
    }
}


class VoiceBridge:
    """Universal Domain-Agnostic Voice Engine Bridge."""

    _instance = None
    _copilot = None

    @classmethod
    def get_copilot(cls) -> KokoroVoiceCopilot:
        if cls._copilot is None:
            cls._copilot = KokoroVoiceCopilot()
        return cls._copilot

    @classmethod
    def speak(
        cls,
        text: str,
        domain: str = "GENERAL",
        priority: str = "NORMAL",
        voice: Optional[str] = None,
        dsp_preset: Optional[str] = None,
        sfx_intro: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Universal 1-line speech dispatcher for any agent, script, or workflow.
        """
        copilot = cls.get_copilot()
        profile = DOMAIN_PROFILES.get(domain.upper(), DOMAIN_PROFILES["GENERAL"])

        selected_voice = voice or profile["voice"]
        selected_dsp = dsp_preset or profile["dsp_preset"]

        # If sfx_intro requested, play SFX first
        if sfx_intro and sfx_intro in SFX_LIBRARY:
            copilot.speak(f"[{sfx_intro}]", priority="INFO", force_sapi=True)

        rec = copilot.speak(
            text=text,
            priority=priority,
            voice=selected_voice
        )
        rec["domain"] = domain
        rec["dsp_preset"] = selected_dsp
        return rec

    @classmethod
    def synthesize_bytes(
        cls,
        text: str,
        voice: str = "bf_emma",
        speed: float = 1.0,
        response_format: str = "wav"
    ) -> Optional[bytes]:
        """Synthesize raw audio bytes (OpenAI compatible)."""
        copilot = cls.get_copilot()
        return copilot.synthesize_neural_audio(text, voice=voice, speed=speed, response_format=response_format)

    @classmethod
    def play_sfx(cls, sfx_name: str) -> Optional[bytes]:
        """Synthesize and return procedural SFX audio bytes."""
        return render_sfx_to_wav_bytes(sfx_name)

    @classmethod
    def announce_ci_pipeline_status(cls, workflow_name: str, passed: bool = True) -> Dict[str, Any]:
        """DevOps Helper: Speak CI pipeline test result."""
        status_text = "succeeded with 100 percent pass rate" if passed else "failed tests"
        msg = f"DevOps Notice: GitHub Actions workflow {workflow_name} {status_text}."
        priority = "NORMAL" if passed else "CRITICAL"
        return cls.speak(msg, domain="DEV_OPS", priority=priority)

    @classmethod
    def announce_tududi_daily_brief(cls, pending_count: int, completed_today: int) -> Dict[str, Any]:
        """Productivity Helper: Speak Tududi daily briefing."""
        msg = (
            f"Good day Savian. Tududi Task Master report: You have completed {completed_today} tasks today, "
            f"with {pending_count} pending action items remaining on your dashboard."
        )
        return cls.speak(msg, domain="DAILY_BRIEF", priority="NORMAL")

    @classmethod
    def get_supported_personas(cls) -> Dict[str, str]:
        """Return available voice personas."""
        return KOKORO_PERSONAS

    @classmethod
    def get_domain_profiles(cls) -> Dict[str, Any]:
        """Return registered domain profiles."""
        return DOMAIN_PROFILES
