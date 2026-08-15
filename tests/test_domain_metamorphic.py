import os
import sys
import time
import tempfile
import unittest
import shutil
import sqlite3
import hashlib

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, init_db
from src.infrastructure.repositories.files import save_file_revision, get_file_revisions, revert_file_revision
from src.infrastructure.vector_engine import index_directory
from src.infrastructure.parsers import safe_write_file, safe_read_file, calculate_sha256
from src.core.domain.services import chunk_text, sanitise_fts_query, reciprocal_rank_fusion

class TestDomainMetamorphic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_metamorphic_")
        self.db_path = os.path.join(self.test_dir, "test_metamorphic.db")
        self.orig_db_file = db_module.DB_FILE
        db_module.DB_FILE = self.db_path
        db_module.reset_db_connections()
        init_db()

        self.doc1 = os.path.join(self.test_dir, "doc1.txt")
        self.doc2 = os.path.join(self.test_dir, "doc2.txt")
        self.doc3 = os.path.join(self.test_dir, "doc3.txt")

        safe_write_file(self.doc1, "quantum computing astrophysics astrophysics research")
        safe_write_file(self.doc2, "quantum mechanics physics equations")
        safe_write_file(self.doc3, "astrophysics cosmology space research")

        index_directory(self.test_dir)

    def tearDown(self):
        db_module.reset_db_connections()
        db_module.DB_FILE = self.orig_db_file
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_mr1_fts_conjunction_set_containment(self):
        """Verify Metamorphic Relation 1: Search(A AND B) MUST be a subset of Search(A).

        Preconditions: Sample text documents indexed into FTS database.
        Invariants: Conjunction query (A AND B) narrows result set relative to single term search (A).
        Expected Outcomes: Result set for 'quantum AND mechanics' is a subset of result set for 'quantum'.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ?", ("quantum",))
            results_a = set(r[0] for r in cursor.fetchall())

            cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ?", ("quantum AND mechanics",))
            results_a_and_b = set(r[0] for r in cursor.fetchall())

            self.assertTrue(
                results_a_and_b.issubset(results_a),
                f"Metamorphic Relation 1 Violated: {results_a_and_b} is not subset of {results_a}"
            )

    def test_02_mr2_fts_disjunction_expansion(self):
        """Verify Metamorphic Relation 2: Search(A) MUST be a subset of Search(A OR B).

        Preconditions: Sample text documents indexed into FTS database.
        Invariants: Disjunction query (A OR B) expands result set relative to single term search (A).
        Expected Outcomes: Result set for 'astrophysics' is a subset of result set for 'astrophysics OR cosmology'.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ?", ("astrophysics",))
            results_a = set(r[0] for r in cursor.fetchall())

            cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ?", ("astrophysics OR cosmology",))
            results_a_or_b = set(r[0] for r in cursor.fetchall())

            self.assertTrue(
                results_a.issubset(results_a_or_b),
                f"Metamorphic Relation 2 Violated: {results_a} is not subset of {results_a_or_b}"
            )

    def test_03_mr3_revision_reversibility_invariant(self):
        """Verify Metamorphic Relation 3: Reverting revision 1 MUST restore exact original content C1.

        Preconditions: Original content written and saved as initial revision, then updated with second revision.
        Invariants: Reverting revision history restores exact byte string of first revision.
        Expected Outcomes: Content read from disk matches original version string after revert.
        """
        original_content = "Original Document Version 1.0"
        updated_content = "Modified Document Version 2.0"

        rev_file = os.path.join(self.test_dir, "rev_file.txt")
        safe_write_file(rev_file, original_content)
        save_file_revision(rev_file, original_content)

        safe_write_file(rev_file, updated_content)
        save_file_revision(rev_file, updated_content)

        revisions = get_file_revisions(rev_file)
        self.assertTrue(len(revisions) >= 2)

        first_rev_id = revisions[-1]["id"]
        revert_file_revision(rev_file, first_rev_id)

        restored = safe_read_file(rev_file).decode("utf-8")
        self.assertEqual(restored, original_content, "Reversibility Invariant Violated!")

    def test_04_mr4_chunk_length_coverage_invariant(self):
        """Verify Metamorphic Relation 4: Sum of chunk lengths with overlap MUST be >= original text length.

        Preconditions: Target text string provided to chunk_text with specified chunk_size and overlap.
        Invariants: Chunking with overlap covers entire input string without missing characters.
        Expected Outcomes: Total length of all generated text chunks is greater than or equal to original text length.
        """
        text = "Deep learning networks analyze complex high-dimensional feature spaces for accurate prediction." * 10
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        total_chunk_length = sum(len(c) for c in chunks)
        self.assertGreaterEqual(
            total_chunk_length,
            len(text),
            f"Chunk Coverage Invariant Violated: {total_chunk_length} < {len(text)}"
        )

    def test_05_mr5_sha256_idempotency_invariant(self):
        """Verify Metamorphic Relation 5: SHA-256 calculation MUST be deterministic and idempotent.

        Preconditions: File written to temporary test directory.
        Invariants: SHA-256 digest function returns identical hash value on repeated execution.
        Expected Outcomes: Hash values from consecutive calls match identically and length is 64 hex characters.
        """
        hash1 = calculate_sha256(self.doc1)
        hash2 = calculate_sha256(self.doc1)
        self.assertEqual(hash1, hash2, "SHA-256 Idempotency Invariant Violated!")
        self.assertEqual(len(hash1), 64)

    def test_06_mr6_differential_search_engine_parity(self):
        """Verify Metamorphic Relation 6: Differential parity check between FTS5 and substring matching.

        Preconditions: Documents indexed in both SQLite FTS5 table and standard files table.
        Invariants: FTS index matching matches Python substring search for single search terms.
        Expected Outcomes: Filepath set returned by FTS MATCH equals filepath set returned by naive substring scan.
        """
        search_term = "cosmology"
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ?", (search_term,))
            fts_matches = set(r[0] for r in cursor.fetchall())

            cursor.execute("SELECT filepath, content FROM files")
            ref_matches = set(row[0] for row in cursor.fetchall() if search_term in (row[1] or ""))

            self.assertEqual(fts_matches, ref_matches, "Differential Search Engine Parity Violated!")

if __name__ == "__main__":
    unittest.main()
