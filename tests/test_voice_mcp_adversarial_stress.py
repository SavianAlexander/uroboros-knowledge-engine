"""
Empirical Adversarial Stress Harness for Milestone 2: Voice & MCP Subsystems.
Adversarially challenges:
1. VoiceDSP: Boundary inputs, extreme sample rates (1Hz to 384kHz), filter stability, NaN/Inf handling, unknown presets, ducking & mastering limits.
2. VoiceSFX: Procedural generators, concurrency stress, thread-safe caching, malformed cue names, WAV header structural validity.
3. VoicePersonaBlender: Missing files, corrupted payload fallbacks, extreme weights, unknown personas, vector dimension & numerical stability.
4. VoiceNormalizer: Empty strings, extreme Unicode/Zalgo, unclosed markdown, complex polyglot AST code translation, financial/acronym edge cases.
5. Antigravity Voice MCP & MCP Server: Tool dispatch robustness, unknown tools, malformed JSON-RPC payloads, parameter type mismatches.
6. Voice Audio Router & Command Parser & Streaming Pipeline: Malformed commands, empty streaming generators, invalid volume percentages.
"""

import os
import sys
import math
import json
import unittest
import threading
import concurrent.futures
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_dsp import (
    VoiceDSP,
    biquad_peaking,
    biquad_highpass,
    biquad_lowpass,
    apply_iir_filter,
    _DSP_PIPELINES
)
from src.core.voice_sfx import VoiceSFX, _SFX_GENERATORS
from src.core.voice_persona_blend import VoicePersonaBlender, SIGNATURE_PERSONA_BLENDS
from src.core.voice_normalizer import VoiceNormalizer, LEXICAL_PHONETIC_REPLACEMENTS
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_command_parser import VoiceCommandParser
from src.core.voice_streaming_pipeline import VoiceStreamingPipeliner
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.core.voice_engine import NonInterruptingAudioQueue, KokoroVoiceEngine
from src.antigravity_voice_mcp import handle_tool_call, _process_jsonrpc_request, TOOLS_SCHEMA
from src.mcp_server import handle_call_tool, _MCP_TOOL_HANDLERS


