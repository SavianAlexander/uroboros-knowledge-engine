import unittest
from src.domain.extractive_summarizer import summarize_text
from fastapi.testclient import TestClient
from src.app.main import app

class TestExtractiveSummarizer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_summarize_text_extractive(self):
        sample_text = (
            "Accounting standards regulate corporate financial reporting worldwide. "
            "The International Financial Reporting Standards (IFRS) set global rules for balance sheets. "
            "Compliance audits verify that accounting records match published financial reports. "
            "Zero-dependency software architectures eliminate supply chain vulnerabilities."
        )
        res = summarize_text(sample_text, max_sentences=2)
        
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_sentences"], 0)
        self.assertEqual(len(res["key_sentences"]), 2)
        self.assertIn("summary", res)

    def test_file_summary_endpoint(self):
        res = self.client.get("/api/file/summary?filepath=dumps/sample.txt&max_sentences=2")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("summary", data)
        self.assertIn("key_sentences", data)

if __name__ == "__main__":
    unittest.main()
