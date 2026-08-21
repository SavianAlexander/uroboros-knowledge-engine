"""
Comprehensive Test Suite for Web Ingestion Pipeline Using Crawl4AI:
1. CrawledDocument Pydantic v2 schema and deterministic SHA-256 hashing.
2. Async multi-URL concurrency and stealth browser configuration.
3. Markdown layout, HTML table reconstruction, and fenced code block preservation.
4. Delta change detection and sync ledger caching.
5. Integration with Chonkie chunking engine.
6. End-to-end crawling, delta hashing, chunking, and Qdrant vector store indexing.
"""

import unittest
import os
import sys
import json
import hashlib
import asyncio
import tempfile
from typing import Dict, Any, List

from src.infrastructure.database import init_db, reset_db_connections

# Import Web Ingestion and RAG Modules
from src.domain.ingestion.crawlers.web_crawler import (
    CrawledDocument,
    DocumentationIngestor,
    AsyncDocumentationCrawler,
    ProductionWebCrawler
)
from src.domain.ingestion.chunker import ProductionChunker
from src.infrastructure.storage.qdrant_store import QdrantVectorEngine


class TestWebIngestionCrawler(unittest.TestCase):
    """Empirical verification suite for Crawl4AI web and documentation ingestion pipeline."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        reset_db_connections()

    def tearDown(self):
        reset_db_connections()

    def test_01_crawled_document_schema_and_hashing(self):
        """Test 1: Verify CrawledDocument schema validation and SHA-256 content hashing."""
        text = "# Technical Documentation\n\nHigh-performance vector retrieval with SQLite and Qdrant."
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        doc = CrawledDocument(
            url="https://docs.neuro.local/v2/architecture",
            title="Neuro Architecture Overview",
            markdown_content=text,
            content_hash=expected_hash,
            metadata={"category": "architecture", "version": "2.0"}
        )

        self.assertEqual(doc.url, "https://docs.neuro.local/v2/architecture")
        self.assertEqual(doc.title, "Neuro Architecture Overview")
        self.assertEqual(doc.content_hash, expected_hash)
        self.assertEqual(doc.status_code, 200)
        self.assertIn("category", doc.metadata)
        self.assertTrue(doc.crawled_at.startswith("202"))

    def test_02_async_multi_url_crawl(self):
        """Test 2: Verify DocumentationIngestor multi-URL concurrent crawling."""
        ingestor = DocumentationIngestor(headless=True, max_concurrent=3)

        urls = [
            "https://docs.example.com/api/v1/auth",
            "https://docs.example.com/api/v1/vectors",
            "https://docs.example.com/api/v1/retrieval"
        ]

        docs = ingestor.crawl_urls_sync(urls)
        self.assertEqual(len(docs), 3)

        for doc in docs:
            self.assertIsInstance(doc, CrawledDocument)
            self.assertTrue(doc.url.startswith("https://docs.example.com/"))
            self.assertTrue(len(doc.markdown_content) > 0)
            self.assertEqual(len(doc.content_hash), 64)

    def test_03_markdown_table_and_code_preservation(self):
        """Test 3: Verify HTML table reconstruction and fenced code block extraction."""
        ingestor = DocumentationIngestor()

        # Simulate crawling HTML with table and code block via fallback parser
        raw_html = """
        <html>
        <head><title>API Reference & Endpoints</title></head>
        <body>
            <nav><a href="/home">Home</a></nav>
            <h1>API Specification</h1>
            <p>Here is the list of supported endpoints and latencies:</p>
            <table>
                <tr><th>Endpoint</th><th>Method</th><th>Latency</th></tr>
                <tr><td>/api/search</td><td>POST</td><td>12ms</td></tr>
                <tr><td>/api/embed</td><td>POST</td><td>45ms</td></tr>
            </table>
            <p>Example request script:</p>
            <pre><code class="language-python">import httpx\nresp = httpx.post("http://localhost:8000/api/search", json={"query": "test"})</code></pre>
            <footer>Copyright 2026 Neuro Inc</footer>
        </body>
        </html>
        """

        # Perform parsing test via fallback logic
        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code

        class MockClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            async def get(self, url, *args, **kwargs):
                return MockResponse(text=raw_html, status_code=200)

        # Monkeypatch httpx for deterministic local test
        import httpx
        orig_client = httpx.AsyncClient
        httpx.AsyncClient = MockClient
        try:
            doc = asyncio.run(ingestor._fallback_crawl_document("https://docs.local/api"))
        finally:
            httpx.AsyncClient = orig_client

        # Verify tables preserved as markdown tables
        self.assertIn("| Endpoint | Method | Latency |", doc.markdown_content)
        self.assertIn("| /api/search | POST | 12ms |", doc.markdown_content)
        self.assertEqual(doc.tables_count, 1)

        # Verify fenced code block preserved
        self.assertIn("```python", doc.markdown_content)
        self.assertIn("httpx.post", doc.markdown_content)
        self.assertEqual(doc.code_blocks_count, 1)

        # Verify navigation and footer boilerplate was stripped
        self.assertNotIn("Copyright 2026", doc.markdown_content)

    def test_04_delta_hashing_and_skip_logic(self):
        """Test 4: Verify SHA-256 delta change detection and sync ledger caching."""
        ingestor = DocumentationIngestor()
        url = "https://docs.neuro.local/guide"
        initial_content = "# User Guide\n\nInitial version."
        hash_v1 = hashlib.sha256(initial_content.encode("utf-8")).hexdigest()

        sync_ledger: Dict[str, str] = {}

        # 1. First crawl: Not in ledger -> changed
        self.assertTrue(ingestor.is_content_changed(url, hash_v1, sync_ledger))
        sync_ledger[url] = hash_v1

        # 2. Second crawl with identical content -> unchanged
        self.assertFalse(ingestor.is_content_changed(url, hash_v1, sync_ledger))

        # 3. Third crawl with modified content -> changed
        updated_content = "# User Guide\n\nUpdated version with new vector index configurations."
        hash_v2 = hashlib.sha256(updated_content.encode("utf-8")).hexdigest()
        self.assertTrue(ingestor.is_content_changed(url, hash_v2, sync_ledger))

    def test_05_crawl_to_chunk_pipeline(self):
        """Test 5: Verify feeding CrawledDocument into ProductionChunker and attaching URL metadata."""
        markdown = """# System Requirements
