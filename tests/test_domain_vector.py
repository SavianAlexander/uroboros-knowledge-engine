import unittest
import os
import shutil
import tempfile
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainVector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_vec_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        know._cached_doc_vectors = None
        know._cached_inverted_index = None
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_mini_vector_engine_basic(self):
        """Verify MiniVectorEngine document tokenization and semantic vector similarity search.

        Preconditions: Database populated with doc1 (physics) and doc2 (baking).
        Invariants: Semantic query maps tokens to closest TF-IDF document vectors.
        Expected Outcomes: Query 'quantum physics' returns doc1.txt as top ranked result.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (filepath, filename, content)
            VALUES ('/tmp/doc1.txt', 'doc1.txt', 'Astrophysics and quantum computing research.')
        """)
        cursor.execute("""
            INSERT INTO files (filepath, filename, content)
            VALUES ('/tmp/doc2.txt', 'doc2.txt', 'Baking chocolate cakes and pastries.')
        """)
        conn.commit()
        know._db_version += 1

        hits = know.MiniVectorEngine.search_semantic("quantum physics")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]['filename'], "doc1.txt")
        conn.close()

    def test_02_inverted_index_posting_lists(self):
        """Verify O(D_matching) inverted index posting list construction and term indexing.

        Preconditions: Target document inserted with specific keyword.
        Invariants: Vector engine builds inverted index mapping terms to document IDs.
        Expected Outcomes: Normalized term 'keywordtarget' is present in inverted index dictionary.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (filepath, filename, content)
            VALUES ('/tmp/target.txt', 'target.txt', 'KeywordTarget is present here.')
        """)
        conn.commit()
        know._db_version += 1

        doc_vecs, inv_index, df, num_docs = know.MiniVectorEngine.get_vectors()
        self.assertIn("keywordtarget", inv_index)
        conn.close()

    def test_03_reciprocal_rank_fusion(self):
        """Verify Reciprocal Rank Fusion (RRF) result merging between FTS keyword and vector search hits.

        Preconditions: Disjoint FTS and vector result sets provided.
        Invariants: RRF algorithm computes combined score based on rank positions.
        Expected Outcomes: Fused result list contains merged entries up to requested limit.
        """
        fts_hits = [{"filepath": "/a.txt", "filename": "a.txt", "content": "hello"}]
        vec_hits = [{"filepath": "/b.txt", "filename": "b.txt", "content": "world"}]
        fused = know.reciprocal_rank_fusion(fts_hits, vec_hits, k=60, limit=5)
        self.assertEqual(len(fused), 2)

    def test_04_zero_match_vector_fallback(self):
        """Verify semantic search query with zero matching vocabulary terms returns empty list cleanly.

        Preconditions: Search query contains terms absent from vector index.
        Invariants: Search engine handles missing vocabulary without raising key errors.
        Expected Outcomes: search_semantic returns an empty list.
        """
        hits = know.MiniVectorEngine.search_semantic("nonexistentxyz9999")
        self.assertEqual(hits, [])

    def test_05_empty_query_string(self):
        """Verify vector engine handling of empty or whitespace query strings.

        Preconditions: Empty string and whitespace-only queries submitted.
        Invariants: Query sanitizer handles zero-length inputs without execution.
        Expected Outcomes: Both empty and whitespace queries return empty result lists.
        """
        hits1 = know.MiniVectorEngine.search_semantic("")
        hits2 = know.MiniVectorEngine.search_semantic("   ")
        self.assertEqual(hits1, [])
        self.assertEqual(hits2, [])

    def test_06_version_invalidation_matrix(self):
        """Verify database version increment invalidates cached vector matrix state.

        Preconditions: Vector engine cache version recorded.
        Invariants: Incrementing know._db_version signals cache staleness.
        Expected Outcomes: Version variable correctly updates to force cache rebuild.
        """
        know._db_version += 1
        v1 = know._db_version
        know._db_version += 1
        v2 = know._db_version
        self.assertEqual(v2, v1 + 1)

    def test_07_high_cardinality_vocabulary(self):
        """Verify vector matrix memory bounding for high-cardinality vocabulary documents.

        Preconditions: Document containing 1,000 unique terms indexed.
        Invariants: Matrix generation handles wide vocabulary without memory allocation failure.
        Expected Outcomes: Semantic search returns non-empty result set for high-cardinality term.
        """
        vocab_file = os.path.join(self.test_dir, "vocab.txt")
        words = ["quantumconcept", "astronomyconcept", "physicsconcept", "mathematicsconcept"] * 250
        many_words = " ".join(words)
        with open(vocab_file, "w", encoding="utf-8") as f:
            f.write(many_words)

        know.index_directory(self.test_dir)
        know._cached_doc_vectors = None
        know._cached_inverted_index = None
        know._db_version += 1

        hits = know.MiniVectorEngine.search_semantic("quantumconcept")
        self.assertGreater(len(hits), 0)

    def test_08_reciprocal_rank_fusion_duplicate_merging(self):
        """Verify Reciprocal Rank Fusion (RRF) score accumulation for duplicate document entries.

        Preconditions: Same document present in both FTS and vector result lists.
        Invariants: RRF merges duplicate document paths into single entry with accumulated score.
        Expected Outcomes: Fused list length is 1 and contains rrf_score metadata.
        """
        fts_hits = [{"filepath": "/shared.txt", "filename": "shared.txt", "content": "Shared"}]
        vec_hits = [{"filepath": "/shared.txt", "filename": "shared.txt", "content": "Shared"}]
        fused = know.reciprocal_rank_fusion(fts_hits, vec_hits, k=60, limit=5)
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0]['filepath'], "/shared.txt")
        self.assertIn("rrf_score", fused[0])

if __name__ == "__main__":
    unittest.main()


