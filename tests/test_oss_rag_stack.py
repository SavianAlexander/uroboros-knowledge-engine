"""
Comprehensive Integration Test Suite for Production Open-Source RAG Infrastructure Stack:
1. Document Ingestion (Marker-PDF)
2. Web Ingestion (Crawl4AI)
3. Chunking Engine (Chonkie)
4. Vector & Payload Storage (Qdrant Client)
5. Universal Model Gateway (LiteLLM)
6. Type-Safe Extraction (Instructor + Pydantic v2)
7. Observability & Tracing (Langfuse)
8. Programmatic Prompt Optimization (DSPy)
"""

import unittest
import asyncio
import os
import sys
import tempfile
from typing import List, Dict, Any

from src.infrastructure.database import init_db, reset_db_connections

# Import OSS RAG Modules
from src.domain.ingestion.parsers.pdf_parser import LayoutAwarePDFParser
from src.domain.ingestion.crawlers.web_crawler import ProductionWebCrawler
from src.domain.ingestion.chunker import ProductionChunker, ChunkingStrategy, ChunkPayload
from src.infrastructure.storage.qdrant_store import QdrantVectorEngine, QdrantSearchResult
from src.core.gateway.litellm_gateway import UniversalModelGateway, GatewayCompletionRequest
from src.domain.extraction.instructor_extractor import TypeSafeExtractor, QueryIntentPayload, CRAGStateEvaluation
from src.infrastructure.observability.langfuse_tracer import LangfuseTracer, RAGTraceRecord
from src.domain.optimization.dspy_optimizer import DSPyRAGModule


