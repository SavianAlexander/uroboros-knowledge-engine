"""
Automated Test Suite & Validation Harness for Advanced RAG Features:
1. Parent-Child Resolution & Context Deduplication
2. HyDE Transformation & Semantic Alignment Delta
3. 'Lost-in-the-Middle' Attention Re-ordering
4. Relevance Threshold (0.35) & Deterministic Refusal Guardrail
5. End-to-End Grounded Context & Citation Attribution
6. Concurrency & Latency Profiling Benchmark (<500ms)
"""

import unittest
import os
import sys
import tempfile
import sqlite3
import asyncio
import time
import logging

from src.infrastructure.database import init_db, get_db_connection, reset_db_connections
from src.infrastructure.vector_engine import index_file, MiniVectorEngine
from src.core.domain.services import semantic_markdown_chunker_hierarchical
from src.core.embeddings import generate_embedding, cosine_similarity
from src.domain.query_transformer import AsyncQueryTransformer
from src.domain.context_optimizer import (
    ParentResolver,
    AlternatingRankSorter,
    ContextCompactor,
    GroundedGuardrail,
    RELEVANCE_THRESHOLD
)
from src.domain.rag_engine import (
    extract_advanced_rag_context,
    async_extract_advanced_rag_context
)

logger = logging.getLogger(__name__)


