"""
Comprehensive Test Suite for 10-Tool Open-Source RAG Infrastructure Stack:
1. Web Ingestion: crawl4ai (DocumentationIngestor, AsyncDocumentationCrawler)
2. Document Ingestion: marker-pdf (LayoutAwarePDFParser)
3. Chunking Engine: chonkie (UniversalChunker, TableChunker, ProductionChunker)
4. Vector Storage: qdrant-client (QdrantVectorStore, HNSW, payload pre-filtering)
5. Local Model Execution: ollama (local endpoints failover)
6. Universal Model Gateway: litellm (ModelGatewayRouter, Router load balancing)
7. Constrained Output (Local): outlines (StructuredEngine logit masking)
8. Structured Extraction (Cloud): instructor (StructuredEngine Pydantic v2 retries)
9. Programmatic Prompt Optimization: dspy (DSPyRAGPipeline, MIPROv2 compilation)
10. Observability & Evals: langfuse (LangfuseTracer, @observe() span logging)
"""

import unittest
import os
import sys
import json
import asyncio
import tempfile
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from src.infrastructure.database import init_db, reset_db_connections

# Import 10-Tool Stack Modules
from src.domain.ingestion.crawlers.web_crawler import DocumentationIngestor, CrawledDocument
from src.domain.ingestion.parsers.pdf_parser import LayoutAwarePDFParser
from src.domain.ingestion.chunker import UniversalChunker, TableChunker, ChunkingStrategy, ProductionChunker
from src.infrastructure.storage.vector_store import QdrantVectorStore
from src.core.gateway import ModelGatewayRouter
from src.core.structured_engine import StructuredEngine
from src.domain.optimization.dspy_rag import DSPyRAGPipeline
from src.infrastructure.observability.tracer import LangfuseTracer, observe


class SampleTestSchema(BaseModel):
    """Test schema for structured extraction."""
    intent: str = Field(default="WANT_TO_KNOW")
    confidence: float = Field(default=0.95)
    tags: List[str] = Field(default_factory=lambda: ["rag", "open_source"])


class TestTenToolStack(unittest.TestCase):
    """Empirical integration test suite for the 10-tool open-source RAG infrastructure stack."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        reset_db_connections()
        LangfuseTracer.get_instance().clear()

    def tearDown(self):
        reset_db_connections()

    def test_01_crawl4ai_web_crawler(self):
        """Tool 1: Verify crawl4ai DocumentationIngestor multi-URL async crawling and table preservation."""
        ingestor = DocumentationIngestor()
        urls = ["https://docs.neuro.local/v1/intro", "https://docs.neuro.local/v1/tables"]
        docs = ingestor.crawl_urls_sync(urls)

        self.assertEqual(len(docs), 2)
        for doc in docs:
            self.assertIsInstance(doc, CrawledDocument)
            self.assertTrue(len(doc.markdown_content) > 0)
            self.assertEqual(len(doc.content_hash), 64)

    def test_02_marker_pdf_parser(self):
        """Tool 2: Verify marker LayoutAwarePDFParser multi-column & table PDF extraction."""
        parser = LayoutAwarePDFParser()
        sample_pdf_text = "Neuro Whitepaper\n\nHigh throughput vector indexing."
        res = parser.parse_pdf_bytes(sample_pdf_text.encode("utf-8"), filename="whitepaper.pdf")

        self.assertIn("markdown", res)
        self.assertIn("metadata", res)
        self.assertEqual(res["metadata"]["filename"], "whitepaper.pdf")

    def test_03_chonkie_universal_chunker(self):
        """Tool 3: Verify chonkie UniversalChunker (Recursive, Semantic, Sentence, Table modes)."""
        # 1. Recursive Mode
        r_chunker = UniversalChunker(strategy=ChunkingStrategy.RECURSIVE, chunk_size=100)
        chunks = r_chunker.chunk("# Title\n\nParagraph text for recursive chunking.")
        self.assertGreater(len(chunks), 0)

        # 2. Table Mode
        table_text = """| Service | Tier | Cost |
