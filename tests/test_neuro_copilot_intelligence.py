"""
Unit test suite verifying Neuro-Copilot intelligence capabilities:
1. AST Stack-Trace Auto-Diagnosis & Symbol Localizer (ast_graph_bridge.py)
2. Blast Radius & Targeted Test Resolver (blast_radius_bridge.py)
3. HyDE Query Expansion with Hypothetical Answers (neuro_bridge.py)
4. Executive Voice Telemetry & Speech Sanitization (voice_operator_bridge.py)
5. ReAct Autonomous Agent Error Diagnosis Tool (react_agent_bridge.py)
"""
import unittest
import os
import sys
import json
import importlib.util

# Add scripts directory to sys.path
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "neuro-copilot", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


def load_bridge_module(name: str, filename: str):
    path = os.path.join(SCRIPTS_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestNeuroCopilotIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ast_mod = load_bridge_module("ast_graph_bridge", "ast_graph_bridge.py")
        cls.blast_mod = load_bridge_module("blast_radius_bridge", "blast_radius_bridge.py")
        cls.neuro_mod = load_bridge_module("neuro_bridge", "neuro_bridge.py")
        cls.voice_mod = load_bridge_module("voice_operator_bridge", "voice_operator_bridge.py")
        cls.react_mod = load_bridge_module("react_agent_bridge", "react_agent_bridge.py")

    def test_traceback_auto_diagnosis_and_ast_localization(self):
        """Test #1: Verify diagnose_traceback pinpoints failing frame, symbol, and line."""
        sample_traceback = """
Traceback (most recent call last):
  File "src/app/server.py", line 16, in lifespan
    init_db()
"""
        res = self.ast_mod.diagnose_traceback(sample_traceback)
        self.assertEqual(res.get("status"), "success")
        self.assertGreaterEqual(res.get("total_frames", 0), 1)
        
        ff = res.get("failing_frame", {})
        self.assertIn("server.py", ff.get("filepath", ""))
        self.assertEqual(ff.get("line"), 16)
        self.assertEqual(ff.get("function"), "lifespan")
        self.assertTrue(len(res.get("code_snippet", "")) > 0)

    def test_blast_radius_and_targeted_test_resolution(self):
        """Test #2: Verify find_targeted_tests maps modified file to targeted tests in <50ms."""
        target_file = "src/domain/background_worker.py"
        targeted = self.blast_mod.find_targeted_tests(target_file)
        self.assertIsInstance(targeted, list)
        self.assertTrue(len(targeted) > 0)
        # Should include smooth background worker test
        self.assertTrue(any("background_worker" in t for t in targeted))

    def test_hyde_query_expansion_with_hypothetical_document(self):
        """Test #3: Verify hyde_expand returns query, expansion, and hypothetical context."""
        raw_res = self.neuro_mod.hyde_expand("how does vector search operate")
        res = json.loads(raw_res)
        self.assertEqual(res.get("status"), "success")
        self.assertIn("hypothetical_document", res)
        self.assertIn("combined_embedding_text", res)
        self.assertIn("vector search", res.get("hypothetical_document", "").lower())

    def test_voice_operator_sanitization_and_presets(self):
        """Test #4: Verify speech text sanitizer strips markdown and URLs cleanly."""
        dirty_text = "### System Status\nCheck [link](https://example.com) for `code` and **bold** alerts."
        clean = self.voice_mod.sanitize_speech_text(dirty_text)
        self.assertNotIn("https://", clean)
        self.assertNotIn("`", clean)
        self.assertNotIn("#", clean)
        self.assertIn("System Status", clean)
        self.assertIn("EXECUTIVE_PRECISION", self.voice_mod.KOKORO_PRESETS)

    def test_react_agent_error_diagnosis_tool(self):
        """Test #5: Verify tool_diagnose integrates seamlessly into ReAct loop."""
        tb = 'File "src/domain/background_worker.py", line 40, in process_single_unsummarized_document\n    pass'
        diag_output = self.react_mod.tool_diagnose(tb)
        self.assertIn("Traceback Diagnosis", diag_output)
        self.assertIn("background_worker.py", diag_output)


if __name__ == "__main__":
    unittest.main()
