import unittest
import know
from src.domain.rag_engine import sanitize_fts_query

class TestAdvancedRAG(unittest.TestCase):
    def test_reciprocal_rank_fusion(self):
        fts_list = [
            {"filepath": "docA.txt", "filename": "docA.txt", "content": "alpha"},
            {"filepath": "docB.txt", "filename": "docB.txt", "content": "beta"}
        ]
        vector_list = [
            {"filepath": "docB.txt", "filename": "docB.txt", "content": "beta"},
            {"filepath": "docC.txt", "filename": "docC.txt", "content": "gamma"}
        ]
        fused = know.rrf_rerank(fts_list, vector_list, k=60)
        self.assertGreater(len(fused), 0)
        # docB is present in both lists, so its RRF score should be highest!
        top_filepath = fused[0]["filepath"]
        self.assertEqual(top_filepath, "docB.txt")
        self.assertIn("rrf_score", fused[0])

    def test_generate_hyde_expansion(self):
        expanded = know.generate_hyde_expansion("what is database lock?")
        self.assertIn("database lock", expanded)

    def test_sanitize_fts_query(self):
        raw_query = 'what is "database" OR lock (near:table) / test*?'
        sanitized = sanitize_fts_query(raw_query)
        self.assertNotIn('"', sanitized)
        self.assertNotIn('(', sanitized)
        self.assertNotIn(')', sanitized)
        self.assertNotIn('/', sanitized)
        self.assertIn("database", sanitized)
        self.assertIn("lock", sanitized)

    def test_jaccard_deduplicate(self):
        snippets = [
            {"filepath": "d1.txt", "content": "Quantum computing leverages qubits and superposition for exponential speedup."},
            {"filepath": "d2.txt", "content": "Quantum computing leverages qubits and superposition for exponential speedup."}, # Duplicate >= 0.70
            {"filepath": "d3.txt", "content": "Relativity principles dictate that physical laws are invariant across inertial reference frames."} # Distinct < 0.70
        ]
        deduped = know.jaccard_deduplicate(snippets, threshold=0.70)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0]["filepath"], "d1.txt")
        self.assertEqual(deduped[1]["filepath"], "d3.txt")

    def test_web_search_fetcher_offline(self):
        results = know.fetch_web_context("quantum computing overview", max_results=2)
        self.assertIsInstance(results, list)
        
        # Test class method
        results_class = know.WebSearchFetcher.search("quantum computing overview", max_results=2)
        self.assertIsInstance(results_class, list)

        # Empty query handling
        empty_res = know.fetch_web_context("")
        self.assertEqual(empty_res, [])

    def test_rrf_search_endpoint(self):
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
        res = client.get("/api/search/rrf?query=accounting")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "rrf_hybrid")
        self.assertIn("results", data)

if __name__ == "__main__":
    unittest.main()
