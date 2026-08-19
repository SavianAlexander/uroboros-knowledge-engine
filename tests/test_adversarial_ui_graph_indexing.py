import os
import sys
import threading
import shutil
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.core.config as config
import src.infrastructure.database as db
import know

def mock_watcher(directory, callback=None):
    pass

know.start_active_folder_watcher = mock_watcher

import main
from fastapi.testclient import TestClient


class TestAdversarialI3(unittest.TestCase):
    """Domain 24: Adversarial Indexing & Query Cache Invalidation Test Suite."""

    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path("test_sandbox_adversarial").resolve()
        if cls.sandbox.exists():
            shutil.rmtree(cls.sandbox, ignore_errors=True)
        cls.sandbox.mkdir(parents=True, exist_ok=True)

        know.reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = "adversarial_i3.db" + suffix
            if os.path.exists(fpath):
                for _ in range(10):
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                        os.remove(fpath)
                        break
                    except OSError:
                        threading.Event().wait(0.05)

        cls.orig_db_file = db.DB_FILE
        cls.orig_know_db_file = getattr(know, "DB_FILE", db.DB_FILE)
        cls.orig_active_dir = config.ACTIVE_DIR
        db.DB_FILE = "adversarial_i3.db"
        know.DB_FILE = "adversarial_i3.db"
        config.ACTIVE_DIR = str(cls.sandbox)
        know.init_db()

        files_data = [
            ("formula.txt", "This is an astrophysics formula about gravity and quantum physics."),
            ("data_analysis.txt", "Astrophysics statistics data report about planetary orbit and gravity."),
            ("quantum.txt", "Quantum mechanics explains the behavior of subatomic particles and physics."),
            ("chemistry.txt", "Organic chemistry molecules study and molecular physics bond calculations."),
            ("general.txt", "General document about gravity in astrophysics context.")
        ]

        os.makedirs(cls.sandbox, exist_ok=True)
        for fname, content in files_data:
            fpath = cls.sandbox / fname
            fpath.write_text(content, encoding="utf-8")

        know.index_directory(str(cls.sandbox))

    @classmethod
    def tearDownClass(cls):
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = "adversarial_i3.db" + suffix
            if os.path.exists(fpath):
                for _ in range(10):
                    try:
                        from src.infrastructure.database import reset_db_connections
                        reset_db_connections()
                        os.remove(fpath)
                        break
                    except OSError:
                        threading.Event().wait(0.05)

        if cls.sandbox.exists():
            for _ in range(10):
                try:
                    shutil.rmtree(cls.sandbox, ignore_errors=True)
                    break
                except OSError:
                    threading.Event().wait(0.05)

        db.DB_FILE = cls.orig_db_file
        know.DB_FILE = cls.orig_know_db_file
        config.ACTIVE_DIR = cls.orig_active_dir

    def setUp(self):
        db.DB_FILE = "adversarial_i3.db"
        config.ACTIVE_DIR = str(self.sandbox)

    def tearDown(self):
        pass

    def test_02_cache_no_empty_when_indexing(self):
        """
        Preconditions: Global query cache initialized with search API endpoints active.
        Invariants: Empty search result sets produced while an 'IndexerThread' is running must not be cached.
        Outcomes: Unmatched search queries return 0 results and leave cache key unpopulated when IndexerThread is active; non-empty search results cache normally.
        """
        main.GLOBAL_QUERY_CACHE.invalidate()
        main.GLOBAL_QUERY_CACHE.hits = 0
        main.GLOBAL_QUERY_CACHE.misses = 0

        res1 = main.GLOBAL_QUERY_CACHE.get("empty_query")
        self.assertIsNone(res1)

        client = TestClient(main.app)
        response = client.get("/api/search?q=notexistinanyfile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 0)

        cache_key = "notexistinanyfile:keyword:None:OR"
        self.assertIsNotNone(main.GLOBAL_QUERY_CACHE.get(cache_key))

        mock_indexer = threading.Thread(name="IndexerThread", target=lambda: threading.Event().wait(2.0))
        mock_indexer.start()

        main.GLOBAL_QUERY_CACHE.invalidate()
        response = client.get("/api/search?q=anothernotexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 0)

        cache_key_2 = "anothernotexistent:keyword:None:OR"
        self.assertIsNone(main.GLOBAL_QUERY_CACHE.get(cache_key_2))

        response_ok = client.get("/api/search?q=gravity")
        self.assertEqual(response_ok.status_code, 200)
        self.assertGreater(len(response_ok.json()["results"]), 0)

        cache_key_ok = "gravity:keyword:None:OR"
        self.assertIsNotNone(main.GLOBAL_QUERY_CACHE.get(cache_key_ok))

        mock_indexer.join(timeout=3.0)


if __name__ == "__main__":
    unittest.main()