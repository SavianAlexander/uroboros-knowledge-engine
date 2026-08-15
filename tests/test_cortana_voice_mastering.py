"""
Automated Test Suite for Cortana-Grade Neural Audio Pipeline & Broadcast DSP Mastering Rack.
Standard: Pure Python Standard Library + pytest + FastAPI TestClient + NumPy.
Ponytail Senior Dev Principle: 100% deterministic local unit & integration verification for zero-cloud neural audio.
"""

import os
import sys
import io
import pytest
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_persona_blend import VoicePersonaBlender, SIGNATURE_PERSONA_BLENDS
from src.core.voice_normalizer import VoiceNormalizer
from src.infrastructure.eve_voice_dsp import (
    biquad_peaking,
    biquad_highshelf,
    apply_biquad,
    apply_parametric_mastering_eq,
    apply_studio_compression_limiting,
    apply_dynamic_deesser,
    apply_holographic_spatial_widener,
    process_tactical_dsp_pipeline
)
from src.core.voice_bridge import VoiceBridge


@pytest.fixture
def test_signal():
    # 1-second 24kHz synthetic signal with mix of frequencies
    fs = 24000
    t = np.linspace(0, 1.0, fs, endpoint=False)
    sig = 0.3 * np.sin(2 * np.pi * 200 * t) + 0.2 * np.sin(2 * np.pi * 2800 * t) + 0.2 * np.sin(2 * np.pi * 7500 * t)
    return sig.astype(np.float32)


class TestVoicePersonaBlender:
    """Validate 512-D Kokoro voice embedding vector interpolation."""


    def test_load_voices_embeddings(self):
        voices = VoicePersonaBlender.load_voices_embeddings()
        assert isinstance(voices, dict)
        assert len(voices) > 0
        assert "af_sky" in voices
        assert "af_bella" in voices
        assert "af_sarah" in voices

    def test_cortana_prime_vector_shape(self):
        vec = VoicePersonaBlender.get_blended_vector("CORTANA_PRIME")
        assert vec is not None
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (511, 1, 256)
        assert vec.dtype == np.float32
        assert np.all(np.isfinite(vec))

    def test_aura_ship_ai_vector_shape(self):
        vec = VoicePersonaBlender.get_blended_vector("AURA_SHIP_AI")
        assert vec is not None
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (511, 1, 256)

    def test_custom_linear_blend(self):
        res = VoicePersonaBlender.blend_personas({"af_sky": 0.5, "af_bella": 0.5}, custom_name="test_blend")
        assert res["status"] == "success"
        assert res["has_embedding_vector"] is True
        assert res["vector_dimension"] == 511

        vec = VoicePersonaBlender.get_blended_vector("test_blend")
        assert vec is not None
        assert vec.shape == (511, 1, 256)


class TestBroadcastDSPMasteringRack:
    """Validate acoustic DSP mastering filters, compressors, and spatial wideners."""

    def test_biquad_coefficients(self):

        b, a = biquad_peaking(2800.0, gain_db=1.8, q=1.4, fs=24000)
        assert len(b) == 3 and len(a) == 3
        assert np.all(np.isfinite(b)) and np.all(np.isfinite(a))

    def test_parametric_mastering_eq(self, test_signal):
        eq = apply_parametric_mastering_eq(test_signal, sample_rate=24000)
        assert eq is not None
        assert len(eq) == len(test_signal)
        assert np.all(np.isfinite(eq))

    def test_studio_compression_and_limiting(self, test_signal):
        # Scale to high volume to test compression limiting
        hot_signal = test_signal * 3.0
        limited = apply_studio_compression_limiting(hot_signal, sample_rate=24000, threshold_db=-14.0)
        assert np.all(np.isfinite(limited))
        assert np.max(np.abs(limited)) <= 0.99  # Peak limiter ceiling

    def test_dynamic_deesser(self, test_signal):
        deessed = apply_dynamic_deesser(test_signal, sample_rate=24000)
        assert len(deessed) == len(test_signal)
        assert np.all(np.isfinite(deessed))

    def test_holographic_spatial_widener(self, test_signal):
        stereo = apply_holographic_spatial_widener(test_signal, sample_rate=24000, delay_ms=14.0, wet=0.08)
        assert stereo.ndim == 2
        assert stereo.shape == (len(test_signal), 2)
        assert np.all(np.isfinite(stereo))

    def test_process_tactical_dsp_presets(self, test_signal):
        for preset in ["STUDIO_MASTER", "CORTANA_MASTER", "HOLOGRAPHIC_AI", "AURA_COCKPIT", "TACTICAL_RADIO", "STUDIO_DIRECT"]:
            out, sr = process_tactical_dsp_pipeline(test_signal, sample_rate=24000, preset=preset)
            assert out is not None
            assert sr == 24000
            assert np.all(np.isfinite(out))


