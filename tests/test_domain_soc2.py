import unittest
import os
import shutil
import tempfile
import sys
import re

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainSOC2(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_soc2_")
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

    def test_01_soc2_security_zero_secret_leakage(self):
        """Verify zero plaintext API keys, AWS credentials, or private keys exist in codebase.

        Preconditions: Source tree scanned across .py, .js, .json, .html, .css, .md files.
        Invariants: Regex patterns for AWS keys, GitHub tokens, and private key headers find no matches.
        Expected Outcomes: Detected secret leaks list length is exactly 0.
        """
        prefix_ghp = "ghp_"
        prefix_aws = "AKIA"
        prefix_pem = "-----BEGIN " + "PRIVATE KEY-----"
        secret_patterns = [
            re.compile(rf'{prefix_aws}[0-9A-Z]{{16}}'),
            re.compile(rf'{prefix_ghp}[a-zA-Z0-9]{{36}}'),
            re.compile(rf'{prefix_pem}')
        ]

        leaks = []
        for root, _, files in os.walk(root_dir):
            if ".git" in root or ".venv" in root or "__pycache__" in root or "dist" in root or "build" in root or ".gemini" in root:
                continue
            for f_name in files:
                if f_name.endswith(('.py', '.js', '.json', '.html', '.css', '.md')):
                    f_path = os.path.join(root, f_name)
                    try:
                        with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for pat in secret_patterns:
                                if pat.search(content):
                                    leaks.append(f_path)
                    except Exception as e:
                        import logging; logging.error(f"Swallowed error in test_domain_soc2.py: {e}")

        self.assertEqual(len(leaks), 0, f"SOC 2 Security Violation: Secrets detected in {leaks}")

    def test_02_soc2_availability_resource_guard(self):
        """Verify 50MB file size safety ceiling guard prevents memory exhaustion.

        Preconditions: 51MB sparse text file created in temporary test directory.
        Invariants: Text extractor checks file size before reading full contents into RAM memory.
        Expected Outcomes: Content extraction returns placeholder indicating size exceeds 50MB.
        """
        large_path = os.path.join(self.test_dir, "soc2_large.txt")
        with open(large_path, "wb") as f:
            f.seek(51 * 1024 * 1024)
            f.write(b"\0")

        content, _ = know.extract_content(large_path, ".txt")
        self.assertIn("Exceeds 50MB", content)

    def test_03_soc2_processing_integrity_sha256_verification(self):
        """Verify SHA-256 cryptographic file checksum calculation for data integrity verification.

        Preconditions: Text file written with deterministic payload string in test directory.
        Invariants: calculate_sha256 computes 256-bit hexadecimal digest string.
        Expected Outcomes: Resulting hash digest string length is exactly 64 hexadecimal characters.
        """
        sample_path = os.path.join(self.test_dir, "integrity.txt")
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write("SOC 2 Processing Integrity Verification Payload")

        h1 = know.calculate_sha256(sample_path)
        self.assertEqual(len(h1), 64)

    def test_04_soc2_confidentiality_acl_permissions(self):
        """Verify presence of acl_permissions column in files table schema for access control.

        Preconditions: Active database schema initialized via know.init_db().
        Invariants: Database table 'files' schema defines mandatory acl_permissions column.
        Expected Outcomes: Table column list includes 'acl_permissions'.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(files)")
        columns = [row['name'] for row in cursor.fetchall()]
        self.assertIn("acl_permissions", columns)
        conn.close()

    def test_05_soc2_privacy_sanitization_guard(self):
        """Verify FTS query sanitizer strips non-printable ASCII control characters.

        Preconditions: Raw input string containing null byte (\\x00) and unit separator (\\x1f).
        Invariants: Sanitizer strips control characters prior to query execution.
        Expected Outcomes: Sanitized output query string contains neither \\x00 nor \\x1f bytes.
        """
        sanitised = main.sanitise_fts_query("user_data \x00\x1f AND private_key")
        self.assertNotIn("\x00", sanitised)
        self.assertNotIn("\x1f", sanitised)

if __name__ == "__main__":
    unittest.main()
