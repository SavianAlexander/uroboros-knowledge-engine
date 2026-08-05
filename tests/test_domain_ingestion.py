import unittest
import os
import shutil
import tempfile
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainIngestion(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_ingest_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_text_file_ingestion(self):
        """Verify standard text file content extraction and database indexing.

        Preconditions: Plain text note written to test directory.
        Invariants: Ingestion engine parses file content and stores record in database.
        Expected Outcomes: Querying files table yields non-null record containing extracted text.
        """
        sample_path = os.path.join(self.test_dir, "quantum_note.txt")
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write("Quantum mechanics and general relativity principles.")

        know.index_directory(self.test_dir)
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, content FROM files WHERE filename = 'quantum_note.txt'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertIn("Quantum mechanics", row['content'])
        conn.close()

    def test_02_auto_tag_extraction(self):
        """Verify automatic AI keyword tag extraction based on document content rules.

        Preconditions: Content text and filename matching rule keywords.
        Invariants: extract_ai_tags evaluates content against tag taxonomy.
        Expected Outcomes: Returned tag list includes expected domain tag 'science'.
        """
        tags = know.extract_ai_tags("Financial report and astrophysics data", "report.pdf")
        self.assertIn("science", tags)

    def test_03_empty_file_ingestion(self):
        """Verify ingestion handling of empty 0-byte text files without crashing.

        Preconditions: Zero-byte text file created in test directory.
        Invariants: Indexer handles empty files gracefully and registers record.
        Expected Outcomes: Record for empty file exists in database.
        """
        empty_path = os.path.join(self.test_dir, "empty.txt")
        with open(empty_path, "w", encoding="utf-8") as f:
            f.write("")

        know.index_directory(self.test_dir)
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM files WHERE filename = 'empty.txt'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        conn.close()

    def test_04_50mb_size_limit_guard(self):
        """Verify RAM safety guard skips files exceeding 50MB size limit.

        Preconditions: Large file exceeding 50MB threshold created.
        Invariants: Content extractor checks file size before loading into memory.
        Expected Outcomes: Extracted content string contains 'Exceeds 50MB' warning notice.
        """
        large_path = os.path.join(self.test_dir, "large_mock.txt")
        with open(large_path, "wb") as f:
            f.seek(51 * 1024 * 1024)
            f.write(b"\0")

        content, coords = know.extract_content(large_path, ".txt")
        self.assertIn("Exceeds 50MB", content)

    def test_05_audio_metadata_fallback(self):
        """Verify audio metadata extraction fallback for unsupported binary files.

        Preconditions: Audio file path provided for metadata parsing.
        Invariants: Extractor returns structured dictionary regardless of binary availability.
        Expected Outcomes: Returned object is instance of dict.
        """
        audio_meta = know.parse_audio_metadata("/nonexistent/file.wav")
        self.assertIsInstance(audio_meta, dict)

    def test_06_unknown_extension_fallback(self):
        """Verify safe plain-text fallback extraction for files with unknown extensions.

        Preconditions: File created with unknown file extension .xyz_unknown.
        Invariants: Extractor falls back to UTF-8 text reading without raising error.
        Expected Outcomes: Returned content is instance of str.
        """
        unknown_path = os.path.join(self.test_dir, "custom.xyz_unknown")
        with open(unknown_path, "w", encoding="utf-8") as f:
            f.write("Plain text fallback test content.")

        content, coords = know.extract_content(unknown_path, ".xyz_unknown")
        self.assertIsInstance(content, str)

    def test_07_deep_nested_directories(self):
        """Verify recursive directory indexing across 10-level deep folder hierarchies.

        Preconditions: File created inside 10-level nested directory structure.
        Invariants: Recursive directory traversal visits deep paths and indexes files.
        Expected Outcomes: Database record exists for file located in deep directory.
        """
        deep_dir = os.path.join(self.test_dir, "a", "b", "c", "d", "e", "f", "g", "h", "i", "j")
        os.makedirs(deep_dir, exist_ok=True)
        deep_file = os.path.join(deep_dir, "deep.txt")
        with open(deep_file, "w", encoding="utf-8") as f:
            f.write("Deep nested content")

        know.index_directory(self.test_dir)
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM files WHERE filename = 'deep.txt'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        conn.close()

    def test_08_rtf_and_ocr_coords_extraction(self):
        """Verify RTF text stripping and OCR coordinate table insertion.

        Preconditions: Sample RTF document and OCR bounding box coordinates provided.
        Invariants: RTF markup stripped to plain text; OCR coordinates committed to ocr_coords.
        Expected Outcomes: Extracted content contains 'Quantum RTF text' and OCR query returns 'Quantum'.
        """
        rtf_path = os.path.join(self.test_dir, "sample.rtf")
        rtf_raw = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}} \f0\fs24 Quantum RTF text.}"
        with open(rtf_path, "w", encoding="utf-8") as f:
            f.write(rtf_raw)

        content, coords = know.extract_content(rtf_path, ".rtf")
        self.assertIsInstance(content, str)
        self.assertIn("Quantum RTF text", content)

        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (filepath, filename, content) VALUES ('/tmp/ocr.png', 'ocr.png', 'OCR text')")
        file_id = cursor.lastrowid
        cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?)", (file_id, "Quantum", 10, 20, 50, 15))
        conn.commit()

        cursor.execute("SELECT word FROM ocr_coords WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        self.assertEqual(row['word'], "Quantum")
        conn.close()

    def test_09_wildcard_rule_matching(self):
        """Verify wildcard glob rule matching in extract_ai_tags without regex exceptions.

        Preconditions: Tag rule defined with wildcard pattern (*quantum*).
        Invariants: Pattern matching evaluates glob wildcards against document text.
        Expected Outcomes: Extracted tags include rule target 'quantum_physics'.
        """
        rule_matches = [("*quantum*", "quantum_physics")]
        tags = know.extract_ai_tags("Quantum computing research note", "note.txt", rule_matches)
        self.assertIn("quantum_physics", tags)

if __name__ == "__main__":
    unittest.main()



