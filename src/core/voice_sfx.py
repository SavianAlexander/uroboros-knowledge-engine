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
from typing import Dict, Any, Optional

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


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
    def synthesize_sfx(cls, sfx_name: str) -> bytes:
        """
        Generate crystalline audio cue by name.
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
            return b""

        if name in ("ready", "listening", "mic_on"):
            # Crystalline chime: C6 (1046.5 Hz) + E6 (1318.5 Hz) + G6 (1567.98 Hz)
            duration = 0.38
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            env = np.exp(-t * 9.5) * (1.0 - np.exp(-t * 400.0))  # 2.5ms attack, smooth ring decay
            f1, f2, f3 = 1046.50, 1318.51, 1567.98
            # Stereo Haas delay for spatial width
            left = (0.50 * np.sin(2 * np.pi * f1 * t) + 0.35 * np.sin(2 * np.pi * f2 * t) + 0.15 * np.sin(2 * np.pi * f3 * t)) * env
            right = (0.35 * np.sin(2 * np.pi * f1 * t) + 0.50 * np.sin(2 * np.pi * f2 * t) + 0.15 * np.sin(2 * np.pi * f3 * t)) * env

        elif name in ("confirm", "executing", "acknowledge"):
            # Upward holographic sweep (880 Hz -> 1760 Hz) with FM bell shimmer
            duration = 0.28
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            env = np.exp(-t * 8.0) * (1.0 - np.exp(-t * 300.0))
            freq = 880.0 + (1760.0 - 880.0) * (t / duration) ** 1.5
            mod = 0.2 * np.sin(2 * np.pi * 32.0 * t)  # 32Hz vibrato shimmer
            left = np.sin(2 * np.pi * freq * t + mod) * env * 0.7
            right = np.sin(2 * np.pi * freq * (t + 0.002) + mod) * env * 0.7

        elif name in ("complete", "done", "success"):
            # Warm dual bell cadence: Note 1 (D5 587.33 Hz) -> Note 2 (A5 880.00 Hz)
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
            # Spatial widening
            right = np.roll(left, int(sr * 0.008))

        elif name in ("alert", "ping", "warning"):
            # Tactical double-ping radar notification (1500 Hz)
            duration = 0.32
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            pulse1 = (t < 0.08) * np.exp(-t * 22.0) * np.sin(2 * np.pi * 1500 * t)
            t_sub = np.maximum(0, t - 0.10)
            pulse2 = (t >= 0.10) * np.exp(-t_sub * 14.0) * np.sin(2 * np.pi * 1800 * t_sub)
            sig = (pulse1 + pulse2) * 0.8
            left = sig
            right = sig

        elif name in ("dismiss", "stop", "mic_off"):
            # Downward soft crystal fade (1200 Hz -> 600 Hz)
            duration = 0.22
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            env = np.exp(-t * 12.0)
            freq = 1200.0 - (1200.0 - 600.0) * (t / duration)
            sig = np.sin(2 * np.pi * freq * t) * env * 0.6
            left = sig
            right = np.roll(sig, int(sr * 0.004))

        else:
            # Neutral soft tick
            duration = 0.05
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            sig = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 80.0) * 0.5
            left = sig
            right = sig

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
