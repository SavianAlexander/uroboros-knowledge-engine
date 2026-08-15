"""
Non-Scale RAG Validation Verification Suite.
Covers RAG Lineage Explainer, Self-Correction Rewriter, Sentence Citation Deep Linking, Persona Search Tuner, and Local RLHF.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.rag_lineage_explainer import get_rag_lineage_telemetry
from src.domain.self_correcting_rewriter import rewrite_grounded_answer
from src.domain.citation_deep_linker import create_deep_citation_link
from src.domain.persona_search_tuner import tune_search_by_persona
from src.domain.preference_learning import log_user_feedback, get_document_preference_weight


class TestNonScaleRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_lineage_explainer(self):
        res = get_rag_lineage_telemetry("Quantum", "Quantum entanglement is grounded.", ["Quantum entanglement is grounded."])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["self_rag_critique"]["IS_REL"], "[IS_REL: ✓]")
        self.assertEqual(res["self_rag_critique"]["IS_SUP"], "[IS_SUP: ✓]")

    def test_02_self_correcting_rewriter(self):
        source = ["Quantum entanglement allows instant state correlation."]
        hallucinated = "Quantum entanglement allows instant state correlation. The culinary recipe requires fresh basil."
        
        res = rewrite_grounded_answer(hallucinated, source, threshold=0.5)
        self.assertTrue(res["was_rewritten"])
        self.assertEqual(res["status"], "self_corrected")
        self.assertNotIn("culinary recipe", res["rewritten_answer"])

    def test_03_citation_deep_linker(self):
        doc = "Introductory text. Target sentence for citation linking. Closing conclusion."
        target = "Target sentence for citation linking."
        res = create_deep_citation_link(1, doc, target)
        self.assertTrue(res["found"])
        self.assertEqual(res["start_char"], 19)

    def test_04_persona_search_tuner(self):
        cands = [
            {"id": "doc_code", "content": "def example_function(): return True", "score": 0.70},
            {"id": "doc_general", "content": "General text overview.", "score": 0.72}
        ]
        res = tune_search_by_persona("function code", cands, persona="developer")
        self.assertEqual(res["status"], "success")
        # Developer persona should boost doc_code past doc_general
        self.assertEqual(res["tuned_candidates"][0]["id"], "doc_code")

    def test_05_preference_learning(self):
        res = log_user_feedback("doc101", "query", rating=1)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["new_weight"], 1.0)
        self.assertEqual(get_document_preference_weight("doc101"), res["new_weight"])

    def test_06_lineage_explain_endpoint(self):
        payload = {
            "query": "Neural Network",
            "answer": "Neural networks use artificial neurons.",
            "source_chunks": ["Neural networks use artificial neurons."]
        }
        res = self.client.post("/api/rag/lineage/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_07_grounding_rewrite_endpoint(self):
        payload = {
            "llm_response": "Astrophysics studies celestial bodies.",
            "source_chunks": ["Astrophysics is the study of celestial bodies."]
        }
        res = self.client.post("/api/rag/grounding/rewrite", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("rewritten_answer", data)

    def test_08_citation_deep_link_endpoint(self):
        payload = {
            "citation_id": 1,
            "source_document_text": "Sample document text line.",
            "target_sentence": "Sample document text line."
        }
        res = self.client.post("/api/rag/citation/deep-link", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["found"])

    def test_09_persona_search_endpoint(self):
        payload = {
            "query": "revenue quarter report",
            "candidates": [{"id": "c1", "content": "Quarterly revenue report", "score": 0.8}],
            "persona": "executive"
        }
        res = self.client.post("/api/vector/search/persona", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_10_preference_feedback_endpoint(self):
        payload = {"document_id": "doc202", "query": "q", "rating": 1}
        res = self.client.post("/api/rag/preference/feedback", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")


if __name__ == "__main__":
    unittest.main()
