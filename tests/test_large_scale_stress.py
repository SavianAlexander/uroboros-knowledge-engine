"""
Unit and Integration Test Suite for 100,000+ Chunk Massive-Scale Stress Test.
Standard: Pure Python standard library with unittest/pytest assertions.
"""

import os
import sys
import unittest

# Ensure root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.benchmark_large_scale_stress import (
    generate_synthetic_chunk,
    run_large_scale_stress_test,
    benchmark_hardware_popcnt_colbert_maxsim
)


class TestLargeScaleStress(unittest.TestCase):
    """Test suite verifying massive-scale chunk ingestion and vector stress testing."""

    def test_generate_synthetic_chunk(self):
        chunk = generate_synthetic_chunk(42)
        self.assertEqual(chunk["chunk_id"], 42)
        self.assertIn("text", chunk)
        self.assertIn("filename", chunk)
        self.assertGreater(len(chunk["text"]), 10)

    def test_benchmark_hardware_popcnt_colbert_maxsim(self):
        res = benchmark_hardware_popcnt_colbert_maxsim(candidates_count=1000)
        self.assertEqual(res["benchmark"], "popcnt_binary_colbert_maxsim_100k")
        self.assertEqual(res["candidates_evaluated"], 1000)
        self.assertGreater(res["comparisons_per_second"], 0)
        self.assertGreater(res["candidate_matrix_qps"], 0)

    def test_run_large_scale_stress_test_sample(self):
        # Run test with 5,000 chunks for quick unit test execution
        scorecard = run_large_scale_stress_test(chunks=5000, threads=4)
        self.assertEqual(scorecard["status"], "PASS")
        self.assertEqual(scorecard["total_chunks_stress_tested"], 5000)
        self.assertIn("bulk_ingestion", scorecard)
        self.assertIn("concurrent_fts5_bm25", scorecard)
        self.assertIn("popcnt_colbert_maxsim", scorecard)


if __name__ == "__main__":
    unittest.main()
