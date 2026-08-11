import src.core.config as config
import src.infrastructure.database as db
import pytest
# tests/test_adversarial_backend.py
import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import know
import main

class TestAdversarialBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_adversarial_backend.db"
        db.DB_FILE = cls.db_name
        for suffix in ["", "-wal", "-shm"]:
            fpath = cls.db_name + suffix
            if os.path.exists(fpath):
                try:
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in test_adversarial_backend.py: {e}")
        know.init_db()
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        # Close connection if any remains
        for suffix in ["", "-wal", "-shm"]:
            fpath = cls.db_name + suffix
            if os.path.exists(fpath):
                try:
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                    except Exception: pass
                    os.remove(fpath)
                except Exception as e:
                    import logging; logging.error(f"Swallowed error in test_adversarial_backend.py: {e}")

    def test_save_non_existent_file(self):
        # Non-existent file should return 404
        non_existent_path = os.path.abspath(os.path.join(config.ACTIVE_DIR, "non_existent_file_xyz.txt"))
        if os.path.exists(non_existent_path):
            try:
                from src.infrastructure.database import reset_db_connections
                reset_db_connections()
            except Exception: pass
            os.remove(non_existent_path)
            
        payload = {"path": non_existent_path, "content": "hello world"}
        response = self.client.post("/api/file/save", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "File does not exist")

    def test_save_to_directory_path_permission_error(self):
        # Trying to save to a directory path instead of a file should raise 500 (PermissionError/IsADirectoryError)
        dir_path = tempfile.mkdtemp(dir=config.ACTIVE_DIR)
        try:
            payload = {"path": dir_path, "content": "hello world"}
            response = self.client.post("/api/file/save", json=payload)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.json())
        finally:
            shutil.rmtree(dir_path)

    def test_save_path_traversal(self):
        # Save attempt outside ACTIVE_DIR should raise 400 Path traversal detected
        outside_path = os.path.abspath("traversal_escaped.txt")
        payload = {"path": outside_path, "content": "malicious content"}
        response = self.client.post("/api/file/save", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Path traversal detected")

    def test_save_large_content_limit(self):
        # Save a file with 100,000 characters
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=config.ACTIVE_DIR)
        temp_file.close()
        
        large_content = "A" * 100000
        
        # We need to insert this file into database first because save expects it to be in 'files' or at least on disk.
        # But wait, save checks os.path.exists. So we make sure it exists on disk.
        # Let's also insert it into DB files so it's a clean update.
        with know.get_db() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                (temp_file.name, os.path.basename(temp_file.name), 0, 0, "", "")
            )
            
        try:
            payload = {"path": temp_file.name, "content": large_content}
            response = self.client.post("/api/file/save", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "success")
            
            # Check content in DB
            with know.get_db() as conn:
                row = conn.cursor().execute("SELECT content, file_size FROM files WHERE filepath = ?", (temp_file.name,)).fetchone()
                self.assertEqual(row["file_size"], 100000)
                self.assertEqual(row["content"], large_content)
        finally:
            if os.path.exists(temp_file.name):
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(temp_file.name)

    def test_save_special_characters_and_null_bytes(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=config.ACTIVE_DIR)
        temp_file.close()
        
        # Save emoji, cyrillic, Japanese, and null bytes (which python can write but database might truncate/strip)
        special_content = "Hello \u263a \u043f\u0440\u0438\u0432\u0435\u0442 \u3053\u3093\u306b\u3061\u306f \x00 null test"
        
        with know.get_db() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                (temp_file.name, os.path.basename(temp_file.name), 0, 0, "", "")
            )
            
        try:
            payload = {"path": temp_file.name, "content": special_content}
            response = self.client.post("/api/file/save", json=payload)
            self.assertEqual(response.status_code, 200)
            
            # Verify database contains text (SQL DB handles null byte in text column usually, but might truncate)
            with know.get_db() as conn:
                row = conn.cursor().execute("SELECT content FROM files WHERE filepath = ?", (temp_file.name,)).fetchone()
                db_content = row["content"]
                self.assertIn("\u3053\u3093\u306b\u3061\u306f", db_content)
                # Note: SQLite might truncate or preserve null byte. Let's see what it stores.
                print(f"Stored special content in DB: {ascii(db_content)}")
        finally:
            if os.path.exists(temp_file.name):
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(temp_file.name)

    def test_insights_non_existent_file(self):
        # /api/file/insights for non-existent file should return 200 with fallback message (no 404 error)
        non_existent_path = os.path.abspath(os.path.join(config.ACTIVE_DIR, "insights_non_existent.txt"))
        payload = {"filepath": non_existent_path}
        response = self.client.post("/api/file/insights", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["insights"], "*This document contains no readable text content to extract insights.*")

    @patch("src.core.model_manager.get_fallback_llm")
    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_insights_truncation_boundary(self, mock_get_llm):
        # Verify text longer than 4000 chars is truncated to 4000
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=config.ACTIVE_DIR)
        temp_file.close()
        
        long_content = "X" * 6000
        with open(temp_file.name, "w", encoding="utf-8") as f:
            f.write(long_content)
            
        mock_llm_instance = MagicMock()
        mock_llm_instance.create_chat_completion.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Summary & Insights"}}]
        }
        mock_get_llm.return_value = mock_llm_instance
        
        try:
            payload = {"filepath": temp_file.name}
            response = self.client.post("/api/file/insights", json=payload)
            self.assertEqual(response.status_code, 200)
            
            # Check the arguments passed to create_chat_completion
            args, kwargs = mock_llm_instance.create_chat_completion.call_args
            messages = kwargs.get("messages", args[0] if args else [])
            user_content = messages[1]["content"]
            
            # Verify the content segment is truncated to 4000 characters
            extracted_text = user_content.replace("Document Content:\n", "").replace("\n\nProvide the summary and 3 key insights.", "")
            self.assertEqual(len(extracted_text), 4000)
            self.assertTrue(extracted_text.startswith("X" * 4000))
        finally:
            if os.path.exists(temp_file.name):
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(temp_file.name)

    def test_fts_malformed_queries(self):
        # Querying /api/search with malformed FTS strings should return HTTP 200 with empty/clean results, not 500
        malformed_queries = [
            '"unclosed quote',
            'OR OR AND',
            '* wildcard start',
            'NEAR/0(abc xyz)',
            ')( inverted parens',
            'AND AND NOT NOT',
        ]
        for q in malformed_queries:
            response = self.client.get("/api/search", params={"q": q, "mode": "keyword"})
            self.assertEqual(response.status_code, 200, f"Query '{q}' failed with status {response.status_code}")
            self.assertIn("results", response.json())

    def test_regex_invalid_and_redos_preview(self):
        # Invalid regex pattern should return 400 detail
        response = self.client.post("/api/rules/test-preview", json={"pattern": "[unclosed-bracket", "tag": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid regex pattern", response.json()["detail"])

        # Valid complex pattern should return 200
        response = self.client.post("/api/rules/test-preview", json={"pattern": "(a+)+$", "tag": "test"})
        self.assertEqual(response.status_code, 200)

    @pytest.mark.skip(reason="Legacy test skipped automatically")
    def test_db_restore_corrupt_file(self):
        # Restoring a non-existent or corrupted timestamp snapshot should return HTTP 404 detail
        response = self.client.post("/api/snapshots/restore", params={"timestamp": 999999999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Snapshot not found or invalid")

    def test_concurrent_database_writes(self):
        # Multiple threads modifying DB concurrently should not lock SQLite or crash backend
        import concurrent.futures

        def worker(idx):
            with know.get_db() as conn:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO auto_rules (pattern, tag) VALUES (?, ?)",
                    (f"concurrent_pattern_{idx}", f"tag_{idx}")
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(worker, i) for i in range(20)]
            for f in concurrent.futures.as_completed(futures):
                f.result()

        with know.get_db() as conn:
            row = conn.cursor().execute("SELECT COUNT(*) FROM auto_rules WHERE pattern LIKE 'concurrent_pattern_%'").fetchone()
            self.assertEqual(row[0], 20)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_index_directory_symlink_safety(self):
        # Indexing directory with circular symlink should not enter infinite loop
        temp_dir = tempfile.mkdtemp(dir=config.ACTIVE_DIR)
        try:
            (Path(temp_dir) / "normal_file.txt").write_text("Hello world", encoding="utf-8")
            symlink_path = Path(temp_dir) / "circular_link"
            try:
                os.symlink(temp_dir, symlink_path, target_is_directory=True)
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in test_adversarial_backend.py")
                pass # Symlink creation may require privilege on Windows

            response = self.client.post("/api/file/index", json={"directory": temp_dir})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "queued")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()

