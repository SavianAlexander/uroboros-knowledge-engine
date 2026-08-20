"""
Self-check unit test suite for Next-Level Comparative RAG Frontier Paradigms v2:
1. Semantic Entropy Context Compressor
2. Zero-Shot Cross-Lingual RAG Fusion
3. Quantum-Safe Zero-Knowledge Data Masker
4. Sub-1ms Speculative Query Intent Router
"""

import pytest
from src.domain.adaptive_context_compressor import compress_context_entropy
from src.domain.rag_engine import cross_lingual_rag_search, expand_cross_lingual_query
from src.domain.zk_data_masker import mask_payload_with_zk_proof
from src.domain.intent_router import route_query_intent, classify_query_intent


import unittest


class TestCrossLingualEntropyIntentRouting(unittest.TestCase):
    def test_adaptive_context_compressor(self):
        chunks = [
            "First sentence provides basic overview. The database configuration uses SQLite WAL mode on port 8000.",
            "Just filler text with no numbers or code."
        ]
        res = compress_context_entropy(chunks)
        assert res["status"] == "success"
        assert res["compressed_chars"] <= res["original_chars"]
        assert len(res["compressed_chunks"]) == 2


    def test_cross_lingual_fusion(self):
        exp = expand_cross_lingual_query("database security")
        assert "base de datos" in exp
        assert "sicherheit" in exp

        res = cross_lingual_rag_search("database security", max_chunks=2)
        assert res["status"] == "success"
        assert "expanded_cross_lingual_query" in res


    def test_zk_data_masker(self):
        res = mask_payload_with_zk_proof("secret database password admin123")
        assert res["status"] == "success"
        assert "zk_proof" in res
        assert "[ZK_" in res["masked_payload"]


    def test_intent_router(self):
        assert classify_query_intent("def main():") == "code_search"
        assert classify_query_intent("summary report") == "executive_summary"

        res = route_query_intent("how to fix database error")
        assert res["status"] == "success"
        assert res["classified_intent"] == "code_search"
        assert "recommended_pipeline" in res
