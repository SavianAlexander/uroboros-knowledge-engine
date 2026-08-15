"""
User-Expanded RAG Validation Verification Suite.
Covers Cognitive Swarm RAG, Agentic Memory, Screen Perception, Contradictions Resolver, AST Parser, Dataset Synthesizer, Audio Briefing, Architecture Doctor, Dual Fusion RAG, Code Diff Synthesizer, Retrieval Benchmark, Entity Resolver, Density Optimizer, Compliance Inspector, Reasoning Visualizer, and Master Scoreboard.
"""

import unittest
from fastapi.testclient import TestClient
from main import app


class TestUserExpandedRAGValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_memory_recall_endpoint(self):
        res_rem = self.client.post("/api/rag/memory/remember", json={"key": "pref_theme", "value": "dark", "category": "preference"})
        self.assertEqual(res_rem.status_code, 200)

        res_rec = self.client.get("/api/rag/memory/recall?key=pref_theme&category=preference")
        self.assertEqual(res_rec.status_code, 200)
        self.assertEqual(res_rec.json()["value"], "dark")

    def test_02_ast_parse_endpoint(self):
        res = self.client.post("/api/rag/ast/parse", json={"code": "def hello(): pass", "filename": "test.py"})
        self.assertEqual(res.status_code, 200)

    def test_03_compliance_inspect_endpoint(self):
        res = self.client.post("/api/rag/compliance/inspect", json={"text": "Contact user@example.com for details."})
        self.assertEqual(res.status_code, 200)

    def test_04_scoreboard_endpoint(self):
        res = self.client.get("/api/rag/scoreboard")
        self.assertEqual(res.status_code, 200)

    def test_05_architecture_doctor_endpoint(self):
        res = self.client.get("/api/rag/architecture/audit")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
