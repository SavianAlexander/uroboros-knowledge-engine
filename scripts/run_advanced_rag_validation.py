"""
CLI Validation Harness & Profiling Runner for Advanced RAG Features:
- Parent-Child Chunking & Deduplication
- HyDE Expansion & Cosine Alignment Delta
- Lost-in-the-Middle Attention Ordering
- Grounded Guardrails (0.35 Refusal)
- End-to-End Citation Attribution
- Async Latency Profiling per Stage (<500ms)
"""

import os
import sys
import time
import asyncio
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.database import init_db
from src.core.embeddings import generate_embedding, cosine_similarity
from src.domain.query_transformer import AsyncQueryTransformer
from src.infrastructure.vector_engine import MiniVectorEngine
from src.domain.context_optimizer import ParentResolver, AlternatingRankSorter
from src.domain.rag_engine import async_extract_advanced_rag_context
from tests.test_advanced_rag_architecture import TestAdvancedRAGArchitecture


async def profile_rag_pipeline_stages():
    """Profiles latency breakdown per stage in milliseconds."""
    test_query = "Windows NTFS SQLite database locking and thread teardown protocol"
    
    timings = {}

    # Stage 1: HyDE & Query Transformation
    t0 = time.perf_counter()
    trans_plan = await AsyncQueryTransformer.transform_query_async(test_query)
    timings["HyDE & Query Transformation"] = (time.perf_counter() - t0) * 1000.0

    # Stage 2: Dense Vector Retrieval (MRL 256 + 768)
    t0 = time.perf_counter()
    dense_hits = MiniVectorEngine.search_semantic(test_query, top_k=10)
    timings["Dense Vector Search (MRL)"] = (time.perf_counter() - t0) * 1000.0

    # Stage 3: Sparse FTS5 BM25 Search
    t0 = time.perf_counter()
    from src.infrastructure.database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, filename, content FROM fts_files WHERE fts_files MATCH ? LIMIT 10", ("SQLite",))
    sparse_hits = cursor.fetchall()
    timings["Sparse FTS5 BM25 Search"] = (time.perf_counter() - t0) * 1000.0

    # Stage 4: Cross-Encoder Reranking
    t0 = time.perf_counter()
    from src.domain.situational_cross_reranker import SituationalCrossReranker
    from src.domain.situational_query_analyzer import SituationalQueryAnalyzer
    q_plan = SituationalQueryAnalyzer.analyze_situational_query(test_query)
    cross_hits = SituationalCrossReranker.rerank(test_query, dense_hits[:15], q_plan)
    timings["Cross-Encoder Reranking"] = (time.perf_counter() - t0) * 1000.0

    # Stage 5: Parent Resolution & Deduplication
    t0 = time.perf_counter()
    resolved_parents = ParentResolver.resolve_parents_from_child_hits(cross_hits[:6])
    timings["Parent Resolution & Dedup"] = (time.perf_counter() - t0) * 1000.0

    # Stage 6: Lost-in-the-Middle Sorter
    t0 = time.perf_counter()
    reordered = AlternatingRankSorter.reorder_lost_in_the_middle(resolved_parents)
    timings["Lost-in-the-Middle Sorter"] = (time.perf_counter() - t0) * 1000.0

    total_pipeline_latency = sum(timings.values())
    return timings, total_pipeline_latency, trans_plan


def compute_hyde_similarity_delta():
    """Measures empirical cosine similarity gain from HyDE generation."""
    raw_query = "my screen turns black when running heavy renders"
    target_doc = (
        "Windows Graphics Driver TDR (Timeout Detection and Recovery) resets the GPU "
        "when a rendering shader takes longer than 2 seconds. The display driver unloads, "
        "screen turns black momentarily, and recovers without requiring a full system reboot."
    )
    
    plan = asyncio.run(AsyncQueryTransformer.transform_query_async(raw_query))
    hyde_text = plan["hyde_passage"]

    raw_vec = generate_embedding(raw_query)
    hyde_vec = generate_embedding(hyde_text)
    doc_vec = generate_embedding(target_doc)

    raw_sim = cosine_similarity(raw_vec, doc_vec)
    hyde_sim = cosine_similarity(hyde_vec, doc_vec)
    delta = hyde_sim - raw_sim
    pct_gain = (delta / raw_sim) * 100.0 if raw_sim > 0 else 0.0

    return raw_sim, hyde_sim, delta, pct_gain, hyde_text


