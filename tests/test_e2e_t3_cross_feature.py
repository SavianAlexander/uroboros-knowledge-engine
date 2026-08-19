import src.core.config as config
import src.infrastructure.database as db
import pytest
"""
Tier 3 Cross-Feature Integration Tests for Uroboros Knowledge Engine.
Validates 5 multi-subsystem interaction chains across FastAPI backend endpoints.
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
db.DB_FILE = "e2e_t3_test.db"


# Mock watcher to prevent background thread spawning during imports
def mock_watcher(directory, callback=None):
    pass


original_watcher = getattr(know, "real_start_active_folder_watcher", know.start_active_folder_watcher)
know.start_active_folder_watcher = mock_watcher

# Import main and FastAPI TestClient
import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class TestE2ETier3CrossFeature(unittest.TestCase):
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
        self.db_file = f"e2e_t3_{test_name}.db"
        self.sandbox_dir = Path(f"test_sandbox_t3_{test_name}").resolve()
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
            except Exception:
                pass
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if hasattr(self, "sandbox_dir") and self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception:
                pass
        if hasattr(self, "db_file"):
            self._cleanup_db_files(self.db_file)

    def test_chain1_ingestion_autotag_fts_graph_inspector_insights(self):
        """
        Chain 1: Ingestion -> Auto-Tag Rule -> FTS Search -> Graph Highlighting -> Inspector -> AI Insights
        """
        # Step 1: Ingestion via Upload
        filename = "financial_audit_2026.txt"
        file_content = "This document contains the financial audit details for 2026 quarterly operations."
        resp_upload = self.client.post(
            "/api/upload",
            files={"file": (filename, file_content.encode("utf-8"), "text/plain")}
        )
        self.assertEqual(resp_upload.status_code, 200)
        upload_data = resp_upload.json()
        self.assertEqual(upload_data["status"], "success")
        uploaded_path = upload_data["filepath"]
        self.assertTrue(os.path.exists(uploaded_path))

        # Step 2: Auto-Tag Rule Creation & Application
        resp_rule = self.client.post(
            "/api/rules",
            json={"pattern": "financial", "tag": "finance", "priority": 10}
        )
        self.assertEqual(resp_rule.status_code, 200)

        # Trigger re-index to evaluate auto-tagging rules
        know.index_directory(self.sandbox_dir_str)

        # Step 3: FTS Search for tagged document
        resp_search = self.client.get("/api/search", params={"q": "tag:finance", "mode": "keyword"})
        self.assertEqual(resp_search.status_code, 200)
        search_data = resp_search.json()
        self.assertGreater(search_data["total"], 0)
        matched = any(r.get("filename") == filename or filename in r.get("filepath", "") for r in search_data["results"])
        self.assertTrue(matched, f"File {filename} not found in search results for tag:finance")

        # Step 4: Graph Canvas Query
        resp_graph = self.client.get("/api/graph/data")
        self.assertEqual(resp_graph.status_code, 200)
        graph_data = resp_graph.json()
        nodes = graph_data.get("nodes", [])
        self.assertGreater(len(nodes), 0)
        doc_nodes = [n for n in nodes if filename in n.get("id", "") or filename in n.get("label", "")]
        self.assertGreater(len(doc_nodes), 0, "Doc node missing in graph data")

        # Step 5: Floating File Inspector & Notes
        resp_notes_add = self.client.post("/api/notes", json={"path": uploaded_path, "notes": "Audited by team lead."})
        self.assertEqual(resp_notes_add.status_code, 200)
        resp_notes_get = self.client.get("/api/notes", params={"path": uploaded_path})
        self.assertEqual(resp_notes_get.status_code, 200)
        self.assertEqual(resp_notes_get.json().get("notes"), "Audited by team lead.")

        # Step 6: AI Insights Generation
        resp_insights = self.client.post("/api/file/insights", json={"filepath": uploaded_path})
        self.assertIn(resp_insights.status_code, (200, 501))
        if resp_insights.status_code == 200:
            insights_data = resp_insights.json()
            self.assertIn("insights", insights_data)
        else:
            self.assertIn("detail", resp_insights.json())

    def test_chain2_audio_upload_transcription_indexing_fts_rag_stream(self):
        """
        Chain 2: Audio Upload -> Transcription -> Indexing -> FTS Search -> RAG Chat Citation Stream
        """
        # Step 1: Upload Audio File
        audio_name = "voice-memo-meeting.wav"
        import wave
        memo_dir = self.sandbox_dir
        memo_file = memo_dir / audio_name
        with wave.open(str(memo_file), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00\x00" * 16000)

        # Step 2: Trigger Transcription
        resp_transcribe = self.client.post("/api/transcribe", json={"filepath": str(memo_file)})
        self.assertEqual(resp_transcribe.status_code, 200)
        trans_data = resp_transcribe.json()
        self.assertEqual(trans_data["status"], "success")

        # Step 3: FTS Search
        resp_search = self.client.get("/api/search", params={"q": "meeting", "mode": "keyword"})
        self.assertEqual(resp_search.status_code, 200)

        # Step 4: RAG Chat Citation Stream
        resp_stream = self.client.post("/api/chat/stream", json={"message": "What is mentioned in the voice memo transcription?"})
        self.assertEqual(resp_stream.status_code, 200)
        stream_text = resp_stream.text
        self.assertIn("data:", stream_text)

    def test_chain3_bookmark_macro_alias_expansion_csv_export(self):
        """
        Chain 3: Bookmark Creation -> Macro & Alias Registration -> Search Expansion -> CSV Export
        """
        # Seed a test document
        doc_path = self.sandbox_dir / "priority_spec.txt"
        doc_path.write_text("Priority specification document for urgent audit.", encoding="utf-8")
        know.index_directory(self.sandbox_dir_str)

        # Step 1: Register Macro
        resp_macro = self.client.post("/api/macros", json={"name": "critical", "expansion": "type:txt tag:urgent"})
        self.assertEqual(resp_macro.status_code, 200)

        # Step 2: Register Alias
        resp_alias = self.client.post("/api/aliases", json={"alias": "urgent", "target": "priority"})
        self.assertEqual(resp_alias.status_code, 200)

        # Tag the document with target tag 'priority'
        real_doc_path = str(doc_path.resolve())
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE filepath = ?", (real_doc_path,))
            r = cursor.fetchone()
            if r:
                cursor.execute("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", (r[0], "priority"))
                conn.commit()

        # Step 3: Create Search Bookmark
        resp_bm = self.client.post("/api/bookmarks", json={"name": "Critical Audit", "query": "%critical%", "search_mode": "keyword"})
        self.assertEqual(resp_bm.status_code, 200)

        # Step 4: Search Expansion
        resp_search = self.client.get("/api/search", params={"q": "%critical%"})
        self.assertEqual(resp_search.status_code, 200)

        # Step 5: CSV Export
        resp_export = self.client.get("/api/export", params={"query": "%critical%", "format": "csv"})
        self.assertEqual(resp_export.status_code, 200)
        self.assertIn("text/csv", resp_export.headers.get("content-type", ""))
        csv_content = resp_export.text
        self.assertIn("Filepath,Filename,Size (bytes),Modified At", csv_content)

    def test_chain4_rule_test_preview_reindex_graph_cluster_rag_chat(self):
        """
        Chain 4: Auto-Tag Rule -> Test Preview -> Directory Re-index -> Graph Cluster Edge -> RAG Chat
        """
        # Create sample files
        file1 = self.sandbox_dir / "quantum_doc_1.txt"
        file2 = self.sandbox_dir / "quantum_doc_2.txt"
        file1.write_text("Quantum entanglement and superposition physics.", encoding="utf-8")
        file2.write_text("Quantum computing algorithms in modern physics.", encoding="utf-8")

        # Step 1: Create Auto-Tag Rule
        resp_rule = self.client.post("/api/rules", json={"pattern": "Quantum", "tag": "physics", "priority": 5})
        self.assertEqual(resp_rule.status_code, 200)

        # Step 2: Test Preview Rule
        resp_prev = self.client.post("/api/rules/test-preview", json={"pattern": "Quantum", "tag": "physics"})
        self.assertEqual(resp_prev.status_code, 200)
        self.assertEqual(resp_prev.json().get("status"), "success")

        # Step 3: Directory Re-index
        know.index_directory(self.sandbox_dir_str)

        # Step 4: Graph Clusters Query
        resp_clusters = self.client.get("/api/graph/clusters")
        self.assertEqual(resp_clusters.status_code, 200)
        cluster_data = resp_clusters.json()
        self.assertIn("clusters", cluster_data)

        # Step 5: RAG Chat Stream
        resp_stream = self.client.post("/api/chat/stream", json={"message": "Explain Quantum entanglement"})
        self.assertEqual(resp_stream.status_code, 200)
        stream_text = resp_stream.text
        self.assertIn("data:", stream_text)

    def test_chain5_p2p_discovery_delta_sync_ingestion_workspace_preview(self):
        """
        Chain 5: P2P Peer Discovery -> Delta Sync -> File Ingestion -> Split-Screen Workspace Preview
        """
        # Step 1: P2P Peer Discovery & Registration
        peer_addr = "http://127.0.0.1:8092"
        resp_add_peer = self.client.post("/api/sync/peers", json={"address": peer_addr, "name": "Node-Alpha"})
        self.assertEqual(resp_add_peer.status_code, 200)

        resp_list_peers = self.client.get("/api/sync/peers")
        self.assertEqual(resp_list_peers.status_code, 200)
        peers_list = resp_list_peers.json().get("peers", [])
        self.assertTrue(any(p.get("address") == peer_addr for p in peers_list))

        # Step 2: Delta Sync Hashes & Delta Request
        resp_hashes = self.client.get("/api/sync/hashes")
        self.assertEqual(resp_hashes.status_code, 200)

        synced_filename = "p2p_synced_vault_item.txt"
        resp_delta = self.client.post("/api/sync/delta", json={"filenames": [synced_filename]})
        self.assertEqual(resp_delta.status_code, 200)
        delta_data = resp_delta.json()
        self.assertEqual(delta_data["status"], "success")

        # Step 3: File Ingestion into Workspace Directory
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        synced_filepath = self.sandbox_dir / synced_filename
        synced_filepath.write_text("Synced P2P document content from remote peer node.", encoding="utf-8")
        know.index_directory(self.sandbox_dir_str)

        # Step 4: Workspace Split-Screen File Tree Navigation
        resp_tree = self.client.get("/api/file/tree")
        self.assertEqual(resp_tree.status_code, 200)
        tree_items = resp_tree.json().get("tree", [])
        self.assertTrue(any(synced_filename in item.get("filepath", "") or synced_filename == item.get("relative_path") for item in tree_items))

        # Step 5: Workspace Split-Screen File Preview
        resp_file = self.client.get("/api/file/raw", params={"path": str(synced_filepath.resolve())})
        self.assertEqual(resp_file.status_code, 200)
        file_data = resp_file.json()
        self.assertIn("content", file_data)
        self.assertIn("Synced P2P document content", file_data["content"])


if __name__ == "__main__":
    unittest.main()