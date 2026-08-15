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
    def _speak_clause_if_valid(
        cls,
        clause: str,
        voice_id: str,
        dsp_preset: str,
        sync: bool,
        clauses_spoken: list,
        t0: float,
        first_clause_ttfs_ms: Optional[float]
    ) -> Optional[float]:
        """Normalize and dispatch single spoken clause, returning updated TTFS metric."""
        stripped = clause.strip()
        if len(stripped) <= 2 or not any(c.isalnum() for c in stripped):
            return first_clause_ttfs_ms
        clean = VoiceNormalizer.normalize_for_speech(stripped)
        clean = re.sub(r'[*_#`\[\]]', '', clean).strip()
        if not clean or not any(c.isalnum() for c in clean):
            return first_clause_ttfs_ms

        if first_clause_ttfs_ms is None:
            first_clause_ttfs_ms = round((time.perf_counter() - t0) * 1000, 2)

        InstantVoiceClient.speak_instant(
            text=clean,
            voice=voice_id,
            dsp_preset=dsp_preset,
            sync=sync
        )
        clauses_spoken.append(clean)
        return first_clause_ttfs_ms

    @classmethod
    def stream_and_speak(
        cls,
        token_generator: Iterator[str],
        persona: str = "AURA_SHIP_AI",
        dsp_preset: str = "HOLOGRAPHIC_AURA",
        sync: bool = False
    ) -> Dict[str, Any]:
        """
        Consume a token generator, chunk clauses, and stream audio concurrently.
        """
        t0 = time.perf_counter()
        from src.core.voice_bridge import KOKORO_PERSONAS
        voice_id = persona if (persona in KOKORO_PERSONAS or persona.isupper()) else KOKORO_PERSONAS.get(persona, "bf_emma")

        buffer = ""
        full_text = ""
        clauses_spoken = []
        first_clause_ttfs_ms = None

        for token in token_generator:
            buffer += token
            full_text += token

            parts = cls.CLAUSE_DELIMITERS.split(buffer)
            if len(parts) <= 1:
                continue

            clause_candidate = (parts[0] + parts[1]).strip()
            # If clause is too short (e.g. "Dr.", "v1.", "e.g."), keep buffering
            if len(clause_candidate) < 6 and not any(d in clause_candidate for d in ("\n", "!", "?")):
                continue

            buffer = "".join(parts[2:])
            first_clause_ttfs_ms = cls._speak_clause_if_valid(
                clause_candidate, voice_id, dsp_preset, sync, clauses_spoken, t0, first_clause_ttfs_ms
            )

        # Tail buffer
        if buffer.strip():
            first_clause_ttfs_ms = cls._speak_clause_if_valid(
                buffer, voice_id, dsp_preset, sync, clauses_spoken, t0, first_clause_ttfs_ms
            )

        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "stream_completed",
            "full_text": full_text.strip(),
            "clauses_count": len(clauses_spoken),
            "first_clause_ttfs_ms": first_clause_ttfs_ms or total_ms,
            "total_ms": total_ms,
            "clauses": clauses_spoken
        }
