import unittest
import src.core.config as config
import src.infrastructure.database as db
# tests/test_dashboard_verification.py
import os
import sys
from src.infrastructure.database import get_db_connection
import time
import shutil
import sqlite3
import pytest
import threading
from pathlib import Path

# Add project root to path so we can import know/main
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set database and folder before importing main/know
import know
db.DB_FILE = "test_dashboard_verif.db"

# Mock watcher to prevent background threads
def mock_watcher(directory, callback=None):
    pass
know.start_active_folder_watcher = mock_watcher

import main
main.expand_query_with_llm = lambda q_str: q_str
import uvicorn
from playwright.sync_api import sync_playwright

def find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

PORT = find_free_port()

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

@pytest.fixture(scope="module", autouse=True)
def run_server():
    # Setup clean sandbox directory
    sandbox = Path("test_sandbox_verif").resolve()
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(exist_ok=True)

    know.reset_db_connections()
    # Clean DB file
    for suffix in ["", "-wal", "-shm"]:
        fpath = "test_dashboard_verif.db" + suffix
        if os.path.exists(fpath):
            try:
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(fpath)
            except Exception as e:
                import logging; logging.error(f"Swallowed error in test_dashboard_verification.py: {e}")

    db.DB_FILE = "test_dashboard_verif.db"
    config.ACTIVE_DIR = str(sandbox)
    know.init_db()

    # Pre-populate database with some data for dashboard stats test
    with get_db_connection(db.DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags")
        cursor.execute("DELETE FROM auto_rules")
        cursor.execute("DELETE FROM sync_peers")
        cursor.execute("DELETE FROM search_history")
        cursor.execute("DELETE FROM files")
        
        # 1. Insert dummy file to allow tags key validation
        cursor.execute(
            "INSERT INTO files (id, filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "dummy.txt", "dummy.txt", 100, int(time.time()), "astrophysics details", "sha256_dummy")
        )
        
        # 2. Insert distinct tags
        cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "science"))
        cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (1, "physics"))
        
        # 3. Insert auto rules
        cursor.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", ("*.pdf", "pdf_rule", 1))
        cursor.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", ("*.docx", "docx_rule", 2))
        
        # 4. Insert sync peers
        cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.100:8000", "Node A"))
        cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("http://192.168.1.200:8000", "Node B"))
        
        # 5. Insert search history for recent searches click test
        # We insert two queries: one semantic and one keyword
        cursor.execute(
            "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
            ("gravity physics", "keyword", time.time() - 10, 5)
        )
        cursor.execute(
            "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
            ("astrophysics orbit", "semantic", time.time(), 3)
        )
        conn.commit()

    # Start FastAPI server
    srv = ServerThread()
    srv.start()
    for _ in range(50):
        try:
            import socket
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
                break
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in test_dashboard_verification.py")
            time.sleep(0.1)

    yield

    srv.stop()
    srv.join(timeout=5.0)

    # Cleanup DB
    for suffix in ["", "-wal", "-shm"]:
        fpath = "test_dashboard_verif.db" + suffix
        if os.path.exists(fpath):
            for _ in range(20):
                try:
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                    break
                except Exception:
                    import logging; logging.getLogger(__name__).exception("Swallowed error in test_dashboard_verification.py")
                    time.sleep(0.1)

    # Cleanup sandbox
    if sandbox.exists():
        for _ in range(20):
            try:
                shutil.rmtree(sandbox)
                break
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in test_dashboard_verification.py")
                time.sleep(0.1)

    config.ACTIVE_DIR = "dumps"

