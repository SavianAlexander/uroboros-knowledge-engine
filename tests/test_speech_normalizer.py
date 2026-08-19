"""
Domain Unit Test Suite: Intelligent Neural Speech Normalizer.
Standard: Pure Python Standard Library (unittest, re, json) + SpeechNormalizer.
Enterprise Naming & Domain Protocol Guard: test_speech_normalizer.py
Reference: Tududi Task #2013
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.speech_normalizer import SpeechNormalizer, number_to_words


class TestSpeechNormalizer(unittest.TestCase):
    """Test SpeechNormalizer across markdown stripping, code block summarization, and phonetic expansions."""

    def test_number_to_words(self):
        """Verify number to words conversion for arbitrary integers."""
        self.assertEqual(number_to_words(0), "zero")
        self.assertEqual(number_to_words(15), "fifteen")
        self.assertEqual(number_to_words(100), "one hundred")
        self.assertEqual(number_to_words(1250), "one thousand two hundred fifty")
        self.assertEqual(number_to_words(15000), "fifteen thousand")
        self.assertEqual(number_to_words(250000), "two hundred fifty thousand")

    def test_currency_expansion(self):
        """Verify currencies like $15,000 are expanded into natural spoken English."""
        cases = [
            ("The total cost is $15,000 for the enterprise license.", "fifteen thousand dollars"),
            ("Budget allocation of $1,250.50 was approved.", "one thousand two hundred fifty dollars and fifty cents"),
            ("Raised $500M in Series B funding.", "500 million dollars"),
            ("Estimated valuation is $2.5B.", "2.5 billion dollars"),
        ]
        for raw, expected_substr in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected_substr.lower(), norm.lower(), f"Failed on {raw} -> Got: {norm}")
            self.assertNotIn("$", norm)

    def test_technical_acronym_phonetic_expansion(self):
        """Verify technical acronyms are expanded phonetically without stuttering."""
        cases = [
            ("The SHA-256 checksum is verified.", "S-H-A two fifty six"),
            ("Consult title 14 of the eCFR regulations.", "e-C-F-R"),
            ("Indexed full text records using FTS5 virtual table.", "F-T-S five"),
            ("Execute SQL statements on the SQLite engine.", "sequel"),
            ("Call the REST API endpoints and process APIs responses.", "A-P-I"),
            ("Payload is formatted as JSON.", "j-son"),
            ("Run PRAGMA journal_mode=WAL on the database.", "pragma"),
            ("Enable WAL mode for high concurrency.", "write ahead log"),
        ]
        for raw, expected_substr in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected_substr.lower(), norm.lower(), f"Failed on {raw} -> Got: {norm}")

    def test_markdown_stripping_into_breathing_pauses(self):
        """Verify markdown headers, bold, links, and lists become smooth spoken text with breathing pauses."""
        raw = """
### System Architecture Overview
The **Uroboros Engine** utilizes [FastAPI Documentation](https://fastapi.tiangolo.com) for high throughput.
- Feature 1: Low latency
- Feature 2: High reliability
<think>Processing background telemetry</think>
All operations completed successfully.
"""
        norm = SpeechNormalizer.normalize_for_speech(raw)
        self.assertNotIn("###", norm)
        self.assertNotIn("**", norm)
        self.assertNotIn("[FastAPI Documentation]", norm)
        self.assertNotIn("https://", norm)
        self.assertNotIn("think", norm.lower())
        self.assertIn("System Architecture Overview", norm)
        self.assertIn("Oo-roh-bor-os Engine", norm)
        self.assertIn("Fast A-P-I Documentation", norm)
        self.assertIn("Low latency", norm)
        self.assertIn("All operations completed successfully.", norm)

    def test_code_block_summarization(self):
        """Verify fenced code blocks are summarized into natural spoken developer descriptions."""
        code_input = """
Here is the implementation:
```python
def calculate_merkle_root(transactions: list) -> str:
    return sha256_hash(transactions)
```
Let me know if you want to proceed.
"""
        norm = SpeechNormalizer.normalize_for_speech(code_input)
        self.assertNotIn("```", norm)
        self.assertIn("A code snippet defining function calculate merkle root", norm)
        self.assertIn("Let me know if you want to proceed.", norm)

    def test_cadence_double_punctuation_cleaning(self):
        """Verify cadence formatting prevents duplicate commas and preserve decimal numbers."""
        raw = "Latency is 3.14 ms, , and throughput is 100%.. All systems nominal; proceeding."
        norm = SpeechNormalizer.normalize_for_speech(raw)
        self.assertNotIn(", ,", norm)
        self.assertNotIn("..", norm)
        self.assertIn("3.14", norm)
        self.assertIn("100 percent", norm)


if __name__ == "__main__":
    unittest.main()
