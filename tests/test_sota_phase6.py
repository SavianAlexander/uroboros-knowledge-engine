"""
Self-check unit test suite for Phase VI SOTA Knowledge Engine features:
1. Knowledge Graph Reasoning Path Visualizer
2. Incremental SHA-256 Vector Cache Guard
3. Master System Telemetry Scoreboard
"""

import pytest
from src.domain.reasoning_visualizer import generate_mermaid_reasoning_diagram
from src.domain.cache_guard import VectorCacheGuard
from src.domain.system_scoreboard import generate_system_scoreboard


def test_reasoning_visualizer():
    pathways = [
        {"path_filenames": ["Doc A.md", "Doc B.md", "Doc C.md"]}
    ]
    res = generate_mermaid_reasoning_diagram(pathways)
    assert res["status"] == "success"
    assert "graph LR" in res["mermaid_markup"]
    assert "Doc_A_md -->|Hop 1| Doc_B_md" in res["mermaid_markup"]


def test_vector_cache_guard():
    guard = VectorCacheGuard()
    doc_id = "doc_100"
    text_a = "Initial content"
    text_b = "Modified content"

    # First check populates cache (returns False)
    assert guard.is_cache_valid(doc_id, text_a) is False
    # Second check with same content returns True
    assert guard.is_cache_valid(doc_id, text_a) is True
    # Check with modified content returns False
    assert guard.is_cache_valid(doc_id, text_b) is False


def test_system_scoreboard():
    res = generate_system_scoreboard(root_dir="src/domain")
    assert res["status"] == "success"
    assert res["total_sota_engines"] == 19
    assert "architecture_health_score" in res
    assert res["master_pass_rate_percentage"] == 100.0
