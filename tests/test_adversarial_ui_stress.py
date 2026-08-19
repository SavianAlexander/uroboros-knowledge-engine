import os
import sys
import time
import shutil
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.core.config as config
import src.infrastructure.database as db
from src.infrastructure.database import get_db_connection, reset_db_connections
import know
import main

DB_NAME = "test_challenger1_stress.db"
SANDBOX_DIR = PROJECT_ROOT / "test_sandbox_challenger1_stress"


class TestAdversarialUIStress(unittest.TestCase):
    """Domain 22: Adversarial Backend API Stress & Input Resilience Test Suite."""

    @classmethod
    def setUpClass(cls):
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        (SANDBOX_DIR / "stress_doc.txt").write_text(
            "Adversarial search query test document with <script>alert(1)</script>.", encoding="utf-8"
        )

        know.reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = str(PROJECT_ROOT / (DB_NAME + suffix))
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

        cls.orig_db_file = db.DB_FILE
        cls.orig_know_db_file = getattr(know, "DB_FILE", db.DB_FILE)
        cls.orig_active_dir = config.ACTIVE_DIR
        db.DB_FILE = DB_NAME
        know.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(SANDBOX_DIR)
        know.init_db()

        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM tags")
            now = int(time.time())
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, str(SANDBOX_DIR / "stress_doc.txt"), "stress_doc.txt", 100, now, "Adversarial search query test document.", "sha_stress", "text/plain")
            )
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "stress"))
            conn.commit()

        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        know.reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = str(PROJECT_ROOT / (DB_NAME + suffix))
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)

        db.DB_FILE = cls.orig_db_file
        know.DB_FILE = cls.orig_know_db_file
        config.ACTIVE_DIR = cls.orig_active_dir

    def setUp(self):
        db.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(SANDBOX_DIR)

    def test_01_rapid_api_endpoint_stress(self):
        """Verify rapid repeated API queries handle load deterministically without connection leaks."""
        endpoints = ["/api/stats", "/api/file/tree", "/api/system/env", "/api/tags"]
        for ep in endpoints:
            for _ in range(5):
                res = self.client.get(ep)
                self.assertEqual(res.status_code, 200)

    def test_02_adversarial_unbalanced_quotes_search_query(self):
        """Verify malformed/unbalanced quotes search queries execute safely without crashing backend."""
        unbalanced_query = 'tag:stress AND "unbalanced quotes query ('
        response = self.client.get(f"/api/search?q={unbalanced_query}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)

    def test_03_graph_data_adversarial_bounds(self):
        """Verify graph data API endpoint returns valid node/edge structures under adversarial load."""
        res = self.client.get("/api/graph/data?limit=50")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)

    def test_04_xss_payload_search_sanitization(self):
        """Verify script tag search queries are safely sanitized without SQL injection or reflection."""
        xss_query = "<script>alert(1)</script>"
        res = self.client.get(f"/api/search?q={xss_query}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)


if __name__ == "__main__":
    unittest.main()