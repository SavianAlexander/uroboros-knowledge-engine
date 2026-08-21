import os
import sys
import json
import shutil
import tempfile
import unittest
import logging
from unittest.mock import patch
from fastapi.testclient import TestClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know
import main
from src.app.routers.rag import classify_adaptive_intent


class TestRAGChatE2EPipeline(unittest.TestCase):
    """
    End-to-End Test Suite for Adaptive RAG Chat Pipeline (Tududi Task #2040):
    - Zero-retrieval adaptive intelligence on greetings and conversational prompts.
    - Grounded domain retrieval with verified citations and SSE token streaming.
    - Structured telemetry log emissions verification.
    - End-to-end verification of both /api/chat/stream and /api/rag/stream endpoints.
    - Intent classification coverage across all adaptive routing modes.
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_rag_e2e_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        self.client = TestClient(main.app)

        # Seed sample documents
        doc_path = os.path.join(self.test_dir, "neural_voice_engine.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(
                "# Neural Voice Engine\n\n"
                "Kokoro-82M ONNX powers real-time neural text-to-speech synthesis in Uroboros with sub-80ms first-chunk audio streaming.\n"
                "SQLite WAL mode ensures multi-reader lock-free high concurrency for knowledge graph indexing."
            )

        doc_code = os.path.join(self.test_dir, "database_pool.py")
        with open(doc_code, "w", encoding="utf-8") as f:
            f.write(
                "def get_wal_connection():\n"
                "    '''Returns high-performance SQLite connection configured with WAL journal mode.'''\n"
                "    import sqlite3\n"
                "    conn = sqlite3.connect('know.db')\n"
                "    conn.execute('PRAGMA journal_mode=WAL;')\n"
                "    return conn\n"
            )

        know.index_directory(self.test_dir)

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_classify_adaptive_intent_modes(self):
        """Verify query intent classification across all 5 adaptive routing modes."""
        self.assertEqual(classify_adaptive_intent("hello"), "GREETING_CONVERSATIONAL")
        self.assertEqual(classify_adaptive_intent("hi"), "GREETING_CONVERSATIONAL")
        self.assertEqual(classify_adaptive_intent("how does this work?"), "GREETING_CONVERSATIONAL")
        self.assertEqual(classify_adaptive_intent("good morning Uroboros"), "GREETING_CONVERSATIONAL")

        self.assertEqual(classify_adaptive_intent("def parse_tree_ast(): import ast"), "TECHNICAL_CODE")
        self.assertEqual(classify_adaptive_intent("how do I fix this python error in react frontend?"), "TECHNICAL_CODE")

        self.assertEqual(classify_adaptive_intent("calculate quarterly revenue margin percentage"), "MATHEMATICAL_ANALYTIC")
        self.assertEqual(classify_adaptive_intent("what is the standard deviation and math formula?"), "MATHEMATICAL_ANALYTIC")

        self.assertEqual(classify_adaptive_intent("what is the statutory compliance requirement under 17 CFR?"), "LEGAL_STATUTORY")
        self.assertEqual(classify_adaptive_intent("explain the regulatory liability clause"), "LEGAL_STATUTORY")

        self.assertEqual(classify_adaptive_intent("quantum computing superposition qubits"), "GENERAL_RAG")

    def test_02_zero_retrieval_greeting_adaptive_intelligence_chat_stream(self):
        """Verify zero-retrieval greeting returns adaptive assistant response without errors."""
        res = self.client.post("/api/chat/stream", json={"message": "hello"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))

        lines = res.text.strip().split("\n")
        sources_found = False
        tokens = []
        done_found = False

        for line in lines:
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                if payload.get("type") == "sources":
                    sources_found = True
                    self.assertEqual(payload.get("intent"), "GREETING_CONVERSATIONAL")
                elif payload.get("type") == "token":
                    tokens.append(payload.get("content", ""))
                elif payload.get("type") == "done":
                    done_found = True
                    self.assertEqual(payload.get("intent"), "GREETING_CONVERSATIONAL")

        self.assertTrue(sources_found)
        self.assertTrue(done_found)
        full_text = "".join(tokens)
        self.assertTrue(len(full_text.strip()) > 0)

    def test_03_domain_query_grounded_retrieval_and_citations(self):
        """Verify domain query against indexed vault data returns grounded citations and tokens."""
        res = self.client.post("/api/chat/stream", json={"message": "Kokoro-82M ONNX voice synthesis"})
        self.assertEqual(res.status_code, 200)

        lines = res.text.strip().split("\n")
        sources_payload = None
        tokens = []
        done_payload = None

        for line in lines:
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                if payload.get("type") == "sources":
                    sources_payload = payload
                elif payload.get("type") == "token":
                    tokens.append(payload.get("content", ""))
                elif payload.get("type") == "done":
                    done_payload = payload

        self.assertIsNotNone(sources_payload)
        citations = sources_payload.get("sources") or sources_payload.get("local_citations", [])
        self.assertGreater(len(citations), 0)
        self.assertTrue(any("neural_voice_engine.md" in c.get("filename", "") for c in citations))

        full_text = "".join(tokens)
        self.assertGreater(len(full_text), 10)
        self.assertIsNotNone(done_payload)
        self.assertGreater(done_payload.get("tokens_generated", 0), 0)

    def test_04_structured_telemetry_logging_emission(self):
        """Verify explicit structured telemetry log output on RAG execution."""
        with self.assertLogs("src.app.routers.rag", level="INFO") as log_capture:
            res = self.client.post("/api/chat/stream", json={"message": "How does SQLite WAL mode work?"})
            self.assertEqual(res.status_code, 200)

            log_output = "\n".join(log_capture.output)
            self.assertIn("RAG Execution | query='How does SQLite WAL mode work?'", log_output)
            self.assertIn("primary_mode=", log_output)
            self.assertIn("retrieved_chunk_count=", log_output)
            self.assertIn("final_prompt_len=", log_output)
            self.assertIn("Final Prompt:", log_output)

    def test_05_rag_stream_and_rag_query_endpoint_parity(self):
        """Verify parity between /api/rag/stream and /api/rag/query using unified DAG engine."""
        for ep in ["/api/rag/stream", "/api/rag/query"]:
            res = self.client.post(ep, json={"query": "hello"})
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/event-stream", res.headers.get("content-type", ""))

            lines = res.text.strip().split("\n")
            has_sources = False
            has_done = False
            for line in lines:
                if line.startswith("data: "):
                    payload = json.loads(line[6:])
                    if payload.get("type") == "sources":
                        has_sources = True
                    elif payload.get("type") == "done":
                        has_done = True
            self.assertTrue(has_sources, f"Missing sources in {ep}")
            self.assertTrue(has_done, f"Missing done in {ep}")

    def test_06_empty_query_validation(self):
        """Verify empty query returns HTTP 422 validation error."""
        res = self.client.post("/api/chat/stream", json={"message": "   "})
        self.assertEqual(res.status_code, 422)

        res_rag = self.client.post("/api/rag/stream", json={"query": ""})
        self.assertEqual(res_rag.status_code, 422)


if __name__ == "__main__":
    unittest.main()
