"""
Unit & Integration Test Suite for Milestone 1 Document Intelligence Analytics Engine and REST API.
"""

import os
import sys
import time
import tempfile
import sqlite3
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import know
from src.app.server import app
from src.infrastructure.database import init_db
from src.domain.analytics_engine import (
    get_indexing_overview,
    get_storage_breakdown,
    get_tag_distribution,
    get_search_activity,
    clear_analytics_cache
)


class TestDomainAnalyticsIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        clear_analytics_cache()
        self.tmp_db_fd, self.tmp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_db_fd)

        self.orig_db_file = know.DB_FILE
        know.DB_FILE = self.tmp_db_path
        init_db()

    def tearDown(self):
        know.DB_FILE = self.orig_db_file
        clear_analytics_cache()
        if os.path.exists(self.tmp_db_path):
            try:
                os.remove(self.tmp_db_path)
            except OSError:
                pass

    def test_01_zero_state_resilience(self):
        """
        Preconditions: Uninitialized database or tables containing zero document records.
        Invariants: Analytics calculations return zeroed metric schemas without throwing divide-by-zero or missing field errors.
        Outcomes: Verifies fallback handling for overview, storage, tag distribution, and search activity analytics.
        """
        overview = get_indexing_overview(self.tmp_db_path)
        self.assertEqual(overview.total_documents, 0)
        self.assertEqual(overview.total_chunks, 0)
        self.assertEqual(overview.fts_records, 0)
        self.assertEqual(overview.storage_total_bytes, 0)
        self.assertEqual(overview.indexing_status, "idle")

        storage = get_storage_breakdown(self.tmp_db_path)
        self.assertEqual(storage.by_mime, {})
        self.assertEqual(storage.by_extension, {})
        self.assertEqual(storage.top_directories, [])

        tags = get_tag_distribution(self.tmp_db_path)
        self.assertEqual(tags.total_tags, 0)
        self.assertEqual(tags.top_tags, [])
        self.assertEqual(tags.tag_cooccurrence, [])

        activity = get_search_activity(self.tmp_db_path)
        self.assertEqual(activity.total_queries, 0)
        self.assertEqual(activity.top_queries, [])
        self.assertEqual(activity.recent_queries, [])

    def test_02_analytics_with_populated_data(self):
        """
        Preconditions: Database seeded with files, file_chunks, fts_files, tags, and search history.
        Invariants: Calculated metrics aggregate file counts, total storage bytes, tag distribution, and query counts accurately.
        Outcomes: Verifies metrics calculation against populated SQLite database state.
        """
        with sqlite3.connect(self.tmp_db_path) as conn:
            conn.execute(
                "INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                ("/vault/docs/spec.pdf", "spec.pdf", 2048, "application/pdf")
            )
            conn.execute(
                "INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                ("/vault/docs/data.csv", "data.csv", 1024, "text/csv")
            )
            conn.execute(
                "INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                ("/vault/code/main.py", "main.py", 512, "text/x-python")
            )
            conn.execute("INSERT INTO file_chunks (file_id, chunk_index, content) VALUES (1, 0, 'chunk content 1')")
            conn.execute("INSERT INTO file_chunks (file_id, chunk_index, content) VALUES (1, 1, 'chunk content 2')")
            conn.execute("INSERT INTO fts_files (filepath, filename, content) VALUES ('/vault/docs/spec.pdf', 'spec.pdf', 'content')")

            conn.execute("INSERT INTO tags (file_id, tag) VALUES (1, 'pdf')")
            conn.execute("INSERT INTO tags (file_id, tag) VALUES (1, 'important')")
            conn.execute("INSERT INTO tags (file_id, tag) VALUES (2, 'csv')")
            conn.execute("INSERT INTO tags (file_id, tag) VALUES (2, 'important')")

            now = time.time()
            conn.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", ("python", "fts", now, 3))
            conn.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", ("python", "fts", now, 3))
            conn.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", ("pdf", "keyword", now, 1))
            conn.commit()

        clear_analytics_cache()

        overview = get_indexing_overview(self.tmp_db_path)
        self.assertEqual(overview.total_documents, 3)
        self.assertEqual(overview.total_chunks, 2)
        self.assertEqual(overview.fts_records, 1)
        self.assertEqual(overview.storage_total_bytes, 3584)

        storage = get_storage_breakdown(self.tmp_db_path)
        self.assertEqual(storage.by_mime["application/pdf"], 1)
        self.assertEqual(storage.by_mime["text/csv"], 1)
        self.assertEqual(storage.by_extension[".pdf"], 1)
        self.assertEqual(storage.by_extension[".csv"], 1)
        self.assertGreater(len(storage.top_directories), 0)

        tags = get_tag_distribution(self.tmp_db_path)
        self.assertEqual(tags.total_tags, 3)
        self.assertGreater(len(tags.top_tags), 0)
        self.assertGreater(len(tags.tag_cooccurrence), 0)

        activity = get_search_activity(self.tmp_db_path)
        self.assertEqual(activity.total_queries, 3)
        self.assertEqual(activity.top_queries[0]["query"], "python")
        self.assertEqual(activity.top_queries[0]["count"], 2)

    def test_03_fastapi_rest_endpoints(self):
        """
        Preconditions: FastAPI server instance mounted on TestClient.
        Invariants: Analytics endpoints return HTTP 200 responses with valid JSON data structures.
        Outcomes: Verifies overview, storage, tags, and search activity GET routes.
        """
        res = self.client.get("/api/analytics/overview")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_documents", data)
        self.assertIn("storage_total_bytes", data)

        res = self.client.get("/api/analytics/storage")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("by_mime", data)
        self.assertIn("top_directories", data)

        res = self.client.get("/api/analytics/tags")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_tags", data)
        self.assertIn("tag_cooccurrence", data)

        res = self.client.get("/api/analytics/search-activity")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_queries", data)
        self.assertIn("top_queries", data)

    def test_04_latency_under_50ms(self):
        """
        Preconditions: Active database and TestClient connection.
        Invariants: Response execution latency across all analytics endpoints remains strictly under 50.0ms threshold.
        Outcomes: Verifies sub-50ms execution SLA for all analytics API endpoints.
        """
        endpoints = [
            "/api/analytics/overview",
            "/api/analytics/storage",
            "/api/analytics/tags",
            "/api/analytics/search-activity"
        ]
        for ep in endpoints:
            t0 = time.time()
            res = self.client.get(ep)
            elapsed_ms = (time.time() - t0) * 1000.0
            self.assertEqual(res.status_code, 200)
            self.assertLess(elapsed_ms, 50.0, f"Endpoint {ep} latency {elapsed_ms:.2f}ms exceeded 50ms threshold")


if __name__ == "__main__":
    unittest.main()
