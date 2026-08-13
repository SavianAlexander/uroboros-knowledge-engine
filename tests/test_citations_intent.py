import unittest
from src.domain.source_citation_generator import locate_text_in_file, generate_source_citations
from src.domain.query_intent_classifier import classify_query_intent
from fastapi.testclient import TestClient
from src.app.main import app

class TestCitationsAndIntent(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_classify_query_intent(self):
        res1 = classify_query_intent("accounting standards vs GAAP")
        self.assertEqual(res1["intent"], "comparative_analysis")

        res2 = classify_query_intent("summarize annual financial report")
        self.assertEqual(res2["intent"], "analytical_summary")

        res3 = classify_query_intent("def parse_query_operators")
        self.assertEqual(res3["intent"], "code_search")

    def test_02_generate_source_citations(self):
        passages = [
            {"filename": "report.md", "filepath": "C:/tmp/report.md", "content": "Financial statement preview"}
        ]
        citations = generate_source_citations(passages)
        self.assertEqual(len(citations), 1)
        self.assertIn("report.md", citations[0]["markdown_citation"])

    def test_03_citations_and_intent_endpoints(self):
        res1 = self.client.get("/api/search/classify-intent?query=compare+GAAP+and+IFRS")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["intent"], "comparative_analysis")

        res2 = self.client.post("/api/search/generate-citations", json={
            "passages": [{"filename": "doc.md", "content": "sample content"}]
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
