"""
Self-check unit test suite for Phase II SOTA Knowledge Engine features:
1. Vault Contradiction & Discrepancy Resolver
2. Keystroke Speculative Context Warmer
3. Multi-Language AST Code-Flow Parser
"""

import pytest
from src.domain.contradiction_resolver import detect_vault_contradictions
from src.domain.speculative_warmer import SpeculativeContextWarmer
from src.domain.ast_parser import parse_python_ast
from src.domain.vector_store import DenseVectorStore


import unittest


class TestContextWarmerAst(unittest.TestCase):
    def test_contradiction_resolver(self):
        res = detect_vault_contradictions(limit=10)
        assert "status" in res
        assert "contradictions" in res


    def test_speculative_context_warmer(self, tmp_path=None):
        if tmp_path is None:
            import tempfile, pathlib
            _temp_dir = tempfile.TemporaryDirectory()
            tmp_path = pathlib.Path(_temp_dir.name)

        db_file = str(tmp_path / "test_warmer_vectors.db")
        store = DenseVectorStore(dimension=128, db_path=db_file)
        store.add_vector("doc_alpha", [0.1] * 128, {"title": "Alpha"})

        warmer = SpeculativeContextWarmer(vector_store=store)
        sample_vec = [0.1] * 128

        doc_ids = warmer.warm_prefix("alp", sample_vec)
        assert len(doc_ids) > 0
        assert doc_ids[0] == "doc_alpha"

        cached = warmer.get_warmed_candidates("alp")
        assert cached == ["doc_alpha"]


    def test_ast_python_parser(self):
        sample_code = '''
    import os
    from math import sqrt

    class KnowledgeHub:
        def __init__(self):
            self.val = sqrt(16)

        def query(self, text: str):
            return os.path.exists(text)
    '''
        res = parse_python_ast(sample_code, filename="hub.py")
        assert res["status"] == "success"
        assert "KnowledgeHub" in res["classes"]
        assert "query" in res["functions"]
        assert "os" in res["imports"]
        assert len(res["graph_edges"]) > 0
