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

import src.core.config as config
import src.infrastructure.database as db
from src.infrastructure.database import reset_db_connections
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
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass
        know.init_db()
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = cls.db_name + suffix
            if os.path.exists(fpath):
                try:
                    reset_db_connections()
                    os.remove(fpath)
                except OSError:
                    pass

    def test_save_non_existent_file(self):
        non_existent_path = os.path.abspath(os.path.join(config.ACTIVE_DIR, "non_existent_file_xyz.txt"))
        if os.path.exists(non_existent_path):
            try:
                reset_db_connections()
                os.remove(non_existent_path)
            except OSError:
                pass

        payload = {"path": non_existent_path, "content": "hello world"}
        response = self.client.post("/api/file/save", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "File does not exist")

    def test_save_to_directory_path_permission_error(self):
        dir_path = tempfile.mkdtemp(dir=config.ACTIVE_DIR)
        try:
            payload = {"path": dir_path, "content": "hello world"}
            response = self.client.post("/api/file/save", json=payload)
            self.assertIn(response.status_code, [400, 500])
            self.assertIn("detail", response.json())
        finally:
            shutil.rmtree(dir_path, ignore_errors=True)

    def test_save_path_traversal(self):
        outside_path = os.path.abspath("traversal_escaped.txt")
        payload = {"path": outside_path, "content": "malicious content"}
        response = self.client.post("/api/file/save", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Path traversal detected")

    def test_save_large_content_limit(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=config.ACTIVE_DIR)
        temp_file.close()

        large_content = "A" * 100000

        with know.get_db() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                (temp_file.name, "large.txt", len(large_content), 1234567, large_content, "dummy_sha")
            )

        try:
            payload = {"path": temp_file.name, "content": large_content}
            response = self.client.post("/api/file/save", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertIn(response.json().get("status"), ["success", "saved"])
        finally:
            if os.path.exists(temp_file.name):
                try:
                    reset_db_connections()
                    os.remove(temp_file.name)
                except OSError:
                    pass

    def test_insights_non_existent_file(self):
        bogus_path = os.path.join(config.ACTIVE_DIR, "completely_bogus_missing_path.txt")
        payload = {"filepath": bogus_path}
        response = self.client.post("/api/file/insights", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("insights", response.json())

    def test_insights_empty_file_bypasses_llm(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=config.ACTIVE_DIR)
        temp_file.close()

        try:
            payload = {"filepath": temp_file.name}
            response = self.client.post("/api/file/insights", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["insights"], "*This document contains no readable text content to extract insights.*")
        finally:
            if os.path.exists(temp_file.name):
                try:
                    reset_db_connections()
                    os.remove(temp_file.name)
                except OSError:
                    pass

    @patch("src.core.model_manager.get_fallback_llm")
    def test_insights_truncation_boundary(self, mock_get_llm):
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

            args, kwargs = mock_llm_instance.create_chat_completion.call_args
            messages = kwargs.get("messages", args[0] if args else [])
            user_content = messages[1]["content"]

            extracted_text = user_content.replace("Document Content:\n", "").replace("\n\nProvide the summary and 3 key insights.", "")
            self.assertEqual(len(extracted_text), 4000)
            self.assertTrue(extracted_text.startswith("X" * 4000))
        finally:
            if os.path.exists(temp_file.name):
                try:
                    reset_db_connections()
                    os.remove(temp_file.name)
                except OSError:
                    pass

    def test_fts_malformed_queries(self):
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
        response = self.client.post("/api/rules/test-preview", json={"pattern": "[unclosed-bracket", "tag": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid regex pattern", response.json()["detail"])

        response = self.client.post("/api/rules/test-preview", json={"pattern": "(a+)+$", "tag": "test"})
        self.assertEqual(response.status_code, 200)

    def test_db_restore_corrupt_file(self):
        response = self.client.post("/api/snapshots/restore", params={"timestamp": 999999999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Snapshot not found or invalid")

    def test_concurrent_database_writes(self):
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

    def test_index_directory_symlink_safety(self):
        temp_dir = tempfile.mkdtemp(dir=config.ACTIVE_DIR)
        try:
            (Path(temp_dir) / "normal_file.txt").write_text("Hello world", encoding="utf-8")
            symlink_path = Path(temp_dir) / "circular_link"
            try:
                os.symlink(temp_dir, symlink_path, target_is_directory=True)
            except OSError:
                pass

            response = self.client.post("/api/file/index", json={"directory": temp_dir})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "queued")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