class TestVoiceNormalizerPhonetics:
    """Validate technical jargon phonetics and cadence normalizer."""

    def test_strip_markdown(self):
        md = "### Header\n\n```python\nprint('code')\n```\n\nThis is **bold** with a [link](https://example.com) and `inline code`."
        clean = VoiceNormalizer.strip_markdown(md)
        assert "```" not in clean
        assert "print('code')" not in clean
        assert "https://" not in clean
        assert "bold with a link and inline code" in clean

    def test_phonetic_dictionary(self):
        text = "Deploying CI/CD on SQLite with FastAPI and ONNX for Cortana O(n log n) complexity != null."
        normalized = VoiceNormalizer.apply_phonetic_dictionary(text)
        assert "C-I C-D" in normalized
        assert "Sequel Light" in normalized
        assert "Fast A-P-I" in normalized
        assert "on-ix" in normalized
        assert "Cor-tah-nah" in normalized
        assert "O of N log N" in normalized
        assert "is not equal to" in normalized

    def test_master_audio_buffer(self, test_signal):
        mastered = VoiceNormalizer.master_audio_buffer(test_signal, sample_rate=24000, dsp_preset="STUDIO_MASTER")
        assert mastered is not None
        assert np.all(np.isfinite(mastered))
        assert np.max(np.abs(mastered)) <= 1.0

    def test_code_to_spoken_english(self):
        code_snip = """def authenticate_user(username, password=None) -> bool:
    if username == 'admin' and password != '':
        return True
    return False"""
        spoken = VoiceNormalizer.convert_code_to_spoken_english(code_snip)
        assert "Defining function authenticate user" in spoken
        assert "with arguments username, password=None returning bool" in spoken
        assert "If username == 'admin' and password != ''" in spoken
        assert "Returns True" in spoken

    def test_email_memo_normalization(self):
        email_text = """From: Sarah Connor <sarah@cyber.com>
To: John <john@pm.me>
Subject: Urgent Security Patch
Date: 2026-08-15 14:30:00

Hi John,
FYI, we noticed an issue w/ the database SLA.
Best regards,
Sarah Connor
Sent from my iPhone"""
        spoken = VoiceNormalizer.normalize_for_speech(email_text)
        assert "Email from Sarah Connor" in spoken
        assert "sarah at cyber dot com" in spoken
        assert "Addressed to John" in spoken
        assert "john at pm dot me" in spoken
        assert "August 15, 2026" in spoken
        assert "2:30 P-M" in spoken
        assert "For your information" in spoken
        assert "with the database S-L-A" in spoken
        assert "Sent from my iPhone" not in spoken

    def test_markdown_table_spoken_summary(self):
        table_text = """Here is the status:
| Service | Status | Port |
|---|---|---|
| FastAPI | Online | 8085 |
| SQLite | Active | 0 |
"""
        spoken = VoiceNormalizer.normalize_for_speech(table_text)
        assert "Table with columns: Service, Status, Port" in spoken
        assert "Row 1: Service: Fast A-P-I, Status: Online, Port: 8085" in spoken
        assert "Row 2: Service: Sequel Light, Status: Active, Port: 0" in spoken

    def test_daily_business_lexicon(self):
        text = "Our Q3 MRR reached $1,250,500.50 and ARR is $15M. Check - [x] task A and - [ ] task B ASAP."
        spoken = VoiceNormalizer.normalize_for_speech(text)
        assert "third quarter" in spoken
        assert "M-R-R" in spoken
        assert "1250500 dollars and 50 cents" in spoken
        assert "15 million dollars" in spoken
        assert "Completed task: task A" in spoken
        assert "Pending task: task B" in spoken
        assert "as soon as possible" in spoken



