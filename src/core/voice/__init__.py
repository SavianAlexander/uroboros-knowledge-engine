"""
Unified Neural Voice & Tactical Audio Subsystem (Kokoro-82M ONNX Standard).
Consolidates neural TTS synthesis, WASAPI/circular buffering, multi-tap DSP reverb,
and real-time SSE/WebSocket audio streaming.
"""

from typing import Dict, Any, List, Optional

# Core engine and DSP components
try:
    from src.core.voice_engine import VoiceEngine, KokoroVoiceEngine
except ImportError:
    VoiceEngine = None
    KokoroVoiceEngine = None

try:
    from src.core.voice_dsp import VoiceDSP, apply_tactical_dsp, apply_reverb
except ImportError:
    VoiceDSP = None
    apply_tactical_dsp = None
    apply_reverb = None

try:
    from src.core.voice_normalizer import normalize_audio_chunk, AudioNormalizer
except ImportError:
    normalize_audio_chunk = None
    AudioNormalizer = None

try:
    from src.core.voice_streaming import VoiceStreamManager
except ImportError:
    VoiceStreamManager = None

try:
    from src.core.voice_audio_router import AudioRouter
except ImportError:
    AudioRouter = None

try:
    from src.core.voice_sfx import SoundEffectsEngine, play_sfx
except ImportError:
    SoundEffectsEngine = None
    play_sfx = None

try:
    from src.core.voice_stt_ear import SpeechToTextEar
except ImportError:
    SpeechToTextEar = None


__all__ = [
    "VoiceEngine",
    "KokoroVoiceEngine",
    "VoiceDSP",
    "apply_tactical_dsp",
    "apply_reverb",
    "AudioNormalizer",
    "normalize_audio_chunk",
    "VoiceStreamManager",
    "AudioRouter",
    "SoundEffectsEngine",
    "play_sfx",
    "SpeechToTextEar"
]
