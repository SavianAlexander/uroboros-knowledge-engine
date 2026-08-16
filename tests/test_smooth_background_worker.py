"""
Unit test suite verifying cooperative zero-stutter background summarizer daemon.
"""
import unittest
import time
import os
import shutil
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch

import src.infrastructure.database as db
from src.infrastructure.database import get_db, reset_db_connections
from src.domain.background_worker import (
    DocumentSummarizerDaemon,
    set_current_thread_idle_priority
)


class TestSmoothBackgroundWorker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="worker_test_")
        self.db_file = os.path.join(self.test_dir, "test_vault.db")
        self.orig_db = db.DB_FILE
        db.DB_FILE = self.db_file
        os.environ["DB_FILE"] = self.db_file
        reset_db_connections()

        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 0,
                    filepath TEXT UNIQUE,
                    filename TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    sha256 TEXT,
                    modified_at REAL,
                    content TEXT,
                    metadata_json TEXT
                )
            """)

    def tearDown(self):
        reset_db_connections()
        db.DB_FILE = self.orig_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_thread_idle_priority_execution(self):
        """Test #1: Verify thread idle priority call executes safely."""
        try:
            set_current_thread_idle_priority()
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

    def test_boot_grace_and_clean_stop(self):
        """Test #2: Verify daemon initializes with boot grace and stops immediately."""
        daemon = DocumentSummarizerDaemon(boot_grace_seconds=1, cooloff_seconds=1, idle_interval_seconds=1)
        daemon.start()
        self.assertTrue(daemon.is_alive())
        time.sleep(0.2)
        daemon.stop()
        daemon.join(timeout=2.0)
        self.assertFalse(daemon.is_alive())

    def test_process_single_unsummarized_document_skips_when_empty(self):
        """Test #3: When no documents need summary, returns False without spinning."""
        daemon = DocumentSummarizerDaemon(boot_grace_seconds=0)
        result = daemon.process_single_unsummarized_document()
        self.assertFalse(result)

    def test_process_single_unsummarized_document_processes_one(self):
        """Test #4: Processes exactly 1 document and stores summary in JSON metadata."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                "INSERT INTO files (filename, filepath, content) VALUES (?, ?, ?)",
                ("server_arch.md", "/vault/server_arch.md", "Architecture notes for scalable zero-stutter background queues.")
            )

        # Mock LLM completion
        mock_llm = MagicMock()
        mock_llm.create_chat_completion.return_value = {
            "choices": [{"message": {"content": "Scalable server architecture summary."}}]
        }

        with patch("src.core.model_manager.get_fallback_llm", return_value=mock_llm):
            daemon = DocumentSummarizerDaemon(boot_grace_seconds=0)
            did_work = daemon.process_single_unsummarized_document()
            self.assertTrue(did_work)

            # Verify summary was written to database
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT metadata_json FROM files WHERE filename = 'server_arch.md'")
                row = cursor.fetchone()
                self.assertIsNotNone(row)
                self.assertIn("Scalable server architecture summary", row[0])

            # Running again should return False since it is now already summarized
            did_work_again = daemon.process_single_unsummarized_document()
            self.assertFalse(did_work_again)


if __name__ == "__main__":
    unittest.main()
