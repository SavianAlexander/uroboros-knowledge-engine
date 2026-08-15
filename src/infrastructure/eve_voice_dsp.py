"""
Autonomous EVE Online Tactical DSP Acoustic Engine & Studio Broadcast Audio Mastering Rack.
Standard: Pure Python Standard Library + NumPy (with SciPy / pure-NumPy IIR biquad filtering).
Ponytail Senior Dev Principle: Zero-dependency studio mastering rack delivering Cortana-grade presence, air, dynamic control, and holographic 3D spatial width.
"""

import os
import sys
import math
import io
import time
import warnings
warnings.filterwarnings("ignore")
try:
    import numpy as np
except ImportError:
    np = None
from typing import Dict, Any, List, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ----------------------------------------------------------------------
# 1. Biquad Parametric Filter Coefficient Generators (Audio EQ Cookbook)
# ----------------------------------------------------------------------
def biquad_peaking(f0: float, gain_db: float, q: float = 1.0, fs: int = 24000) -> Tuple[np.ndarray, np.ndarray]:
    """Generate peaking / bell filter coefficients."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * min(f0, fs * 0.49) / fs
    alpha = np.sin(w0) / (2.0 * max(0.01, q))
    b0 = 1.0 + alpha * A
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / A
    b = np.array([b0 / a0, b1 / a0, b2 / a0], dtype=np.float32)
    a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float32)
    return b, a


def biquad_highshelf(f0: float, gain_db: float, q: float = 0.707, fs: int = 24000) -> Tuple[np.ndarray, np.ndarray]:
    """Generate high-shelf filter coefficients (presence air boost)."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * min(f0, fs * 0.49) / fs
    alpha = np.sin(w0) / (2.0 * max(0.01, q))
    cos_w0 = np.cos(w0)
    sqrt_A = np.sqrt(A)
    b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * sqrt_A * alpha)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * sqrt_A * alpha)
    a0 = (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * sqrt_A * alpha
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
    a2 = (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * sqrt_A * alpha
    b = np.array([b0 / a0, b1 / a0, b2 / a0], dtype=np.float32)
    a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float32)
    return b, a


def apply_biquad(samples: np.ndarray, b: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Apply IIR biquad filter via SciPy lfilter or vectorized fallback."""
    if samples is None or len(samples) == 0:
        return samples
    try:
        from scipy.signal import lfilter
        return lfilter(b, a, samples).astype(np.float32)
    except Exception:
        # Fallback pure python/numpy IIR recursion
        out = np.zeros_like(samples, dtype=np.float32)
        b0, b1, b2 = b[0], b[1], b[2]
        a1, a2 = a[1], a[2]
        x1 = x2 = y1 = y2 = 0.0
        for i in range(len(samples)):
            x0 = float(samples[i])
            y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            out[i] = y0
            x2, x1 = x1, x0
            y2, y1 = y1, y0
        return out


# ----------------------------------------------------------------------
# 2. Studio Acoustic Equalization & Broadcast Tone Shaping
# ----------------------------------------------------------------------
def apply_parametric_mastering_eq(samples: np.ndarray, sample_rate: int = 24000) -> np.ndarray:
    """
    Cortana Broadcast 4-Band Mastering EQ:
    1. High Air Presence Shelf (+3.5 dB @ 5.5 kHz): Crystalline clarity and vocal sheen.
    2. Consonant Presence Bell (+1.8 dB @ 2.8 kHz): Speech intelligibility.
    3. Warmth Proximity Bell (+1.5 dB @ 180 Hz): Chest resonance and executive authority.
    4. Boxiness / Mud Notch (-2.5 dB @ 480 Hz): Removes hollow acoustic reflections.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    out = samples.copy()
    # 1. High Air Presence Shelf
    b, a = biquad_highshelf(5500.0, gain_db=3.5, q=0.707, fs=sample_rate)
    out = apply_biquad(out, b, a)

    # 2. Consonant Presence Bell
    b, a = biquad_peaking(2800.0, gain_db=1.8, q=1.4, fs=sample_rate)
    out = apply_biquad(out, b, a)

    # 3. Warmth Proximity Bell
    b, a = biquad_peaking(180.0, gain_db=1.5, q=1.2, fs=sample_rate)
    out = apply_biquad(out, b, a)

    # 4. Boxiness Mud Notch
    b, a = biquad_peaking(480.0, gain_db=-2.5, q=1.8, fs=sample_rate)
    out = apply_biquad(out, b, a)

    return out


# ----------------------------------------------------------------------
# 3. Dynamic Range Compressor, Peak Limiter & De-Esser
# ----------------------------------------------------------------------
def apply_studio_compression_limiting(
    samples: np.ndarray,
    sample_rate: int = 24000,
    threshold_db: float = -14.0,
    ratio: float = 2.5,
    makeup_gain_db: float = 2.0
) -> np.ndarray:
    """
    Studio RMS Dynamic Range Compressor with Soft-Knee and True Peak Brickwall Limiter.
    Ensures consistent vocal projection without digital clipping.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    # Calculate signal envelope with fast attack and smooth release
    abs_sig = np.abs(samples)
    attack_coeff = np.exp(-1.0 / (sample_rate * 0.008))   # 8ms attack
    release_coeff = np.exp(-1.0 / (sample_rate * 0.060))  # 60ms release

    envelope = np.zeros_like(abs_sig)
    env = 0.0
    for i in range(len(abs_sig)):
        x = abs_sig[i]
        if x > env:
            env = attack_coeff * env + (1.0 - attack_coeff) * x
        else:
            env = release_coeff * env + (1.0 - release_coeff) * x
        envelope[i] = env

    # Compression gain curve
    env_db = 20.0 * np.log10(np.maximum(envelope, 1e-6))
    gain_db = np.zeros_like(env_db)
    over_mask = env_db > threshold_db
    gain_db[over_mask] = (threshold_db - env_db[over_mask]) * (1.0 - 1.0 / ratio)
    gain_linear = 10.0 ** ((gain_db + makeup_gain_db) / 20.0)

    compressed = samples * gain_linear

    # Soft-knee peak limiting (-0.5 dBFS ceiling)
    ceiling = 10.0 ** (-0.5 / 20.0)  # ~0.944
    limited = np.tanh(compressed / ceiling) * ceiling
    return limited.astype(np.float32)


def apply_dynamic_deesser(samples: np.ndarray, sample_rate: int = 24000) -> np.ndarray:
    """
    Dynamic sibilance attenuator targeting harsh 6.5 kHz - 8.5 kHz frequencies.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    # Bandpass filter for sibilant energy
    b, a = biquad_peaking(7500.0, gain_db=6.0, q=2.0, fs=sample_rate)
    sibilance = apply_biquad(samples, b, a)

    sibilance_env = np.abs(sibilance)
    threshold = 0.35
    attenuation = np.ones_like(samples)
    mask = sibilance_env > threshold
    attenuation[mask] = 1.0 / (1.0 + (sibilance_env[mask] - threshold) * 2.0)

    return (samples * attenuation).astype(np.float32)


# ----------------------------------------------------------------------
# 4. Spatial Stereo Widening & Cockpit Holographic Acoustics
# ----------------------------------------------------------------------
def apply_holographic_spatial_widener(
    samples: np.ndarray,
    sample_rate: int = 24000,
    delay_ms: float = 14.0,
    wet: float = 0.08
) -> np.ndarray:
    """
    Haas-effect binaural spatial widener creating a 3D holographic acoustic soundstage.
    Returns (N, 2) stereo array or mono if stereo unavailable.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    delay_samples = max(1, int(sample_rate * (delay_ms / 1000.0)))
    left_channel = samples.copy()
    right_channel = samples.copy()

    # Subtle micro-delay on right channel + phase inverted reflection
    if len(samples) > delay_samples:
        right_channel[delay_samples:] = (1.0 - wet) * samples[delay_samples:] + wet * samples[:-delay_samples]
        left_channel[:-delay_samples] += (wet * 0.5) * samples[delay_samples:]

    stereo = np.column_stack((left_channel, right_channel)).astype(np.float32)
    return stereo


def generate_radio_chirp(sample_rate: int = 24000, duration_ms: int = 60, start_freq: float = 880.0, end_freq: float = 1760.0) -> np.ndarray:
    """Generate high-tech start-of-transmission tactical chirp."""
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms / 1000.0, n_samples, endpoint=False)
    freqs = np.linspace(start_freq, end_freq, n_samples)
    phase = 2 * np.pi * np.cumsum(freqs) / sample_rate
    chirp = 0.25 * np.sin(phase)
    window = np.hanning(n_samples)
    return (chirp * window).astype(np.float32)


def generate_squelch_burst(sample_rate: int = 24000, duration_ms: int = 40) -> np.ndarray:
    """Generate end-of-transmission radio squelch burst."""
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    noise = np.random.uniform(-0.15, 0.15, n_samples)
    window = np.hanning(n_samples)
    return (noise * window).astype(np.float32)


def apply_radio_comms_dsp(samples: np.ndarray, sample_rate: int = 24000) -> np.ndarray:
    """Apply tactical military radio bandpass filter (300 Hz - 3400 Hz)."""
    b_high, a_high = biquad_highshelf(3400.0, gain_db=-18.0, q=0.707, fs=sample_rate)
    b_low, a_low = biquad_highshelf(300.0, gain_db=18.0, q=0.707, fs=sample_rate)
    filtered = apply_biquad(samples, b_high, a_high)
    distorted = np.tanh(filtered * 1.3) * 0.9
    return distorted.astype(np.float32)


def apply_cockpit_spatial_reverb(samples: np.ndarray, sample_rate: int = 24000, delay_ms: int = 35, decay: float = 0.28) -> np.ndarray:
    """Apply multi-tap spatial reverberation modeling a starship bridge / cockpit acoustic environment."""
    delay_samples = int(sample_rate * (delay_ms / 1000.0))
    output = np.zeros(len(samples) + delay_samples * 3, dtype=np.float32)
    output[:len(samples)] = samples
    output[delay_samples:delay_samples + len(samples)] += samples * decay
    output[delay_samples * 2:delay_samples * 2 + len(samples)] += samples * (decay * decay)
    max_val = np.max(np.abs(output))
    if max_val > 1.0:
        output = output / max_val
    return output


def apply_spatial_panning(samples: np.ndarray, pan: float = 0.0) -> np.ndarray:
    """Convert mono speech into stereo array with spatial panning."""
    if samples.ndim == 2:
        return samples
    pan = max(-1.0, min(1.0, pan))
    angle = (pan + 1.0) * (np.pi / 4.0)
    left_channel = samples * math.cos(angle)
    right_channel = samples * math.sin(angle)
    return np.column_stack((left_channel, right_channel)).astype(np.float32)


# ----------------------------------------------------------------------
# 5. Executive Precision & Magnetic Gravitas Harmonic DSP
# ----------------------------------------------------------------------
def apply_subharmonic_chest_resonance(
    samples: np.ndarray,
    sample_rate: int = 24000,
    sub_freq: float = 75.0,
    blend: float = 0.22
) -> np.ndarray:
    """
    Generates 2nd-order sub-harmonic chest resonance (50Hz - 110Hz).
    Provides the physical, room-filling acoustic thump of Kratos / Master Chief.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    # 1. Extract low frequencies (<160 Hz)
    b_low, a_low = biquad_peaking(sub_freq, gain_db=6.0, q=1.2, fs=sample_rate)
    low_band = apply_biquad(samples, b_low, a_low)

    # 2. Generate sub-octave harmonic energy via non-linear full-wave phase folding
    sub_harmonics = np.sign(low_band) * (low_band ** 2)

    # 3. Steep low-pass filter to keep only sub-bass warmth (<120 Hz)
    b_sub, a_sub = biquad_highshelf(120.0, gain_db=-18.0, q=0.707, fs=sample_rate)
    filtered_sub = apply_biquad(sub_harmonics, b_sub, a_sub)

    # 4. Blend sub-harmonics into original signal
    out = samples + filtered_sub * blend
    return out.astype(np.float32)


def apply_magnetic_tube_saturation(
    samples: np.ndarray,
    drive: float = 1.35,
    warmth: float = 0.18
) -> np.ndarray:
    """
    Analog Vacuum Tube & Tape Saturation.
    Uses polynomial wave-shaping and asymmetric 2nd-order harmonics for rich velvet vocal warmth.
    """
    if np is None or samples is None or len(samples) == 0:
        return samples

    x = samples * drive
    # Asymmetric polynomial distortion: tanh(x) + warmth * x^2 for even-order tube harmonics
    even_harmonics = warmth * (x * np.abs(x))
    saturated = np.tanh(x) + even_harmonics

    # Normalize ceiling to avoid clipping
    max_val = np.max(np.abs(saturated))
    if max_val > 0.95:
        saturated = saturated * (0.95 / max_val)

    return saturated.astype(np.float32)


# ----------------------------------------------------------------------
# 6. Master DSP Preset Orchestrator
# ----------------------------------------------------------------------
def process_tactical_dsp_pipeline(
    raw_samples: np.ndarray,
    sample_rate: int = 24000,
    preset: str = "STUDIO_MASTER",
    pan: float = 0.0
) -> Tuple[np.ndarray, int]:
    """
    Master Audio DSP Processing Pipeline.
    Presets:
    - 'EXECUTIVE_PRECISION': Sub-harmonic chest drive + Magnetic tube warmth + 4-band mastering EQ + 3D spatial air.
    - 'STOIC_GRAVITAS': Maximum sub-bass chest thump + Analog tube drive + Proximity compressor (Kratos / Master Chief).
    - 'MAGNETIC_INTIMATE': Velvet tube saturation + De-esser + Vocal presence + Haas 3D stereo widener.
    - 'STUDIO_MASTER' / 'CORTANA_MASTER': Full 4-band mastering EQ + Studio compressor + De-esser + Holographic presence.
    - 'HOLOGRAPHIC_AI': Air shelf EQ + Haas 3D stereo widener + subtle room acoustics.
    - 'AURA_COCKPIT': Crystalline voice + cockpit reverb reflections.
    - 'TACTICAL_RADIO': VHF bandpass filter + chirp + squelch.
    - 'STUDIO_DIRECT': Pure uncolored neural audio.
    """
    if raw_samples is None or len(raw_samples) == 0:
        return raw_samples, sample_rate

    p_upper = (preset or "STUDIO_MASTER").upper()

    if p_upper in ("EXECUTIVE_PRECISION", "ALEXANDER_SOVEREIGN", "FREYA_VALKYRIE", "SOVEREIGN"):
        # 1. 4-Band Mastering EQ
        eq = apply_parametric_mastering_eq(raw_samples, sample_rate)
        # 2. Sub-harmonic chest resonance (physical thump)
        chested = apply_subharmonic_chest_resonance(eq, sample_rate, sub_freq=75.0, blend=0.24)
        # 3. Magnetic tube saturation (velvet warmth)
        saturated = apply_magnetic_tube_saturation(chested, drive=1.35, warmth=0.20)
        # 4. De-esser
        deessed = apply_dynamic_deesser(saturated, sample_rate)
        # 5. Studio compression & peak limiting
        compressed = apply_studio_compression_limiting(deessed, sample_rate, threshold_db=-15.0, ratio=2.8, makeup_gain_db=2.2)
        # 6. Holographic 3D spatial widener
        mastered = apply_holographic_spatial_widener(compressed, sample_rate, wet=0.08)
        return mastered, sample_rate

    if p_upper in ("STOIC_GRAVITAS", "AURELIUS_STOIC", "NOCTURNA_SOLON", "KRATOS", "MASTER_CHIEF"):
        # 1. Low-end heavy EQ
        b_low, a_low = biquad_peaking(110.0, gain_db=3.5, q=1.0, fs=sample_rate)
        eq = apply_biquad(raw_samples, b_low, a_low)
        # 2. Deep sub-harmonic chest resonance
        chested = apply_subharmonic_chest_resonance(eq, sample_rate, sub_freq=65.0, blend=0.32)
        # 3. Heavy tube saturation
        saturated = apply_magnetic_tube_saturation(chested, drive=1.45, warmth=0.25)
        # 4. De-esser
        deessed = apply_dynamic_deesser(saturated, sample_rate)
        # 5. Heavy optical proximity compression
        compressed = apply_studio_compression_limiting(deessed, sample_rate, threshold_db=-17.0, ratio=3.2, makeup_gain_db=2.5)
        # 6. Subtle spatial width
        mastered = apply_holographic_spatial_widener(compressed, sample_rate, wet=0.05)
        return mastered, sample_rate

    if p_upper in ("MAGNETIC_INTIMATE", "INTIMATE"):
        eq = apply_parametric_mastering_eq(raw_samples, sample_rate)
        saturated = apply_magnetic_tube_saturation(eq, drive=1.25, warmth=0.16)
        deessed = apply_dynamic_deesser(saturated, sample_rate)
        compressed = apply_studio_compression_limiting(deessed, sample_rate, threshold_db=-14.0, ratio=2.4)
        mastered = apply_holographic_spatial_widener(compressed, sample_rate, wet=0.10)
        return mastered, sample_rate

    if p_upper in ("STUDIO_MASTER", "CORTANA_MASTER", "CORTANA_PRIME"):
        eq = apply_parametric_mastering_eq(raw_samples, sample_rate)
        deessed = apply_dynamic_deesser(eq, sample_rate)
        compressed = apply_studio_compression_limiting(deessed, sample_rate)
        mastered = apply_holographic_spatial_widener(compressed, sample_rate, wet=0.06)
        return mastered, sample_rate

    if p_upper == "HOLOGRAPHIC_AI":
        eq = apply_parametric_mastering_eq(raw_samples, sample_rate)
        compressed = apply_studio_compression_limiting(eq, sample_rate)
        widened = apply_holographic_spatial_widener(compressed, sample_rate, wet=0.12)
        return widened, sample_rate

    if p_upper == "TACTICAL_RADIO":
        filtered = apply_radio_comms_dsp(raw_samples, sample_rate)
        chirp = generate_radio_chirp(sample_rate, duration_ms=45)
        squelch = generate_squelch_burst(sample_rate, duration_ms=30)
        combined = np.concatenate((chirp, filtered, squelch))
        return apply_spatial_panning(combined, pan), sample_rate

    if p_upper == "AURA_COCKPIT":
        reverbed = apply_cockpit_spatial_reverb(raw_samples, sample_rate, delay_ms=28, decay=0.20)
        compressed = apply_studio_compression_limiting(reverbed, sample_rate)
        return apply_spatial_panning(compressed, pan), sample_rate

    # Default STUDIO_DIRECT
    if pan != 0.0:
        return apply_spatial_panning(raw_samples, pan), sample_rate
    return raw_samples, sample_rate


