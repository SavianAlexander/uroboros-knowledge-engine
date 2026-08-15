"""
Adversarial Stress & Edge-Case Verification Suite for Voice & MCP Subsystems.
Standard: Pure Python Standard Library (unittest, json, asyncio, unittest.mock).
Enterprise Naming & Domain Protocol Guard: test_voice_mcp_adversarial_edge_cases.py
"""

import os
import sys
import json
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.antigravity_voice_mcp import (
    handle_tool_call,
    _process_jsonrpc_request,
    _TOOL_HANDLERS,
    TOOLS_SCHEMA
)
from src.mcp_server import handle_call_tool, _MCP_TOOL_HANDLERS
from src.core.voice_command_parser import VoiceCommandParser
from src.core.voice_dsp import VoiceDSP
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_sfx import VoiceSFX


class TestVoiceMCPAdversarialEdgeCases(unittest.TestCase):
    """Adversarial challenge suite testing boundary invariants, fuzz payloads, and table dispatch safety."""

    def test_antigravity_mcp_unknown_tool_dispatch(self):
        """Test unknown tool names return structured error without exception."""
        unknown_cases = [
            "__nonexistent_tool__",
            "",
            "UNKNOWN",
            "12345",
            "null",
            "DROP TABLE users;",
            "../../../etc/passwd"
        ]
        for tool_name in unknown_cases:
            res = handle_tool_call(tool_name, {})
            self.assertIsInstance(res, dict)
            self.assertIn("error", res)
            self.assertIn(tool_name, res["error"])

    @patch("src.core.voice_stt_ear.VoiceEarTranscriber.record_microphone_sample")
    @patch("src.core.voice_stt_ear.VoiceEarTranscriber.transcribe_audio_file")
    @patch("src.core.voice_bridge.VoiceBridge.speak")
    def test_antigravity_mcp_all_39_tools_empty_args(self, mock_speak, mock_transcribe, mock_rec):
        """Test all 39 tool handlers with empty arguments dictionary {}."""
        mock_rec.return_value = {"status": "recorded", "output_path": "dummy.wav"}
        mock_transcribe.return_value = {"status": "success", "text": "dummy transcription"}
        mock_speak.return_value = {"status": "spoken", "dispatched": True, "engine": "Kokoro-82M"}

        for tool_name in _TOOL_HANDLERS:
            try:
                res = handle_tool_call(tool_name, {})
                self.assertIsInstance(res, dict, f"Tool {tool_name} returned non-dict on empty args")
            except Exception as e:
                self.fail(f"Tool {tool_name} raised unexpected exception on empty args: {e}")

    def test_jsonrpc_request_processing_edge_cases(self):
        """Test JSON-RPC request parser against malformed envelopes and unknown methods."""
        # 1. Unknown method
        res = _process_jsonrpc_request({"id": 1, "method": "invalid/method", "params": {}})
        self.assertEqual(res["jsonrpc"], "2.0")
        self.assertEqual(res["id"], 1)
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32601)

        # 2. tools/list
        res_list = _process_jsonrpc_request({"id": "req-2", "method": "tools/list"})
        self.assertEqual(res_list["jsonrpc"], "2.0")
        self.assertIn("result", res_list)
        self.assertIn("tools", res_list["result"])
        self.assertEqual(len(res_list["result"]["tools"]), len(TOOLS_SCHEMA))

        # 3. tools/call with unknown tool
        res_call = _process_jsonrpc_request({
            "id": "req-3",
            "method": "tools/call",
            "params": {"name": "ghost_tool", "arguments": {}}
        })
        self.assertEqual(res_call["jsonrpc"], "2.0")
        self.assertIn("result", res_call)
        content_text = res_call["result"]["content"][0]["text"]
        self.assertIn("Unknown tool: ghost_tool", content_text)

        # 4. tools/call with missing params
        res_call_empty = _process_jsonrpc_request({
            "id": "req-4",
            "method": "tools/call"
        })
        self.assertEqual(res_call_empty["jsonrpc"], "2.0")
        self.assertIn("result", res_call_empty)

    def test_domain_mcp_handle_call_tool_edge_cases(self):
        """Test domain MCP server handle_call_tool with unknown tools, None args, and empty args."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 1. Unknown tool
            res_unknown = loop.run_until_complete(handle_call_tool("unknown_tool", {}))
            self.assertGreater(len(res_unknown), 0)
            self.assertIn("Unknown tool", res_unknown[0].text)

            # 2. None arguments for valid tool
            res_none_args = loop.run_until_complete(handle_call_tool("neuro_stats", None))
            self.assertGreater(len(res_none_args), 0)

            # 3. Test non-network domain MCP tools with empty arguments
            safe_domain_tools = [
                "neuro_stats",
                "neuro_graph_query",
                "neuro_release_certificate",
                "neuro_speak",
                "neuro_play_sfx"
            ]
            for name in safe_domain_tools:
                res = loop.run_until_complete(handle_call_tool(name, {}))
                self.assertIsInstance(res, list, f"Domain tool {name} did not return a list")
                self.assertGreater(len(res), 0)
        finally:
            loop.close()

    def test_voice_command_parser_adversarial_inputs(self):
        """Test voice command parser against boundary and unstructured inputs."""
        edge_commands = [
            "",
            "   ",
            "!!!???",
            "execute order 66",
            "random unmapped utterance without any keywords",
            "set persona to INVALID_NONEXISTENT_PERSONA_NAME",
            "warp to Jita IV-4"
        ]
        for cmd in edge_commands:
            res = VoiceCommandParser.execute_command(spoken_text=cmd, speak_feedback=False)
            self.assertIsInstance(res, dict)
            self.assertIn("intent", res)
            self.assertIn("status", res)

    def test_voice_dsp_preset_fallback_safety(self):
        """Test DSP preset pipeline table with invalid or unknown presets."""
        import numpy as np
        samples = np.zeros(1024, dtype=np.float32)
        
        # Unknown preset should fallback to direct / bypass without crashing
        res = VoiceDSP.apply_dsp_preset(samples, preset="NONEXISTENT_DSP_PRESET", fs=24000)
        self.assertEqual(len(res), 1024)
        np.testing.assert_array_equal(res, samples)

    def test_voice_normalizer_code_translation_edge_cases(self):
        """Test code-to-speech normalizer with blank lines, comments, and unusual syntax."""
        # Blank / whitespace code returns empty string
        self.assertEqual(VoiceNormalizer.convert_code_to_spoken_english(""), "")
        self.assertEqual(VoiceNormalizer.convert_code_to_spoken_english("   \n\n  "), "")

        # Valid snippets produce spoken narrative
        snippets = [
            "# Just a comment",
            "def foo(x: int = 42) -> bool:\n    return x > 0\n",
            "SELECT COUNT(*) FROM table WHERE id = 1;",
            "kubectl get pods -n kube-system -o wide",
            "x = [i**2 for i in range(10) if i % 2 == 0]"
        ]
        for snippet in snippets:
            spoken = VoiceNormalizer.convert_code_to_spoken_english(snippet)
            self.assertIsInstance(spoken, str)
            self.assertGreater(len(spoken), 0)

    def test_voice_sfx_generator_unknown_type(self):
        """Test procedural SFX generator with unknown sound effect key."""
        res = VoiceSFX.synthesize_sfx("unknown_sfx_type_12345")
        self.assertIsInstance(res, (bytes, bytearray))
        self.assertGreater(len(res), 0)


if __name__ == "__main__":
    unittest.main()