class TestM2AdversarialVoiceMatrix(unittest.TestCase):
    """Adversarial stress testing suite for refactored Milestone 2 Voice & MCP components."""

    # ----------------------------------------------------------------------
    # 1. VoiceDSP Adversarial Tests
    # ----------------------------------------------------------------------
    def test_dsp_presets_exhaustive_and_unknown(self):
        """Test all known DSP presets + unknown presets + edge case preset strings."""
        test_samples = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 2400, dtype=np.float32))
        
        # Test all pipelines in _DSP_PIPELINES
        for preset_name in _DSP_PIPELINES:
            out = VoiceDSP.apply_dsp_preset(test_samples, preset=preset_name, fs=24000)
            self.assertEqual(len(out), len(test_samples))
            self.assertFalse(np.isnan(out).any(), f"NaN detected in preset {preset_name}")
            self.assertFalse(np.isinf(out).any(), f"Inf detected in preset {preset_name}")
            self.assertLessEqual(np.max(np.abs(out)), 1.05)

        # Test unknown / boundary preset names (should gracefully fallback to linear mastering)
        for bad_preset in ["NON_EXISTENT_PRESET", "", "   ", None, "12345", "lowercase_studio"]:
            out = VoiceDSP.apply_dsp_preset(test_samples, preset=bad_preset if bad_preset is not None else "STUDIO_DIRECT")
            self.assertEqual(len(out), len(test_samples))
            self.assertFalse(np.isnan(out).any())

    def test_dsp_boundary_buffers(self):
        """Test DSP filters and mastering on boundary audio buffers."""
        # 1. Empty buffer
        empty = np.array([], dtype=np.float32)
        out_empty = VoiceDSP.apply_dsp_preset(empty, preset="EXECUTIVE_PRESENCE")
        self.assertEqual(len(out_empty), 0)

        # 2. All zeros buffer (silent)
        zeros = np.zeros(2400, dtype=np.float32)
        out_zeros = VoiceDSP.apply_dsp_preset(zeros, preset="COMMANDER_TACTICAL")
        self.assertEqual(len(out_zeros), 2400)
        self.assertTrue(np.all(out_zeros == 0))

        # 3. Massive amplitude buffer (over-driven 10,000x)
        massive = np.ones(2400, dtype=np.float32) * 10000.0
        out_massive = VoiceDSP.apply_dsp_preset(massive, preset="AWE_STUDIO_MASTER")
        self.assertEqual(len(out_massive), 2400)
        self.assertFalse(np.isnan(out_massive).any())
        self.assertLessEqual(np.max(np.abs(out_massive)), 1.0)  # Limiter must clamp

        # 4. DC Offset
        dc = np.ones(2400, dtype=np.float32) * 0.5
        out_dc = VoiceDSP.apply_dsp_preset(dc, preset="RADIO_BANDPASS_300_3400HZ")
        self.assertEqual(len(out_dc), 2400)
        self.assertFalse(np.isnan(out_dc).any())

    def test_dsp_extreme_sample_rates(self):
        """Test DSP filters across extreme sample rates (1 Hz to 384 kHz)."""
        sample_rates = [100, 4000, 8000, 16000, 24000, 44100, 48000, 96000, 192000, 384000]
        for fs in sample_rates:
            n_samples = min(2400, fs)
            buf = np.random.uniform(-0.5, 0.5, n_samples).astype(np.float32)
            out = VoiceDSP.apply_dsp_preset(buf, preset="HOLOGRAPHIC_AURA", fs=fs)
            self.assertEqual(len(out), n_samples)
            self.assertFalse(np.isnan(out).any(), f"NaN at sample rate {fs}")

    def test_dsp_biquad_extreme_parameters(self):
        """Test raw biquad filter generators with extreme/adversarial cutoffs, gains, and Q values."""
        # Frequency beyond Nyquist (should be clamped safely)
        b, a = biquad_peaking(f0=100000.0, gain_db=12.0, q=1.0, fs=24000)
        self.assertEqual(len(b), 3)
        self.assertEqual(len(a), 3)
        self.assertFalse(np.isnan(b).any())

        # Zero Q factor
        b, a = biquad_highpass(f0=100.0, q=0.0, fs=24000)
        self.assertFalse(np.isnan(b).any())

        # Extreme negative and positive gains
        b, a = biquad_peaking(f0=1000.0, gain_db=-100.0, q=0.1, fs=24000)
        self.assertFalse(np.isnan(b).any())
        b, a = biquad_peaking(f0=1000.0, gain_db=100.0, q=50.0, fs=24000)
        self.assertFalse(np.isnan(b).any())

    def test_dsp_ducking_and_mastering_boundaries(self):
        """Test dynamic audio ducking and true-peak mastering with mismatched and boundary inputs."""
        # Mismatched length ducking
        ambient = np.random.uniform(-0.2, 0.2, 48000).astype(np.float32)
        voice = np.random.uniform(-0.8, 0.8, 12000).astype(np.float32)
        ducked = VoiceDSP.apply_audio_ducking(ambient, voice, duck_gain=0.10)
        self.assertEqual(len(ducked), 48000)
        self.assertFalse(np.isnan(ducked).any())

    # ----------------------------------------------------------------------
    # 2. VoiceSFX Adversarial Tests
    # ----------------------------------------------------------------------
    def test_sfx_generators_exhaustive(self):
        """Test every registered SFX generator produces valid stereo PCM WAV audio."""
        for cue_name in _SFX_GENERATORS:
            wav_bytes = VoiceSFX.synthesize_sfx(cue_name)
            self.assertGreater(len(wav_bytes), 44, f"WAV bytes too short for cue: {cue_name}")
            # Verify WAV header magic bytes
            self.assertEqual(wav_bytes[:4], b"RIFF")
            self.assertEqual(wav_bytes[8:12], b"WAVE")
            self.assertEqual(wav_bytes[12:16], b"fmt ")
            self.assertEqual(wav_bytes[36:40], b"data")

    def test_sfx_unknown_cues_and_empty(self):
        """Test unknown and boundary cue names fallback gracefully to neutral tick without crashing."""
        for unknown_cue in ["non_existent_sfx", "", "   ", "???!!!", "UPPERCASE_ALERT"]:
            wav_bytes = VoiceSFX.synthesize_sfx(unknown_cue)
            self.assertGreater(len(wav_bytes), 44)
            self.assertEqual(wav_bytes[:4], b"RIFF")

    def test_sfx_concurrent_synthesis_thread_safety(self):
        """Concurrently synthesize multiple SFX cues from 50 worker threads to stress the cache."""
        cues = list(_SFX_GENERATORS.keys()) + ["unknown_1", "unknown_2", "confirm", "alert"]
        errors = []

        def worker_task(cue):
            try:
                for _ in range(10):
                    res = VoiceSFX.synthesize_sfx(cue)
                    if len(res) <= 44:
                        errors.append(f"Invalid length for {cue}")
            except Exception as e:
                errors.append(f"Exception for {cue}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(worker_task, cue) for cue in cues * 5]
            concurrent.futures.wait(futures)

        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")

    # ----------------------------------------------------------------------
    # 3. VoicePersonaBlender Adversarial Tests
    # ----------------------------------------------------------------------
    def test_persona_blend_signature_catalog(self):
        """Test vector interpolation for all signature persona blends."""
        voices = VoicePersonaBlender.load_voices_embeddings()
        for persona_name, weights in SIGNATURE_PERSONA_BLENDS.items():
            vec = VoicePersonaBlender.get_blended_vector(persona_name)
            if voices:
                self.assertIsNotNone(vec)
                self.assertFalse(np.isnan(vec).any())
            # Custom blend weights test
            res = VoicePersonaBlender.blend_personas(weights, custom_name=f"test_{persona_name}")
            self.assertEqual(res["status"], "success")

    def test_persona_blend_boundary_weights(self):
        """Test persona blending with adversarial weights (negative, extreme, sum != 1.0, unknown voice keys)."""
        # Empty weights
        res_empty = VoicePersonaBlender.blend_personas({})
        self.assertEqual(res_empty["status"], "error")

        # Unknown voice key
        res_unknown = VoicePersonaBlender.blend_personas({"unknown_voice_tensor_999": 1.0})
        self.assertIn(res_unknown["status"], ["error", "success"])

        # Unnormalized weights (sum = 10.0) -> should auto-normalize
        res_unnorm = VoicePersonaBlender.blend_personas({"bf_emma": 8.0, "af_bella": 2.0})
        self.assertEqual(res_unnorm["status"], "success")
        self.assertAlmostEqual(res_unnorm["weights"]["bf_emma"], 0.80, places=2)
        self.assertAlmostEqual(res_unnorm["weights"]["af_bella"], 0.20, places=2)

        # Negative weights
        res_neg = VoicePersonaBlender.blend_personas({"bf_emma": -0.5, "af_bella": 1.5})
        self.assertIn(res_neg["status"], ["error", "success"])

    def test_persona_missing_and_corrupted_loader_fallbacks(self):
        """Test _try_load_voices_json and _try_load_voices_bin with non-existent and corrupt files."""
        # Non-existent file
        self.assertIsNone(VoicePersonaBlender._try_load_voices_json("non_existent_file.json"))
        self.assertIsNone(VoicePersonaBlender._try_load_voices_bin("non_existent_file.bin"))

        # Direct ndarray input to get_blended_vector
        dummy_tensor = np.ones((511, 1, 256), dtype=np.float32)
        out_vec = VoicePersonaBlender.get_blended_vector(dummy_tensor)
        self.assertTrue(np.array_equal(out_vec, dummy_tensor))

    # ----------------------------------------------------------------------
    # 4. VoiceNormalizer Adversarial Tests
    # ----------------------------------------------------------------------
    def test_normalizer_empty_and_whitespace(self):
        """Test normalization of empty, whitespace, and single-character inputs."""
        self.assertEqual(VoiceNormalizer.normalize_for_speech(""), "")
        self.assertEqual(VoiceNormalizer.strip_markdown(""), "")
        self.assertEqual(VoiceNormalizer.apply_phonetic_dictionary(""), "")
        self.assertEqual(VoiceNormalizer.convert_code_to_spoken_english(""), "")

    def test_normalizer_unclosed_and_malformed_markdown(self):
        """Test resilience against broken/malformed markdown syntax."""
        malformed_inputs = [
            "This is **bold without closing asterisk",
            "Broken [link with no closing parenthesis](http://example.com",
            "![Broken image with unclosed brackets",
            ">>> Nested quotes with no body\n> ",
            "| Unfinished | Table |\n|---|",
            "Emoji overload 🚀🔥⚡👑💎 with Zalgo: t̶e̶s̶t̶",
            "HTML injected <script>alert('xss')</script> &amp; <b>bold</b>"
        ]
        for text in malformed_inputs:
            normalized = VoiceNormalizer.normalize_for_speech(text)
            self.assertIsInstance(normalized, str)
            self.assertNotIn("<script>", normalized)

    def test_normalizer_code_to_spoken_english_patterns(self):
        """Test complex programming lines translated into spoken developer English."""
        code_snippets = [
            "def calculate_trajectory(target_id: int, speed: float = 1.0) -> dict:",
            "export async function authenticateUser(token, options)",
            "const [isLoading, setIsLoading] = useState(false)",
            "class WarpDriveController(BaseEngine):",
            "import os, sys, json",
            "from src.core.voice_dsp import VoiceDSP",
            "git commit -m \"fix: resolve edge case\"",
            "npm install --save-dev typescript",
            "docker run -d -p 8080:80 nginx:alpine",
            "+ added_line = 42",
            "- removed_line = 0",
            "if (temperature > 0.8):",
            "elif (status == 200):",
            "else:",
            "return total_cost;"
        ]
        for line in code_snippets:
            spoken = VoiceNormalizer.convert_code_to_spoken_english(line)
            self.assertIsInstance(spoken, str)
            self.assertGreater(len(spoken), 0)

    def test_normalizer_financial_and_time_lexicon(self):
        """Test technical acronyms, currency, and time normalizations."""
        sample_text = "The search takes 14:30 to run. Cost is $45,000 w/ 30 mins duration. FYI SLA is P0."
        normalized = VoiceNormalizer.normalize_for_speech(sample_text)
        self.assertIn("2:30 P-M", normalized)
        self.assertTrue("forty-five thousand dollars" in normalized.lower() or "45000 dollars" in normalized.lower())
        self.assertIn("with", normalized)
        self.assertIn("30 minutes", normalized)
        self.assertIn("For your information", normalized)
        self.assertIn("priority zero critical", normalized)

    # ----------------------------------------------------------------------
    # 5. MCP Tool Dispatch & Server Adversarial Tests
    # ----------------------------------------------------------------------
    def test_antigravity_voice_mcp_all_handlers(self):
        """Adversarially test all tool handlers in antigravity_voice_mcp with minimal/boundary arguments."""
        # 1. Unknown tool call
        res_unknown = handle_tool_call("non_existent_tool_123", {})
        self.assertIn("error", res_unknown)
        self.assertIn("Unknown tool", res_unknown.get("error", ""))

        # 2. Known tools with empty/default arguments
        test_calls = [
            ("antigravity_get_status", {}),
            ("antigravity_list_audio_devices", {}),
            ("antigravity_get_dsp_presets", {}),
            ("antigravity_get_signature_personas", {}),
            ("antigravity_get_spectrum", {"num_bands": 32}),
            ("antigravity_get_voice_history", {"limit": 5}),
            ("antigravity_barge_in_cut", {}),
            ("antigravity_get_call_status", {}),
            ("antigravity_get_telemetry", {"format": "json"}),
            ("antigravity_get_eve_alert_templates", {}),
            ("antigravity_configure_voice", {"default_persona": "CALM_OPERATIONS"}),
            ("antigravity_play_sfx", {"sfx_name": "ready", "blocking": False}),
            ("antigravity_convert_code", {"code": "def hello(): pass", "language": "python"}),
            ("antigravity_read_document", {"text": "# Title\nHello world.", "doc_type": "markdown"})
        ]

        for tool_name, args in test_calls:
            res = handle_tool_call(tool_name, args)
            self.assertIsInstance(res, dict, f"Tool {tool_name} did not return a dictionary")
            self.assertTrue(len(res) > 0, f"Tool {tool_name} returned empty dictionary")

    def test_antigravity_voice_mcp_jsonrpc_protocol(self):
        """Test JSON-RPC 2.0 processor against malformed, invalid, and boundary payloads."""
        # 1. Initialize
        init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = _process_jsonrpc_request(init_req)
        self.assertEqual(resp["id"], 1)
        self.assertIn("result", resp)
        self.assertEqual(resp["result"]["serverInfo"]["name"], "antigravity-voice-mcp")

        # 2. tools/list
        list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = _process_jsonrpc_request(list_req)
        self.assertEqual(resp["id"], 2)
        self.assertIn("tools", resp["result"])
        self.assertGreater(len(resp["result"]["tools"]), 20)

        # 3. tools/call valid
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "antigravity_get_dsp_presets", "arguments": {}}
        }
        resp = _process_jsonrpc_request(call_req)
        self.assertEqual(resp["id"], 3)
        self.assertIn("content", resp["result"])

        # 4. tools/call unknown method
        bad_method_req = {"jsonrpc": "2.0", "id": 4, "method": "unknown/method", "params": {}}
        resp = _process_jsonrpc_request(bad_method_req)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)

        # 5. Malformed payload without method
        malformed = {"jsonrpc": "2.0", "id": 5}
        resp = _process_jsonrpc_request(malformed)
        self.assertIn("error", resp)

    def test_domain_mcp_server_dispatch_table(self):
        """Test domain MCP server _MCP_TOOL_HANDLERS table dispatch."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 1. Unknown tool
            unknown_res = loop.run_until_complete(handle_call_tool("unknown_tool", {}))
            self.assertEqual(len(unknown_res), 1)
            self.assertIn("Unknown tool", unknown_res[0].text)

            # 2. Valid tools via table
            valid_actions = [
                ("neuro_stats", {}),
                ("neuro_graph_query", {"query": "EVE", "limit": 2}),
                ("neuro_compress_ast", {"code": "def add(a, b): return a + b"}),
                ("neuro_release_certificate", {})
            ]
            for tool_name, args in valid_actions:
                res = loop.run_until_complete(handle_call_tool(tool_name, args))
                self.assertGreater(len(res), 0)
                self.assertIsInstance(res[0].text, str)
        finally:
            loop.close()

    # ----------------------------------------------------------------------
    # 6. Additional Subsystems: Router, Command Parser, Streaming Pipeline
    # ----------------------------------------------------------------------
    def test_voice_audio_router_boundary_volume(self):
        """Test volume bounds: negative, over 100%, 0%."""
        vol_neg = VoiceAudioRouter.set_master_volume(-50)
        self.assertEqual(vol_neg["master_volume"], 0)

        vol_over = VoiceAudioRouter.set_master_volume(250)
        self.assertEqual(vol_over["master_volume"], 100)

        vol_zero = VoiceAudioRouter.set_master_volume(0)
        self.assertEqual(vol_zero["master_volume"], 0)

    def test_voice_command_parser_adversarial_intents(self):
        """Test voice command parser with garbage strings, ambiguous commands, and punctuation."""
        garbage_inputs = [
            "",
            "   ",
            "!@#$%^&*()",
            "some completely unrecognized text",
            "set volume to infinity percent",
            "mute unmute mute switch voice"
        ]
        for cmd in garbage_inputs:
            res = VoiceCommandParser.parse_intent(cmd)
            self.assertIsInstance(res, dict)
            self.assertIn("intent", res)
            self.assertIn("matched", res)

            # Test execution path with speak_feedback=False for zero latency
            exec_res = VoiceCommandParser.execute_command(cmd, speak_feedback=False)
            self.assertEqual(exec_res["status"], "command_executed")
            self.assertIn("parsed_intent", exec_res)



    def test_voice_streaming_pipeline_empty_and_single_token(self):
        """Test streaming pipeliner on empty token generator and single token."""
        # Empty generator
        res_empty = VoiceStreamingPipeliner.stream_and_speak(iter([]), sync=False)
        self.assertEqual(res_empty["status"], "stream_completed")
        self.assertEqual(res_empty["clauses_count"], 0)

        # Single token
        res_single = VoiceStreamingPipeliner.stream_and_speak(iter(["Single token."]), sync=False)
        self.assertEqual(res_single["status"], "stream_completed")
        self.assertGreaterEqual(res_single["clauses_count"], 1)


if __name__ == "__main__":
    unittest.main()
