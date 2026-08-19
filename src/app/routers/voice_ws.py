"""
WebSocket & Real-Time Full-Duplex Audio Stream Router.
Standard: Pure Python Standard Library + FastAPI WebSockets + Kokoro-82M ONNX.
Ponytail Senior Dev Principle: Ultra-low latency (<300ms TTFS) full-duplex voice call engine, streaming VAD with 450ms silence hangover auto-endpointing, and sub-10ms instant barge-in task preemption.
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from starlette.websockets import WebSocketState

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_agent_loop import VoiceAgentLoop
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer
from src.core.voice_streaming_pipeline import VoiceStreamingPipeliner, LIVE_VOICE_SYSTEM_PROMPT
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.core.voice_stt_ear import VoiceEarTranscriber

router = APIRouter()
logger = logging = __import__("logging").getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None


class VoiceCallSessionState:
    """Manages active call session state per WebSocket connection."""

    def __init__(self, session_id: str, sample_rate: int = 24000):
        self.session_id = session_id
        self.sample_rate = sample_rate
        self.vad = VoiceActivityInterrupter(
            sample_rate=sample_rate,
            frame_duration_ms=20,
            energy_threshold=0.018,
            zcr_threshold=0.015,
            consecutive_frames_to_trigger=2,
            silence_hangover_ms=450.0
        )
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": LIVE_VOICE_SYSTEM_PROMPT}
        ]
        self.active_generation_task: Optional[asyncio.Task] = None
        self.is_assistant_speaking: bool = False
        self.persona: str = "af_heart"
        self.dsp_preset: str = "STUDIO_MASTER"

    def cancel_active_generation(self) -> bool:
        """Immediately cancel any running LLM / Kokoro synthesis task (<10ms)."""
        cancelled = False
        if self.active_generation_task is not None and not self.active_generation_task.done():
            self.active_generation_task.cancel()
            cancelled = True
        VoiceActivityInterrupter.execute_instant_barge_in()
        self.is_assistant_speaking = False
        return cancelled


async def _run_spoken_response_task(
    websocket: WebSocket,
    session: VoiceCallSessionState,
    persona: Optional[str] = None,
    dsp_preset: Optional[str] = None
):
    """Executes pipelined token-to-audio synthesis and streams frames over WebSocket."""
    session.is_assistant_speaking = True
    active_persona = persona or session.persona
    active_dsp = dsp_preset or session.dsp_preset

    try:
        res = await VoiceStreamingPipeliner.stream_chat_to_audio_ws(
            websocket=websocket,
            messages=session.messages,
            session_id=session.session_id,
            persona=active_persona,
            dsp_preset=active_dsp
        )
        if full_text := res.get("full_text"):
            session.messages.append({"role": "assistant", "content": full_text})
    except asyncio.CancelledError:
        logger.debug(f"Voice generation task cancelled for session {session.session_id}")
    except Exception as e:
        logger.debug(f"Voice generation task error: {e}")
    finally:
        session.is_assistant_speaking = False


async def _handle_ws_text_message(
    websocket: WebSocket,
    raw_text: str,
    session: VoiceCallSessionState
):
    """Handle incoming JSON text command / turn."""
    try:
        payload = json.loads(raw_text)
    except Exception:
        payload = {"action": "say", "text": raw_text}

    action = payload.get("action", "turn")
    text = payload.get("text", "")
    persona = payload.get("persona") or session.persona
    dsp_preset = payload.get("dsp_preset") or session.dsp_preset

    if action in ("call_start", "start"):
        await websocket.send_json({
            "event": "call_started",
            "session_id": session.session_id,
            "greeting": "Voice link established. Assistant online and listening."
        })
        return

    if action in ("barge_in", "interrupt", "stop"):
        session.cancel_active_generation()
        await websocket.send_json({
            "event": "interrupted",
            "session_id": session.session_id,
            "reason": "client_requested"
        })
        return

    if action in ("turn", "say", "command", "user_turn"):
        if not text:
            return
        # Cancel previous generation if still active
        session.cancel_active_generation()
        session.messages.append({"role": "user", "content": text})

        # Launch pipelined async generation task
        session.active_generation_task = asyncio.create_task(
            _run_spoken_response_task(websocket, session, persona, dsp_preset)
        )
        return

    if action == "ping":
        await websocket.send_json({"event": "pong", "timestamp": time.time()})
        return

    if action == "history":
        await websocket.send_json({"event": "history", "data": session.messages})


async def _handle_ws_bytes_message(
    websocket: WebSocket,
    raw_bytes: bytes,
    session: VoiceCallSessionState
):
    """
    Handle incoming binary PCM audio telemetry:
    1. Compute FFT spectrum telemetry for UI visualizer.
    2. Run 20ms RMS VAD frame analysis.
    3. If user speaks while assistant is speaking -> trigger instant barge-in preemption (<10ms).
    4. When 450ms silence hangover is reached -> auto-endpoint, transcribe, and launch response turn.
    """
    # 1. FFT visualizer telemetry
    if np is not None:
        try:
            samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            fft_res = VoiceSpectrumAnalyzer.compute_spectrum_bins(samples)
            await websocket.send_json({
                "event": "spectrum_telemetry",
                "data": fft_res
            })
        except Exception:
            pass

    # 2. VAD Streaming Analysis
    vad_res = session.vad.process_streaming_pcm_chunk(
        raw_pcm_bytes=raw_bytes,
        is_assistant_speaking=session.is_assistant_speaking
    )

    # 3. Barge-In Preemption
    if vad_res.get("barge_in_triggered"):
        session.cancel_active_generation()
        await websocket.send_json({
            "event": "interrupted",
            "session_id": session.session_id,
            "reason": "vad_barge_in",
            "latency_ms": vad_res.get("latency_ms", 1.0)
        })

    # 4. Auto-Endpointing (450ms silence hangover completed)
    if vad_res.get("endpoint_triggered"):
        speech_bytes = vad_res.get("speech_bytes")
        if speech_bytes and len(speech_bytes) >= 1600:
            await websocket.send_json({
                "event": "speech_endpoint",
                "session_id": session.session_id
            })

            # Transcribe captured turn
            user_text = ""
            try:
                import soundfile as sf
                scratch_dir = os.path.join(BASE_DIR, "scratch")
                os.makedirs(scratch_dir, exist_ok=True)
                scratch_wav = os.path.join(scratch_dir, f"vad_turn_{session.session_id}_{int(time.time()*1000)}.wav")
                
                if np is not None:
                    pcm_arr = np.frombuffer(speech_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    sf.write(scratch_wav, pcm_arr, session.sample_rate, format="WAV", subtype="PCM_16")
                
                trans_res = await asyncio.to_thread(VoiceEarTranscriber.transcribe_audio_file, scratch_wav)
                user_text = trans_res.get("text", "").strip()

                try:
                    if os.path.exists(scratch_wav):
                        os.remove(scratch_wav)
                except Exception:
                    pass
            except Exception:
                user_text = ""

            if user_text and user_text not in ("[Audio stream captured]", ""):
                await websocket.send_json({
                    "event": "transcription",
                    "session_id": session.session_id,
                    "text": user_text,
                    "role": "user"
                })
                session.cancel_active_generation()
                session.messages.append({"role": "user", "content": user_text})
                session.active_generation_task = asyncio.create_task(
                    _run_spoken_response_task(websocket, session)
                )

        session.vad.reset_turn()


async def _ws_stream_loop(websocket: WebSocket, session: VoiceCallSessionState):
    """Main stream loop reading incoming WebSocket frames."""
    while True:
        message = await websocket.receive()
        if text := message.get("text"):
            await _handle_ws_text_message(websocket, text, session)
        elif raw_bytes := message.get("bytes"):
            await _handle_ws_bytes_message(websocket, raw_bytes, session)


@router.websocket("/ws/voice/stream")
async def voice_streaming_websocket_endpoint(websocket: WebSocket):
    """
    Full-duplex WebSocket stream for live conversational voice calls (Gemini Live Mode),
    real-time streaming VAD with 450ms silence hangover auto-endpointing,
    instant barge-in task preemption, and 24kHz PCM audio pipelining.
    """
    await websocket.accept()
    session_id = f"ws-voice-{int(time.time() * 1000)}"
    session = VoiceCallSessionState(session_id=session_id, sample_rate=24000)
    VoiceAgentLoop.start_session(session_id)

    try:
        # Send initial connected handshake
        await websocket.send_json({
            "event": "connected",
            "session_id": session_id,
            "timestamp": time.time(),
            "sample_rate": 24000,
            "silence_hangover_ms": 450
        })
        await _ws_stream_loop(websocket, session)

    except WebSocketDisconnect:
        session.cancel_active_generation()
        VoiceAgentLoop.end_session(session_id)
        logger.debug(f"Voice WebSocket disconnected: {session_id}")
    except Exception as e:
        session.cancel_active_generation()
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

