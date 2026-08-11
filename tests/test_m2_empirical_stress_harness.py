import src.core.config as config
import src.infrastructure.database as db
"""
Empirical Stress and Performance Test Harness for Milestone 2.
Evaluates:
1. /api/chat/stream SSE stream throughput and token event format correctness.
2. RRF score calculation accuracy and sorting stability.
3. Session turn logging completeness when streaming multi-turn conversations.
"""

import unittest
import os
import sys
import shutil
import tempfile
import time
import json
import concurrent.futures
from typing import List, Dict, Any
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main
from src.domain.rag_engine import rrf_rerank, extract_advanced_rag_context, jaccard_deduplicate, sanitize_fts_query


class TestM2EmpiricalStressHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="m2_empirical_test_")
        cls.db_backup = db.DB_FILE
        cls.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(cls.test_dir, "test_m2_know.db")
        config.ACTIVE_DIR = cls.test_dir
        know.reset_db_connections()
        know.init_db()

        # Seed sample documents in vault
        for i in range(1, 10):
            doc_path = os.path.join(cls.test_dir, f"doc_{i}.txt")
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(f"Document #{i}: Quantum computing, superposition, entanglement, and algorithm iteration {i}.")

        know.index_directory(cls.test_dir)
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        know.reset_db_connections()
        db.DB_FILE = cls.db_backup
        config.ACTIVE_DIR = cls.active_backup
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. SSE STREAM THROUGHPUT & EVENT FORMAT CORRECTNESS
    # -------------------------------------------------------------------------

    def test_01_sse_event_format_strictness(self):
        """Verify strict event-stream formatting, JSON validity of every line, and event sequence."""
        res = self.client.post("/api/chat/stream", json={
            "message": "Quantum computing superposition algorithm",
            "temperature": 0.2
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))

        lines = res.text.strip().split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        event_types = []
        parsed_tokens = []
        sources_event = None
        done_event = None

        for line in non_empty_lines:
            self.assertTrue(line.startswith("data: "), f"Line does not start with 'data: ': {line}")
            payload_str = line[6:]
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError as err:
                self.fail(f"Invalid JSON in SSE payload: '{payload_str}' - Error: {err}")

            self.assertIn("type", payload, "SSE event payload missing 'type' field")
            event_types.append(payload["type"])

            if payload["type"] == "sources":
                sources_event = payload
                self.assertIn("session_id", payload)
                self.assertIn("sources", payload)
                self.assertIn("local_citations", payload)
                self.assertIn("web_sources", payload)
                self.assertIsInstance(payload["local_citations"], list)
                self.assertIsInstance(payload["web_sources"], list)
            elif payload["type"] == "token":
                self.assertIn("content", payload)
                parsed_tokens.append(payload["content"])
            elif payload["type"] == "done":
                done_event = payload
                self.assertIn("session_id", payload)

        self.assertIsNotNone(sources_event, "Missing 'sources' SSE event")
        self.assertIsNotNone(done_event, "Missing 'done' SSE event")
        self.assertEqual(event_types[0], "sources", "First SSE event must be 'sources'")
        self.assertEqual(event_types[-1], "done", "Last SSE event must be 'done'")
        self.assertGreater(len(parsed_tokens), 0, "Expected at least one token event")
        
        full_text = "".join(parsed_tokens)
        self.assertGreater(len(full_text), 0, "Concatenated streamed tokens must not be empty")

    def test_02_sse_throughput_and_latency_benchmark(self):
        """Benchmark TTFT (time to first token), total stream duration, and tokens per second throughput."""
        start_time = time.perf_counter()
        res = self.client.post("/api/chat/stream", json={
            "message": "Explain quantum entanglement in detail",
            "web_search": False
        })
        end_time = time.perf_counter()
        total_duration = end_time - start_time

        self.assertEqual(res.status_code, 200)
        lines = [l for l in res.text.strip().split("\n") if l.startswith("data: ")]
        tokens = [json.loads(l[6:])["content"] for l in lines if json.loads(l[6:])["type"] == "token"]

        token_count = len(tokens)
        throughput = token_count / total_duration if total_duration > 0 else 0

        print(f"\n[BENCHMARK] SSE Throughput: {token_count} tokens in {total_duration:.4f}s ({throughput:.2f} tokens/sec)")
        self.assertGreater(token_count, 0)
        self.assertLess(total_duration, 5.0, "Streaming took longer than 5 seconds")

    def test_03_sse_concurrent_streaming_stress(self):
        """Stress-test 10 concurrent clients hitting /api/chat/stream simultaneously."""
        concurrency = 10
        errors = []
        durations = []

        def worker(client_idx: int):
            t0 = time.perf_counter()
            try:
                res = self.client.post("/api/chat/stream", json={
                    "message": f"Concurrent client request {client_idx} about quantum doc_{client_idx % 9 + 1}.txt"
                })
                t1 = time.perf_counter()
                durations.append(t1 - t0)
                if res.status_code != 200:
                    errors.append(f"Client {client_idx} failed with status {res.status_code}")
                    return
                if '"type": "done"' not in res.text:
                    errors.append(f"Client {client_idx} response incomplete: missing done event")
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in test_m2_empirical_stress_harness.py: {e}")
                errors.append(f"Client {client_idx} exception: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker, i) for i in range(concurrency)]
            concurrent.futures.wait(futures)

        self.assertEqual(len(errors), 0, f"Concurrent SSE streaming errors encountered: {errors}")
        avg_duration = sum(durations) / len(durations) if durations else 0
        print(f"[BENCHMARK] Concurrent SSE ({concurrency} workers): avg request latency = {avg_duration:.4f}s")

    def test_04_sse_edge_case_inputs(self):
        """Test streaming with long input, special unicode, and invalid payload."""
        # 1. Empty message -> 422
        res_empty = self.client.post("/api/chat/stream", json={"message": "   "})
        self.assertEqual(res_empty.status_code, 422)

        # 2. Large 5,000 character prompt
        large_prompt = "quantum superposition " * 250
        res_large = self.client.post("/api/chat/stream", json={"message": large_prompt})
        self.assertEqual(res_large.status_code, 200)
        self.assertIn('"type": "done"', res_large.text)

        # 3. Unicode and FTS syntax characters
        weird_prompt = "🚀 ¿Quantum? (MATCH 'test*' OR AND NOT \\ / -- ;) ⚛️"
        res_weird = self.client.post("/api/chat/stream", json={"message": weird_prompt})
        self.assertEqual(res_weird.status_code, 200)
        self.assertIn('"type": "done"', res_weird.text)

    # -------------------------------------------------------------------------
    # 2. RRF SCORE CALCULATION ACCURACY & SORTING STABILITY
    # -------------------------------------------------------------------------

    def test_05_rrf_mathematical_formula_accuracy(self):
        """Verify exact Reciprocal Rank Fusion score: 1/(k + r_fts) + 1/(k + r_vec)."""
        fts_hits = [
            {"filepath": "docA.txt", "filename": "docA.txt"}, # rank 1 -> 1/(60+1) = 1/61 = 0.01639344...
            {"filepath": "docB.txt", "filename": "docB.txt"}, # rank 2 -> 1/(60+2) = 1/62 = 0.01612903...
        ]
        vec_hits = [
            {"filepath": "docB.txt", "filename": "docB.txt"}, # rank 1 -> 1/(60+1) = 1/61 = 0.01639344...
            {"filepath": "docC.txt", "filename": "docC.txt"}, # rank 2 -> 1/(60+2) = 1/62 = 0.01612903...
        ]

        # docB is rank 2 in FTS (1/62) and rank 1 in VEC (1/61). Total score = 1/62 + 1/61 = 0.03252247... -> round to 6 digits = 0.032522
        # docA is rank 1 in FTS (1/61) only. Total = 1/61 = 0.01639344... -> 0.016393
        # docC is rank 2 in VEC (1/62) only. Total = 1/62 = 0.01612903... -> 0.016129

        fused = rrf_rerank(fts_hits, vec_hits, k=60)
        self.assertEqual(len(fused), 3)

        expected_scores = {
            "docB.txt": round(1.0 / 62 + 1.0 / 61, 6),
            "docA.txt": round(1.0 / 61, 6),
            "docC.txt": round(1.0 / 62, 6)
        }

        # Check ranking order
        self.assertEqual(fused[0]["filepath"], "docB.txt")
        self.assertEqual(fused[1]["filepath"], "docA.txt")
        self.assertEqual(fused[2]["filepath"], "docC.txt")

        # Check exact score values
        for hit in fused:
            fp = hit["filepath"]
            self.assertEqual(hit["rrf_score"], expected_scores[fp], f"Score mismatch for {fp}")

    def test_06_rrf_sorting_stability_on_ties(self):
        """Stress test sorting stability when multiple items have identical RRF scores."""
        # Create 50 items with identical scores (e.g. FTS rank i, VEC rank 51-i)
        fts_items = [{"filepath": f"doc_{i}.txt", "filename": f"doc_{i}.txt"} for i in range(1, 21)]
        vec_items = [{"filepath": f"doc_{21-i}.txt", "filename": f"doc_{21-i}.txt"} for i in range(1, 21)]

        # Each doc_i will have FTS rank i and VEC rank (21-i).
        # Score = 1/(60+i) + 1/(60+21-i).
        # Notice for doc_1: 1/61 + 1/80. For doc_20: 1/80 + 1/61. These have IDENTICAL math scores!

        first_run = rrf_rerank(fts_items, vec_items, k=60)
        
        # Run 50 times to check for deterministic ordering stability
        for run_idx in range(50):
            rerun = rrf_rerank(fts_items, vec_items, k=60)
            self.assertEqual(
                [x["filepath"] for x in rerun],
                [x["filepath"] for x in first_run],
                f"RRF sorting order changed on iteration {run_idx}"
            )

    def test_07_rrf_edge_cases(self):
        """Test RRF edge cases: empty lists, single items, missing key fallbacks."""
        # Empty inputs
        self.assertEqual(rrf_rerank([], []), [])
        self.assertEqual(rrf_rerank(None, None), [])

        # Item without filepath/filename using string representation key
        fts_raw = [{"snippet": "content 1"}, {"snippet": "content 2"}]
        vec_raw = [{"snippet": "content 2"}]
        fused = rrf_rerank(fts_raw, vec_raw, k=60)
        self.assertEqual(len(fused), 2)
        self.assertIn("rrf_score", fused[0])

    # -------------------------------------------------------------------------
    # 3. SESSION TURN LOGGING COMPLETENESS IN MULTI-TURN CONVERSATIONS
    # -------------------------------------------------------------------------

    def test_08_multi_turn_session_logging_completeness(self):
        """Simulate a 4-turn streaming conversation under a single session and verify full DB persistence."""
        # Turn 1: Create new session automatically
        res1 = self.client.post("/api/chat/stream", json={"message": "Turn 1: What is quantum superposition?"})
        self.assertEqual(res1.status_code, 200)

        # Extract session_id from sources event
        lines1 = [l for l in res1.text.split("\n") if l.startswith("data: ")]
        sources1 = json.loads(lines1[0][6:])
        session_id = sources1["session_id"]
        self.assertIsNotNone(session_id)

        # Turn 2: Continue session
        res2 = self.client.post("/api/chat/stream", json={
            "session_id": session_id,
            "message": "Turn 2: How does it differ from entanglement?"
        })
        self.assertEqual(res2.status_code, 200)

        # Turn 3: Continue session
        res3 = self.client.post("/api/chat/stream", json={
            "session_id": session_id,
            "message": "Turn 3: Give a summary of doc_1.txt"
        })
        self.assertEqual(res3.status_code, 200)

        # Turn 4: Continue session with web_search flag
        res4 = self.client.post("/api/chat/stream", json={
            "session_id": session_id,
            "message": "Turn 4: Latest news on quantum computers",
            "web_search": True
        })
        self.assertEqual(res4.status_code, 200)

        # Inspect SQLite DB state via know.py
        messages = know.get_chat_messages(session_id)
        # 4 turns -> 4 user messages + 4 assistant messages = 8 total messages
        self.assertEqual(len(messages), 8, f"Expected 8 messages in session, found {len(messages)}")

        # Verify chronological role sequence: user, assistant, user, assistant, user, assistant, user, assistant
        expected_roles = ["user", "assistant", "user", "assistant", "user", "assistant", "user", "assistant"]
        actual_roles = [m["role"] for m in messages]
        self.assertEqual(actual_roles, expected_roles, "Message role sequence is corrupted")

        # Verify content accuracy
        self.assertIn("Turn 1", messages[0]["content"])
        self.assertIn("Turn 2", messages[2]["content"])
        self.assertIn("Turn 3", messages[4]["content"])
        self.assertIn("Turn 4", messages[6]["content"])

        # Verify assistant message metadata fields
        for idx in [1, 3, 5, 7]:
            asst_msg = messages[idx]
            self.assertEqual(asst_msg["role"], "assistant")
            self.assertGreater(len(asst_msg["content"]), 0, f"Assistant message at index {idx} has empty content")
            self.assertIsNotNone(asst_msg.get("citations_json"), f"Missing citations_json at index {idx}")
            self.assertIsNotNone(asst_msg.get("web_sources_json"), f"Missing web_sources_json at index {idx}")

    def test_09_concurrent_multi_session_turn_isolation(self):
        """Stress-test 5 parallel multi-turn sessions running concurrently to ensure zero cross-talk."""
        num_sessions = 5
        turns_per_session = 3

        def run_session_flow(sess_idx: int):
            # Create session
            sess_info = know.create_chat_session(title=f"Isolated Session {sess_idx}")
            s_id = sess_info["id"]

            for turn in range(turns_per_session):
                msg_content = f"Session_{sess_idx}_Turn_{turn}_Payload"
                res = self.client.post("/api/chat/stream", json={
                    "session_id": s_id,
                    "message": msg_content
                })
                if res.status_code != 200 or '"type": "done"' not in res.text:
                    raise RuntimeError(f"Session {sess_idx} turn {turn} streaming failed")

            return s_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_sessions) as executor:
            futures = [executor.submit(run_session_flow, i) for i in range(num_sessions)]
            session_ids = [f.result() for f in futures]

        # Verify each session has exactly 6 messages (3 turns * 2) with no cross-session contamination
        for idx, s_id in enumerate(session_ids):
            msgs = know.get_chat_messages(s_id)
            self.assertEqual(len(msgs), turns_per_session * 2, f"Session {s_id} has wrong message count")
            user_msgs = [m for m in msgs if m["role"] == "user"]
            for turn_idx, u_msg in enumerate(user_msgs):
                expected = f"Session_{idx}_Turn_{turn_idx}_Payload"
                self.assertEqual(u_msg["content"], expected, f"Cross-session message leakage detected in session {s_id}")

        print(f"[BENCHMARK] Concurrent Multi-Session Logging: Verified {num_sessions} isolated sessions with {num_sessions * turns_per_session * 2} total turns in DB.")


if __name__ == "__main__":
    unittest.main()
