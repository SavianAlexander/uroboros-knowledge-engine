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
    input: Optional[str] = None
    text: Optional[str] = None
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
# 1. Standard OpenAI-Compatible Audio & Voice Synthesize API
# ----------------------------------------------------------------------
@router.post("/v1/audio/speech")
@router.post("/api/voice/synthesize")
def openai_speech_endpoint(req: OpenAISpeechRequest):
    """
    Standard OpenAI-compatible Audio API drop-in endpoint with Studio DSP Mastering.
    Accepts OpenAI TTS JSON and returns binary streaming audio.
    """
    try:
        raw_text = req.input or req.text or ""
        if not raw_text:
            raise HTTPException(status_code=422, detail="Missing input text for voice synthesis.")

        audio_bytes = VoiceBridge.synthesize_bytes(
            text=raw_text,
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



class CustomPersonaRequest(BaseModel):
    name: str
    weights: Dict[str, float]
    dsp_preset: Optional[str] = "EXECUTIVE_PRECISION"
    description: Optional[str] = ""


class VoicePreviewRequest(BaseModel):
    text: Optional[str] = "Command recognized. Power and intent online."
    voice: Optional[str] = None
    weights: Optional[Dict[str, float]] = None
    dsp_preset: Optional[str] = "EXECUTIVE_PRECISION"
    speed: Optional[float] = 0.92


@router.get("/v1/audio/voices")
@router.get("/api/voice/personas")
def list_voices_endpoint():
    """List available signature voice personas and DSP mastering presets."""
    try:
        from src.core.voice_persona_blend import VoicePersonaBlender, SIGNATURE_PERSONA_BLENDS
        all_blends = VoicePersonaBlender.get_preset_blends()
    except Exception:
        all_blends = {}

    dsp_presets = [
        {"id": "EXECUTIVE_PRECISION", "name": "Executive Precision (Sub-Harmonic Chest & Tube Warmth)", "description": "Visceral chest thump, magnetic tube saturation, dynamic limiter & 3D spatial air."},
        {"id": "STOIC_GRAVITAS", "name": "Stoic Gravitas (Kratos / Master Chief)", "description": "Maximum sub-bass chest resonance, analog tube drive & intimate proximity leveler."},
        {"id": "MAGNETIC_INTIMATE", "name": "Magnetic Intimate (Velvet Warmth)", "description": "Velvet mid-range tube saturation, vocal presence & Haas 3D stereo widener."},
        {"id": "STUDIO_MASTER", "name": "Studio Master (Cortana Broadcast)", "description": "4-Band Mastering EQ, Studio Compressor, De-Esser & Subtle Holographic Presence."},
        {"id": "HOLOGRAPHIC_AI", "name": "Holographic AI (3D Spatial)", "description": "Air Presence EQ with Haas 3D Spatial Stereo Widener."},
        {"id": "AURA_COCKPIT", "name": "Aura Cockpit (Starship Bridge)", "description": "Naval AI Crystalline Voice with Multi-Tap Bridge Reverb."},
        {"id": "TACTICAL_RADIO", "name": "Tactical Radio (Military Comms)", "description": "VHF Bandpass Filter with Tactical Start Chirp and End Squelch Burst."},
        {"id": "STUDIO_DIRECT", "name": "Studio Direct (Raw Neural)", "description": "Uncolored Direct Neural PCM Audio."}
    ]

    personas = [
        # Executive & Command Tier
        {"id": "ALEXANDER_SOVEREIGN", "name": "Alexander (Executive Command)", "category": "Executive", "description": "Deep baritone, resonant chest power & vocal authority."},
        {"id": "FREYA_VALKYRIE", "name": "Freya (Resolute Command)", "category": "Executive", "description": "Crystalline, articulate noble authority & clarity."},
        {"id": "AURELIUS_STOIC", "name": "Aurelius (Stoic Presence)", "category": "Executive", "description": "Resonant low-end presence, deliberate pacing & philosophical depth."},
        {"id": "NOCTURNA_SOLON", "name": "Nocturna (Strategic Analysis)", "category": "Executive", "description": "Focused, articulate analysis & strategic gravitas."},
        
        # Classic AI & Signature Tier
        {"id": "CORTANA_PRIME", "name": "Cortana Prime (Halo AI)", "category": "Signature", "description": "Articulate, crystalline, warm Cortana AI persona."},
        {"id": "AURA_SHIP_AI", "name": "Aura Ship AI (British Naval)", "category": "Signature", "description": "Authoritative crystalline starship bridge AI."},
        {"id": "EXECUTIVE_ADVISOR", "name": "Executive Advisor (Warm Productivity)", "category": "Signature", "description": "Engaging, natural executive briefing tone."},
        {"id": "TACTICAL_OFFICER", "name": "Tactical Officer (Command)", "category": "Signature", "description": "Deep, resonant tactical commanding officer."},
        
        # Base Kokoro Embeddings
        {"id": "am_adam", "name": "Kokoro Adam (Deep US Male)", "category": "Base", "description": "Deep resonant American male baritone."},
        {"id": "bm_george", "name": "Kokoro George (Commanding UK Male)", "category": "Base", "description": "Commanding authoritative British male."},
        {"id": "bf_emma", "name": "Kokoro Emma (Crystalline UK Female)", "category": "Base", "description": "Crystalline, articulate British female."},
        {"id": "af_sky", "name": "Kokoro Sky (Clear US Female)", "category": "Base", "description": "Clear, bright American female."},
        {"id": "af_bella", "name": "Kokoro Bella (Warm US Female)", "category": "Base", "description": "Warm, velvety American female."}
    ]

    return {
        "status": "success",
        "default_voice": "ALEXANDER_SOVEREIGN",
        "default_dsp": "EXECUTIVE_PRECISION",
        "personas": personas,
        "signature_blends": all_blends,
        "dsp_presets": dsp_presets,
        "domain_profiles": DOMAIN_PROFILES
    }


# ----------------------------------------------------------------------
# 2. Custom Persona CRUD & Preview
# ----------------------------------------------------------------------
@router.get("/api/voice/custom-personas")
def list_custom_personas():
    """List all saved custom user personas."""
    try:
        from src.core.voice_persona_blend import VoicePersonaBlender
        custom = VoicePersonaBlender.load_custom_personas()
        return {"status": "success", "personas": custom}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/voice/custom-personas")
def save_custom_persona_endpoint(req: CustomPersonaRequest):
    """Save a user-created custom sovereign persona."""
    try:
        from src.core.voice_persona_blend import VoicePersonaBlender
        res = VoicePersonaBlender.save_custom_persona(
            name=req.name,
            weights=req.weights,
            dsp_preset=req.dsp_preset or "EXECUTIVE_PRECISION",
            description=req.description or ""
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/voice/custom-personas/{persona_id}")
def delete_custom_persona_endpoint(persona_id: str):
    """Delete a custom persona."""
    try:
        from src.core.voice_persona_blend import VoicePersonaBlender
        deleted = VoicePersonaBlender.delete_custom_persona(persona_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Persona not found.")
        return {"status": "success", "message": f"Persona '{persona_id}' deleted."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/voice/preview")
def preview_voice_endpoint(req: VoicePreviewRequest):
    """Instant low-latency audio preview for any custom blend or preset."""
    try:
        target_voice = req.weights if req.weights else (req.voice or "ALEXANDER_SOVEREIGN")
        audio_bytes = VoiceBridge.synthesize_bytes(
            text=req.text or "Command recognized. Power and intent online.",
            voice=target_voice,
            speed=req.speed or 0.92,
            response_format="wav",
            dsp_preset=req.dsp_preset or "EXECUTIVE_PRECISION"
        )
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Preview synthesis failed.")
        return Response(content=audio_bytes, media_type="audio/wav")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




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


@router.get("/api/voice/hardware")
def get_voice_hardware_endpoint():
    """Get neural voice engine hardware acceleration and execution provider telemetry."""
    copilot = VoiceBridge.get_copilot()
    if not copilot:
        return {"status": "error", "message": "Voice engine not initialized"}
    info = copilot.get_hardware_acceleration_info()
    return {"status": "success", **info}


class VoiceIntercomTurnRequest(BaseModel):
    prompt: str
    persona: Optional[str] = "AURA_SHIP_AI"
    dsp_preset: Optional[str] = "HOLOGRAPHIC_AURA"
    use_rag: Optional[bool] = True


@router.post("/api/voice/intercom/turn")
def voice_intercom_turn_endpoint(req: VoiceIntercomTurnRequest):
    """
    Real-time full-duplex conversational turn endpoint.
    Retrieves facts from SOTA RAG, normalizes text for speech, synthesizes Kokoro audio in RAM,
    and returns base64 WAV payload + citations for instant browser/client playback.
    """
    import base64
    from src.core.voice_rag_bridge import VoiceRAGBridge
    from src.core.voice_normalizer import VoiceNormalizer

    try:
        t0 = time.perf_counter()
        if req.use_rag:
            summary = VoiceRAGBridge.query_and_summarize(req.prompt, max_sentences=2)
            speech_text = summary["speech_text"]
            citations = summary.get("citations", [])
            retrieval_ms = summary.get("retrieval_ms", 0)
        else:
            speech_text = req.prompt
            citations = []
            retrieval_ms = 0

        clean_text = VoiceNormalizer.normalize_for_speech(speech_text)
        voice_id = KOKORO_PERSONAS.get(req.persona, "bf_emma")

        audio_bytes = VoiceBridge.synthesize_bytes(
            text=clean_text,
            voice=voice_id,
            speed=1.0,
            response_format="wav",
            dsp_preset=req.dsp_preset or "HOLOGRAPHIC_AURA"
        )

        audio_b64 = base64.b64encode(audio_bytes).decode("ascii") if audio_bytes else ""
        turnaround_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "status": "success",
            "prompt": req.prompt,
            "speech_text": speech_text,
            "normalized_text": clean_text,
            "persona": req.persona,
            "citations": citations,
            "retrieval_ms": retrieval_ms,
            "turnaround_ms": turnaround_ms,
            "audio_base64": audio_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PodcastDialogueRequest(BaseModel):
    turns: List[Dict[str, str]]
    pause_duration_s: Optional[float] = 0.35
    play_live: Optional[bool] = False


@router.post("/api/voice/podcast/generate")
def generate_podcast_endpoint(req: PodcastDialogueRequest):
    """Synthesize multi-persona roundtable audio dialogue."""
    from src.core.voice_podcast_generator import VoicePodcastGenerator
    try:
        res = VoicePodcastGenerator.synthesize_dialogue(
            turns=req.turns,
            pause_duration_s=req.pause_duration_s or 0.35,
            play_live=req.play_live or False
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class STTListenRequest(BaseModel):
    duration_seconds: Optional[float] = 3.0
    language: Optional[str] = "en"


@router.post("/api/voice/stt/listen")
def stt_listen_endpoint(req: STTListenRequest):
    """Record live microphone audio and transcribe speech into text."""
    from src.core.voice_stt_ear import VoiceEarTranscriber
    try:
        return VoiceEarTranscriber.listen_and_transcribe(
            duration_s=req.duration_seconds or 3.0,
            language=req.language or "en"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/voice/vault/scan")
def vault_scan_endpoint():
    """Trigger incremental filesystem delta scan and auto-index into SQLite FTS5."""
    from src.infrastructure.vault_auto_watcher import VaultAutoWatcher
    try:
        watcher = VaultAutoWatcher()
        return watcher.scan_and_index_delta()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
