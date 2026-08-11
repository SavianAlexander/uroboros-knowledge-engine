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

class TestDomainMutation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_mutation_")
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

    def test_01_mutation_caught_corrupted_fts_query(self):
        """Verify FTS query sanitizer catches invalid inverted logic query mutations.

        Preconditions: Search query containing trailing boolean operator 'quantum NOT'.
        Invariants: Sanitization parser strips dangling syntax operators to protect FTS execution.
        Expected Outcomes: Sanitized output query string does not contain 'NOT'.
        """
        bad_query = "quantum NOT"
        sanitised = main.sanitise_fts_query(bad_query)
        self.assertNotIn("NOT", sanitised)

    def test_02_mutation_caught_oversized_ram_ingestion(self):
        """Verify RAM ingestion safety limit catches mutated file threshold boundaries.

        Preconditions: File created exceeding 50MB size limit (51MB sparse file).
        Invariants: Ingestion pipeline enforces size guard irrespective of minor configuration mutations.
        Expected Outcomes: File extraction returns string containing 'Exceeds 50MB'.
        """
        large_path = os.path.join(self.test_dir, "mutate.txt")
        with open(large_path, "wb") as f:
            f.seek(51 * 1024 * 1024)
            f.write(b"\0")

        content, _ = know.extract_content(large_path, ".txt")
        self.assertIn("Exceeds 50MB", content)

if __name__ == "__main__":
    unittest.main()
