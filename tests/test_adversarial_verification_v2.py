import src.core.config as config
import src.infrastructure.database as db
import pytest
"""
Domain 23: Playwright UI Verification Test Suite 2.
Validates /api/stats accuracy against direct SQLite queries and verifies recent search click behaviors in Playwright UI.
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import sqlite3
import threading
import shutil
import tempfile
import unittest
import urllib.request
from pathlib import Path
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know
import main
import uvicorn

PORT = 8092
DB_NAME = os.path.join(tempfile.gettempdir(), "test_verification_2.db")


class ServerThread(threading.Thread):
    def __init__(self, port=PORT):
        super().__init__()
        self.daemon = True
        self.port = port
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=self.port, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class TestAdversarialVerification2(unittest.TestCase):
    port = PORT

    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path(tempfile.mkdtemp(prefix="test_sandbox_verification_2_")).resolve()
        db.DB_FILE = DB_NAME
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = DB_NAME + suffix
            if os.path.exists(fpath):
                try:
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in test_adversarial_verification_2.py: {e}")

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

        cls.server = None
        cls.port = PORT

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.stop()
            cls.server.join(timeout=5.0)
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = DB_NAME + suffix
            if os.path.exists(fpath):
                for _ in range(10):
                    try:
                        try:
                            from src.infrastructure.database import reset_db_connections
                            reset_db_connections()
                        except Exception: pass
                        os.remove(fpath)
                        break
                    except Exception:
                        threading.Event().wait(0.05)

        if cls.sandbox.exists():
            for _ in range(10):
                try:
                    shutil.rmtree(cls.sandbox)
                    break
                except Exception:
                    import logging; logging.getLogger(__name__).exception("Swallowed error in test_adversarial_verification_2.py")
                    threading.Event().wait(0.05)

    def setUp(self):
        db.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(self.sandbox)

    def tearDown(self):
        pass

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_01_api_stats_against_db(self):
        """
        Preconditions: Seeded database with tags, rules, peers, and history.
        Invariants: GET /api/stats must return aggregate metrics exactly matching direct SQLite queries.
        Outcomes: total_tags, total_rules, and sync_peers JSON payloads match database contents.
        """
        db.DB_FILE = DB_NAME
        client = TestClient(main.app)
        
        response = client.get("/api/stats")
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
            db_peers = [dict(sqlite3.Row(cursor, row)) for row in cursor.fetchall()]
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

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_02_recent_searches_click_behavior(self):
        """
        Preconditions: Active uvicorn server with seeded search history.
        Invariants: Clicking a recent search timeline row in Playwright UI triggers query filling, tab focusing, and search execution.
        Outcomes: Search input populates with query string, active tab switches to 'explorer', and search results/metrics panel displays.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.wait_for_selector("#recent-searches-list", timeout=5000)
            
            active_tab_btn = page.locator(".tab-link.active")
            self.assertEqual(active_tab_btn.get_attribute("data-tab"), "diagnostics")
            
            recent_item = page.locator("#recent-searches-list .timeline-row").first
            recent_item.wait_for(state="visible")
            
            query_text_el = recent_item.locator("span")
            query_text = query_text_el.inner_text()
            self.assertIn(query_text, ["quantum mechanics", "astrophysics gravity"])
            
            badge_text = recent_item.locator(".badge").inner_text()
            expected_mode = "semantic" if "semantic" in badge_text else "keyword"
            
            recent_item.click()
            
            search_input = page.locator("#search-input")
            self.assertEqual(search_input.input_value(), query_text)
            
            active_tab_btn = page.locator(".tab-link.active")
            self.assertEqual(active_tab_btn.get_attribute("data-tab"), "explorer")
            
            if expected_mode == "semantic":
                self.assertIn("active", page.locator("#mode-semantic").get_attribute("class"))
            else:
                self.assertIn("active", page.locator("#mode-keyword").get_attribute("class"))
                
            metrics_panel = page.locator("#search-metrics-panel")
            metrics_panel.wait_for(state="visible", timeout=3000)
            self.assertTrue(page.is_visible("#search-metrics-panel"))
            
            browser.close()


if __name__ == "__main__":
    unittest.main()