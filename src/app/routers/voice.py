"""
FastAPI Router for Universal Neural Voice Bridge & OpenAI-Compatible Audio API.
Standard: Pure Python Standard Library + FastAPI.
Ponytail Senior Dev Principle: Drop-in /v1/audio/speech compatibility for any AI client or agent framework.
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES, KOKORO_PERSONAS

router = APIRouter(tags=["Universal Voice Bridge"])


class OpenAISpeechRequest(BaseModel):
    model: Optional[str] = "kokoro"
    input: str
    voice: Optional[str] = "bf_emma"
    response_format: Optional[str] = "wav"
    speed: Optional[float] = 1.0


class UniversalSpeakRequest(BaseModel):
    text: str
    domain: Optional[str] = "GENERAL"
    priority: Optional[str] = "NORMAL"
    voice: Optional[str] = None
    dsp_preset: Optional[str] = None
    sfx_intro: Optional[str] = None


# ----------------------------------------------------------------------
# 1. Standard OpenAI-Compatible Audio API
# ----------------------------------------------------------------------
@router.post("/v1/audio/speech")
def openai_speech_endpoint(req: OpenAISpeechRequest):
    """
    Standard OpenAI-compatible Audio API drop-in endpoint.
    Accepts OpenAI TTS JSON and returns binary streaming audio.
    """
    try:
        audio_bytes = VoiceBridge.synthesize_bytes(
            text=req.input,
            voice=req.voice or "bf_emma",
            speed=req.speed or 1.0,
            response_format=req.response_format or "wav"
        )
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Voice synthesis failed.")

        media_type = "audio/mpeg" if req.response_format == "mp3" else "audio/wav"
        return Response(content=audio_bytes, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/audio/voices")
def list_voices_endpoint():
    """List available voice personas and domain profiles."""
    return {
        "voices": [
            {"id": code, "name": name, "model": "kokoro-82m"}
            for name, code in KOKORO_PERSONAS.items()
        ],
        "domain_profiles": DOMAIN_PROFILES
    }


# ----------------------------------------------------------------------
# 2. Universal Domain Voice Bridge Endpoints
# ----------------------------------------------------------------------
@router.post("/api/voice/speak")
def universal_speak_endpoint(req: UniversalSpeakRequest):
    """Universal 1-line speech dispatch endpoint for multi-domain agents."""
    try:
        res = VoiceBridge.speak(
            text=req.text,
            domain=req.domain or "GENERAL",
            priority=req.priority or "NORMAL",
            voice=req.voice,
            dsp_preset=req.dsp_preset,
            sfx_intro=req.sfx_intro
        )
        return {"status": "success", "record": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/voice/sfx/{sfx_name}")
def get_sfx_endpoint(sfx_name: str):
    """Stream procedural tactical SFX."""
    try:
        wav_bytes = VoiceBridge.play_sfx(sfx_name)
        if not wav_bytes:
            raise HTTPException(status_code=404, detail=f"SFX '{sfx_name}' not found.")
        return Response(content=wav_bytes, media_type="audio/wav")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/voice/profiles")
def get_profiles_endpoint():
    """Get all domain profiles and active configuration."""
    return {
        "status": "success",
        "domain_profiles": DOMAIN_PROFILES,
        "personas": KOKORO_PERSONAS
    }
