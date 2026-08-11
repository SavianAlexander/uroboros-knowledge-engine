import src.core.config as config
import pytest
"""
Playwright E2E Verification Test Suite for Milestone 4:
- View 1 Document Intelligence Panel rendering
- DOM card integrity (#storage-analytics-card, #tag-analytics-card, #search-telemetry-card, #workflow-logs-panel)
- Button clicks: triggerWorkflowTest() and filterSearchByTagPair()
- Canvas rendering
- Zero uncaught browser console errors
"""
import os
import sys
from src.infrastructure.database import get_db_connection
import time
import shutil
import sqlite3
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import know
import main
import uvicorn

PORT = 0
DB_NAME = "test_m4_playwright.db"
SANDBOX_DIR = PROJECT_ROOT / "test_sandbox_m4_playwright"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="error")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class TestM4PlaywrightE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

        (SANDBOX_DIR / "alpha.txt").write_text("Alpha test document content for tag analytics.", encoding="utf-8")
        (SANDBOX_DIR / "beta.md").write_text("# Beta Document\nWikilink test [[alpha.txt]]", encoding="utf-8")

        import src.infrastructure.database as db_infra
        know.reset_db_connections()
        db_infra.reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = str(PROJECT_ROOT / (DB_NAME + suffix))
            if os.path.exists(fpath):
                try:
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in test_e2e_m4_playwright.py: {e}")

        db.DB_FILE = DB_NAME
        db_infra.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(SANDBOX_DIR)
        know.init_db()
        db_infra.init_db()

        now = int(time.time())
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM tags")
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, str(SANDBOX_DIR / "alpha.txt"), "alpha.txt", 100, now, "Alpha content", "sha1", "text/plain")
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256, mime_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (2, str(SANDBOX_DIR / "beta.md"), "beta.md", 200, now, "Beta content [[alpha.txt]]", "sha2", "text/markdown")
            )
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "analytics"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "intelligence"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (2, "analytics"))
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (2, "intelligence"))
            conn.commit()

        cls.server_thread = ServerThread()
        cls.server_thread.start()
        time.sleep(1.5)
        
        global PORT
        PORT = cls.server_thread.server.servers[0].sockets[0].getsockname()[1]
        from src.infrastructure.repositories.workflows import create_workflow_trigger
        create_workflow_trigger(
            name="Test Trigger Rule",
            event_type="document_ingested",
            webhook_url=f"http://127.0.0.1:{PORT}/api/webhook/mock",
            condition_pattern="",
            is_active=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.stop()
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_m4_frontend_analytics_and_buttons(self):
        console_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.on("console", lambda msg: print(f"BROWSER CONSOLE [{msg.type}]: {msg.text}"))
            page.on("pageerror", lambda exc: console_errors.append(str(exc)))
            page.on("response", lambda resp: print(f"HTTP RESPONSE: {resp.status} {resp.url}"))

            import urllib.request
            for _ in range(30):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/health", timeout=1)
                    break
                except Exception:
                    import logging; logging.getLogger(__name__).exception("Swallowed error in test_e2e_m4_playwright.py")
                    time.sleep(0.2)

            page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            page.wait_for_timeout(1000)

            # 1. Verify View 1 (Diagnostics) rendering & DOM Card Integrity
            storage_card = page.locator("#storage-analytics-card")
            tag_card = page.locator("#tag-analytics-card")
            search_card = page.locator("#search-telemetry-card")
            workflow_panel = page.locator("#workflow-logs-panel")

            self.assertTrue(storage_card.is_visible(), "Storage analytics card #storage-analytics-card not visible")
            self.assertTrue(tag_card.is_visible(), "Tag analytics card #tag-analytics-card not visible")
            self.assertTrue(search_card.is_visible(), "Search telemetry card #search-telemetry-card not visible")
            self.assertTrue(workflow_panel.is_visible(), "Workflow logs panel #workflow-logs-panel not visible")

            # 2. Test triggerWorkflowTest() button click
            test_btn = page.locator("#workflow-test-btn")
            self.assertTrue(test_btn.is_visible(), "#workflow-test-btn not visible")
            print("--- EVALUATING WORKFLOW TEST FUNC ---")
            eval_res = page.evaluate("window.triggerWorkflowTest()")
            print("EVAL RES:", eval_res)
            page.wait_for_timeout(8000)

            # Check that workflow table populated
            logs_tbody = page.locator("#workflow-logs-tbody")
            print("LOGS TBODY INNER HTML:", logs_tbody.inner_html())
            self.assertIn("document_ingested", logs_tbody.inner_html())

            # 3. Test filterSearchByTagPair() click
            chips = page.locator(".tag-pair-chip")
            if chips.count() > 0:
                chips.first.click()
                page.wait_for_timeout(500)
                search_val = page.locator("#search-input").input_value()
                self.assertTrue(len(search_val) > 0, "Search input should be populated after tag-pair chip click")

            # 4. Canvas Element Check (Select Graph Category to reveal canvas)
            page.evaluate("if (typeof selectCategory === 'function') { const btn = document.querySelector('[data-category=\"graph\"]'); if (btn) selectCategory(btn); }")
            page.wait_for_timeout(500)
            canvas = page.locator("#concept-graph-canvas")
            self.assertTrue(canvas.is_visible(), "#concept-graph-canvas should be visible")

            browser.close()

        # 5. Verify zero console errors
        critical_errors = [e for e in console_errors if "favicon" not in e and "404" not in e]
        self.assertEqual(len(critical_errors), 0, f"Uncaught browser console errors detected: {critical_errors}")


if __name__ == "__main__":
    unittest.main()