## Operating Systems
Neuro Alexander runs on Windows 10/11, Linux, and macOS.

## Hardware Constraints
Pricing considerations: Free local deployment on NVIDIA GPUs with 8GB VRAM.
"""
        doc = CrawledDocument(
            url="https://docs.neuro.local/requirements",
            title="System Requirements",
            markdown_content=markdown,
            content_hash=hashlib.sha256(markdown.encode()).hexdigest()
        )

        chunks = ProductionChunker.chunk_document(
            text=doc.markdown_content,
            doc_title=doc.title,
            filepath=doc.url
        )

        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertEqual(c.doc_title, "System Requirements")
            self.assertIsNotNone(c.trust_type)
            self.assertIsNotNone(c.intent_type)

    def test_06_end_to_end_crawl_and_qdrant_indexing(self):
        """Test 6: Verify end-to-end crawl -> delta hash -> chunk -> Qdrant vector upsert pipeline."""
        # Initialize isolated in-memory Qdrant vector engine
        qdrant = QdrantVectorEngine(
            location=":memory:",
            collection_name="test_web_crawl_collection",
            vector_dim=128
        )

        ingestor = DocumentationIngestor()
        sync_ledger: Dict[str, str] = {}

        urls = [
            "https://docs.example.com/v1/installation",
            "https://docs.example.com/v1/troubleshooting"
        ]

        # Run pipeline
        res = asyncio.run(
            ingestor.crawl_and_index_pipeline(
                urls=urls,
                qdrant_engine=qdrant,
                sync_ledger=sync_ledger,
                tenant_id="tenant_web_test"
            )
        )

        self.assertEqual(res["total_urls"], 2)
        self.assertEqual(res["indexed_pages"], 2)
        self.assertEqual(res["skipped_pages"], 0)
        self.assertGreater(res["total_chunks_indexed"], 0)
        self.assertEqual(len(sync_ledger), 2)

        # Query Qdrant with tenant filter
        from src.core.embeddings import generate_embedding
        q_vec = generate_embedding("installation instructions")
        hits = qdrant.search_similarity(
            query_vector=q_vec,
            top_k=5,
            tenant_id="tenant_web_test"
        )

        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0].tenant_id, "tenant_web_test")
        self.assertTrue(hits[0].payload.get("filepath", "").startswith("https://docs.example.com/v1/"))

        # Run second pass with unchanged ledger -> should skip 2 pages
        res2 = asyncio.run(
            ingestor.crawl_and_index_pipeline(
                urls=urls,
                qdrant_engine=qdrant,
                sync_ledger=sync_ledger,
                tenant_id="tenant_web_test"
            )
        )
        self.assertEqual(res2["indexed_pages"], 0)
        self.assertEqual(res2["skipped_pages"], 2)
        self.assertEqual(res2["total_chunks_indexed"], 0)


if __name__ == "__main__":
    unittest.main()
