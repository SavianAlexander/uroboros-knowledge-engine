"""
54-Subsystem Extended Platform Validation Verification Suite.
Covers Autonomous Code Self-Refactoring, Agent Swarm Manager, Docstring Harmonizer, and ZK Data Masker.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.code_self_refactor import analyze_and_propose_refactoring
from src.domain.rag_engine import decompose_goal_into_agent_swarm
from src.domain.code_doc_aligner import check_code_docstring_alignment
from src.domain.zk_data_masker import mask_payload_with_zk_proof


class TestExtendedPlatformValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_code_self_refactor(self):
        code = "def large_fn():\n" + "\n".join([f"    x_{i} = {i}" for i in range(20)])
        res = analyze_and_propose_refactoring(code)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["refactor_needed"])

    def test_02_agent_swarm_manager(self):
        goal = "Build end-to-end multi-modal pipeline"
        res = decompose_goal_into_agent_swarm(goal)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_worker_agents"], 4)

    def test_03_code_doc_aligner(self):
        code = "def process(val_a, val_b):\n    '''Doc for val_a only.'''\n    pass"
        res = check_code_docstring_alignment(code)
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_aligned"])

    def test_04_zk_data_masker(self):
        res = mask_payload_with_zk_proof("secret_ssn_12345")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["verification_passed"])
        self.assertIn("zk_proof_hash", res)

    def test_05_endpoints(self):
        res_swarm = self.client.post("/api/rag/swarm/decompose", json={"master_goal": "Goal test"})
        self.assertEqual(res_swarm.status_code, 200)

        res_zk = self.client.post("/api/rag/privacy/zk-mask", json={"sensitive_data": "secret"})
        self.assertEqual(res_zk.status_code, 200)


if __name__ == "__main__":
    unittest.main()
