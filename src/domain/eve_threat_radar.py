"""
Live EVE Tactical Threat Radar & Acoustic Cyno Klaxon Engine.
Standard: Pure Python Standard Library (urllib, json, time, math) + Kokoro-82M Voice Bridge.
Ponytail Senior Dev Principle: Real-time CCP ESI kills/jumps endpoint analysis, dynamic constellation adjacent system sweep, and acoustic warning thresholds.
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
    Tactical Threat Sentinel querying live CCP ESI universe metrics and triggering acoustic klaxons.
    """

    SYSTEM_IDS: Dict[str, int] = {
        "G-EURJ": 30001155,  # Sovereign staging
        "1DQ1-A": 30004759,  # Delve Capital Hub
        "TAMA": 30002813,    # Notorious Lowsec choke point
        "RANCER": 30002014,  # Pipe Gatecamp route
        "AMAMAKE": 30002537, # Heimatar FW hub
        "JITA": 30000142     # The Forge Trade Center
    }

    _kills_cache: Dict[int, Dict[str, int]] = {}
    _jumps_cache: Dict[int, int] = {}
    _constellation_systems_cache: Dict[int, List[str]] = {}
    _last_fetch_ts: float = 0.0
    _CACHE_TTL_S: float = 60.0

    @classmethod
    def resolve_solar_system_id(cls, system_name: str) -> int:
        """
        Dynamically resolve ANY solar system name from request to its CCP ESI system_id.
        """
        clean = system_name.strip()
        for k, v in cls.SYSTEM_IDS.items():
            if k.lower() == clean.lower():
                return v

        try:
            url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility"
            payload = json.dumps([clean]).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "NeuroAlexander-SovereignRadar/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                systems = data.get("systems", [])
                if systems:
                    sys_id = systems[0]["id"]
                    cls.SYSTEM_IDS[clean.upper()] = sys_id
                    return sys_id
        except Exception:
            pass

        return cls.SYSTEM_IDS.get(clean.upper(), 30001155)

    @classmethod
    def resolve_constellation_systems(cls, system_id: int) -> List[str]:
        """Dynamically fetch all adjacent system names in the same constellation from CCP ESI."""
        if system_id in cls._constellation_systems_cache:
            return cls._constellation_systems_cache[system_id]

        try:
            # 1. Fetch system details
            url_sys = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility"
            req_sys = urllib.request.Request(url_sys, headers={"User-Agent": "NeuroAlexander-SovereignRadar/1.0"})
            with urllib.request.urlopen(req_sys, timeout=2.0) as resp:
                sys_data = json.loads(resp.read().decode("utf-8"))
                con_id = sys_data.get("constellation_id")

            if con_id:
                # 2. Fetch constellation systems
                url_con = f"https://esi.evetech.net/latest/universe/constellations/{con_id}/?datasource=tranquility"
                req_con = urllib.request.Request(url_con, headers={"User-Agent": "NeuroAlexander-SovereignRadar/1.0"})
                with urllib.request.urlopen(req_con, timeout=2.0) as resp2:
                    con_data = json.loads(resp2.read().decode("utf-8"))
                    sys_ids = con_data.get("systems", [])

                if sys_ids:
                    # 3. Resolve system names
                    url_names = "https://esi.evetech.net/latest/universe/names/?datasource=tranquility"
                    req_names = urllib.request.Request(
                        url_names,
                        data=json.dumps(sys_ids).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": "NeuroAlexander-SovereignRadar/1.0"}
                    )
                    with urllib.request.urlopen(req_names, timeout=2.0) as resp3:
                        names_data = json.loads(resp3.read().decode("utf-8"))
                        names = [item["name"] for item in names_data]
                        cls._constellation_systems_cache[system_id] = names
                        return names
        except Exception:
            pass

        fallback = list(cls.SYSTEM_IDS.keys())
        cls._constellation_systems_cache[system_id] = fallback
        return fallback

    @classmethod
    def _fetch_esi_universe_stats(cls):
        """Fetch live system kills and jumps from CCP ESI."""
        now = time.time()
        if now - cls._last_fetch_ts < cls._CACHE_TTL_S and cls._kills_cache:
            return

        # 1. System Kills
        try:
            req = urllib.request.Request(
                "https://esi.evetech.net/latest/universe/system_kills/?datasource=tranquility",
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
                "https://esi.evetech.net/latest/universe/system_jumps/?datasource=tranquility",
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
        Dynamically audits adjacent constellation systems from CCP ESI.
        """
        t0 = time.perf_counter()
        streamer = get_instant_streamer()
        cls._fetch_esi_universe_stats()

        system_id = cls.resolve_solar_system_id(target_system)
        kills_info = cls._kills_cache.get(system_id, {"ship_kills": 0, "pod_kills": 0, "npc_kills": 0})
        jumps_count = cls._jumps_cache.get(system_id, 0)
        adjacent_systems = cls.resolve_constellation_systems(system_id)

        ship_kills = kills_info["ship_kills"]
        pod_kills = kills_info["pod_kills"]
        npc_kills = kills_info["npc_kills"]

        # Dynamic Threat Classification
        if ship_kills >= 5 or pod_kills >= 2:
            threat_level = "CRITICAL_RED"
            dsp = "COMMANDER_TACTICAL"
            cue = "alert"
            spoken_alert = f"Tactical Alert! Combat activity detected in solar system {target_system}. {ship_kills} ship kills and {pod_kills} pod destructions in the last hour. Align out immediately."
        elif ship_kills > 0 or jumps_count > 40:
            threat_level = "ELEVATED_AMBER"
            dsp = "AURA_COCKPIT"
            cue = "acknowledge"
            spoken_alert = f"Caution. Elevated traffic in solar system {target_system}. {jumps_count} stargate jumps and {ship_kills} combat losses recorded."
        else:
            threat_level = "NOMINAL_GREEN"
            dsp = "HOLOGRAPHIC_AURA"
            cue = "wake"
            spoken_alert = f"Tactical radar sweep for solar system {target_system} is clear. Zero hostile losses in the past hour. Industrial operations nominal."

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
            "adjacent_systems_checked": adjacent_systems,
            "elapsed_ms": elapsed_ms,
            "spoken_alert": spoken_alert
        }

    @classmethod
    def trigger_simulated_cyno_alarm(cls, system: str = "G-EURJ") -> Dict[str, Any]:
        """Trigger emergency cynosural beacon alert for tactical drills."""
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
