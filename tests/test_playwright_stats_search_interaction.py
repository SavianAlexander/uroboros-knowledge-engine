import os
import sys
import time
import sqlite3
import threading
import shutil
import tempfile
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

DB_NAME = os.path.join(tempfile.gettempdir(), "test_verification_2.db")


class TestAdversarialVerification2(unittest.TestCase):
    """Domain 23: Direct SQLite vs REST API Stats Verification Suite."""

    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path(tempfile.mkdtemp(prefix="test_sandbox_verification_2_")).resolve()
        db.DB_FILE = DB_NAME
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = DB_NAME + suffix
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

        config.ACTIVE_DIR = str(cls.sandbox)
        know.init_db()

        with get_db_connection(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags")
            cursor.execute("DELETE FROM auto_rules")
            cursor.execute("DELETE FROM sync_peers")
            cursor.execute("DELETE FROM search_history")
            cursor.execute("DELETE FROM files")

            cursor.execute(
                "INSERT INTO files (filepath, filename, file_size, mime_type, sha256) VALUES (?, ?, ?, ?, ?)",
                ("test_sandbox_verification_2/file1.txt", "file1.txt", 100, "text/plain", "sha1")
            )
            file_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO files (filepath, filename, file_size, mime_type, sha256) VALUES (?, ?, ?, ?, ?)",
                ("test_sandbox_verification_2/file2.txt", "file2.txt", 200, "text/plain", "sha2")
            )

            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (file_id, "tag1"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (file_id, "tag2"))

            cursor.execute("INSERT INTO auto_rules (pattern, tag) VALUES (?, ?)", ("*python*", "programming"))
            cursor.execute("INSERT INTO auto_rules (pattern, tag) VALUES (?, ?)", ("*rust*", "rustlang"))
            cursor.execute("INSERT INTO auto_rules (pattern, tag) VALUES (?, ?)", ("*c++*", "cpp"))

            cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.50:8000", "Peer A"))
            cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.60:8000", "Peer B"))

            cursor.execute(
                "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
                ("quantum mechanics", "semantic", time.time(), 3)
            )
            cursor.execute(
                "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
                ("astrophysics gravity", "keyword", time.time() - 100, 5)
            )
            conn.commit()

        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = DB_NAME + suffix
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

        if cls.sandbox.exists():
            try:
                shutil.rmtree(cls.sandbox, ignore_errors=True)
            except OSError:
                pass

    def setUp(self):
        db.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(self.sandbox)

    def test_01_api_stats_against_db(self):
        """
        Preconditions: Seeded database with tags, rules, peers, and history.
        Invariants: GET /api/stats must return aggregate metrics exactly matching direct SQLite queries.
        Outcomes: total_tags, total_rules, and sync_peers JSON payloads match database contents.
        """
        db.DB_FILE = DB_NAME
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("total_tags", data)
        self.assertIn("total_rules", data)
        self.assertIn("sync_peers", data)

        with get_db_connection(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
            db_tags_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM auto_rules")
            db_rules_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT name, address FROM sync_peers")
            db_peers = [{"name": row["name"], "address": row["address"]} for row in cursor.fetchall()]
            db_peers_count = len(db_peers)

        self.assertEqual(data["total_tags"], db_tags_count)
        self.assertEqual(data["total_rules"], db_rules_count)
        self.assertEqual(len(data["sync_peers"]), db_peers_count)

        api_peers = data["sync_peers"]
        for db_peer in db_peers:
            matched = any(
                api_peer["address"] == db_peer["address"] and api_peer["name"] == db_peer["name"]
                for api_peer in api_peers
            )
            self.assertTrue(matched, f"Peer {db_peer} not found in API response {api_peers}")


if __name__ == "__main__":
    unittest.main()