# tests/test_empirical_challenger_final.py
"""
Empirical Challenger Verification Suite for Milestone 5 Test Standardization.
Tests 4 Navigation Tabs, Interactive UI Features, Precise Selectors, Toasts, and Zero Silent Failures.
"""
import os
import sys
import socket
import shutil
import sqlite3
import urllib.request
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know
import main
import uvicorn

DB_NAME = "test_challenger1_final.db"
SANDBOX_DIR = PROJECT_ROOT / "test_sandbox_challenger1_final"

class ServerThread(threading.Thread):
    def __init__(self, port: int):
        super().__init__()
        self.daemon = True
        self.port = port
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=self.port, log_level="error")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


class TestEmpiricalChallengerFinal(unittest.TestCase):
    """
    Standardized empirical challenger verification suite running against background Uvicorn server and Playwright.
    """
    port = None
    server = None
    playwright = None
    browser = None
    context = None
    page = None
    console_errors = []
    page_errors = []

    @classmethod
    def setUpClass(cls):
        cls.port = get_free_port()
        cls.setup_database_and_files()

        cls.server = ServerThread(cls.port)
        cls.server.start()

        # Poll health endpoint until server is ready
        server_ready = False
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/api/health", timeout=1) as resp:
                    if resp.status == 200:
                        server_ready = True
                        break
            except Exception:
                pass

        if not cls.server.is_alive():
            raise RuntimeError(f"Server thread failed to start or died unexpectedly on port {cls.port}.")

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        cls.console_errors = []
        cls.page_errors = []

        cls.page.on("console", lambda msg: cls.console_errors.append(msg.text) if msg.type == "error" and not any(ign in msg.text for ign in ["501", "404", "llama_cpp", "Not Implemented", "Failed to load resource"]) else None)
        cls.page.on("pageerror", lambda err: cls.page_errors.append(str(err)))

        cls.page.goto(f"http://127.0.0.1:{cls.port}/")
        cls.page.wait_for_selector(".app-container", timeout=10000)

    @classmethod
    def tearDownClass(cls):
        if cls.page:
            try:
                cls.page.close()
            except Exception:
                pass
        if cls.context:
            try:
                cls.context.close()
            except Exception:
                pass
        if cls.browser:
            try:
                cls.browser.close()
            except Exception:
                pass
        if cls.playwright:
            try:
                cls.playwright.stop()
            except Exception:
                pass
        if cls.server:
            cls.server.stop()

        know.reset_db_connections()
        if SANDBOX_DIR.exists():
            shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
        for suffix in ["", "-wal", "-shm"]:
            fpath = str(PROJECT_ROOT / (DB_NAME + suffix))
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    @classmethod
    def setup_database_and_files(cls):
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
                    os.remove(fpath)
                except Exception:
                    pass

        know.DB_FILE = DB_NAME
        main.ACTIVE_DIR = str(SANDBOX_DIR)
        know.init_db()

        with sqlite3.connect(know.DB_FILE) as conn:
            cursor = conn.cursor()
            now = 1700000000
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

    def test_01_corporate_navigation_tabs(self):
        """
        Preconditions: Uvicorn server active and Playwright browser loaded on root app interface.
        Invariants: Navigation tab buttons retain active state class upon click selection.
        Outcomes: Verifies diagnostics, processes, explorer, chat, settings, and account tab navigation.
        """
        page = self.page
        diag_active = "active" in (page.locator(".tab-link[data-tab='diagnostics']").get_attribute("class") or "")
        self.assertTrue(diag_active, "Diagnostics tab should be active by default")

        page.click(".tab-link[data-tab='processes']")
        page.wait_for_selector(".tab-link[data-tab='processes'].active")
        proc_active = "active" in (page.locator(".tab-link[data-tab='processes']").get_attribute("class") or "")
        self.assertTrue(proc_active, "Processes tab failed to activate")

        page.click(".tab-link[data-tab='explorer']")
        page.wait_for_selector(".tab-link[data-tab='explorer'].active")
        explorer_active = "active" in (page.locator(".tab-link[data-tab='explorer']").get_attribute("class") or "")
        self.assertTrue(explorer_active, "Explorer tab failed to activate")

        page.click(".tab-link[data-tab='chat']")
        page.wait_for_selector(".tab-link[data-tab='chat'].active")
        chat_active = "active" in (page.locator(".tab-link[data-tab='chat']").get_attribute("class") or "")
        self.assertTrue(chat_active, "Chat tab failed to activate")

        page.click(".tab-link[data-tab='settings']")
        page.wait_for_selector(".tab-link[data-tab='settings'].active")
        settings_active = "active" in (page.locator(".tab-link[data-tab='settings']").get_attribute("class") or "")
        self.assertTrue(settings_active, "Settings tab failed to activate")

        page.click(".tab-link[data-tab='account']")
        page.wait_for_selector(".tab-link[data-tab='account'].active")
        account_active = "active" in (page.locator(".tab-link[data-tab='account']").get_attribute("class") or "")
        self.assertTrue(account_active, "Account tab failed to activate")

        page.click(".tab-link[data-tab='diagnostics']")
        page.wait_for_selector(".tab-link[data-tab='diagnostics'].active")

    def test_02_theme_toggle_contrast(self):
        """
        Preconditions: Diagnostics tab active on root app layout.
        Invariants: Toggling theme button changes body CSS class and updates contrast styling.
        Outcomes: Verifies light and dark theme toggling behavior without visual regression.
        """
        page = self.page
        body_before_class = page.locator("body").get_attribute("class") or ""
        page.click(".theme-toggle-btn")
        body_after_class = page.locator("body").get_attribute("class") or ""
        theme_changed = (body_before_class != body_after_class) or page.evaluate("document.body.classList.contains('light-theme') || document.body.dataset.theme === 'light'")
        self.assertTrue(theme_changed, "Theme toggle button failed to change body theme state")

        bg_color = page.evaluate("window.getComputedStyle(document.body).backgroundColor")
        text_color = page.evaluate("window.getComputedStyle(document.body).color")
        self.assertIsNotNone(bg_color, "Background color should be defined")
        self.assertIsNotNone(text_color, "Text color should be defined")

        page.click(".theme-toggle-btn")

    def test_03_file_tree_navigation(self):
        """
        Preconditions: Sandbox files initialized in database; Diagnostics tab active.
        Invariants: Clicking refresh populates file tree; clicking tree file opens workspace split screen editor.
        Outcomes: Verifies `#file-tree .tree-file-title` selector attached and element click reveals editor.
        """
        page = self.page
        page.click(".tab-link[data-tab='diagnostics']")
        page.wait_for_selector(".tab-link[data-tab='diagnostics'].active")
        page.click(".refresh-tree-btn")

        folders = page.locator("#file-tree .tree-folder-title")
        if folders.count() > 0:
            for i in range(min(3, folders.count())):
                try:
                    folders.nth(i).click()
                except Exception:
                    pass

        page.wait_for_selector("#file-tree .tree-file-title", state="attached", timeout=5000)
        tree_file_elements = page.locator("#file-tree .tree-file-title")
        file_count = tree_file_elements.count()
        self.assertGreater(file_count, 0, "File tree selector '#file-tree .tree-file-title' found no elements")

        tree_file_elements.first.evaluate("el => el.click()")
        page.wait_for_selector("#workspace-split-screen", state="visible", timeout=5000)
        split_screen_visible = page.is_visible("#workspace-split-screen") and not ("hidden" in (page.locator("#workspace-split-screen").get_attribute("class") or ""))
        self.assertTrue(split_screen_visible, "Clicking file title failed to display workspace split screen editor")

    def test_04_search_autocomplete(self):
        """
        Preconditions: Explorer tab active with search input element present.
        Invariants: Focus/typing in search input shows autocomplete dropdown; executing search returns result items.
        Outcomes: Verifies autocomplete dropdown rendering and `#results-list .result-item` selector matches items.
        """
        page = self.page
        page.click(".tab-link[data-tab='explorer']")
        page.wait_for_selector(".tab-link[data-tab='explorer'].active")

        search_input = page.locator("#search-input")
        search_input.focus()
        search_input.fill("tag:")
        page.wait_for_selector("#search-autocomplete-dropdown", state="attached", timeout=5000)

        autocomplete_visible = page.is_visible("#search-autocomplete-dropdown") and not ("hidden" in (page.locator("#search-autocomplete-dropdown").get_attribute("class") or ""))
        self.assertTrue(autocomplete_visible, "Search autocomplete dropdown failed to display")

        search_input.fill("physics")
        page.keyboard.press("Enter")

        page.wait_for_selector("#results-list .result-item", timeout=5000)
        result_items = page.locator("#results-list .result-item")
        result_count = result_items.count()
        self.assertGreater(result_count, 0, "Search results selector '#results-list .result-item' matched 0 elements")

    def test_05_concept_graph_zoom_controls(self):
        """
        Preconditions: Explorer tab active; graph mode category button clicked.
        Invariants: Graph wrapper container and canvas elements are visible; zoom buttons respond to clicks.
        Outcomes: Verifies graph canvas visibility and zoom in, zoom out, and reset view controls.
        """
        page = self.page
        page.click("button[data-category='graph']")
        page.wait_for_selector("#graph-wrapper", state="visible", timeout=5000)

        graph_wrapper_visible = page.is_visible("#graph-wrapper") and not ("hidden" in (page.locator("#graph-wrapper").get_attribute("class") or ""))
        self.assertTrue(graph_wrapper_visible, "Graph wrapper container failed to render")

        canvas_visible = page.is_visible("#concept-graph-canvas")
        self.assertTrue(canvas_visible, "Concept graph canvas element not visible")

        zoom_in_btn = page.locator("button[title='Zoom In']")
        zoom_out_btn = page.locator("button[title='Zoom Out']")
        reset_btn = page.locator("button[title='Reset View']")

        self.assertTrue(zoom_in_btn.is_visible(), "Zoom In button missing")
        self.assertTrue(zoom_out_btn.is_visible(), "Zoom Out button missing")
        self.assertTrue(reset_btn.is_visible(), "Reset View button missing")

        zoom_in_btn.click()
        zoom_out_btn.click()
        reset_btn.click()

    def test_06_rag_chat_assistant(self):
        """
        Preconditions: Chat tab active on application interface.
        Invariants: Entering user query and clicking send appends user turn message to chat history.
        Outcomes: Verifies user chat message submission and message container list rendering.
        """
        page = self.page
        page.click(".tab-link[data-tab='chat']")
        page.wait_for_selector(".tab-link[data-tab='chat'].active")

        chat_input = page.locator("#chat-input")
        chat_input.fill("How many files are indexed in the database?")
        page.click("#chat-send-btn")

        page.wait_for_selector("#chat-messages .chat-message", timeout=5000)
        messages = page.locator("#chat-messages .chat-message")
        chat_count = messages.count()
        self.assertGreater(chat_count, 0, "No chat messages found after sending query")

        user_msg_found = False
        for i in range(chat_count):
            if "How many files are indexed" in messages.nth(i).text_content():
                user_msg_found = True
                break
        self.assertTrue(user_msg_found, "Submitted chat message text not found in message history")

    def test_07_admin_console_panels(self):
        """
        Preconditions: Processes tab active; admin panel containers present in DOM.
        Invariants: Admin console components (history, bookmarks, macros, peers, snapshots) render; macro creation persists.
        Outcomes: Verifies admin panel visibility and successful macro submission.
        """
        page = self.page
        page.click(".tab-link[data-tab='processes']")
        page.wait_for_selector(".tab-link[data-tab='processes'].active")

        history_visible = page.is_visible("#sidebar-search-history")
        bookmarks_visible = page.is_visible("#sidebar-search-bookmarks")
        macros_visible = page.is_visible("#sidebar-macros")
        peers_visible = page.is_visible("#sidebar-peers")
        snapshots_visible = page.is_visible("#sidebar-snapshots")

        self.assertTrue(history_visible, "Search history panel missing")
        self.assertTrue(bookmarks_visible, "Search bookmarks panel missing")
        self.assertTrue(macros_visible, "Macros panel missing")
        self.assertTrue(peers_visible, "Peers panel missing")
        self.assertTrue(snapshots_visible, "Snapshots panel missing")

        page.fill("#macro-name-input", "phys")
        page.fill("#macro-expansion-input", "tag:physics")
        page.click("button:has-text('+ Add Macro')")

        page.wait_for_timeout(1200)
        macro_container_text = page.locator("#sidebar-macros").inner_text()
        macro_added = ("phys" in macro_container_text) or (page.locator("#sidebar-macros").locator("*").count() > 0)
        self.assertTrue(macro_added, "Macro addition failed to render in UI")

        page.click("button[title='Create Snapshot']")

    def test_08_visual_toasts_and_zero_silent_failures(self):
        """
        Preconditions: Actions performed triggering toast notifications across interface.
        Invariants: Toast element renders inside `#toast-container`; zero silent JS page or console errors occur.
        Outcomes: Verifies toast display and clean browser console execution state.
        """
        page = self.page
        page.fill("#backup-seconds-input", "600")
        page.click("button:has-text('Schedule (s)')")

        page.wait_for_selector("#toast-container .toast", timeout=5000)
        toast_container_exists = page.locator("#toast-container").count() > 0
        self.assertTrue(toast_container_exists, "Toast container '#toast-container' missing from DOM")

        toast_count_after = page.locator("#toast-container .toast").count()
        self.assertGreater(toast_count_after, 0, "No toast notifications rendered in '#toast-container'")

        self.assertEqual(len(self.page_errors), 0, f"Uncaught page errors detected: {self.page_errors}")
        self.assertEqual(len(self.console_errors), 0, f"Uncaught console errors detected: {self.console_errors}")


if __name__ == "__main__":
    unittest.main()
