"""
Frontier RAG Validation Verification Suite.
Covers Active RAG Loop, Adaptive Context Budget Allocator, and Distractor Filter.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.rag_engine import execute_active_rag_loop, reformulate_query
from src.domain.context_budget_allocator import allocate_context_budget
from src.domain.distractor_filter import filter_distractor_chunks


class TestFrontierRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_active_rag_loop(self):
        query = "Quantum Entanglement"
        chunks_good = ["Quantum entanglement allows instant state correlation across spatial distances."]
        chunks_bad = ["The weather forecast calls for sunny skies."]
        
        res_good = execute_active_rag_loop(query, chunks_good, confidence_threshold=0.3)
        self.assertFalse(res_good["second_pass_required"])
        self.assertEqual(res_good["status"], "optimal")

        res_bad = execute_active_rag_loop(query, chunks_bad, confidence_threshold=0.3)
        self.assertTrue(res_bad["second_pass_required"])
        self.assertEqual(res_bad["status"], "refinement_needed")

    def test_02_context_budget_allocator(self):
        vec_chunks = ["Chunk 1 text content " * 10, "Chunk 2 text content " * 10]
        halos = ["Graph halo 1 " * 5]
        
        res = allocate_context_budget(total_token_budget=1000, vector_chunks=vec_chunks, graph_halos=halos)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["approx_tokens_used"], 0)
        self.assertIn("allocated_chunks", res)
        self.assertIn("allocated_halos", res)

    def test_03_distractor_filter(self):
        query = "Neural Network Optimization"
        candidates = [
            {"id": "c1", "content": "Neural network optimization algorithms include SGD and Adam."},
            {"id": "c2", "content": "The culinary recipe requires fresh basil and olive oil."}
        ]
        
        res = filter_distractor_chunks(query, candidates, min_intent_overlap=0.25)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["filtered_candidates"]), 1)
        self.assertEqual(res["filtered_candidates"][0]["id"], "c1")
        self.assertEqual(res["distractors_removed"], 1)

    def test_04_active_rag_endpoint(self):
        payload = {
            "query": "Relativistic Physics",
            "initial_chunks": ["Relativistic physics generalizes Newton equations."],
            "confidence_threshold": 0.3
        }
        res = self.client.post("/api/rag/active/refine", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("second_pass_required", data)
        self.assertIn("refined_query", data)

    def test_05_budget_allocate_endpoint(self):
        payload = {
            "total_token_budget": 2048,
            "vector_chunks": ["Sample chunk content text."],
            "graph_halos": ["Sample halo text."]
        }
        res = self.client.post("/api/rag/budget/allocate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_06_distractor_filter_endpoint(self):
        payload = {
            "query": "Superconducting Qubits",
            "candidates": [
                {"id": "q1", "content": "Superconducting qubits operate at cryogenic temperatures."},
                {"id": "d1", "content": "The recipe requires baking at 350 degrees."}
            ],
            "min_intent_overlap": 0.15
        }
        res = self.client.post("/api/rag/distractor/filter", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["filtered_candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
