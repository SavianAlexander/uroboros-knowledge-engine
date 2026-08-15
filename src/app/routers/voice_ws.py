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

        while True:
            # Receive message (JSON text command or binary PCM audio)
            message = await websocket.receive()
            if "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                except Exception:
                    payload = {"action": "say", "text": message["text"]}

                action = payload.get("action", "turn")
                text = payload.get("text", "")
                persona = payload.get("persona")
                dsp_preset = payload.get("dsp_preset")

                if action in ("turn", "say", "command"):
                    turn_res = VoiceAgentLoop.process_spoken_turn(
                        user_input_text=text,
                        session_id=session_id,
                        persona=persona,
                        dsp_preset=dsp_preset
                    )
                    await websocket.send_json({
                        "event": "turn_complete",
                        "data": turn_res
                    })

                elif action == "ping":
                    await websocket.send_json({"event": "pong", "timestamp": time.time()})

                elif action == "history":
                    hist = VoiceAgentLoop.get_session_history(session_id)
                    await websocket.send_json({"event": "history", "data": hist})

            elif "bytes" in message and message["bytes"]:
                # Binary audio telemetry: compute FFT spectrum
                try:
                    import numpy as np
                    samples = np.frombuffer(message["bytes"], dtype=np.int16).astype(np.float32) / 32768.0
                    fft_res = VoiceSpectrumAnalyzer.compute_spectrum_bins(samples)
                    await websocket.send_json({
                        "event": "spectrum_telemetry",
                        "data": fft_res
                    })
                except Exception:
                    pass

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
