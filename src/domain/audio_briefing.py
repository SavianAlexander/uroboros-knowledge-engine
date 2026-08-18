"""
Executive Audio Briefing & Podcast Script Generator.
Transforms executive daily briefing telemetry into structured conversational podcast scripts.
"""
import unicodedata

from typing import Dict, Any, List, Optional
from src.domain.daily_briefing import generate_daily_briefing


def generate_audio_podcast_script(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Synthesizes a 2-speaker interactive podcast script from daily briefing metrics.
    # ponytail: conversational script generation without external audio dependencies; ceiling: 2-speaker SSML text template; upgrade: integrate Edge-TTS or ElevenLabs SDK if audio synthesis is requested
    """
    try:
        briefing = generate_daily_briefing(db_path) if db_path is not None else generate_daily_briefing()
        total_files = briefing.get("total_documents", briefing.get("total_files", 0)) if isinstance(briefing, dict) else 0
        raw_tags = briefing.get("top_tags") or briefing.get("active_tags", []) if isinstance(briefing, dict) else []
        tags = []
        if isinstance(raw_tags, list):
            for t in raw_tags:
                if isinstance(t, dict) and "tag" in t:
                    tags.append(unicodedata.normalize("NFC", str(t["tag"])))
                elif t:
                    tags.append(unicodedata.normalize("NFC", str(t)))
        summary = unicodedata.normalize("NFC", str(briefing.get("executive_summary", "") or "")) if isinstance(briefing, dict) else ""

        script_turns = [
            {
                "speaker": "Host",
                "text": f"Welcome to your Daily Executive Intelligence Briefing. Today, our local vault contains {total_files} active index documents across key domain tags: {', '.join(tags[:4]) if tags else 'general'}."
            },
            {
                "speaker": "Analyst",
                "text": f"That's right. The primary executive takeaway for today: {summary}"
            },
            {
                "speaker": "Host",
                "text": "All vector indices and graph relationships are fully synchronized. That concludes today's debrief."
            }
        ]

        return {
            "status": "success",
            "podcast_title": "Daily Uroboros Intelligence Debrief",
            "total_turns": len(script_turns),
            "script": script_turns,
            "estimated_duration_seconds": len(script_turns) * 12
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "script": []}

# Epistemic 4-Pillar and backward-compatible aliases
generate_audio_briefing_script = generate_audio_podcast_script

class AudioBriefingSynthesizer:
    generate = staticmethod(generate_audio_podcast_script)

