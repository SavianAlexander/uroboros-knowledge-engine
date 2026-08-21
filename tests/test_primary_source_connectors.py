"""
Unit and Integration Test Suite for DomainPrimarySources:
Validates primary source ingestion connectors, persistent cryptographic SHA-256 sync ledger,
and unredacted regulatory dataset integrity.
"""

import unittest
import os
import sys
import json
import hashlib

from src.infrastructure.database import init_db, reset_db_connections, DB_FILE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNC_LEDGER_PATH = os.path.join(BASE_DIR, "vault", ".sync_ledger.json")


class TestPrimarySourceConnectors(unittest.TestCase):
    """Verifies Primary Source Connectors and Sync Ledger Integrity."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        reset_db_connections()

    def tearDown(self):
        reset_db_connections()

    def test_sync_ledger_exists_and_valid(self):
        """Test 1: Verify persistent cryptographic sync ledger exists and contains valid JSON."""
        self.assertTrue(os.path.exists(SYNC_LEDGER_PATH), f"Missing sync ledger at {SYNC_LEDGER_PATH}")
        with open(SYNC_LEDGER_PATH, "r", encoding="utf-8") as f:
            ledger = json.load(f)

        self.assertIn("entries", ledger)
        entries = ledger["entries"]
        self.assertGreater(len(entries), 0, "Sync ledger must contain at least 1 registered primary source dataset")

    def test_sync_ledger_sha256_cryptographic_signatures(self):
        """Test 2: Verify 100% of sync ledger entries have valid 64-character hex SHA-256 digests."""
        with open(SYNC_LEDGER_PATH, "r", encoding="utf-8") as f:
            ledger = json.load(f)

        entries = ledger.get("entries", {})
        for dataset_name, meta in entries.items():
            sha = meta.get("sha256", "")
            self.assertEqual(len(sha), 64, f"Dataset '{dataset_name}' has invalid SHA-256 length: {sha}")
            self.assertTrue(all(c in "0123456789abcdefABCDEF" for c in sha), f"Dataset '{dataset_name}' has non-hex SHA-256: {sha}")

    def test_statutory_data_connector_interface(self):
        """Test 3: Verify statutory data domain provider can query and calculate statutory thresholds."""
        from src.domain.statutory_data import load_statutory_policy, get_fpl_monthly

        policy = load_statutory_policy()
        self.assertIsNotNone(policy)
        self.assertIn("fpl_guidelines", policy)

        fpl_1 = get_fpl_monthly(1, policy=policy)
        self.assertGreater(fpl_1, 1000.0)


if __name__ == "__main__":
    unittest.main()
