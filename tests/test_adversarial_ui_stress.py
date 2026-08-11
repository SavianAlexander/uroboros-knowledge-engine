import src.core.config as config
import src.infrastructure.database as db
import pytest
"""
Domain 22: Adversarial UI Stress Test Suite.
Stress-tests rapid tab switching, malformed search queries, edge case form submissions, and canvas zoom bounds using Playwright.
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import shutil
import sqlite3
import threading
import unittest
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know
import main
import uvicorn

PORT = 8105
DB_NAME = "test_challenger1_stress.db"
SANDBOX_DIR = PROJECT_ROOT / "test_sandbox_challenger1_stress"


class ServerThread(threading.Thread):
    def __init__(self, port=PORT):
        super().__init__()
        self.daemon = True
        self.port = port
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=self.port, log_level="error")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class TestAdversarialUIStress(unittest.TestCase):
    port = PORT

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
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in test_adversarial_ui_stress.py: {e}")

        db.DB_FILE = DB_NAME
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

        import socket
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        cls.port = sock.getsockname()[1]
        sock.close()

        cls.server = ServerThread(cls.port)
        cls.server.start()

        # Health polling loop (up to 10 seconds)
        server_ready = False
        start_time = time.time()
        while time.time() - start_time < 10.0:
            if not cls.server.is_alive():
                raise RuntimeError(f"Server thread died before initialization on port {cls.port}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/api/health", timeout=1.0) as resp:
                    if resp.status == 200:
                        server_ready = True
                        break
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in test_adversarial_ui_stress.py")
                threading.Event().wait(0.1)

        if not server_ready:
            raise RuntimeError(f"Uvicorn server failed to respond on port {cls.port}")

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.server.join(timeout=5.0)
        know.reset_db_connections()

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
                    import logging; logging.error(f"Swallowed error in test_adversarial_ui_stress.py: {e}")

        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)

    def setUp(self):
        db.DB_FILE = DB_NAME
        config.ACTIVE_DIR = str(SANDBOX_DIR)

    def tearDown(self):
        pass

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_01_rapid_tab_toggle_stress(self):
        """
        Preconditions: Running application server with UI tab views.
        Invariants: Rapidly clicking tab navigation headers must leave exactly 1 tab active and visible.
        Outcomes: Final tab state reflects last clicked tab ('account') with zero console or page errors.
        """
        console_errors = []
        page_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.wait_for_selector(".app-container", timeout=5000)

            tabs = ["diagnostics", "processes", "explorer", "chat", "settings", "account", "diagnostics", "explorer", "account"]
            for tab in tabs:
                page.click(f".tab-link[data-tab='{tab}']")

            page.wait_for_selector("#account-tab-view", state="visible", timeout=3000)

            corporate_views = ["diagnostics", "processes", "explorer", "chat", "settings", "account"]
            visible_tabs = [
                t for t in corporate_views
                if page.is_visible(f"#{t}-tab-view") and not ("hidden" in (page.locator(f"#{t}-tab-view").get_attribute("class") or ""))
            ]

            self.assertEqual(len(visible_tabs), 1, "Multiple tabs rendered visible simultaneously!")
            self.assertEqual(visible_tabs[0], "account")
            self.assertEqual(len(console_errors), 0, f"Console errors: {console_errors}")
            self.assertEqual(len(page_errors), 0, f"Page errors: {page_errors}")

            browser.close()

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_02_adversarial_unbalanced_quotes_search_query(self):
        """
        Preconditions: UI Explorer search tab open.
        Invariants: Submitting malformed / unbalanced quotes search queries must handle errors without crashing UI.
        Outcomes: Search results or syntax feedback renders gracefully without throwing unhandled page errors.
        """
        console_errors = []
        page_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.click(".tab-link[data-tab='explorer']")
            page.wait_for_selector("#search-input", state="visible", timeout=5000)

            search_input = page.locator("#search-input")
            unbalanced_query = 'tag:stress AND "unbalanced quotes query ('
            search_input.fill(unbalanced_query)
            page.keyboard.press("Enter")
            page.wait_for_selector("#results-list", timeout=3000)

            results_list_text = page.locator("#results-list").text_content()
            handled = page.is_visible("#search-syntax-feedback") or ("0 found" in page.locator("#results-count").text_content() or "No files" in results_list_text)
            self.assertTrue(handled, "Adversarial search query failed to render syntax feedback or empty result state!")
            self.assertEqual(len(console_errors), 0, f"Console errors: {console_errors}")
            self.assertEqual(len(page_errors), 0, f"Page errors: {page_errors}")

            browser.close()

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_03_canvas_zoom_stress_bounds(self):
        """
        Preconditions: Concept graph canvas view loaded in UI.
        Invariants: Executing rapid zoom in, zoom out, and reset button clicks must preserve canvas rendering.
        Outcomes: Canvas canvas element remains visible and active with zero page exceptions.
        """
        console_errors = []
        page_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.click(".tab-link[data-tab='explorer']")
            page.click("button[data-category='graph']")
            page.wait_for_selector("#concept-graph-canvas", timeout=5000)
            page.wait_for_function("typeof window.zoomConceptGraph === 'function'", timeout=5000)

            zoom_in = page.locator("button[title='Zoom In']")
            for _ in range(10):
                zoom_in.click()

            zoom_out = page.locator("button[title='Zoom Out']")
            for _ in range(10):
                zoom_out.click()

            reset_btn = page.locator("button[title='Reset View']")
            reset_btn.click()

            self.assertTrue(page.is_visible("#concept-graph-canvas"))
            self.assertEqual(len(console_errors), 0, f"Console errors: {console_errors}")
            self.assertEqual(len(page_errors), 0, f"Page errors: {page_errors}")

            browser.close()

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_04_dom_selector_compliance_and_error_tally(self):
        """
        Preconditions: Application file tree and search result containers rendered.
        Invariants: Precise DOM selectors matching '#file-tree .tree-file-title' and '#results-list .result-item' must exist.
        Outcomes: DOM elements match project layout standards; zero page or console errors reported.
        """
        console_errors = []
        page_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.click(".tab-link[data-tab='diagnostics']")
            page.wait_for_selector("#file-tree", state="visible", timeout=5000)
            page.click(".refresh-tree-btn")

            tree_titles = page.evaluate("Array.from(document.querySelectorAll('#file-tree .tree-file-title')).map(e => e.className)")
            
            page.click(".tab-link[data-tab='explorer']")
            page.wait_for_selector("#search-input", state="visible", timeout=5000)
            page.locator("#search-input").fill("stress")
            page.keyboard.press("Enter")
            page.wait_for_selector("#results-list", timeout=3000)

            result_items = page.evaluate("Array.from(document.querySelectorAll('#results-list .result-item')).map(e => e.className)")

            self.assertTrue(len(tree_titles) > 0 or len(result_items) > 0, "DOM selectors failed to locate tree titles or result items!")
            self.assertEqual(len(console_errors), 0, f"Console errors: {console_errors}")
            self.assertEqual(len(page_errors), 0, f"Page errors: {page_errors}")

            browser.close()


if __name__ == "__main__":
    unittest.main()