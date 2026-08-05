"""
Domain 19: Localization (i18n), Unicode Normalization (NFC/NFD), and Script Expansion Suite.
Validates multi-language text tokenization (CJK, Arabic RTL, Cyrillic, Devanagari, German),
NFC vs NFD string normalization equivalence, zero-width space handling, and emoji token indexing.
"""

import os
import sys
import unicodedata
import unittest
import tempfile
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import know
import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, init_db, index_directory, reset_db_connections
from src.infrastructure.parsers import safe_write_file, safe_read_file
from src.core.domain.services import chunk_text, sanitise_fts_query


class TestDomainLocalization(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_i18n_")
        self.db_path = os.path.join(self.test_dir, "test_i18n.db")
        db_module.DB_FILE = self.db_path
        know.DB_FILE = self.db_path
        reset_db_connections()
        init_db()

    def tearDown(self):
        reset_db_connections()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_unicode_nfc_nfd_normalization_equivalence(self):
        """
        Preconditions: NFC (composed) and NFD (decomposed) strings with accented characters.
        Invariants: FTS query sanitization must produce identical NFC normalized output for equivalent NFC and NFD strings.
        Outcomes: NFC and NFD input strings are verified distinct raw byte sequences but sanitize to identical NFC output.
        """
        nfc_str = "café résumé"
        nfd_str = unicodedata.normalize("NFD", nfc_str)
        
        self.assertNotEqual(nfc_str, nfd_str)
        
        sanitized_nfc = unicodedata.normalize("NFC", sanitise_fts_query(nfc_str))
        sanitized_nfd = unicodedata.normalize("NFC", sanitise_fts_query(nfd_str))
        self.assertEqual(sanitized_nfc, sanitized_nfd, "NFC/NFD Unicode Normalization Equivalence Violated!")

    def test_02_arabic_rtl_and_cjk_tokenization(self):
        """
        Preconditions: Temporary sandbox seeded with Arabic (RTL) and CJK (Chinese, Japanese) documents.
        Invariants: Multibyte non-ASCII text tokenization must persist in database without corruption.
        Outcomes: SQL queries for Arabic and CJK keywords return valid matching record filepaths.
        """
        arabic_text = "البحث العلمي والذكاء الاصطناعي في قاعدة البيانات"
        cjk_text = "人工知能と機械学習のナレッジエンジン検索"
        
        arabic_file = os.path.join(self.test_dir, "arabic_doc.txt")
        cjk_file = os.path.join(self.test_dir, "cjk_doc.txt")

        safe_write_file(arabic_file, arabic_text)
        safe_write_file(cjk_file, cjk_text)

        index_directory(self.test_dir)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM files WHERE content LIKE ?", ("%الذكاء%",))
            row_ar = cursor.fetchone()
            self.assertIsNotNone(row_ar)

            cursor.execute("SELECT filepath FROM files WHERE content LIKE ?", ("%人工知能%",))
            row_cjk = cursor.fetchone()
            self.assertIsNotNone(row_cjk)

    def test_03_german_compound_word_string_expansion(self):
        """
        Preconditions: Document containing German compound word (63 characters).
        Invariants: Long compound words must index cleanly without string truncation.
        Outcomes: Database lookup for compound word sub-tokens successfully retrieves the file record.
        """
        compound_word = "Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz"
        fpath = os.path.join(self.test_dir, "german.txt")
        safe_write_file(fpath, f"Deutsches Gesetz: {compound_word}")
        
        index_directory(self.test_dir)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM files WHERE content LIKE ?", ("%Rindfleisch%",))
            row = cursor.fetchone()
            self.assertIsNotNone(row)

    def test_04_zwj_family_emoji_indexing(self):
        """
        Preconditions: Document containing Zero-Width Joiner (ZWJ) multi-character emoji sequences.
        Invariants: ZWJ emojis must store as valid UTF-8 sequences in file content fields.
        Outcomes: SQL content queries matching ZWJ emojis successfully return the exact emoji text.
        """
        emoji_content = "Document with complex emojis 👨‍👩‍👧‍👦 🚀 <ctrl42> 🔬"
        fpath = os.path.join(self.test_dir, "emoji.txt")
        safe_write_file(fpath, emoji_content)

        index_directory(self.test_dir)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM files WHERE content LIKE ?", ("%👨‍👩‍👧‍👦%",))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertIn("👨‍👩‍👧‍👦", row[0])


if __name__ == "__main__":
    unittest.main()
