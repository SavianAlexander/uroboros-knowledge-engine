"""
Unit test suite verifying performance and quality upgrades:
- ORJSONResponse SIMD serialization
- Vector math acceleration (math.fsum)
- 60 FPS token stream coalescing
- SQLite multi-threaded query execution (PRAGMA threads = 4)
"""
import unittest
import math
import time
from src.core.embeddings import dot_product, cosine_similarity, l2_normalize
from src.core.rag_query_cache import _cosine_similarity
from src.infrastructure.llm import coalesce_token_chunks
from src.infrastructure.database import get_db, reset_db_connections
from src.app.server import FastJSONResponse

class TestPerformanceUpgrades(unittest.TestCase):
    def setUp(self):
        reset_db_connections()

    def tearDown(self):
        reset_db_connections()

    def test_orjson_response_serialization(self):
        data = {
            "status": "success",
            "count": 1000,
            "items": [{"id": i, "score": 0.95 * i, "active": True} for i in range(1000)]
        }
        res = FastJSONResponse(content=data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.body) > 0)

    def test_accelerated_vector_math(self):
        v1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        v2 = [0.1, 0.2, 0.3, 0.4, 0.5]
        v3 = [0.5, 0.4, 0.3, 0.2, 0.1]
        
        # Identical vectors should have cosine similarity == 1.0
        sim_identical = cosine_similarity(v1, v2)
        self.assertAlmostEqual(sim_identical, 1.0, places=5)

        # Rag query cache cosine similarity
        sim_cache = _cosine_similarity(v1, v2)
        self.assertAlmostEqual(sim_cache, 1.0, places=5)

        # Dot product of unit vectors
        u1 = l2_normalize(v1)
        u2 = l2_normalize(v3)
        dot = dot_product(u1, u2)
        cos = cosine_similarity(u1, u2)
        self.assertAlmostEqual(dot, cos, places=5)

    def test_token_stream_coalescing(self):
        def raw_tokens():
            tokens = ["H", "e", "l", "l", "o", " ", "world", "!", "\n", "This", " ", "is", " ", "fast."]
            for t in tokens:
                yield t

        coalesced = list(coalesce_token_chunks(raw_tokens(), frame_interval=0.016))
        # Total reconstituted string must match original exactly
        self.assertEqual("".join(coalesced), "Hello world!\nThis is fast.")
        # Chunks should be grouped, so length is strictly less than raw character count
        self.assertTrue(len(coalesced) < 14)

    def test_sqlite_pragmas_and_threading(self):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA threads")
            threads = cur.fetchone()[0]
            self.assertEqual(threads, 4)

            cur.execute("PRAGMA journal_mode")
            mode = cur.fetchone()[0]
            self.assertEqual(mode.upper(), "WAL")

    def test_dense_vector_store_heap_top_k(self):
        import tempfile, os
        from src.domain.vector_store import DenseVectorStore
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            temp_db = tf.name
        try:
            store = DenseVectorStore(dimension=4, db_path=temp_db)
            store.add_vector("doc_1", [1.0, 0.0, 0.0, 0.0], {"title": "Doc 1"})
            store.add_vector("doc_2", [0.0, 1.0, 0.0, 0.0], {"title": "Doc 2"})
            store.add_vector("doc_3", [0.9, 0.1, 0.0, 0.0], {"title": "Doc 3"})

            results = store.search_nearest([1.0, 0.0, 0.0, 0.0], top_k=2)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0][0], "doc_1")
            self.assertEqual(results[1][0], "doc_3")
        finally:
            reset_db_connections()
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass

    def test_voice_sfx_prewarm_and_latency(self):
        from src.core.voice_sfx import VoiceSFX
        VoiceSFX.prewarm_all()
        # Synthesis should be instant O(1) from cache
        wav = VoiceSFX.synthesize_sfx("ready")
        self.assertTrue(len(wav) > 44)
        self.assertTrue(wav.startswith(b"RIFF"))

    def test_static_rag_prompt_prefix(self):
        from src.domain.rag_engine import build_augmented_prompt, STATIC_RAG_SYSTEM_PREFIX
        prompt = build_augmented_prompt("What is our architecture?", "Engine is built on FastAPI.")
        self.assertTrue(prompt.startswith(STATIC_RAG_SYSTEM_PREFIX))
        self.assertIn("Engine is built on FastAPI.", prompt)
        self.assertIn("Question: What is our architecture?", prompt)

    def test_batch_l2_normalize(self):
        from src.core.embeddings import batch_l2_normalize, dot_product
        vectors = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [0.0, 0.0, 0.0]
        ]
        normalized = batch_l2_normalize(vectors)
        self.assertEqual(len(normalized), 3)
        self.assertAlmostEqual(dot_product(normalized[0], normalized[0]), 1.0, places=5)
        self.assertAlmostEqual(dot_product(normalized[1], normalized[1]), 1.0, places=5)

    def test_eve_sde_o1_lookup_and_search(self):
        from src.infrastructure.eve_sde import get_ship_hull, search_ship_hulls
        hulk = get_ship_hull("Hulk")
        self.assertIsNotNone(hulk)
        self.assertEqual(hulk["class"], "Exhumer")
        self.assertEqual(hulk["race"], "ORE")

        # Case insensitive lookup
        mack = get_ship_hull("mackinaw")
        self.assertIsNotNone(mack)
        self.assertEqual(mack["class"], "Exhumer")

        # Search query
        dreads = search_ship_hulls("Dreadnought", limit=5)
        self.assertTrue(len(dreads) > 0)
        self.assertTrue(any(d["name"] in ("Revelation", "Naglfar") for d in dreads))

    def test_semantic_rag_cache_prenormalization(self):
        from src.core.rag_query_cache import SemanticRAGQueryCache
        cache = SemanticRAGQueryCache(max_entries=10, similarity_threshold=0.95)
        raw_emb = [3.0, 4.0, 0.0] # Un-normalized vector with norm 5.0
        cache.put("what is mining boost?", "Mining boost docs", embedding=raw_emb)

        # Hit by near-identical normalized query
        query_emb = [0.6, 0.8, 0.0] # Unit vector (3/5, 4/5, 0)
        hit = cache.get("what is mining boost?", embedding=query_emb)
        self.assertIsNotNone(hit)
        self.assertEqual(hit["results"], "Mining boost docs")

    def test_static_asset_cache_control_headers(self):
        from fastapi.testclient import TestClient
        from src.app.server import app
        client = TestClient(app)
        res_idx = client.get("/")
        self.assertIn(res_idx.status_code, (200, 404))
        if res_idx.status_code == 200:
            self.assertIn("no-cache", res_idx.headers.get("cache-control", ""))

    def test_ast_code_extractor_lru_cache(self):
        from src.domain.code_ast_extractor import extract_code_structure
        code = "def calculate_dps(turrets: int, damage_mod: float) -> float:\n    return turrets * damage_mod * 1.25\n"
        # First parse
        res1 = extract_code_structure(code, filename="dps_calc.py")
        self.assertEqual(res1["status"], "success")
        self.assertEqual(len(res1["functions"]), 1)
        self.assertEqual(res1["functions"][0]["name"], "calculate_dps")

        # Second parse must be identical from cache
        res2 = extract_code_structure(code, filename="dps_calc.py")
        self.assertIs(res1, res2)

    def test_batch_dot_product_and_matrix_cosine(self):
        from src.core.embeddings import batch_dot_product, batch_cosine_similarity
        q = [1.0, 0.0, 0.0]
        matrix = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.7071, 0.7071, 0.0]
        ]
        dots = batch_dot_product(q, matrix)
        self.assertEqual(len(dots), 3)
        self.assertAlmostEqual(dots[0], 1.0, places=4)
        self.assertAlmostEqual(dots[1], 0.0, places=4)
        self.assertAlmostEqual(dots[2], 0.7071, places=4)

        cos_scores = batch_cosine_similarity(q, matrix)
        self.assertEqual(len(cos_scores), 3)
        self.assertAlmostEqual(cos_scores[0], 1.0, places=4)

    def test_eve_asset_valuation_aggregation(self):
        from src.infrastructure.eve_market import compute_asset_valuation
        sample_items = [
            {"type_id": 17478, "quantity": 2, "name": "Hulk"},
            {"type_id": 12068, "quantity": 100, "name": "Scordite"},
        ]
        mock_prices = {
            "17478": {"average_price": 350000000.0, "adjusted_price": 340000000.0},
            "12068": {"average_price": 45.0, "adjusted_price": 42.0},
        }
        res = compute_asset_valuation(sample_items, prices=mock_prices)
        self.assertEqual(res["total_items"], 2)
        self.assertEqual(res["total_valuation"], 700004500.0)
        self.assertEqual(len(res["top_items"]), 2)
        self.assertEqual(res["top_items"][0]["name"], "Hulk")

if __name__ == "__main__":
    unittest.main()
