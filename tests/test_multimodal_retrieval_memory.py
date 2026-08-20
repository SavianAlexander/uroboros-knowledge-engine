"""
Unit test suite for Multimodal Retrieval and Memory features:
1. 2-Phase Matryoshka Vector Search
2. Cognitive Swarm RAG Engine
3. Agentic Long-Term Memory
4. Workspace Screen Perception Engine
"""

import os
import pytest
from src.domain.vector_store import DenseVectorStore
from src.domain.rag_engine import execute_swarm_rag
from src.domain.agent_memory import remember, recall, list_memories
from src.domain.screen_perception import capture_screen_context


import unittest


class TestMultimodalRetrievalMemory(unittest.TestCase):
    def test_2phase_mrl_vector_search(self, tmp_path=None):
        if tmp_path is None:
            import tempfile, pathlib
            _temp_dir = tempfile.TemporaryDirectory()
            tmp_path = pathlib.Path(_temp_dir.name)

        db_file = str(tmp_path / "test_mrl_vectors.db")
        store = DenseVectorStore(dimension=128, db_path=db_file)

        # Add dummy vectors
        vec_a = [0.1 * i for i in range(128)]
        vec_b = [0.05 * i for i in range(128)]
        store.add_vector("doc_1", vec_a, {"title": "Doc 1"})
        store.add_vector("doc_2", vec_b, {"title": "Doc 2"})

        query = [0.09 * i for i in range(128)]
        results = store.search_nearest_2phase(query, top_k=2, coarse_dim=32, candidate_k=5)

        assert len(results) > 0
        assert results[0][0] in ["doc_1", "doc_2"]


    def test_agent_memory_persistence(self, tmp_path=None):
        if tmp_path is None:
            import tempfile, pathlib
            _temp_dir = tempfile.TemporaryDirectory()
            tmp_path = pathlib.Path(_temp_dir.name)

        db_file = str(tmp_path / "test_agent_memory.db")
        res = remember("user_theme", "dark", category="ui_config", db_path=db_file)
        assert res["status"] == "success"

        recalled = recall("user_theme", category="ui_config", db_path=db_file)
        assert recalled == "dark"

        all_memories = list_memories(db_path=db_file)
        assert len(all_memories) == 1
        assert all_memories[0]["key"] == "user_theme"


    def test_screen_perception_fallback(self):
        perception = capture_screen_context(sample_ocr=False)
        assert "status" in perception
        assert "timestamp" in perception


    def test_cognitive_swarm_rag(self):
        res = execute_swarm_rag("database architecture", db_path="e2e_knowledge.db")
        assert "synthesis" in res
        assert "sources" in res
        assert "critic_audit" in res
