"""
Self-check unit test suite for Comparative SOTA RAG Frontier Paradigms:
1. Counterfactual RAG & Multi-Scenario Stress Testing
2. RAPTOR Tree Indexer
3. Episodic Memory RAG
4. Binary ColBERT MaxSim Reranker
5. Inline Self-Correction & Real-Time Source Patching
"""

import pytest
from src.domain.rag_engine import execute_counterfactual_rag
from src.domain.raptor_tree_indexer import build_raptor_tree, search_raptor_tree
from src.domain.episodic_rag import query_episodic_rag
from src.domain.binary_colbert import binary_colbert_maxsim, rerank_search_results_colbert
from src.domain.auto_correct_rag import auto_correct_grounding


def test_counterfactual_rag():
    res = execute_counterfactual_rag("database connection pool")
    assert res["status"] == "success"
    assert res["stress_tested"] is True
    assert len(res["scenarios"]) >= 1


def test_raptor_tree_indexer():
    chunks = [
        {"text": "SQLite WAL mode enables concurrent readers and single writer.", "source": "db.txt"},
        {"text": "FTS5 provides full-text search indexing with BM25 ranking.", "source": "fts.txt"},
        {"text": "PyInstaller bundles standard library Python modules into standalone binary.", "source": "build.txt"}
    ]
    tree = build_raptor_tree(chunks)
    assert tree["status"] == "success"
    assert tree["tree_depth"] in (2, 3)
    assert tree["level_0_count"] == 3
    assert tree["level_1_count"] >= 1

    level_1_nodes = search_raptor_tree(tree, "SQLite database", target_level=1)
    assert len(level_1_nodes) >= 1


def test_episodic_rag():
    res = query_episodic_rag("database architecture", session_id="session_101")
    assert res["status"] == "success"
    assert "vault_snippets" in res
    assert "episodic_memories" in res


def test_binary_colbert_maxsim():
    q_tokens = [[0.5, -0.2, 0.1] * 22]
    d_tokens = [[0.4, -0.1, 0.2] * 22]
    score = binary_colbert_maxsim(q_tokens, d_tokens)
    assert score > 0.5

    # Test candidate reranking
    candidates = [
        {"id": 1, "snippet": "Unrelated culinary recipe for apple pie", "score": 0.8},
        {"id": 2, "snippet": "High performance SQLite database WAL connection pool", "score": 0.5}
    ]
    reranked = rerank_search_results_colbert("SQLite database performance", candidates, top_k=2)
    assert len(reranked) == 2
    assert reranked[0]["id"] == 2


def test_auto_correct_grounding():
    resp = "Quantum computing relies on qubits."
    chunks = ["Quantum computing uses qubits and superposition."]
    res = auto_correct_grounding(resp, chunks)
    assert res["status"] in ("success", "grounded", "corrected")
    assert "patched_response" in res
