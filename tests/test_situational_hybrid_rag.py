"""
Comprehensive Test Suite for Attribute-Aware Hybrid Semantic RAG Pipeline.
Verifies:
1. Markdown-Aware Semantic & Hierarchical Chunking
2. Contextual Breadcrumb Enrichment & Answer-First Formatting
3. Chunk Attribute Extraction (Intent, Entities, Domain Scope)
4. Pre-Retrieval Situational Query Analysis & Decomposition
5. Attribute-Aware Hybrid Retrieval & RRF Fusion
6. Post-Retrieval Situational Cross-Encoder Reranker & Relevance Gating
7. Multi-Variable Situational Retrieval Accuracy
"""

import unittest
import os
import tempfile
import sqlite3
import json

from src.core.domain.services import (
    semantic_markdown_chunker,
    extract_chunk_attributes,
    chunk_text,
    reciprocal_rank_fusion
)
from src.domain.situational_query_analyzer import (
    SituationalQueryAnalyzer,
    SituationalQueryPlan
)
from src.domain.situational_cross_reranker import SituationalCrossReranker
from src.domain.rag_engine import extract_advanced_rag_context, rrf_rerank
from src.infrastructure.database import init_db, DB_FILE, reset_db_connections, get_db_write_connection
from src.infrastructure.vector_engine import index_file, MiniVectorEngine


