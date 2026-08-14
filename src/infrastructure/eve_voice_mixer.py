"""
Autonomous EVE Online Dynamic Multi-Track Audio Mixer & Soundscape Ducking Engine.
Standard: Pure Python Standard Library + NumPy.
Ponytail Senior Dev Principle: Exact mathematical audio ducking (-14dB attenuation envelope) and multi-channel soundscape compositing.
"""

import os
import sys
import numpy as np
import io
import soundfile as sf
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_voice_soundboard import SFX_LIBRARY


def apply_audio_ducking(
    ambient_track: np.ndarray,
    voice_track: np.ndarray,
    duck_gain: float = 0.20,  # -14 dB attenuation
    ramp_samples: int = 4800  # 200ms smooth transition at 24kHz
) -> np.ndarray:
    """
    Calculate dynamic audio ducking envelope: attenuates ambient track while voice track is active.
    """
    target_length = max(len(ambient_track), len(voice_track))
    # Pad ambient track if necessary
    if len(ambient_track) < target_length:
        repeats = int(np.ceil(target_length / len(ambient_track)))
        ambient_padded = np.tile(ambient_track, repeats)[:target_length]
    else:
        ambient_padded = ambient_track[:target_length].copy()

    # Calculate voice energy envelope
    voice_padded = np.zeros(target_length, dtype=np.float32)
    voice_padded[:len(voice_track)] = voice_track

    is_speaking = np.abs(voice_padded) > 0.01

    # Generate smooth gain curve
    gain_curve = np.ones(target_length, dtype=np.float32)
    gain_curve[is_speaking] = duck_gain

    # Smooth the gain curve using a simple moving average window
    window = np.ones(ramp_samples) / ramp_samples
    smooth_gain = np.convolve(gain_curve, window, mode='same')

    ducked_ambient = ambient_padded * smooth_gain
    return ducked_ambient


def composite_tactical_soundscape(
    voice_samples: Optional[np.ndarray] = None,
    sfx_type: Optional[str] = None,
    include_ambient: bool = True,
    sample_rate: int = 24000
) -> np.ndarray:
    """
    Composite Voice + Tactical SFX + Ambient Reactor Drone into a unified master audio track.
    """
    # 1. Base Voice Track
    if voice_samples is not None:
        v_track = voice_samples.astype(np.float32)
    else:
        v_track = np.zeros(sample_rate * 2, dtype=np.float32)

    total_len = len(v_track)

    # 2. SFX Track (if specified)
    sfx_track = np.zeros(total_len, dtype=np.float32)
    if sfx_type and sfx_type in SFX_LIBRARY:
        sfx_data = SFX_LIBRARY[sfx_type](sample_rate=sample_rate)
        if len(sfx_data) > total_len:
            # Expand master length
            total_len = len(sfx_data)
            v_padded = np.zeros(total_len, dtype=np.float32)
            v_padded[:len(v_track)] = v_track
            v_track = v_padded
            sfx_track = sfx_data
        else:
            sfx_track[:len(sfx_data)] = sfx_data

    # 3. Ambient Cockpit Hum
    if include_ambient:
        ambient_raw = SFX_LIBRARY["cockpit_ambient"](sample_rate=sample_rate, duration_s=5.0)
        ducked_ambient = apply_audio_ducking(ambient_raw, v_track, duck_gain=0.25)
        if len(ducked_ambient) < total_len:
            repeats = int(np.ceil(total_len / len(ducked_ambient)))
            ducked_ambient = np.tile(ducked_ambient, repeats)[:total_len]
        else:
            ducked_ambient = ducked_ambient[:total_len]
    else:
        ducked_ambient = np.zeros(total_len, dtype=np.float32)

    # 4. Master Composite Summation & Soft Limiter
    master = v_track * 0.95 + sfx_track * 0.70 + ducked_ambient * 0.40
    # Soft saturation limiter to prevent digital clipping
    master_limited = np.tanh(master) * 0.98

    return master_limited.astype(np.float32)