class TestVoiceBridgeAndAPI:
    """Validate high-level VoiceBridge synthesis and FastAPI endpoints."""

    def test_voice_bridge_synthesize_bytes(self):
        wav = VoiceBridge.synthesize_bytes(
            "Cortana Prime systems online.",
            voice="CORTANA_PRIME",
            speed=1.0,
            dsp_preset="STUDIO_MASTER"
        )
        assert wav is not None
        assert len(wav) > 1000
        # Check standard WAV RIFF header
        assert wav[:4] == b"RIFF"
        assert b"WAVE" in wav[:16]

    def test_fastapi_voice_endpoints(self):
        from fastapi.testclient import TestClient
        from src.app.main import app

        client = TestClient(app)

        # 1. Test /api/voice/personas
        resp = client.get("/api/voice/personas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["default_voice"] == "CORTANA_PRIME"
        assert any(p["id"] == "CORTANA_PRIME" for p in data["personas"])
        assert any(d["id"] == "STUDIO_MASTER" for d in data["dsp_presets"])

        # 2. Test /v1/audio/speech
        speech_resp = client.post(
            "/v1/audio/speech",
            json={
                "input": "Testing neural voice streaming API.",
                "voice": "CORTANA_PRIME",
                "dsp_preset": "STUDIO_MASTER",
                "speed": 1.0,
                "response_format": "wav"
            }
        )
        assert speech_resp.status_code == 200
        assert speech_resp.headers["content-type"] in ("audio/wav", "audio/x-wav")
        assert len(speech_resp.content) > 1000
        assert speech_resp.content[:4] == b"RIFF"

        # 3. Test /api/voice/sfx/{sfx_name}
        for sfx_name in ["ready", "confirm", "complete", "alert", "dismiss"]:
            sfx_resp = client.get(f"/api/voice/sfx/{sfx_name}")
            assert sfx_resp.status_code == 200
            assert sfx_resp.headers["content-type"] in ("audio/wav", "audio/x-wav")
            assert len(sfx_resp.content) > 500
            assert sfx_resp.content[:4] == b"RIFF"

        # 4. Test /v1/audio/speech/stream
        stream_resp = client.post(
            "/v1/audio/speech/stream",
            json={
                "input": "First clause here. Second clause follows.",
                "voice": "CORTANA_PRIME",
                "dsp_preset": "STUDIO_MASTER"
            }
        )
        assert stream_resp.status_code == 200
        lines = [line for line in stream_resp.text.split("\n") if line.strip()]
        assert len(lines) >= 2


class TestVoiceSFXAndEarcons:
    """Validate procedural mathematical synthesis of Cortana UI sound cues."""

    def test_synthesize_all_sfx(self):
        from src.core.voice_sfx import VoiceSFX
        for sfx in ["ready", "confirm", "complete", "alert", "dismiss"]:
            wav = VoiceSFX.synthesize_sfx(sfx)
            assert wav is not None
            assert len(wav) > 1000
            assert wav[:4] == b"RIFF"
            assert b"WAVE" in wav[:16]

    def test_voice_bridge_play_sfx(self):
        wav = VoiceBridge.play_sfx("ready")
        assert wav is not None
        assert len(wav) > 1000
        assert wav[:4] == b"RIFF"


class TestStreamingNeuralSynthesizerAndCache:
    """Validate clause splitting, streaming generation, and LRU cache."""

    def test_clause_splitting(self):
        from src.core.voice_streaming import StreamingNeuralSynthesizer
        text = "Hello world. This is sentence two! And here is three?"
        clauses = StreamingNeuralSynthesizer.split_into_acoustic_clauses(text)
        assert len(clauses) == 3
        assert "Hello world." in clauses[0]

    def test_lru_audio_cache(self):
        from src.core.voice_streaming import StreamingAudioCache
        StreamingAudioCache.clear()
        dummy_wav = b"RIFF" + b"\x00" * 100
        StreamingAudioCache.put("test clause", "CORTANA_PRIME", 1.0, "STUDIO_MASTER", dummy_wav)
        cached = StreamingAudioCache.get("test clause", "CORTANA_PRIME", 1.0, "STUDIO_MASTER")
        assert cached == dummy_wav
        StreamingAudioCache.clear()
        assert StreamingAudioCache.get("test clause", "CORTANA_PRIME", 1.0, "STUDIO_MASTER") is None


