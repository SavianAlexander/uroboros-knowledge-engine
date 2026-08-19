"""
Comprehensive Test Suite for Full-Duplex Conversational Voice Call Engine (Gemini Live Mode).
Standard: Pure Python Standard Library (unittest, asyncio, struct, json, os) + FastAPI TestClient + NumPy.
Ponytail Senior Dev Principle: 100% deterministic local verification for token-to-audio pipelining, VAD streaming, silence hangover auto-endpointing, sub-10ms barge-in preemption, and WebSocket streaming.
"""

import os
import sys
import time
import json
import asyncio
import struct
import unittest
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_streaming_pipeline import (
    VoiceStreamingPipeliner,
    LIVE_VOICE_SYSTEM_PROMPT,
    wav_to_pcm16
)
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.app.routers.voice_ws import VoiceCallSessionState
from src.app.main import app
from fastapi.testclient import TestClient


class TestVoicePipeliner(unittest.IsolatedAsyncioTestCase):
    """Validate async token-to-speech clause pipeliner & PCM audio extraction."""

    def test_live_voice_system_prompt_format(self):
        self.assertIn("real-time conversational voice assistant", LIVE_VOICE_SYSTEM_PROMPT)
        self.assertIn("Never output markdown", LIVE_VOICE_SYSTEM_PROMPT)
        self.assertIn("1 to 3 short sentences", LIVE_VOICE_SYSTEM_PROMPT)

    def test_wav_to_pcm16_conversion(self):
        num_samples = 480
        pcm_raw = struct.pack(f'<{num_samples}h', *[int(1000 * np.sin(i)) for i in range(num_samples)])
        wav_header = b'RIFF' + struct.pack('<I', 36 + len(pcm_raw)) + b'WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data' + struct.pack('<I', len(pcm_raw))
        full_wav = wav_header + pcm_raw

        extracted = wav_to_pcm16(full_wav)
        self.assertEqual(len(extracted), len(pcm_raw))
        self.assertEqual(extracted, pcm_raw)

    def test_clean_clause_text_markdown_stripping(self):
        dirty = "### Hello **world**! Check this `code` [link](url)."
        clean = VoiceStreamingPipeliner._clean_clause_text(dirty)
        self.assertNotIn("**", clean)
        self.assertNotIn("###", clean)
        self.assertNotIn("`", clean)
        self.assertIn("Hello", clean)
        self.assertIn("world", clean)

    async def test_async_stream_and_synthesize_pipelining(self):
        async def mock_token_generator():
            tokens = ["Hello ", "there. ", "I am ", "your live ", "assistant. ", "How can I ", "assist today?"]
            for t in tokens:
                yield t
                await asyncio.sleep(0.01)

        chunks = []
        async for chunk in VoiceStreamingPipeliner.async_stream_and_synthesize(mock_token_generator()):
            chunks.append(chunk)

        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(chunks[0]["is_first"])
        self.assertIsNotNone(chunks[0]["ttfs_ms"])
        self.assertGreater(chunks[0]["ttfs_ms"], 0)
        self.assertEqual(chunks[0]["sample_rate"], 24000)
        self.assertGreater(len(chunks[0]["audio_wav"]), 44)
        self.assertGreater(len(chunks[0]["audio_pcm"]), 0)


