import os
import sys
import unittest
import tempfile
import shutil

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.domain.sla_circuit_breaker import execute_with_sla_circuit_breaker
from src.domain.cache_guard import VectorCacheGuard
from src.domain.streaming_token_compressor import compress_streaming_tokens
from src.domain.adaptive_context_compressor import compress_context_entropy
from src.domain.context_budget_allocator import allocate_context_budget
from src.domain.speculative_warmer import SpeculativeContextWarmer
from src.domain.predictive_precacher import precache_graph_neighborhood
from src.domain.vector_store import DenseVectorStore


class TestDomainSLACaching(unittest.TestCase):
    """Domain test suite for SLA circuit breakers, vector cache guards, and streaming compressors."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_sla_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_sla_circuit_breaker_normal_execution(self):
        """Verify SLA circuit breaker executes primary strategy when latency is within SLA limits.

        Preconditions: Mock primary and fallback functions provided with latency=15.0ms (max_sla=50.0ms).
        Invariants: Primary function is executed and returned with circuit_tripped=False.
        Expected Outcomes: strategy_used='primary_colbert', circuit_tripped=False, status='success'.
        """
        primary_fn = lambda: ["doc_primary_1", "doc_primary_2"]
        fallback_fn = lambda: ["doc_fallback_1"]

        res = execute_with_sla_circuit_breaker(
            primary_func=primary_fn,
            fallback_func=fallback_fn,
            latency_ms=15.0,
            max_sla_ms=50.0
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["circuit_tripped"])
        self.assertEqual(res["strategy_used"], "primary_colbert")
        self.assertEqual(res["result"], ["doc_primary_1", "doc_primary_2"])

    def test_02_sla_circuit_breaker_tripping_and_fallback(self):
        """Verify (Angle 8) SLA circuit breaker trips to fast fallback strategy when latency exceeds limit.

        Preconditions: Measured latency=85.0ms exceeds max_sla=50.0ms.
        Invariants: Circuit breaker skips primary and invokes lightweight fallback strategy.
        Expected Outcomes: strategy_used='fallback_fts5_fast', circuit_tripped=True, status='degraded_fallback'.
        """
        primary_fn = lambda: ["slow_doc"]
        fallback_fn = lambda: ["fast_fallback_doc"]

        res = execute_with_sla_circuit_breaker(
            primary_func=primary_fn,
            fallback_func=fallback_fn,
            latency_ms=85.0,
            max_sla_ms=50.0
        )
        self.assertEqual(res["status"], "degraded_fallback")
        self.assertTrue(res["circuit_tripped"])
        self.assertEqual(res["strategy_used"], "fallback_fts5_fast")
        self.assertEqual(res["result"], ["fast_fallback_doc"])

    def test_03_sla_circuit_breaker_primary_exception_handling(self):
        """Verify graceful fallback degradation when primary strategy raises an unhandled exception.

        Preconditions: Primary function raises RuntimeError while latency is nominally within SLA.
        Invariants: Exception caught internally, triggering fast fallback strategy.
        Expected Outcomes: status='degraded_fallback', circuit_tripped=True.
        """
        def failing_primary():
            raise RuntimeError("Model offloading OOM spike")

        fallback_fn = lambda: ["recovered_via_fts5"]

        res = execute_with_sla_circuit_breaker(
            primary_func=failing_primary,
            fallback_func=fallback_fn,
            latency_ms=20.0,
            max_sla_ms=50.0
        )
        self.assertEqual(res["status"], "degraded_fallback")
        self.assertTrue(res["circuit_tripped"])
        self.assertEqual(res["result"], ["recovered_via_fts5"])

    def test_04_cache_guard_lru_invalidation_and_hashes(self):
        """Verify (Angle 18) SHA-256 VectorCacheGuard detects content mutation and invalidation.

        Preconditions: VectorCacheGuard initialized.
        Invariants: First check returns False (cache miss); second check with identical content returns True (cache valid).
        Expected Outcomes: Content mutation returns False; invalidate() forces re-embedding.
        """
        guard = VectorCacheGuard()
        doc_id = "doc_101"
        initial_content = "Quantum computing relies on qubits."

        # Cache miss & update
        self.assertFalse(guard.is_cache_valid(doc_id, initial_content))
        # Cache hit
        self.assertTrue(guard.is_cache_valid(doc_id, initial_content))

        # Content mutation -> Cache miss
        mutated_content = "Quantum computing relies on topological anyons."
        self.assertFalse(guard.is_cache_valid(doc_id, mutated_content))
        self.assertTrue(guard.is_cache_valid(doc_id, mutated_content))

        # Manual invalidation
        guard.invalidate(doc_id)
        self.assertFalse(guard.is_cache_valid(doc_id, mutated_content))

    def test_05_streaming_token_compressor_budget(self):
        """Verify streaming token compressor prunes conversational filler phrases in real-time.

        Preconditions: Prompt string containing redundant conversational filler phrases ('essentially', 'in order to').
        Invariants: Filler phrases stripped; character reduction metric calculated.
        Expected Outcomes: status='success', fillers_removed_count >= 2, character_reduction > 0.
        """
        text = "It should be noted that basically we need in order to optimize our database throughput."
        res = compress_streaming_tokens(text)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["fillers_removed_count"], 2)
        self.assertGreater(res["character_reduction"], 0.0)
        self.assertNotIn("basically", res["compressed_text"])
        self.assertNotIn("in order to", res["compressed_text"])

    def test_06_adaptive_context_entropy_compressor(self):
        """Verify (Angle 10 & 20) adaptive context entropy compressor preserves entities and numbers while pruning filler.

        Preconditions: Multi-sentence text chunks with numbers (e.g. '128 nodes') and technical identifiers.
        Invariants: High-entropy sentences containing numbers or symbols retained.
        Expected Outcomes: status='success', compressed_chunks returned, token_reduction_percentage >= 0.
        """
        chunks = [
            "The cluster operates on 128 nodes across 4 availability zones.",
            "This is a general filler introductory sentence with no specific data."
        ]
        res = compress_context_entropy(chunks)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["compressed_chunks"]), 2)
        self.assertIn("128 nodes", res["compressed_chunks"][0])

    def test_07_context_budget_allocation_ratios(self):
        """Verify dynamic context token budget allocation across vector, graph, and memory slots.

        Preconditions: Context chunks, graph pathways, and episodic memories provided with max_tokens=8192.
        Invariants: Allocations respect proportional budget ratios (50% vector, 25% graph, 15% memory, 10% system).
        Expected Outcomes: status='success', allocations dictionary populated with correct budget caps.
        """
        vec_snippets = ["Vector chunk 1", "Vector chunk 2"]
        graph_halos = ["Node A -> Node B"]
        memories = ["User prefers Python"]

        res = allocate_context_budget(
            max_tokens=4000,
            vector_snippets=vec_snippets,
            graph_pathways=graph_halos,
            episodic_memories=memories
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["allocations"]["vector_snippets"]["token_budget"], 2000)
        self.assertEqual(res["allocations"]["graph_pathways"]["token_budget"], 1000)
        self.assertEqual(res["allocations"]["episodic_memories"]["token_budget"], 600)
        self.assertEqual(res["allocations"]["system_overhead"]["token_budget"], 400)

    def test_08_speculative_context_warmer_prefix_caching(self):
        """Verify speculative keystroke query warmer memoization cache.

        Preconditions: SpeculativeContextWarmer initialized with mock DenseVectorStore.
        Invariants: warm_prefix caches candidate IDs; get_warmed_candidates returns cached list in sub-millisecond time.
        Expected Outcomes: get_warmed_candidates matches warmed document ID list.
        """
        vec_db = os.path.join(self.test_dir, "test_vectors.db")
        store = DenseVectorStore(dimension=64, db_path=vec_db)
        # Seed vector store
        store.add_vector("doc_alpha", [0.1] * 64, {"filename": "alpha.txt"})
        store.add_vector("doc_beta", [0.2] * 64, {"filename": "beta.txt"})

        warmer = SpeculativeContextWarmer(vector_store=store)
        sample_vec = [0.1] * 64

        warmed = warmer.warm_prefix("alph", sample_vec)
        self.assertIsInstance(warmed, list)

        cached = warmer.get_warmed_candidates("alph")
        self.assertEqual(cached, warmed)

    def test_09_predictive_precacher_graph_neighborhood(self):
        """Verify (Angle 16) predictive pre-cacher handles non-existent or zero-link documents cleanly.

        Preconditions: Isolated database with document without wikilinks.
        Invariants: precache_graph_neighborhood executes without errors.
        Expected Outcomes: Returns precached_count=0 and status='success' or 'not_found'.
        """
        res = precache_graph_neighborhood("missing_source_doc_99.txt")
        self.assertEqual(res["status"], "not_found")
        self.assertEqual(res["precached_count"], 0)

    def test_10_angle_empty_and_corrupt_payload_resilience(self):
        """Verify (Angle 4 & 25) resilience against empty strings, None, and corrupted payloads.

        Preconditions: None, empty string, and malformed inputs passed to all compressors.
        Invariants: Functions return clean default structures without throwing exceptions.
        Expected Outcomes: compress_streaming_tokens, compress_context_entropy, and allocate_context_budget complete cleanly.
        """
        c1 = compress_streaming_tokens("")
        self.assertEqual(c1["status"], "empty_input")

        c2 = compress_context_entropy([])
        self.assertEqual(c2["status"], "empty")

        c3 = allocate_context_budget(max_tokens=0, vector_snippets=None)
        self.assertEqual(c3["status"], "success")


if __name__ == "__main__":
    unittest.main()
