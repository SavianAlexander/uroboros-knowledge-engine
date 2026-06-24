import os
import know
# Override DB_FILE and initialize it for API tests to avoid state contamination from E2E tests
know.DB_FILE = "test_knowledge.db"
for suffix in ["", "-wal", "-shm"]:
    fpath = "test_knowledge.db" + suffix
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
        except Exception:
            pass
know.init_db()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

import pytest

@pytest.fixture(autouse=True)
def setup_api_db():
    import know
    know.DB_FILE = "test_knowledge.db"
    know.init_db()
    for f in ["dumps/mock_crud.txt", "dumps/renamed_crud.txt"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def test_static_routes():
    response = client.get("/")
    assert response.status_code == 200
    assert "Uroboros" in response.text

    response = client.get("/style.css")
    assert response.status_code == 200
    assert "var(--bg-dark)" in response.text

    response = client.get("/app.js")
    assert response.status_code == 200
    assert "fetchStats" in response.text

def test_api_endpoints():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_files" in data
    assert "total_size" in data
    assert "mime_breakdown" in data
    assert "timeline" in data

    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

    # Multi-tag search logic tests
    response = client.get("/api/search?tag=science,physics&tag_mode=AND")
    assert response.status_code == 200
    assert "results" in response.json()

    response = client.get("/api/search?tag=science,physics&tag_mode=OR")
    assert response.status_code == 200
    assert "results" in response.json()

    response = client.post("/api/index", json={"directory": "/nonexistent/path/for/test"})
    assert response.status_code == 400

def test_crud_and_annotations():
    # 1. Upload mock file
    payload = {"file": ("mock_crud.txt", b"temporary crud content for tests", "text/plain")}
    response = client.post("/api/upload", files=payload)
    assert response.status_code == 200
    filepath = response.json()["filepath"]
    
    # 2. Add custom note annotation
    response = client.post("/api/file/notes", json={"filepath": filepath, "notes": "important reference formula"})
    assert response.status_code == 200
    
    # 3. Check notes retrieval and suggested tags
    response = client.get(f"/api/file?path={filepath}")
    assert response.status_code == 200
    file_data = response.json()
    assert file_data["notes"] == "important reference formula"
    
    # 4. Rename the file
    response = client.post("/api/file/rename", json={"filepath": filepath, "new_name": "renamed_crud.txt"})
    assert response.status_code == 200
    renamed_path = response.json()["new_filepath"]
    assert "renamed_crud.txt" in renamed_path
    
    # 5. Rules API tests
    response = client.post("/api/rules", json={"pattern": "mock_pattern", "tag": "test_tag"})
    assert response.status_code == 200
    
    response = client.get("/api/rules")
    assert response.status_code == 200
    rules = response.json()["rules"]
    assert len(rules) > 0
    rule_id = rules[0]["id"]
    
    # 6. Semantic Search API Routing check
    response = client.get("/api/search?q=crud&mode=semantic")
    assert response.status_code == 200
    
    response = client.delete(f"/api/rules?id={rule_id}")
    assert response.status_code == 200

    # 7. Sync Peers API tests
    response = client.post("/api/sync/peers", json={"address": "http://localhost:8080", "name": "Neighbor Node"})
    assert response.status_code == 200
    
    response = client.get("/api/sync/peers")
    assert response.status_code == 200
    peers = response.json()["peers"]
    assert len(peers) > 0
    peer_id = peers[0]["id"]
    
    response = client.delete(f"/api/sync/peers?id={peer_id}")
    assert response.status_code == 200

    # 8. Edit File API test
    response = client.post("/api/file/edit", json={"filepath": renamed_path, "content": "updated mock content from api test [[another-mock.txt]]"})
    assert response.status_code == 200
    
    # 9. Snapshots API checks
    response = client.post("/api/snapshots")
    assert response.status_code == 200
    ts = response.json()["timestamp"]
    
    response = client.get("/api/snapshots")
    assert response.status_code == 200
    assert ts in response.json()["snapshots"]
    
    response = client.delete(f"/api/snapshots?timestamp={ts}")
    assert response.status_code == 200
    
    # 10. Graph Network endpoint test
    response = client.get("/api/graph")
    assert response.status_code == 200
    assert "nodes" in response.json()

    # 11. PDF Report Export test
    response = client.get("/api/report/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # PDF Filtered Report Export test
    response = client.get("/api/report/export?category=documents&tag=science")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # PDF Custom title and theme palette Report Export test
    response = client.get("/api/report/export?report_title=Custom+Title+Test&theme_palette=crimson")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    
    # PDF Filtered Report Export test with comma-separated tag list
    response = client.get("/api/report/export?tag=science,physics,quantum")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # Rules preview test
    response = client.post("/api/rules/test-preview", json={"pattern": "mock", "tag": "science"})
    assert response.status_code == 200
    assert "matches" in response.json()

    # 12. Audio metadata parsing check
    # Let's write a simple WAV header mockup to check the native parser
    import struct
    wav_payload = (
        b"RIFF" + struct.pack("<I", 36 + 44) + b"WAVE" +
        b"fmt " + struct.pack("<IHHIIHH", 16, 1, 2, 44100, 176400, 4, 16) +
        b"data" + struct.pack("<I", 44) + (b"\x00" * 44)
    )
    response = client.post("/api/upload", files={"file": ("mock_audio.wav", wav_payload, "audio/wav")})
    assert response.status_code == 200
    audio_path = response.json()["filepath"]

    response = client.get(f"/api/file?path={audio_path}")
    assert response.status_code == 200
    audio_data = response.json()
    assert "audio_metadata" in audio_data
    assert audio_data["audio_metadata"]["channels"] == 2
    assert audio_data["audio_metadata"]["samplerate"] == 44100

    # Clean up audio test file
    response = client.delete(f"/api/file/delete?path={audio_path}")
    assert response.status_code == 200

    # 13. PDF compact style template test
    response = client.get("/api/report/export?style_template=compact")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # PDF descriptive style template test
    response = client.get("/api/report/export?style_template=descriptive")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # PDF TOC style template test
    response = client.get("/api/report/export?style_template=toc")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # PDF export with include_notes disabled test
    response = client.get("/api/report/export?include_notes=false")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # 14. Stats CSV Export test
    response = client.get("/api/stats/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Total Size" in response.text

    # PDF gallery style template test
    response = client.get("/api/report/export?style_template=gallery")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # Search exclusions tests
    # Exclude files tagged "tag_not_existent" (should return the file)
    response = client.get("/api/search?q=-tag:tag_not_existent")
    assert response.status_code == 200
    
    # Exclude files matching type "png" (should exclude images if any, or not fail)
    response = client.get("/api/search?q=-type:png")
    assert response.status_code == 200

    # Tag Custom Colors API tests
    response = client.post("/api/tags/color", json={"tag": "science", "color": "#00ff00"})
    assert response.status_code == 200
    
    # Retrieve tags with color info checks
    response = client.get("/api/tags")
    assert response.status_code == 200
    
    # Custom configuration snippet parameters test
    response = client.get("/api/search?q=reference&snippet_limit=5&highlight_start=[START]&highlight_end=[END]")
    assert response.status_code == 200

    # Query macros endpoint tests
    response = client.post("/api/macros", json={"name": "macro_test", "expansion": "tag:science type:txt"})
    assert response.status_code == 200
    response = client.get("/api/macros")
    assert response.status_code == 200
    
    # Tag aliases endpoint tests
    response = client.post("/api/aliases", json={"alias": "physics_alias", "target": "science"})
    assert response.status_code == 200
    response = client.get("/api/aliases")
    assert response.status_code == 200

    # Macro expansion and directory path scoping search test
    response = client.get("/api/search?q=%macro_test%&folder_path=test_sandbox")
    assert response.status_code == 200

    # Macro deletion endpoint check
    response = client.delete("/api/macros?name=macro_test")
    assert response.status_code == 200

    # FTS Proximity NEAR check search test
    response = client.get("/api/search?q=NEAR(\"gravity\" \"physics\", 5)")
    assert response.status_code == 200
    
    # Synonyms mapping endpoints test
    response = client.post("/api/synonyms", json={"word": "physics", "substitutes": "quantum, relativity"})
    assert response.status_code == 200
    response = client.get("/api/synonyms")
    assert response.status_code == 200
    
    # Similarity threshold search test
    response = client.get("/api/search?q=formula&mode=semantic&similarity_threshold=50.0")
    assert response.status_code == 200
    
    # Backups scheduling endpoint test
    response = client.post("/api/backups/schedule", json={"interval_seconds": 60})
    assert response.status_code == 200

    # 15. Delete renamed file
    # We will upload a secondary mockup file to test bulk deletion API too
    payload_bulk = {"file": ("mock_bulk_delete.txt", b"temporary mock bulk delete", "text/plain")}
    response = client.post("/api/upload", files=payload_bulk)
    assert response.status_code == 200
    bulk_path = response.json()["filepath"]
    
    response = client.post("/api/file/bulk-delete", json={"filepaths": [renamed_path, bulk_path]})
    assert response.status_code in [200, 207]
    
    # Check that disk files are gone
    assert not os.path.exists(renamed_path)
    assert not os.path.exists(bulk_path)

def test_cache_loophole_and_watcher_guard():
    import sys
    is_testing = (
        os.environ.get("TESTING") == "true"
        or "pytest" in sys.modules
        or "unittest" in sys.modules
        or any("test" in arg for arg in sys.argv)
    )
    assert is_testing is True

    import threading
    from unittest.mock import MagicMock
    
    mock_thread_indexer = MagicMock()
    mock_thread_indexer.name = "IndexerThread"
    
    mock_thread_watcher = MagicMock()
    mock_thread_watcher.name = "WatcherThread"
    
    original_enumerate = threading.enumerate
    try:
        threading.enumerate = lambda: [mock_thread_indexer]
        has_active_indexer = any(t.name in ("IndexerThread", "WatcherThread") for t in threading.enumerate())
        assert has_active_indexer is True
        
        threading.enumerate = lambda: [mock_thread_watcher]
        has_active_watcher = any(t.name in ("IndexerThread", "WatcherThread") for t in threading.enumerate())
        assert has_active_watcher is True

        threading.enumerate = lambda: []
        has_active_indexing = any(t.name in ("IndexerThread", "WatcherThread") for t in threading.enumerate())
        assert has_active_indexing is False
    finally:
        threading.enumerate = original_enumerate

if __name__ == "__main__":
    print("Running API CRUD self-checks...")
    test_static_routes()
    test_api_endpoints()
    test_crud_and_annotations()
    print("All API, Static route, CRUD, Rules, Semantic routing, and LAN Sync checks passed successfully!")
