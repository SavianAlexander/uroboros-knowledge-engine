"""
Unit & Integration Test Suite for Milestone 3 (UI Session Sidebar & GGUF Model Controls + SHA-256 sync).
Verifies HTML structure, CSS styling rules, JS function definitions & exports, SHA-256 bitwise parity,
and backend API endpoints.
"""

import os
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from src.app.server import app

client = TestClient(app)

def test_html_view4_m3_elements_exist():
    """Verify index.html contains all required Milestone 3 element IDs and classes."""
    html_path = "index.html"
    assert os.path.exists(html_path), "index.html must exist"
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    required_ids = [
        "chat-tab-view",
        "session-sidebar",
        "new-session-btn",
        "session-search-input",
        "session-list",
        "gguf-controls-panel",
        "gguf-model-path",
        "gguf-temperature",
        "gguf-temp-val",
        "gguf-context-window",
        "web-search-toggle",
        "citation-chips-container",
        "chat-messages",
        "chat-input",
        "chat-send-btn",
    ]
    
    for req_id in required_ids:
        assert f'id="{req_id}"' in html_content, f"Missing required ID: {req_id} in index.html"

def test_css_m3_rules_exist():
    """Verify style.css contains all required Milestone 3 styling classes."""
    css_path = "style.css"
    assert os.path.exists(css_path), "style.css must exist"
    
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
        
    required_selectors = [
        ".session-sidebar",
        ".new-session-btn",
        "#session-search-input",
        ".session-list",
        ".session-item",
        ".session-item.active",
        ".delete-session-btn",
        ".gguf-controls-panel",
        "#gguf-model-path",
        "#gguf-temperature",
        "#gguf-temp-val",
        "#gguf-context-window",
        ".toggle-switch",
        ".toggle-slider",
        "#citation-chips-container",
        ".local-source-chip",
        ".web-source-chip",
        ".copy-code-btn",
        ".chat-code-block-wrapper",
    ]
    
    for selector in required_selectors:
        assert selector in css_content, f"Missing required selector: {selector} in style.css"

def test_js_m3_functions_exist():
    """Verify app.js defines and exposes all required Milestone 3 functions."""
    js_path = "app.js"
    assert os.path.exists(js_path), "app.js must exist"
    
    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()
        
    required_functions = [
        "function fetchChatSessions",
        "function createNewSession",
        "function switchSession",
        "function deleteSession",
        "function filterChatSessions",
        "function sendChatMessage",
        "function sendChatMessageWithText",
        "function parseChatMarkdown",
        "function renderSourceChips",
        "function renderGlobalCitationChips",
        "window.fetchChatSessions",
        "window.createNewSession",
        "window.switchSession",
        "window.deleteSession",
        "window.filterChatSessions",
    ]
    
    for fn in required_functions:
        assert fn in js_content, f"Missing required function/export: {fn} in app.js"

def test_sha256_bitwise_asset_parity():
    """Verify 100% SHA-256 bitwise parity between root assets and src/assets copies."""
    pairs = [
        ("index.html", "src/assets/index.html"),
        ("style.css", "src/assets/style.css"),
        ("app.js", "src/assets/app.js"),
    ]
    
    for root_file, asset_file in pairs:
        assert os.path.exists(root_file), f"Root file missing: {root_file}"
        assert os.path.exists(asset_file), f"Asset file missing: {asset_file}"
        
        with open(root_file, "rb") as f1, open(asset_file, "rb") as f2:
            h1 = hashlib.sha256(f1.read()).hexdigest()
            h2 = hashlib.sha256(f2.read()).hexdigest()
            assert h1 == h2, f"SHA-256 mismatch for {root_file} vs {asset_file}: {h1} != {h2}"

def test_chat_sessions_api_endpoints():
    """Integration test for backend session CRUD endpoints consumed by frontend app.js."""
    import src.infrastructure.database as db
    import tempfile
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        test_db_path = os.path.join(tmp_dir, "test_m3.db")
        orig_db = db.DB_FILE
        db.DB_FILE = test_db_path
        try:
            db.init_db()
            test_client = TestClient(app)
            
            # 1. Create a session
            create_resp = test_client.post("/api/chat/sessions", json={
                "title": "M3 Integration Test Session",
                "model_path": "models/tinyllama.gguf",
                "temperature": 0.7,
                "context_window": 4096
            })
            assert create_resp.status_code == 200
            sess_data = create_resp.json()
            assert "id" in sess_data
            session_id = sess_data["id"]
            assert sess_data["title"] == "M3 Integration Test Session"
            
            # 2. List sessions
            list_resp = test_client.get("/api/chat/sessions")
            assert list_resp.status_code == 200
            sessions_list = list_resp.json()
            assert any(s["id"] == session_id for s in sessions_list)
            
            # 3. Get session details
            get_resp = test_client.get(f"/api/chat/sessions/{session_id}")
            assert get_resp.status_code == 200
            get_data = get_resp.json()
            assert get_data["id"] == session_id
            assert "messages" in get_data
            
            # 4. Delete session
            del_resp = test_client.delete(f"/api/chat/sessions/{session_id}")
            assert del_resp.status_code == 200
            
            # 5. Verify deletion
            get_del_resp = test_client.get(f"/api/chat/sessions/{session_id}")
            assert get_del_resp.status_code == 404
        finally:
            db.reset_db_connections()
            db.DB_FILE = orig_db
