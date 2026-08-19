import os
import sys
import time
import shutil
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import src.core.config as config
import src.infrastructure.database as db
from src.infrastructure.database import get_db_connection, reset_db_connections
import know
import main
from fastapi.testclient import TestClient


class TestDashboardVerification(unittest.TestCase):
    """Domain test verifying dashboard statistics API matches SQLite DB ground truth."""

    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path("test_sandbox_verif").resolve()
        if cls.sandbox.exists():
            shutil.rmtree(cls.sandbox, ignore_errors=True)
        cls.sandbox.mkdir(exist_ok=True)

        reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = "test_dashboard_verif.db" + suffix
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

        cls.orig_db_file = db.DB_FILE
        cls.orig_know_db_file = getattr(know, "DB_FILE", db.DB_FILE)
        cls.orig_active_dir = config.ACTIVE_DIR
        db.DB_FILE = "test_dashboard_verif.db"
        know.DB_FILE = "test_dashboard_verif.db"
        config.ACTIVE_DIR = str(cls.sandbox)
        know.init_db()

        # Pre-populate database with test data
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags")
            cursor.execute("DELETE FROM auto_rules")
            cursor.execute("DELETE FROM sync_peers")
            cursor.execute("DELETE FROM search_history")
            cursor.execute("DELETE FROM files")

            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (1, "dummy.txt", "dummy.txt", 100, int(time.time()), "astrophysics details", "sha256_dummy")
            )
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "science"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "physics"))
            cursor.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", ("*.pdf", "pdf_rule", 1))
            cursor.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", ("*.docx", "docx_rule", 2))
            cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.100:8000", "Node A"))
            cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.200:8000", "Node B"))
            cursor.execute(
                "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
                ("gravity physics", "keyword", time.time() - 10, 5)
            )
            cursor.execute(
                "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
                ("astrophysics orbit", "semantic", time.time(), 3)
            )
            conn.commit()

        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = "test_dashboard_verif.db" + suffix
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

        if cls.sandbox.exists():
            try:
                shutil.rmtree(cls.sandbox, ignore_errors=True)
            except OSError:
                pass

        db.DB_FILE = cls.orig_db_file
        know.DB_FILE = cls.orig_know_db_file
        config.ACTIVE_DIR = cls.orig_active_dir

    def test_dashboard_stats_api_vs_db(self):
        """Verify GET /api/stats returns accurate entity counts matching SQLite ground truth."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("total_tags", data)
        self.assertIn("total_rules", data)
        self.assertIn("sync_peers", data)

        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
            db_tags = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM auto_rules")
            db_rules = cursor.fetchone()[0] or 0

            cursor.execute("SELECT name, address FROM sync_peers")
            db_peers_list = [{"name": n, "address": a} for n, a in cursor.fetchall()]

        self.assertEqual(data["total_tags"], db_tags)
        self.assertEqual(data["total_rules"], db_rules)
        self.assertEqual(len(data["sync_peers"]), len(db_peers_list))
        self.assertEqual(db_tags, 2)
        self.assertEqual(db_rules, 2)
        self.assertEqual(len(db_peers_list), 2)

        api_peers = sorted(data["sync_peers"], key=lambda x: x["address"])
        db_peers = sorted(db_peers_list, key=lambda x: x["address"])
        self.assertEqual(api_peers, db_peers)


if __name__ == "__main__":
    unittest.main()