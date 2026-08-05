"""
Empirical Adversarial Test Suite for Milestone 3 (UI Session Sidebar & GGUF Controls + SSE Streaming)
Written by Empirical Challenger 1.
"""

import os
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from src.app.server import app
import src.infrastructure.database as db
import tempfile

client = TestClient(app)

def test_empirically_verify_js_temperature_zero_handling():
    """
    Empirically inspect app.js and src/assets/app.js for the Temperature 0.0 evaluation bug.
    `parseFloat(tempEl.value) || 0.7` incorrectly turns 0.0 into 0.7 because 0 is falsy in JS.
    """
    js_paths = ["app.js", "src/assets/app.js"]
    bug_detected = False
    for path in js_paths:
        assert os.path.exists(path), f"{path} must exist"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        has_buggy_pattern = "parseFloat(tempEl.value) || 0.7" in content or "(parseFloat(tempEl.value) || 0.7)" in content
        if has_buggy_pattern:
            bug_detected = True
    
    # Asserting that the bug is absent (will fail if bug is present, flagging it for remediation)
    assert not bug_detected, "Temperature 0.0 falsy evaluation bug found in JS: `parseFloat(tempEl.value) || 0.7` treats 0 as falsy and overrides 0.0 with 0.7!"

def test_sse_stream_fragmentation_handling_simulation():
    """
    Empirically test partial SSE stream line handling logic with split chunks.
    """
    sse_events = [
        'data: {"type": "token", "content": "Hello"}\n\n',
        'data: {"type": "token", "content": " World"}\n\n',
        'data: {"type": "sources", "local_citations": [{"file": "doc1.txt"}]}\n\n',
        'data: [DONE]\n\n'
    ]
    raw_stream = "".join(sse_events)

    # Chunk stream into 3-char fragments
    fragments = [raw_stream[i:i+3] for i in range(0, len(raw_stream), 3)]

    line_buffer = ""
    parsed_tokens = []
    parsed_sources = []

    for frag in fragments:
        line_buffer += frag
        lines = line_buffer.split("\n")
        line_buffer = lines.pop()

        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith(":"):
                continue
            if line_str.startswith("data: "):
                payload = line_str[6:].strip()
                if payload == "[DONE]":
                    continue
                try:
                    data = json.loads(payload)
                    if "content" in data:
                        parsed_tokens.append(data["content"])
                    if "local_citations" in data:
                        parsed_sources.extend(data["local_citations"])
                except json.JSONDecodeError:
                    pytest.fail(f"Partial JSON syntax error encountered on line: {line_str}")

    assert "".join(parsed_tokens) == "Hello World"
    assert len(parsed_sources) == 1
    assert parsed_sources[0]["file"] == "doc1.txt"

def test_rapid_session_api_stress_crud():
    """
    Empirically stress test backend session creation, listing, getting, and deleting 50 sessions.
    """
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        test_db_path = os.path.join(tmp_dir, "test_rapid_m3.db")
        orig_db = db.DB_FILE
        db.DB_FILE = test_db_path
        try:
            db.init_db()
            test_client = TestClient(app)
            
            created_ids = []
            
            # Rapidly create 50 sessions
            for i in range(50):
                resp = test_client.post("/api/chat/sessions", json={
                    "title": f"Stress Session {i}",
                    "model_path": "models/tinyllama.gguf",
                    "temperature": 0.7,
                    "context_window": 4096
                })
                assert resp.status_code == 200
                data = resp.json()
                created_ids.append(data["id"])
            
            assert len(created_ids) == 50
            
            # List sessions
            list_resp = test_client.get("/api/chat/sessions")
            assert list_resp.status_code == 200
            sessions = list_resp.json()
            assert len(sessions) == 50
            
            # Delete 25 sessions
            for sid in created_ids[:25]:
                del_resp = test_client.delete(f"/api/chat/sessions/{sid}")
                assert del_resp.status_code == 200
            
            # Verify list contains remaining 25
            list_resp2 = test_client.get("/api/chat/sessions")
            assert list_resp2.status_code == 200
            assert len(list_resp2.json()) == 25
            
        finally:
            db.reset_db_connections()
            db.DB_FILE = orig_db

def test_sha256_bitwise_sync_check():
    """
    Empirically verify 100% SHA-256 bitwise equality between root and src/assets files.
    """
    pairs = [
        ("index.html", "src/assets/index.html"),
        ("style.css", "src/assets/style.css"),
        ("app.js", "src/assets/app.js"),
    ]
    for root_f, asset_f in pairs:
        assert os.path.exists(root_f), f"Missing {root_f}"
        assert os.path.exists(asset_f), f"Missing {asset_f}"
        with open(root_f, "rb") as f1, open(asset_f, "rb") as f2:
            h1 = hashlib.sha256(f1.read()).hexdigest()
            h2 = hashlib.sha256(f2.read()).hexdigest()
            assert h1 == h2, f"SHA-256 mismatch for {root_f} vs {asset_f}"
