import os
import time
import json
import shutil
import unittest
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

# ponytail: override DB_FILE before importing main/know to isolate tests
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


class TestE2ETier2Tier3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def poll_api_file(
        self, filepath, expected_status=200, timeout=5.0, interval=0.1
    ):
        start = time.time()
        while time.time() - start < timeout:
            response = self.client.get("/api/file", params={"path": filepath})
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

    def _cleanup_db_files(self, db_file):
        # ponytail: robustly remove database and sidecar files on Windows
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
                    time.sleep(0.1)

    def setUp(self):
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

        # ponytail: join background threads by inspecting t._target.__name__
        for t in threading.enumerate():
            if hasattr(t, "_target") and t._target is not None:
                try:
                    name = getattr(t._target, "__name__", "")
                    if name in ["run_indexer", "watch_loop", "backup_loop"]:
                        t.join(timeout=5.0)
                except AttributeError:
                    pass

        # Clean up this test's database and its WAL/SHM sidecars
        self._cleanup_db_files(self.db_file)

        # Remove any snapshot files (and their sidecars) for this database
        for f in Path(".").glob(f"{self.db_file}.snapshot-*"):
            try:
                self._cleanup_db_files(str(f))
            except Exception:
                pass

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
    # TIER 2: FEATURE 1: WORKSPACE INGESTION & DOCUMENT PARSING
    # ==========================================

    def test_01_empty_file_upload(self):
        response = self.client.post(
            "/api/upload",
            files={"file": ("empty.txt", b"", "text/plain")}
        )
        self.assertEqual(response.status_code, 200)
        filepath = response.json()["filepath"]
        self.assertTrue(os.path.exists(filepath))

        # Check database content via API
        response = self.client.get("/api/file", params={"path": filepath})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "")

    def test_02_deeply_nested_directory_watch(self):
        deep_dir = (
            self.sandbox_dir / "a" / "b" / "c" / "d" / "e" / "f" / "g" / "h"
        )
        deep_dir.mkdir(parents=True, exist_ok=True)
        deep_file = deep_dir / "deep.txt"
        deep_file.write_text("deep nested content", encoding="utf-8")

        response = self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        # Poll until deep_file is indexed
        self.poll_api_file(str(deep_file), expected_status=200)

    def test_03_corrupt_docx_pdf_ingestion(self):
        # Create a corrupt PDF (just random text)
        corrupt_pdf = self.sandbox_dir / "corrupt.pdf"
        corrupt_pdf.write_bytes(b"NOT_A_VALID_PDF_HEADER_OR_CONTENT")

        response = self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        # Poll file
        self.poll_api_file(str(corrupt_pdf), expected_status=200)

        # Verify content contains placeholder parsing error
        response = self.client.get(
            "/api/file", params={"path": str(corrupt_pdf)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("[Parsing Error:", response.json()["content"])

    def test_04_storage_space_check_mock(self):
        with patch(
            "shutil.disk_usage",
            return_value=(100 * 1024 * 1024, 95 * 1024 * 1024, 5 * 1024 * 1024)
        ):
            response = self.client.post(
                "/api/index",
                json={"directory": str(self.sandbox_dir)}
            )
            # Expect 507 Insufficient Storage
            self.assertEqual(response.status_code, 507)
            self.assertIn("Insufficient storage", response.json()["detail"])

    def test_05_special_characters_unicode_filename(self):
        special_file = self.sandbox_dir / "Spécial & Chàracters #123.txt"
        special_file.write_text("special characters content", encoding="utf-8")

        response = self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        # Poll
        self.poll_api_file(str(special_file), expected_status=200)

        # Search
        response = self.poll_search(
            "special characters",
            expected_filename="Spécial & Chàracters #123.txt"
        )
        self.assertEqual(response.status_code, 200)

    # ==========================================
    # TIER 2: FEATURE 2: CORE HYBRID SEARCH & QUERY PARSING
    # ==========================================

    def test_06_empty_search_query(self):
        response = self.client.get("/api/search", params={"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_07_unbalanced_quotes_search_validation(self):
        response = self.client.post(
            "/api/search/validate",
            json={"query": '"unmatched quote'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["valid"])

        response = self.client.get(
            "/api/search", params={"q": '"unmatched quote'}
        )
        self.assertEqual(response.status_code, 200)

    def test_08_proximity_search_extreme_values(self):
        prox_file = self.sandbox_dir / "prox.txt"
        prox_file.write_text("wordA wordB", encoding="utf-8")
        self.client.post(
            "/api/index", json={"directory": str(self.sandbox_dir)}
        )
        self.poll_api_file(str(prox_file), expected_status=200)

        # Distance of 0
        response = self.client.get(
            "/api/search", params={"q": "NEAR(wordA wordB, 0)"}
        )
        self.assertEqual(response.status_code, 200)

        # Negative distance
        response = self.client.get(
            "/api/search", params={"q": "NEAR(wordA wordB, -5)"}
        )
        self.assertEqual(response.status_code, 200)

    def test_09_sql_injection_attempt(self):
        sqli_queries = [
            "' OR 1=1 --",
            "'; DROP TABLE files; --",
            "\" OR \"\"=\"",
        ]
        for q in sqli_queries:
            response = self.client.get("/api/search", params={"q": q})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(response.json()["results"], list))

    def test_10_search_all_items_excluded(self):
        ex_file = self.sandbox_dir / "exclude_all.txt"
        ex_file.write_text("test content here", encoding="utf-8")
        self.client.post(
            "/api/index", json={"directory": str(self.sandbox_dir)}
        )
        self.poll_api_file(str(ex_file), expected_status=200)

        # Exclude type txt
        response = self.client.get(
            "/api/search", params={"q": "test -type:txt"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    # ==========================================
    # TIER 2: FEATURE 3: QUERY EXTENSIONS
    # ==========================================

    def test_11_autocomplete_empty_or_special_token(self):
        # Empty token
        response = self.client.get("/api/search/suggest", params={"token": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggestions"], [])

        # Special character token
        response = self.client.get(
            "/api/search/suggest", params={"token": "$"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json()["suggestions"], list))

    def test_12_circular_macros_resolution(self):
        self.client.post(
            "/api/macros", json={"name": "macroA", "expansion": "%macroB%"}
        )
        self.client.post(
            "/api/macros", json={"name": "macroB", "expansion": "%macroA%"}
        )

        response = self.client.get("/api/search", params={"q": "%macroA%"})
        self.assertEqual(response.status_code, 200)

    def test_13_lru_cache_eviction_behavior(self):
        main.GLOBAL_QUERY_CACHE.invalidate()
        main.GLOBAL_QUERY_CACHE.hits = 0
        main.GLOBAL_QUERY_CACHE.misses = 0

        orig_capacity = main.GLOBAL_QUERY_CACHE.capacity
        main.GLOBAL_QUERY_CACHE.capacity = 2
        try:
            self.client.get("/api/search", params={"q": "evict1"})
            self.client.get("/api/search", params={"q": "evict2"})
            self.client.get("/api/search", params={"q": "evict3"})

            main.GLOBAL_QUERY_CACHE.hits = 0
            main.GLOBAL_QUERY_CACHE.misses = 0
            self.client.get("/api/search", params={"q": "evict1"})
            self.assertEqual(main.GLOBAL_QUERY_CACHE.misses, 1)
            self.assertEqual(main.GLOBAL_QUERY_CACHE.hits, 0)
        finally:
            main.GLOBAL_QUERY_CACHE.capacity = orig_capacity
            main.GLOBAL_QUERY_CACHE.invalidate()

    def test_14_bookmarks_duplicate_registration_collision(self):
        response = self.client.post(
            "/api/bookmarks",
            json={
                "name": "coll_bookmark",
                "query_string": "tag:physics",
                "search_mode": "keyword"
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/bookmarks",
            json={
                "name": "coll_bookmark",
                "query_string": "tag:math",
                "search_mode": "keyword"
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/bookmarks")
        self.assertEqual(response.status_code, 200)
        bookmarks = response.json()["bookmarks"]
        coll_b = [b for b in bookmarks if b["name"] == "coll_bookmark"]
        self.assertEqual(len(coll_b), 1)
        self.assertEqual(coll_b[0]["query_string"], "tag:math")

    def test_15_synonyms_cyclic_mapping(self):
        self.client.post(
            "/api/synonyms",
            json={"word": "math", "substitutes": "mathematics"}
        )
        self.client.post(
            "/api/synonyms",
            json={"word": "mathematics", "substitutes": "math"}
        )

        response = self.client.get("/api/search", params={"q": "math"})
        self.assertEqual(response.status_code, 200)

    # ==========================================
    # TIER 2: FEATURE 4: METADATA, ANNOTATIONS & RELATIONAL GRAPH
    # ==========================================

    def test_16_duplicate_tag_assignment(self):
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("dup_tag.txt", b"content", "text/plain")}
        )
        f = f_resp.json()["filepath"]

        self.client.post(
            "/api/file/tag", json={"filepath": f, "tag": "science"}
        )
        self.client.post(
            "/api/file/tag", json={"filepath": f, "tag": "science"}
        )

        response = self.client.get("/api/file", params={"path": f})
        self.assertEqual(response.status_code, 200)
        tags = response.json()["tags"]
        self.assertEqual(tags, ["science"])

    def test_17_stopwords_file_suggested_tags_empty(self):
        f_resp = self.client.post(
            "/api/upload",
            files={
                "file": (
                    "stopwords.txt",
                    b"the is and or of in on at with a an",
                    "text/plain"
                )
            }
        )
        f = f_resp.json()["filepath"]

        response = self.client.get("/api/file", params={"path": f})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggested_tags"], [])

    def test_18_auto_tagging_rules_regex_syntax_error(self):
        response = self.client.post(
            "/api/rules/test-preview",
            json={"pattern": "[a-z", "tag": "test", "priority": 1}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid regex pattern", response.json()["detail"])

    def test_19_malformed_tag_colors_input_validation(self):
        response = self.client.post(
            "/api/tags/color",
            json={"color": "#ff0000"}
        )
        self.assertEqual(response.status_code, 422)

    def test_20_wikilinks_to_non_existent_files(self):
        self.client.post(
            "/api/upload",
            files={
                "file": (
                    "wikilink.txt",
                    b"Check out [[NonExistentFile]] for more.",
                    "text/plain"
                )
            }
        )

        response = self.client.get("/api/graph")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        node_labels = [n["label"] for n in data["nodes"]]
        self.assertIn("wikilink.txt", node_labels)
        self.assertNotIn("NonExistentFile", node_labels)
        self.assertEqual(len(data["links"]), 0)

    # ==========================================
    # TIER 2: FEATURE 5: OPERATIONS, SNAPSHOTS & REPORTING
    # ==========================================

    def test_21_file_rename_collision(self):
        f1_resp = self.client.post(
            "/api/upload",
            files={"file": ("rename_f1.txt", b"content 1", "text/plain")}
        )
        f1 = f1_resp.json()["filepath"]

        self.client.post(
            "/api/upload",
            files={"file": ("rename_f2.txt", b"content 2", "text/plain")}
        )

        response = self.client.post(
            "/api/file/rename",
            json={"filepath": f1, "new_name": "rename_f2.txt"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["detail"])

    def test_22_file_rename_path_traversal(self):
        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("traversal.txt", b"content", "text/plain")}
        )
        f = f_resp.json()["filepath"]

        response = self.client.post(
            "/api/file/rename",
            json={"filepath": f, "new_name": "../traversal_escaped.txt"}
        )
        self.assertIn(response.status_code, [400, 500])

    def test_23_restore_snapshot_missing_or_invalid_timestamp(self):
        response = self.client.post(
            "/api/snapshots/restore",
            params={"timestamp": 999999999}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Snapshot not found", response.json()["detail"])

    def test_24_p2p_sync_exchange_unreachable_peer(self):
        response = self.client.post(
            "/api/sync/exchange",
            json={"target_peer": "http://127.0.0.1:9999"}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to reach peer", response.json()["detail"])

    def test_25_pdf_generation_empty_dataset(self):
        response = self.client.get(
            "/api/report/export",
            params={"tag": "nonexistent_tag"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))

    # ==========================================
    # TIER 3: CROSS-FEATURE COMBINATIONS
    # ==========================================

    def test_26_comb_ingestion_and_auto_tag_rules(self):
        # Workspace Ingestion + Auto-Tag Rules (Feature 1 + Feature 4)
        self.client.post(
            "/api/rules",
            json={"pattern": "neural", "tag": "deep-learning", "priority": 10}
        )

        rule_file = self.sandbox_dir / "neural_network.txt"
        rule_file.write_text("Mentions neural networks.", encoding="utf-8")

        self.client.post(
            "/api/index",
            json={"directory": str(self.sandbox_dir)}
        )

        self.poll_api_file(str(rule_file), expected_status=200)

        response = self.client.get(
            "/api/file", params={"path": str(rule_file)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("deep-learning", response.json()["tags"])

    def test_27_comb_edit_and_search(self):
        # Inline Content Editing + Core Hybrid Search (Feature 5 + Feature 2)
        f_resp = self.client.post(
            "/api/upload",
            files={
                "file": (
                    "search_edit.txt",
                    b"original search text here",
                    "text/plain"
                )
            }
        )
        f = f_resp.json()["filepath"]

        self.poll_search(
            "original search", expected_filename="search_edit.txt"
        )

        response = self.client.post(
            "/api/file/edit",
            json={"filepath": f, "content": "updated keyword content here"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/api/search", params={"q": "original search"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertFalse(
            any("search_edit.txt" in r["filename"] for r in results)
        )

        self.poll_search(
            "updated keyword", expected_filename="search_edit.txt"
        )

    def test_28_comb_aliases_exclusions_autocomplete(self):
        # Feature 4 + Feature 2 + Feature 3 Pairwise Combination
        self.client.post(
            "/api/aliases", json={"alias": "phys", "target": "physics"}
        )

        f_resp = self.client.post(
            "/api/upload",
            files={"file": ("alias_ex.txt", b"content", "text/plain")}
        )
        f = f_resp.json()["filepath"]
        self.client.post(
            "/api/file/tag", json={"filepath": f, "tag": "physics"}
        )

        response = self.client.get(
            "/api/search/suggest", params={"token": "tag:phy"}
        )
        self.assertEqual(response.status_code, 200)
        suggestions = [s["text"] for s in response.json()["suggestions"]]
        self.assertIn("tag:physics", suggestions)

        response = self.client.get("/api/search", params={"tag": "phys"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)

        response = self.client.get(
            "/api/search", params={"q": "-tag:physics"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertFalse(
            any("alias_ex.txt" in r["filename"] for r in results)
        )

    def test_29_comb_snapshots_and_watcher(self):
        # DB Snapshots + Workspace Ingestion Watcher (Feature 5 + Feature 1)
        file1 = self.sandbox_dir / "file1.txt"
        file1.write_text("file 1 content", encoding="utf-8")
        self.client.post(
            "/api/index", json={"directory": str(self.sandbox_dir)}
        )
        self.poll_api_file(str(file1), expected_status=200)

        response = self.client.post("/api/snapshots")
        self.assertEqual(response.status_code, 200)
        ts = response.json()["timestamp"]

        file2 = self.sandbox_dir / "file2.txt"
        file2.write_text("file 2 content", encoding="utf-8")
        self.client.post(
            "/api/index", json={"directory": str(self.sandbox_dir)}
        )
        self.poll_api_file(str(file2), expected_status=200)

        know.start_active_folder_watcher.active = False
        response = self.client.post(
            "/api/snapshots/restore", params={"timestamp": ts}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/file", params={"path": str(file2)})
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            "/api/index", json={"directory": str(self.sandbox_dir)}
        )
        self.assertEqual(response.status_code, 200)

        self.poll_api_file(str(file2), expected_status=200)

    def test_30_comb_macros_and_p2p_sync(self):
        # Macros Expansion + P2P LAN Sync (Feature 3 + Feature 5)
        self.client.post(
            "/api/macros", json={"name": "scidoc", "expansion": "science"}
        )

        peer_manifest = {
            "manifest": [
                {
                    "filename": "synced_macro_file.txt",
                    "file_size": 25,
                    "sha256": "abcdef1234567890",
                    "modified_at": time.time(),
                    "content": "science data and quantum results"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(peer_manifest).encode(
            "utf-8"
        )
        mock_response.__enter__.return_value = mock_response

        # ponytail: mock sync exchange peer response
        with patch("urllib.request.urlopen", return_value=mock_response):
            response = self.client.post(
                "/api/sync/exchange",
                json={"target_peer": "http://127.0.0.1:9999"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("synced_macro_file.txt", response.json()["synced"])

        response = self.poll_search(
            "%scidoc%", expected_filename="synced_macro_file.txt"
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertTrue(
            any("synced_macro_file.txt" in r["filename"] for r in results)
        )
