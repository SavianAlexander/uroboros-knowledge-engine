"""
Self-check unit test suite for Core RAG Retrieval Paradigms v3:
1. Knowledge Graph Self-Healing & Wikilink Synthesizer
2. Specular Speculative Context Streaming Guard
3. Multi-Document Semantic Diff & Evolution Tracker
4. Dynamic Context Budget Allocator
"""

import pytest
from src.domain.graph_link_synthesizer import auto_synthesize_wikilinks
from src.domain.speculative_streamer import speculative_stream_context
from src.domain.semantic_doc_diff import compute_semantic_doc_diff
from src.domain.context_budget_allocator import allocate_context_budget


import unittest


class TestGraphWikilinksSpeculativeBudgeting(unittest.TestCase):
    def test_graph_link_synthesizer(self):
        text = "The SQLite WAL mode improves database performance."
        known = ["SQLite WAL mode", "database performance"]
        res = auto_synthesize_wikilinks(text, known)
        assert res["status"] == "success"
        assert res["links_added"] >= 1
        assert "[[SQLite WAL mode]]" in res["synthesized_text"]


    def test_speculative_streamer(self):
        snippets = ["Quantum computing relies on qubits.", "Superposition enables parallel state computation."]
        stream = list(speculative_stream_context(snippets, chunk_size=5))
        assert len(stream) > 1
        assert stream[0]["is_first_token"] is True
        assert stream[-1]["type"] == "context_stream_done"


    def test_semantic_doc_diff(self):
        doc_a = "SQLite database uses WAL mode for concurrency."
        doc_b = "SQLite database uses WAL mode for concurrency. Vector search embeddings are stored in SQLite."
        res = compute_semantic_doc_diff(doc_a, doc_b)
        assert res["status"] == "success"
        assert res["added_claims_count"] == 1
        assert res["retained_claims_count"] == 1


    def test_context_budget_allocator(self):
        res = allocate_context_budget(max_tokens=4096, vector_snippets=["snippet 1"], graph_pathways=["path 1"])
        assert res["status"] == "success"
        assert res["allocations"]["vector_snippets"]["token_budget"] == 2048
        assert res["allocations"]["graph_pathways"]["token_budget"] == 1024
