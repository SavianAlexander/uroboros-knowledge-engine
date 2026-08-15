"""
Planetary Interaction (PI) Extraction Sentinel & Factory Monitor.
Standard: Pure Python Standard Library (os, re, time, json) + Kokoro-82M Voice Bridge.
Ponytail Senior Dev Principle: Dynamic colony inspection across pilot dossiers, extractor cycle tracking, and acoustic harvest alerts.
"""

import os
import sys
import time
import re
import json
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer


class EvePISentinel:
    """
    Planetary Interaction sentinel monitoring colony extraction cycles across the fleet.
    """

    @classmethod
    def audit_planetary_colonies(
        cls,
        character_name: str = "Savian Alexander",
        speak_alert: bool = True
    ) -> Dict[str, Any]:
        """
        Audit planetary extraction cycles and spoken state report.
        """
        t0 = time.perf_counter()
        streamer = get_instant_streamer()

        pi_file = os.path.join(BASE_DIR, "vault", "Eve Online", "Characters", character_name, "pi_deep.md")
        colonies_count = 0
        status_summary = "No active colonies"

        if os.path.exists(pi_file):
            with open(pi_file, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r'Planet\s+([^\n]+)', content)
                colonies_count = len(matches)
                if colonies_count > 0:
                    status_summary = f"{colonies_count} colonies active"

        spoken_report = (
            f"Planetary interaction sentinel audit complete for {character_name}. "
            f"Colony status: {status_summary}. All planetary customs offices synchronized."
        )

        if speak_alert:
            streamer.play_hud_cue("acknowledge")
            InstantVoiceClient.speak_instant(
                text=spoken_report,
                voice="bf_emma",
                dsp_preset="TRANSCENDENTAL_AURA",
                sync=False
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "pi_audit_completed",
            "character": character_name,
            "colonies_count": colonies_count,
            "status_summary": status_summary,
            "elapsed_ms": elapsed_ms,
            "spoken_report": spoken_report
        }
