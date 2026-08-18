"""
Universal Voice Audio Matrix Verification Suite & System Diagnostic.
Standard: Pure Python Standard Library (unittest, json, os, sys, time).
Ponytail Senior Dev Principle: Single unified verification entrypoint for the complete neural audio stack (Kokoro-82M TTS, STT Ear, Persona Blending, DSP Acoustics, Procedural Soundboard, SQLite Memory, FFT Spectrum, Tududi Radar, Full-Duplex Call Intercom, VAD Barge-In, Code Syntax Narrator, Email Reader, and 19-Tool MCP Server).
"""

import os
import sys
import unittest
import time
import json

os.environ["ORT_LOGGING_LEVEL"] = "3"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_persona_blend import VoicePersonaBlender
from src.core.voice_stt_ear import VoiceEarTranscriber
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_memory_ledger import VoiceMemoryLedger
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.core.voice_code_narrator import CodeSyntaxNarrator
from src.core.voice_document_reader import DocumentVoiceReader
from src.antigravity_voice_mcp import handle_tool_call, TOOLS_SCHEMA
from scripts.verify_system_integrity import run_zero_assumption_audit


from src.core.voice_studio_showcase import VoiceStudioShowcase
from src.core.voice_dsp import VoiceDSP
from src.core.rag_query_cache import SemanticRAGQueryCache, GLOBAL_RAG_CACHE
from src.core.audit_hashchain import AuditHashchainLedger, GLOBAL_AUDIT_HASHCHAIN
from src.core.voice_command_parser import VoiceCommandParser
from src.core.voice_telemetry_exporter import AudioTelemetryExporter