class TestSituationalHybridRAG(unittest.TestCase):

    def setUp(self):
        reset_db_connections()
        init_db()

    def tearDown(self):
        reset_db_connections()

    def test_semantic_markdown_chunking_with_breadcrumbs(self):
        """Verify markdown AST chunker preserves breadcrumbs, headers, and tables."""
        md_text = (
            "# Uroboros Knowledge Engine\n\n"
            "This is the overarching architecture.\n\n"
            "## Database Layer\n\n"
            "SQLite is used as the primary embedded database with WAL mode.\n\n"
            "| Pragma | Setting | Purpose |\n"
            "| :--- | :--- | :--- |\n"
            "| journal_mode | WAL | High Concurrency |\n"
            "| busy_timeout | 60000 | Lock Resilience |\n\n"
            "### Windows Concurrency\n\n"
            "On Windows, handle thread-local connections to avoid WinError 32 permission errors.\n"
        )
        chunks = semantic_markdown_chunker(md_text, filepath="/vault/architecture/db.md", max_chunk_size=400)
        self.assertTrue(len(chunks) >= 2)
        
        # Check breadcrumb resolution
        first_chunk = chunks[0]
        self.assertIn("Uroboros Knowledge Engine", first_chunk["parent_header"])
        self.assertIn("[Context:", first_chunk["content"])

        # Check table preservation
        table_chunk = next((c for c in chunks if "|" in c["raw_content"]), None)
        self.assertIsNotNone(table_chunk)
        self.assertIn("busy_timeout", table_chunk["raw_content"])
        self.assertIn("journal_mode", table_chunk["raw_content"])

    def test_chunk_attribute_extraction(self):
        """Verify automatic extraction of intent, entities, and domain scope."""
        troubleshooting_text = "Fixing WinError 32 database lock exception in Python sqlite3 driver on Windows."
        attrs = extract_chunk_attributes(troubleshooting_text, doc_title="Troubleshooting Guide", parent_headers="Windows > SQLite")
        
        self.assertEqual(attrs["intent_type"], "troubleshooting")
        self.assertIn("windows", attrs["entities"])
        self.assertIn("sqlite", attrs["entities"])
        self.assertIn("python", attrs["entities"])
        self.assertEqual(attrs["domain_scope"], "backend_engineering")

        pricing_text = "Enterprise pricing tier costs $499 per month for unlimited API requests."
        attrs_pricing = extract_chunk_attributes(pricing_text, doc_title="Pricing Spec")
        self.assertEqual(attrs_pricing["intent_type"], "pricing")

    def test_situational_query_analysis(self):
        """Verify long situational query decomposition into semantic query, attributes, and sub-queries."""
        long_query = (
            "Hi team, could you please help us understand why we are seeing a WinError 32 database lock error "
            "when running concurrent SQLite writes in Python on Windows? What is the recommended WAL configuration?"
        )
        plan = SituationalQueryAnalyzer.analyze_situational_query(long_query)
        
        self.assertEqual(plan.intent_type, "troubleshooting")
        self.assertIn("windows", plan.environments)
        self.assertIn("sqlite", plan.technologies)
        self.assertIn("python", plan.technologies)
        self.assertTrue(len(plan.sub_queries) >= 2)
        self.assertNotIn("could you please", plan.core_semantic_query.lower())
        self.assertIn("winerror 32", plan.core_semantic_query.lower())

    def test_situational_cross_reranker_and_relevance_gate(self):
        """Verify situational cross-reranking boosts attribute-matched candidates and gates distractors."""
        plan = SituationalQueryPlan(
            raw_query="How to fix SQLite WinError 32 lock on Windows in Python",
            core_semantic_query="fix SQLite WinError 32 lock Windows Python",
            intent_type="troubleshooting",
            environments=["windows"],
            technologies=["sqlite", "python"]
        )

        candidates = [
            {
                "id": 1,
                "filename": "windows_sqlite_troubleshooting.md",
                "doc_title": "Windows SQLite Troubleshooting",
                "parent_header": "Architecture > Troubleshooting",
                "content": "On Windows, SQLite multi-threading requires closing thread-local connections to resolve WinError 32 permission lock issues.",
                "intent_type": "troubleshooting",
                "domain_scope": "backend_engineering",
                "score": 0.5
            },
            {
                "id": 2,
                "filename": "react_tailwind_buttons.md",
                "doc_title": "React Button Styling",
                "parent_header": "UI > Components",
                "content": "Use Tailwind CSS classes bg-blue-500 hover:bg-blue-700 to style primary React action buttons.",
                "intent_type": "procedural",
                "domain_scope": "frontend_ui",
                "score": 0.45
            }
        ]

        reranked = SituationalCrossReranker.rerank(
            query=plan.raw_query,
            candidates=candidates,
            query_plan=plan,
            min_relevance_threshold=0.25
        )

        # The relevant Windows SQLite troubleshooting doc should be #1
        self.assertTrue(len(reranked) >= 1)
        self.assertEqual(reranked[0]["id"], 1)
        self.assertGreater(reranked[0]["relevance_confidence"], 0.3)
        self.assertIn("cross_score", reranked[0])

    def test_e2e_situational_hybrid_rag(self):
        """Verify full end-to-end situational hybrid RAG context extraction."""
        query = "How do we resolve SQLite database locking in Python on Windows?"
        context, citations = extract_advanced_rag_context(query, max_chunks=3)
        
        self.assertIsInstance(context, str)
        self.assertIsInstance(citations, list)

    def test_indexing_with_semantic_chunks_and_database_persistence(self):
        """Verify index_file stores parent_header, doc_title, and attributes into SQLite."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = os.path.join(tmp_dir, "test_doc.md")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(
                    "# FastTrack Guide\n\n"
                    "## Configuration\n\n"
                    "Configure FastAPI routes in `src/app/routers/` using Pydantic schemas.\n\n"
                    "## Troubleshooting\n\n"
                    "If a 500 internal server error occurs, check the uvicorn exception logs.\n"
                )

            # Index the file
            success = index_file(test_file)
            self.assertTrue(success)

            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT c.*, f.filepath FROM file_chunks c JOIN files f ON c.file_id = f.id "
                    "WHERE f.filepath LIKE ? OR c.doc_title LIKE ?",
                    (f"%test_doc.md%", "%FastTrack%")
                ).fetchall()
                self.assertTrue(len(rows) >= 1)
                row = rows[0]
                self.assertIn("FastTrack Guide", row["doc_title"] or row["parent_header"] or row["content"])


if __name__ == "__main__":
    unittest.main()
