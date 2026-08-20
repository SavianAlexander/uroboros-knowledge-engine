"""
Self-check unit test suite for Phase V SOTA Knowledge Engine features:
1. Knowledge Graph Entity Disambiguation & Alias Resolver
2. Dynamic RAG Prompt Density Optimizer
3. SOC 2 & HIPAA Privacy Compliance Inspector
"""

import pytest
from src.domain.entity_resolver import resolve_canonical_entity, batch_resolve_entities
from src.domain.prompt_optimizer import optimize_rag_prompt_density
from src.domain.compliance_inspector import inspect_privacy_compliance


import unittest


class TestEntityResolutionPromptOptimizationCompliance(unittest.TestCase):
    def test_entity_resolver(self):
        assert resolve_canonical_entity("postgres") == "PostgreSQL"
        assert resolve_canonical_entity("py") == "Python"

        batch_res = batch_resolve_entities(["postgres", "PostgreSQL", "py", "Python"])
        assert batch_res["status"] == "success"
        assert batch_res["total_canonical_entities"] == 2


    def test_prompt_optimizer(self):
        chunks = [
            "Database architecture using SQLite WAL mode and FTS5 indexing.",
            "Unrelated document about baking chocolate cookies."
        ]
        res = optimize_rag_prompt_density("database architecture", chunks, token_budget=100)
        assert res["status"] == "success"
        assert res["selected_chunk_count"] > 0
        assert "SQLite" in res["optimized_prompt"]


    def test_compliance_inspector(self):
        sample_text = "Contact user at admin@example.com with key sk_123456789012345678901234."
        res = inspect_privacy_compliance(sample_text)
        assert res["status"] == "privacy_risk"
        assert res["total_violations"] >= 1
        assert "[REDACTED_EMAIL]" in res["masked_text"]
