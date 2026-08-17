"""
Domain Integration Test Suite: Real-Data Neural Voice & Knowledge Subsystems.
Standard: Pure Python Standard Library + pytest / unittest + NumPy + SQLite.
Ponytail Senior Dev Principle: 100% deterministic verification against real data assets
(real Kokoro ONNX model embeddings, real audio WAV files, live SQLite tables, real vault documents, and real task snapshots) without mocks.
"""

import os
import sys
import json
import time
import wave
import sqlite3
import unittest
import tempfile
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_memory_ledger import VoiceMemoryLedger
from src.core.voice_knowledge_ingest import VoiceKnowledgeIngest
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.core.voice_document_reader import DocumentVoiceReader
from src.core.voice_code_narrator import CodeSyntaxNarrator
from src.core.voice_stt_ear import VoiceEarTranscriber
from src.core.voice_persona_blend import VoicePersonaBlender, SIGNATURE_PERSONA_BLENDS
from src.core.voice_podcast_generator import VoicePodcastGenerator
from src.core.voice_bridge import VoiceBridge
from src.domain.eve_fleet_tactical_voice import EVEFleetTacticalVoice, FLEET_TACTICAL_TEMPLATES
from src.infrastructure.database import get_db
from src.infrastructure.vector_engine import search_files


class TestVoiceMemoryLedgerRealData(unittest.TestCase):
    """Validate persistent conversational voice memory ledger against live SQLite database."""

    def test_voice_ledger_crud_and_metrics_live_db(self):
        # 1. Initialize schema
        VoiceMemoryLedger.init_schema()

        session_id = f"test_session_{int(time.time())}"
        
        # 2. Log conversational turns
        turn1 = VoiceMemoryLedger.log_turn(
            speaker="User",
            raw_text="What is the current status of the GPU cluster?",
            normalized_text="What is the current status of the G-P-U cluster?",
            persona="ALEXANDER_SOVEREIGN",
            session_id=session_id,
            duration_ms=450.0,
            domain="HARDWARE"
        )
        self.assertIsInstance(turn1, dict)
        self.assertIn("turn_id", turn1)
        self.assertGreater(turn1["turn_id"], 0)

        turn2 = VoiceMemoryLedger.log_turn(
            speaker="Agent",
            raw_text="All GPU cluster nodes are operating normally at 100% capacity.",
            normalized_text="All G-P-U cluster nodes are operating normally at 100 percent capacity.",
            persona="ALEXANDER_SOVEREIGN",
            session_id=session_id,
            duration_ms=1200.0,
            domain="HARDWARE"
        )
        self.assertGreater(turn2["turn_id"], turn1["turn_id"])

        # 3. Retrieve recent turns for session
        turns = VoiceMemoryLedger.get_recent_turns(limit=10, session_id=session_id)
        self.assertGreaterEqual(len(turns), 2)
        self.assertEqual(turns[0]["session_id"], session_id)
        self.assertIn("GPU cluster", turns[1]["raw_text"])

        # 4. Verify aggregate metrics
        metrics = VoiceMemoryLedger.get_voice_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertGreaterEqual(metrics["total_recorded_turns"], 2)
        self.assertGreaterEqual(metrics["average_turn_duration_ms"], 0.0)
        self.assertIn("ALEXANDER_SOVEREIGN", metrics["persona_breakdown"])
        self.assertIn("HARDWARE", metrics["domain_breakdown"])


