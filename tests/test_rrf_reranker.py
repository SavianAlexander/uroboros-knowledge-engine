import unittest
import time
from src.domain.reranker import compute_rrf_scores

class TestRRFReranker(unittest.TestCase):
    def test_rrf_fusion_combines_vector_and_fts_rankings(self):
        vector_res = [
            {"id": "doc1", "filename": "doc1.txt", "score": 0.95},
            {"id": "doc2", "filename": "doc2.txt", "score": 0.80},
        ]
        fts_res = [
            {"id": "doc2", "filename": "doc2.txt", "score": 10.5},
            {"id": "doc3", "filename": "doc3.txt", "score": 8.0},
        ]
        results = compute_rrf_scores(vector_res, fts_res)
        self.assertEqual(len(results), 3)
        # doc2 appears in both vector and fts results, so it should rank first with highest RRF score
        self.assertEqual(results[0]["id"], "doc2")

    def test_rrf_recency_decay(self):
        now = time.time()
        vector_res = [
            {"id": "old_doc", "filename": "old.txt", "mtime": now - (86400 * 365)}, # 1 year old
            {"id": "new_doc", "filename": "new.txt", "mtime": now},
        ]
        results = compute_rrf_scores(vector_res, [], time_decay_lambda=0.01)
        self.assertEqual(results[0]["id"], "new_doc")

if __name__ == "__main__":
    unittest.main()