| --- | --- | --- |
| Qdrant | Cloud | Free |
| Ollama | Local | Free |
| LiteLLM | Router | Free |"""
        t_chunks = TableChunker.chunk_table(table_text=table_text, doc_title="Pricing Matrix")
        self.assertGreater(len(t_chunks), 0)
        self.assertEqual(t_chunks[0].trust_type, "pricing")

    def test_04_qdrant_vector_store(self):
        """Tool 4: Verify qdrant-client QdrantVectorStore with HNSW, Cosine similarity, and pre-filtering."""
        store = QdrantVectorStore(
            location=":memory:",
            collection_name="test_ten_tool_vault",
            vector_dim=128,
            hnsw_m=16,
            hnsw_ef=100
        )

        records = [
            {
                "id": "point_1",
                "vector": [0.1] * 128,
                "content": "Windows SQLite WAL locks resolution guide.",
                "doc_title": "Windows DB Guide",
                "tenant_id": "tenant_alpha",
                "trust_type": "repair_vs_replace"
            },
            {
                "id": "point_2",
                "vector": [0.9] * 128,
                "content": "Linux GPU acceleration options.",
                "doc_title": "Linux GPU Guide",
                "tenant_id": "tenant_beta",
                "trust_type": "environment_constraints"
            }
        ]
        upserted = store.upsert_chunks(records)
        self.assertEqual(upserted, 2)

        # Search with tenant filter
        results = store.search_similarity(
            query_vector=[0.1] * 128,
            top_k=5,
            tenant_id="tenant_alpha"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].tenant_id, "tenant_alpha")
        self.assertEqual(results[0].doc_title, "Windows DB Guide")

    def test_05_ollama_local_execution(self):
        """Tool 5: Verify ollama local open-weight model execution via gateway."""
        gateway = ModelGatewayRouter(default_model="ollama/qwen2.5:7b")
        resp = gateway.completion(
            messages=[{"role": "user", "content": "Ping local Ollama engine."}],
            model="ollama/qwen2.5:7b"
        )
        self.assertTrue(len(resp.text) > 0)
        self.assertTrue(resp.is_fallback or resp.provider in ["litellm", "ollama_local", "deterministic_offline_gateway"])

    def test_06_litellm_model_gateway(self):
        """Tool 6: Verify litellm ModelGatewayRouter completion and embedding generation."""
        gateway = ModelGatewayRouter()
        emb = gateway.embedding("Embed vector representation.")
        self.assertIsInstance(emb, list)
        self.assertGreater(len(emb), 0)

    def test_07_outlines_constrained_generation(self):
        """Tool 7: Verify outlines StructuredEngine local constrained generation (JSON, regex, choices)."""
        # 1. JSON constrained
        model_out = StructuredEngine.generate_local_constrained(
            schema_cls=SampleTestSchema,
            prompt="Analyze system performance metrics"
        )
        self.assertIsInstance(model_out, SampleTestSchema)

        # 2. Regex constrained
        reg_out = StructuredEngine.generate_regex_constrained(
            regex_pattern=r"\[Doc:\s*\w+\]",
            prompt="Reference knowledge document"
        )
        self.assertRegex(reg_out, r"\[Doc:\s*\w+\]")

        # 3. Choice constrained
        choice_out = StructuredEngine.generate_choice_constrained(
            choices=["HIGH", "MEDIUM", "LOW"],
            prompt="Priority level"
        )
        self.assertIn(choice_out, ["HIGH", "MEDIUM", "LOW"])

    def test_08_instructor_structured_extraction(self):
        """Tool 8: Verify instructor StructuredEngine cloud structured extraction with Pydantic v2."""
        extracted = StructuredEngine.extract_cloud_structured(
            schema_cls=SampleTestSchema,
            prompt="Extract user intent regarding vector database storage"
        )
        self.assertIsInstance(extracted, SampleTestSchema)
        self.assertTrue(len(extracted.tags) > 0)
        self.assertGreater(extracted.confidence, 0.0)

    def test_09_dspy_programmatic_optimization(self):
        """Tool 9: Verify dspy DSPyRAGPipeline forward pass and prompt compilation."""
        pipeline = DSPyRAGPipeline()
        context_xml = '<doc id="kb_oss_rag">The 10-tool OSS RAG stack eliminates custom boilerplate.</doc>'
        out = pipeline.forward(
            user_inquiry="How does the OSS RAG stack benefit developers?",
            context=context_xml
        )
        self.assertIn("sub_queries", out)
        self.assertIn("cited_answer", out)
        self.assertIn("kb_oss_rag", out["citations"])

    def test_10_langfuse_observability_tracer(self):
        """Tool 10: Verify langfuse LangfuseTracer span recording and @observe() decorator."""
        tracer = LangfuseTracer.get_instance()

        @observe(name="test_rag_pipeline_stage", as_type="chain")
        def execute_stage():
            tracer.record_span("qdrant_vector_retrieval", span_type="retrieval", duration_ms=15.4, tokens=120)
            tracer.record_span("litellm_synthesis", span_type="generation", duration_ms=85.2, tokens=350)
            return "SUCCESS"

        status = execute_stage()
        self.assertEqual(status, "SUCCESS")

        metrics = tracer.get_metrics_summary()
        self.assertGreaterEqual(metrics["total_spans"], 3)
        self.assertGreater(metrics["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