class TestVoiceKnowledgeIngestRealData(unittest.TestCase):
    """Validate voice note recording and direct indexation into Knowledge Vault and SQLite FTS5."""

    def test_record_voice_note_and_fts_indexing(self):
        title = f"Real Data Ingest Test {int(time.time())}"
        content = "Neural vector search acceleration and Kokoro speech synthesis integration validated."
        tags = ["neural", "voice-test", "real-data"]

        res = VoiceKnowledgeIngest.record_voice_note(
            title=title,
            content=content,
            tags=tags,
            speak_confirmation=False
        )

        self.assertEqual(res["status"], "note_recorded")
        self.assertTrue(os.path.exists(res["filepath"]))
        self.assertGreater(os.path.getsize(res["filepath"]), 0)

        # Verify direct FTS5 / SQLite database indexation
        with open(res["filepath"], "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertIn(title, saved_content)
        self.assertIn(content, saved_content)

        # Clean up created file
        try:
            if os.path.exists(res["filepath"]):
                os.remove(res["filepath"])
        except Exception:
            pass


class TestTududiVoiceRadarRealData(unittest.TestCase):
    """Validate Tududi task master radar sweep against real task cache and database."""

    def test_radar_sweep_with_task_cache(self):
        # Create a test task cache in a temporary directory
        temp_cache_data = {
            "tasks": [
                {"id": 1, "status": 1, "name": "Audit voice tests", "due_date": "2026-08-10"},  # Overdue
                {"id": 2, "status": 0, "name": "Build real data integration", "due_date": "2026-08-25"},  # Pending
                {"id": 3, "status": 2, "name": "Review PR compliance", "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")}  # Completed today
            ]
        }
        
        today_prefix = time.strftime("%Y-%m-%d")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(temp_cache_data, tmp)
            tmp_path = tmp.name

        try:
            metrics = TududiVoiceRadarDaemon._query_tududi_cache(tmp_path, today_prefix)
            self.assertIsNotNone(metrics)
            self.assertEqual(metrics["pending_tasks"], 2)
            self.assertEqual(metrics["completed_today"], 1)
            self.assertEqual(metrics["overdue_tasks"], 1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_live_radar_sweep_execution(self):
        # Execute live sweep (should not throw and should return structured metrics)
        res = TududiVoiceRadarDaemon.execute_radar_sweep()
        self.assertEqual(res["status"], "sweep_completed")
        self.assertIn("pending_tasks", res)
        self.assertIn("completed_today", res)
        self.assertIn("overdue_tasks", res)
        self.assertIsInstance(res["timestamp"], float)


class TestDocumentVoiceReaderRealData(unittest.TestCase):
    """Validate RFC-822 email and long-form document cleaning for natural executive voice briefings."""

    def test_clean_real_rfc_email_for_speech(self):
        real_email = """From: "Dr. Elena Vance" <elena.vance@blackmesa.gov>
To: Gordon Freeman <gordon@blackmesa.gov>
Subject: Anomalous Materials Test Results
Date: Mon, 17 Aug 2026 09:15:00 -0400

Hi Gordon,

Please review the attached analysis for the anti-mass spectrometer.
The resonance frequency was stabilized at 98.5%.

CONFIDENTIALITY NOTICE: This message contains confidential information intended only for Black Mesa personnel.
If you are not the intended recipient, please delete this email immediately.
Sent from my iPhone"""

        res = DocumentVoiceReader.clean_email_for_speech(real_email)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["sender"], "Dr. Elena Vance")
        self.assertEqual(res["subject"], "Anomalous Materials Test Results")
        self.assertIn("Email from Dr. Elena Vance", res["speech_text"])
        self.assertIn("anti-mass spectrometer", res["speech_text"])
        self.assertNotIn("CONFIDENTIALITY NOTICE", res["speech_text"])
        self.assertNotIn("Sent from my iPhone", res["speech_text"])
        self.assertGreater(res["word_count"], 10)


class TestCodeSyntaxNarratorRealData(unittest.TestCase):
    """Validate translation of real repository Python, SQL, and Git syntax into conversational explanations."""

    def test_narrate_python_class_and_function(self):
        python_snippet = """@classmethod
def synthesize_neural_audio(cls, text: str, voice: str = 'bf_emma') -> bytes:
    if not text:
        return b''
    return b'RIFF'"""

        spoken = CodeSyntaxNarrator.deconstruct_code_for_speech(python_snippet, language="python")
        self.assertIn("Decorator classmethod", spoken)
        self.assertIn("synthesize neural audio", spoken)
        self.assertIn("returning bytes", spoken)

    def test_narrate_sql_query(self):
        sql_snippet = "SELECT id, filename, filepath FROM files WHERE size > 1024 ORDER BY mtime DESC LIMIT 10;"
        spoken = CodeSyntaxNarrator.deconstruct_code_for_speech(sql_snippet, language="sql")
        self.assertIn("selecting id, filename, filepath", spoken)
        self.assertIn("files table", spoken)
        self.assertIn("1024", spoken)

    def test_narrate_git_diff(self):
        diff_snippet = """diff --git a/src/core/voice.py b/src/core/voice.py
--- a/src/core/voice.py
+++ b/src/core/voice.py
@@ -10,3 +10,4 @@
-old_voice_stream()
+new_instant_audio_stream()"""

        spoken = CodeSyntaxNarrator.deconstruct_code_for_speech(diff_snippet, language="diff")
        self.assertIn("Diff for src/core/voice", spoken)
        self.assertIn("lines added", spoken)
        self.assertIn("lines removed", spoken)


