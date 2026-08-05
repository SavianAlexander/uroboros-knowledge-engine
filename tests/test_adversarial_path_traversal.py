# tests/test_adversarial_path_traversal.py
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import know
import main

class TestPathTraversalProtections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        know.DB_FILE = "test_adversarial_traversal.db"
        know.init_db()
        cls.client = TestClient(main.app)
        cls.outside_path = "../outside_test_file.txt"
        cls.absolute_outside_path = os.path.abspath("outside_test_file.txt")
        
        # Ensure dumps directory exists and has a test file
        os.makedirs("dumps", exist_ok=True)
        with open("dumps/ok.txt", "w") as f:
            f.write("dummy content")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("dumps/ok.txt"):
            os.remove("dumps/ok.txt")
        for suffix in ["", "-wal", "-shm"]:
            fpath = f"test_adversarial_traversal.db{suffix}"
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    def test_get_file_raw_traversal(self):
        response = self.client.get("/api/file/raw", params={"path": self.outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.get("/api/file/raw", params={"path": self.absolute_outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_get_file_traversal(self):
        response = self.client.get("/api/file", params={"path": self.outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.get("/api/file", params={"path": self.absolute_outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_save_file_traversal(self):
        response = self.client.post("/api/file/save", json={"path": self.outside_path, "content": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.post("/api/file/save", json={"path": self.absolute_outside_path, "content": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_edit_file_traversal(self):
        response = self.client.post("/api/file/edit", json={"filepath": self.outside_path, "content": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.post("/api/file/edit", json={"filepath": self.absolute_outside_path, "content": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_delete_file_traversal(self):
        response = self.client.post("/api/file/delete", json={"filepath": self.outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.post("/api/file/delete", json={"filepath": self.absolute_outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_bulk_delete_file_traversal(self):
        response = self.client.post("/api/file/bulk-delete", json={"filepaths": [self.absolute_outside_path]})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.absolute_outside_path, response.json()["deleted"])

    def test_rename_file_traversal(self):
        response = self.client.post("/api/file/rename", json={"filepath": self.absolute_outside_path, "new_name": "new.txt"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_insights_file_traversal(self):
        response = self.client.post("/api/file/insights", json={"filepath": self.outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

        response = self.client.post("/api/file/insights", json={"filepath": self.absolute_outside_path})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Path traversal", response.json()["detail"])

    def test_upload_file_path_traversal(self):
        outside_dest = os.path.abspath(os.path.join(main.ACTIVE_DIR, "../../traversal_upload.txt"))
        if os.path.exists(outside_dest):
            os.remove(outside_dest)

        inside_dest = os.path.join(main.ACTIVE_DIR, "traversal_upload.txt")
        if os.path.exists(inside_dest):
            os.remove(inside_dest)

        payload = {"file": ("../../traversal_upload.txt", b"path traversal upload test content", "text/plain")}
        response = self.client.post("/api/upload", files=payload)

        self.assertIn(response.status_code, [200, 400])
        self.assertFalse(os.path.exists(outside_dest))

        if response.status_code == 200:
            if os.path.exists(inside_dest):
                os.remove(inside_dest)

    def test_sync_exchange_path_traversal(self):
        from unittest.mock import patch, MagicMock
        import json

        # Prepare payload with path traversal filename
        payload = {
            "manifest": [
                {
                    "filepath": "../../outside_sync.txt",
                    "filename": "outside_sync.txt",
                    "file_size": 26,
                    "sha256": "fake_sha256_hash_here_for_traversal",
                    "modified_at": 123456789.0,
                    "content": "adversarial sync traversal content"
                }
            ]
        }

        # Setup mock response for urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        # Target file that should NOT be created outside ACTIVE_DIR
        outside_sync_file = os.path.abspath(os.path.join(main.ACTIVE_DIR, "../../outside_sync.txt"))
        if os.path.exists(outside_sync_file):
            try:
                os.remove(outside_sync_file)
            except Exception:
                pass

        inside_sync_file = os.path.join(main.ACTIVE_DIR, "outside_sync.txt")
        if os.path.exists(inside_sync_file):
            try:
                os.remove(inside_sync_file)
            except Exception:
                pass

        # Patch urlopen and make the request
        with patch("urllib.request.urlopen", return_value=mock_response):
            response = self.client.post("/api/sync/exchange", json={"target_peer": "http://localhost:8000"})
            
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists(outside_sync_file))

        # Cleanup if it created the sanitized file inside dumps
        if os.path.exists(inside_sync_file):
            try:
                os.remove(inside_sync_file)
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
