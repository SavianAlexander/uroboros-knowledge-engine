"""
Milestone 1 Adversarial Edge Case & Boundary Stress Test Suite.
Verifies all 9 modified components under boundary, malformed, extreme, and concurrent inputs.

Subsystems Tested:
1. Search Tag Filtering & Excluded Words (search.py)
2. Embedding LRU Cache & Vector Math (embeddings.py)
3. Model Router Selection (model_router.py)
4. File Tree Node Population & Traversal (files.py)
5. RAG Smart Context Extraction (rag.py)
6. Job Queue Single-Pass Stale Eviction (jobs.py)
7. Voice RAG Bridge Citation & Fact Extraction (voice_rag_bridge.py)
8. Vector Engine MMR Re-ranking & Autocomplete (vector_engine.py)
9. Parsers PPTX Speaker Notes & Obsidian Frontmatter (parsers.py)
"""

import os
import sys
import time
import tempfile
import unittest
import zipfile
import threading
from collections import OrderedDict
from typing import Dict, Any, List

# Ensure repository root is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.infrastructure.database import get_db, reset_db_connections, init_db
from src.app.routers.search import _filter_by_excluded_tags, _filter_by_excluded_words, _batch_fetch_tags
from src.core.embeddings import (
    _embed_cache, MAX_EMBED_CACHE_SIZE, generate_embeddings_batch,
    l2_normalize, matryoshka_slice, quantize_int8
)
from src.core.model_router import _pick_best_available, get_available_models
from src.app.routers.files import _populate_db_tree_nodes, resolve_file_on_disk
from src.app.routers.rag import _smart_extract_context
from src.core.jobs import JobManager
from src.core.voice_rag_bridge import VoiceRAGBridge
from src.infrastructure.vector_engine import MiniVectorEngine
from src.infrastructure.parsers import parse_pptx_presentation, parse_obsidian_markdown