class TestOSSRAGInfrastructureStack(unittest.TestCase):
    """Verifies all 8 layers of the production open-source RAG infrastructure stack."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        reset_db_connections()

    def tearDown(self):
        reset_db_connections()

    def test_01_marker_pdf_ingestion(self):
        """Test 1: Verify LayoutAwarePDFParser parses PDF content into structured Markdown."""
        # Create a dummy PDF for test parsing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name
            try:
                import pypdf
                writer = pypdf.PdfWriter()
                writer.add_blank_page(width=200, height=200)
                writer.write(tmp_pdf)
            except Exception:
                tmp_pdf.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0/Kids[]>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n103\n%%EOF")

        try:
            res = LayoutAwarePDFParser.parse_pdf_to_markdown(pdf_path)
            self.assertIsInstance(res, dict)
            self.assertIn("markdown", res)
            self.assertIn("page_count", res)
            self.assertIn("engine", res)
            self.assertTrue(len(res["engine"]) > 0)
        finally:
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass

    def test_02_crawl4ai_web_ingestion(self):
        """Test 2: Verify ProductionWebCrawler crawls web content into clean Markdown."""
        # Test URL parsing
        with self.assertRaises(ValueError):
            ProductionWebCrawler.crawl_url_sync("invalid_url_without_scheme")

        # Test simulated URL parsing
        async def run_crawl_test():
            # Mock crawl result
            res = await ProductionWebCrawler._fallback_crawl("https://example.com")
            self.assertIsInstance(res, dict)
            self.assertIn("markdown", res)
            self.assertIn("title", res)
            self.assertEqual(res["status_code"], 200)

        # Run async test safely
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(run_crawl_test())
        finally:
            loop.close()

    def test_03_chonkie_semantic_chunking(self):
        """Test 3: Verify ProductionChunker decomposes text into validated Pydantic ChunkPayloads."""
        sample_doc = (
            "# High-Performance RAG Architecture\n\n"
            "## Section 1: Vector Indexing\n"
            "Qdrant enables high-throughput vector search with Rust-level performance.\n"
            "Pricing for cloud hosting starts at reasonable tiers.\n\n"
            "## Section 2: Hybrid Fusion\n"
            "Reciprocal rank fusion merges sparse BM25 and dense embeddings.\n"
            "Windows NTFS requires clean file handle unmapping.\n"
        )

        chunks = ProductionChunker.chunk_document(
            text=sample_doc,
            doc_title="rag_spec.md",
            filepath="/docs/rag_spec.md",
            chunk_size=150,
            overlap=30
        )

        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertIsInstance(c, ChunkPayload)
            self.assertIn(c.doc_title, ["rag_spec.md", "High-Performance RAG Architecture"])
            self.assertTrue(len(c.content) > 0)
            self.assertIn(c.trust_type, ["pricing", "environment_context", "environment_constraints", "general", "problems", "not_a_fit", "repair_vs_replace"])

    def test_04_qdrant_vector_store_payload_filtering(self):
        """Test 4: Verify QdrantVectorEngine vector indexing and deterministic payload pre-filtering."""
        engine = QdrantVectorEngine(location=":memory:", collection_name="test_oss_collection", vector_dim=4)

        test_records = [
            {
                "id": "doc_tenant_42",
                "vector": [0.9, 0.1, 0.0, 0.0],
                "content": "Tenant 42 confidential financial spec",
                "doc_title": "finance.md",
                "tenant_id": 42,
                "trust_type": "pricing"
            },
            {
                "id": "doc_tenant_99",
                "vector": [0.88, 0.12, 0.0, 0.0],
                "content": "Tenant 99 general operational documentation",
                "doc_title": "operations.md",
                "tenant_id": 99,
                "trust_type": "general"
            }
        ]

        count = engine.upsert_chunks(test_records)
        self.assertEqual(count, 2)

        # 1. Unfiltered query
        all_hits = engine.search_similarity(query_vector=[0.9, 0.1, 0.0, 0.0], top_k=5)
        self.assertEqual(len(all_hits), 2)

        # 2. Strict Tenant Pre-Filter: Only Tenant 42 allowed
        filtered_hits = engine.search_similarity(
            query_vector=[0.9, 0.1, 0.0, 0.0],
            top_k=5,
            tenant_id=42
        )
        self.assertEqual(len(filtered_hits), 1)
        self.assertEqual(filtered_hits[0].tenant_id, 42)
        self.assertEqual(filtered_hits[0].id, "doc_tenant_42")

        # 3. Strict Trust-Type Pre-Filter: Only 'pricing' allowed
        pricing_hits = engine.search_similarity(
            query_vector=[0.9, 0.1, 0.0, 0.0],
            top_k=5,
            trust_type="pricing"
        )
        self.assertEqual(len(pricing_hits), 1)
        self.assertEqual(pricing_hits[0].trust_type, "pricing")

    def test_05_litellm_gateway_completions(self):
        """Test 5: Verify UniversalModelGateway completion execution and embedding generation."""
        req = GatewayCompletionRequest(
            model="ollama/qwen2.5:7b",
            messages=[
                {"role": "system", "content": "You are a concise engineering assistant."},
                {"role": "user", "content": "Explain vector similarity."}
            ],
            temperature=0.1,
            max_tokens=64
        )

        resp = UniversalModelGateway.complete_sync(req)
        self.assertIsInstance(resp.content, str)
        self.assertTrue(len(resp.content) > 0)
        self.assertTrue(len(resp.gateway_engine) > 0)

        # Test embedding generation
        emb = asyncio.run(UniversalModelGateway.get_embedding_async("Qdrant high throughput vector retrieval"))
        self.assertIsInstance(emb, list)
        self.assertGreater(len(emb), 0)

    def test_06_instructor_pydantic_extraction(self):
        """Test 6: Verify TypeSafeExtractor Pydantic v2 structured extraction."""
        # 1. Query Intent Extraction
        intent_res = TypeSafeExtractor.extract_structured(
            schema_cls=QueryIntentPayload,
            prompt="How do I configure SQLite WAL checkpointing in Python on Windows env:windows?"
        )
        self.assertIsInstance(intent_res, QueryIntentPayload)
        self.assertIn("sqlite", [e.lower() for e in intent_res.entities + intent_res.technologies + [intent_res.clean_query]])

        # 2. CRAG State Evaluation
        crag_res = TypeSafeExtractor.extract_structured(
            schema_cls=CRAGStateEvaluation,
            prompt="Query: Python vector search\nContext: Qdrant client provides fast Rust-backed vector search."
        )
        self.assertIsInstance(crag_res, CRAGStateEvaluation)
        self.assertIn(crag_res.state, ["CORRECT", "AMBIGUOUS", "INCORRECT"])
        self.assertGreaterEqual(crag_res.confidence, 0.0)

    def test_07_langfuse_observability_tracing(self):
        """Test 7: Verify LangfuseTracer span logging and lifecycle telemetry records."""
        trace = LangfuseTracer.create_trace(query="What are the benefits of Chonkie recursive chunking?")
        self.assertIsInstance(trace, RAGTraceRecord)

        # Log retrieval span
        span1 = LangfuseTracer.log_span(
            trace=trace,
            stage_name="retrieval_dense",
            input_data={"query": trace.query},
            output_data={"hits": 5, "top_score": 0.94},
            latency_ms=12.45,
            tokens_used=45
        )
        self.assertEqual(span1.stage_name, "retrieval_dense")
        self.assertEqual(len(trace.spans), 1)

        # Log cross-encoder rerank span
        span2 = LangfuseTracer.log_span(
            trace=trace,
            stage_name="cross_encoder_rerank",
            input_data={"candidates": 5},
            output_data={"reranked": 3},
            latency_ms=4.12,
            tokens_used=120
        )
        self.assertEqual(len(trace.spans), 2)
        self.assertAlmostEqual(trace.total_latency_ms, 16.57, places=1)
        self.assertEqual(trace.total_tokens, 165)

        # Finalize trace
        LangfuseTracer.finalize_trace(trace, final_output="Chonkie preserves markdown headings.")
        self.assertEqual(trace.final_output, "Chonkie preserves markdown headings.")

    def test_08_dspy_programmatic_prompt_module(self):
        """Test 8: Verify DSPyRAGModule multi-hop decomposition and grounded synthesis."""
        dspy_mod = DSPyRAGModule()

        # Query decomposition
        decomp = dspy_mod.decompose_query("Compare Qdrant vs SQLite vector performance on Windows")
        self.assertIsInstance(decomp.sub_queries, list)
        self.assertGreater(len(decomp.sub_queries), 0)

        # Grounded answer synthesis
        synth = dspy_mod.synthesize_answer(
            context="Qdrant uses Rust with AVX2 SIMD acceleration for vector distances.",
            question="What acceleration does Qdrant use?"
        )
        self.assertIsInstance(synth.answer, str)
        self.assertTrue(len(synth.answer) > 0)
        self.assertGreater(synth.confidence_score, 0.5)

        # Few-shot optimizer compilation
        trainset = [
            {"question": "How to chunk?", "context": "Chonkie recursive", "answer": "Use Chonkie"}
        ]
        compiled = dspy_mod.optimize_with_few_shot(trainset)
        self.assertTrue(compiled)


if __name__ == "__main__":
    unittest.main()
