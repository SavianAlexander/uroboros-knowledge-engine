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

DEFAULT_CANONICAL_VOICE = "af_heart"
DEFAULT_CANONICAL_SPEED = 1.02
DEFAULT_CANONICAL_DSP = "STUDIO_MASTER"

CANONICAL_VOICE_PROFILE = {
    "voice": "af_heart",
    "speed": 1.02,
    "dsp_preset": "STUDIO_MASTER",
    "description": "Universal Singular Canonical Synthesizer (af_heart Studio Master)"
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
        blocking: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Universal 1-line speech dispatcher for any agent, script, or workflow.
        Zero-disk in-memory playback path using the singular canonical voice profile.
        """
        copilot = cls.get_copilot()
        selected_voice = voice or CANONICAL_VOICE_PROFILE["voice"]
        selected_dsp = dsp_preset or CANONICAL_VOICE_PROFILE["dsp_preset"]

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
        speed: float = 1.02,
        sync: bool = False
    ) -> Dict[str, Any]:
        """Ultra-low latency instant voice dispatch (<1ms cached, <25ms fresh)."""
        from src.core.instant_audio_streamer import InstantVoiceClient
        v = voice or "af_heart"
        d = dsp_preset or "STUDIO_MASTER"
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
        voice: str = "af_heart",
        speed: float = 1.02,
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
            return VoiceSFX.synthesize_sfx(sfx_name)
        except Exception:
            return None


    @classmethod
    def announce_ci_pipeline_status(cls, workflow_name: str, passed: bool = True) -> Dict[str, Any]:
        """DevOps Helper: Speak CI pipeline test result."""
        status_text = "succeeded with 100 percent pass rate" if passed else "failed tests"
        msg = f"DevOps Notice: GitHub Actions workflow {workflow_name} {status_text}."
        priority = "NORMAL" if passed else "CRITICAL"
        return cls.speak(msg, domain="DEV_OPS", priority=priority)
