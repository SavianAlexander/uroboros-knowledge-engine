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

    # 8. Delete renamed file
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
