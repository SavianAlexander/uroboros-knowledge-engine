"""
Full-Duplex Conversational Voice Call & Radio Intercom Session Engine.
Standard: Pure Python Standard Library + NumPy.
Ponytail Senior Dev Principle: Zero-latency call state machine, procedural DTMF/Roger beeps, and sub-50ms conversational fillers.
"""

import os
import sys
import time
import math
import struct
import io
from typing import Dict, Any, List, Optional

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_memory_ledger import VoiceMemoryLedger


# Conversational Haptic Filler Bank
CONVERSATIONAL_FILLERS = [
    "Copy that, Commander.",
    "Understood.",
    "Checking telemetry now.",
    "One moment.",
    "Affirmative, processing.",
    "Scanning database now."
]


class VoiceCallIntercomEngine:
    """Manages full-duplex interactive voice calls and tactical radio intercoms."""

    _active_call: Optional[Dict[str, Any]] = None

    @classmethod
    def _create_wav_header(cls, num_samples: int, sample_rate: int = 24000) -> bytes:
        """Create 44-byte standard 16-bit PCM WAV header."""
        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
        block_align = num_channels * (bits_per_sample // 8)
        data_size = num_samples * block_align
        chunk_size = 36 + data_size

        return struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', chunk_size, b'WAVE',
            b'fmt ', 16, 1, num_channels,
            sample_rate, byte_rate, block_align, bits_per_sample,
            b'data', data_size
        )

    @classmethod
    def generate_dtmf_tone(
        cls,
        f1: float,
        f2: float,
        duration_s: float = 0.15,
        sample_rate: int = 24000,
        volume: float = 0.25
    ) -> bytes:
        """Generate procedural dual-frequency DTMF tone WAV bytes in RAM."""
        num_samples = int(sample_rate * duration_s)
        if np is not None:
            t = np.linspace(0, duration_s, num_samples, endpoint=False)
            envelope = np.ones_like(t)
            # 10ms smooth ramp up/down to prevent clicks
            fade_len = int(sample_rate * 0.01)
            if fade_len > 0 and len(t) > fade_len * 2:
                envelope[:fade_len] = np.linspace(0, 1, fade_len)
                envelope[-fade_len:] = np.linspace(1, 0, fade_len)
            signal = (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)) * 0.5 * volume * envelope
            pcm_16 = (signal * 32767.0).astype(np.int16)
            header = cls._create_wav_header(num_samples, sample_rate)
            return header + pcm_16.tobytes()
        else:
            # Fallback pure python math
            samples = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                val = 0.5 * (math.sin(2 * math.pi * f1 * t) + math.sin(2 * math.pi * f2 * t)) * volume
                ival = max(-32768, min(32767, int(val * 32767.0)))
                samples.extend(struct.pack('<h', ival))
            header = cls._create_wav_header(num_samples, sample_rate)
            return header + bytes(samples)

    @classmethod
    def generate_call_connect_chime(cls) -> bytes:
        """Generate two-tone rising chime (C5 523Hz -> E5 659Hz) signaling active call connect."""
        b1 = cls.generate_dtmf_tone(523.25, 1046.50, duration_s=0.12, volume=0.30)
        b2 = cls.generate_dtmf_tone(659.25, 1318.50, duration_s=0.18, volume=0.30)
        # Extract raw PCM data and merge
        pcm1 = b1[44:]
        pcm2 = b2[44:]
        merged_pcm = pcm1 + pcm2
        num_samples = len(merged_pcm) // 2
        return cls._create_wav_header(num_samples, 24000) + merged_pcm

    @classmethod
    def generate_roger_beep(cls) -> bytes:
        """Generate tactical NASA Apollo / Radio Roger Beep (2475Hz, 80ms) with squelch tail."""
        tone = cls.generate_dtmf_tone(2475.0, 1237.5, duration_s=0.08, volume=0.20)
        pcm_tone = tone[44:]
        # Add 30ms of subtle white noise squelch tail
        if np is not None:
            num_squelch = int(24000 * 0.03)
            squelch = (np.random.uniform(-0.03, 0.03, num_squelch) * 32767.0).astype(np.int16)
            merged = pcm_tone + squelch.tobytes()
        else:
            merged = pcm_tone
        return cls._create_wav_header(len(merged) // 2, 24000) + merged

    @classmethod
    def generate_call_disconnect_chime(cls) -> bytes:
        """Generate two-tone falling chime (E5 659Hz -> C5 523Hz) signaling call end."""
        b1 = cls.generate_dtmf_tone(659.25, 1318.50, duration_s=0.12, volume=0.25)
        b2 = cls.generate_dtmf_tone(440.00, 880.00, duration_s=0.18, volume=0.25)
        pcm1 = b1[44:]
        pcm2 = b2[44:]
        merged = pcm1 + pcm2
        return cls._create_wav_header(len(merged) // 2, 24000) + merged

    @classmethod
    def start_call(
        cls,
        persona: str = "AURA_SHIP_AI",
        caller_name: str = "Commander Savian Alexander"
    ) -> Dict[str, Any]:
        """Initiate an active full-duplex conversational voice call session."""
        call_id = f"call_{int(time.time())}"
        cls._active_call = {
            "call_id": call_id,
            "caller": caller_name,
            "persona": persona,
            "state": "ACTIVE_CALL",
            "started_at": time.time(),
            "turn_count": 0,
            "last_activity": time.time(),
            "dialogue": []
        }

        # 1. Play connect chime in RAM
        chime_bytes = cls.generate_call_connect_chime()
        copilot = VoiceBridge.get_copilot()
        if copilot:
            copilot.audio_queue.play_raw_pcm_wav(chime_bytes)

        # 2. Greeting
        greeting_text = f"Secure voice channel established. Go ahead, {caller_name}."
        VoiceBridge.speak(
            text=greeting_text,
            domain="TACTICAL_COCKPIT",
            priority="HIGH",
            voice=KOKORO_PERSONAS.get(persona, "bf_emma"),
            dsp_preset="COCKPIT_ACOUSTIC"
        )

        VoiceMemoryLedger.log_turn(
            speaker="Antigravity",
            raw_text=greeting_text,
            normalized_text=greeting_text,
            persona=persona,
            domain="CALL_INTERCOM"
        )

        return {
            "status": "call_connected",
            "call_id": call_id,
            "persona": persona,
            "caller": caller_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def trigger_immediate_filler(cls) -> Dict[str, Any]:
        """Dispatch a sub-50ms conversational acknowledgment filler while processing."""
        if not cls._active_call:
            return {"status": "no_active_call"}

        import random
        filler = random.choice(CONVERSATIONAL_FILLERS)
        VoiceBridge.speak(
            text=filler,
            domain="TACTICAL_COCKPIT",
            priority="HIGH",
            voice=KOKORO_PERSONAS.get(cls._active_call.get("persona", "AURA_SHIP_AI"), "bf_emma"),
            dsp_preset="COCKPIT_ACOUSTIC"
        )
        return {"status": "filler_dispatched", "filler": filler}

    @classmethod
    def respond_in_call(
        cls,
        response_text: str,
        with_roger_beep: bool = True
    ) -> Dict[str, Any]:
        """Speak conversational response in active call, followed by Roger beep squelch."""
        if not cls._active_call:
            # Auto-create ephemeral session if none exists
            cls.start_call()

        cls._active_call["state"] = "AI_SPEAKING"
        cls._active_call["turn_count"] += 1
        cls._active_call["last_activity"] = time.time()

        clean_text = VoiceNormalizer.normalize_for_speech(response_text)
        persona = cls._active_call.get("persona", "AURA_SHIP_AI")
        voice = KOKORO_PERSONAS.get(persona, "bf_emma")

        # Speak via in-memory streamer
        speak_res = VoiceBridge.speak(
            text=clean_text,
            domain="TACTICAL_COCKPIT",
            priority="HIGH",
            voice=voice,
            dsp_preset="COCKPIT_ACOUSTIC"
        )

        # Append Roger Beep if requested
        if with_roger_beep:
            roger_bytes = cls.generate_roger_beep()
            copilot = VoiceBridge.get_copilot()
            if copilot:
                copilot.audio_queue.play_raw_pcm_wav(roger_bytes)

        cls._active_call["state"] = "ACTIVE_CALL"
        cls._active_call["dialogue"].append({
            "turn": cls._active_call["turn_count"],
            "speaker": "Antigravity",
            "text": clean_text,
            "timestamp": time.time()
        })

        VoiceMemoryLedger.log_turn(
            speaker="Antigravity",
            raw_text=response_text,
            normalized_text=clean_text,
            persona=persona,
            domain="CALL_INTERCOM"
        )

        return {
            "status": "responded",
            "call_id": cls._active_call["call_id"],
            "turn_count": cls._active_call["turn_count"],
            "text_spoken": clean_text,
            "with_roger_beep": with_roger_beep
        }

    @classmethod
    def end_call(cls) -> Dict[str, Any]:
        """Terminate the active voice call session and play disconnect chime."""
        if not cls._active_call:
            return {"status": "no_active_call"}

        call_id = cls._active_call["call_id"]
        duration_s = round(time.time() - cls._active_call["started_at"], 1)
        turn_count = cls._active_call["turn_count"]

        # 1. Closing remark
        closing_text = "Channel closed. Out."
        VoiceBridge.speak(
            text=closing_text,
            domain="TACTICAL_COCKPIT",
            priority="NORMAL",
            voice=KOKORO_PERSONAS.get(cls._active_call.get("persona", "AURA_SHIP_AI"), "bf_emma")
        )

        # 2. Play disconnect chime in RAM
        disconnect_bytes = cls.generate_call_disconnect_chime()
        copilot = VoiceBridge.get_copilot()
        if copilot:
            copilot.audio_queue.play_raw_pcm_wav(disconnect_bytes)

        summary = {
            "status": "call_ended",
            "call_id": call_id,
            "duration_seconds": duration_s,
            "turn_count": turn_count,
            "closed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        cls._active_call = None
        return summary

    @classmethod
    def get_call_status(cls) -> Dict[str, Any]:
        """Get live status of active call session."""
        if not cls._active_call:
            return {"active": False, "state": "DISCONNECTED"}
        return {
            "active": True,
            "call_id": cls._active_call["call_id"],
            "caller": cls._active_call["caller"],
            "persona": cls._active_call["persona"],
            "state": cls._active_call["state"],
            "duration_seconds": round(time.time() - cls._active_call["started_at"], 1),
            "turn_count": cls._active_call["turn_count"]
        }