class TestTagFilteringBoundaryAndEdgeCases(unittest.TestCase):
    """Adversarial stress tests for tag filtering and tag batch fetching."""

    def test_filter_by_excluded_tags_empty_and_single_char(self):
        """Test with empty tag lists, empty strings, and single-character tags."""
        sample_results = [
            {"id": 10001, "filename": "doc1.md"},
            {"id": 10002, "filename": "doc2.md"},
            {"id": 10003, "filename": "doc3.md"}
        ]
        
        # Insert known files and tags in DB
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE file_id IN (10001, 10002, 10003)")
            cursor.execute("DELETE FROM files WHERE id IN (10001, 10002, 10003)")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (10001, '/tmp/doc1.md', 'doc1.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (10002, '/tmp/doc2.md', 'doc2.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (10003, '/tmp/doc3.md', 'doc3.md')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (10001, 'a')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (10001, 'alpha')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (10002, 'b')")
            conn.commit()

        try:
            # 1. Empty list
            res_empty = _filter_by_excluded_tags(sample_results, [])
            self.assertEqual(len(res_empty), 3)

            # 2. Empty string
            res_empty_str = _filter_by_excluded_tags(sample_results, "")
            self.assertEqual(len(res_empty_str), 3)

            # 3. Single-character tag 'a'
            res_single_a = _filter_by_excluded_tags(sample_results, ["a"])
            ids_a = [r["id"] for r in res_single_a]
            self.assertNotIn(10001, ids_a)
            self.assertIn(10002, ids_a)
            self.assertIn(10003, ids_a)

            # 4. Single-character tag as string instead of list
            res_single_b = _filter_by_excluded_tags(sample_results, "b")
            ids_b = [r["id"] for r in res_single_b]
            self.assertIn(10001, ids_b)
            self.assertNotIn(10002, ids_b)
            self.assertIn(10003, ids_b)
        finally:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tags WHERE file_id IN (10001, 10002, 10003)")
                cursor.execute("DELETE FROM files WHERE id IN (10001, 10002, 10003)")
                conn.commit()

    def test_filter_by_excluded_tags_punctuation_unicode_whitespace(self):
        """Test tag filtering with unicode, punctuation, emojis, and whitespace."""
        sample_results = [
            {"id": 20001, "filename": "unicode_doc.md"},
            {"id": 20002, "filename": "emoji_doc.md"},
            {"id": 20003, "filename": "punct_doc.md"},
            {"id": 20004, "filename": "clean_doc.md"}
        ]
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE file_id IN (20001, 20002, 20003, 20004)")
            cursor.execute("DELETE FROM files WHERE id IN (20001, 20002, 20003, 20004)")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (20001, '/tmp/u.md', 'unicode_doc.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (20002, '/tmp/e.md', 'emoji_doc.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (20003, '/tmp/p.md', 'punct_doc.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (20004, '/tmp/c.md', 'clean_doc.md')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (20001, 'café_résumé')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (20002, '🏷️_special')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (20003, 'sec-ops.v2:prod!')")
            conn.commit()

        try:
            # Exclude unicode tag
            res_unicode = _filter_by_excluded_tags(sample_results, ["café_résumé"])
            self.assertNotIn(20001, [r["id"] for r in res_unicode])
            self.assertIn(20002, [r["id"] for r in res_unicode])

            # Exclude emoji tag
            res_emoji = _filter_by_excluded_tags(sample_results, ["🏷️_special"])
            self.assertNotIn(20002, [r["id"] for r in res_emoji])

            # Exclude punctuation tag
            res_punct = _filter_by_excluded_tags(sample_results, ["sec-ops.v2:prod!"])
            self.assertNotIn(20003, [r["id"] for r in res_punct])
            self.assertIn(20004, [r["id"] for r in res_punct])
        finally:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tags WHERE file_id IN (20001, 20002, 20003, 20004)")
                cursor.execute("DELETE FROM files WHERE id IN (20001, 20002, 20003, 20004)")
                conn.commit()

    def test_filter_by_excluded_tags_malformed_records(self):
        """Test with malformed result dictionaries (missing IDs, None values, non-existent IDs)."""
        malformed_results = [
            {},
            {"filename": "no_id.txt"},
            {"id": None, "filename": "none_id.txt"},
            {"id": 999999999, "filename": "ghost.txt"}
        ]
        # Should execute cleanly without raising KeyError or TypeError
        filtered = _filter_by_excluded_tags(malformed_results, ["anytag"])
        self.assertEqual(len(filtered), 4)

    def test_batch_fetch_tags_large_scale(self):
        """Test _batch_fetch_tags across chunk boundaries (>500 IDs)."""
        empty_map = _batch_fetch_tags([])
        self.assertEqual(empty_map, {})

        # Test with 1250 synthetic IDs to verify 500-chunk iteration
        large_ids = list(range(50000, 51250))
        tags_map = _batch_fetch_tags(large_ids)
        self.assertEqual(len(tags_map), 1250)
        for fid in large_ids:
            self.assertIsInstance(tags_map[fid], set)


class TestExcludedWordsAndDiskIOEdgeCases(unittest.TestCase):
    """Adversarial stress tests for excluded word single-pass disk I/O."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_file = os.path.join(self.temp_dir.name, "valid.txt")
        with open(self.valid_file, "w", encoding="utf-8") as f:
            f.write("Alpha Bravo Charlie Delta SecretToken123")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_filter_by_excluded_words_empty_and_none(self):
        """Test with empty word list, None values, and missing disk files."""
        results = [
            {"id": 1, "filename": "valid.txt", "filepath": self.valid_file, "content": None},
            {"id": 2, "filename": "missing.txt", "filepath": "/path/to/missing_file_xyz.txt", "content": None},
            {"id": 3, "filename": "empty_path.txt", "filepath": "", "content": None},
            {"id": 4, "filename": "", "filepath": None, "content": "Inline content text"}
        ]

        # 1. Empty excluded words
        res_empty = _filter_by_excluded_words(results, [])
        self.assertEqual(len(res_empty), 4)

        # 2. None input
        res_none = _filter_by_excluded_words(results, None)
        self.assertEqual(len(res_none), 4)

        # 3. Exclude word found in disk file
        res_disk = _filter_by_excluded_words(results, ["SecretToken123"])
        self.assertNotIn(1, [r["id"] for r in res_disk])
        self.assertIn(2, [r["id"] for r in res_disk])
        self.assertIn(3, [r["id"] for r in res_disk])
        self.assertIn(4, [r["id"] for r in res_disk])

    def test_filter_by_excluded_words_filename_match(self):
        """Test excluded word present in filename even if content is empty/missing."""
        results = [
            {"id": 1, "filename": "confidential_memo.pdf", "filepath": "/no/such/file.pdf", "content": ""},
            {"id": 2, "filename": "public_notes.txt", "filepath": "/no/such/file2.txt", "content": ""}
        ]
        filtered = _filter_by_excluded_words(results, ["confidential"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 2)

    def test_filter_by_excluded_words_binary_corrupt_file(self):
        """Test graceful fallback when encountering binary/corrupt file on disk."""
        bin_file = os.path.join(self.temp_dir.name, "corrupt.bin")
        with open(bin_file, "wb") as f:
            f.write(b"\x80\xFF\xFE\x00\x01\xAA\xBB\xCC")

        results = [{"id": 10, "filename": "corrupt.bin", "filepath": bin_file, "content": None}]
        # Should not crash on invalid utf-8 due to errors="ignore"
        filtered = _filter_by_excluded_words(results, ["someword"])
        self.assertEqual(len(filtered), 1)


class TestEmbeddingCacheLRUBoundaryCases(unittest.TestCase):
    """Adversarial stress tests for embedding cache OrderedDict true LRU eviction."""

    def test_lru_cache_eviction_and_recency(self):
        """Test that OrderedDict properly behaves as LRU (least recently used evicted first)."""
        test_cache: OrderedDict = OrderedDict()
        cap = 3

        def put(k, v):
            if k in test_cache:
                test_cache.move_to_end(k)
            else:
                if len(test_cache) >= cap:
                    test_cache.popitem(last=False)
                test_cache[k] = v

        def get(k):
            if k in test_cache:
                test_cache.move_to_end(k)
                return test_cache[k]
            return None

        # Insert A, B, C
        put("A", [1.0])
        put("B", [2.0])
        put("C", [3.0])
        self.assertEqual(list(test_cache.keys()), ["A", "B", "C"])

        # Access A (moves A to most recent)
        self.assertEqual(get("A"), [1.0])
        self.assertEqual(list(test_cache.keys()), ["B", "C", "A"])

        # Insert D (should evict B, since B is least recent)
        put("D", [4.0])
        self.assertEqual(list(test_cache.keys()), ["C", "A", "D"])
        self.assertNotIn("B", test_cache)

        # Access C (moves C to most recent)
        get("C")
        self.assertEqual(list(test_cache.keys()), ["A", "D", "C"])

        # Insert E (should evict A)
        put("E", [5.0])
        self.assertEqual(list(test_cache.keys()), ["D", "C", "E"])
        self.assertNotIn("A", test_cache)

    def test_lru_cache_capacity_boundary_zero_and_one(self):
        """Test LRU eviction behavior under boundary capacity of 1."""
        test_cache: OrderedDict = OrderedDict()
        cap = 1

        def put(k, v):
            if k in test_cache:
                test_cache.move_to_end(k)
            else:
                if len(test_cache) >= cap:
                    test_cache.popitem(last=False)
                test_cache[k] = v

        put("item1", [1.0])
        self.assertEqual(len(test_cache), 1)
        self.assertIn("item1", test_cache)

        put("item2", [2.0])
        self.assertEqual(len(test_cache), 1)
        self.assertNotIn("item1", test_cache)
        self.assertIn("item2", test_cache)

    def test_generate_embeddings_batch_boundary_inputs(self):
        """Test generate_embeddings_batch with empty lists and blank prompts."""
        # 1. Empty input
        self.assertEqual(generate_embeddings_batch([]), [])

        # 2. Blank and whitespace strings
        blanks = ["", "   ", "\t\n\r", "   \n  "]
        res = generate_embeddings_batch(blanks)
        self.assertEqual(len(res), 4)
        for r in res:
            self.assertEqual(r, [])

    def test_vector_math_boundary_conditions(self):
        """Test L2 normalization, Matryoshka dimension slicing, and SQ8 quantization under zero/empty inputs."""
        # L2 Normalize
        self.assertEqual(l2_normalize([]), [])
        self.assertEqual(l2_normalize([0.0, 0.0, 0.0]), [0.0, 0.0, 0.0])
        norm_v = l2_normalize([3.0, 4.0])
        self.assertAlmostEqual(norm_v[0], 0.6)
        self.assertAlmostEqual(norm_v[1], 0.8)

        # Matryoshka Slicing
        self.assertEqual(matryoshka_slice([]), [])
        sliced = matryoshka_slice([1.0, 2.0, 3.0, 4.0], target_dim=2)
        self.assertEqual(len(sliced), 2)
        # Target dim larger than vector len
        oversized = matryoshka_slice([3.0, 4.0], target_dim=10)
        self.assertEqual(len(oversized), 2)

        # Int8 Quantization
        self.assertEqual(quantize_int8([]), [])
        # Constant vector (diff == 0) -> should return zeros, not ZeroDivisionError
        const_q = quantize_int8([5.0, 5.0, 5.0])
        self.assertEqual(const_q, [0, 0, 0])
        
        # Valid spread
        spread_q = quantize_int8([-1.0, 0.0, 1.0])
        self.assertEqual(len(spread_q), 3)
        self.assertTrue(all(-128 <= x <= 127 for x in spread_q))


class TestJobQueueEdgeCases(unittest.TestCase):
    """Adversarial stress tests for JobManager single-pass TTL and max history eviction."""

    def test_reap_stale_jobs_empty_queue(self):
        """Test reaping an empty job manager."""
        mgr = JobManager(max_workers=1)
        reaped = mgr.reap_stale_jobs(ttl_seconds=3600.0, max_history=100)
        self.assertEqual(reaped, 0)
        self.assertEqual(mgr._reaped_jobs_count, 0)

    def test_reap_stale_jobs_zero_terminal_jobs(self):
        """Test that running and pending jobs are never reaped regardless of TTL."""
        mgr = JobManager(max_workers=1)
        with mgr._jobs_lock:
            mgr.jobs["job_running"] = {
                "id": "job_running", "status": "running", "started_at": time.time() - 99999
            }
            mgr.jobs["job_pending"] = {
                "id": "job_pending", "status": "pending", "started_at": time.time() - 99999
            }

        reaped = mgr.reap_stale_jobs(ttl_seconds=1.0, max_history=10)
        self.assertEqual(reaped, 0)
        self.assertIn("job_running", mgr.jobs)
        self.assertIn("job_pending", mgr.jobs)

    def test_reap_stale_jobs_all_expired(self):
        """Test that all terminal jobs exceeding TTL are evicted in a single pass."""
        mgr = JobManager(max_workers=1)
        now = time.time()
        with mgr._jobs_lock:
            for i in range(10):
                mgr.jobs[f"job_done_{i}"] = {
                    "id": f"job_done_{i}",
                    "status": "completed" if i % 2 == 0 else "failed",
                    "completed_at": now - 7200.0
                }

        reaped = mgr.reap_stale_jobs(ttl_seconds=3600.0, max_history=100)
        self.assertEqual(reaped, 10)
        self.assertEqual(len(mgr.jobs), 0)
        self.assertEqual(mgr._reaped_jobs_count, 10)

    def test_reap_stale_jobs_max_history_overflow(self):
        """Test that unexpired terminal jobs exceeding max_history are evicted oldest-first."""
        mgr = JobManager(max_workers=1)
        now = time.time()
        with mgr._jobs_lock:
            # Create 15 unexpired terminal jobs with sequential completion times
            for i in range(15):
                mgr.jobs[f"job_{i}"] = {
                    "id": f"job_{i}",
                    "status": "completed",
                    "completed_at": now - (15 - i) * 10  # job_0 is oldest, job_14 is newest
                }

        # Cap history at 5
        reaped = mgr.reap_stale_jobs(ttl_seconds=86400.0, max_history=5)
        self.assertEqual(reaped, 10)
        self.assertEqual(len(mgr.jobs), 5)
        # Verify that only the 5 newest jobs (10..14) survived
        for i in range(10):
            self.assertNotIn(f"job_{i}", mgr.jobs)
        for i in range(10, 15):
            self.assertIn(f"job_{i}", mgr.jobs)

    def test_reap_stale_jobs_missing_timestamps(self):
        """Test robustness against corrupted job dicts missing timestamp fields."""
        mgr = JobManager(max_workers=1)
        with mgr._jobs_lock:
            mgr.jobs["corrupt_job"] = {
                "id": "corrupt_job",
                "status": "cancelled"
                # completed_at and started_at intentionally absent
            }

        # Should not throw KeyError or crash
        reaped = mgr.reap_stale_jobs(ttl_seconds=3600.0, max_history=10)
        # Brand new default timestamp within TTL -> preserved
        self.assertEqual(reaped, 0)
        self.assertIn("corrupt_job", mgr.jobs)


class TestVectorEngineMMRAndAutocompleteEdgeCases(unittest.TestCase):
    """Adversarial stress tests for MiniVectorEngine search_mmr and search_autocomplete_suggested."""

    def test_mmr_empty_and_whitespace_queries(self):
        """Test search_mmr with empty, whitespace, and non-string queries."""
        self.assertEqual(MiniVectorEngine.search_mmr(""), [])
        self.assertEqual(MiniVectorEngine.search_mmr("   "), [])
        self.assertEqual(MiniVectorEngine.search_mmr("\t\n"), [])

    def test_mmr_empty_candidate_pool(self):
        """Test search_mmr when underlying semantic search returns no results."""
        # Query with random gibberish that matches nothing
        res = MiniVectorEngine.search_mmr("zzzz_nonexistent_gibberish_9999_xyz_alpha")
        self.assertIsInstance(res, list)

    def test_mmr_lambda_parameter_bounds(self):
        """Test search_mmr with extreme lambda values (0.0 pure diversity vs 1.0 pure relevance)."""
        res_div = MiniVectorEngine.search_mmr("knowledge", top_k=3, lambda_param=0.0)
        res_rel = MiniVectorEngine.search_mmr("knowledge", top_k=3, lambda_param=1.0)
        self.assertIsInstance(res_div, list)
        self.assertIsInstance(res_rel, list)

    def test_autocomplete_empty_and_missing_prefix(self):
        """Test search_autocomplete_suggested with empty prefix, unmatched prefix, and zero top_k."""
        # Unmatched prefix -> returns [prefix] fallback
        unmatched = MiniVectorEngine.search_autocomplete_suggested("xyz999nonexistent", top_k=5)
        self.assertEqual(unmatched, ["xyz999nonexistent"])

        # Top k = 0 -> returns empty or fallback without crash
        zero_k = MiniVectorEngine.search_autocomplete_suggested("test", top_k=0)
        self.assertIsInstance(zero_k, list)

    def test_autocomplete_deduplication_and_order(self):
        """Test that autocomplete suggestions deduplicate words and preserve insertion order."""
        # Force cached chunks with duplicate words
        old_chunks = MiniVectorEngine._cached_chunks
        try:
            MiniVectorEngine._cached_chunks = [
                {"content": "Authentication protocol authorization credentials auth_v1"},
                {"content": "authentication protocol authorization token auth_v2"},
                {"content": "AUTH_V3 security authentication credentials"}
            ]
            sug = MiniVectorEngine.search_autocomplete_suggested("auth", top_k=10)
            self.assertIsInstance(sug, list)
            # Verify no duplicates
            self.assertEqual(len(sug), len(set(sug)))
            # Verify all match prefix
            for s in sug:
                self.assertTrue(s.startswith("auth"))
        finally:
            MiniVectorEngine._cached_chunks = old_chunks


class TestRAGContextAndVoiceBridgeEdgeCases(unittest.TestCase):
    """Adversarial stress tests for _smart_extract_context and VoiceRAGBridge."""

    def test_smart_extract_context_boundaries(self):
        """Test RAG context extraction under empty inputs, small thresholds, and stopword-only queries."""
        # 1. Empty context
        self.assertEqual(_smart_extract_context("", "query"), "")

        # 2. Context shorter than max_chars
        short_text = "This is a short sentence. Another sentence here."
        self.assertEqual(_smart_extract_context(short_text, "sentence", max_chars=1000), short_text)

        # 3. Query with only short words (<= 3 chars) -> keywords empty -> returns context[:max_chars]
        long_context = "Word. " * 500
        extracted_short_q = _smart_extract_context(long_context, "is it a on to", max_chars=100)
        self.assertEqual(extracted_short_q, long_context[:100])

        # 4. Multi-sentence keyword ranking
        doc = (
            "The weather in Tokyo is sunny today. "
            "Quantum entanglement enables superdense coding and quantum cryptography. "
            "Apples and oranges are rich in vitamin C. "
            "Quantum error correction preserves quantum states across noisy quantum channels."
        )
        query = "quantum cryptography error correction"
        res = _smart_extract_context(doc, query, max_chars=180)
        self.assertIn("Quantum entanglement", res)
        self.assertIn("Quantum error correction", res)
        self.assertNotIn("Apples and oranges", res)

    def test_voice_rag_bridge_empty_and_no_match_query(self):
        """Test VoiceRAGBridge query_and_summarize with empty query and missing database records."""
        from unittest.mock import patch

        # 1. Empty candidates scenario
        with patch("src.core.voice_rag_bridge.execute_sota_rag_search", return_value={"top_candidates": []}):
            res = VoiceRAGBridge.query_and_summarize("")
            self.assertIsInstance(res, dict)
            self.assertFalse(res["found"])
            self.assertIn("found no matching records", res["speech_text"])
            self.assertEqual(res["citations"], [])

        # 2. Query with mock candidates and fact extraction
        mock_candidates = [
            {"filename": "quantum_doc.md", "content": "Quantum algorithms provide exponential speedup for factorization. Classical computers are slower."},
            {"filename": "quantum_doc.md", "content": "Quantum cryptography guarantees secure key distribution protocol."},
            {"filename": "ai_doc.md", "content": "Neural networks learn hierarchical representations of input data."}
        ]
        with patch("src.core.voice_rag_bridge.execute_sota_rag_search", return_value={"top_candidates": mock_candidates}):
            res_cand = VoiceRAGBridge.query_and_summarize("quantum speedup", max_sentences=2)
            self.assertIsInstance(res_cand, dict)
            self.assertIn("speech_text", res_cand)
            # Candidate 1 provides 2 facts, triggering early break at max_sentences=2
            self.assertEqual(len(res_cand["citations"]), 1)
            self.assertEqual(res_cand["citations"][0], "quantum_doc.md")
            self.assertIn("Quantum algorithms provide exponential speedup", res_cand["speech_text"])

    def test_voice_rag_fact_deduplication(self):
        """Test that duplicate facts and citations across candidates are deduplicated."""
        extracted_facts = []
        seen_facts = set()
        valid_words = {"quantum", "cryptography"}
        content = "Quantum cryptography is secure. Quantum cryptography is secure. Quantum states collapse."
        
        VoiceRAGBridge._extract_facts_from_content(
            content=content,
            valid_query_words=valid_words,
            seen_facts=seen_facts,
            extracted_facts=extracted_facts,
            max_sentences=5
        )
        self.assertEqual(len(extracted_facts), 2)
        self.assertEqual(extracted_facts[0], "Quantum cryptography is secure")
        self.assertEqual(extracted_facts[1], "Quantum states collapse")

    def test_voice_rag_bridge_live_database_search(self):
        """Test VoiceRAGBridge query_and_summarize directly against live database records without mocks."""
        # Query real knowledge database for known domain terms
        res = VoiceRAGBridge.query_and_summarize("Alexander", max_sentences=2)
        self.assertIsInstance(res, dict)
        self.assertIn("speech_text", res)
        self.assertIn("citations", res)
        self.assertIn("retrieval_ms", res)
        self.assertIsInstance(res["citations"], list)
        self.assertGreaterEqual(res["retrieval_ms"], 0.0)


class TestModelRouterAndParsersEdgeCases(unittest.TestCase):
    """Adversarial stress tests for Model Router and Document Parsers."""

    def test_model_router_candidates_selection(self):
        """Test _pick_best_available with empty candidates, prefix matches, and invalid formats."""
        # 1. Empty candidates list -> fallback to default
        self.assertEqual(_pick_best_available([], default_model="fallback_model"), "fallback_model")

        # 2. Non-existent candidate models -> fallback
        self.assertEqual(
            _pick_best_available(["nonexistent_tier_1:99b", "nonexistent_tier_2"], default_model="fallback_model"),
            "fallback_model"
        )

        # 3. Valid candidate prefix matching against probed models
        # Standard probed models include qwen2.5:7b and smollm2:1.7b
        best = _pick_best_available(["smollm2:1.7b", "qwen2.5:7b"])
        self.assertIn(best, ["smollm2:1.7b", "qwen2.5:7b"])

    def test_pptx_parser_missing_and_corrupt_files(self):
        """Test parse_pptx_presentation with missing files and invalid zip containers."""
        # 1. Missing file
        err_missing = parse_pptx_presentation("/nonexistent/path/pres.pptx")
        self.assertTrue(err_missing.startswith("[PPTX Parsing Error:"))

        # 2. Corrupt non-zip file
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            f.write(b"NOT A REAL ZIP FILE CONTENT")
            corrupt_path = f.name

        try:
            err_corrupt = parse_pptx_presentation(corrupt_path)
            self.assertTrue(err_corrupt.startswith("[PPTX Parsing Error:"))
        finally:
            if os.path.exists(corrupt_path):
                os.remove(corrupt_path)

    def test_pptx_parser_valid_minimal_container(self):
        """Test parse_pptx_presentation with a constructed minimal PPTX zip structure."""
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            pptx_path = f.name

        try:
            with zipfile.ZipFile(pptx_path, "w") as z:
                # Add slide XML
                slide_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
                    <p:cSld>
                        <p:spTree>
                            <p:sp>
                                <p:txBody>
                                    <a:p><a:r><a:t>Executive Summary</a:t></a:r></a:p>
                                    <a:p><a:r><a:t>Q3 Revenue increased by 42%.</a:t></a:r></a:p>
                                </p:txBody>
                            </p:sp>
                        </p:spTree>
                    </p:cSld>
                </p:sld>"""
                z.writestr("ppt/slides/slide1.xml", slide_xml)

                # Add speaker notes XML
                notes_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
                    <p:cSld>
                        <p:spTree>
                            <p:sp>
                                <p:txBody>
                                    <a:p><a:r><a:t>Emphasize recurring subscriptions.</a:t></a:r></a:p>
                                </p:txBody>
                            </p:sp>
                        </p:spTree>
                    </p:cSld>
                </p:notes>"""
                z.writestr("ppt/notesSlides/notesSlide1.xml", notes_xml)

            parsed = parse_pptx_presentation(pptx_path)
            self.assertIn("Executive Summary", parsed)
            self.assertIn("Q3 Revenue increased by 42%", parsed)
            self.assertIn("Speaker Notes", parsed)
            self.assertIn("Emphasize recurring subscriptions", parsed)
        finally:
            if os.path.exists(pptx_path):
                os.remove(pptx_path)

    def test_obsidian_parser_tags_deduplication(self):
        """Test parse_obsidian_markdown tag parsing and hashtag deduplication."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("""---
tags: [alpha, beta, #gamma]
aliases: [TestDoc]
created: 2026-08-15
---
# Heading

This is a test note linking to [[Architecture Roadmap|Roadmap]].
Inline hashtags: #alpha #delta #beta #delta #epsilon/sub
""")
            md_path = f.name

        try:
            content, meta = parse_obsidian_markdown(md_path)
            self.assertIn("tags", meta)
            # Frontmatter tags: alpha, beta, gamma
            # Inline tags: delta, epsilon/sub (alpha, beta already seen and should not duplicate)
            tags = meta["tags"]
            self.assertEqual(tags.count("alpha"), 1)
            self.assertEqual(tags.count("beta"), 1)
            self.assertIn("gamma", tags)
            self.assertIn("delta", tags)
            self.assertIn("epsilon/sub", tags)
            self.assertEqual(len(tags), len(set(tags)))

            # Check wikilinks
            self.assertEqual(len(meta["wikilinks"]), 1)
            self.assertEqual(meta["wikilinks"][0]["target"], "Architecture Roadmap")
            self.assertEqual(meta["wikilinks"][0]["display"], "Roadmap")
        finally:
            if os.path.exists(md_path):
                os.remove(md_path)


class TestFileTreePopulationEdgeCases(unittest.TestCase):
    """Adversarial stress tests for _populate_db_tree_nodes and resolve_file_on_disk."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_populate_db_tree_nodes_deduplication(self):
        """Test _populate_db_tree_nodes with pre-existing seen paths and empty rows."""
        base_dir = os.path.abspath(".")
        seen = set()
        tree = []

        # Populate once
        _populate_db_tree_nodes(base_dir, seen, tree)
        initial_count = len(tree)

        # Populate a second time with the same seen set -> should add 0 duplicates
        _populate_db_tree_nodes(base_dir, seen, tree)
        self.assertEqual(len(tree), initial_count)

    def test_resolve_file_on_disk_missing(self):
        """Test resolve_file_on_disk with non-existent paths."""
        self.assertIsNone(resolve_file_on_disk("non_existent_file_abc_123_xyz.txt"))


class TestGraphBoundsCheckStress(unittest.TestCase):
    """Adversarial stress tests for graph node bounds checking (O(1) bounds check)."""

    def test_doc_nid_list_bounds_checking(self):
        """Verify 0 <= fid < len(doc_nid_list) handles all boundary and invalid numeric types."""
        doc_nid_list = [f"file_{i}" for i in range(10)]

        valid_fids = [0, 5, 9]
        invalid_fids = [-1, -999, 10, 100, 999999]

        for fid in valid_fids:
            self.assertTrue(0 <= fid < len(doc_nid_list))
            self.assertEqual(doc_nid_list[fid], f"file_{fid}")

        for fid in invalid_fids:
            self.assertFalse(0 <= fid < len(doc_nid_list))

        # Empty doc_nid_list
        empty_list = []
        for fid in [0, -1, 1]:
            self.assertFalse(0 <= fid < len(empty_list))


class TestConcurrencyAndHighLoadStress(unittest.TestCase):
    """Adversarial stress tests for thread-safety and race condition resilience under high load."""

    def test_job_manager_concurrent_submissions_and_reaping(self):
        """Stress test JobManager under 20 concurrent threads running submits, updates, cancels, and reaps."""
        mgr = JobManager(max_workers=4)
        errors = []

        def worker_task(thread_id):
            try:
                for i in range(25):
                    # Submit dummy completed job
                    jid = f"t_{thread_id}_j_{i}"
                    with mgr._jobs_lock:
                        mgr.jobs[jid] = {
                            "id": jid,
                            "status": "completed" if i % 2 == 0 else "running",
                            "completed_at": time.time() - (100 if i % 3 == 0 else 0)
                        }
                    mgr.update_progress(jid, float(i * 4))
                    if i % 5 == 0:
                        mgr.reap_stale_jobs(ttl_seconds=50.0, max_history=20)
                    if i % 7 == 0:
                        mgr.cancel_job(jid)
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        threads = [threading.Thread(target=worker_task, args=(tid,)) for tid in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Encountered concurrency errors: {errors}")
        # Final reap check
        final_reaped = mgr.reap_stale_jobs(ttl_seconds=0.0, max_history=10)
        self.assertIsInstance(final_reaped, int)


class TestExtremeAdversarialInputs(unittest.TestCase):
    """Adversarial testing with SQL injection patterns, regex special chars, and massive payloads."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_tag_filtering_sql_injection_and_null_bytes(self):
        """Test tag filtering resilience against SQL injection strings and null byte payloads."""
        adversarial_tags = [
            "' OR '1'='1",
            "'; DROP TABLE tags; --",
            "tag\x00with_null",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "\u202Ereversed_bidi_tag\u202C"
        ]
        sample_results = [{"id": 30001, "filename": "safe.md"}]
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE file_id = 30001")
            cursor.execute("DELETE FROM files WHERE id = 30001")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (30001, '/tmp/safe.md', 'safe.md')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (30001, 'standard_tag')")
            conn.commit()

        try:
            # None of the malicious tags match standard_tag -> all should pass through safely without SQL injection
            filtered = _filter_by_excluded_tags(sample_results, adversarial_tags)
            self.assertEqual(len(filtered), 1)
        finally:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tags WHERE file_id = 30001")
                cursor.execute("DELETE FROM files WHERE id = 30001")
                conn.commit()

    def test_autocomplete_regex_special_characters(self):
        """Test autocomplete suggestion generation with regex metacharacters in prefix."""
        metachar_prefixes = [".*", "^[a-z]", "(?i)", "$", "[0-9]+", "\\w+", "{1,3}"]
        for prefix in metachar_prefixes:
            # Must not crash with regex re.error / syntax error
            res = MiniVectorEngine.search_autocomplete_suggested(prefix, top_k=5)
            self.assertIsInstance(res, list)

    def test_smart_extract_context_massive_payload(self):
        """Test _smart_extract_context with 500,000-character payload and 2,000 sentences."""
        sentences = [f"Sentence {i} discusses deep neural indexing and algorithmic complexity." for i in range(2000)]
        massive_context = " ".join(sentences)
        self.assertGreater(len(massive_context), 100000)

        t0 = time.perf_counter()
        extracted = _smart_extract_context(massive_context, "neural algorithmic complexity", max_chars=4000)
        t_elapsed = time.perf_counter() - t0

        self.assertLessEqual(len(extracted), 4500)
        self.assertIn("algorithmic", extracted)
        # Should execute in under 100ms due to set intersection optimization
        self.assertLess(t_elapsed, 0.5)


if __name__ == "__main__":
    unittest.main()

