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

    def test_10_adaptive_rrf_scoring(self):
        """Verify Adaptive RRF auto-tuning calculation across short and long queries."""
        from src.domain.sota_rag_engine import execute_sota_rag_search
        short_res = execute_sota_rag_search("quantum")
        self.assertEqual(short_res["status"], "success")
        self.assertIn("top_candidates", short_res)

        long_res = execute_sota_rag_search("what are the latest advancements in quantum error correction and topology")
        self.assertEqual(long_res["status"], "success")
        self.assertIn("top_candidates", long_res)

    def test_11_revision_diff_visualizer(self):
        """Verify Myers diff computation endpoint /api/file/diff."""
        res = self.client.get("/api/file/diff", params={"path": "dumps/notes.txt"})
        self.assertIn(res.status_code, [200, 404])
        if res.status_code == 200:
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertIn("similarity_ratio", data)
            self.assertIn("unified_diff", data)

    def test_12_graph_community_summarizer(self):
        """Verify /api/graph/clusters/summaries auto-topical synthesis."""
        res = self.client.get("/api/graph/clusters/summaries")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("communities", data)

    def test_13_live_apm_telemetry(self):
        """Verify live APM telemetry endpoint /api/system/live-telemetry."""
        res = self.client.get("/api/system/live-telemetry")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("runtime", data)
        self.assertIn("database", data)

    def test_14_hot_index_validator(self):
        """Verify B-Tree index validation and hot repair endpoint."""
        res = self.client.post("/api/vault/indexes/repair")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total_required"], 5)

    def test_15_intent_classification_router(self):
        """Verify deterministic syntactic query intent classification."""
        from src.domain.query_intent_classifier import classify_query_intent
        res_compare = classify_query_intent("compare redis vs sqlite")
        self.assertEqual(res_compare["intent"], "comparative_analysis")
        self.assertEqual(res_compare["recommended_pipeline"], "multi_query_decomposition")

        res_path = classify_query_intent("relationship between machine learning and optimization")
        self.assertEqual(res_path["intent"], "exploratory_pathfinding")
        self.assertEqual(res_path["recommended_pipeline"], "graph_multihop_traversal")

    def test_16_vault_duplicate_chunks(self):
        """Verify vault-wide duplicate chunk consolidation endpoint."""
        res = self.client.get("/api/vault/duplicate-chunks")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("duplicate_clusters", data)

    def test_17_fuzzy_scored_tag_suggestions(self):
        """Verify confidence-scored tag suggestions endpoint /api/tags/suggestions."""
        sample_text = "Quantum computing and quantum superposition algorithms for quantum cryptography."
        res = self.client.get("/api/tags/suggestions", params={"text": sample_text})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("scored_suggestions", data)

    def test_18_vault_export_manifest_and_package(self):
        """Verify vault export manifest metadata and package generator."""
        res_manifest = self.client.get("/api/vault/export/manifest")
        self.assertEqual(res_manifest.status_code, 200)
        manifest_data = res_manifest.json()
        self.assertEqual(manifest_data["status"], "success")
        self.assertIn("manifest", manifest_data)

        res_pkg = self.client.get("/api/vault/export/package")
        self.assertEqual(res_pkg.status_code, 200)
        self.assertEqual(res_pkg.headers.get("content-type"), "application/zip")

    def test_19_system_memory_and_db_compactor(self):
        """Verify runtime memory compaction and SQLite page cache shrinker."""
        res = self.client.post("/api/system/compact")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("reclaimed_gc_objects", data)

    def test_20_agent_memory_crud_endpoints(self):
        """Verify persistent agent memory store, recall, listing, and deletion."""
        # 1. Store
        res_post = self.client.post("/api/memory", json={"key": "user_theme", "value": "dark", "category": "ui_pref"})
        self.assertEqual(res_post.status_code, 200)

        # 2. List
        res_list = self.client.get("/api/memory", params={"category": "ui_pref"})
        self.assertEqual(res_list.status_code, 200)
        memories = res_list.json().get("memories", [])
        self.assertTrue(any(m["key"] == "user_theme" for m in memories))

        # 3. Direct recall verification
        from src.domain.agent_memory import recall
        self.assertEqual(recall("user_theme"), "dark")

        # 4. Delete
        res_del = self.client.delete("/api/memory/user_theme")
        self.assertEqual(res_del.status_code, 200)
        self.assertIsNone(recall("user_theme"))

    def test_21_p2p_socket_and_rule_regex_guard(self):
        """Verify invalid regex rules cleanly return 400 without unhandled server crashes."""
        res_bad_regex = self.client.post("/api/rules", json={"pattern": "[a-z", "tag": "broken"})
        self.assertEqual(res_bad_regex.status_code, 400)
        self.assertIn("Invalid regex pattern", res_bad_regex.json().get("detail", ""))

    def test_22_sse_streaming_rag(self):
        """Verify SSE progressive streaming RAG endpoint /api/stream/rag."""
        res = self.client.get("/api/stream/rag", params={"q": "architecture guidelines"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "text/event-stream; charset=utf-8")
        body = res.text
        self.assertIn("event: intent_classified", body)
        self.assertIn("event: query_decomposed", body)
        self.assertIn("event: done", body)

    def test_23_temporal_timeline(self):
        """Verify chronological knowledge timeline generator /api/vault/timeline."""
        res = self.client.get("/api/vault/timeline")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("timeline", data)

    def test_24_conversational_query_reformulator(self):
        """Verify multi-turn query reformulation and antecedent injection."""
        history = [
            {"user": "Explain SQLite WAL mode locking", "assistant": "SQLite WAL mode uses shared memory for concurrency."}
        ]
        res = self.client.post("/api/chat/reformulate", json={"history": history, "query": "Why does it prevent blocking?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["has_pronouns"])
        self.assertIn("SQLite", data["reformulated_query"])

    def test_25_code_ast_callgraph_complexity(self):
        """Verify zero-dependency code AST call graph and cyclomatic complexity."""
        sample_code = """
import os

class DatabaseWorker:
    def execute_query(self, query: str):
        if not query:
            return None
        for i in range(3):
            print(query)
        return True
"""
        res = self.client.post("/api/code/analyze", json={"code": sample_code, "filename": "worker.py"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["language"], "python")
        self.assertEqual(len(data["classes"]), 1)
        self.assertEqual(data["classes"][0]["name"], "DatabaseWorker")
        self.assertGreaterEqual(data["cyclomatic_complexity"], 3)

    def test_26_vault_merkle_tree_attestation(self):
        """Verify deterministic binary Merkle Tree root and cryptographic audit inclusion proof."""
        res_root = self.client.get("/api/vault/merkle-root")
        self.assertEqual(res_root.status_code, 200)
        root_data = res_root.json()
        self.assertEqual(root_data["status"], "success")
        self.assertIn("merkle_root", root_data)
        self.assertGreater(len(root_data["merkle_root"]), 10)

        # Proof generation for top file if leaves exist
        leaves = root_data.get("leaves", [])
        if leaves:
            sample_target = leaves[0]["filename"]
            res_proof = self.client.get("/api/vault/merkle-proof", params={"filename": sample_target})
            self.assertEqual(res_proof.status_code, 200)
            proof_data = res_proof.json()
            self.assertEqual(proof_data["status"], "success")
            self.assertIn("audit_proof", proof_data)

            # Mathematical verification
            from src.domain.vault_merkle_tree import verify_merkle_proof
            valid = verify_merkle_proof(proof_data["leaf_hash"], proof_data["audit_proof"], root_data["merkle_root"])
            self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
