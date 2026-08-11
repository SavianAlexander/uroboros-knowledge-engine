import src.core.config as config
import src.infrastructure.database as db
import pytest
"""
Tier 4 Real-World Application Workload Scenarios for Uroboros Knowledge Engine.
Validates 3 complete enterprise user journeys across FastAPI backend endpoints.
"""

import os
import time
import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

# ponytail: override DB_FILE before importing main/know to isolate tests
import know
db.DB_FILE = "e2e_t4_test.db"


# Mock watcher to prevent background thread spawning during imports
def mock_watcher(directory, callback=None):
    pass


original_watcher = getattr(know, "real_start_active_folder_watcher", know.start_active_folder_watcher)
know.start_active_folder_watcher = mock_watcher

# Import main and FastAPI TestClient
import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class TestE2ETier4RealWorldWorkloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.is_testing = True
        cls.client = TestClient(main.app)

    def _cleanup_db_files(self, db_file):
        for suffix in ["", "-wal", "-shm"]:
            fpath = db_file + suffix
            if os.path.exists(fpath):
                for _ in range(50):
                    try:
                        try:
                            from src.infrastructure.database import reset_db_connections
                            reset_db_connections()
                        except Exception: pass
                        os.remove(fpath)
                    except FileNotFoundError:
                        break
                    except PermissionError:
                        pass
                    if not os.path.exists(fpath):
                        break
                    time.sleep(0.05)

    def setUp(self):
        test_name = self.id().split('.')[-1]
        self.db_file = f"e2e_t4_{test_name}.db"
        self.sandbox_dir = Path(f"test_sandbox_t4_{test_name}").resolve()
        self.sandbox_dir_str = str(self.sandbox_dir)

        # Update global references
        db.DB_FILE = self.db_file
        config.ACTIVE_DIR = self.sandbox_dir_str

        # Cleanup & Init DB
        self._cleanup_db_files(self.db_file)
        know.init_db()

        # Init fresh sandbox directory
        if self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception as e:
                import logging; logging.error(f"Swallowed error in test_e2e_t4_realworld_workloads.py: {e}")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if hasattr(self, "sandbox_dir") and self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception as e:
                import logging; logging.error(f"Swallowed error in test_e2e_t4_realworld_workloads.py: {e}")
        if hasattr(self, "db_file"):
            self._cleanup_db_files(self.db_file)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_scenario1_workspace_splitscreen_document_intelligence_workflow(self):
        """
        Scenario 1: Workspace Split-Screen Document Intelligence Workflow
        User Story: Enterprise analyst ingests research reports, inspects documents in split-screen mode,
        extracts AI insights, and updates metadata tags and notes.
        """
        # Step 1: Upload Research Report
        filename = "quarterly_market_intelligence.txt"
        file_content = (
            "Quarterly Market Intelligence Report 2026.\n"
            "Key takeaway 1: Cloud adoption grew by 45% year-over-year in enterprise accounts.\n"
            "Key takeaway 2: Local AI model deployment reduced latency by 60ms.\n"
            "Key takeaway 3: Zero-trust architecture compliance reached 98% across all nodes."
        )
        resp_upload = self.client.post(
            "/api/upload",
            files={"file": (filename, file_content.encode("utf-8"), "text/plain")}
        )
        self.assertEqual(resp_upload.status_code, 200)
        upload_data = resp_upload.json()
        uploaded_path = upload_data["filepath"]
        self.assertTrue(os.path.exists(uploaded_path))

        # Step 2: File Tree Update Verification
        resp_tree = self.client.get("/api/file/tree")
        self.assertEqual(resp_tree.status_code, 200)
        tree = resp_tree.json().get("tree", [])
        self.assertTrue(any(filename in item.get("filepath", "") for item in tree))

        # Step 3: Raw Inspection & Preview
        resp_preview = self.client.get("/api/file/raw", params={"path": uploaded_path})
        self.assertEqual(resp_preview.status_code, 200)
        preview_data = resp_preview.json()
        self.assertEqual(preview_data["filename"], filename)
        self.assertIn("Quarterly Market Intelligence Report", preview_data["content"])

        # Step 4: AI Insights Extraction
        resp_insights = self.client.post("/api/file/insights", json={"filepath": uploaded_path})
        self.assertIn(resp_insights.status_code, (200, 501))
        if resp_insights.status_code == 200:
            insights_data = resp_insights.json()
            self.assertIn("insights", insights_data)
            self.assertTrue(len(insights_data["insights"]) > 0)
        else:
            self.assertIn("detail", resp_insights.json())

        # Step 5: Metadata Tagging & Notes Assignment
        resp_tag = self.client.post("/api/file/tag", json={"filepath": uploaded_path, "tag": "reviewed"})
        self.assertEqual(resp_tag.status_code, 200)
        self.assertEqual(resp_tag.json().get("tag"), "reviewed")

        resp_notes = self.client.post("/api/notes", json={"path": uploaded_path, "notes": "Approved by Chief Analyst."})
        self.assertEqual(resp_notes.status_code, 200)

        # Verify Metadata Persistence
        resp_raw_updated = self.client.get("/api/file/raw", params={"path": uploaded_path})
        self.assertEqual(resp_raw_updated.status_code, 200)
        self.assertIn("reviewed", resp_raw_updated.json().get("tags", []))

        resp_notes_verify = self.client.get("/api/notes", params={"path": uploaded_path})
        self.assertEqual(resp_notes_verify.status_code, 200)
        self.assertEqual(resp_notes_verify.json().get("notes"), "Approved by Chief Analyst.")

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_scenario2_local_p2p_knowledge_vault_sync_workflow(self):
        """
        Scenario 2: Local Peer-to-Peer Knowledge Vault Sync Workflow
        User Story: Two isolated workstations on a local network synchronize knowledge vault documents
        without external cloud access.
        """
        # Step 1: Peer Discovery & Manual Peer Registration
        peer_address = "http://127.0.0.1:8093"
        resp_add_peer = self.client.post("/api/sync/peers", json={"address": peer_address, "name": "Workstation-B"})
        self.assertEqual(resp_add_peer.status_code, 200)

        resp_peers = self.client.get("/api/sync/peers")
        self.assertEqual(resp_peers.status_code, 200)
        peers = resp_peers.json().get("peers", [])
        self.assertTrue(any(p.get("address") == peer_address for p in peers))

        # Step 2: Request Local Delta Hashes Map
        resp_hashes = self.client.get("/api/sync/hashes")
        self.assertEqual(resp_hashes.status_code, 200)
        hashes_data = resp_hashes.json()
        self.assertEqual(hashes_data.get("status"), "success")
        self.assertIn("hashes", hashes_data)

        # Step 3: Delta Payload Retrieval
        remote_files = ["remote_vault_doc_1.txt", "remote_vault_doc_2.txt"]
        resp_delta = self.client.post("/api/sync/delta", json={"filenames": remote_files})
        self.assertEqual(resp_delta.status_code, 200)
        delta_data = resp_delta.json()
        self.assertEqual(delta_data.get("status"), "success")
        self.assertIn("files", delta_data)

        # Step 4: Write Synced Payloads & Re-index Workspace Pipeline
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        for idx, fn in enumerate(remote_files, start=1):
            file_p = self.sandbox_dir / fn
            file_p.write_text(f"Synced payload content for document {idx} from remote node Workstation-B.", encoding="utf-8")

        resp_index = self.client.post("/api/index", json={"directory": self.sandbox_dir_str})
        self.assertEqual(resp_index.status_code, 200)

        # Step 5: Verify Vault Stats Update & Transaction Logging
        resp_stats = self.client.get("/api/stats")
        self.assertEqual(resp_stats.status_code, 200)
        self.assertGreaterEqual(resp_stats.json().get("total_files", 0), 2)

        resp_sync_logs = self.client.get("/api/sync/logs")
        self.assertEqual(resp_sync_logs.status_code, 200)
        self.assertIn("logs", resp_sync_logs.json())

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_scenario3_disaster_recovery_db_snapshot_restore_workflow(self):
        """
        Scenario 3: Disaster Recovery & Database Snapshot Restore Workflow
        User Story: System administrator captures a clean database snapshot, simulates catastrophic file
        deletion, and restores vault state from snapshot.
        """
        # Step 1: Seed Workspace & Capture Baseline Snapshot
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        doc1 = self.sandbox_dir / "recovery_doc_1.txt"
        doc2 = self.sandbox_dir / "recovery_doc_2.txt"
        doc1.write_text("Critical disaster recovery test payload alpha.", encoding="utf-8")
        doc2.write_text("Critical disaster recovery test payload beta.", encoding="utf-8")

        self.client.post("/api/index", json={"directory": self.sandbox_dir_str})
        resp_baseline_stats = self.client.get("/api/stats")
        self.assertEqual(resp_baseline_stats.status_code, 200)
        baseline_file_count = resp_baseline_stats.json().get("total_files", 0)
        self.assertEqual(baseline_file_count, 2)

        # Capture Snapshot
        resp_snap = self.client.post("/api/snapshots")
        self.assertEqual(resp_snap.status_code, 200)
        snap_data = resp_snap.json()
        self.assertEqual(snap_data.get("status"), "success")
        snap_ts = snap_data.get("snapshot_timestamp") or snap_data.get("timestamp")
        self.assertIsNotNone(snap_ts)

        # Verify Snapshot Listed
        resp_list_snaps = self.client.get("/api/snapshots")
        self.assertEqual(resp_list_snaps.status_code, 200)
        snaps = resp_list_snaps.json().get("snapshots", [])
        self.assertTrue(any(str(snap_ts) in str(s) for s in snaps), f"Snapshot {snap_ts} not found in {snaps}")

        # Step 2: Simulate Accidental Bulk Delete & DB File Removal
        resp_delete = self.client.post(
            "/api/bulk_delete",
            json={"filepaths": [str(doc1.resolve()), str(doc2.resolve())]}
        )
        self.assertEqual(resp_delete.status_code, 200)

        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE filepath LIKE '%recovery_doc%'")
            cursor.execute("DELETE FROM fts_files WHERE filepath LIKE '%recovery_doc%'")
            conn.commit()

        resp_dropped_stats = self.client.get("/api/stats")
        self.assertEqual(resp_dropped_stats.status_code, 200)
        dropped_file_count = resp_dropped_stats.json().get("total_files", 0)
        self.assertEqual(dropped_file_count, 0)

        # Step 3: Database Snapshot Restore
        resp_restore = self.client.post(f"/api/snapshots/restore?timestamp={snap_ts}")
        self.assertEqual(resp_restore.status_code, 200)
        self.assertEqual(resp_restore.json().get("status"), "success")

        # Step 4: Re-create disk files if needed and Re-index Workspace Directory
        doc1.write_text("Critical disaster recovery test payload alpha.", encoding="utf-8")
        doc2.write_text("Critical disaster recovery test payload beta.", encoding="utf-8")
        self.client.post("/api/index", json={"directory": self.sandbox_dir_str})

        # Step 5: Verification of Vault Integrity Restoration
        resp_restored_stats = self.client.get("/api/stats")
        self.assertEqual(resp_restored_stats.status_code, 200)
        restored_file_count = resp_restored_stats.json().get("total_files", 0)
        self.assertEqual(restored_file_count, 2)


if __name__ == "__main__":
    unittest.main()
