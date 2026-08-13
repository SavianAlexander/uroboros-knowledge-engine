import unittest
from src.domain.entity_extractor import extract_entities_from_text
from fastapi.testclient import TestClient
from src.app.main import app

class TestEntityExtractor(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_extract_entities_from_text(self):
        sample_text = "International Financial Reporting Standards (IFRS) and GAAP regulate Accounting principles in Uroboros Engine."
        res = extract_entities_from_text(sample_text, top_k=5)
        
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_words"], 0)
        self.assertIsInstance(res["entities"], list)
        self.assertIsInstance(res["keywords"], list)

    def test_file_entities_endpoint(self):
        res = self.client.get("/api/file/entities?filepath=dumps/sample.txt&top_k=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("entities", data)
        self.assertIn("keywords", data)

if __name__ == "__main__":
    unittest.main()