def main():
    print("=" * 85)
    print("      UROBOROS KNOWLEDGE ENGINE — ADVANCED RAG ARCHITECTURE VALIDATION HARNESS      ")
    print("=" * 85)
    print("Timestamp:", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("Engine Target: Parent-Child, HyDE, Lost-in-the-Middle, Grounded Guardrails, Async")
    print("-" * 85)

    # 1. Run Unit & Integration Test Suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAdvancedRAGArchitecture)
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.perf_counter()
    result = runner.run(suite)
    test_duration = time.perf_counter() - start_time

    # 2. HyDE Semantic Alignment Delta Measurement
    raw_sim, hyde_sim, delta, pct_gain, hyde_text = compute_hyde_similarity_delta()

    # 3. Latency Profiling per Stage
    timings, total_lat, trans_plan = asyncio.run(profile_rag_pipeline_stages())

    print("\n" + "=" * 85)
    print("                         STAGE-BY-STAGE LATENCY PROFILING                        ")
    print("=" * 85)
    print(f"{'Pipeline Stage':<38} | {'Execution Time (ms)':<22} | {'Budget Status'}")
    print("-" * 85)
    for stage, ms in timings.items():
        status = "OPTIMAL (<50ms)" if ms < 50.0 else "ACCEPTABLE"
        print(f"{stage:<38} | {ms:8.2f} ms             | {status}")
    print("-" * 85)
    print(f"{'TOTAL RETRIEVAL + RERANK LATENCY':<38} | {total_lat:8.2f} ms             | {'PASS (<500ms)' if total_lat < 500.0 else 'FAIL'}")

    print("\n" + "=" * 85)
    print("                       HyDE SEMANTIC ALIGNMENT BENCHMARK                        ")
    print("=" * 85)
    print(f"Colloquial Query : \"my screen turns black when running heavy renders\"")
    print(f"HyDE Passage     : \"{hyde_text[:110]}...\"")
    print(f"Raw Cosine Sim   : {raw_sim:.4f}")
    print(f"HyDE Cosine Sim  : {hyde_sim:.4f}")
    print(f"Similarity Delta : +{delta:.4f} ({pct_gain:+.2f}% semantic alignment gain)")

    print("\n" + "=" * 85)
    print("                           VALIDATION TEST MATRIX SUMMARY                        ")
    print("=" * 85)

    matrix = [
        ("Test 1: Parent-Child Resolution", "Multiple child hits resolve to 1 deduplicated parent", "PASS" if not any(f[0]._testMethodName == "test_1_parent_child_resolution_and_deduplication" for f in result.failures) else "FAIL"),
        ("Test 2: HyDE Alignment Delta", f"Cosine alignment gain (+{delta:.4f} delta)", "PASS" if not any(f[0]._testMethodName == "test_2_hyde_transformation_and_semantic_alignment_delta" for f in result.failures) else "FAIL"),
        ("Test 3: Lost-in-the-Middle Layout", "Alternating [P1, P3, P4, P2] layout verified", "PASS" if not any(f[0]._testMethodName == "test_3_lost_in_the_middle_attention_reordering" for f in result.failures) else "FAIL"),
        ("Test 4: Relevance Guardrail (0.35)", "Out-of-scope query triggers deterministic refusal", "PASS" if not any(f[0]._testMethodName == "test_4_relevance_threshold_and_fallback_guardrail" for f in result.failures) else "FAIL"),
        ("Test 5: Grounded Citations", "Inline [Source: ... | Section: ...] verified", "PASS" if not any(f[0]._testMethodName == "test_5_end_to_end_grounded_generation_and_citation_verification" for f in result.failures) else "FAIL"),
        ("Test 6: Async Latency Benchmark", f"End-to-end execution ({total_lat:.2f}ms < 500ms)", "PASS" if not any(f[0]._testMethodName == "test_6_concurrency_and_latency_benchmark" for f in result.failures) else "FAIL"),
    ]

    print(f"{'Feature Subsystem':<36} | {'Validation Invariant':<36} | {'Status'}")
    print("-" * 85)
    for feat, inv, status in matrix:
        print(f"{feat:<36} | {inv:<36} | {status}")
    print("-" * 85)

    print(f"\nOVERALL RESULT: {'100% PASS (ALL GREEN)' if result.wasSuccessful() else 'FAILED'}")
    print(f"Total Tests Run: {result.testsRun} | Failures: {len(result.failures)} | Errors: {len(result.errors)} | Duration: {test_duration:.3f}s")
    print("=" * 85)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
