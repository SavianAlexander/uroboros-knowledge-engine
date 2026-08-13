"""
Domain unit test suite for Advanced Engine features:
1. Semantic Query Caching & Cosine Similarity Invariants
2. Graph RAG Vector Semantic Edges
3. File Watcher Daemon Status & Toggle Endpoints
4. OCR Spatial Bounding Box Visualizer Coordinates
5. Micro-Benchmark Execution Validation
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

from main import app
from src.core.state import cosine_similarity, QueryCache
from src.infrastructure.database import get_db, reset_db_connections, init_db
from scripts.benchmark_engine import benchmark_cosine_similarity, benchmark_semantic_query_cache


class TestAdvancedFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        init_db()

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()

    def test_01_cosine_similarity_edge_cases(self):
        """Verify standard library cosine similarity edge cases and mathematical precision."""
        self.assertEqual(cosine_similarity([], []), 0.0)
        self.assertEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]), 1.0, places=5)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [2.0, 0.0]), 1.0, places=5)

    def test_02_semantic_query_cache(self):
        """Verify exact and semantic vector cache retrieval."""
        cache = QueryCache(capacity=10)
        vec_base = [1.0, 0.0, 0.0, 0.5]
        cache.set_semantic("quantum mechanics", {"data": "physics"}, query_embedding=vec_base)

        # Exact hit
        res_exact, sim_exact = cache.get_semantic("quantum mechanics")
        self.assertEqual(res_exact, {"data": "physics"})
        self.assertEqual(sim_exact, 1.0)

        # Semantic hit with close vector
        vec_close = [0.99, 0.01, 0.0, 0.49]
        res_sem, sim_sem = cache.get_semantic("quantum principles", query_embedding=vec_close, threshold=0.90)
        self.assertEqual(res_sem, {"data": "physics"})
        self.assertGreaterEqual(sim_sem, 0.90)

        # Miss with distant vector
        vec_far = [0.0, 1.0, 1.0, 0.0]
        res_miss, sim_miss = cache.get_semantic("astronomy", query_embedding=vec_far, threshold=0.90)
        self.assertIsNone(res_miss)
        self.assertLess(sim_miss, 0.90)

    def test_03_file_watcher_endpoints(self):
        """Verify watcher status, start, and stop HTTP endpoints."""
        res_status = self.client.get("/api/watcher/status")
        self.assertEqual(res_status.status_code, 200)
        self.assertIn("active", res_status.json())

        res_start = self.client.post("/api/watcher/start")
        self.assertEqual(res_start.status_code, 200)
        self.assertEqual(res_start.json()["status"], "started")

        res_stop = self.client.post("/api/watcher/stop")
        self.assertEqual(res_stop.status_code, 200)
        self.assertEqual(res_stop.json()["status"], "stopped")

    def test_04_ocr_coords_endpoint(self):
        """Verify OCR spatial bounding box coordinate retrieval and filtering."""
        from src.core.config import ACTIVE_DIR
        test_file = os.path.join(ACTIVE_DIR, "test_ocr.pdf")
        with get_db() as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO files (id, filepath, filename) VALUES (9999, ?, 'test_ocr.pdf')", (test_file,))
                cursor.execute("DELETE FROM ocr_coords WHERE file_id = 9999")
                cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES (9999, 'architecture', 10, 20, 50, 15)")
                cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES (9999, 'pipeline', 65, 20, 40, 15)")

        # Query all coords
        res = self.client.get(f"/api/file/ocr-coords?path={test_file}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["words_count"], 2)
        self.assertEqual(len(data["coords"]), 2)

        # Filter by term
        res_filter = self.client.get(f"/api/file/ocr-coords?path={test_file}&term=arch")
        self.assertEqual(res_filter.status_code, 200)
        data_filter = res_filter.json()
        self.assertEqual(data_filter["words_count"], 1)
        self.assertEqual(data_filter["coords"][0]["word"], "architecture")

    def test_05_micro_benchmark_execution(self):
        """Verify micro-benchmark runner functions execute deterministically."""
        res_cos = benchmark_cosine_similarity(iterations=100)
        self.assertIn("ops_per_second", res_cos)
        self.assertGreater(res_cos["ops_per_second"], 0)

        res_cache = benchmark_semantic_query_cache(iterations=100)
        self.assertIn("exact_hit_ops_sec", res_cache)
        self.assertGreater(res_cache["exact_hit_ops_sec"], 0)

    def test_06_p2p_mesh_hashes_and_delta(self):
        """Verify P2P document hashing and delta synchronization."""
        res_hashes = self.client.get("/api/sync/hashes")
        self.assertEqual(res_hashes.status_code, 200)
        self.assertIn("hashes", res_hashes.json())

        res_delta = self.client.post("/api/sync/delta", json={"filenames": ["test_ocr.pdf"]})
        self.assertEqual(res_delta.status_code, 200)
        self.assertIn("files", res_delta.json())

    def test_07_pii_redaction_credit_card_and_keys(self):
        """Verify deterministic PII token redaction (SSN, CC, API Keys, Emails)."""
        from src.domain.pii_privacy_guard import redact_pii_from_text
        sample = "Contact agent at user@example.com, SSN 123-45-6789, CC 4111 2222 3333 4444, key sk_live_1234567890abcdef"
        res = redact_pii_from_text(sample)
        self.assertEqual(res["status"], "success")
        self.assertNotIn("user@example.com", res["redacted_text"])
        self.assertNotIn("123-45-6789", res["redacted_text"])
        self.assertNotIn("4111 2222 3333 4444", res["redacted_text"])
        self.assertNotIn("sk_live_1234567890abcdef", res["redacted_text"])
        self.assertGreaterEqual(res["total_redactions"], 4)

    def test_08_multihop_and_hyde_synthesis(self):
        """Verify HyDE contextual synthesis and multi-hop traversal."""
        from src.domain.contextual_hyde import generate_hypothetical_document
        from src.domain.graph_multihop import find_multihop_pathways
        hyde_res = generate_hypothetical_document("quantum computing algorithms")
        self.assertEqual(hyde_res["status"], "success")
        self.assertIn("hypothetical_text", hyde_res)

        path_res = find_multihop_pathways("test_ocr.pdf")
        self.assertIn("status", path_res)

    def test_09_vault_integrity_and_self_healing(self):
        """Verify vault integrity auditor and autonomous repair endpoints."""
        res_integ = self.client.get("/api/vault/integrity")
        self.assertEqual(res_integ.status_code, 200)
        self.assertIn("health_score", res_integ.json())

        res_heal = self.client.post("/api/vault/self-heal")
        self.assertEqual(res_heal.status_code, 200)
        self.assertEqual(res_heal.json()["status"], "success")


if __name__ == "__main__":
    unittest.main()