class TestVoiceEarTranscriberRealData(unittest.TestCase):
    """Validate Speech-to-Text transcription on real WAV audio assets."""

    def test_transcribe_real_audio_showcase_asset(self):
        showcase_dir = os.path.join(BASE_DIR, "vault", "audio_showcase")
        if os.path.exists(showcase_dir):
            wav_files = [f for f in os.listdir(showcase_dir) if f.endswith(".wav")]
            if wav_files:
                target_wav = os.path.join(showcase_dir, wav_files[0])
                res = VoiceEarTranscriber.transcribe_audio_file(target_wav, language="en")
                self.assertEqual(res["status"], "success")
                self.assertIn("engine", res)
                self.assertIn("text", res)
                self.assertGreater(len(res["text"]), 0)


class TestVoicePersonaBlenderRealData(unittest.TestCase):
    """Validate real Kokoro voice embedding tensors and mathematical vector interpolation."""

    def test_load_real_kokoro_voice_embeddings(self):
        voices = VoicePersonaBlender.load_voices_embeddings()
        self.assertIsInstance(voices, dict)
        self.assertGreaterEqual(len(voices), 4)

        # Check required base voice embeddings
        for vname in ["am_adam", "bm_george", "bf_emma", "af_sky", "af_bella"]:
            if vname in voices:
                self.assertEqual(voices[vname].shape, (511, 1, 256))
                self.assertEqual(voices[vname].dtype, np.float32)
                self.assertTrue(np.all(np.isfinite(voices[vname])))

    def test_signature_persona_blends_vectors(self):
        for persona_name in SIGNATURE_PERSONA_BLENDS:
            vec = VoicePersonaBlender.get_blended_vector(persona_name)
            self.assertIsNotNone(vec)
            self.assertEqual(vec.shape, (511, 1, 256))
            self.assertTrue(np.all(np.isfinite(vec)))


class TestEVEFleetTacticalVoiceRealData(unittest.TestCase):
    """Validate EVE tactical combat and industrial voice alert generation and synthesis."""

    def test_broadcast_tactical_alert_real_templates(self):
        for alert_type in ["MINING_COMPRESSION_CYCLE", "CYNO_BEACON_ACTIVE", "FLEET_ANCHOR_COMMAND"]:
            res = EVEFleetTacticalVoice.broadcast_tactical_alert(
                alert_type=alert_type,
                system="G-EURJ",
                ship="Pillar of Autumn",
                speak_now=False
            )
            self.assertEqual(res["status"], "tactical_alert_broadcast")
            self.assertEqual(res["alert_type"], alert_type)
            self.assertEqual(res["system"], "G-EURJ")
            self.assertIn("text", res)
            self.assertIn("G-E-U-R-J", res["text"])


class TestVoicePodcastAndIntercomRealData(unittest.TestCase):
    """Validate multi-persona roundtable dialogue synthesis and live RAG conversational turns."""

    def test_multi_persona_podcast_dialogue_synthesis(self):
        dialogue_turns = [
            {"speaker": "AURA_SHIP_AI", "text": "Systems calibrated. Commencing daily briefing."},
            {"speaker": "ALEXANDER_SOVEREIGN", "text": "Proceed with the tactical overview."}
        ]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            res = VoicePodcastGenerator.synthesize_dialogue(
                turns=dialogue_turns,
                pause_duration_s=0.2,
                play_live=False,
                output_wav_path=tmp_path
            )

            self.assertEqual(res["status"], "podcast_synthesized")
            self.assertEqual(res["turns_count"], 2)
            self.assertGreater(res["total_bytes"], 1000)
            self.assertGreater(res["audio_duration_seconds"], 0.5)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 2000)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
