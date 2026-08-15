"""
FastAPI Router for Universal Neural Voice Bridge & OpenAI-Compatible Audio API.
Standard: Pure Python Standard Library + FastAPI.
Ponytail Senior Dev Principle: Drop-in /v1/audio/speech compatibility for any AI client or agent framework.
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io
import json

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES, KOKORO_PERSONAS
from src.core.voice_streaming import StreamingNeuralSynthesizer, StreamingAudioCache

router = APIRouter(tags=["Universal Voice Bridge"])


class OpenAISpeechRequest(BaseModel):
    model: Optional[str] = "kokoro"
    input: str
    voice: Optional[str] = "CORTANA_PRIME"
    response_format: Optional[str] = "wav"
    speed: Optional[float] = 1.0
    dsp_preset: Optional[str] = "STUDIO_MASTER"


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
    Standard OpenAI-compatible Audio API drop-in endpoint with Studio DSP Mastering.
    Accepts OpenAI TTS JSON and returns binary streaming audio.
    """
    try:
        audio_bytes = VoiceBridge.synthesize_bytes(
            text=req.input,
            voice=req.voice or "CORTANA_PRIME",
            speed=req.speed or 1.0,
            response_format=req.response_format or "wav",
            dsp_preset=req.dsp_preset or "STUDIO_MASTER"
        )
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Voice synthesis failed.")

        media_type = "audio/mpeg" if req.response_format == "mp3" else "audio/wav"
        return Response(content=audio_bytes, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/audio/speech/stream")
@router.post("/api/voice/stream")
def streaming_speech_endpoint(req: OpenAISpeechRequest):
    """
    Real-time streaming clause-by-clause neural TTS endpoint.
    Yields newline-delimited JSON (NDJSON) chunks with base64 audio frames and metadata.
    Allows clients to start playback in ~150-250ms on long documents.
    """
    try:
        def event_generator():
            for chunk in StreamingNeuralSynthesizer.stream_speech_chunks(
                text=req.input,
                voice=req.voice or "CORTANA_PRIME",
                speed=req.speed or 1.0,
                dsp_preset=req.dsp_preset or "STUDIO_MASTER"
            ):
                yield json.dumps(chunk) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/voice/cache/clear")
def clear_voice_cache_endpoint():
    """Clear in-memory LRU audio cache."""
    StreamingAudioCache.clear()
    return {"status": "success", "message": "In-memory voice cache cleared."}



@router.get("/v1/audio/voices")
@router.get("/api/voice/personas")
def list_voices_endpoint():
    """List available signature voice personas and DSP mastering presets."""
    try:
        from src.core.voice_persona_blend import SIGNATURE_PERSONA_BLENDS
    except Exception:
        SIGNATURE_PERSONA_BLENDS = {}

    dsp_presets = [
        {"id": "STUDIO_MASTER", "name": "Studio Master (Cortana Broadcast)", "description": "4-Band Mastering EQ, Studio Compressor, De-Esser & Subtle Holographic Presence"},
        {"id": "HOLOGRAPHIC_AI", "name": "Holographic AI (3D Spatial)", "description": "Air Presence EQ with Haas 3D Spatial Stereo Widener"},
        {"id": "AURA_COCKPIT", "name": "Aura Cockpit (Starship Bridge)", "description": "Naval AI Crystalline Voice with Multi-Tap Bridge Reverb"},
        {"id": "TACTICAL_RADIO", "name": "Tactical Radio (Military Comms)", "description": "VHF Bandpass Filter with Tactical Start Chirp and End Squelch Burst"},
        {"id": "STUDIO_DIRECT", "name": "Studio Direct (Raw Neural)", "description": "Uncolored Direct Neural PCM Audio"}
    ]

    personas = [
        {"id": "CORTANA_PRIME", "name": "Cortana Prime (Halo AI)", "category": "Signature", "description": "Articulate, crystalline, warm Cortana AI persona"},
        {"id": "AURA_SHIP_AI", "name": "Aura Ship AI (British Naval)", "category": "Signature", "description": "Authoritative crystalline starship bridge AI"},
        {"id": "EXECUTIVE_ADVISOR", "name": "Executive Advisor (Warm Productivity)", "category": "Signature", "description": "Engaging, natural executive briefing tone"},
        {"id": "TACTICAL_OFFICER", "name": "Tactical Officer (Command)", "category": "Signature", "description": "Deep, resonant tactical commanding officer"},
        {"id": "af_sky", "name": "Kokoro Sky (Clear US Female)", "category": "Base", "description": "Base Kokoro clear American female"},
        {"id": "af_bella", "name": "Kokoro Bella (Warm US Female)", "category": "Base", "description": "Base Kokoro warm American female"},
        {"id": "bf_emma", "name": "Kokoro Emma (British Female)", "category": "Base", "description": "Base Kokoro British female"}
    ]

    return {
        "status": "success",
        "default_voice": "CORTANA_PRIME",
        "default_dsp": "STUDIO_MASTER",
        "personas": personas,
        "signature_blends": SIGNATURE_PERSONA_BLENDS,
        "dsp_presets": dsp_presets,
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
