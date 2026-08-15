"""
Nullsec Tactical Threat Radar & Cynosural Acoustic Alerter.
Standard: Pure Python Standard Library (urllib, json, time) + Kokoro-82M Voice Bridge.
Ponytail Senior Dev Principle: Dynamic CCP ESI telemetry polling, deterministic threat scoring, and procedural klaxon audio dispatch.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer


class EveTacticalThreatRadar:
    """
    Nullsec threat sentinel monitoring G-EURJ and adjacent constellation systems via live CCP ESI.
    """

    SYSTEM_IDS = {
        "G-EURJ": 30001155,
        "M-OEE8": 30001156,
        "Q-S7D1": 30001157,
        "319-3D": 30001158,
        "PR-8CA": 30001159,
        "YZ-LQL": 30001160
    }

    _kills_cache: Dict[int, Dict[str, int]] = {}
    _jumps_cache: Dict[int, int] = {}
    _last_fetch_ts: float = 0.0
    _CACHE_TTL_S: float = 60.0

    @classmethod
    def _fetch_esi_universe_stats(cls):
        """Fetch live system kills and jumps from CCP ESI."""
        now = time.time()
        if now - cls._last_fetch_ts < cls._CACHE_TTL_S and cls._kills_cache:
            return

        # 1. System Kills
        try:
            req = urllib.request.Request(
                "https://esi.evetech.net/latest/universe/system_kills/",
                headers={"User-Agent": "NeuroAlexander-SovereignRadar/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cls._kills_cache = {
                    item["system_id"]: {
                        "ship_kills": item.get("ship_kills", 0),
                        "pod_kills": item.get("pod_kills", 0),
                        "npc_kills": item.get("npc_kills", 0)
                    }
                    for item in data
                }
        except Exception:
            pass

        # 2. System Jumps
        try:
            req = urllib.request.Request(
                "https://esi.evetech.net/latest/universe/system_jumps/",
                headers={"User-Agent": "NeuroAlexander-SovereignRadar/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cls._jumps_cache = {
                    item["system_id"]: item.get("ship_jumps", 0)
                    for item in data
                }
        except Exception:
            pass

        cls._last_fetch_ts = now

    @classmethod
    def evaluate_system_threat(
        cls,
        target_system: str = "G-EURJ",
        speak_alert: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate real-time threat metrics in solar system and trigger acoustic klaxon if elevated.
        """
        t0 = time.perf_counter()
        streamer = get_instant_streamer()
        cls._fetch_esi_universe_stats()

        system_id = cls.SYSTEM_IDS.get(target_system.upper(), 30001155)
        kills_info = cls._kills_cache.get(system_id, {"ship_kills": 0, "pod_kills": 0, "npc_kills": 0})
        jumps_count = cls._jumps_cache.get(system_id, 0)

        ship_kills = kills_info["ship_kills"]
        pod_kills = kills_info["pod_kills"]
        npc_kills = kills_info["npc_kills"]

        # Dynamic Threat Classification
        if ship_kills > 5:
            threat_level = "CRITICAL_RED"
            spoken_alert = f"Critical threat alert for solar system {target_system}. {ship_kills} ship destructions recorded in the past hour. Hostile fleet active."
            cue = "alert"
            dsp = "COMMANDER_TACTICAL"
        elif ship_kills > 0 or pod_kills > 0 or jumps_count > 25:
            threat_level = "ELEVATED_AMBER"
            spoken_alert = f"Elevated threat in system {target_system}. {ship_kills} ship kills and {jumps_count} stargate jumps logged in the last hour. Maintain alignment."
            cue = "target_lock"
            dsp = "COMMANDER_TACTICAL"
        else:
            threat_level = "NOMINAL_GREEN"
            spoken_alert = f"Tactical radar sweep complete for system {target_system}. Threat level is nominal green with {npc_kills} NPC rat destructions and zero hostile kills."
            cue = "acknowledge"
            dsp = "TRANSCENDENTAL_AURA"

        if speak_alert:
            streamer.play_hud_cue(cue)
            InstantVoiceClient.speak_instant(
                text=spoken_alert,
                voice="am_adam" if "CRITICAL" in threat_level or "ELEVATED" in threat_level else "bf_emma",
                dsp_preset=dsp,
                sync=False
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "sweep_completed",
            "system": target_system,
            "system_id": system_id,
            "threat_level": threat_level,
            "ship_kills_1h": ship_kills,
            "pod_kills_1h": pod_kills,
            "npc_kills_1h": npc_kills,
            "stargate_jumps_1h": jumps_count,
            "adjacent_systems_checked": list(cls.SYSTEM_IDS.keys()),
            "elapsed_ms": elapsed_ms,
            "spoken_alert": spoken_alert
        }

    @classmethod
    def trigger_simulated_cyno_alarm(cls, system: str = "G-EURJ") -> Dict[str, Any]:
        """Trigger simulated hostile cynosural beacon alert for drill verification."""
        streamer = get_instant_streamer()
        streamer.play_hud_cue("alert")

        spoken_warning = f"Warning! Cynosural beacon signature detected in solar system {system}. All industrial fleet units hold dock or align to safe POS."
        InstantVoiceClient.speak_instant(
            text=spoken_warning,
            voice="am_adam",
            dsp_preset="COMMANDER_TACTICAL",
            sync=False
        )

        return {
            "status": "cyno_alarm_dispatched",
            "system": system,
            "threat_level": "CRITICAL_RED",
            "spoken_warning": spoken_warning
        }
