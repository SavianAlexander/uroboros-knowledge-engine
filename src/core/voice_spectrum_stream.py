"""
Autonomous Real-Time FFT Audio Waveform & Spectrum Visualizer Engine.
Standard: Pure Python Standard Library + NumPy (optional guard).
Ponytail Senior Dev Principle: 32-band log-frequency FFT spectrum bins and RMS energy envelope calculation with sub-millisecond compute.
"""

import os
import sys
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_dsp import VoiceDSP


class VoiceSpectrumAnalyzer:
    """Computes real-time FFT frequency spectrum and waveform envelope for UI visualization."""

    @classmethod
    def analyze_audio_buffer(
        cls,
        samples: Any,
        sample_rate: int = 24000,
        num_bands: int = 32
    ) -> Dict[str, Any]:
        """
        Analyze audio sample array and generate 32-band spectrum + amplitude envelope.
        Delegates directly to unified VoiceDSP engine.
        """
        return VoiceDSP.analyze_spectrum(audio_samples=samples, sample_rate=sample_rate, num_bands=num_bands)
