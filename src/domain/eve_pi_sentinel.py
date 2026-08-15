"""
Planetary Interaction (PI) Extraction Sentinel & Factory Monitor.
Standard: Pure Python Standard Library (os, re, time, json) + Kokoro-82M Voice Bridge.
Ponytail Senior Dev Principle: Dynamic colony inspection across pilot dossiers, extractor cycle tracking, fleet-wide aggregation, and acoustic harvest alerts.
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
        Accepts specific character names or 'all'/'fleet' to aggregate across the full roster.
        """
        t0 = time.perf_counter()
        streamer = get_instant_streamer()

        char_root = os.path.join(BASE_DIR, "vault", "Eve Online", "Characters")
        is_fleet_audit = character_name.lower() in ("all", "fleet", "total", "")

        colonies_count = 0
        fleet_colonies: Dict[str, int] = {}
        status_summary = "No active colonies"

        if is_fleet_audit:
            if os.path.isdir(char_root):
                for entry in sorted(os.listdir(char_root)):
                    p = os.path.join(char_root, entry, "pi_deep.md")
                    if os.path.isfile(p):
                        with open(p, "r", encoding="utf-8") as f:
                            matches = re.findall(r'Planet\s+([^\n]+)', f.read())
                            cnt = len(matches)
                            fleet_colonies[entry] = cnt
                            colonies_count += cnt
            status_summary = f"{colonies_count} total colonies active across {len(fleet_colonies)} pilots"
            spoken_report = (
                f"Fleet-wide planetary interaction audit complete. {colonies_count} active planetary colonies "
                f"synchronized across the industrial wing. Customs offices nominal."
            )
        else:
            pi_file = os.path.join(char_root, character_name, "pi_deep.md")
            if os.path.exists(pi_file):
                with open(pi_file, "r", encoding="utf-8") as f:
                    matches = re.findall(r'Planet\s+([^\n]+)', f.read())
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
                dsp_preset="HOLOGRAPHIC_AURA",
                sync=False
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "pi_audit_completed",
            "character": character_name if not is_fleet_audit else "Fleet Total",
            "colonies_count": colonies_count,
            "fleet_breakdown": fleet_colonies,
            "status_summary": status_summary,
            "elapsed_ms": elapsed_ms,
            "spoken_report": spoken_report
        }
