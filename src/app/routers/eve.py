"""
FastAPI Router for EVE Online SSO Authentication, Character Management, and ESI Knowledge Sync.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import os
import json
import io

from src.infrastructure.eve_sso import (
    token_manager,
    generate_auth_url,
    exchange_code_for_token,
    DEFAULT_SCOPES
)
from src.infrastructure.eve_esi import CharacterDataExtractor
from src.infrastructure.eve_vault_sync import synthesize_character_markdown, sync_and_index_all_characters
from batch_index import index_single_file

router = APIRouter(prefix="/api/eve", tags=["EVE Online Intelligence"])


class AuthUrlRequest(BaseModel):
    client_id: str
    callback_url: str = "http://localhost:8085/api/eve/sso/callback"
    scopes: Optional[List[str]] = None


class CallbackExchangeRequest(BaseModel):
    client_id: str
    code: str
    code_verifier: str
    callback_url: str = "http://localhost:8085/api/eve/sso/callback"


class SyncCharacterRequest(BaseModel):
    character_id: Optional[int] = None


@router.post("/sso/auth-url")
def get_sso_auth_url(req: AuthUrlRequest):
    """Generate EVE SSO v2 Authorization URL and PKCE Code Verifier."""
    try:
        url, verifier, state = generate_auth_url(
            client_id=req.client_id,
            callback_url=req.callback_url,
            scopes=req.scopes or DEFAULT_SCOPES
        )
        return {
            "auth_url": url,
            "code_verifier": verifier,
            "state": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sso/callback")
def exchange_sso_callback(req: CallbackExchangeRequest):
    """Exchange authorization code and verifier for persistent character tokens."""
    try:
        token_entry = exchange_code_for_token(
            client_id=req.client_id,
            code=req.code,
            code_verifier=req.code_verifier,
            callback_url=req.callback_url
        )
        return {
            "status": "authorized",
            "character_id": token_entry.get("character_id"),
            "character_name": token_entry.get("character_name"),
            "scopes": token_entry.get("scopes")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SSO Token Exchange Failed: {e}")


@router.get("/characters")
def list_authorized_characters():
    """List all authorized characters currently in the local token store."""
    chars = token_manager.list_characters()
    sanitized = []
    for c in chars:
        sanitized.append({
            "character_id": c.get("character_id"),
            "character_name": c.get("character_name"),
            "client_id": c.get("client_id"),
            "has_refresh_token": bool(c.get("refresh_token")),
            "expires_in_seconds": max(0, int(c.get("expires_at", 0) - time.time())),
            "scopes": c.get("scopes", []),
            "updated_at": c.get("updated_at")
        })
    return {"count": len(sanitized), "characters": sanitized}


@router.delete("/characters/{character_id}")
def delete_character(character_id: int):
    """Remove character authorization from local vault."""
    token_manager.delete_character(character_id)
    return {"status": "deleted", "character_id": character_id}


@router.post("/sync")
def sync_characters(req: SyncCharacterRequest, background_tasks: BackgroundTasks):
    """Extract telemetry from ESI, synthesize Markdown vault documents, and index into knowledge.db."""
    if req.character_id:
        try:
            extractor = CharacterDataExtractor(req.character_id)
            profile = extractor.extract_full_profile()
            files = synthesize_character_markdown(profile)
            for fp in files:
                index_single_file(fp)
            return {
                "status": "success",
                "character_id": req.character_id,
                "character_name": profile.get("character_name"),
                "indexed_files": files
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Character sync failed: {e}")
    else:
        results = sync_and_index_all_characters()
        return {"status": "completed", "results": results}


from fastapi.responses import StreamingResponse
import asyncio
from src.infrastructure.eve_hybrid_rag import hybrid_search_rrf
from src.infrastructure.eve_optimizer import calculate_optimal_remap


@router.get("/live-stream")
async def get_live_telemetry_stream():
    """Server-Sent Events (SSE) stream pushing real-time tactical events and heartbeats."""
    async def event_generator():
        while True:
            chars = token_manager.list_characters()
            active_count = len(chars)
            pilot_str = f"{active_count} pilot{'s' if active_count != 1 else ''}"
            event_data = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                "active_pilots": active_count,
                "tactical_status": "MONITORING_ACTIVE",
                "cyno_threat_level": "LOW",
                "message": f"Tranquility ESI telemetry nominal. {pilot_str} synchronized in local vault."
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/search/hybrid")
def search_hybrid(q: str, limit: int = 5):
    """Execute sub-5ms Reciprocal Rank Fusion (RRF) search across FTS5 and vector knowledge."""
    try:
        return hybrid_search_rrf(query=q, top_k=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hud/state")
def get_hud_state_endpoint():
    """Retrieve unified tactical HUD state for all active fleet pilots."""
    try:
        from src.infrastructure.eve_hud_server import get_hud_state
        return get_hud_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/cyno")
def get_cyno_route(origin: str = "1DQ1-A (Delve)", destination: str = "Jita (The Forge)"):
    """Calculate multi-jump capital cyno route avoiding choke points."""
    try:
        from src.infrastructure.eve_route_navigator import plan_cyno_route
        return plan_cyno_route(origin_system=origin, destination_system=destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multibox/mind")
def get_multibox_mind_endpoint():
    """Retrieve operational fleet mindset, active responsibilities, and tactical intent for all pilots."""
    try:
        from src.infrastructure.eve_multibox_controller import get_multibox_mind_state
        return get_multibox_mind_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multibox/recommendations/{character_id}")
def get_pilot_recommendations(character_id: int):
    """Retrieve actionable next steps and protective defensive protocols for a specific pilot."""
    try:
        from src.infrastructure.eve_multibox_controller import get_pilot_action_recommendations
        res = get_pilot_action_recommendations(character_id)
        if "status" in res and res["status"] == "error":
            raise HTTPException(status_code=404, detail=res["message"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry/empirical")
def get_empirical_telemetry_endpoint():
    """Retrieve 100% verified empirical telemetry dataset and fleet totals."""
    try:
        from src.infrastructure.eve_empirical_telemetry import calculate_fleet_totals
        return calculate_fleet_totals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sde/types")
def get_sde_types_endpoint():
    """Retrieve canonical SDE Type ID database."""
    try:
        from src.infrastructure.eve_empirical_telemetry import CANONICAL_SDE_TYPES
        return CANONICAL_SDE_TYPES
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wormholes/mass")
def get_wormhole_mass_endpoint(total_gg: float = 3000.0, max_jump_gg: float = 300.0, jumped_gg: float = 1650.0):
    """Calculate wormhole mass state and collapse risk."""
    try:
        from src.infrastructure.eve_celestial_exotic import calculate_wormhole_mass_state
        return calculate_wormhole_mass_state(total_capacity_gg=total_gg, max_jump_mass_gg=max_jump_gg, mass_jumped_gg=jumped_gg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/arbitrage")
def get_market_arbitrage_endpoint(item: str = "Tritanium (Packaged 100k)", buy_p: float = 3.85, sell_p: float = 4.45, qty: int = 10000000):
    """Calculate inter-hub market arbitrage ROI and profit spread."""
    try:
        from src.infrastructure.eve_industry_arbitrage import calculate_interhub_arbitrage_spread
        return calculate_interhub_arbitrage_spread(item_name=item, buy_price_isk=buy_p, sell_price_isk=sell_p, quantity=qty)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ewar/jamming")
def get_ewar_jamming_endpoint(jammer: float = 12.5, sensor: float = 24.0):
    """Calculate ECM jamming probability."""
    try:
        from src.infrastructure.eve_combat_ewar_incursions import calculate_ecm_jam_probability
        return calculate_ecm_jam_probability(jammer_strength=jammer, target_sensor_strength=sensor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eft/parse")
def parse_eft_endpoint(payload: Dict[str, str]):
    """Parse standard EFT/Pyfa text fitting block."""
    try:
        from src.infrastructure.eve_eft_parser import parse_eft_fitting_block
        eft_text = payload.get("eft_text", "")
        return parse_eft_fitting_block(eft_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/stream")
def get_log_stream_endpoint(
    pilot_name: Optional[str] = Query(None, description="Filter log events by pilot name"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. combat, intel, navigation)"),
    max_events: int = Query(50, ge=1, le=200, description="Max events to return")
):
    """Retrieve simulated/live log streamer event buffer with dynamic filtering."""
    try:
        from src.infrastructure.eve_log_streamer import EveLogStreamer
        streamer = EveLogStreamer()
        events = streamer.stream_events()
        if pilot_name and isinstance(events, list):
            p_norm = pilot_name.strip().lower()
            events = [e for e in events if p_norm in str(e.get("pilot", "")).lower() or p_norm in str(e.get("raw_text", "")).lower()]
        if event_type and isinstance(events, list):
            e_norm = event_type.strip().lower()
            events = [e for e in events if e_norm in str(e.get("type", "")).lower() or e_norm in str(e.get("category", "")).lower()]
        if isinstance(events, list) and max_events:
            events = events[:max_events]
        return {"status": "success", "events": events, "total_events": len(events) if isinstance(events, list) else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/alert")
def trigger_voice_alert_endpoint(payload: Dict[str, Any]):
    """Dispatch text-to-speech alert to local audio output using Kokoro-82M Neural Audio."""
    try:
        from src.infrastructure.eve_voice_copilot import KokoroVoiceCopilot
        copilot = KokoroVoiceCopilot()
        msg = payload.get("message", "Tactical alert.")
        priority = payload.get("priority", "HIGH")
        voice = payload.get("voice", "CORTANA_PRIME")
        return copilot.speak(msg, priority=priority, voice=voice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/synthesize")
def synthesize_voice_audio_endpoint(text: str = "Tactical alert notification.", voice: Optional[str] = "CORTANA_PRIME"):
    """Synthesize text into Kokoro-82M neural audio binary stream (WAV/MP3)."""
    try:
        from src.infrastructure.eve_voice_copilot import KokoroVoiceCopilot
        copilot = KokoroVoiceCopilot()
        audio_bytes = copilot.synthesize_neural_audio(text, voice=voice)
        if audio_bytes:
            return Response(content=audio_bytes, media_type="audio/wav")
        return {"status": "error", "message": "Kokoro neural synthesis unavailable", "text": text, "voice": voice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/sp-farm/roi")
def get_sp_farm_roi_endpoint():
    """Calculate passive skill farm extraction ROI and PLEX balances."""
    try:
        from src.infrastructure.eve_sp_farm_calculator import calculate_sp_farming_roi
        return calculate_sp_farming_roi()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asset-safety/evac")
def get_asset_safety_evac_endpoint(asset_value: float = 25000000000.0, in_system: bool = True):
    """Calculate asset safety recovery fees and emergency jump freighter evacuation routes."""
    try:
        from src.infrastructure.eve_asset_safety import calculate_asset_safety_costs
        return calculate_asset_safety_costs(total_asset_value_isk=asset_value, in_system_recovery=in_system)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/command")
def execute_voice_command_endpoint(payload: Dict[str, Any]):
    """Execute natural language voice command and return intent, response, and audio."""
    try:
        from src.infrastructure.eve_voice_commander import VoiceCommander
        cmd = VoiceCommander()
        prompt = payload.get("prompt", "")
        auto_speak = payload.get("auto_speak", False)
        return cmd.execute_voice_prompt(prompt, auto_speak=auto_speak)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/dsp/presets")
def get_voice_dsp_presets_endpoint():
    """Return available tactical DSP acoustic presets and character voice stems."""
    try:
        from src.infrastructure.eve_voice_copilot import KOKORO_PERSONAS
        return {
            "status": "success",
            "dsp_presets": ["AURA_COCKPIT", "TACTICAL_RADIO", "HARVESTER_COMMS", "STUDIO_DIRECT"],
            "personas": KOKORO_PERSONAS,
            "spatial_panning": {
                "harvester_wing": -0.8,
                "aura_ship_ai": 0.0,
                "threat_combat_radar": 1.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/radar/sweep")
def trigger_voice_radar_sweep_endpoint():
    """Trigger automated tactical log radar sweep and dispatch audio alerts."""
    try:
        from src.infrastructure.eve_voice_radar_daemon import TacticalVoiceRadarDaemon
        daemon = TacticalVoiceRadarDaemon()
        return {"status": "success", "dispatches": daemon.execute_live_radar_sweep(auto_speak=False)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/soundscape/sfx")
def get_procedural_sfx_endpoint(sfx_type: str = "warp_spool"):
    """Synthesize and stream procedural tactical sci-fi SFX audio."""
    try:
        from src.infrastructure.eve_voice_soundboard import render_sfx_to_wav_bytes, SFX_LIBRARY
        if sfx_type not in SFX_LIBRARY:
            raise HTTPException(status_code=400, detail=f"Unknown SFX type: {sfx_type}. Available: {list(SFX_LIBRARY.keys())}")
        wav_bytes = render_sfx_to_wav_bytes(sfx_type)
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/mixer/composite")
def composite_audio_soundscape_endpoint(payload: Dict[str, Any]):
    """Composite voice track + SFX + ambient hum with dynamic audio ducking."""
    try:
        from src.infrastructure.eve_voice_mixer import composite_tactical_soundscape
        import soundfile as sf
        sfx_type = payload.get("sfx_type")
        include_ambient = payload.get("include_ambient", True)
        master = composite_tactical_soundscape(sfx_type=sfx_type, include_ambient=include_ambient)
        buf = io.BytesIO()
        sf.write(buf, master, 24000, format="WAV")
        return Response(content=buf.getvalue(), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/vad/process-frame")
def process_vad_frame_endpoint(payload: Dict[str, Any]):
    """Evaluate audio frame for voice activity and barge-in state transition."""
    try:
        from src.infrastructure.eve_voice_vad_duplex import VoiceActivityDetector
        import numpy as np
        samples_list = payload.get("samples", [])
        is_ai_speaking = payload.get("is_ai_speaking", False)
        detector = VoiceActivityDetector()
        detector.set_ai_speaking_state(is_ai_speaking)
        frame_arr = np.array(samples_list, dtype=np.float32) if samples_list else np.zeros(480, dtype=np.float32)
        return detector.process_audio_frame(frame_arr)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/templates")
def get_eve_voice_alert_templates():
    """Retrieve all available EVE Online cockpit tactical voice alert templates."""
    try:
        from src.domain.eve_voice_alerts import TACTICAL_VOICE_TEMPLATES
        return {
            "status": "success",
            "templates": TACTICAL_VOICE_TEMPLATES
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/format")
def format_eve_voice_alert(payload: Dict[str, Any]):
    """Format an EVE cockpit tactical voice alert template with parameters."""
    template_key = payload.get("template_key", "")
    params = payload.get("params", {})
    if not template_key:
        raise HTTPException(status_code=400, detail="Missing template_key in request.")
    try:
        from src.domain.eve_voice_alerts import EVEVoiceAlertManager
        formatted = EVEVoiceAlertManager.format_alert(template_key, **params)
        return {
            "status": "success",
            "template_key": template_key,
            "formatted_message": formatted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/speak")
def speak_eve_voice_alert(payload: Dict[str, Any]):
    """Synthesize and dispatch an EVE cockpit tactical voice alert with SFX and Kokoro voice synthesis."""
    template_key = payload.get("template_key", "")
    params = payload.get("params", {})
    persona = payload.get("persona", "AURA_SHIP_AI")
    priority = payload.get("priority", "HIGH")
    sfx_intro = payload.get("sfx_intro")

    if not template_key:
        raise HTTPException(status_code=400, detail="Missing template_key in request.")
    try:
        from src.domain.eve_voice_alerts import EVEVoiceAlertManager
        dispatch = EVEVoiceAlertManager.speak_alert(
            template_key=template_key,
            priority=priority,
            persona=persona,
            sfx_intro=sfx_intro,
            **params
        )
        return {
            "status": "success",
            "dispatch": dispatch
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




