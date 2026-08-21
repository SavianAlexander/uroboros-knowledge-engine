"""
Automated Test Suite for Three Frontiers:
1. Streaming Anti-Drift Tokenizer Verification Filter (Sync & Async stream auditing).
2. Graph-Enhanced Multi-Hop Entity Linking Engine (BFS path finding & topology context).
3. Continuous Zero-Stutter Background Vault Watcher (IDLE-priority polling & auto-reindexing).
"""

import unittest
import os
import sys
import tempfile
import time
import json
import asyncio
import logging

from src.infrastructure.database import init_db, get_db_connection, reset_db_connections, DB_FILE
from src.infrastructure.vector_engine import index_file, MiniVectorEngine
from src.domain.streaming_verifier import StreamingAntiDriftFilter
from src.domain.entity_graph import EntityKnowledgeGraph
from src.domain.vault_watcher import ZeroStutterVaultWatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FRONTIERS_TEST")


class TestRAGFrontiers(unittest.TestCase):
    """Empirical test suite for the Three Frontiers."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        reset_db_connections()
        init_db()
        with get_db_connection(DB_FILE) as conn:
            with conn:
                conn.execute("DELETE FROM files WHERE filepath LIKE '%Temp%' OR filepath LIKE '%tmp%'")
                conn.execute("DELETE FROM parent_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                conn.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
        MiniVectorEngine.reset_cache()

    def tearDown(self):
        reset_db_connections()

    # =========================================================================
    # Frontier 1: Streaming Anti-Drift Verification Filter Tests
    # =========================================================================

    def test_streaming_verifier_sync_emission(self):
        """Test 1: Non-assertive tokens stream through with sub-10ms delay."""
        context = "SQLite database uses Write-Ahead Logging (WAL) for concurrency."
        tokens = ["The ", "database ", "uses ", "WAL ", "mode ", "to ", "support ", "concurrent ", "reads."]

        t0 = time.perf_counter()
        streamed = list(StreamingAntiDriftFilter.filter_stream_sync(iter(tokens), context))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assembled = "".join(streamed)
        logger.info(f"[STREAMING_SYNC] Assembled: '{assembled}' in {elapsed_ms:.3f}ms")
        self.assertEqual(assembled, "".join(tokens))
        self.assertLess(elapsed_ms, 15.0)

    def test_streaming_verifier_catches_and_remediates_hallucination(self):
        """Test 2: Stream with ungrounded numerical assertion (100,000 writes/sec) is remediated to 5,000 writes/sec."""
        context = "The cache cluster has a hard limit of 5,000 writes/sec per instance."
        hallucinated_tokens = ["Our ", "cache ", "easily ", "handles ", "100,000", " ", "writes/sec", " without ", "stutter."]

        streamed = list(StreamingAntiDriftFilter.filter_stream_sync(iter(hallucinated_tokens), context))
        assembled = "".join(streamed)

        logger.info(f"[STREAMING_REMEDIATED] Result: '{assembled}'")
        self.assertIn("5,000 writes/sec", assembled)
        self.assertNotIn("100,000 writes/sec", assembled)

    def test_streaming_verifier_async_stream(self):
        """Test 3: Asynchronous token generator stream auditing and remediation."""
        async def _run_async():
            context = "The system latency SLA is 20 ms under peak load."
            raw_tokens = ["Average ", "latency ", "is ", "capped ", "at ", "500", " ", "ms", " across ", "all ", "regions."]

            async def _token_gen():
                for t in raw_tokens:
                    await asyncio.sleep(0.001)
                    yield t

            filtered_tokens = []
            async for token in StreamingAntiDriftFilter.filter_stream_async(_token_gen(), context):
                filtered_tokens.append(token)

            assembled = "".join(filtered_tokens)
            logger.info(f"[STREAMING_ASYNC] Assembled: '{assembled}'")
            self.assertIn("20 ms", assembled)
            self.assertNotIn("500 ms", assembled)

        asyncio.run(_run_async())

    # =========================================================================
    # Frontier 2: Graph-Enhanced Multi-Hop Entity Linking Engine Tests
    # =========================================================================

    def test_entity_graph_multi_hop_traversal(self):
        """Test 4: Construct graph and find multi-hop dependency paths (fastapi -> sqlite -> wal)."""
        graph = EntityKnowledgeGraph()

        # Build mock topology: fastapi -> sqlite -> wal -> ntfs
        graph.add_edge("fastapi", "sqlite", relationship="DEPENDS_ON", weight=2.0)
        graph.add_edge("sqlite", "wal", relationship="CONFIGURED_VIA", weight=3.0)
        graph.add_edge("wal", "ntfs", relationship="RUNS_ON", weight=1.5)
        graph.add_edge("fastapi", "pydantic", relationship="USES_SCHEMA", weight=4.0)

        # 2-hop path: fastapi -> sqlite -> wal
        paths_2hop = graph.find_multi_hop_paths("fastapi", "wal", max_depth=2)
        logger.info(f"[ENTITY_GRAPH_PATHS] 2-Hop paths (fastapi -> wal): {paths_2hop}")
        self.assertTrue(len(paths_2hop) > 0)
        self.assertEqual(paths_2hop[0], ["fastapi", "sqlite", "wal"])

        # 3-hop path: fastapi -> sqlite -> wal -> ntfs
        paths_3hop = graph.find_multi_hop_paths("fastapi", "ntfs", max_depth=3)
        logger.info(f"[ENTITY_GRAPH_PATHS] 3-Hop paths (fastapi -> ntfs): {paths_3hop}")
        self.assertTrue(len(paths_3hop) > 0)
        self.assertEqual(paths_3hop[0], ["fastapi", "sqlite", "wal", "ntfs"])

    def test_entity_graph_neighborhood_context_rendering(self):
        """Test 5: Retrieve neighborhood topology and format markdown block for RAG."""
        graph = EntityKnowledgeGraph()
        mock_chunks = [
            {"entities_json": json.dumps(["fastapi", "pydantic", "uvicorn"])},
            {"entities_json": json.dumps(["sqlite", "wal", "python"])},
            {"entities_json": json.dumps(["fastapi", "sqlite"])}
        ]
        graph.build_from_chunks(mock_chunks)

        n_fastapi = graph.get_neighborhood("fastapi", max_neighbors=3)
        self.assertTrue(len(n_fastapi) > 0)

        context_md = graph.format_topology_context(["fastapi", "sqlite"])
        logger.info(f"[GRAPH_TOPOLOGY_MD]\n{context_md}")
        self.assertIn("Graph Knowledge Topology", context_md)
        self.assertIn("fastapi", context_md)
        self.assertIn("sqlite", context_md)

    # =========================================================================
    # Frontier 3: Continuous Zero-Stutter Background Vault Watcher Tests
    # =========================================================================

    def test_vault_watcher_polling_and_auto_indexing(self):
        """Test 6: VaultWatcher polls directory, detects new document, and auto-indexes into DB & Vector Cache."""
        watcher = ZeroStutterVaultWatcher(
            watch_directory=self.temp_dir,
            poll_interval=0.5,
            inter_task_cooling=0.01
        )

        # 1. Initial scan on empty temp dir
        res1 = watcher.poll_sync_once()
        self.assertEqual(res1["added_count"], 0)

        # 2. Add a new file to watched directory
        new_doc_path = os.path.join(self.temp_dir, "reactive_sync_spec.md")
        with open(new_doc_path, "w", encoding="utf-8") as f:
            f.write("# Reactive Sync Specification\n\nAutomated real-time file synchronization with zero thread stutter.\n")

        # 3. Trigger poll pass
        res2 = watcher.poll_sync_once()
        logger.info(f"[VAULT_WATCHER_POLL] Sync Pass 2: {res2}")
        self.assertEqual(res2["added_count"], 1)
        self.assertEqual(res2["total_tracked"], 1)

        # 4. Verify file is now searchable in vector engine
        hits = MiniVectorEngine.search_semantic("reactive sync file synchronization")
        self.assertTrue(len(hits) > 0)
        self.assertEqual(hits[0]["filename"], "reactive_sync_spec.md")

    def test_vault_watcher_daemon_thread_lifecycle(self):
        """Test 7: Start background thread, verify running state, and cleanly stop."""
        watcher = ZeroStutterVaultWatcher(
            watch_directory=self.temp_dir,
            poll_interval=0.1,
            inter_task_cooling=0.01
        )

        self.assertFalse(watcher.is_running())
        watcher.start()
        self.assertTrue(watcher.is_running())
        time.sleep(0.2)
        watcher.stop()
        self.assertFalse(watcher.is_running())


if __name__ == "__main__":
    unittest.main()
