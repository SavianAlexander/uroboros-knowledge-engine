"""
WebSocket & Real-Time Audio Stream Router.
Standard: Pure Python Standard Library + FastAPI WebSockets.
Ponytail Senior Dev Principle: Ultra low-latency 60FPS binary telemetry and streaming audio chunks.
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from starlette.websockets import WebSocketState

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_agent_loop import VoiceAgentLoop
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer

router = APIRouter()
logger = logging = __import__("logging").getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None


async def _handle_ws_text_message(websocket: WebSocket, raw_text: str, session_id: str):
    """Handle incoming JSON text message in voice WebSocket stream."""
    try:
        payload = json.loads(raw_text)
    except Exception:
        payload = {"action": "say", "text": raw_text}

    action = payload.get("action", "turn")
    text = payload.get("text", "")
    persona = payload.get("persona")
    dsp_preset = payload.get("dsp_preset")

    if action in ("turn", "say", "command"):
        turn_res = await asyncio.to_thread(
            VoiceAgentLoop.process_spoken_turn,
            user_input_text=text,
            session_id=session_id,
            persona=persona,
            dsp_preset=dsp_preset
        )
        await websocket.send_json({
            "event": "turn_complete",
            "data": turn_res
        })
        return

    if action == "ping":
        await websocket.send_json({"event": "pong", "timestamp": time.time()})
        return

    if action == "history":
        hist = await asyncio.to_thread(VoiceAgentLoop.get_session_history, session_id)
        await websocket.send_json({"event": "history", "data": hist})


async def _handle_ws_bytes_message(websocket: WebSocket, raw_bytes: bytes):
    """Handle incoming binary PCM audio telemetry in voice WebSocket stream."""
    if np is None:
        return
    try:
        samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        fft_res = VoiceSpectrumAnalyzer.compute_spectrum_bins(samples)
        await websocket.send_json({
            "event": "spectrum_telemetry",
            "data": fft_res
        })
    except Exception:
        pass


async def _dispatch_ws_message(websocket: WebSocket, message: dict, session_id: str):
    """Dispatch WebSocket message to text or binary handler."""
    if text := message.get("text"):
        await _handle_ws_text_message(websocket, text, session_id)
    elif raw_bytes := message.get("bytes"):
        await _handle_ws_bytes_message(websocket, raw_bytes)


async def _ws_stream_loop(websocket: WebSocket, session_id: str):
    """Stream loop reading incoming WebSocket frames."""
    while True:
        message = await websocket.receive()
        await _dispatch_ws_message(websocket, message, session_id)


@router.websocket("/ws/voice/stream")
async def voice_streaming_websocket_endpoint(websocket: WebSocket):
    """
    Full-duplex WebSocket stream for hands-free neural voice conversations and FFT visualizer telemetry.
    """
    await websocket.accept()
    session_id = f"ws-voice-{int(time.time() * 1000)}"
    VoiceAgentLoop.start_session(session_id)

    try:
        # Send initial connected handshake
        await websocket.send_json({
            "event": "connected",
            "session_id": session_id,
            "timestamp": time.time()
        })
        await _ws_stream_loop(websocket, session_id)

    except WebSocketDisconnect:
        VoiceAgentLoop.end_session(session_id)
        logger.debug(f"Voice WebSocket disconnected: {session_id}")
    except Exception as e:
        VoiceAgentLoop.end_session(session_id)
        logger.debug(f"Voice WebSocket error: {e}")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()


@router.get("/api/voice/agent/history/{session_id}")
def get_voice_agent_session_history(session_id: str):
    """Retrieves session history for a multi-turn voice agent session."""
    return VoiceAgentLoop.get_session_history(session_id)


@router.post("/api/voice/agent/turn")
def execute_voice_agent_turn(payload: Dict[str, Any]):
    """Executes a single conversational turn in the hands-free voice agent loop."""
    text = payload.get("text", "")
    session_id = payload.get("session_id", f"http-session-{int(time.time())}")
    persona = payload.get("persona")
    dsp_preset = payload.get("dsp_preset")

    if not text:
        raise HTTPException(status_code=400, detail="Missing text parameter.")

    return VoiceAgentLoop.process_spoken_turn(
        user_input_text=text,
        session_id=session_id,
        persona=persona,
        dsp_preset=dsp_preset
    )
