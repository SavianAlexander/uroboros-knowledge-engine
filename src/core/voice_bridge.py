"""
Universal Polyglot Neural Voice Bridge & Multi-Domain Audio Dispatcher.
Standard: Pure Python Standard Library (os, sys, json, time, threading).
Ponytail Senior Dev Principle: Domain-agnostic unified bridge serving DevOps, Tududi Productivity, Executive Briefs, Call Intercom, and Gaming with zero overhead.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from src.core.voice_engine import KokoroVoiceEngine
    KokoroVoiceCopilot = KokoroVoiceEngine  # Backward compatibility alias
except Exception:
    KokoroVoiceEngine = None
    KokoroVoiceCopilot = None

KOKORO_PERSONAS = {
    "CORTANA_PRIME": "af_sky",
    "AURA_SHIP_AI": "bf_emma",
    "EXECUTIVE_ADVISOR": "af_heart",
    "TACTICAL_OFFICER": "af_sarah",
    "TACTICAL_ADVISOR": "af_sarah",
    "FLEET_COMMANDER": "am_adam",
    "INDUSTRY_OVERSEER": "bm_george",
    "CALM_OPERATIONS": "af_bella",
    "EXECUTIVE_DIRECTOR": "af_heart",
    "WARP_NAVIGATOR": "bf_isabella",
    "ORACLE_ADVISOR": "af_sky",
    "SOVEREIGN_ORACLE": "af_sky",
    "KOKORO_SKY": "af_sky",
    "KOKORO_BELLA": "af_bella",
    "KOKORO_SARAH": "af_sarah",
    "KOKORO_EMMA": "bf_emma",
    "KOKORO_ADAM": "am_adam",
    "KOKORO_GEORGE": "bm_george"
}


DOMAIN_PROFILES = {
    "CORTANA_AI": {
        "voice": "af_sky",
        "speed": 1.02,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Cortana-Grade Neural AI Assistant & Master Broadcaster"
    },
    "DEV_OPS": {
        "voice": "af_sarah",
        "speed": 1.05,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Concise Developer & CI/CD Terminal Broadcaster"
    },
    "DAILY_BRIEF": {
        "voice": "af_heart",
        "speed": 1.00,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Warm, engaging Task Master & Tududi Productivity Speaker"
    },
    "EXECUTIVE_ASSISTANT": {
        "voice": "af_sky",
        "speed": 1.00,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Authoritative, crystalline Executive Intelligence Voice"
    },
    "TACTICAL_COCKPIT": {
        "voice": "af_sarah",
        "speed": 1.10,
        "dsp_preset": "TACTICAL_RADIO",
        "description": "Military-grade Tactical Radar & Combat Alert Voice"
    },
    "CALL_INTERCOM": {
        "voice": "af_sky",
        "speed": 1.05,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Real-Time Full-Duplex Phone Call & Radio Intercom Voice"
    },
    "GENERAL": {
        "voice": "af_sky",
        "speed": 1.00,
        "dsp_preset": "STUDIO_MASTER",
        "description": "Universal Multi-Purpose Neural Synthesizer"
    }
}



class VoiceBridge:
    """Universal Domain-Agnostic Voice Engine Bridge."""

    _instance = None
    _copilot = None

    @classmethod
    def get_copilot(cls) -> Optional[KokoroVoiceCopilot]:
        if cls._copilot is None and KokoroVoiceCopilot is not None:
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
        sfx_intro: Optional[str] = None,
        blocking: bool = False
    ) -> Dict[str, Any]:
        """
        Universal 1-line speech dispatcher for any agent, script, or workflow.
        Zero-disk in-memory playback path.
        """
        copilot = cls.get_copilot()
        profile = DOMAIN_PROFILES.get(domain.upper(), DOMAIN_PROFILES["GENERAL"])

        raw_voice = voice or profile["voice"]
        selected_voice = KOKORO_PERSONAS.get(raw_voice, raw_voice)
        selected_dsp = dsp_preset or profile["dsp_preset"]

        if copilot:
            rec = copilot.speak(
                text=text,
                priority=priority,
                voice=selected_voice,
                dsp_preset=selected_dsp,
                sfx_intro=sfx_intro,
                blocking=blocking
            )
        else:
            rec = {
                "status": "fallback_logged",
                "priority": priority,
                "text": text,
                "voice": selected_voice,
                "engine": "Offline_Fallback"
            }

        rec["domain"] = domain
        rec["dsp_preset"] = selected_dsp
        return rec

    @classmethod
    def speak_instant(
        cls,
        text: str,
        voice: Optional[str] = None,
        dsp_preset: Optional[str] = None,
        speed: float = 1.0,
        sync: bool = False
    ) -> Dict[str, Any]:
        """Ultra-low latency instant voice dispatch (<1ms cached, <25ms fresh)."""
        from src.core.instant_audio_streamer import InstantVoiceClient
        v = voice or "bf_emma"
        d = dsp_preset or "HOLOGRAPHIC_AURA"
        return InstantVoiceClient.speak_instant(text, voice=v, dsp_preset=d, speed=speed, sync=sync)

    @classmethod
    def pre_warm(cls):
        """Pre-warm ONNX weights and tactical phrase cache in RAM."""
        from src.core.instant_audio_streamer import InstantVoiceClient
        InstantVoiceClient.pre_warm_tactical_phrases()

    @classmethod
    def purge_current_speech(cls) -> Dict[str, Any]:
        """Instantly stop active audio playback and clear pending queues (barge-in cutoff)."""
        from src.core.instant_audio_streamer import get_instant_streamer
        get_instant_streamer().purge_and_interrupt()
        copilot = cls.get_copilot()
        if copilot:
            copilot.purge_playback()
        return {"status": "purged", "timestamp": time.time()}

    @classmethod
    def synthesize_bytes(
        cls,
        text: str,
        voice: str = "CORTANA_PRIME",
        speed: float = 1.0,
        response_format: str = "wav",
        dsp_preset: Optional[str] = "STUDIO_MASTER"
    ) -> Optional[bytes]:
        """Synthesize raw audio bytes (OpenAI compatible)."""
        copilot = cls.get_copilot()
        if copilot:
            return copilot.synthesize_neural_audio(
                text,
                voice=voice,
                speed=speed,
                response_format=response_format,
                dsp_preset=dsp_preset
            )
        return None

    synthesize_speech_bytes = synthesize_bytes


    @classmethod
    def play_sfx(cls, sfx_name: str) -> Optional[bytes]:
        """Synthesize and return procedural SFX audio bytes."""
        try:
            from src.core.voice_sfx import VoiceSFX
            sfx_bytes = VoiceSFX.synthesize_sfx(sfx_name)
            if not sfx_bytes:
                from src.infrastructure.eve_voice_soundboard import render_sfx_to_wav_bytes
                sfx_bytes = render_sfx_to_wav_bytes(sfx_name)
            return sfx_bytes
        except Exception:
            return None


    @classmethod
    def announce_ci_pipeline_status(cls, workflow_name: str, passed: bool = True) -> Dict[str, Any]:
        """DevOps Helper: Speak CI pipeline test result."""
        status_text = "succeeded with 100 percent pass rate" if passed else "failed tests"
        msg = f"DevOps Notice: GitHub Actions workflow {workflow_name} {status_text}."
        priority = "NORMAL" if passed else "CRITICAL"
        return cls.speak(msg, domain="DEV_OPS", priority=priority)
