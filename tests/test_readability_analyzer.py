import unittest
from src.domain.readability_analyzer import analyze_readability, count_syllables_in_word
from fastapi.testclient import TestClient
from src.app.main import app

import os

class TestReadabilityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        os.makedirs("dumps", exist_ok=True)
        with open("dumps/sample.txt", "w", encoding="utf-8") as f:
            f.write("The quick brown fox jumps over the lazy dog. It was an excellent day for software testing!\n")

    def test_count_syllables_in_word(self):
        self.assertEqual(count_syllables_in_word("cat"), 1)
        self.assertEqual(count_syllables_in_word("beautiful"), 3)

    def test_analyze_readability_formula(self):
        sample_text = "The quick brown fox jumps over the lazy dog. It was an excellent day for software testing!"
        res = analyze_readability(sample_text)
        
        self.assertEqual(res["status"], "success")
        self.assertIn("flesch_reading_ease", res)
        self.assertIn("flesch_kincaid_grade", res)
        self.assertIn("sentiment_score", res)
        self.assertEqual(res["sentiment_label"], "Positive")

    def test_file_readability_endpoint(self):
        res = self.client.get("/api/file/readability?filepath=dumps/sample.txt")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("flesch_reading_ease", data)
        self.assertIn("reading_level", data)

if __name__ == "__main__":
    unittest.main()
