import src.core.config as config
import src.infrastructure.database as db
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
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
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
        """Verify wildcard glob rule matching in extract_ai_tags without regex exceptions."""
        rule_matches = [("*quantum*", "quantum_physics")]
        tags = know.extract_ai_tags("Quantum computing research note", "note.txt", rule_matches)
        self.assertIn("quantum_physics", tags)

    def test_10_jupyter_notebook_extraction(self):
        """Verify structured extraction of markdown, code, and stdout from Jupyter Notebooks (.ipynb)."""
        import json
        ipynb_path = os.path.join(self.test_dir, "analysis.ipynb")
        nb_data = {
            "metadata": {"language_info": {"name": "python"}},
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["# Statistical Data Analysis\n", "Evaluating distribution parameters $E=mc^2$."]
                },
                {
                    "cell_type": "code",
                    "source": ["import math\n", "print('Variance calculated: 42.0')"],
                    "outputs": [
                        {"output_type": "stream", "text": ["Variance calculated: 42.0\n"]}
                    ]
                }
            ]
        }
        with open(ipynb_path, "w", encoding="utf-8") as f:
            json.dump(nb_data, f)

        content, coords = know.extract_content(ipynb_path, ".ipynb")
        self.assertIsInstance(content, str)
        self.assertIn("Statistical Data Analysis", content)
        self.assertIn("Variance calculated: 42.0", content)
        self.assertIn("```python", content)

    def test_11_obsidian_frontmatter_wikilinks_extraction(self):
        """Verify YAML frontmatter, dataview fields, and wikilinks extraction from Obsidian markdown."""
        md_path = os.path.join(self.test_dir, "quantum_pkm.md")
        md_text = """---
tags: [quantum, physics, computation]
aliases: [Quantum PKM, QC Notes]
date: 2026-08-13
status: active
---

# Quantum Computation Architecture
Exploring [[Quantum Algorithms|Shor's Algorithm]] and [[Superconducting Qubits]].
[priority:: high]

Inline concept #entanglement and notes.
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        content, coords = know.extract_content(md_path, ".md")
        self.assertIsInstance(content, str)
        self.assertIn("**Tags**: quantum, physics, computation", content)
        self.assertIn("**Aliases**: Quantum PKM, QC Notes", content)
        self.assertIn("**Wikilinks**: Quantum Algorithms, Superconducting Qubits", content)
        self.assertIn("Shor's Algorithm", content)

    def test_12_pptx_presentation_extraction(self):
        """Verify slide titles, bullet points, and speaker notes extraction from PowerPoint (.pptx)."""
        import zipfile
        pptx_path = os.path.join(self.test_dir, "deck.pptx")
        
        slide_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>Executive Strategy Overview</a:t></a:r></a:p>
          <a:p><a:r><a:t>High-velocity autonomous engineering</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""

        notes_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>Key talking point: emphasize zero-dependency runtime resilience.</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:notes>"""

        with zipfile.ZipFile(pptx_path, "w") as z:
            z.writestr("ppt/slides/slide1.xml", slide_xml)
            z.writestr("ppt/notesSlides/notesSlide1.xml", notes_xml)

        content, coords = know.extract_content(pptx_path, ".pptx")
        self.assertIsInstance(content, str)
        self.assertIn("Executive Strategy Overview", content)
        self.assertIn("High-velocity autonomous engineering", content)
        self.assertIn("Key talking point: emphasize zero-dependency runtime resilience.", content)

    def test_13_csv_tsv_tabular_dataset_extraction(self):
        """Verify schema type inference, summary statistics, and markdown table rendering for CSV/TSV."""
        csv_path = os.path.join(self.test_dir, "metrics.csv")
        csv_data = "TransactionID,Amount,Category,Date\nTX101,150.50,Infrastructure,2026-08-01\nTX102,320.00,Security,2026-08-02\nTX103,45.25,Compute,2026-08-03\n"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_data)

        content, coords = know.extract_content(csv_path, ".csv")
        self.assertIsInstance(content, str)
        self.assertIn("3 rows x 4 columns", content)
        self.assertIn("`Amount` (Float)", content)
        self.assertIn("`Date` (Date/ISO)", content)
        self.assertIn("| TX101 | 150.50 | Infrastructure | 2026-08-01 |", content)

if __name__ == "__main__":
    unittest.main()



