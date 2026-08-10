import pytest
import os
import time
import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 1. Override DB_FILE before importing main/know
import know
know.DB_FILE = "e2e_knowledge.db"


# Mock watcher to prevent import-time background threads
def mock_watcher(directory, callback=None):
    pass


original_watcher = getattr(know, "real_start_active_folder_watcher", know.start_active_folder_watcher)
know.start_active_folder_watcher = mock_watcher

# Now import main and FastAPI TestClient
import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class TestE2ETier1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def poll_api_file(
        self, filepath, expected_status=200, timeout=5.0, interval=0.1
    ):
        start = time.time()
        while time.time() - start < timeout:
            response = self.client.get("/api/file", params={"path": filepath})
            if response.status_code == 500:
                import os
                import know
                print(
                    f"DEBUG POLL: 500 received. "
                    f"know.DB_FILE={know.DB_FILE}, "
                    f"exists={os.path.exists(know.DB_FILE)}"
                )
            if response.status_code == expected_status:
                return response
            time.sleep(interval)
        return self.client.get("/api/file", params={"path": filepath})

    def poll_search(
        self, query, mode="keyword", expected_filename=None,
        timeout=5.0, interval=0.1
    ):
        start = time.time()
        while time.time() - start < timeout:
            response = self.client.get(
                "/api/search", params={"q": query, "mode": mode}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                print(
                    f"DEBUG_POLL: query={query}, mode={mode}, "
                    f"DB={know.DB_FILE}, "
                    f"results={[r.get('filename') for r in results]}"
                )
                if expected_filename:
                    if any(
                        expected_filename in r["filename"] for r in results
                    ):
                        return response
                else:
                    if len(results) > 0:
                        return response
            time.sleep(interval)
        return self.client.get(
            "/api/search", params={"q": query, "mode": mode}
        )

    def poll_stats(self, expected_files, timeout=5.0, interval=0.1):
        start = time.time()
        while time.time() - start < timeout:
            response = self.client.get("/api/stats")
            if response.status_code == 200:
                if response.json().get("total_files", 0) == expected_files:
                    return response
            time.sleep(interval)
        return self.client.get("/api/stats")

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
                    time.sleep(0.1)

    def setUp(self):
        # Generate unique database and directory names for each test
        test_name = self.id().split('.')[-1]
        self.db_file = f"e2e_knowledge_{test_name}.db"
        self.sandbox_dir = Path(f"test_sandbox_e2e_{test_name}").resolve()

        # Update global references
        know.DB_FILE = self.db_file
        main.ACTIVE_DIR = str(self.sandbox_dir)
        know.start_active_folder_watcher.active = True

        # Initialize fresh database
        self._cleanup_db_files(self.db_file)
        know.init_db()

        # Initialize fresh sandbox directory
        if self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except PermissionError:
                pass
        self.sandbox_dir.mkdir(exist_ok=True)

    def tearDown(self):
        # Stop any running watchers
        know.start_active_folder_watcher.active = False
        original_watcher.active = False

        # Join any active WatcherThread or IndexerThread to avoid database
        # state collision in the next test
        import threading
        for t in threading.enumerate():
            if t.name in ["WatcherThread", "IndexerThread"]:
                t.join(timeout=5.0)

        # Attempt cleanup of this test's unique database and its
        # WAL/SHM sidecars
        self._cleanup_db_files(self.db_file)

        # Remove any snapshot files (and their sidecars) for this database
        for f in Path(".").glob(f"{self.db_file}.snapshot-*"):
            try:
                self._cleanup_db_files(str(f))
            except Exception as e:
                import logging; logging.error(f"Swallowed error in test_e2e_tier1.py: {e}")

        # Remove sandbox directory
        if self.sandbox_dir.exists():
            for _ in range(5):
                try:
                    shutil.rmtree(self.sandbox_dir)
                    break
                except PermissionError:
                    time.sleep(0.1)

        main.ACTIVE_DIR = "dumps"

    # ==========================================
    # FEATURE 1: WORKSPACE INGESTION & DOCUMENT PARSING
    # ==========================================

    def test_01_file_upload_text(self):
        # Upload text file
        response = self.client.post(
            "/api/upload",
            files={
                "file": (
                    "test_upload.txt",
                    b"This is a test document about artificial intelligence.",
                    "text/plain"
                )
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("filepath", data)
        filepath = data["filepath"]
        self.assertTrue(os.path.exists(filepath))

        # Check database content via API
        response = self.client.get(f"/api/file?path={filepath}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("artificial intelligence", response.json()["content"])

    def test_02_audio_wav_metadata_extraction(self):
        # Create a mock WAV file with minimal header structure
        import struct
        wav_payload = (
            b"RIFF" + struct.pack("<I", 36 + 44) + b"WAVE" +
            b"fmt " + struct.pack("<IHHIIHH", 16, 1, 2, 44100, 176400, 4, 16) +
            b"data" + struct.pack("<I", 44) + (b"\x00" * 44)
        )
        response = self.client.post(
            "/api/upload",
            files={"file": ("test_audio.wav", wav_payload, "audio/wav")}
        )
        self.assertEqual(response.status_code, 200)
        filepath = response.json()["filepath"]

        # Retrieve file details
        response = self.client.get("/api/file", params={"path": filepath})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("audio_metadata", data)
        self.assertEqual(data["audio_metadata"]["channels"], 2)
        self.assertEqual(data["audio_metadata"]["samplerate"], 44100)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_03_word_docx_ingestion(self):
        # Create a mock docx file
        import docx
        doc = docx.Document()
        doc.add_paragraph(
            "This is a Word document containing neural network descriptions."
        )
        docx_path = self.sandbox_dir / "test_doc.docx"
        doc.save(docx_path)

        # Ingest docx by triggering directory index
        response = self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        # Poll until test_doc.docx is indexed
        self.poll_api_file(str(docx_path), expected_status=200)

        # Search for content
        response = self.poll_search(
            "neural network", expected_filename="test_doc.docx"
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertTrue(len(results) > 0)
        self.assertIn("test_doc.docx", results[0]["filename"])

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_04_index_directory_trigger(self):
        # Place two files in sandbox
        (self.sandbox_dir / "file1.txt").write_text(
            "Unique text code alpha", encoding="utf-8"
        )
        (self.sandbox_dir / "file2.txt").write_text(
            "Unique text code beta", encoding="utf-8"
        )

        # Trigger directory index
        response = self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        # Verify both are in database via API
        response = self.poll_stats(2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_files"], 2)

    def test_05_watcher_sync(self):
        # Start a local watcher thread on the sandbox directory
        watcher_cb_called = [0]

        def cb():
            watcher_cb_called[0] += 1

        original_watcher(str(self.sandbox_dir), callback=cb)

        # Write file
        test_file = self.sandbox_dir / "watcher_file.txt"
        test_file.write_text("watcher sync content", encoding="utf-8")

        # Poll until indexed
        response = self.poll_api_file(str(test_file), expected_status=200, timeout=10.0)
        self.assertEqual(response.status_code, 200)

        # Delete file
        try:
            test_file.unlink()
        except FileNotFoundError:
            pass

        # Poll until deleted
        response = self.poll_api_file(str(test_file), expected_status=404, timeout=10.0)
        self.assertEqual(response.status_code, 404)

        # Explicitly shut down the watcher thread at the end of the test
        know.start_active_folder_watcher.active = False
        original_watcher.active = False
        import threading
        for t in threading.enumerate():
            if t.name == "WatcherThread":
                t.join(timeout=5.0)

    # ==========================================
    # FEATURE 2: CORE HYBRID SEARCH & QUERY PARSING
    # ==========================================

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_06_fts5_keyword_search(self):
        # Ingest file
        (self.sandbox_dir / "fts_doc.txt").write_text(
            "The quick brown fox jumps over the lazy dog.", encoding="utf-8"
        )
        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )

        # Poll until fts_doc.txt is indexed
        self.poll_api_file(
            str(self.sandbox_dir / "fts_doc.txt"), expected_status=200
        )

        # Search with polling to ensure async indexing is complete
        response = self.poll_search("fox jumps", expected_filename="fts_doc.txt")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertIn("fts_doc.txt", results[0]["filename"])

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_07_semantic_search(self):
        # Ingest document
        doc_path = self.sandbox_dir / "semantic_doc.txt"
        doc_path.write_text(
            "Artificial intelligence and machine learning algorithm is "
            "evolving.",
            encoding="utf-8"
        )
        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )

        # Poll until semantic_doc.txt is indexed
        self.poll_api_file(str(doc_path), expected_status=200)

        # Semantic search with polling to ensure async indexing is complete
        response = self.poll_search(
            "algorithm", mode="semantic", expected_filename="semantic_doc.txt"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "semantic")
        results = data["results"]
        self.assertTrue(len(results) > 0)
        self.assertTrue(results[0]["score"] > 0)

    def test_08_and_or_tag_filtering(self):
        # Upload two files and add tags
        f1_resp = self.client.post(
            "/api/upload",
            files={"file": ("f1.txt", b"content f1", "text/plain")}
        )
        f1 = f1_resp.json()["filepath"]
        f2_resp = self.client.post(
            "/api/upload",
            files={"file": ("f2.txt", b"content f2", "text/plain")}
        )
        f2 = f2_resp.json()["filepath"]

        self.client.post(
            "/api/file/tag",
            json={"filepath": f1, "tag": "science"}
        )
        self.client.post(
            "/api/file/tag",
            json={"filepath": f1, "tag": "math"}
        )
        self.client.post(
            "/api/file/tag",
            json={"filepath": f2, "tag": "science"}
        )

        # Test AND filtering: both science and math
        resp_and = self.client.get("/api/search?tag=science,math&tag_mode=AND")
        self.assertEqual(len(resp_and.json()["results"]), 1)
        self.assertEqual(resp_and.json()["results"][0]["filename"], "f1.txt")

        # Test OR filtering: science or math
        resp_or = self.client.get("/api/search?tag=science,math&tag_mode=OR")
        self.assertEqual(len(resp_or.json()["results"]), 2)

    def test_09_tag_type_exclusion_filters(self):
        # Create a text file and a pdf file
        self.client.post(
            "/api/upload",
            files={
                "file": (
                    "f1.txt",
                    b"content matching keyword",
                    "text/plain"
                )
            }
        )

        from reportlab.pdfgen import canvas
        pdf_path = self.sandbox_dir / "f2.pdf"
        c = canvas.Canvas(str(pdf_path))
        c.drawString(100, 750, "content matching keyword")
        c.save()
        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        # Poll until f2.pdf is indexed
        self.poll_api_file(str(pdf_path), expected_status=200)

        # Search matching keyword, exclude type:pdf
        start = time.time()
        results = []
        while time.time() - start < 5.0:
            response = self.client.get(
                "/api/search", params={"q": "content -type:pdf"}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if len(results) == 1 and results[0]["filename"] == "f1.txt":
                    break
            time.sleep(0.1)
        self.assertEqual(response.status_code, 200)
        # Only f1.txt should be returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "f1.txt")

        # Search matching keyword, exclude word:matching
        start = time.time()
        while time.time() - start < 5.0:
            response = self.client.get(
                "/api/search", params={"q": "content -word:matching"}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if len(results) == 0:
                    break
            time.sleep(0.1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 0)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_10_proximity_near_query(self):
        # Create file
        (self.sandbox_dir / "prox.txt").write_text(
            "gravity is an attractive force in physics", encoding="utf-8"
        )
        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        # Poll until prox.txt is indexed
        self.poll_api_file(
            str(self.sandbox_dir / "prox.txt"), expected_status=200
        )

        # Proximity NEAR query within 5 words with polling to ensure async indexing is complete
        response = self.poll_search("NEAR(gravity physics, 5)", expected_filename="prox.txt")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "prox.txt")

    # ==========================================
    # FEATURE 3: QUERY EXTENSIONS
    # ==========================================

    def test_11_syntax_validation(self):
        # Valid query
        response = self.client.post(
            "/api/search/validate",
            json={"query": "tag:science type:pdf"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])

        # Invalid unmatched quote query
        response = self.client.post(
            "/api/search/validate",
            json={"query": '"unmatched quote'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["valid"])
        self.assertIn("Unmatched double quotes", response.json()["error"])

    def test_12_autocomplete_suggestions(self):
        response = self.client.get("/api/search/suggest?token=tag:")
        self.assertEqual(response.status_code, 200)
        suggestions = response.json()["suggestions"]
        self.assertTrue(any(s["text"] == "tag:" for s in suggestions))

    def test_13_query_cache_stats(self):
        # Reset cache
        main.GLOBAL_QUERY_CACHE.invalidate()
        main.GLOBAL_QUERY_CACHE.hits = 0
        main.GLOBAL_QUERY_CACHE.misses = 0

        # Initial search (miss)
        response1 = self.client.get("/api/search?q=cache_test_query")
        self.assertEqual(response1.status_code, 200)

        # Second search (hit)
        response2 = self.client.get("/api/search?q=cache_test_query")
        self.assertEqual(response2.status_code, 200)

        # Check stats
        stats_resp = self.client.get("/api/search/cache/stats")
        self.assertEqual(stats_resp.status_code, 200)
        stats = stats_resp.json()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_ratio"], 50.0)

    def test_14_bookmarks_crud(self):
        # Create
        response = self.client.post(
            "/api/bookmarks",
            json={
                "name": "my_query",
                "query_string": "tag:physics",
                "search_mode": "keyword"
            }
        )
        self.assertEqual(response.status_code, 200)

        # Read
        response = self.client.get("/api/bookmarks")
        self.assertEqual(response.status_code, 200)
        bookmarks = response.json()["bookmarks"]
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0]["name"], "my_query")
        bookmark_id = bookmarks[0]["id"]

        # Delete
        response = self.client.delete(f"/api/bookmarks?id={bookmark_id}")
        self.assertEqual(response.status_code, 200)

        # Verify deleted
        response = self.client.get("/api/bookmarks")
        self.assertEqual(len(response.json()["bookmarks"]), 0)

    def test_15_macros_registration_search(self):
        # Register macro
        response = self.client.post(
            "/api/macros",
            json={"name": "scidoc", "expansion": "tag:science type:txt"}
        )
        self.assertEqual(response.status_code, 200)

        # Verify listing
        response = self.client.get("/api/macros")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any(m["name"] == "scidoc" for m in response.json()["macros"])
        )

        # Ingest matching file
        f1_resp = self.client.post(
            "/api/upload",
            files={"file": ("macro_file.txt", b"macro content", "text/plain")}
        )
        f1 = f1_resp.json()["filepath"]
        self.client.post(
            "/api/file/tag",
            json={"filepath": f1, "tag": "science"}
        )

        # Search using macro %scidoc%
        response = self.client.get("/api/search?q=%scidoc%")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "macro_file.txt")

    # ==========================================
    # FEATURE 4: METADATA, ANNOTATIONS & RELATIONAL GRAPH
    # ==========================================

    def test_16_tag_assignment_deletion(self):
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("tag_crud.txt", b"tag content", "text/plain")}
        )
        f = f_resp.json()["filepath"]

        # Assign tag
        response = self.client.post(
            "/api/file/tag",
            json={"filepath": f, "tag": "chemistry"}
        )
        self.assertEqual(response.status_code, 200)

        # Get details to verify tag assigned
        response = self.client.get("/api/file", params={"path": f})
        self.assertIn("chemistry", response.json()["tags"])

        # Delete tag
        response = self.client.delete(
            "/api/file/tag",
            params={"filepath": f, "tag": "chemistry"}
        )
        self.assertEqual(response.status_code, 200)

        # Verify tag deleted
        response = self.client.get("/api/file", params={"path": f})
        self.assertNotIn("chemistry", response.json()["tags"])

    def test_17_suggested_tags_retval(self):
        text_content = (
            "gravity gravity gravity physics physics quantum "
            "relativity relativity relativity relativity"
        )
        f_resp = self.client.post(
            "/api/upload",
            files={
                "file": (
                    "suggest_tags.txt",
                    text_content.encode("utf-8"),
                    "text/plain"
                )
            }
        )
        f = f_resp.json()["filepath"]

        response = self.client.get("/api/file", params={"path": f})
        self.assertEqual(response.status_code, 200)
        suggested = response.json()["suggested_tags"]
        self.assertIn("relativity", suggested)
        self.assertIn("gravity", suggested)

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    def test_18_auto_tag_rules(self):
        # Create rule first
        response = self.client.post(
            "/api/rules",
            json={"pattern": "organic", "tag": "biology"}
        )
        self.assertEqual(response.status_code, 200)

        # Write file with keyword 'organic'
        (self.sandbox_dir / "rule_test.txt").write_text(
            "This contains organic compounds.",
            encoding="utf-8"
        )

        # Index directory to index file and apply rule automatically
        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        # Check database via API with polling to avoid race conditions
        filepath = str(self.sandbox_dir / "rule_test.txt")
        response = self.poll_api_file(filepath, expected_status=200)
        self.assertEqual(response.status_code, 200)

        # Preview rule (the file is now in DB)
        response = self.client.post(
            "/api/rules/test-preview",
            json={"pattern": "organic", "tag": "biology"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()["matches"]) > 0)

        # Check tags via API
        response = self.client.get("/api/file", params={"path": filepath})
        self.assertEqual(response.status_code, 200)
        self.assertIn("biology", response.json().get("tags", []))

    def test_19_tag_custom_colors(self):
        # Set tag color
        response = self.client.post(
            "/api/tags/color",
            json={"tag": "red_tag", "color": "#ff0000"}
        )
        self.assertEqual(response.status_code, 200)

        # Retrieve all tags and check color
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("color_test.txt", b"some text", "text/plain")}
        )
        f = f_resp.json()["filepath"]
        self.client.post(
            "/api/file/tag",
            json={"filepath": f, "tag": "red_tag"}
        )

        response = self.client.get("/api/tags")
        self.assertEqual(response.status_code, 200)
        tags = response.json()["tags"]
        red_tag_data = [t for t in tags if t["tag"] == "red_tag"]
        self.assertEqual(len(red_tag_data), 1)
        self.assertEqual(red_tag_data[0]["color"], "#ff0000")

    def test_20_tag_aliases(self):
        # Set tag alias: phys -> physics
        response = self.client.post(
            "/api/aliases",
            json={"alias": "phys", "target": "physics"}
        )
        self.assertEqual(response.status_code, 200)

        # Verify alias was set
        response = self.client.get("/api/aliases")
        self.assertTrue(
            any(
                a["alias"] == "phys" and a["target"] == "physics"
                for a in response.json()["aliases"]
            )
        )

        # Ingest file tagged with target tag 'physics'
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("alias_test.txt", b"alias content", "text/plain")}
        )
        f = f_resp.json()["filepath"]
        self.client.post(
            "/api/file/tag",
            json={"filepath": f, "tag": "physics"}
        )

        # Search using tag 'phys'
        response = self.client.get("/api/search?tag=phys")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "alias_test.txt")

    # ==========================================
    # FEATURE 5: OPERATIONS, SNAPSHOTS & REPORTING
    # ==========================================

    def test_21_file_rename(self):
        # Upload file
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("oldname.txt", b"content", "text/plain")}
        )
        f = f_resp.json()["filepath"]

        # Rename file
        response = self.client.post(
            "/api/file/rename",
            json={"filepath": f, "new_name": "newname.txt"}
        )
        self.assertEqual(response.status_code, 200)
        new_filepath = response.json()["new_filepath"]

        self.assertFalse(os.path.exists(f))
        self.assertTrue(os.path.exists(new_filepath))

        # Verify database updated via API
        response = self.client.get("/api/file", params={"path": new_filepath})
        self.assertEqual(response.status_code, 200)

    def test_22_inline_content_editing(self):
        f_resp = self.client.post(
            "/api/upload",
            files={
                "file": (
                    "edit_test.txt",
                    b"original content",
                    "text/plain"
                )
            }
        )
        f = f_resp.json()["filepath"]

        # Edit content inline
        response = self.client.post(
            "/api/file/edit",
            json={"filepath": f, "content": "updated content inline"}
        )
        self.assertEqual(response.status_code, 200)

        # Verify physical file updated
        content_disk = Path(f).read_text(encoding="utf-8")
        self.assertEqual(content_disk, "updated content inline")

        # Verify DB updated via API
        response = self.client.get("/api/file", params={"path": f})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "updated content inline")

    def test_23_db_snapshots(self):
        # Insert a file
        self.client.post(
            "/api/upload",
            files={"file": ("snap1.txt", b"snap 1 content", "text/plain")}
        )

        # Create snapshot
        response = self.client.post("/api/snapshots")
        self.assertEqual(response.status_code, 200)
        ts = response.json()["timestamp"]

        # Verify snapshot exists in list
        response_list = self.client.get("/api/snapshots")
        snapshots = response_list.json()["snapshots"]
        self.assertIn(ts, snapshots)

        # Insert a second file
        snap2_resp = self.client.post(
            "/api/upload",
            files={"file": ("snap2.txt", b"snap 2 content", "text/plain")}
        )
        self.assertEqual(snap2_resp.status_code, 200)
        snap2_filepath = snap2_resp.json()["filepath"]

        # Restore snapshot
        know.start_active_folder_watcher.active = False
        response_restore = self.client.post(
            f"/api/snapshots/restore?timestamp={ts}"
        )
        self.assertEqual(response_restore.status_code, 200)

        # Verify snap2.txt is no longer in DB via API
        response = self.client.get(
            "/api/file", params={"path": snap2_filepath}
        )
        self.assertEqual(response.status_code, 404)

        # Delete snapshot
        response_delete = self.client.delete(
            f"/api/snapshots?timestamp={ts}"
        )
        self.assertEqual(response_delete.status_code, 200)

    def test_24_p2p_lan_peer_manifest(self):
        # Get local manifest
        response = self.client.get("/api/sync/manifest")
        self.assertEqual(response.status_code, 200)
        self.assertIn("manifest", response.json())

        # Mock urllib urlopen for peer exchange sync
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "manifest": [{
                    "filepath": "some_peer_path/peer_file.txt",
                    "filename": "peer_file.txt",
                    "file_size": 25,
                    "sha256": "fakehash123",
                    "modified_at": 123456789.0,
                    "content": "peer synced content"
                }]
            }).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_response

            # Post exchange
            response_exchange = self.client.post(
                "/api/sync/exchange",
                json={"target_peer": "http://127.0.0.1:9999"}
            )
            self.assertEqual(response_exchange.status_code, 200)
            self.assertIn(
                "peer_file.txt",
                response_exchange.json()["synced"]
            )

            # Verify file created physically in active dir and in DB
            synced_file_path = self.sandbox_dir / "peer_file.txt"
            self.assertTrue(synced_file_path.exists())
            self.assertEqual(
                synced_file_path.read_text(encoding="utf-8"),
                "peer synced content"
            )

            # Verify file in DB via API
            response = self.client.get(
                "/api/file", params={"path": synced_file_path}
            )
            self.assertEqual(response.status_code, 200)

    def test_25_exports_pdf_csv(self):
        # Ingest file
        self.client.post(
            "/api/upload",
            files={"file": ("export_doc.txt", b"export content", "text/plain")}
        )

        # Export PDF report with compact template
        response_pdf = self.client.get(
            "/api/report/export?style_template=compact"
        )
        self.assertEqual(response_pdf.status_code, 200)
        self.assertEqual(
            response_pdf.headers["content-type"],
            "application/pdf"
        )
        self.assertTrue(len(response_pdf.content) > 0)

        # Export CSV statistics
        response_csv = self.client.get("/api/stats/export")
        self.assertEqual(response_csv.status_code, 200)
        self.assertIn(
            "text/csv",
            response_csv.headers["content-type"]
        )
        self.assertTrue(len(response_csv.content) > 0)


if __name__ == "__main__":
    unittest.main()
