"""
Unit and Integration Test Suite for Live Local LLM & Real-Time Latency Benchmark.
Standard: Pure Python standard library with pytest assertions.
"""

import os
import sys
import unittest
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.benchmark_llm_inference import (
    probe_ollama_endpoint,
    benchmark_model_router_accuracy,
    benchmark_streaming_inference,
    benchmark_embedding_latency,
    run_full_llm_benchmark
)


class TestLlmInferenceBenchmark(unittest.TestCase):
    """Test suite verifying LLM inference benchmarking components."""

    def test_probe_ollama_endpoint(self):
        res = probe_ollama_endpoint()
        self.assertIn("status", res)
        self.assertIn(res["status"], ["ONLINE", "OFFLINE_FALLBACK"])
        self.assertIn("host", res)
        self.assertIsInstance(res.get("latency_ms"), (int, float))

    def test_benchmark_model_router_accuracy(self):
        res = benchmark_model_router_accuracy()
        self.assertEqual(res["benchmark"], "model_router_5_tier_accuracy")
        self.assertEqual(res["total_test_cases"], 5)
        self.assertEqual(res["passed_cases"], 5)
        self.assertEqual(res["accuracy_pct"], 100.0)
        self.assertGreater(len(res["results"]), 0)

    def test_benchmark_streaming_inference(self):
        res = benchmark_streaming_inference(
            prompt="Briefly describe SQLite WAL mode.",
            model_name="qwen2.5:7b"
        )
        self.assertEqual(res["benchmark"], "streaming_llm_inference")
        self.assertGreater(res["ttft_ms"], 0)
        self.assertGreater(res["generated_tokens"], 0)
        self.assertGreater(res["tokens_per_second"], 0)
        self.assertTrue(len(res["sample_output"]) > 0)

    def test_benchmark_embedding_latency(self):
        res = benchmark_embedding_latency(iterations=10)
        self.assertEqual(res["benchmark"], "embedding_inference_nomic")
        self.assertEqual(res["dimensions"], 768)
        self.assertGreater(res["embeddings_per_sec"], 0)
        self.assertGreater(res["avg_latency_ms"], 0)

    def test_run_full_llm_benchmark(self):
        scorecard = run_full_llm_benchmark()
        self.assertEqual(scorecard["status"], "PASS")
        self.assertIn("timestamp", scorecard)
        self.assertIn("router_benchmark", scorecard)
        self.assertIn("streaming_benchmark", scorecard)
        self.assertIn("embedding_benchmark", scorecard)


if __name__ == "__main__":
    unittest.main()
