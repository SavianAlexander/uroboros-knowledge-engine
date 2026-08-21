"""
Diagnostic & Integration Test Suite: Advanced Context Architecture.
Verifies:
1. Parent-Child Resolution (Child hits expand to full Parent sections).
2. Parent Deduplication (Multiple child hits from same parent collapse into 1 block).
3. 'Lost in the Middle' Alternating Layout ([R1, R3, R5, ..., R6, R4, R2]).
4. Async HyDE & Step-Back Query Transformation.
5. Strict Confidence Gating & Grounded Refusal Fallback.
6. Async Retrieval Orchestrator Concurrency & Latency.
"""

import unittest
import os
import sys
import tempfile
import sqlite3
import asyncio
import time

from src.infrastructure.database import init_db, get_db_connection, reset_db_connections
from src.infrastructure.vector_engine import index_file, MiniVectorEngine
from src.core.domain.services import semantic_markdown_chunker_hierarchical
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


class TestAdvancedContextArchitecture(unittest.TestCase):
    """Empirical verification suite for Advanced Context Architecture."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        import src.infrastructure.database as db
        with get_db_connection(db.DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM files WHERE filepath LIKE '%Temp%' OR filepath LIKE '%tmp%'")
                conn.execute("DELETE FROM parent_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                conn.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
        MiniVectorEngine.reset_cache()

    def tearDown(self):
        reset_db_connections()

    def test_1_parent_child_hierarchical_chunking_and_storage(self):
        """Verify two-tier chunker generates section parents and granular child chunks."""
        markdown_doc = """# Operating System Architecture

## Kernel Process Scheduler

The kernel preemptively schedules tasks using a multi-level feedback queue. Priority decay ensures starvation resistance across background and interactive tasks.

## Virtual Memory Paging

Pages are allocated on demand using copy-on-write semantics. Page faults trigger kernel trap handlers to page in memory frames from swap storage.
"""
        hierarchy = semantic_markdown_chunker_hierarchical(
            markdown_doc,
            filepath="os_architecture.md",
            parent_size=300,
            child_size=120,
            child_overlap=30
        )
        parents = hierarchy["parent_chunks"]
        children = hierarchy["child_chunks"]

        self.assertGreaterEqual(len(parents), 2)
        self.assertGreaterEqual(len(children), 2)
        
        # Verify parent IDs are referenced by children
        parent_ids = {p["id"] for p in parents}
        for child in children:
            self.assertIn(child["parent_id"], parent_ids)
            self.assertIn("[Context: ", child["content"])

    def test_2_parent_resolver_and_deduplication(self):
        """Verify multiple child hits from the same parent section collapse into one parent block."""
        parent_id = "parent_test_12345"
        mock_child_hits = [
            {
                "id": 1,
                "chunk_id": 101,
                "parent_id": parent_id,
                "filename": "sys_spec.md",
                "score": 0.85,
                "cross_score": 0.90,
                "content": "Child chunk 1 content"
            },
            {
                "id": 1,
                "chunk_id": 102,
                "parent_id": parent_id,
                "filename": "sys_spec.md",
                "score": 0.75,
                "cross_score": 0.80,
                "content": "Child chunk 2 content"
            },
            {
                "id": 2,
                "chunk_id": 201,
                "parent_id": "parent_other_67890",
                "filename": "other_spec.md",
                "score": 0.60,
                "cross_score": 0.65,
                "content": "Other parent chunk content"
            }
        ]

        # Insert test parents into DB
        import src.infrastructure.database as db
        with get_db_connection(db.DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM parent_chunks WHERE id IN (?, ?)", (parent_id, "parent_other_67890"))
                conn.execute("""
                    INSERT INTO parent_chunks (id, file_id, section_header, content, doc_title, domain_scope, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (parent_id, 1, "Process Scheduler", "Full section context for Process Scheduler.", "System Spec", "backend", time.time()))
                conn.execute("""
                    INSERT INTO parent_chunks (id, file_id, section_header, content, doc_title, domain_scope, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("parent_other_67890", 2, "Memory Manager", "Full section context for Memory Manager.", "Other Spec", "backend", time.time()))

        resolved = ParentResolver.resolve_parents_from_child_hits(mock_child_hits)
        
        # Must resolve to exactly 2 unique parent sections, not 3
        self.assertEqual(len(resolved), 2)
        self.assertEqual(resolved[0]["parent_id"], parent_id)
        self.assertEqual(resolved[0]["content"], "Full section context for Process Scheduler.")
        # Highest score should be retained
        self.assertEqual(resolved[0]["cross_score"], 0.90)

    def test_3_lost_in_the_middle_alternating_layout(self):
        """Verify AlternatingRankSorter implements [R1, R3, R5, ..., R6, R4, R2] layout."""
        items = [
            {"name": "R1", "score": 0.95},
            {"name": "R2", "score": 0.85},
            {"name": "R3", "score": 0.75},
            {"name": "R4", "score": 0.65},
            {"name": "R5", "score": 0.55},
            {"name": "R6", "score": 0.45},
        ]
        reordered = AlternatingRankSorter.reorder_lost_in_the_middle(items)
        names = [x["name"] for x in reordered]

        # Top item (R1) must be at index 0 (top)
        self.assertEqual(names[0], "R1")
        # Second item (R2) must be at index -1 (bottom)
        self.assertEqual(names[-1], "R2")
        # Third item (R3) at index 1
        self.assertEqual(names[1], "R3")
        # Layout should match [R1, R3, R5, R6, R4, R2]
        self.assertEqual(names, ["R1", "R3", "R5", "R6", "R4", "R2"])

    def test_4_async_query_transformation_hyde_and_step_back(self):
        """Verify HyDE passage generation and step-back conceptual expansion."""
        async def _run():
            prompt = "How to resolve WinError 32 sqlite db-wal file locking in Windows pytest"
            plan = await AsyncQueryTransformer.transform_query_async(prompt)
            
            self.assertIn("raw_prompt", plan)
            self.assertTrue(len(plan["hyde_passage"]) > 10)
            self.assertTrue(len(plan["step_back_query"]) > 10)
            self.assertIn("database", plan["step_back_query"].lower())
            self.assertGreaterEqual(len(plan["sub_queries"]), 1)

        asyncio.run(_run())

    def test_5_strict_confidence_gating_and_refusal_fallback(self):
        """Verify queries with cross-encoder score below 0.35 trigger deterministic refusal."""
        query = "Quantum teleportation flux capacitor warp drive protocol"
        
        ctx_text, citations = extract_advanced_rag_context(
            query=query,
            confidence_threshold=0.35
        )
        self.assertIn("Insufficient verified context", ctx_text)
        self.assertEqual(len(citations), 0)

    def test_6_async_retrieval_orchestrator_concurrency(self):
        """Verify async_extract_advanced_rag_context executes concurrently without blocking."""
        async def _run():
            # Index a test document
            doc_path = os.path.join(self.temp_dir, "async_spec.md")
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write("# Distributed Messaging\n\n## Ring Buffer Queue\n\nHigh throughput circular buffers process packets asynchronously.\n")
            index_file(doc_path)

            t0 = time.time()
            ctx, cites, trace = await async_extract_advanced_rag_context(
                query="circular ring buffer queue asynchronous packet processing",
                return_trace=True
            )
            elapsed = time.time() - t0

            self.assertTrue(len(ctx) > 0)
            self.assertTrue(len(cites) > 0)
            self.assertIn("transform_plan", trace)
            self.assertLess(elapsed, 2.0)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
