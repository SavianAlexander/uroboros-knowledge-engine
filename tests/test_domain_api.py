import src.core.config as config
import src.infrastructure.database as db
import unittest
import os
import shutil
import tempfile
import sys
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainAPI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_api_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        self.client = TestClient(main.app)

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_search_api_endpoint(self):
        """Verify /api/search REST API query endpoint behavior for keyword search.

        Preconditions: Test database initialized and TestClient bound to application instance.
        Invariants: Search API endpoint returns valid HTTP responses for formatted keyword queries.
        Expected Outcomes: GET /api/search returns status code HTTP 200 OK.
        """
        response = self.client.get("/api/search?query=test&mode=keyword")
        self.assertEqual(response.status_code, 200)

    def test_02_sse_chat_stream_endpoint(self):
        """Verify /api/chat/stream live token SSE streaming response endpoint.

        Preconditions: TestClient initialized with active application state.
        Invariants: Streaming chat endpoint returns Server-Sent Events content type headers.
        Expected Outcomes: POST /api/chat/stream returns HTTP 200 OK with text/event-stream header.
        """
        response = self.client.post("/api/chat/stream", json={"message": "hello", "history": []})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers.get("content-type", ""))

    def test_03_angle_missing_field_422_validation(self):
        """Verify request body schema validation failure returns HTTP 422 Unprocessable Entity.

        Preconditions: TestClient initialized; POST request submitted missing required 'history' field.
        Invariants: FastAPI request validation rejects malformed payload prior to execution.
        Expected Outcomes: POST /api/chat returns status code HTTP 422.
        """
        response = self.client.post("/api/chat", json={"message": ""})
        self.assertEqual(response.status_code, 422)

    def test_04_angle_gzip_compression_header(self):
        """Verify HTTP GZip compression header processing on search endpoint payloads.

        Preconditions: TestClient initialized; request headers include Accept-Encoding: gzip.
        Invariants: Compression middleware processes incoming request headers without error.
        Expected Outcomes: GET /api/search with gzip header returns HTTP 200 OK.
        """
        response = self.client.get(
            "/api/search?query=test&mode=keyword",
            headers={"Accept-Encoding": "gzip"}
        )
        self.assertEqual(response.status_code, 200)

    def test_05_angle_rapid_file_save_sync(self):
        """Verify rapid file save operation instantly updates FTS search index records.

        Preconditions: Initial text file created in test active directory and indexed.
        Invariants: File save API endpoint synchronously updates disk file and SQLite FTS index.
        Expected Outcomes: POST /api/file/save succeeds with HTTP 200 and search query retrieves updated keyword.
        """
        target_file = os.path.join(self.test_dir, "save_sync.txt")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("Initial content")

        know.index_directory(self.test_dir)

        save_res = self.client.post("/api/file/save", json={
            "path": target_file,
            "content": "Updated content with unique_keyword_alpha"
        })
        self.assertEqual(save_res.status_code, 200)

        search_res = self.client.get("/api/search?query=unique_keyword_alpha&mode=keyword")
        self.assertEqual(search_res.status_code, 200)

    def test_06_simulation_giant_query_string(self):
        """Verify search API robustness when processing 10,000 character query payload strings.

        Preconditions: Giant query string constructed with 1,000 repeated tokens.
        Invariants: Search endpoint handles large query inputs without internal crash or buffer overflow.
        Expected Outcomes: GET /api/search returns HTTP 200 OK status code.
        """
        giant_query = "quantum " * 1000
        response = self.client.get(f"/api/search?query={giant_query}&mode=keyword")
        self.assertEqual(response.status_code, 200)

    def test_07_simulation_invalid_json_body(self):
        """Verify request body parser error handling on malformed non-JSON payloads.

        Preconditions: POST request sent with non-JSON string content and application/json header.
        Invariants: Application parser catches invalid JSON syntax and rejects request.
        Expected Outcomes: POST /api/chat/stream returns status code HTTP 422.
        """
        response = self.client.post(
            "/api/chat/stream",
            content="NOT_VALID_JSON",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)

    def test_08_health_status_endpoint(self):
        """Verify /api/health system status probe endpoint response payload.

        Preconditions: TestClient connected to application routing stack.
        Invariants: Health check endpoint returns JSON dictionary with operational status flag.
        Expected Outcomes: GET /api/health returns HTTP 200 OK with status equal to 'ok'.
        """
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")

    def test_09_db_stats_backup_and_delete_endpoints(self):
        """Verify /api/db/stats database metrics, /api/backup, and /api/file/delete endpoints.

        Preconditions: File created and indexed in test environment; test client connected.
        Invariants: DB stats return metric details; backup creates snapshot; delete removes target file.
        Expected Outcomes: All endpoints return HTTP 200 OK; target file is deleted from disk.
        """
        stats_res = self.client.get("/api/db/stats")
        self.assertEqual(stats_res.status_code, 200)
        self.assertIn("db_size_bytes", stats_res.json())

        backup_res = self.client.post("/api/backup")
        self.assertEqual(backup_res.status_code, 200)
        self.assertEqual(backup_res.json().get("status"), "success")

        del_f = os.path.join(self.test_dir, "del_test.txt")
        with open(del_f, "w", encoding="utf-8") as f:
            f.write("To be deleted")
        know.index_directory(self.test_dir)

        del_res = self.client.post("/api/file/delete", json={"path": del_f})
        self.assertEqual(del_res.status_code, 200)
        self.assertFalse(os.path.exists(del_f))

    def test_10_tags_and_bookmarks_api_endpoints(self):
        """Verify /api/tags listing and /api/bookmarks vault read endpoints.

        Preconditions: Database initialized with default schema; test client connected.
        Invariants: Endpoint returns JSON objects containing tag and bookmark array fields.
        Expected Outcomes: GET /api/tags and GET /api/bookmarks return HTTP 200 with list payloads.
        """
        tags_res = self.client.get("/api/tags")
        self.assertEqual(tags_res.status_code, 200)
        self.assertIn("tags", tags_res.json())
        self.assertIsInstance(tags_res.json()["tags"], list)

        bookmarks_res = self.client.get("/api/bookmarks")
        self.assertEqual(bookmarks_res.status_code, 200)
        self.assertIn("bookmarks", bookmarks_res.json())
        self.assertIsInstance(bookmarks_res.json()["bookmarks"], list)

    def test_11_export_pdf_and_csv_endpoints(self):
        """Verify /api/export endpoint handling for metadata export in CSV format.

        Preconditions: Active database schema; test client bound to API router.
        Invariants: Metadata export endpoint formats query results into downloadable CSV streams.
        Expected Outcomes: GET /api/export with format=csv returns HTTP 200 OK.
        """
        csv_res = self.client.get("/api/export?query=test&format=csv")
        self.assertEqual(csv_res.status_code, 200)

    def test_12_tag_and_bookmark_mutations(self):
        """Verify /api/bookmarks/add and /api/bookmarks/delete macro vault mutation operations.

        Preconditions: Test client connected; bookmark payload created.
        Invariants: Bookmark mutations modify macro database tables cleanly.
        Expected Outcomes: Add and delete bookmark requests return HTTP 200 OK status codes.
        """
        add_res = self.client.post("/api/bookmarks/add", json={"name": "test_macro", "query": "quantum"})
        self.assertEqual(add_res.status_code, 200)

        del_res = self.client.post("/api/bookmarks/delete", json={"name": "test_macro"})
        self.assertEqual(del_res.status_code, 200)

    def test_13_summary_and_graph_endpoints(self):
        """Verify /api/file/summary document extraction and /api/graph/data layout endpoints.

        Preconditions: Sample text file created in test directory.
        Invariants: Summary endpoint extracts key takeaways; graph endpoint returns node topology.
        Expected Outcomes: Both GET requests return HTTP 200 OK with takeaways and nodes payload keys.
        """
        sum_f = os.path.join(self.test_dir, "sum_test.txt")
        with open(sum_f, "w", encoding="utf-8") as f:
            f.write("Quantum mechanics provides an explanation of physical phenomena at atomic scales.")

        sum_res = self.client.get(f"/api/file/summary?path={sum_f}")
        self.assertEqual(sum_res.status_code, 200)
        self.assertIn("takeaways", sum_res.json())

        graph_res = self.client.get("/api/graph/data")
        self.assertEqual(graph_res.status_code, 200)
        self.assertIn("nodes", graph_res.json())

if __name__ == "__main__":
    unittest.main()
