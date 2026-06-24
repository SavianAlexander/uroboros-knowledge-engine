import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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
    
    # PDF export with include_notes disabled test
    response = client.get("/api/report/export?include_notes=false")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # 14. Stats CSV Export test
    response = client.get("/api/stats/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Total Size" in response.text

    # 15. Delete renamed file
    response = client.delete(f"/api/file/delete?path={renamed_path}")
    assert response.status_code == 200
    
    # Check that disk file is gone
    assert not os.path.exists(renamed_path)

if __name__ == "__main__":
    print("Running API CRUD self-checks...")
    test_static_routes()
    test_api_endpoints()
    test_crud_and_annotations()
    print("All API, Static route, CRUD, Rules, Semantic routing, and LAN Sync checks passed successfully!")
