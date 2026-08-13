import unittest
from src.domain.graph_multihop import find_multihop_pathways
from src.domain.contextual_hyde import generate_hypothetical_document, format_contextual_chunk
from fastapi.testclient import TestClient
from src.app.main import app

class TestMultihopHyde(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_generate_hypothetical_document(self):
        q = "accounting standards regulate financial balance sheets"
        res = generate_hypothetical_document(q)
        self.assertEqual(res["status"], "success")
        self.assertIn("hypothetical_text", res)

    def test_02_format_contextual_chunk(self):
        formatted = format_contextual_chunk("Sample chunk content", "Annual Report 2026", ["Finance", "Audit"])
        self.assertIn("Annual Report 2026", formatted)
        self.assertIn("Finance, Audit", formatted)

    def test_03_find_multihop_pathways(self):
        res = find_multihop_pathways("non_existent_doc_xyz")
        self.assertIn(res["status"], ["success", "error"])


    def test_04_multihop_and_hyde_endpoints(self):
        res1 = self.client.get("/api/search/hyde?query=accounting+standards")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "success")

        res2 = self.client.get("/api/graph/multihop?start_doc=sample.txt")
        self.assertEqual(res2.status_code, 200)

if __name__ == "__main__":
    unittest.main()
