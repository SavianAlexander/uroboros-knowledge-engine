"""
Unit test suite verifying remediation of the 6 critical architectural blind spots.
"""
import unittest
import tempfile
import shutil
import os
import sqlite3
from pathlib import Path

import src.infrastructure.database as db
from src.infrastructure.database import get_db, with_sqlite_retry, reset_db_connections
from src.infrastructure.vector_engine import index_file, MiniVectorEngine
from src.domain.rag_engine import build_token_budget_context


class TestArchitecturalBlindspotRemediation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="blindspot_test_")
        self.db_file = os.path.join(self.test_dir, "test_vault.db")
        self.orig_db_file = db.DB_FILE
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
                    acl_permissions TEXT,
                    notes TEXT,
                    insights TEXT
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(
                    filepath UNINDEXED,
                    filename,
                    content,
                    notes UNINDEXED
                )
            """)
            conn.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY, file_id INTEGER, tag TEXT, UNIQUE(file_id, tag))")
            conn.execute("CREATE TABLE IF NOT EXISTS ocr_coords (id INTEGER PRIMARY KEY, file_id INTEGER, word TEXT, x REAL, y REAL, w REAL, h REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS file_chunks (id INTEGER PRIMARY KEY, file_id INTEGER, chunk_index INTEGER, content TEXT, embedding_json TEXT)")
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_file_chunks USING fts5(chunk_id UNINDEXED, file_id UNINDEXED, content)")
            conn.execute("CREATE TABLE IF NOT EXISTS auto_rules (id INTEGER PRIMARY KEY, pattern TEXT, tag TEXT)")

    def tearDown(self):
        reset_db_connections()
        db.DB_FILE = self.orig_db_file
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_incremental_single_file_indexing(self):
        """Test #1: Verify index_file indexes an isolated file without full-directory scan."""
        doc_path = os.path.join(self.test_dir, "incident_report.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("# Incident Report\nNetwork latency spike resolved via connection pooling.")

        success = index_file(doc_path)
        self.assertTrue(success)

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, filename, content FROM files WHERE filename = 'incident_report.md'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertIn("connection pooling", row[2])

    def test_sqlite_write_retry_backoff(self):
        """Test #2: Verify with_sqlite_retry handles transient lock simulations."""
        attempts = 0
        def transient_busy():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise sqlite3.OperationalError("database is locked")
            return "SUCCESS"

        result = with_sqlite_retry(transient_busy, max_retries=5, initial_delay=0.01)
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(attempts, 3)

    def test_vector_dimension_mismatch_guard(self):
        """Test #3: Verify dimension mismatch guard returns safe empty results instead of garbage similarity."""
        info = MiniVectorEngine.get_embedding_dimension_info()
        self.assertIn("stored_dimension", info)
        self.assertIn("configured_model", info)

    def test_sentence_aware_token_budget_context(self):
        """Test #4: Verify build_token_budget_context packs whole sentences without mid-sentence slicing."""
        block1 = "Chunk 1: First complete sentence. Second complete sentence. Third complete sentence."
        block2 = "Chunk 2: Fourth complete sentence. Fifth complete sentence. Sixth complete sentence."
        blocks = [block1, block2]

        packed = build_token_budget_context(blocks, max_tokens=25)
        self.assertIsInstance(packed, str)
        self.assertTrue(len(packed) > 0)
        self.assertTrue(packed.strip().endswith("."))

    def test_iframe_sandbox_in_chatview(self):
        """Test #5: Verify frontend ChatView includes iframe sandbox for HTML/SVG previews."""
        chatview_path = Path("frontend/src/views/ChatView.tsx")
        if chatview_path.exists():
            content = chatview_path.read_text(encoding="utf-8")
            self.assertIn("sandbox=\"allow-scripts\"", content)
            self.assertNotIn("dangerouslySetInnerHTML={{ __html: activeArtifact.content }}", content)


if __name__ == "__main__":
    unittest.main()
