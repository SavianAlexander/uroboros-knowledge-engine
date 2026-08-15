"""
Real-Time Conversational Voice & Audio Spectrum WebSocket Router.
Endpoint: /ws/voice/call
Standard: Pure FastAPI WebSocket + VoiceActivityInterrupter + VoiceDSP + AuditHashchain.
"""

import json
import time
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.voice_dsp import VoiceDSP
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.audit_hashchain import GLOBAL_AUDIT_HASHCHAIN

router = APIRouter(tags=["voice-ws"])


@router.websocket("/ws/voice/call")
async def voice_call_websocket(websocket: WebSocket):
    """Full-duplex real-time audio WebSocket for live call sessions, VAD barge-in, and FFT spectral feeds."""
    await websocket.accept()
    session_id = f"ws_call_{int(time.time())}"
    
    GLOBAL_AUDIT_HASHCHAIN.append_event(
        event_type="WS_CALL_CONNECTED",
        payload={"session_id": session_id},
        actor="CLIENT_WEBSOCKET"
    )

    try:
        await websocket.send_json({
            "event": "CONNECTED",
            "session_id": session_id,
            "status": "ready",
            "sample_rate": 24000,
            "available_presets": list(VoiceDSP.get_available_presets().keys())
        })

        while True:
            # Handle incoming WebSocket message (text or binary)
            message = await websocket.receive()
            
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                except Exception:
                    data = {"action": message["text"]}

                action = data.get("action", "")

                if action == "ping":
                    await websocket.send_json({"event": "PONG", "timestamp": time.time()})

                elif action == "barge_in":
                    cut = VoiceActivityInterrupter.execute_instant_barge_in()
                    GLOBAL_AUDIT_HASHCHAIN.append_event(
                        event_type="BARGE_IN_TRIGGERED",
                        payload={"session_id": session_id, "cut": cut},
                        actor="CLIENT_USER"
                    )
                    await websocket.send_json({"event": "BARGE_IN_CONFIRMED", "result": cut})

                elif action == "get_spectrum":
                    spectrum = VoiceDSP.get_latest_spectrum()
                    await websocket.send_json({"event": "SPECTRUM_FRAME", "spectrum": spectrum})

                elif action == "call_status":
                    status = VoiceCallIntercomEngine.get_call_status()
                    await websocket.send_json({"event": "CALL_STATUS", "status": status})

            elif "bytes" in message:
                # Binary PCM audio frame received from user mic
                raw_bytes = message["bytes"]
                # Process audio chunk for VAD
                cut_needed = False
                try:
                    import numpy as np
                    samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    vad_res = VoiceActivityInterrupter.get_vad().analyze_frame(samples)
                    if vad_res["is_speech"] and VoiceCallIntercomEngine.get_call_status()["ai_speaking"]:
                        VoiceActivityInterrupter.execute_instant_barge_in()
                        cut_needed = True
                except Exception:
                    pass

                if cut_needed:
                    await websocket.send_json({"event": "VAD_BARGE_IN_CUT", "reason": "user_speech_detected"})

    except WebSocketDisconnect:
        GLOBAL_AUDIT_HASHCHAIN.append_event(
            event_type="WS_CALL_DISCONNECTED",
            payload={"session_id": session_id},
            actor="CLIENT_WEBSOCKET"
        )
    except Exception as exc:
        GLOBAL_AUDIT_HASHCHAIN.append_event(
            event_type="WS_CALL_ERROR",
            payload={"session_id": session_id, "error": str(exc)},
            actor="SERVER_EXCEPTION"
        )
