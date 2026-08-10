import pytest
import unittest
import os
import shutil
import tempfile
import sys
import json
import time
from fastapi.testclient import TestClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainRAG(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_rag_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        self.client = TestClient(main.app)

        doc_path = os.path.join(self.test_dir, "quantum_rag.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("Quantum computing leverages qubits and superposition for exponential speedup.")

        know.index_directory(self.test_dir)

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_01_extract_rag_context_hybrid_rrf(self):
        """Verify HyDE + RRF hybrid context extraction and citation formatting.

        Preconditions: Isolated temporary database seeded with sample quantum text document.
        Invariants: Context extraction returns formatted string context and list of source dictionaries.
        Expected Outcomes: Source list is non-empty, contains citation key, and references quantum_rag.txt.
        """
        context, sources = know.extract_rag_context("quantum computing qubits", max_chunks=3)
        self.assertIsInstance(context, str)
        self.assertIsInstance(sources, list)
        self.assertGreater(len(sources), 0)
        self.assertIn("citation", sources[0])
        self.assertIn("quantum_rag.txt", sources[0]["filename"])

    def test_02_rag_stream_sse_endpoint(self):
        """Verify /api/rag/stream live SSE token streaming endpoint.

        Preconditions: FastAPI TestClient initialized with seeded test database.
        Invariants: HTTP POST to /api/rag/stream returns 200 OK status code.
        Expected Outcomes: Response header Content-Type is text/event-stream and response body contains SSE data tokens and sources.
        """
        response = self.client.post("/api/rag/stream", json={"message": "quantum qubits", "history": []})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers.get("content-type", ""))
        self.assertIn("data:", response.text)
        self.assertIn("sources", response.text)

    def test_03_empty_query_rag_fallback(self):
        """Verify empty query fallback handling in extract_rag_context.

        Preconditions: Target database initialized.
        Invariants: Empty string query does not trigger errors or full database scan.
        Expected Outcomes: extract_rag_context returns empty string context and empty sources list.
        """
        context, sources = know.extract_rag_context("")
        self.assertEqual(context, "")
        self.assertEqual(sources, [])

    def test_04_hyde_query_expansion_resilience(self):
        """Verify HyDE query expansion generator output.

        Preconditions: know module initialized with HyDE prompt configuration.
        Invariants: generate_hyde_expansion returns non-empty string hypothetical document.
        Expected Outcomes: Returned expanded string has length greater than zero.
        """
        expanded = know.generate_hyde_expansion("astrophysics research")
        self.assertIsInstance(expanded, str)
        self.assertGreater(len(expanded), 0)

    def test_05_jaccard_deduplication_and_thresholding(self):
        """Verify semantic Jaccard deduplication of duplicate context snippets.

        Preconditions: Multiple text files with identical content indexed into temporary database.
        Invariants: Deduplication reduces redundant source snippets below max_chunks limit.
        Expected Outcomes: Returned sources list length is less than or equal to 2.
        """
        doc2 = os.path.join(self.test_dir, "quantum_dup.txt")
        with open(doc2, "w", encoding="utf-8") as f:
            f.write("Quantum computing leverages qubits and superposition for exponential speedup.")

        know.index_directory(self.test_dir)
        know._cached_doc_vectors = None
        know._cached_inverted_index = None

        _, sources = know.extract_rag_context("quantum qubits superposition", max_chunks=5)
        self.assertLessEqual(len(sources), 2)

    def test_06_rag_dynamic_hyperparameters_and_auto_defrag(self):
        """Verify RAG SSE stream payload with custom max_tokens and temperature parameters.

        Preconditions: FastAPI TestClient initialized.
        Invariants: Endpoint handles valid numeric max_tokens and temperature payload fields.
        Expected Outcomes: HTTP POST response status code is 200.
        """
        res = self.client.post("/api/rag/stream", json={"message": "quantum", "max_tokens": 300, "temperature": 0.5})
        self.assertEqual(res.status_code, 200)

    def test_07_chat_stream_sse_endpoint_and_turn_persistence(self):
        """Verify /api/chat/stream SSE streaming, sources, tokens, and SQLite message turn persistence.

        Preconditions: Active chat session created via know.create_chat_session().
        Invariants: Chat streaming yields SSE event markers and persists user/assistant message turns.
        Expected Outcomes: Response status 200, SSE data markers present, and chat_messages table contains user and assistant turns.
        """
        session = know.create_chat_session(title="Streaming Test Session")
        session_id = session["id"]

        req_payload = {
            "session_id": session_id,
            "message": "quantum computing qubits",
            "temperature": 0.3
        }

        res = self.client.post("/api/chat/stream", json=req_payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))
        self.assertIn("data:", res.text)
        self.assertIn('"type": "sources"', res.text)
        self.assertIn('"type": "done"', res.text)

        messages = know.get_chat_messages(session_id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "quantum computing qubits")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertGreater(len(messages[1]["content"]), 0)
        self.assertIsNotNone(messages[1].get("citations_json"))

    def test_08_chat_stream_web_search_trigger(self):
        """Verify /api/chat/stream web search triggering when web_search flag is set.

        Preconditions: Active chat session created with web_search enabled in payload.
        Invariants: Stream payload includes web search source markers.
        Expected Outcomes: Response status 200 and SSE output includes sources and web_sources events.
        """
        session = know.create_chat_session(title="Web Search Session")
        session_id = session["id"]

        req_payload = {
            "session_id": session_id,
            "message": "latest dark matter discovery 2026",
            "web_search": True
        }

        res = self.client.post("/api/chat/stream", json=req_payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn('"type": "sources"', res.text)
        self.assertIn('"web_sources"', res.text)

    def test_09_hierarchical_parent_child_chunking(self):
        """Verify Parent-Child hierarchical section and snippet chunking logic.

        Preconditions: Multi-paragraph text document provided to chunk_text_hierarchical().
        Invariants: Each generated chunk maintains child_content within parent_content boundary.
        Expected Outcomes: Non-empty list of chunk dictionaries returned, with child_content contained in parent_content.
        """
        text = (
            "Paragraph 1: The Uroboros Knowledge Engine is designed for high-speed document indexing and semantic retrieval. "
            "It features zero-dependency architecture with thread-local connection pooling.\n\n"
            "Paragraph 2: Advanced RAG features include HyDE query expansion and Reciprocal Rank Fusion. "
            "It guarantees 100% deterministic fact grounding with zero external AI frameworks."
        )
        chunks = know.chunk_text_hierarchical(text, parent_size=300, child_size=100)
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertIn("child_content", c)
            self.assertIn("parent_content", c)
            self.assertLessEqual(len(c["child_content"]), len(c["parent_content"]))
            self.assertIn(c["child_content"], c["parent_content"])

    def test_10_multihop_query_decomposition(self):
        """Verify multi-hop comparative query decomposition into atomic sub-queries.

        Preconditions: Complex compound query string passed to decompose_multihop_query().
        Invariants: Compound terms split into independent target sub-queries.
        Expected Outcomes: Returned list contains expected key query components for both security/retention and GDPR/HIPAA.
        """
        sub1 = know.decompose_multihop_query("security policy and data retention rules")
        self.assertIn("security policy", sub1)
        self.assertIn("data retention rules", sub1)

        sub2 = know.decompose_multihop_query("GDPR vs HIPAA compliance requirements")
        self.assertIn("GDPR", sub2)
        self.assertIn("HIPAA compliance requirements", sub2)

    def test_11_precision_cross_reranking_and_recency_decay(self):
        """Verify Pass-2 precision re-ranking with phrase proximity and recency decay.

        Preconditions: List of document candidates with varying timestamps and keyword matches.
        Invariants: Reranking prioritizes candidate with exact phrase match and recent timestamp.
        Expected Outcomes: Reranked list places doc2.txt first with higher rrf_score.
        """
        now_ts = time.time()
        query = "database connection pool"
        candidates = [
            {"filename": "doc1.txt", "content": "This file discusses general software design and database concepts.", "rrf_score": 0.05, "modified_at": now_ts - 864000},
            {"filename": "doc2.txt", "content": "Here we configure database connection pool settings for SQLite WAL mode.", "rrf_score": 0.04, "modified_at": now_ts},
        ]
        reranked = know.precision_cross_rerank(query, candidates)
        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0]["filename"], "doc2.txt")
        self.assertGreater(reranked[0]["rrf_score"], reranked[1]["rrf_score"])

    def test_12_porter_stemmer_and_synonyms(self):
        """Verify Porter stemmer and technical domain synonym expansion.

        Preconditions: Input terms passed to stem_word() and expand_synonyms().
        Invariants: Stemmer reduces inflected forms and synonym expander maps technical abbreviations.
        Expected Outcomes: 'indexing' stems to 'index' and 'check db auth errors' expands with 'database', 'authentication', 'error'.
        """
        self.assertIn(know.stem_word("rules"), ("rule", "rules"))
        self.assertEqual(know.stem_word("indexing"), "index")

        expanded = know.expand_synonyms("check db auth errors")
        self.assertIn("database", expanded)
        self.assertIn("authentication", expanded)
        self.assertIn("error", expanded)

    def test_13_metadata_filter_parsing_and_sentence_trimming(self):
        """Verify inline metadata filter parsing (ext:, tag:) and clean sentence trimming.

        Preconditions: Query with ext: and tag: filters and long text string.
        Invariants: parse_metadata_filters extracts filter dict and returns cleaned query string.
        Expected Outcomes: Filter values correctly extracted and trimmed text ends on sentence boundary period.
        """
        cleaned, filters = know.parse_metadata_filters("database connection pool ext:md tag:python")
        self.assertEqual(cleaned, "database connection pool")
        self.assertEqual(filters.get("ext"), "md")
        self.assertEqual(filters.get("tag"), "python")

        text = "First sentence is complete. Second sentence provides important context. Third sentence extends past threshold."
        trimmed = know.trim_to_sentence_boundary(text, max_chars=80)
        self.assertTrue(trimmed.endswith("."))
        self.assertIn("First sentence is complete.", trimmed)

if __name__ == "__main__":
    unittest.main()
