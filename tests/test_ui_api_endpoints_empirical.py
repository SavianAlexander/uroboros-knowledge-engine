"""
Empirical verification test suite for all 9 UI API endpoints in Uroboros Knowledge Engine.
Challenger 1 Gate Verification.
"""

import os
import sys
import unittest
import tempfile
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import main
from src.app.server import app
from src.infrastructure.database import init_db, index_directory, get_db

class TestUIAPIEndpointsEmpirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath("dumps")
        os.makedirs(cls.test_dir, exist_ok=True)
        main.ACTIVE_DIR = cls.test_dir
        cls.db_file = os.path.join(cls.test_dir, "test_ui_endpoints.db")
        main._infra_db.DB_FILE = cls.db_file
        init_db()

        # Create dummy file inside dumps dir
        cls.test_file_path = os.path.join(cls.test_dir, "empirical_test_doc.txt")
        with open(cls.test_file_path, "w", encoding="utf-8") as f:
            f.write("Empirical challenge test content for UI endpoints verification.")

        # Index directory
        index_directory(cls.test_dir)

        cls.client = TestClient(app)

    def test_01_get_file_endpoint(self):
        """1. GET /api/file - File details & metadata retrieval"""
        response = self.client.get("/api/file", params={"path": self.test_file_path})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("filepath", data)
        self.assertIn("filename", data)

    def test_02_rename_file_endpoint(self):
        """2. POST /api/file/rename - Rename file endpoint"""
        renamed_file = os.path.join(self.test_dir, "renamed_target.txt")
        if os.path.exists(renamed_file):
            try:
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(renamed_file)
            except Exception as e:
                import logging; logging.error(f"Swallowed error in test_ui_api_endpoints_empirical.py: {e}")

        # Create a specific file to rename
        target_file = os.path.join(self.test_dir, "rename_target.txt")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("Content to be renamed.")
        index_directory(self.test_dir)

        response = self.client.post(
            "/api/file/rename",
            json={"filepath": target_file, "new_name": "renamed_target.txt", "overwrite": True}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")

    def test_03_file_tag_endpoints(self):
        """3. POST /api/file/tag & DELETE /api/file/tag - Tag management endpoints"""
        # Add tag
        pos_resp = self.client.post(
            "/api/file/tag",
            json={"filepath": self.test_file_path, "tag": "empirical_tag"}
        )
        self.assertEqual(pos_resp.status_code, 200)
        self.assertEqual(pos_resp.json().get("status"), "success")

        # Remove tag
        del_resp = self.client.delete(
            f"/api/file/tag?filepath={self.test_file_path}&tag=empirical_tag"
        )
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get("status"), "success")

    def test_04_bulk_delete_endpoint(self):
        """4. POST /api/file/bulk-delete - Bulk file deletion endpoint"""
        dummy_file = os.path.join(self.test_dir, "to_delete.txt")
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write("To delete")
        index_directory(self.test_dir)

        response = self.client.post(
            "/api/file/bulk-delete",
            json={"filepaths": [dummy_file]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "success")

    def test_05_file_notes_endpoints(self):
        """5. GET /api/file/notes & POST /api/file/notes - Notes management endpoints"""
        # Save note
        save_resp = self.client.post(
            "/api/file/notes",
            json={"filepath": self.test_file_path, "notes": "Empirical note content"}
        )
        self.assertEqual(save_resp.status_code, 200)
        self.assertEqual(save_resp.json().get("status"), "success")

        # Get note
        get_resp = self.client.get("/api/file/notes", params={"filepath": self.test_file_path})
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json().get("notes"), "Empirical note content")

    def test_06_open_file_endpoint(self):
        """6. POST /api/file/open - Open file endpoint"""
        response = self.client.post(
            "/api/file/open",
            json={"filepath": self.test_file_path}
        )
        self.assertEqual(response.status_code, 200)

    def test_07_graph_endpoint(self):
        """7. GET /api/graph - Visual graph data endpoint"""
        response = self.client.get("/api/graph")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    def test_08_tags_color_endpoints(self):
        """8. GET /api/tags/color & POST /api/tags/color - Tag color customization endpoints"""
        # Save color
        save_resp = self.client.post(
            "/api/tags/color",
            json={"tag": "empirical_color_tag", "color": "#00ff00"}
        )
        self.assertEqual(save_resp.status_code, 200)

        # Get colors
        get_resp = self.client.get("/api/tags/color")
        self.assertEqual(get_resp.status_code, 200)

    def test_09_search_validate_endpoint(self):
        """9. POST /api/search/validate - Search query syntax validation endpoint"""
        response = self.client.post(
            "/api/search/validate",
            json={"query": "tag:empirical AND status:active"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("valid"))

if __name__ == "__main__":
    unittest.main()