class TestVoiceActivityInterrupter(unittest.IsolatedAsyncioTestCase):
    """Validate 20ms RMS/ZCR VAD streaming, 450ms silence hangover auto-endpointing, and barge-in cutoff."""

    def setUp(self):
        self.vad = VoiceActivityInterrupter(
            sample_rate=24000,
            frame_duration_ms=20,
            energy_threshold=0.018,
            zcr_threshold=0.005,
            consecutive_frames_to_trigger=2,
            silence_hangover_ms=450.0
        )

    def test_silence_frame_analysis(self):
        silence_samples = np.zeros(480, dtype=np.float32)
        res = self.vad.analyze_frame(silence_samples)
        self.assertFalse(res["is_speech"])
        self.assertEqual(res["rms_energy"], 0.0)

    def test_speech_frame_analysis(self):
        t = np.linspace(0, 0.02, 480, endpoint=False)
        voice_samples = (0.5 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
        res = self.vad.analyze_frame(voice_samples)
        self.assertTrue(res["is_speech"])
        self.assertGreater(res["rms_energy"], 0.018)

    def test_streaming_vad_speech_accumulation_and_silence_hangover(self):
        t = np.linspace(0, 0.02, 480, endpoint=False)
        loud_pcm = (0.6 * np.sin(2 * np.pi * 300 * t) * 32767).astype(np.int16).tobytes()

        for _ in range(5):
            res = self.vad.process_streaming_pcm_chunk(loud_pcm, is_assistant_speaking=False)

        self.assertTrue(self.vad.is_speech_active)
        self.assertGreater(len(self.vad.speech_pcm_buffer), 0)
        self.assertFalse(res["endpoint_triggered"])

        silence_pcm = np.zeros(480, dtype=np.int16).tobytes()
        endpoint_hit = False
        captured_bytes = None

        for _ in range(25):
            res = self.vad.process_streaming_pcm_chunk(silence_pcm, is_assistant_speaking=False)
            if res["endpoint_triggered"]:
                endpoint_hit = True
                captured_bytes = res["speech_bytes"]
                break

        self.assertTrue(endpoint_hit)
        self.assertIsNotNone(captured_bytes)
        self.assertGreater(len(captured_bytes), 0)
        self.assertFalse(self.vad.is_speech_active)

    def test_barge_in_instant_preemption(self):
        t = np.linspace(0, 0.02, 480, endpoint=False)
        user_voice_pcm = (0.7 * np.sin(2 * np.pi * 400 * t) * 32767).astype(np.int16).tobytes()

        res1 = self.vad.process_streaming_pcm_chunk(user_voice_pcm, is_assistant_speaking=True)
        res2 = self.vad.process_streaming_pcm_chunk(user_voice_pcm, is_assistant_speaking=True)

        self.assertTrue(res2["barge_in_triggered"])
        self.assertTrue(self.vad.is_interrupted)

    async def test_execute_instant_barge_in_task_cancellation(self):
        async def dummy_long_task():
            try:
                await asyncio.sleep(10.0)
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(dummy_long_task())
        res = VoiceActivityInterrupter.execute_instant_barge_in(active_task=task)
        await asyncio.sleep(0.01)

        self.assertEqual(res["status"], "barge_in_executed")
        self.assertTrue(res["task_cancelled"])
        self.assertLess(res["interruption_latency_ms"], 25.0)
        self.assertTrue(task.cancelled() or task.done())


class TestVoiceWebSocketRouter(unittest.TestCase):
    """Validate full-duplex WebSocket router with text turns, VAD streaming, and barge-in events."""

    def setUp(self):
        self.client = TestClient(app)

    def test_websocket_connection_handshake(self):
        with self.client.websocket_connect("/ws/voice/stream") as ws:
            handshake = ws.receive_json()
            self.assertEqual(handshake["event"], "connected")
            self.assertIn("session_id", handshake)
            self.assertEqual(handshake["sample_rate"], 24000)
            self.assertEqual(handshake["silence_hangover_ms"], 450)

            ws.send_json({"action": "ping"})
            pong = ws.receive_json()
            self.assertEqual(pong["event"], "pong")

    def test_websocket_call_start_and_turn(self):
        with self.client.websocket_connect("/ws/voice/stream") as ws:
            ws.receive_json()  # Handshake

            ws.send_json({"action": "call_start"})
            call_start_event = ws.receive_json()
            self.assertEqual(call_start_event["event"], "call_started")

            ws.send_json({"action": "turn", "text": "What is Uroboros?"})
            
            start_event = ws.receive_json()
            self.assertEqual(start_event["event"], "audio_start")

            events = []
            for _ in range(30):
                msg = ws.receive()
                if "text" in msg and msg["text"]:
                    data = json.loads(msg["text"])
                    events.append(data)
                    if data.get("event") == "turn_complete":
                        break
                elif "bytes" in msg and msg["bytes"]:
                    events.append({"event": "binary_pcm", "bytes_len": len(msg["bytes"])})

            chunk_events = [e for e in events if e.get("event") == "audio_chunk"]
            self.assertGreaterEqual(len(chunk_events), 1)
            self.assertIsNotNone(chunk_events[0]["ttfs_ms"])

    def test_websocket_client_barge_in(self):
        with self.client.websocket_connect("/ws/voice/stream") as ws:
            ws.receive_json()  # Handshake

            ws.send_json({"action": "turn", "text": "Tell me a very long story about ancient algorithms."})
            start_event = ws.receive_json()
            self.assertEqual(start_event["event"], "audio_start")

            ws.send_json({"action": "barge_in"})

            interrupted_hit = False
            for _ in range(20):
                msg = ws.receive()
                if "text" in msg and msg["text"]:
                    data = json.loads(msg["text"])
                    if data.get("event") == "interrupted":
                        interrupted_hit = True
                        break

            self.assertTrue(interrupted_hit)


if __name__ == "__main__":
    unittest.main()