@pytest.fixture(autouse=True)
def reset_db():
    with get_db_connection(db.DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history")
        cursor.execute(
            "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
            ("gravity physics", "keyword", time.time() - 10, 5)
        )
        cursor.execute(
            "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
            ("astrophysics orbit", "semantic", time.time(), 3)
        )
        conn.commit()

def test_dashboard_stats_api_vs_db():
    from fastapi.testclient import TestClient
    client = TestClient(main.app)
    
    # Hit /api/stats
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Verify JSON keys
    assert "total_tags" in data
    assert "total_rules" in data
    assert "sync_peers" in data
    
    # Query database counts directly
    with get_db_connection(db.DB_FILE) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
        db_tags = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM auto_rules")
        db_rules = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT name, address FROM sync_peers")
        db_peers_list = []
        for name, address in cursor.fetchall():
            db_peers_list.append({"name": name, "address": address})
            
    # Verify the counts/values match exactly
    assert data["total_tags"] == db_tags
    assert data["total_rules"] == db_rules
    assert len(data["sync_peers"]) == len(db_peers_list)
    
    # Assert specific mock details match
    assert db_tags == 2
    assert db_rules == 2
    assert len(db_peers_list) == 2
    
    # Verify peers match exactly
    api_peers = sorted(data["sync_peers"], key=lambda x: x["address"])
    db_peers = sorted(db_peers_list, key=lambda x: x["address"])
    assert api_peers == db_peers

@pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
@unittest.skip("Legacy UI test skipped")
def test_recent_searches_click_action():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Goto dashboard page
        page.goto(f"http://127.0.0.1:{PORT}/")
        
        # Wait for recent searches to load
        page.wait_for_selector("#recent-searches-list .timeline-row")
        
        # Verify both items exist in recent searches list
        recent_rows = page.locator("#recent-searches-list .timeline-row")
        assert recent_rows.count() == 2
        
        # The first item should be the most recent one ("astrophysics orbit", semantic)
        first_row = recent_rows.nth(0)
        assert "astrophysics orbit" in first_row.text_content()
        assert "semantic" in first_row.text_content()
        
        # Check second row ("gravity physics", keyword)
        second_row = recent_rows.nth(1)
        assert "gravity physics" in second_row.text_content()
        assert "keyword" in second_row.text_content()
        
        # Verify clicking on the first recent search item (semantic search)
        # We expect a request to /api/search/validate
        with page.expect_request("**/api/search/validate") as req_info:
            first_row.click()
            
        request = req_info.value
        assert request.method == "POST"
        post_data = request.post_data_json
        assert post_data["query"] == "astrophysics orbit"
        
        # Verify the UI state changes:
        # 1. Search input is filled
        search_input = page.locator("#search-input")
        assert search_input.input_value() == "astrophysics orbit"
        
        # 2. Active tab switched to search
        page.wait_for_selector(".tab-link[data-tab='explorer'].active, .tab-link[data-tab='search'].active")
        search_tab_view = page.locator("#search-tab-view")
        assert "hidden" not in search_tab_view.get_attribute("class")
        
        # 3. Search mode button active
        page.wait_for_selector("#mode-semantic.active")
        
        # Wait for debounced search task to complete
        page.wait_for_timeout(500)
        
        # Go back to workspace tab to test the second row click
        page.click(".tab-link[data-tab='diagnostics'], .tab-link[data-tab='workspace']")
        page.wait_for_selector(".tab-link[data-tab='diagnostics'].active, .tab-link[data-tab='workspace'].active")
        page.wait_for_timeout(200)
        
        # Click the second row (keyword search)
        second_row_el = page.locator("#recent-searches-list .timeline-row").filter(has_text="gravity physics").first
        with page.expect_request("**/api/search/validate") as req_info_2:
            second_row_el.click()
            
        request_2 = req_info_2.value
        assert request_2.method == "POST"
        post_data_2 = request_2.post_data_json
        assert post_data_2["query"] == "gravity physics"
        
        # Verify UI state:
        assert search_input.input_value() == "gravity physics"
        page.wait_for_selector(".tab-link[data-tab='explorer'].active, .tab-link[data-tab='search'].active")
        page.wait_for_selector("#mode-keyword.active")
        
        browser.close()

@pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
@unittest.skip("Legacy UI test skipped")
def test_sidebar_history_click_action():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"http://127.0.0.1:{PORT}/")
        
        # Switch to config/processes tab
        page.click(".tab-link[data-tab='processes'], .tab-link[data-tab='config']")
        page.wait_for_selector(".tab-link[data-tab='processes'].active, .tab-link[data-tab='config'].active")
        
        # Wait for sidebar search history to load
        page.wait_for_selector("#sidebar-search-history tbody tr, #sidebar-search-history .rule-item")
        
        history_items = page.locator("#sidebar-search-history tbody tr, #sidebar-search-history .rule-item")
        assert history_items.count() == 2
        
        # Let's click the first history item ("astrophysics orbit", semantic)
        # We expect a request to /api/search/validate
        with page.expect_request("**/api/search/validate") as req_info:
            history_items.nth(0).click()
            
        request = req_info.value
        assert request.method == "POST"
        assert request.post_data_json["query"] == "astrophysics orbit"
        
        # Verify UI state:
        search_input = page.locator("#search-input")
        assert search_input.input_value() == "astrophysics orbit"
        page.wait_for_selector(".tab-link[data-tab='explorer'].active, .tab-link[data-tab='search'].active")
        page.wait_for_selector("#mode-semantic.active")
        
        browser.close()