"""
Streaming Token-to-Speech Clause Pipeliner.
Standard: Pure Python Standard Library (threading, queue, re, time) + Kokoro-82M ONNX + InstantAudioStreamer.
Ponytail Senior Dev Principle: Ultra-low perceived latency (<180ms TTFS), concurrent sentence pipelining, and non-blocking speech playback.
"""

import os
import sys
import time
import re
import queue
import threading
from typing import Dict, Any, List, Optional, Generator, Iterator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer
from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer


class VoiceStreamingPipeliner:
    """
    Pipelined sentence synthesizer.
    Splits token streams into auditory clauses and begins speech synthesis & playback
    on clause 1 while subsequent tokens are generated concurrently.
    """

    CLAUSE_DELIMITERS = re.compile(r'([.!?;\n]+)')

    @classmethod
    def stream_and_speak(
        cls,
        token_generator: Iterator[str],
        persona: str = "AURA_SHIP_AI",
        dsp_preset: str = "TRANSCENDENTAL_AURA",
        sync: bool = False
    ) -> Dict[str, Any]:
        """
        Consume a token generator, chunk clauses, and stream audio concurrently.
        """
        t0 = time.perf_counter()
        streamer = get_instant_streamer()
        voice_id = KOKORO_PERSONAS.get(persona, "bf_emma")

        buffer = ""
        full_text = ""
        clauses_spoken = []
        first_clause_ttfs_ms = None

        for token in token_generator:
            buffer += token
            full_text += token

            parts = cls.CLAUSE_DELIMITERS.split(buffer)
            if len(parts) > 1:
                clause_candidate = (parts[0] + parts[1]).strip()
                buffer = "".join(parts[2:])

                if len(clause_candidate) > 2:
                    clean = VoiceNormalizer.normalize_for_speech(clause_candidate)
                    clean = re.sub(r'[*_#`\[\]]', '', clean).strip()
                    if clean:
                        if first_clause_ttfs_ms is None:
                            first_clause_ttfs_ms = round((time.perf_counter() - t0) * 1000, 2)
                        res = InstantVoiceClient.speak_instant(
                            text=clean,
                            voice=voice_id,
                            dsp_preset=dsp_preset,
                            sync=sync
                        )
                        clauses_spoken.append(clean)

        # Tail buffer
        if buffer.strip():
            clean = VoiceNormalizer.normalize_for_speech(buffer.strip())
            clean = re.sub(r'[*_#`\[\]]', '', clean).strip()
            if clean:
                if first_clause_ttfs_ms is None:
                    first_clause_ttfs_ms = round((time.perf_counter() - t0) * 1000, 2)
                InstantVoiceClient.speak_instant(
                    text=clean,
                    voice=voice_id,
                    dsp_preset=dsp_preset,
                    sync=sync
                )
                clauses_spoken.append(clean)

        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "stream_completed",
            "full_text": full_text.strip(),
            "clauses_count": len(clauses_spoken),
            "first_clause_ttfs_ms": first_clause_ttfs_ms or total_ms,
            "total_ms": total_ms,
            "clauses": clauses_spoken
        }
