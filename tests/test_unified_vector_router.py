"""
Unit & API Route Verification Suite for Unified Vector Router
Covers Task #250 under EPIC #247 (Neuro Alexander Project)
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.core.config as config
import src.infrastructure.database as db_infra
import know
from main import app


class TestUnifiedVectorRouter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_unified_vector_")
        self.db_path = os.path.join(self.test_dir, "test_vector_router.db")
        
        self.old_db = db_infra.DB_FILE
        self.old_active = getattr(config, "ACTIVE_DIR", None)
        
        db_infra.DB_FILE = self.db_path
        config.ACTIVE_DIR = self.test_dir
        
        know.reset_db_connections()
        know.MiniVectorEngine.reset_cache()
        know.init_db()
        
        self.client = TestClient(app)

    def tearDown(self):
        know.reset_db_connections()
        know.MiniVectorEngine.reset_cache()
        db_infra.DB_FILE = self.old_db
        if self.old_active is not None:
            config.ACTIVE_DIR = self.old_active
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('src.core.embeddings.generate_embedding')
    def test_01_search_unified_autoselect_strategies(self, mock_emb):
        """Verify search_unified_autoselect auto-selects correct search strategies."""
        mock_emb.return_value = [0.5, 0.5, 0.0, 0.0]
        
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (100, '/test/neural.txt', 'neural.txt', 'Deep Neural Networks')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (100, 0, 'Deep Neural Networks', '[0.5, 0.5, 0.0, 0.0]')")
        know.get_db().commit()
        db_infra._db_version += 1

        # Self-querying filter pattern
        res_sq, strat_sq = know.MiniVectorEngine.search_unified_autoselect("ext:txt Neural")
        self.assertEqual(strat_sq, "self_querying")

        # Multi-query ensemble pattern
        res_mq, strat_mq = know.MiniVectorEngine.search_unified_autoselect("Transformer vs RNN architecture")
        self.assertEqual(strat_mq, "multi_query_ensemble")

        # Reranker / MMR diversity pattern
        res_mmr, strat_mmr = know.MiniVectorEngine.search_unified_autoselect("exploring deep neural network architectures across multi GPU clusters")
        self.assertIn(strat_mmr, ["mmr", "cross_encoder"])
        
        conn.close()

    def test_02_vector_metrics_endpoint(self):
        """Verify GET /api/vector/metrics returns operational telemetry."""
        response = self.client.get("/api/vector/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("active_cache_version", data)
        self.assertIn("total_chunks_in_db", data)
        self.assertIn("quantization_mode", data)

    @patch('src.core.embeddings.generate_embedding')
    def test_03_unified_vector_search_endpoint(self, mock_emb):
        """Verify GET /api/vector/search/unified returns structured JSON payload."""
        mock_emb.return_value = [0.1, 0.2, 0.3, 0.4]
        
        # Test empty query
        res_empty = self.client.get("/api/vector/search/unified?query=")
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(res_empty.json()["total"], 0)
        self.assertEqual(res_empty.json()["strategy"], "none")

        # Test valid search query
        res_valid = self.client.get("/api/vector/search/unified?query=Neural&limit=5")
        self.assertEqual(res_valid.status_code, 200)
        payload = res_valid.json()
        self.assertEqual(payload["query"], "Neural")
        self.assertIn("results", payload)
        self.assertIn("search_time_ms", payload)
        self.assertIn("strategy", payload)


if __name__ == "__main__":
    unittest.main()
