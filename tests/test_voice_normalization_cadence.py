"""
Domain Unit Test Suite: Neural Voice Normalization, Cadence & Formatting Sanitization.
Standard: Pure Python Standard Library (unittest, re, json) + Kokoro Voice Engine.
Enterprise Naming & Domain Protocol Guard: test_voice_normalization_cadence.py
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_streaming import StreamingNeuralSynthesizer
from src.core.voice_engine import KokoroVoiceEngine


class TestVoiceNormalizationCadence(unittest.TestCase):
    """Test VoiceNormalizer against raw text, code fences, tags, file paths, and math symbols."""

    def test_file_extension_pronunciation(self):
        """Verify file extensions like .txt, .json, .md are pronounced naturally without '. txt' artifacts."""
        cases = [
            ("Please check notes.txt for updates.", "notes text file"),
            ("The settings are stored in config.json.", "config Jason file"),
            ("Read the AGENTS.md document.", "AGENTS markdown file"),
            ("Execute the script.py file.", "script Python script"),
            ("Review output.log for errors.", "output log file"),
            ("Export data to report.csv immediately.", "report C-S-V file"),
            ("Inspect the schema.sql script.", "schema sequel file"),
            ("Download document.pdf from the server.", "document P-D-F document"),
        ]
        for raw, expected_substr in cases:
            norm = VoiceNormalizer.normalize_for_speech(raw)
            self.assertIn(expected_substr.lower(), norm.lower(), f"Failed on {raw} -> Got: {norm}")
            self.assertNotIn(". txt", norm.lower())
            self.assertNotIn(". json", norm.lower())

    def test_html_xml_and_thought_tag_stripping(self):
        """Verify LLM internal reasoning tags (<think>), <details>, and HTML/XML tags are stripped completely."""
        raw = "Start. <think>Evaluating options and formulating response...</think><details><summary>Logs</summary><div>Status OK</div></details> Operation complete."
        norm = VoiceNormalizer.normalize_for_speech(raw)
        self.assertNotIn("think", norm.lower())
        self.assertNotIn("details", norm.lower())
        self.assertNotIn("summary", norm.lower())
        self.assertNotIn("div", norm.lower())
        self.assertIn("Start.", norm)
        self.assertIn("Operation complete.", norm)

    def test_code_fence_txt_sanitization(self):
        """Verify code blocks with txt/text/log are cleanly handled without verbalizing 'xt' or '. txt.'."""
        raw = "Here is the response:\n```txt\nServer running on port 8000\nConnected to SQLite database\n```\nAll systems nominal."
        norm = VoiceNormalizer.normalize_for_speech(raw)
        self.assertNotIn(". xt.", norm)
        self.assertNotIn("xt.", norm)
        self.assertIn("Server running on port 8000", norm)
        self.assertIn("Sequel Light database", norm)
        self.assertIn("All systems nominal.", norm)

    def test_windows_and_unix_path_sanitization(self):
        """Verify full directory paths are simplified to the base file name."""
        cases = [
            ("Refer to C:\\Users\\Administrator\\Desktop\\Neuro Alexander\\output.txt for details.", "output text file"),
            ("Logs located at /var/log/nginx/access.log on the server.", "access log file"),
            ("Check file:///C:/Users/Admin/workspace/data.json now.", "data Jason file"),
        ]
        for raw, expected_substr in cases:
            norm = VoiceNormalizer.normalize_for_speech(raw)
            self.assertIn(expected_substr.lower(), norm.lower())
            self.assertNotIn("c:\\users", norm.lower())
            self.assertNotIn("/var/log", norm.lower())

    def test_unicode_math_and_glyphs(self):
        """Verify math symbols and checklist glyphs are translated to spoken words without encoding crashes."""
        raw = "Summary: • Task 1 completed ✓ with score ∑(x) ≥ 95% and speed ≈ 3.14 ms. ⚠️ Warning: 100% verified."
        norm = VoiceNormalizer.normalize_for_speech(raw)
        self.assertIn("completed", norm)
        self.assertIn("sum of", norm)
        self.assertIn("greater than or equal to", norm)
        self.assertIn("approximately", norm)
        self.assertIn("3.14 milliseconds", norm)
        self.assertIn("Warning:", norm)
        # Verify no duplicate 'Warning: Warning:'
        self.assertNotIn("Warning: Warning:", norm)

    def test_acoustic_clause_splitter_preserves_commas(self):
        """Verify acoustic clause splitter does not inject artificial periods into comma-separated phrases."""
        text = "When you start the application, the local database connects, and the user interface mounts."
        clauses = StreamingNeuralSynthesizer.split_into_acoustic_clauses(text)
        self.assertEqual(len(clauses), 1, f"Expected 1 coherent sentence, got: {clauses}")
        self.assertNotIn("application.", clauses[0])
        self.assertNotIn("connects.", clauses[0])

    def test_snake_case_test_names_pronounced_with_spaces(self):
        """Verify test runner identifiers with underscores are spoken with natural spaces and no stutter."""
        cases = [
            ("Running test_voice_normalization_cadence now.", "test voice normalization cadence"),
            ("Executing test_voice_real_data_integration suite.", "test voice real data integration"),
            ("Passed test_mcp_adversarial_edge_cases.", "test M-C-P adversarial edge cases"),
        ]
        for raw, expected_substr in cases:
            norm = VoiceNormalizer.normalize_for_speech(raw)
            self.assertIn(expected_substr.lower(), norm.lower(), f"Failed on {raw} -> Got: {norm}")
            self.assertNotIn("testvoicenormalizationcadence", norm.lower())
            self.assertNotIn("testvoicerealdataintegration", norm.lower())

    def test_sfx_intro_prepends_into_single_speech_buffer(self):
        """Verify sfx_intro chime prepends seamlessly into speech audio bytes without double-queuing."""
        engine = KokoroVoiceEngine()
        if engine._local_kokoro_instance:
            res_without = engine.speak(text="Test announcement.", priority="NORMAL", blocking=False)
            res_with = engine.speak(text="Test announcement.", priority="NORMAL", sfx_intro="target_lock", blocking=False)
            self.assertGreater(res_with["bytes_len"], res_without["bytes_len"])

    def test_kokoro_synthesis_on_sanitized_text(self):
        """Verify local Kokoro engine produces clean audio without exceptions on challenging inputs."""
        engine = KokoroVoiceEngine()
        if engine._local_kokoro_instance:
            text = "Reviewing output.txt and config.json with 3.14 ms latency. <think>Hidden thought</think> Operation verified."
            audio = engine.synthesize_neural_audio(text, voice="af_bella")
            self.assertIsNotNone(audio)
            self.assertGreater(len(audio), 1000)


if __name__ == "__main__":
    unittest.main()
