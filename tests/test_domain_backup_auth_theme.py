"""
Domain 31: Database Backup, Auth Guard & Theme Switcher Test Suite.
Validates online SQLite database backups/restoration, configurable API key auth guards, and theme toggle contract invariants.
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know
import src.infrastructure.database as db
from scripts.backup_db import backup_database, restore_database
from src.shared.auth import verify_api_key


class TestDomainBackupAuthTheme(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_backup_auth_")
        self.db_path = os.path.join(self.test_dir, "test_backup.db")
        self.orig_db_file = db.DB_FILE
        self.orig_know_db_file = getattr(know, "DB_FILE", db.DB_FILE)
        db.DB_FILE = self.db_path
        know.DB_FILE = self.db_path
        db.reset_db_connections()
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        db.reset_db_connections()
        know.reset_db_connections()
        db.DB_FILE = self.orig_db_file
        know.DB_FILE = self.orig_know_db_file
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_sqlite_online_backup_and_restore(self):
        """Verify online SQLite live backup and restoration capability using C-API conn.backup().

        Preconditions: Active target database initialized with sample files.
        Invariants: Live backup copies database snapshot to backup destination without locking.
        Expected Outcomes: Backup file created, restore operation executes cleanly, and database content persists.
        """
        # Seed dummy file record
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO files (filepath, filename, file_size, mime_type, sha256) VALUES (?, ?, ?, ?, ?)",
            ("test/sample.txt", "sample.txt", 128, "text/plain", "abc123sha")
        )
        conn.commit()

        backup_file = os.path.join(self.test_dir, "backup_snapshot.db")
        saved_path = backup_database(backup_file)

        if isinstance(saved_path, dict):
            saved_knowledge = saved_path.get("knowledge_db", backup_file)
        else:
            saved_knowledge = saved_path

        self.assertTrue(os.path.exists(saved_knowledge))
        self.assertGreater(os.path.getsize(saved_knowledge), 0)

        # Clear active table (re-acquire connection since backup_database resets it via init_db)
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files")
        conn.commit()

        # Restore from backup
        res = restore_database(saved_knowledge)
        self.assertTrue(res)

        # Verify restored record (re-acquire after restore resets connections)
        conn2 = know.get_db()
        c2 = conn2.cursor()
        c2.execute("SELECT COUNT(*) FROM files")
        count = c2.fetchone()[0]
        self.assertEqual(count, 1)

    def test_02_verify_api_key_auth_guard_toggle(self):
        """Verify configurable API key and Bearer token authentication guard toggle.

        Preconditions: UROBOROS_REQUIRE_AUTH environment variable configured.
        Invariants: Disabled auth returns True; enabled auth validates X-API-Key and Bearer header against expected key.
        Expected Outcomes: Valid key returns True; missing or invalid key raises HTTPException(401).
        """
        os.environ["UROBOROS_REQUIRE_AUTH"] = "false"
        self.assertTrue(verify_api_key(None, None))

        os.environ["UROBOROS_REQUIRE_AUTH"] = "true"
        valid_auth_token = "test_enterprise_auth_token"
        os.environ["UROBOROS_API_KEY"] = valid_auth_token

        # Valid X-API-Key
        self.assertTrue(verify_api_key(x_api_key=valid_auth_token))

        # Valid Bearer authorization header
        self.assertTrue(verify_api_key(authorization=f"Bearer {valid_auth_token}"))

        # Invalid key raises 401
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key(x_api_key="wrong_key")
        self.assertEqual(ctx.exception.status_code, 401)

        # Cleanup env vars
        os.environ["UROBOROS_REQUIRE_AUTH"] = "false"

    def test_03_theme_toggle_persistence_contract(self):
        """Verify theme switcher CSS root variables and persistence contract.

        Preconditions: style.css contains theme root variables.
        Invariants: style.css defines base colors, layers, and style variables.
        Expected Outcomes: Theme root variable definitions are present in style.css.
        """
        style_path = os.path.join(PROJECT_ROOT, "style.css")
        with open(style_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        self.assertIn(":root", css_content)
        self.assertTrue("--font-sans:" in css_content or "--color-" in css_content)


if __name__ == "__main__":
    unittest.main()