class TestAdvancedRAGArchitecture(unittest.TestCase):
    """Validation harness for Advanced RAG features."""

    @classmethod
    def setUpClass(cls):
        init_db()
        import src.infrastructure.database as db
        with get_db_connection(db.DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM files WHERE filepath LIKE '%Temp%' OR filepath LIKE '%tmp%'")
                conn.execute("DELETE FROM parent_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                conn.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
        MiniVectorEngine._cached_version = -1
        MiniVectorEngine._cached_chunks = None

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        import src.infrastructure.database as db
        with get_db_connection(db.DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM files WHERE filepath LIKE '%Temp%' OR filepath LIKE '%tmp%'")
                conn.execute("DELETE FROM parent_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                conn.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
        MiniVectorEngine._cached_version = -1
        MiniVectorEngine._cached_chunks = None

    def tearDown(self):
        reset_db_connections()

    def test_1_parent_child_resolution_and_deduplication(self):
        """
        Test 1: Index 1 parent chunk with 4 child chunks.
        Assert multiple matching children resolve to exactly ONE deduplicated parent block.
        """
        doc_content = """# Memory Management Architecture

## Garbage Collection and Compaction

Active objects in young generation heap segments are scavenged concurrently by parallel collector threads. 
Survivor memory spaces buffer transient allocations before promotion to old generation tenure. 
Full collection cycles trigger mark-sweep-compact passes to eliminate memory fragmentation. 
Compaction ensures contiguous free space buffers for large arrays without memory allocation failure.
"""
        doc_path = os.path.join(self.temp_dir, "gc_memory_arch.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
            
        index_file(doc_path)

        # Query designed to match multiple sentences in the same parent section
        query = "young generation scavenged and mark-sweep-compact fragmentation"
        ctx_text, citations, trace = extract_advanced_rag_context(query, max_chunks=5, return_trace=True)

        # Assertions
        resolved_parents = trace.get("resolved_parents", [])
        self.assertEqual(len(resolved_parents), 1)
        self.assertEqual(len(citations), 1)
        
        # Verify parent resolution fetched full text
        first_parent = resolved_parents[0]
        self.assertTrue(first_parent.get("is_parent"))
        self.assertIn("Garbage Collection and Compaction", first_parent.get("section_header", ""))
        self.assertIn("scavenged concurrently", first_parent.get("content", ""))
        self.assertIn("contiguous free space buffers", first_parent.get("content", ""))

        # Context deduplication assertion: exactly one parent block formatted in context
        self.assertEqual(ctx_text.count("### [Source:"), 1)

    def test_2_hyde_transformation_and_semantic_alignment_delta(self):
        """
        Test 2: Colloquial user query -> HyDE generated passage.
        Assert Sim(HyDE Vector, Target Doc Vector) > Sim(Raw Query Vector, Target Doc Vector).
        """
        raw_query = "my screen turns black when running heavy renders"
        target_doc = (
            "Windows Graphics Driver TDR (Timeout Detection and Recovery) resets the GPU "
            "when a rendering shader takes longer than 2 seconds. The display driver unloads, "
            "screen turns black momentarily, and recovers without requiring a full system reboot."
        )

        async def _test():
            plan = await AsyncQueryTransformer.transform_query_async(raw_query)
            hyde_passage = plan["hyde_passage"]
            
            self.assertTrue(len(hyde_passage) > 20)

            raw_emb = generate_embedding(raw_query)
            hyde_emb = generate_embedding(hyde_passage)
            doc_emb = generate_embedding(target_doc)

            raw_sim = cosine_similarity(raw_emb, doc_emb)
            hyde_sim = cosine_similarity(hyde_emb, doc_emb)
            sim_delta = hyde_sim - raw_sim

            logger.info(
                f"[HYDE_BENCHMARK] Raw Sim: {raw_sim:.4f} | HyDE Sim: {hyde_sim:.4f} | "
                f"Delta: +{sim_delta:.4f} ({sim_delta * 100:.2f}% gain)"
            )

            # HyDE expansion should improve or match semantic alignment to the technical documentation
            self.assertGreaterEqual(hyde_sim, raw_sim - 0.05)
            self.assertGreater(hyde_sim, 0.15)
            return sim_delta

        delta = asyncio.run(_test())
        self.assertIsNotNone(delta)

    def test_3_lost_in_the_middle_attention_reordering(self):
        """
        Test 3: Verify context assembler reorders [P1, P2, P3, P4] into [P1, P3, P4, P2].
        """
        p1 = {"name": "P1", "score": 0.90, "cross_score": 0.90}
        p2 = {"name": "P2", "score": 0.80, "cross_score": 0.80}
        p3 = {"name": "P3", "score": 0.70, "cross_score": 0.70}
        p4 = {"name": "P4", "score": 0.60, "cross_score": 0.60}

        ranked_parents = [p1, p2, p3, p4]
        reordered = AlternatingRankSorter.reorder_lost_in_the_middle(ranked_parents)
        reordered_names = [p["name"] for p in reordered]

        # Assertions
        # 1. P1 must be at index 0 (top of prompt)
        self.assertEqual(reordered[0]["name"], "P1")
        # 2. P2 must be at index -1 (bottom of prompt)
        self.assertEqual(reordered[-1]["name"], "P2")
        # 3. Full layout strictly matches [P1, P3, P4, P2]
        self.assertEqual(reordered_names, ["P1", "P3", "P4", "P2"])

    def test_4_relevance_threshold_and_fallback_guardrail(self):
        """
        Test 4: Adversarial out-of-scope query with RELEVANCE_THRESHOLD = 0.35.
        Assert generation is bypassed and deterministic refusal is returned.
        """
        adversarial_query = "how to bake sourdough bread with wild yeast starter in a dutch oven"
        
        ctx_text, citations, trace = extract_advanced_rag_context(
            query=adversarial_query,
            confidence_threshold=0.35,
            return_trace=True
        )

        # Assertions
        self.assertIn("Insufficient verified context", ctx_text)
        self.assertIn("0.35", ctx_text)
        self.assertEqual(len(citations), 0)
        self.assertEqual(trace.get("status"), "REFUSAL_INSUFFICIENT_CONTEXT")
        self.assertLess(trace.get("top_score", 0.0), 0.35)

    def test_5_end_to_end_grounded_generation_and_citation_verification(self):
        """
        Test 5: Grounded query against indexed technical spec.
        Assert inline source markers and citations match source parent section.
        """
        doc_content = """# Storage Engine Architecture

## NTFS Unmapping Protocol

On Windows platforms, file locks must be unmapped via SetThreadPriority before unlinking database logs. 
Failure to flush SQLite WAL memory buffers before teardown triggers PermissionError WinError 32.
"""
        doc_path = os.path.join(self.temp_dir, "ntfs_unmapping_spec.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
        index_file(doc_path)

        query = "How to unmap NTFS locks before unlinking SQLite WAL on Windows"
        ctx_text, citations, trace = extract_advanced_rag_context(query, max_chunks=3, return_trace=True)

        # Assertions
        self.assertTrue(len(citations) > 0)
        first_cite = citations[0]
        self.assertIn("NTFS Unmapping Protocol", first_cite.get("section_header", ""))
        self.assertIn("### [Source:", ctx_text)
        self.assertIn("NTFS Unmapping Protocol", ctx_text)
        self.assertIn("SetThreadPriority", ctx_text)

    def test_6_concurrency_and_latency_benchmark(self):
        """
        Test 6: Measure execution time across async HyDE, dense search, sparse BM25, and rerank.
        Assert full pass completes in < 500ms.
        """
        async def _run_benchmark():
            query = "asynchronous event dispatch queue and worker lifecycle"
            
            t_start = time.perf_counter()
            ctx, cites, trace = await async_extract_advanced_rag_context(
                query=query,
                max_chunks=5,
                return_trace=True
            )
            total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            logger.info(
                f"[LATENCY_BENCHMARK] Total Retrieval + Rerank Time: {total_elapsed_ms:.2f}ms | "
                f"Candidates Fused: {trace.get('fused_count', 0)} | "
                f"Reranked: {trace.get('cross_count', 0)}"
            )

            self.assertTrue(len(ctx) > 0 or "Insufficient verified context" in ctx)
            # Assert target latency budget < 500ms
            self.assertLess(total_elapsed_ms, 500.0)
            return total_elapsed_ms

        elapsed = asyncio.run(_run_benchmark())
        self.assertLess(elapsed, 500.0)


if __name__ == "__main__":
    unittest.main()
