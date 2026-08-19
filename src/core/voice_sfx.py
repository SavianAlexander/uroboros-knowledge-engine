"""
Autonomous Pure-Mathematical Crystalline SFX & Earcon Synthesizer.
Standard: Pure Python Standard Library (math, struct, wave, io) + NumPy.
Ponytail Senior Dev Principle: 100% internal, mathematical synthesis of Cortana holographic chimes, tactical pings, and UI feedback without external audio sample files.
"""

import os
import sys
import math
import struct
import io
from typing import Dict, Any, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def _sfx_crystalline_chime(sr: int) -> Tuple[Any, Any]:
    duration = 0.38
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    env = np.exp(-t * 9.5) * (1.0 - np.exp(-t * 400.0))  # 2.5ms attack, smooth ring decay
    f1, f2, f3 = 1046.50, 1318.51, 1567.98
    left = (0.50 * np.sin(2 * np.pi * f1 * t) + 0.35 * np.sin(2 * np.pi * f2 * t) + 0.15 * np.sin(2 * np.pi * f3 * t)) * env
    right = (0.35 * np.sin(2 * np.pi * f1 * t) + 0.50 * np.sin(2 * np.pi * f2 * t) + 0.15 * np.sin(2 * np.pi * f3 * t)) * env
    return left, right


def _sfx_holographic_sweep(sr: int) -> Tuple[Any, Any]:
    duration = 0.28
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    env = np.exp(-t * 8.0) * (1.0 - np.exp(-t * 300.0))
    freq = 880.0 + (1760.0 - 880.0) * (t / duration) ** 1.5
    mod = 0.2 * np.sin(2 * np.pi * 32.0 * t)  # 32Hz vibrato shimmer
    left = np.sin(2 * np.pi * freq * t + mod) * env * 0.7
    right = np.sin(2 * np.pi * freq * (t + 0.002) + mod) * env * 0.7
    return left, right


def _sfx_dual_bell(sr: int) -> Tuple[Any, Any]:
    duration = 0.45
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    t1 = t[t < 0.12]
    t2 = t[t >= 0.12] - 0.12
    env1 = np.exp(-t[t < 0.12] * 12.0)
    env2 = np.exp(-t2 * 6.5)

    sig1 = (0.6 * np.sin(2 * np.pi * 587.33 * t1) + 0.2 * np.sin(2 * np.pi * 1174.66 * t1)) * env1
    sig2 = (0.7 * np.sin(2 * np.pi * 880.00 * t2) + 0.3 * np.sin(2 * np.pi * 1760.00 * t2)) * env2
    combined = np.concatenate([sig1, sig2])
    left = combined * 0.75
    right = np.roll(left, int(sr * 0.008))
    return left, right


def _sfx_radar_double_ping(sr: int) -> Tuple[Any, Any]:
    duration = 0.32
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    pulse1 = (t < 0.08) * np.exp(-t * 22.0) * np.sin(2 * np.pi * 1500 * t)
    t_sub = np.maximum(0, t - 0.10)
    pulse2 = (t >= 0.10) * np.exp(-t_sub * 14.0) * np.sin(2 * np.pi * 1800 * t_sub)
    sig = (pulse1 + pulse2) * 0.8
    return sig, sig


def _sfx_downward_fade(sr: int) -> Tuple[Any, Any]:
    duration = 0.22
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    env = np.exp(-t * 12.0)
    freq = 1200.0 - (1200.0 - 600.0) * (t / duration)
    sig = np.sin(2 * np.pi * freq * t) * env * 0.6
    left = sig
    right = np.roll(sig, int(sr * 0.004))
    return left, right


def _sfx_neutral_tick(sr: int) -> Tuple[Any, Any]:
    duration = 0.05
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sig = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 80.0) * 0.5
    return sig, sig


_SFX_GENERATORS: Dict[str, Any] = {
    "ready": _sfx_crystalline_chime,
    "listening": _sfx_crystalline_chime,
    "mic_on": _sfx_crystalline_chime,
    "chime": _sfx_crystalline_chime,
    "confirm": _sfx_holographic_sweep,
    "executing": _sfx_holographic_sweep,
    "acknowledge": _sfx_holographic_sweep,
    "sweep": _sfx_holographic_sweep,
    "complete": _sfx_dual_bell,
    "done": _sfx_dual_bell,
    "success": _sfx_dual_bell,
    "bell": _sfx_dual_bell,
    "alert": _sfx_radar_double_ping,
    "ping": _sfx_radar_double_ping,
    "warning": _sfx_radar_double_ping,
    "target_lock": _sfx_radar_double_ping,
    "dismiss": _sfx_downward_fade,
    "stop": _sfx_downward_fade,
    "mic_off": _sfx_downward_fade,
}


