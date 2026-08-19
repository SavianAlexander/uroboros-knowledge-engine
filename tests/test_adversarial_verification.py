import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.core.config as config
import src.infrastructure.database as db
from src.infrastructure.database import reset_db_connections
import know
import main


class TestLeakageWarningGuard(unittest.TestCase):
    """Domain test verifying error-containing files bypass LLM insights to prevent leakage."""

    @classmethod
    def setUpClass(cls):
        db.DB_FILE = "test_verification_leakage.db"
        config.ACTIVE_DIR = "dumps"
        os.makedirs("dumps", exist_ok=True)
        know.init_db()

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = f"test_verification_leakage.db{suffix}"
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

    def setUp(self):
        self.conn = know.get_db()
        self.cursor = self.conn.cursor()

        self.error_cases = [
            ("dumps/parsing_error.txt", "[Parsing Error: failed to parse pdf]"),
            ("dumps/ocr_setup_error.png", "[OCR Setup Error: WinRT not initialized]"),
            ("dumps/ocr_error.jpg", "[OCR Error: WinRT OcrEngine recognize failed]"),
            ("dumps/ocr_not_supported.bmp", "[OCR not supported on this platform]"),
            ("dumps/threadpool_error.txt", "[ThreadPool Error: queue full]"),
        ]

        with self.conn:
            self.cursor.execute("DELETE FROM files")
            for filepath, content in self.error_cases:
                self.cursor.execute(
                    "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                    (filepath, filepath, len(content), 1234567, content, filepath)
                )

        self.client = TestClient(main.app)

    def tearDown(self):
        self.conn.close()

    @patch("src.core.model_manager.get_fallback_llm")
    def test_error_contents_bypass_llm_from_db(self, mock_get_llm):
        """Verify files with parser error markers return informative notice without calling LLM."""
        mock_get_llm.side_effect = AssertionError("LLM should not be called!")

        for filepath, _ in self.error_cases:
            response = self.client.post("/api/file/insights", json={"filepath": filepath})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["insights"], "*This document contains no readable text content to extract insights.*")

        mock_get_llm.assert_not_called()

    @patch("src.core.model_manager.get_fallback_llm")
    def test_error_contents_bypass_llm_from_disk_fallback(self, mock_get_llm):
        """Verify files on disk with error markers bypass LLM even when DB record is cleared."""
        mock_get_llm.side_effect = AssertionError("LLM should not be called!")

        for filepath, content in self.error_cases:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            try:
                # Clear DB to trigger disk fallback
                with know.get_db() as conn:
                    conn.cursor().execute("DELETE FROM files")

                response = self.client.post("/api/file/insights", json={"filepath": filepath})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["insights"], "*This document contains no readable text content to extract insights.*")
            finally:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass

        mock_get_llm.assert_not_called()


if __name__ == "__main__":
    unittest.main()