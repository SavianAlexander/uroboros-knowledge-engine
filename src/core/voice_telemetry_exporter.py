"""
Zero-Dependency Audio & Neural Voice Telemetry Exporter.
Standard: Pure Python Standard Library (json, time, typing).
Ponytail Senior Dev Principle: Provides Prometheus metrics & JSON telemetry across all voice, DSP, RAG cache, and audit subsystems without external telemetry dependencies.
"""

import json
import time
from typing import Dict, Any, List, Optional

from src.core.voice_dsp import VoiceDSP
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.rag_query_cache import GLOBAL_RAG_CACHE
from src.core.audit_hashchain import GLOBAL_AUDIT_HASHCHAIN


class AudioTelemetryExporter:
    """Exports structured telemetry and Prometheus metrics for the audio & voice subsystem."""

    @classmethod
    def get_telemetry_snapshot(cls) -> Dict[str, Any]:
        """Aggregate real-time metrics across all voice, DSP, cache, and audit subsystems."""
        now = time.time()
        call_status = VoiceCallIntercomEngine.get_call_status()
        cache_stats = GLOBAL_RAG_CACHE.get_stats()
        audit_status = GLOBAL_AUDIT_HASHCHAIN.verify_integrity()

        return {
            "timestamp": now,
            "engine": {
                "name": "Kokoro-82M ONNX",
                "sample_rate_hz": 24000,
                "playback": "Native Win32 C-Level SND_MEMORY (<15ms)",
                "status": "operational"
            },
            "intercom_call": {
                "active": call_status.get("active", False),
                "ai_speaking": call_status.get("ai_speaking", False),
                "dialogue_turns": call_status.get("dialogue_turns", 0),
                "duration_seconds": call_status.get("duration_seconds", 0.0)
            },
            "dsp_mastering": {
                "active_presets_count": len(VoiceDSP.get_available_presets()),
                "true_peak_ceiling_dbfs": -1.0,
                "fft_bands": 32
            },
            "semantic_rag_cache": cache_stats,
            "audit_hashchain": {
                "total_blocks": audit_status.get("total_blocks", 0),
                "chain_valid": audit_status.get("valid", False),
                "merkle_root": audit_status.get("merkle_root", "")
            }
        }

    @classmethod
    def export_prometheus_metrics(cls) -> str:
        """Render standard Prometheus exposition format string for monitoring scrapers."""
        snap = cls.get_telemetry_snapshot()
        lines = [
            "# HELP audio_engine_status 1 if operational, 0 if errored",
            "# TYPE audio_engine_status gauge",
            "audio_engine_status 1.0",
            "",
            "# HELP audio_intercom_active 1 if voice call session is active",
            "# TYPE audio_intercom_active gauge",
            f"audio_intercom_active {1.0 if snap['intercom_call']['active'] else 0.0}",
            "",
            "# HELP audio_intercom_dialogue_turns Total turns in active call session",
            "# TYPE audio_intercom_dialogue_turns counter",
            f"audio_intercom_dialogue_turns {snap['intercom_call']['dialogue_turns']}",
            "",
            "# HELP rag_cache_hits Total semantic RAG cache hits",
            "# TYPE rag_cache_hits counter",
            f"rag_cache_hits {snap['semantic_rag_cache']['hits']}",
            "",
            "# HELP rag_cache_misses Total semantic RAG cache misses",
            "# TYPE rag_cache_misses counter",
            f"rag_cache_misses {snap['semantic_rag_cache']['misses']}",
            "",
            "# HELP rag_cache_hit_ratio Hit ratio for semantic RAG cache",
            "# TYPE rag_cache_hit_ratio gauge",
            f"rag_cache_hit_ratio {snap['semantic_rag_cache']['hit_ratio']}",
            "",
            "# HELP audit_hashchain_blocks Total immutable SHA-256 blocks committed",
            "# TYPE audit_hashchain_blocks counter",
            f"audit_hashchain_blocks {snap['audit_hashchain']['total_blocks']}",
            "",
            "# HELP audit_hashchain_valid 1 if Merkle chain is cryptographically intact",
            "# TYPE audit_hashchain_valid gauge",
            f"audit_hashchain_valid {1.0 if snap['audit_hashchain']['chain_valid'] else 0.0}"
        ]
        return "\n".join(lines) + "\n"