class VoiceSFX:
    """
    Mathematical synthesis of Cortana-grade UI chimes, alerts, and earcons.
    All sounds are generated procedurally as 24kHz stereo 16-bit PCM WAV.
    """

    SAMPLE_RATE = 24000
    _sfx_cache: Dict[str, bytes] = {}

    @classmethod
    def _create_wav_header(cls, num_samples: int, num_channels: int = 2, sample_rate: int = 24000) -> bytes:
        """Create standard 44-byte RIFF WAV header."""
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
        block_align = num_channels * (bits_per_sample // 8)
        data_size = num_samples * block_align
        file_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            file_size,
            b"WAVE",
            b"fmt ",
            16,
            1,  # PCM
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size
        )
        return header

    @classmethod
    def _synthesize_sfx_pure_python(cls, name: str, sr: int) -> bytes:
        """Pure standard library math fallback wave synthesizer when numpy is absent."""
        duration = 0.35
        num_samples = int(sr * duration)
        raw_frames = bytearray()
        
        for i in range(num_samples):
            t = i / sr
            env = math.exp(-t * 9.5) * (1.0 - math.exp(-t * 400.0)) if t > 0 else 0.0
            # Crystalline chord tone synthesis
            sig_l = (0.50 * math.sin(2 * math.pi * 1046.50 * t) + 0.35 * math.sin(2 * math.pi * 1318.51 * t) + 0.15 * math.sin(2 * math.pi * 1567.98 * t)) * env
            sig_r = (0.35 * math.sin(2 * math.pi * 1046.50 * t) + 0.50 * math.sin(2 * math.pi * 1318.51 * t) + 0.15 * math.sin(2 * math.pi * 1567.98 * t)) * env
            
            val_l = max(-32767, min(32767, int(sig_l * 32767.0 * 0.95)))
            val_r = max(-32767, min(32767, int(sig_r * 32767.0 * 0.95)))
            raw_frames.extend(struct.pack("<hh", val_l, val_r))
            
        header = cls._create_wav_header(num_samples, num_channels=2, sample_rate=sr)
        return header + bytes(raw_frames)

    @classmethod
    def synthesize_sfx(cls, sfx_name: str) -> bytes:
        """
        Generate crystalline audio cue by name via O(1) generator dispatch.
        Available:
        - 'ready' / 'listening': Dual harmonic crystal chime (C6 + E6)
        - 'confirm' / 'executing': Upward FM holographic sweep
        - 'complete' / 'done': Warm dual bell cadence (D5 -> A5)
        - 'alert' / 'ping': Tactical dual-ping radar notification
        - 'dismiss' / 'stop': Downward soft crystal fade
        """
        name = sfx_name.lower().strip()
        if name in cls._sfx_cache:
            return cls._sfx_cache[name]

        sr = cls.SAMPLE_RATE
        if np is None:
            wav_bytes = cls._synthesize_sfx_pure_python(name, sr)
            cls._sfx_cache[name] = wav_bytes
            return wav_bytes

        gen = _SFX_GENERATORS.get(name, _sfx_neutral_tick)
        left, right = gen(sr)

        # Interleave stereo int16 PCM
        stereo = np.column_stack((left, right))
        stereo = np.clip(stereo, -0.95, 0.95)
        pcm16 = (stereo * 32767.0).astype(np.int16)
        raw_pcm = pcm16.tobytes()

        header = cls._create_wav_header(len(pcm16), num_channels=2, sample_rate=sr)
        wav_bytes = header + raw_pcm

        cls._sfx_cache[name] = wav_bytes
        return wav_bytes

    @classmethod
    def play_sfx(cls, sfx_name: str, blocking: bool = False):
        """Play procedural crystalline SFX locally via Win32 in-memory driver."""
        wav_bytes = cls.synthesize_sfx(sfx_name)
        if not wav_bytes or sys.platform != "win32":
            return

        try:
            import winsound
            flags = winsound.SND_MEMORY | winsound.SND_NODEFAULT
            if not blocking:
                flags |= winsound.SND_ASYNC
            else:
                flags |= winsound.SND_SYNC
            winsound.PlaySound(wav_bytes, flags)
        except Exception:
            pass

    @classmethod
    def prewarm_all(cls):
        """Pre-synthesizes all procedural SFX waveforms into RAM for true 0.0ms trigger latency."""
        for sfx_key in _SFX_GENERATORS:
            cls.synthesize_sfx(sfx_key)


# Instant 0.0ms warm cache initialization
try:
    VoiceSFX.prewarm_all()
except Exception:
    pass
