"""
Self-check unit test suite for Phase IV SOTA Knowledge Engine features:
1. Autonomous Web & Vault Dual-Retrieval Fusion Engine
2. Automated Git Diff & Refactoring Patch Synthesizer
3. Vector Index Recall@K & Latency Benchmarking Harness
"""

import pytest
from src.domain.web_rag_fusion import execute_dual_fusion_rag
from src.domain.code_diff_synthesizer import generate_refactoring_patch
from src.domain.retrieval_benchmark import benchmark_vector_retrieval
from src.domain.vector_store import DenseVectorStore


import unittest


class TestMultihopReasoning(unittest.TestCase):
    def test_dual_fusion_rag(self):
        res = execute_dual_fusion_rag("database architecture", max_local_snippets=2, max_web_results=0)
        assert res["status"] == "success"
        assert "merged_context" in res
        assert "sources" in res


    def test_refactoring_diff_synthesizer(self):
        code_a = "def hello():\n    print('old')\n"
        code_b = "def hello():\n    print('new')\n"
        res = generate_refactoring_patch(code_a, code_b, filepath="src/app.py")
        assert res["status"] == "success"
        assert res["has_changes"] is True
        assert "+    print('new')" in res["patch"]


    def test_retrieval_benchmark(self, tmp_path=None):
        if tmp_path is None:
            import tempfile, pathlib
            _temp_dir = tempfile.TemporaryDirectory()
            tmp_path = pathlib.Path(_temp_dir.name)

        db_file = str(tmp_path / "bench_vectors.db")
        store = DenseVectorStore(dimension=128, db_path=db_file)
        res = benchmark_vector_retrieval(vector_store=store, num_queries=5, dimension=128)
        assert res["status"] == "success"
        assert res["sub_10ms_guarantee"] is True
        assert "avg_latency_ms" in res
