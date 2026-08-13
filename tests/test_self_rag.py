import unittest
from src.domain.self_rag_critique import evaluate_relevance, evaluate_support, critique_rag_passages
from src.domain.parent_child_retrieval import expand_child_chunks_to_parents
from fastapi.testclient import TestClient
from src.app.main import app

class TestSelfRagAndParentChild(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_evaluate_relevance(self):
        q = "accounting standards IFRS"
        c1 = "International Financial Reporting Standards (IFRS) govern corporate accounting."
        c2 = "The weather today is sunny with mild winds."
        
        rel1 = evaluate_relevance(q, c1)
        rel2 = evaluate_relevance(q, c2)
        
        self.assertTrue(rel1["relevant"])
        self.assertEqual(rel1["token"], "[IsRel:Yes]")
        self.assertFalse(rel2["relevant"])
        self.assertEqual(rel2["token"], "[IsRel:No]")

    def test_02_evaluate_support(self):
        a = "IFRS governs accounting standards."
        c = "International Financial Reporting Standards (IFRS) govern corporate accounting."
        sup = evaluate_support(a, c)
        
        self.assertTrue(sup["supported"])
        self.assertEqual(sup["token"], "[IsSup:FullySupported]")

    def test_03_critique_rag_passages(self):
        q = "software engineering"
        chunks = [
            "Software engineering principles prioritize modular clean code.",
            "Accounting standards regulate balance sheet audits."
        ]
        critiqued = critique_rag_passages(q, chunks)
        self.assertEqual(len(critiqued), 1)
        self.assertIn("software", critiqued[0]["content"].lower())

    def test_04_parent_child_endpoints(self):
        res1 = self.client.get("/api/search/parent-context?file_ids=1,2,3")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
