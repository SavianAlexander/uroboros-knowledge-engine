import unittest
"""
Automated Test Suite: L1 Semantic RAG Cache & Cryptographic Audit Hashchain Verification.
Standard: Pure Python Standard Library + pytest + FastAPI TestClient.
"""

import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

from src.domain.semantic_cache import SemanticQueryCache
from src.domain.audit_hashchain import AuditHashchain
from src.infrastructure.database import reset_db_connections, DB_FILE
from src.app.main import app


@pytest.fixture(autouse=True)
def cleanup_connections():
    yield
    reset_db_connections()


class TestSemanticQueryCache(unittest.TestCase):
    """Validate L1 semantic cache put, get, hit count, and invalidation."""

    def test_semantic_cache_put_and_get(self):
        query = "What is Uroboros Knowledge Engine?"
        response = "Uroboros is a zero-dependency high performance knowledge database."
        chunks = [{"id": 1, "text": "Uroboros database"}]

        # Put into cache
        ok = SemanticQueryCache.put(query, response, context_chunks=chunks, domain="GLOBAL")
        assert ok is True

        # Retrieve
        cached = SemanticQueryCache.get(query, domain="GLOBAL")
        assert cached is not None
        assert cached["is_cached"] is True
        assert cached["response_text"] == response
        assert len(cached["context_chunks"]) == 1
        assert cached["hit_count"] >= 1

    def test_semantic_cache_invalidation_and_clear(self):
        query = "Cache test query to invalidate"
        SemanticQueryCache.put(query, "temp response")

        assert SemanticQueryCache.get(query) is not None
        SemanticQueryCache.invalidate(query)
        assert SemanticQueryCache.get(query) is None

        # Test clear
        SemanticQueryCache.put("q1", "r1")
        SemanticQueryCache.put("q2", "r2")
        cleared = SemanticQueryCache.clear()
        assert cleared >= 2

    def test_semantic_cache_stats(self):
        stats = SemanticQueryCache.get_cache_stats()
        assert stats["status"] == "success"
        assert "total_entries" in stats
        assert "total_lifetime_hits" in stats


class TestAuditHashchainCryptographicIntegrity(unittest.TestCase):
    """Validate SHA-256 block hash chaining and tamper detection."""

    def test_record_sealed_audit_event(self):
        res = AuditHashchain.record_sealed_event(
            event_type="SECURITY_LOGIN",
            description="Admin user logged in",
            metadata={"user": "savian", "ip": "127.0.0.1"}
        )
        assert res["status"] == "success"
        assert res["event_id"] > 0
        assert len(res["block_hash"]) == 64
        assert len(res["prev_hash"]) == 64

    def test_verify_chain_integrity(self):
        # Record a second event to ensure multi-block chaining
        AuditHashchain.record_sealed_event(
            event_type="FILE_INGEST",
            description="Ingested document test.pdf",
            metadata={"file": "test.pdf"}
        )

        verification = AuditHashchain.verify_chain_integrity()
        assert verification["status"] == "success"
        assert verification["is_valid"] is True
        assert verification["total_blocks"] >= 2
        assert verification["compliance_tier"] == "SOC2_TYPE_II_VERIFIED"
        assert len(verification["tampered_blocks"]) == 0


class TestAdvancedAPIs(unittest.TestCase):
    """Validate FastAPI endpoints for audit hashchain verification and semantic cache."""

    def test_fastapi_endpoints(self):
        client = TestClient(app)

        # 1. Test /api/system/audit/verify
        audit_resp = client.get("/api/system/audit/verify")
        assert audit_resp.status_code == 200
        audit_data = audit_resp.json()
        assert audit_data["status"] == "success"
        assert "is_valid" in audit_data

        # 2. Test /api/system/cache/semantic
        cache_resp = client.get("/api/system/cache/semantic")
        assert cache_resp.status_code == 200
        cache_data = cache_resp.json()
        assert cache_data["status"] == "success"

        # 3. Test /api/system/cache/semantic/clear
        clear_resp = client.post("/api/system/cache/semantic/clear")
        assert clear_resp.status_code == 200
        clear_data = clear_resp.json()
        assert clear_data["status"] == "success"
