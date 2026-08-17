"""
Multi-Speaker Dialogue Synthesizer & Tactical Audio Podcast Generator.
Standard: Pure Python Standard Library + Kokoro-82M ONNX + VoiceDSP Rack.
Ponytail Senior Dev Principle: Seamless multi-persona roundtable audio synthesis, crossfaded turn boundaries, natural conversational pauses, and mastered broadcast output.
"""

import os
import sys
import time
import io
import struct
from typing import Dict, Any, List, Optional

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, KOKORO_PERSONAS
from src.core.voice_dsp import VoiceDSP
from src.core.voice_normalizer import VoiceNormalizer
from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer


class VoicePodcastGenerator:
    """
    Synthesizes multi-persona roundtable discussions and tactical briefs
    into a continuous, mastered broadcast audio stream.
    """

    SAMPLE_RATE = 24000

    @classmethod
    def synthesize_dialogue(
        cls,
        turns: List[Dict[str, str]],
        pause_duration_s: float = 0.35,
        play_live: bool = False,
        output_wav_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize multi-speaker conversation:
        turns format: [{"speaker": "Aura", "persona": "AURA_SHIP_AI", "text": "..."}, ...]
        """
        t0 = time.perf_counter()
        combined_pcm_chunks = []
        pause_samples = int(cls.SAMPLE_RATE * pause_duration_s)
        pause_buffer = np.zeros(pause_samples, dtype=np.float32) if np is not None else b'\x00' * (pause_samples * 2)

        rendered_turns = []

        for idx, turn in enumerate(turns):
            speaker = turn.get("speaker", f"Speaker {idx+1}")
            persona = turn.get("persona", "AURA_SHIP_AI")
            raw_text = turn.get("text", "")
            voice_id = KOKORO_PERSONAS.get(persona, persona)
            dsp_preset = "HOLOGRAPHIC_AURA" if "AURA" in persona else "COMMANDER_TACTICAL" if "COMMANDER" in persona else "EXECUTIVE_PRESENCE"

            clean_text = VoiceNormalizer.normalize_for_speech(raw_text)

            samples = None
            copilot = VoiceBridge.get_copilot()
            if copilot and getattr(copilot, "_local_kokoro_instance", None):
                try:
                    samples, _ = copilot._local_kokoro_instance.create(clean_text, voice=voice_id, speed=1.0)
                except Exception:
                    samples = None

            if samples is None:
                try:
                    raw_wav = VoiceBridge.synthesize_bytes(clean_text, voice=voice_id, speed=1.0, dsp_preset=dsp_preset)
                    if raw_wav and len(raw_wav) > 44 and np is not None:
                        int16_data = np.frombuffer(raw_wav[44:], dtype=np.int16)
                        samples = int16_data.astype(np.float32) / 32768.0
                except Exception:
                    samples = None

            if samples is not None and len(samples) > 0:
                # Apply DSP preset mastering
                mastered_samples = VoiceDSP.apply_dsp_preset(samples, preset=dsp_preset, fs=cls.SAMPLE_RATE)
                combined_pcm_chunks.append(mastered_samples)

                # Add natural pause between speakers
                if idx < len(turns) - 1:
                    combined_pcm_chunks.append(pause_buffer)

                rendered_turns.append({
                    "turn": idx + 1,
                    "speaker": speaker,
                    "persona": persona,
                    "voice": voice_id,
                    "dsp_preset": dsp_preset,
                    "text": clean_text
                })

        if not combined_pcm_chunks:
            return {"status": "empty_dialogue", "turns_count": 0}

        # Concatenate all mastered audio chunks
        full_audio_float = np.concatenate(combined_pcm_chunks) if np is not None else np.array([])
        # Final broadcast mastering with True-Peak Soft-Tanh Limiter
        final_mastered = VoiceDSP.master_audio_buffer(full_audio_float, target_dbfs=-1.0, sample_rate=cls.SAMPLE_RATE)

        # Convert to 16-bit PCM bytes
        pcm_16 = (np.clip(final_mastered, -1.0, 1.0) * 32767.0).astype(np.int16)
        num_samples = len(pcm_16)
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + num_samples * 2, b'WAVE',
            b'fmt ', 16, 1, 1,
            cls.SAMPLE_RATE, cls.SAMPLE_RATE * 2, 2, 16,
            b'data', num_samples * 2
        )
        wav_bytes = wav_header + pcm_16.tobytes()

        # Save to disk if requested
        if output_wav_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
            with open(output_wav_path, "wb") as f:
                f.write(wav_bytes)

        # Play live through persistent WASAPI streamer if requested
        if play_live:
            streamer = get_instant_streamer()
            streamer.play_instant_pcm(pcm_samples=final_mastered, sample_rate=cls.SAMPLE_RATE, raw_wav_bytes=wav_bytes, sync=True)

        duration_s = round(num_samples / float(cls.SAMPLE_RATE), 2)
        total_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "status": "podcast_synthesized",
            "turns_count": len(rendered_turns),
            "rendered_turns": rendered_turns,
            "audio_duration_seconds": duration_s,
            "total_bytes": len(wav_bytes),
            "synthesis_time_ms": total_time_ms,
            "output_wav_path": output_wav_path
        }