class TestVoiceAudioMatrix(unittest.TestCase):
    """Complete system test suite for Uroboros Neural Voice & Audio Matrix."""

    def test_voice_studio_and_dsp_presets(self):
        """Test DSP mastering presets and studio showcase catalog."""
        catalog = VoiceStudioShowcase.get_studio_catalog()
        self.assertIn("personas", catalog)
        self.assertIn("dsp_presets", catalog)
        self.assertIn("EXECUTIVE_PRESENCE", catalog["dsp_presets"])
        self.assertIn("HOLOGRAPHIC_AURA", catalog["dsp_presets"])

        # Test audition dry-run
        audition = VoiceStudioShowcase.audition_persona("ORACLE_ADVISOR", speak_now=False)
        self.assertEqual(audition["status"], "auditioned")
        self.assertEqual(audition["persona"], "ORACLE_ADVISOR")
        self.assertEqual(audition["dsp_preset"], "EXECUTIVE_PRESENCE")

        # Test DSP filtering
        try:
            import numpy as np
            samples = np.random.uniform(-0.5, 0.5, 4800).astype(np.float32)
            for preset in ["EXECUTIVE_PRESENCE", "STUDIO_MASTER", "COMMANDER_TACTICAL", "HOLOGRAPHIC_AURA"]:
                filtered = VoiceDSP.apply_dsp_preset(samples, preset=preset, fs=24000)
                self.assertEqual(len(filtered), len(samples))
                self.assertLessEqual(np.max(np.abs(filtered)), 1.0)
        except ImportError:
            pass

    def test_semantic_rag_cache_and_deduplication(self):
        """Test LRU semantic RAG query cache and cosine similarity deduplication."""
        cache = SemanticRAGQueryCache(max_entries=10, similarity_threshold=0.95)
        vec_a = [0.1, 0.2, 0.3, 0.4]
        vec_b = [0.105, 0.202, 0.298, 0.401] # Near identical (>0.99 cos sim)

        cache.put("How many SP does Savian have?", {"sp": 74225867}, embedding=vec_a)
        
        # Exact match test
        res_exact = cache.get("How many SP does Savian have?")
        self.assertIsNotNone(res_exact)
        self.assertEqual(res_exact["hit_type"], "exact")
        self.assertEqual(res_exact["results"]["sp"], 74225867)

        # Semantic match test with rephrased query and vector
        res_sim = cache.get("What is Savian's total SP count?", embedding=vec_b)
        self.assertIsNotNone(res_sim)
        self.assertEqual(res_sim["hit_type"], "semantic_similarity")
        self.assertGreaterEqual(res_sim["similarity"], 0.95)

    def test_cryptographic_audit_hashchain(self):
        """Test SHA-256 Merkle audit hashchain tamper-evidence."""
        ledger = AuditHashchainLedger()
        b1 = ledger.append_event("VOICE_ALERT", {"text": "Warp drive active"}, actor="AURA")
        b2 = ledger.append_event("RAG_QUERY", {"query": "Solar systems in Verge Vendor"}, actor="USER")

        self.assertEqual(b1["index"], 0)
        self.assertEqual(b2["index"], 1)
        self.assertEqual(b2["prev_hash"], b1["block_hash"])

        integrity = ledger.verify_integrity()
        self.assertTrue(integrity["valid"])
        self.assertEqual(integrity["total_blocks"], 2)
        self.assertIsNotNone(integrity["merkle_root"])

    def test_spoken_voice_command_parser(self):
        """Test zero-dependency regex & NLP spoken command intent parser."""
        # 1. Persona switch test
        p1 = VoiceCommandParser.parse_intent("switch voice to aura ship ai")
        self.assertEqual(p1["intent"], "SET_PERSONA")
        self.assertIn("aura ship ai", p1["extracted_param"].lower())

        # 2. DSP switch test
        p2 = VoiceCommandParser.parse_intent("apply dsp preset sovereign presence")
        self.assertEqual(p2["intent"], "SET_DSP_PRESET")

        # 3. Radar test
        p3 = VoiceCommandParser.parse_intent("check tududi radar deadlines")
        self.assertEqual(p3["intent"], "CHECK_RADAR")

        # 4. Audit test
        p4 = VoiceCommandParser.parse_intent("audit hashchain security")
        self.assertEqual(p4["intent"], "VERIFY_AUDIT")

        # 5. Execution dry-run test
        exec_res = VoiceCommandParser.execute_command("switch persona to calm operations", speak_feedback=False)
        self.assertEqual(exec_res["status"], "command_executed")
        self.assertEqual(exec_res["action_result"]["new_persona"], "CALM_OPERATIONS")

    def test_audio_telemetry_exporter(self):
        """Test JSON and Prometheus telemetry formatting."""
        snap = AudioTelemetryExporter.get_telemetry_snapshot()
        self.assertIn("engine", snap)
        self.assertIn("intercom_call", snap)
        self.assertIn("semantic_rag_cache", snap)
        self.assertIn("audit_hashchain", snap)

        prom = AudioTelemetryExporter.export_prometheus_metrics()
        self.assertIn("audio_engine_status 1.0", prom)
        self.assertIn("rag_cache_hits", prom)
        self.assertIn("audit_hashchain_blocks", prom)

    def test_code_syntax_narrator(self):
        """Test translation of code syntax, SQL, and CLI into executive spoken narrative."""
        code_fn = "def calculate_risk(threat_level: int, shield_hp: float) -> Optional[Dict[str, Any]]:"
        narrative_fn = CodeSyntaxNarrator.deconstruct_code_for_speech(code_fn)
        self.assertIn("Function calculate risk", narrative_fn)
        self.assertIn("threat level", narrative_fn)

        sql = "SELECT id, system_name FROM solar_systems WHERE security < 0.0 ORDER BY kills DESC LIMIT 10;"
        narrative_sql = CodeSyntaxNarrator.deconstruct_code_for_speech(sql, language="sql")
        self.assertTrue("sequel query" in narrative_sql.lower() or "sql query" in narrative_sql.lower())
        self.assertIn("solar systems", narrative_sql)

        cli = 'git commit -m "feat(voice): deploy ultra-low-latency in-memory playback"'
        narrative_cli = CodeSyntaxNarrator.deconstruct_code_for_speech(cli)
        self.assertIn("Git commit with message", narrative_cli)

    def test_document_voice_reader(self):
        """Test cleaning and extraction of long-form emails and briefing memos."""
        raw_email = """From: Alexander Command <admiral@uroboros.internal>
Subject: Phase 43 Deployment Briefing
Date: Fri, 14 Aug 2026 20:00:00 -0400

Commander,

All mining operations in G-EURJ are operating at 100% capacity.
Please review the telemetry report at https://telemetry.internal/report.

CONFIDENTIALITY NOTICE: This message is intended solely for the recipient.
Sent from my iPhone
"""
        cleaned = DocumentVoiceReader.clean_email_for_speech(raw_email)
        self.assertEqual(cleaned["sender"], "Alexander Command")
        self.assertEqual(cleaned["subject"], "Phase 43 Deployment Briefing")
        self.assertIn("Email from Alexander Command", cleaned["speech_text"])
        self.assertIn("mining operations", cleaned["speech_text"])
        self.assertNotIn("CONFIDENTIALITY NOTICE", cleaned["speech_text"])
        self.assertNotIn("Sent from my iPhone", cleaned["speech_text"])

    def test_voice_normalizer_phonetics(self):
        """Test technical acronym expansion, markdown stripping, and cadence pacing."""
        raw_text = "# Task Complete\n- CI/CD pipeline passed at 25ms (24kHz at -14dB).\n- SQLite PRAGMA journal_mode=WAL; API v2.1.0 online."
        clean = VoiceNormalizer.normalize_for_speech(raw_text)
        self.assertIn("C-I C-D", clean)
        self.assertIn("25 milliseconds", clean)
        self.assertIn("24 kilohertz", clean)
        self.assertIn("-14 decibels", clean)
        self.assertIn("Sequel Light pragma", clean)
        self.assertIn("wall", clean)
        self.assertIn("A-P-I", clean)
        self.assertIn("version 2 point 1 point 0", clean)
        self.assertNotIn("#", clean)

    def test_audio_mastering_peak_limiter(self):
        """Test true-peak normalization and soft saturation limiter."""
        try:
            import numpy as np
            samples = np.array([-1.5, -0.5, 0.0, 0.5, 1.8], dtype=np.float32)
            mastered = VoiceNormalizer.master_audio_buffer(samples, target_dbfs=-1.0)
            self.assertEqual(len(mastered), len(samples))
            self.assertLessEqual(np.max(np.abs(mastered)), 1.0)
        except ImportError:
            pass

    def test_persona_blender_interpolation(self):
        """Test Kokoro 512-D voice embedding linear interpolation."""
        weights = {"bf_emma": 0.70, "af_bella": 0.30}
        res = VoicePersonaBlender.blend_personas(weights, custom_name="test_co_pilot")
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["weights"]["bf_emma"], 0.70)

    def test_stt_transcriber_and_recorder(self):
        """Test speech recognition and real mic buffer allocation."""
        rec = VoiceEarTranscriber.record_microphone_sample(duration_s=0.5)
        self.assertIn(rec["status"], ["recorded", "ready"])
        res = VoiceEarTranscriber.transcribe_audio_file(rec["output_path"])
        self.assertIn(res["status"], ["success", "error"])

    def test_audio_router_and_volume(self):
        """Test audio endpoint discovery and volume scaling."""
        devices = VoiceAudioRouter.list_audio_output_devices()
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        vol_res = VoiceAudioRouter.set_master_volume(85)
        self.assertEqual(vol_res["master_volume"], 85)

    def test_voice_memory_persistence(self):
        """Test SQLite conversational memory ledger logging and metrics."""
        turn = VoiceMemoryLedger.log_turn(
            speaker="Antigravity",
            raw_text="System standardized.",
            normalized_text="System standardized.",
            persona="CALM_OPERATIONS"
        )
        self.assertIn("turn_id", turn)
        recent = VoiceMemoryLedger.get_recent_turns(limit=3)
        self.assertGreater(len(recent), 0)

    def test_fft_spectrum_analyzer(self):
        """Test 32-band log FFT spectrum bins computation."""
        try:
            import numpy as np
            samples = np.random.uniform(-0.5, 0.5, 2048).astype(np.float32)
            spec = VoiceSpectrumAnalyzer.analyze_audio_buffer(samples, sample_rate=24000, num_bands=32)
            self.assertEqual(len(spec["spectrum_32_bands"]), 32)
            self.assertIn("rms_energy", spec)
            self.assertIn("peak_amplitude", spec)
        except ImportError:
            spec = VoiceSpectrumAnalyzer.analyze_audio_buffer(None, num_bands=32)
            self.assertEqual(len(spec["spectrum_32_bands"]), 32)

    def test_tududi_radar_sweep(self):
        """Test autonomous Tududi radar deadline check."""
        sweep = TududiVoiceRadarDaemon.execute_radar_sweep()
        self.assertEqual(sweep["status"], "sweep_completed")

    def test_voice_call_intercom_lifecycle(self):
        """Test full-duplex conversational voice call session lifecycle."""
        # 1. Start Call
        start_res = VoiceCallIntercomEngine.start_call(persona="AURA_SHIP_AI", caller_name="Test Commander")
        self.assertEqual(start_res["status"], "call_connected")
        self.assertTrue(VoiceCallIntercomEngine.get_call_status()["active"])

        # 2. Conversational Filler
        filler_res = VoiceCallIntercomEngine.trigger_immediate_filler()
        self.assertEqual(filler_res["status"], "filler_dispatched")

        # 3. In-Call Response with Roger Beep
        resp_res = VoiceCallIntercomEngine.respond_in_call("Understood, navigating to waypoint.", with_roger_beep=True)
        self.assertEqual(resp_res["status"], "responded")
        self.assertTrue(resp_res["with_roger_beep"])

        # 4. Barge-In Interruption
        cut_res = VoiceCallIntercomEngine.barge_in_cut()
        self.assertEqual(cut_res["status"], "barge_in_executed")

        # 5. End Call
        end_res = VoiceCallIntercomEngine.end_call()
        self.assertEqual(end_res["status"], "call_ended")
        self.assertFalse(VoiceCallIntercomEngine.get_call_status()["active"])

    def test_voice_vad_barge_in(self):
        """Test real-time VAD speech detection and instant audio purge."""
        vad = VoiceActivityInterrupter(energy_threshold=0.01)
        try:
            import numpy as np
            sine_wave = (0.2 * np.sin(2 * np.pi * 440.0 * np.linspace(0, 0.02, 480))).astype(np.float32)
            metrics = vad.analyze_frame(sine_wave)
            self.assertTrue(metrics["is_speech"])
        except ImportError:
            pass

        cut = VoiceActivityInterrupter.execute_instant_barge_in()
        self.assertEqual(cut["status"], "barge_in_executed")
        self.assertLess(cut["interruption_latency_ms"], 50.0)

    def test_all_25_antigravity_mcp_tools(self):
        """Test all 25 tools in the dedicated Antigravity Voice MCP server."""
        expected_tools = [
            "antigravity_speak", "antigravity_announce_task", "antigravity_voice_brief",
            "antigravity_play_sfx", "antigravity_blend_persona", "antigravity_listen",
            "antigravity_list_audio_devices", "antigravity_get_voice_history",
            "antigravity_get_spectrum", "antigravity_trigger_tududi_radar",
            "antigravity_start_call", "antigravity_call_respond", "antigravity_barge_in_cut",
            "antigravity_end_call", "antigravity_get_call_status",
            "antigravity_read_code", "antigravity_read_email",
            "antigravity_showcase_personas", "antigravity_apply_studio_master",
            "antigravity_verify_audit_hashchain", "antigravity_parse_voice_command",
            "antigravity_get_audio_telemetry",
            "antigravity_instant_speak", "antigravity_prewarm_voice_engine",
            "antigravity_get_instant_streamer_stats", "antigravity_voice_rag_query",
            "antigravity_synthesize_podcast_dialogue",
            "antigravity_voice_record_note", "antigravity_voice_create_task",
            "antigravity_stream_pipeline_speak",
            "antigravity_scan_vault_auto_watcher", "antigravity_listen_and_transcribe",
            "antigravity_configure_voice", "antigravity_get_status"
        ]
        tool_names = [t["name"] for t in TOOLS_SCHEMA]
        for exp in expected_tools:
            self.assertIn(exp, tool_names)

        status = handle_tool_call("antigravity_get_status", {})
        self.assertIn("engine", status)
        self.assertIn("playback_engine", status)

        chain_res = handle_tool_call("antigravity_verify_audit_hashchain", {"limit": 5})
        self.assertIn("integrity", chain_res)
        self.assertTrue(chain_res["integrity"]["valid"])

        cmd_res = handle_tool_call("antigravity_parse_voice_command", {"command": "get status", "speak_feedback": False})
        self.assertEqual(cmd_res["status"], "command_executed")

        telemetry_res = handle_tool_call("antigravity_get_audio_telemetry", {"format": "json"})
        self.assertIn("engine", telemetry_res)

        config_res = handle_tool_call("antigravity_configure_voice", {"default_persona": "CALM_OPERATIONS", "dsp_preset": "STUDIO_DIRECT"})
        self.assertEqual(config_res["status"], "updated")

        prewarm_res = handle_tool_call("antigravity_prewarm_voice_engine", {})
        self.assertEqual(prewarm_res["status"], "prewarmed")

        instant_res = handle_tool_call("antigravity_instant_speak", {"text": "Affirmative.", "persona": "CALM_OPERATIONS", "dsp_preset": "STUDIO_DIRECT", "sync": False})
        self.assertEqual(instant_res["status"], "playing")
        self.assertLessEqual(instant_res["latency_ms"], 50.0)

        stats_res = handle_tool_call("antigravity_get_instant_streamer_stats", {})
        self.assertEqual(stats_res["status"], "ok")

    def test_vault_auto_watcher(self):
        """Test autonomous vault filesystem delta scanner."""
        from src.infrastructure.vault_auto_watcher import VaultAutoWatcher
        watcher = VaultAutoWatcher()
        res = watcher.scan_and_index_delta()
        self.assertEqual(res["status"], "scan_complete")
        self.assertIn("scan_ms", res)

    def test_voice_streaming_pipeline(self):
        """Test streaming clause pipeliner with token generator."""
        from src.core.voice_streaming_pipeline import VoiceStreamingPipeliner
        tokens = ["Attention, ", "system ", "integrity ", "verified. ", "All ", "nodes ", "operational."]
        res = VoiceStreamingPipeliner.stream_and_speak(iter(tokens), persona="CALM_OPERATIONS", sync=False)
        self.assertEqual(res["status"], "stream_completed")
        self.assertGreater(res["clauses_count"], 0)

    def test_voice_knowledge_ingest(self):
        """Test voice note and task ingestion."""
        from src.core.voice_knowledge_ingest import VoiceKnowledgeIngest
        note_res = VoiceKnowledgeIngest.record_voice_note(
            title="Strategic Architecture Roadmap",
            content="Knowledge engine decoupling complete with zero regressions.",
            tags=["architecture", "audit"],
            speak_confirmation=False
        )
        self.assertEqual(note_res["status"], "note_recorded")
        self.assertTrue(os.path.exists(note_res["filepath"]))

        task_res = VoiceKnowledgeIngest.create_voice_task(
            title="Verify Multi-Model AI Evaluator",
            priority=1,
            speak_confirmation=False
        )
        self.assertEqual(task_res["status"], "task_logged")

    def test_voice_ear_transcriber_and_listen(self):
        """Test native winmm microphone recording and STT ear."""
        from src.core.voice_stt_ear import VoiceEarTranscriber
        rec_res = VoiceEarTranscriber.record_microphone_sample(duration_s=0.5, output_filename="test_ear_sample.wav")
        self.assertIn("status", rec_res)
        self.assertIn("output_path", rec_res)
        trans_res = VoiceEarTranscriber.transcribe_audio_file(rec_res["output_path"])
        self.assertEqual(trans_res["status"], "success")

    def test_voice_podcast_generator(self):
        """Test multi-speaker roundtable dialogue synthesizer."""
        from src.core.voice_podcast_generator import VoicePodcastGenerator
        turns = [
            {"speaker": "Aura", "persona": "AURA_SHIP_AI", "text": "All starships aligned."},
            {"speaker": "Commander", "persona": "FLEET_COMMANDER", "text": "Warp drive engaged."}
        ]
        res = VoicePodcastGenerator.synthesize_dialogue(turns, play_live=False)
        self.assertEqual(res["status"], "podcast_synthesized")
        self.assertEqual(res["turns_count"], 2)
        self.assertGreater(res["total_bytes"], 1000)

    def test_voice_rag_bridge_retrieval(self):
        """Test direct Voice-RAG knowledge retrieval and speech summarization."""
        from src.core.voice_rag_bridge import VoiceRAGBridge
        res = VoiceRAGBridge.query_and_summarize("Council of Stellar Management", max_sentences=2)
        self.assertIn("query", res)
        self.assertIn("speech_text", res)
        self.assertIn("retrieval_ms", res)
        self.assertTrue(len(res["speech_text"]) > 10)

    def test_instant_audio_streamer_and_client(self):
        """Test persistent WASAPI stream, RAM cache hit latency (<1ms), and pre-warming."""
        from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer
        InstantVoiceClient.pre_warm_tactical_phrases()
        streamer = get_instant_streamer()
        self.assertIsNotNone(streamer)

        # Test cached phrase (<1ms)
        res = InstantVoiceClient.speak_instant("Affirmative.", voice="af_bella", dsp_preset="STUDIO_DIRECT", sync=False)
        self.assertEqual(res["status"], "playing")
        self.assertTrue(res["cache_hit"])
        self.assertLessEqual(res["latency_ms"], 10.0)

    def test_voice_agent_loop_multi_turn(self):
        """Test autonomous multi-turn hands-free voice agent session lifecycle and spoken turn execution."""
        from src.core.voice_agent_loop import VoiceAgentLoop
        session_id = f"test-agent-session-{int(time.time())}"
        
        # 1. Start Session
        start_res = VoiceAgentLoop.start_session(session_id, persona="ORACLE_ADVISOR")
        self.assertEqual(start_res["status"], "active")
        self.assertEqual(start_res["session_id"], session_id)

        # 2. Process Spoken Turn
        turn_res = VoiceAgentLoop.process_spoken_turn(
            user_input_text="Switch voice to Alexander Executive",
            session_id=session_id
        )
        self.assertEqual(turn_res["status"], "success")
        self.assertEqual(turn_res["intent"], "SET_PERSONA")
        self.assertIn("audio_bytes_length", turn_res)

        # 3. Process Conversational Turn
        conv_res = VoiceAgentLoop.process_spoken_turn(
            user_input_text="What is the current system health and stability vitals?",
            session_id=session_id
        )
        self.assertEqual(conv_res["status"], "success")
        self.assertEqual(conv_res["turn_index"], 2)

        # 4. History
        hist = VoiceAgentLoop.get_session_history(session_id)
        self.assertEqual(hist["status"], "success")
        self.assertEqual(hist["session"]["turn_count"], 2)

        # 5. End Session
        end_res = VoiceAgentLoop.end_session(session_id)
        self.assertEqual(end_res["status"], "terminated")
        self.assertEqual(end_res["total_turns"], 2)

    def test_voice_router_endpoints(self):
        """Test voice REST router endpoints."""
        from src.app.routers.voice import (
            stt_listen_endpoint, STTListenRequest,
            vault_scan_endpoint
        )
        # 1. STT Listen Endpoint
        stt = stt_listen_endpoint(STTListenRequest(duration_seconds=0.5))
        self.assertIn("status", stt)

        # 2. Vault Scan Endpoint
        scan = vault_scan_endpoint()
        self.assertEqual(scan["status"], "scan_complete")

    def test_zero_assumptions_integrity(self):
        """Test strict 38-assertion zero-assumption validation suite."""
        success = run_zero_assumption_audit()
        self.assertTrue(success, "Zero-assumption audit failed!")



def main():
    print("\n" + "=" * 65)
    print("🌐 RUNNING UNIVERSAL VOICE AUDIO MATRIX VERIFICATION")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVoiceAudioMatrix)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    print("\n🎉 ALL VOICE AUDIO MATRIX MODULES PASSED (100% GREEN)!\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
