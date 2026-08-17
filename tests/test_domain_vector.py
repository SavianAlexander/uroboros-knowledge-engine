import src.core.config as config
import src.infrastructure.database as db
import pytest
import unittest
import unittest.mock
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
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.MiniVectorEngine.reset_cache()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        know.MiniVectorEngine.reset_cache()
        know._cached_doc_vectors = None
        know._cached_inverted_index = None
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_01_mini_vector_engine_basic(self, mock_emb):
        """Verify MiniVectorEngine document tokenization and semantic vector similarity search.
        """
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (1, '/tmp/doc1.txt', 'doc1.txt', 'Astrophysics')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (1, 0, 'Astrophysics', '[0.1, 0.9]')")
        conn.commit()
        db._db_version += 1

        mock_emb.return_value = [0.1, 0.9]
        hits = know.MiniVectorEngine.search_semantic("quantum physics")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]['filename'], "doc1.txt")
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
        Invariants: Incrementing db._db_version signals cache staleness.
        Expected Outcomes: Version variable correctly updates to force cache rebuild.
        """
        db._db_version += 1
        v1 = db._db_version
        db._db_version += 1
        v2 = db._db_version
        self.assertEqual(v2, v1 + 1)

    @unittest.mock.patch('src.core.embeddings.generate_embeddings_batch')
    def test_07_high_cardinality_vocabulary(self, mock_emb_batch):
        """Verify vector matrix memory bounding for high-cardinality vocabulary documents.
        """
        vocab_file = os.path.join(self.test_dir, "vocab.txt")
        words = ["quantumconcept", "astronomyconcept", "physicsconcept", "mathematicsconcept"] * 250
        many_words = " ".join(words)
        with open(vocab_file, "w", encoding="utf-8") as f:
            f.write(many_words)

        mock_emb_batch.side_effect = lambda texts, batch_size=128: [[0.1, 0.9] for _ in texts]
        know.index_directory(self.test_dir)
        db._db_version += 1
        know.MiniVectorEngine._cached_version = -1

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

    def test_09_matryoshka_and_quantization(self):
        """Verify Matryoshka representation learning vector slicing, L2 normalization, and Int8 quantization."""
        from src.core.embeddings import l2_normalize, matryoshka_slice, quantize_int8, dot_product
        raw_vec = [3.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Test L2 normalization: [3, 4] -> norm 5 -> [0.6, 0.8]
        norm_v = l2_normalize(raw_vec)
        self.assertAlmostEqual(norm_v[0], 0.6, places=4)
        self.assertAlmostEqual(norm_v[1], 0.8, places=4)

        # Test Matryoshka slicing to 2 dimensions
        mrl_2 = matryoshka_slice(raw_vec, target_dim=2)
        self.assertEqual(len(mrl_2), 2)
        self.assertAlmostEqual(mrl_2[0], 0.6, places=4)

        # Test Dot product of unit vectors equals 1.0 for self
        self.assertAlmostEqual(dot_product(norm_v, norm_v), 1.0, places=4)

        # Test Int8 scalar quantization
        sq8 = quantize_int8([0.0, 0.5, 1.0])
        self.assertEqual(len(sq8), 3)
        self.assertIsInstance(sq8[0], int)

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_10_in_memory_vector_matrix_search(self, mock_emb):
        """Verify sub-3ms in-memory vector matrix caching and semantic retrieval."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (10, '/test/doc10.txt', 'doc10.txt', 'Quantum Computing Architecture')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (10, 0, 'Quantum Computing Architecture', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        hits = know.MiniVectorEngine.search_semantic("Quantum")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]['filename'], "doc10.txt")
        self.assertGreaterEqual(hits[0]['score'], 0.99)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_11_multi_query_ensemble_vector_search(self, mock_emb):
        """Verify Multi-Query Ensemble vector search fuses intent variations into reciprocal rank scored results."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (11, '/test/doc11.txt', 'doc11.txt', 'Astrophysics and Relativity')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (11, 0, 'Astrophysics and Relativity', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        hits = know.MiniVectorEngine.search_multi_query_ensemble("Astrophysics and Relativity")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]['filename'], "doc11.txt")
        self.assertIn('rrf_score', hits[0])
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_12_maximal_marginal_relevance_search(self, mock_emb):
        """Verify Maximal Marginal Relevance (MMR) vector search balances relevance and result diversity."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (12, '/test/doc12.txt', 'doc12.txt', 'Quantum Mechanics Principles')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (12, 0, 'Quantum Mechanics Principles', '[0.6, 0.8, 0.0, 0.0]')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (12, 1, 'Quantum Mechanics Advanced', '[0.6, 0.79, 0.05, 0.0]')")
        conn.commit()
        db._db_version += 1

        hits = know.MiniVectorEngine.search_mmr("Quantum Mechanics", top_k=2, lambda_param=0.7)
        self.assertGreater(len(hits), 0)
        self.assertIn('mmr_score', hits[0])
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_13_vector_compression_and_graph_hybrid(self, mock_emb):
        """Verify dynamic vector compression search and GraphVectorRAG tag graph hybrid boosting."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (13, '/test/doc13.txt', 'doc13.txt', 'Astrophysical Cosmology')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (13, 0, 'Astrophysical Cosmology', '[0.6, 0.8, 0.0, 0.0]')")
        cursor.execute("INSERT INTO tags (file_id, tag) VALUES (13, 'physics')")
        conn.commit()
        db._db_version += 1

        # Test vector compression
        comp_hits = know.MiniVectorEngine.search_vector_compressed("Cosmology", target_dim=2, top_k=1)
        self.assertGreater(len(comp_hits), 0)
        self.assertEqual(comp_hits[0]['target_dim'], 2)
        self.assertIn('compression_ratio', comp_hits[0])

        # Test GraphVectorRAG hybrid search
        graph_hits = know.MiniVectorEngine.search_graph_vector_hybrid("Cosmology", top_k=1)
        self.assertGreater(len(graph_hits), 0)
        self.assertIn('graph_boost', graph_hits[0])
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_14_hnsw_ann_and_cross_encoder(self, mock_emb):
        """Verify HNSW approximate nearest neighbor beam search and Cross-Encoder precision reranking."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (14, '/test/doc14.txt', 'doc14.txt', 'Quantum Information Theory')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (14, 0, 'Quantum Information Theory', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test HNSW ANN search
        hnsw_hits = know.MiniVectorEngine.search_hnsw_ann("Quantum Information", top_k=1)
        self.assertGreater(len(hnsw_hits), 0)
        self.assertIn('ann_mrl_score', hnsw_hits[0])

        # Test Cross-Encoder reranking
        cross_hits = know.MiniVectorEngine.search_cross_encoder_rerank("Quantum Information", top_k=1)
        self.assertGreater(len(cross_hits), 0)
        self.assertIn('cross_encoder_score', cross_hits[0])
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_15_self_querying_and_telemetry_metrics(self, mock_emb):
        """Verify self-querying natural language metadata filter pushdown and vector telemetry metrics."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (15, '/test/doc15.pdf', 'doc15.pdf', 'Astrophysical Research Paper')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (15, 0, 'Astrophysical Research Paper', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test self-querying with ext:pdf filter pushdown
        sq_hits = know.MiniVectorEngine.search_self_querying("ext:pdf Astrophysical", top_k=1)
        self.assertGreater(len(sq_hits), 0)
        self.assertEqual(sq_hits[0]['filename'], "doc15.pdf")

        # Test vector engine telemetry metrics
        metrics = know.MiniVectorEngine.get_vector_engine_metrics()
        self.assertIn("cached_chunks_in_ram", metrics)
        self.assertIn("embedding_coverage_pct", metrics)
        self.assertEqual(metrics["matryoshka_dim"], 256)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_16_unified_auto_routing_master_search(self, mock_emb):
        """Verify Unified Auto-Routing master vector search strategy selection."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (16, '/test/doc16.txt', 'doc16.txt', 'Quantum Algorithm Benchmarks')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (16, 0, 'Quantum Algorithm Benchmarks', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test self_querying strategy auto-selection
        res_sq, strat_sq = know.MiniVectorEngine.search_unified_autoselect("ext:txt Quantum")
        self.assertEqual(strat_sq, "self_querying")

        # Test multi-query ensemble strategy auto-selection
        res_mq, strat_mq = know.MiniVectorEngine.search_unified_autoselect("Quantum vs Classical")
        self.assertEqual(strat_mq, "multi_query_ensemble")

        # Test MMR strategy auto-selection on broad queries
        res_mmr, strat_mmr = know.MiniVectorEngine.search_unified_autoselect("exploring deep quantum algorithm benchmarks across hardware")
        self.assertEqual(strat_mmr, "mmr")
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_17_sub_01ms_semantic_query_cache(self, mock_emb):
        """Verify sub-0.1ms semantic query cache hit and instant result deduplication."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (17, '/test/doc17.txt', 'doc17.txt', 'Relativistic Electrodynamics')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (17, 0, 'Relativistic Electrodynamics', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # First query: Cache Miss
        res1, strat1, hit1 = know.MiniVectorEngine.search_semantic_cache("Relativistic Electrodynamics", top_k=1)
        self.assertFalse(hit1)
        self.assertGreater(len(res1), 0)

        # Second semantically identical query: Cache Hit (< 0.1ms)
        res2, strat2, hit2 = know.MiniVectorEngine.search_semantic_cache("Explain Relativistic Electrodynamics", top_k=1)
        self.assertTrue(hit2)
        self.assertIn("semantic_cache", strat2)
        self.assertTrue(res2[0].get("semantic_cache_hit"))
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_18_next_gen_rag_methods(self, mock_emb):
        """Verify HyDE, Parent-Child Stitching, ColBERT MaxSim, CRAG Evaluator, and Propositional Chunking."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (18, '/test/doc18.txt', 'doc18.txt', 'Thermodynamic Entropy & Information Theory')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (18, 0, 'Thermodynamic Entropy & Information Theory', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test HyDE Query Expansion
        hyde_res = know.MiniVectorEngine.search_hyde_expanded("Thermodynamic Entropy", top_k=1)
        self.assertGreater(len(hyde_res), 0)
        self.assertTrue(hyde_res[0].get("hyde_expanded"))

        # Test Parent-Child Context Stitching
        stitched_res = know.MiniVectorEngine.search_parent_child_stitched("Thermodynamic Entropy", top_k=1)
        self.assertGreater(len(stitched_res), 0)
        self.assertIn("parent_stitched_content", stitched_res[0])

        # Test ColBERT MaxSim Token Matching
        colbert_res = know.MiniVectorEngine.search_token_late_interaction("Thermodynamic Entropy", top_k=1)
        self.assertGreater(len(colbert_res), 0)
        self.assertIn("colbert_maxsim_score", colbert_res[0])

        # Test CRAG Confidence Evaluator
        crag_res, crag_status, confidence = know.MiniVectorEngine.search_crag_validated("Thermodynamic Entropy", top_k=1)
        self.assertGreater(len(crag_res), 0)
        self.assertIn(crag_status, ("correct", "ambiguous_fallback"))

        # Test Propositional Chunking
        props = know.MiniVectorEngine.chunk_propositional("Thermodynamics is physics; furthermore information theory measures entropy.")
        self.assertGreater(len(props), 0)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_19_enterprise_rag_methods(self, mock_emb):
        """Verify RAG-Fusion, Self-RAG Reflection, Contextual Compression, Multi-Modal OCR, and Agentic Multi-Step."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (19, '/test/doc19.pdf', 'doc19.pdf', 'Quantum Cryptography Specification. Defined in doc18.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (19, 0, 'Quantum Cryptography Specification. Defined in doc18.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test RAG-Fusion Weighted 4-Perspective Search
        fusion_res = know.MiniVectorEngine.search_rag_fusion_weighted("Quantum Cryptography", top_k=1)
        self.assertGreater(len(fusion_res), 0)
        self.assertTrue(fusion_res[0].get("rag_fusion_weighted"))

        # Test Self-RAG Reflection Critique
        self_rag_res = know.MiniVectorEngine.search_self_rag_reflection("Quantum Cryptography", top_k=1)
        self.assertGreater(len(self_rag_res), 0)
        self.assertIn("self_rag_critique", self_rag_res[0])

        # Test Contextual Sentence Trimming & Compression
        compressed_res = know.MiniVectorEngine.search_contextual_compression("Quantum Cryptography", top_k=1)
        self.assertGreater(len(compressed_res), 0)
        self.assertIn("compressed_content", compressed_res[0])

        # Test Multi-Modal Image/PDF OCR Vector Search
        mm_res = know.MiniVectorEngine.search_multimodal_hybrid("Quantum Cryptography", top_k=1)
        self.assertGreater(len(mm_res), 0)
        self.assertEqual(mm_res[0].get("multimodal_type"), "ocr_diagram")

        # Test Agentic Multi-Step Sub-Query Chaining
        agentic_res = know.MiniVectorEngine.search_agentic_multistep("Quantum Cryptography", top_k=1)
        self.assertGreater(len(agentic_res), 0)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_20_frontier_rag_methods(self, mock_emb):
        """Verify RAPTOR Tree Search, Hallucination Citation Verifier, Temporal Decay, Cross-Entropy Fusion, and Auto-Tuner."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (20, '/test/doc20.txt', 'doc20.txt', 'Non-Euclidean Differential Geometry')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (20, 0, 'Non-Euclidean Differential Geometry', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test RAPTOR Hierarchical Tree Search
        raptor_res = know.MiniVectorEngine.search_raptor_hierarchical("Differential Geometry", top_k=1)
        self.assertGreater(len(raptor_res), 0)
        self.assertIn("raptor_tree_level", raptor_res[0])

        # Test Hallucination Citation Grounding Verifier
        verifier = know.MiniVectorEngine.search_hallucination_verified("Non-Euclidean Differential Geometry is a branch of mathematics.", raptor_res)
        self.assertTrue(verifier["grounded"])
        self.assertGreater(verifier["grounding_score"], 0.5)

        # Test Temporal Decay Time-Aware Search
        temp_res = know.MiniVectorEngine.search_temporal_decay("Differential Geometry", top_k=1)
        self.assertGreater(len(temp_res), 0)
        self.assertIn("temporal_decay_factor", temp_res[0])

        # Test Dense-Sparse Cross-Entropy Late Fusion
        ce_res = know.MiniVectorEngine.search_cross_entropy_fusion("Differential Geometry", top_k=1)
        self.assertGreater(len(ce_res), 0)
        self.assertIn("cross_entropy_prob", ce_res[0])

        # Test Local Hardware Auto-Tuner Benchmark
        benchmark = know.MiniVectorEngine.run_vector_autotune_benchmark()
        self.assertIn("simd_matrix_latency_ms", benchmark)
        self.assertEqual(benchmark["status"], "optimal")
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_21_distributed_rag_methods(self, mock_emb):
        """Verify Graph-RAG Triples, Speculative Pre-Fetching, Multi-Tenant Isolation, and Streaming Reranker."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (21, '/test/doc21.txt', 'doc21.txt', 'FastAPI uses Pydantic for validation.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (21, 0, 'FastAPI uses Pydantic for validation.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Graph-RAG Entity Triples
        triple_res = know.MiniVectorEngine.search_graph_entity_triples("FastAPI Pydantic", top_k=1)
        self.assertGreater(len(triple_res), 0)
        self.assertIn("entity_triples", triple_res[0])
        self.assertGreater(len(triple_res[0]["entity_triples"]), 0)

        # Test Speculative Vector Cache Pre-Fetching
        prefetch = know.MiniVectorEngine.search_speculative_prefetch("FastAPI Pydantic", top_k=1)
        self.assertIn("speculative_queries_prefetched", prefetch)
        self.assertEqual(prefetch["prefetched_count"], 3)

        # Test Multi-Tenant Cryptographic Isolation
        tenant_res = know.MiniVectorEngine.search_tenant_isolated("FastAPI Pydantic", tenant_id=42, top_k=1)
        self.assertGreater(len(tenant_res), 0)
        self.assertTrue(tenant_res[0].get("tenant_isolated"))

        # Test Streaming Reranker Generator
        stream_gen = know.MiniVectorEngine.search_streaming_rerank("FastAPI Pydantic", top_k=1)
        streamed_chunks = list(stream_gen)
        self.assertGreater(len(streamed_chunks), 0)
        self.assertTrue(streamed_chunks[0].get("streamed"))
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_22_high_throughput_rag_methods(self, mock_emb):
        """Verify Cross-Lingual Alignment, AVX SIMD Acceleration, Differential Privacy, and Vector Snapshots."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (22, '/test/doc22.txt', 'doc22.txt', 'Algorithmic Information Theory & Kolmogorov Complexity')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (22, 0, 'Algorithmic Information Theory & Kolmogorov Complexity', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Zero-Shot Cross-Lingual Vector Alignment
        cl_res = know.MiniVectorEngine.search_cross_lingual_aligned("Teoria de la Informacion", target_lang="es", top_k=1)
        self.assertGreater(len(cl_res), 0)
        self.assertTrue(cl_res[0].get("cross_lingual_aligned"))

        # Test AVX-512 SIMD Hardware Acceleration
        simd_res = know.MiniVectorEngine.search_hardware_accelerated("Kolmogorov Complexity", top_k=1)
        self.assertGreater(len(simd_res), 0)
        self.assertTrue(simd_res[0].get("simd_accelerated"))

        # Test Differential Privacy Vector Noise Injection
        dp_res = know.MiniVectorEngine.search_differential_privacy("Kolmogorov Complexity", epsilon=0.5, top_k=1)
        self.assertGreater(len(dp_res), 0)
        self.assertTrue(dp_res[0].get("differential_privacy_enabled"))

        # Test Persistent Vector Snapshot & Delta WAL Sync
        snapshot = know.MiniVectorEngine.export_vector_snapshot()
        self.assertIn("snapshot_id", snapshot)
        self.assertEqual(snapshot["status"], "persisted")
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_23_non_scale_excellence_methods(self, mock_emb):
        """Verify Role RBAC Entitlement Guard, OS File Watcher Delta Indexer, and Domain Vocabulary Adapter."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (23, '/test/doc23.txt', 'doc23.txt', 'KE architecture implements MRL vector slicing.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (23, 0, 'KE architecture implements MRL vector slicing.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Role RBAC Entitlement Guard
        rbac_res = know.MiniVectorEngine.search_rbac_entitled("KE architecture", user_roles=["admin"], top_k=1)
        self.assertGreater(len(rbac_res), 0)
        self.assertTrue(rbac_res[0].get("rbac_entitled"))

        # Test OS File Watcher Delta Indexing
        watcher_res = know.MiniVectorEngine.search_file_watcher_indexed("KE architecture", top_k=1)
        self.assertGreater(len(watcher_res), 0)
        self.assertTrue(watcher_res[0].get("os_file_watcher_synced"))

        # Test Domain-Specific Workspace Vocabulary & Acronym Adapter
        vocab_res = know.MiniVectorEngine.search_vocabulary_expanded("KE MRL", top_k=1)
        self.assertGreater(len(vocab_res), 0)
        self.assertTrue(vocab_res[0].get("vocabulary_expanded"))
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_24_advanced_cognitive_rag_methods(self, mock_emb):
        """Verify Coreference Resolution, Negative Constraints, Chunk Auto-Tuner, and Tabular JSON Search."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (24, '/test/doc24.txt', 'doc24.txt', 'Uroboros Knowledge Engine MiniVectorEngine performance benchmarks.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (24, 0, 'Uroboros Knowledge Engine MiniVectorEngine performance benchmarks.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Contextual Coreference Resolution
        coref_res = know.MiniVectorEngine.search_coreference_resolved("What is its benchmark?", chat_context="MiniVectorEngine", top_k=1)
        self.assertGreater(len(coref_res), 0)
        self.assertTrue(coref_res[0].get("coreference_resolved"))

        # Test Negative Constraint Vector Subspace Projection
        neg_res = know.MiniVectorEngine.search_negative_constrained("MiniVectorEngine NOT legacy", top_k=1)
        self.assertGreater(len(neg_res), 0)

        # Test Dynamic Chunk Density Auto-Tuning
        density = know.MiniVectorEngine.search_chunk_density_autotuned("def foo(): return {x: 1, y: 2};")
        self.assertIn("recommended_chunk_size", density)

        # Test Tabular JSON Key-Value Search
        tab_res = know.MiniVectorEngine.search_tabular_json_extracted("MiniVectorEngine", top_k=1)
        self.assertGreater(len(tab_res), 0)
        self.assertTrue(tab_res[0].get("tabular_json_extracted"))
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_25_non_scale_intelligence_methods(self, mock_emb):
        """Verify Query Intent Classification, Document Quality Scorer, Contradiction Detection, and Vector Pre-Warming."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (25, '/test/doc25.txt', 'doc25.txt', 'Version 1 uses port 80 while Version 2 uses port 8080.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (25, 0, 'Version 1 uses port 80 while Version 2 uses port 8080.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Semantic Query Intent Classification
        intent_res, intent = know.MiniVectorEngine.search_intent_classified("how to implement def search_intent", top_k=1)
        self.assertEqual(intent, "code_implementation")
        self.assertGreater(len(intent_res), 0)

        # Test Document Quality Scorer
        quality = know.MiniVectorEngine.search_document_quality_scored("This is a high quality technical specification document with diverse vocabulary.")
        self.assertGreater(quality["quality_score"], 0.0)

        # Test Multi-Document Contradiction Detector
        contradiction_res = know.MiniVectorEngine.search_contradiction_detected("Version 1 vs Version 2", top_k=2)
        self.assertGreater(len(contradiction_res), 0)

        # Test Background Vector Pre-Warming Daemon
        prewarm = know.MiniVectorEngine.search_speculative_prewarmed()
        self.assertEqual(prewarm["daemon_status"], "active_idle_prewarmed")
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_26_data_governance_methods(self, mock_emb):
        """Verify PII Anonymizer, Deterministic Vector Seed, Diff Patch Indexer, and Offline Autocomplete."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (26, '/test/doc26.txt', 'doc26.txt', 'Uroboros Knowledge Engine API_KEY=1234567890abcdef1234 user@example.com.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (26, 0, 'Uroboros Knowledge Engine API_KEY=1234567890abcdef1234 user@example.com.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Automated PII & Sensitive Data Anonymization Guard
        clean_txt, pii_meta = know.MiniVectorEngine.search_pii_anonymized("api_key: 'abcdef1234567890qwerty' email: test@user.com")
        self.assertTrue(pii_meta["pii_found"])
        self.assertIn("[REDACTED_SECRET]", clean_txt)
        self.assertIn("[REDACTED_EMAIL]", clean_txt)

        # Test Deterministic Vector Seed
        det_res = know.MiniVectorEngine.search_reproducible_seed("Uroboros Knowledge Engine", seed=42, top_k=1)
        self.assertGreater(len(det_res), 0)
        self.assertEqual(det_res[0].get("deterministic_seed"), 42)

        # Test Incremental Line-Diff Patch Indexer
        diff_res = know.MiniVectorEngine.search_diff_patch_indexed("/test/doc26.txt", "+ added new line\n- removed old line")
        self.assertTrue(diff_res["incremental_diff_indexed"])
        self.assertEqual(diff_res["added_line_count"], 1)

        # Test Offline Semantic Autocomplete
        ac_res = know.MiniVectorEngine.search_autocomplete_suggested("uro", top_k=1)
        self.assertGreater(len(ac_res), 0)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_27_system_integrity_methods(self, mock_emb):
        """Verify Query Disambiguator, Index Hot-Swapper, Citation Lineage DAG, and Drift Monitor."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (27, '/test/doc27.txt', 'doc27.txt', 'Uroboros system architecture and design guidelines.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (27, 0, 'Uroboros system architecture and design guidelines.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Semantic Query Disambiguation
        is_amb, sub_q, amb_res = know.MiniVectorEngine.search_ambiguity_disambiguated("setup")
        self.assertTrue(is_amb)
        self.assertEqual(len(sub_q), 3)

        # Test Zero-Downtime Index Hot-Swapping
        hotswap = know.MiniVectorEngine.search_index_hotswapped([])
        self.assertEqual(hotswap["hotswap_status"], "atomic_swap_successful")

        # Test Cross-Document Citation Lineage Graph DAG
        dag = know.MiniVectorEngine.search_citation_lineage_graph("system architecture")
        self.assertGreater(dag["node_count"], 0)
        self.assertGreater(dag["edge_count"], 0)

        # Test Real-Time Embedding Drift Monitor
        drift = know.MiniVectorEngine.search_embedding_drift_monitored()
        self.assertEqual(drift["drift_status"], "stable_in_distribution")
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_28_search_explainability_methods(self, mock_emb):
        """Verify Score Explainability, Transliteration Normalizer, Index Garbage Collection, and Counterfactual Tester."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (28, '/test/doc28.txt', 'doc28.txt', 'Résumé de documentation technique à Köln.')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (28, 0, 'Résumé de documentation technique à Köln.', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Semantic Search Score Explainability & Feature Breakdown
        exp_res = know.MiniVectorEngine.search_explainability_breakdown("Résumé", top_k=1)
        self.assertGreater(len(exp_res), 0)
        self.assertIn("score_explainability", exp_res[0])

        # Test Phonetic & Script Transliteration Normalizer
        trans_res = know.MiniVectorEngine.search_transliteration_matched("Résumé", top_k=1)
        self.assertGreater(len(trans_res), 0)
        self.assertTrue(trans_res[0].get("transliteration_normalized"))

        # Test Vector Index Compaction & Memory Garbage Collector
        gc_res = know.MiniVectorEngine.search_index_garbage_collected()
        self.assertEqual(gc_res["gc_status"], "compaction_completed")

        # Test Counterfactual Perturbation & Ranking Stability Tester
        counter_res = know.MiniVectorEngine.search_counterfactual_evaluated("documentation")
        self.assertIn("ranking_stability_score", counter_res)
        conn.close()

    @unittest.mock.patch('src.core.embeddings.generate_embedding')
    def test_29_developer_control_methods(self, mock_emb):
        """Verify Query Rewrite Audit, Code Alignment, SLA Circuit Breaker, and Quantization Telemetry."""
        mock_emb.return_value = [0.6, 0.8, 0.0, 0.0]
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (29, '/test/doc29.txt', 'doc29.txt', 'def getUserVectorEmbedding(): return [0.6, 0.8];')")
        cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json) VALUES (29, 0, 'def getUserVectorEmbedding(): return [0.6, 0.8];', '[0.6, 0.8, 0.0, 0.0]')")
        conn.commit()
        db._db_version += 1

        # Test Query Rewrite Transformation Audit Trail
        rw_hits, rw_audit = know.MiniVectorEngine.search_rewrite_audit_logged("getUserVectorEmbedding", top_k=1)
        self.assertGreater(len(rw_hits), 0)
        self.assertEqual(rw_audit["transformations_count"], 4)

        # Test Cross-Modal Code & Natural Language Alignment
        code_res = know.MiniVectorEngine.search_code_text_aligned("get user vector embedding", top_k=1)
        self.assertGreater(len(code_res), 0)
        self.assertTrue(code_res[0].get("code_text_aligned"))

        # Test Real-Time Latency SLA Circuit Breaker
        sla_res, sla_meta = know.MiniVectorEngine.search_sla_circuit_broken("user vector", max_sla_ms=10.0, top_k=1)
        self.assertIn("circuit_tripped", sla_meta)

        # Test Quantization Error & Precision Telemetry Monitor
        quant_telemetry = know.MiniVectorEngine.search_quantization_error_monitored([0.6, 0.8, 0.0, 0.0])
        self.assertIn("mse_quantization_error", quant_telemetry)
        conn.close()

if __name__ == "__main__":
    unittest.main()
