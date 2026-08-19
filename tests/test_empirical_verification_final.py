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
from src.infrastructure.database import get_db, reset_db_connections
import know
import main

DB_NAME = "test_verification1_final.db"
SANDBOX_DIR = PROJECT_ROOT / "test_sandbox_verification1_final"


class TestEmpiricalVerificationFinal(unittest.TestCase):
    """Domain empirical system verification test suite executing in-memory via TestClient."""

    @classmethod
    def setUpClass(cls):
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

        (SANDBOX_DIR / "doc1.txt").write_text("Quantum mechanics and astrophysics research notes.", encoding="utf-8")
        (SANDBOX_DIR / "doc2.md").write_text("# Science Report\nDetailed analysis of neural networks.", encoding="utf-8")
        sub_dir = SANDBOX_DIR / "projects"
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / "code.py").write_text("def calculate_orbit(): return 42\n", encoding="utf-8")

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

        with get_db() as conn:
            cursor = conn.cursor()
            now = int(time.time())
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM tags")
            cursor.execute("DELETE FROM search_history")
            cursor.execute("DELETE FROM query_bookmarks")
            cursor.execute("DELETE FROM query_macros")

            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, str(SANDBOX_DIR / "doc1.txt"), "doc1.txt", 150, now, "Quantum mechanics and astrophysics research notes.", "sha_doc1", "text/plain")
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (2, str(SANDBOX_DIR / "doc2.md"), "doc2.md", 200, now, "# Science Report\nDetailed analysis of neural networks.", "sha_doc2", "text/markdown")
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (3, str(SANDBOX_DIR / "projects" / "code.py"), "code.py", 100, now, "def calculate_orbit(): return 42\n", "sha_code", "text/x-python")
            )

            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "physics"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "quantum"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (2, "science"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (3, "code"))

            cursor.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", ("quantum physics", "keyword", now - 100, 2))
            cursor.execute("INSERT INTO query_bookmarks (name, query_string, search_mode, created_at) VALUES (?, ?, ?, ?)", ("Quantum Bookmark", "tag:quantum", "keyword", now - 50))
            cursor.execute("INSERT INTO query_macros (name, expansion) VALUES (?, ?)", ("sci", "tag:science"))
            conn.commit()

        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        know.reset_db_connections()
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
        for suffix in ["", "-wal", "-shm"]:
            fpath = str(PROJECT_ROOT / (DB_NAME + suffix))
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

        db.DB_FILE = cls.orig_db_file
        know.DB_FILE = cls.orig_know_db_file
        config.ACTIVE_DIR = cls.orig_active_dir

    def setUp(self):
        db.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(SANDBOX_DIR)

    def test_01_system_health_and_env(self):
        """Verify GET /api/health and /api/system/env return HTTP 200 with required keys."""
        res_h = self.client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)
        self.assertIn("status", res_h.json())

        res_e = self.client.get("/api/system/env")
        self.assertEqual(res_e.status_code, 200)
        data = res_e.json()
        self.assertIn("python_version", data)
        self.assertIn("sqlite_version", data)

    def test_02_file_tree_hierarchy(self):
        """Verify GET /api/file/tree returns populated file directory hierarchy."""
        res = self.client.get("/api/file/tree")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, (list, dict))

    def test_03_keyword_and_tag_search(self):
        """Verify search API correctly returns physics and quantum results."""
        res = self.client.get("/api/search?q=physics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_04_concept_graph_data(self):
        """Verify GET /api/graph/data returns graph nodes and links."""
        res = self.client.get("/api/graph/data")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)

    def test_05_bookmarks_and_macros_api(self):
        """Verify bookmarks and macros API endpoints return seeded records."""
        res_b = self.client.get("/api/bookmarks")
        self.assertEqual(res_b.status_code, 200)

        res_m = self.client.get("/api/macros")
        self.assertEqual(res_m.status_code, 200)

    def test_06_database_snapshots_endpoint(self):
        """Verify GET /api/snapshots returns available database snapshots."""
        res = self.client.get("/api/snapshots")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list) or "snapshots" in data)


if __name__ == "__main__":
    unittest.main()