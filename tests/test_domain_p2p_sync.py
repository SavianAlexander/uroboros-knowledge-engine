import pytest
import src.core.config as config
"""
Domain test suite for Local Peer-to-Peer Knowledge Base Synchronization (R3).
Verifies UDP Multicast LAN discovery, SHA-256 document hashing, HTTP delta exchange,
REST endpoints (/api/sync/hashes, /api/sync/delta, /api/sync/exchange, /api/sync/logs),
and sync_logs database transaction ledger.
"""

import os
import sys
import tempfile
import shutil
import time
import json
import unittest
from fastapi.testclient import TestClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import main
from main import app
import src.infrastructure.database as db_infra
from src.infrastructure.database import get_db, get_active_dir
from src.infrastructure.p2p_sync import (
    P2PPeerBeacon,
    get_active_peers,
    get_local_document_hashes,
    compute_sync_delta,
)

class TestDomainP2PSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up isolated test database, temporary vault directory, and TestClient."""
        cls.temp_dir = tempfile.mkdtemp(prefix="test_p2p_sync_")
        cls.db_path = os.path.join(cls.temp_dir, "test_p2p_sync.db")
        cls.orig_db_file = db_infra.DB_FILE
        cls.old_active_dir = getattr(main, "ACTIVE_DIR", "dumps")
        main.ACTIVE_DIR = cls.temp_dir
        db_infra.DB_FILE = cls.db_path
        config.ACTIVE_DIR = cls.temp_dir
        db_infra.init_db()

        cls.client = TestClient(app)

        # Create sample test documents in temp vault directory
        cls.doc1_path = os.path.join(cls.temp_dir, "alpha_node_doc1.txt")
        with open(cls.doc1_path, "w", encoding="utf-8") as f:
            f.write("Alpha node test content for peer sync.")

        cls.doc2_path = os.path.join(cls.temp_dir, "beta_node_doc2.md")
        with open(cls.doc2_path, "w", encoding="utf-8") as f:
            f.write("# Beta Node Markdown\nSynchronization content.")

        # Insert documents into DB files table
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content) VALUES (?, ?, ?, ?, ?)",
                (cls.doc1_path, "alpha_node_doc1.txt", os.path.getsize(cls.doc1_path), os.path.getmtime(cls.doc1_path), "Alpha node test content for peer sync.")
            )
            cursor.execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content) VALUES (?, ?, ?, ?, ?)",
                (cls.doc2_path, "beta_node_doc2.md", os.path.getsize(cls.doc2_path), os.path.getmtime(cls.doc2_path), "# Beta Node Markdown\nSynchronization content.")
            )
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary test artifacts and restore original database and active vault directory."""
        db_infra.reset_db_connections()
        db_infra.DB_FILE = cls.orig_db_file
        config.ACTIVE_DIR = cls.old_active_dir
        main.ACTIVE_DIR = cls.old_active_dir
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_01_multicast_beacon_lifecycle(self):
        """
        Contract: P2PPeerBeacon start and stop methods initialize and terminate
        UDP multicast thread without unhandled socket exceptions.
        """
        beacon = P2PPeerBeacon(node_id="test_node_01", http_port=8098)
        self.assertFalse(beacon.running)

        beacon.start()
        self.assertTrue(beacon.running)
        time.sleep(0.1)

        beacon.stop()
        self.assertFalse(beacon.running)

    def test_02_get_local_document_hashes(self):
        """
        Contract: get_local_document_hashes returns map of SHA-256 hashes, file sizes,
        and modified timestamps for indexed vault files.
        """
        hashes = get_local_document_hashes(vault_dir=self.temp_dir)
        self.assertIsInstance(hashes, dict)
        self.assertIn("alpha_node_doc1.txt", hashes)
        self.assertIn("beta_node_doc2.md", hashes)

        doc1_info = hashes["alpha_node_doc1.txt"]
        self.assertIn("sha256", doc1_info)
        self.assertIn("size", doc1_info)
        self.assertIn("modified_at", doc1_info)
        self.assertGreater(len(doc1_info["sha256"]), 0)
        self.assertGreater(doc1_info["size"], 0)

    def test_03_compute_sync_delta_categorization(self):
        """
        Contract: compute_sync_delta correctly identifies missing, outdated, unchanged,
        and to_pull document sets when comparing local vs remote document hash maps.
        """
        local_hashes = {
            "file_identical.txt": {"sha256": "hash_a", "modified_at": 100.0},
            "file_outdated.txt": {"sha256": "hash_b_old", "modified_at": 100.0},
        }
        remote_hashes = {
            "file_identical.txt": {"sha256": "hash_a", "modified_at": 100.0},
            "file_outdated.txt": {"sha256": "hash_b_new", "modified_at": 200.0},
            "file_missing.txt": {"sha256": "hash_c", "modified_at": 150.0},
        }

        delta = compute_sync_delta(local_hashes, remote_hashes)
        self.assertEqual(delta["unchanged"], ["file_identical.txt"])
        self.assertEqual(delta["outdated"], ["file_outdated.txt"])
        self.assertEqual(delta["missing"], ["file_missing.txt"])
        self.assertEqual(set(delta["to_pull"]), {"file_outdated.txt", "file_missing.txt"})

    def test_04_api_sync_hashes_endpoint(self):
        """
        Contract: GET /api/sync/hashes endpoint returns 200 OK and SHA-256 hashes map.
        """
        response = self.client.get("/api/sync/hashes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("hashes", data)
        self.assertIn("alpha_node_doc1.txt", data["hashes"])

    def test_05_api_sync_delta_endpoint(self):
        """
        Contract: POST /api/sync/delta endpoint returns content payloads for requested filenames.
        """
        payload = {"filenames": ["alpha_node_doc1.txt"]}
        response = self.client.post("/api/sync/delta", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("files", data)
        self.assertEqual(len(data["files"]), 1)

        file_item = data["files"][0]
        self.assertEqual(file_item["filename"], "alpha_node_doc1.txt")
        self.assertIn("Alpha node test content", file_item["content"])

    def test_06_api_sync_exchange_unreachable_peer_logging(self):
        """
        Contract: POST /api/sync/exchange returns 500 when peer is unreachable and logs failure into sync_logs.
        """
        response = self.client.post("/api/sync/exchange", json={"target_peer": "http://127.0.0.1:9999"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to reach peer", response.json()["detail"])

        logs_resp = self.client.get("/api/sync/logs")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json().get("logs", [])
        self.assertTrue(any(log["status"] == "failed" and "9999" in log["peer_address"] for log in logs))

    def test_07_api_sync_exchange_successful_delta_flow(self):
        """
        Contract: POST /api/sync/exchange successfully executes delta sync with mocked peer,
        creates synced file on disk, updates database, and logs transaction into sync_logs.
        """
        from unittest.mock import patch, MagicMock

        remote_hashes_response = {
            "status": "success",
            "hashes": {
                "remote_synced_doc.txt": {
                    "filename": "remote_synced_doc.txt",
                    "sha256": "mock_sha256_remote",
                    "size": 38,
                    "modified_at": time.time() + 1000
                }
            }
        }
        remote_delta_response = {
            "status": "success",
            "files": [
                {
                    "filename": "remote_synced_doc.txt",
                    "content": "Content pulled from remote peer node.",
                    "file_size": 38,
                    "modified_at": time.time() + 1000,
                    "sha256": "mock_sha256_remote"
                }
            ]
        }

        def mock_urlopen(url_or_req, timeout=5.0):
            url_str = url_or_req.full_url if hasattr(url_or_req, "full_url") else str(url_or_req)
            m = MagicMock()
            m.__enter__.return_value = m
            if "hashes" in url_str:
                m.read.return_value = json.dumps(remote_hashes_response).encode("utf-8")
            elif "delta" in url_str:
                m.read.return_value = json.dumps(remote_delta_response).encode("utf-8")
            else:
                m.read.return_value = json.dumps({"manifest": []}).encode("utf-8")
            return m

        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
            response = self.client.post("/api/sync/exchange", json={"target_peer": "http://127.0.0.1:8098"})
            self.assertEqual(response.status_code, 200)
            res_json = response.json()
            self.assertEqual(res_json["status"], "success")
            self.assertIn("remote_synced_doc.txt", res_json["synced"])
            self.assertEqual(res_json["files_synced"], 1)

        synced_filepath = os.path.join(self.temp_dir, "remote_synced_doc.txt")
        self.assertTrue(os.path.exists(synced_filepath))
        with open(synced_filepath, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Content pulled from remote peer node.")

        logs_resp = self.client.get("/api/sync/logs")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json().get("logs", [])
        self.assertTrue(any(log["status"] == "success" and log["files_synced"] == 1 for log in logs))

if __name__ == "__main__":
    unittest.main()