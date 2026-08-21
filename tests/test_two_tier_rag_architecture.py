"""
Integration Test Suite for Asynchronous Two-Tier RAG Architecture:
1. Front-Office Fast Interactive Runtime (<1.5s latency).
2. Front-Office Asynchronous Job Dispatch.
3. Back-Office Persistent Job Queue & Priority Scheduling.
4. Colibrì 744B MoE Client Adapter & Fallback Synthesis.
5. Contextual Chunk Prepending (Anthropic Contextual Retrieval).
6. GraphRAG Hierarchical Community Summarization.
7. DSPy MIPROv2 Synthetic QA & Evaluation Generator.
8. Cooperative Zero-Stutter Worker Daemon Lifecycle.
9. FastAPI Back-Office REST Endpoints.
"""

import os
import sys
import time
import json
import uuid
import tempfile
import unittest
from typing import Dict, Any

from fastapi.testclient import TestClient

from src.infrastructure.database import reset_db_connections, get_db_connection
from src.domain.back_office.job_queue import BackOfficeJobQueue, JobStatus, JobType
from src.domain.back_office.colibri_client import ColibriClient
from src.domain.back_office.tasks import (
    ContextualChunkPrependExecutor,
    GraphRAGCommunitySummarizer,
    MIPROEvalSynthesizer,
    MultiDocAuditExecutor
)
from src.domain.back_office.worker_daemon import CooperativeWorkerDaemon, set_idle_thread_priority
from src.domain.front_office.interactive_runtime import FrontOfficeRuntime
from src.app.server import app


class TestTwoTierRAGArchitecture(unittest.TestCase):
    """Exhaustive test suite for Front-Office / Back-Office Two-Tier RAG Architecture."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="test_twotier_")
        cls.db_path = os.path.join(cls.temp_dir, "test_twotier.db")
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        reset_db_connections()
        import shutil
        if os.path.exists(cls.temp_dir):
            try:
                shutil.rmtree(cls.temp_dir)
            except Exception:
                pass

    def setUp(self):
        reset_db_connections()
        self.db_path = os.path.join(self.temp_dir, f"test_{uuid.uuid4().hex[:8]}.db")
        self.queue = BackOfficeJobQueue(db_path=self.db_path)
        self.colibri_client = ColibriClient()

    def tearDown(self):
        reset_db_connections()

    def test_01_front_office_fast_chat_latency(self):
        """Test 1: Verify Front-Office provides fast answers with latency metadata."""
        runtime = FrontOfficeRuntime(job_queue=self.queue)
        resp = runtime.fast_chat(
            query="What are the main performance requirements of the Uroboros Engine?",
            max_tokens=100
        )
        self.assertIsNotNone(resp.answer)
        self.assertTrue(len(resp.answer) > 0)
        self.assertIsInstance(resp.latency_ms, float)
        self.assertTrue(resp.latency_ms > 0.0)  # Verify latency is recorded
        self.assertIsNone(resp.deep_job_id)

    def test_02_front_office_deep_job_dispatch(self):
        """Test 2: Verify Front-Office can non-blockingly dispatch deep jobs to Back-Office queue."""
        runtime = FrontOfficeRuntime(job_queue=self.queue)
        resp = runtime.fast_chat(
            query="Perform a deep GraphRAG audit of the entire database",
            trigger_deep_job=True,
            deep_job_type=JobType.GRAPHRAG_COMMUNITY_SUMMARY
        )
        self.assertIsNotNone(resp.deep_job_id)
        self.assertTrue(resp.deep_job_id.startswith("job_"))

        # Verify job is in PENDING state in queue
        job = self.queue.get_job(resp.deep_job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.job_type, JobType.GRAPHRAG_COMMUNITY_SUMMARY.value)

    def test_03_job_queue_priority_and_state_transitions(self):
        """Test 3: Verify priority queue scheduling (P1 before P2) and status transitions."""
        job_low = self.queue.enqueue(
            job_type=JobType.CUSTOM_BATCH_INFERENCE,
            payload={"task": "low_priority"},
            priority=3
        )
        job_high = self.queue.enqueue(
            job_type=JobType.CUSTOM_BATCH_INFERENCE,
            payload={"task": "high_priority"},
            priority=1
        )
        job_norm = self.queue.enqueue(
            job_type=JobType.CUSTOM_BATCH_INFERENCE,
            payload={"task": "normal_priority"},
            priority=2
        )

        # Dequeue 1 -> should be high priority
        d1 = self.queue.dequeue()
        self.assertIsNotNone(d1)
        self.assertEqual(d1.job_id, job_high)
        self.assertEqual(d1.status, JobStatus.PROCESSING)

        # Complete high priority job
        self.queue.complete_job(job_high, {"status": "success", "processed_by": "colibri_744b"})
        j_high_record = self.queue.get_job(job_high)
        self.assertEqual(j_high_record.status, JobStatus.COMPLETED)
        self.assertEqual(j_high_record.result.get("processed_by"), "colibri_744b")

        # Dequeue 2 -> should be normal priority
        d2 = self.queue.dequeue()
        self.assertIsNotNone(d2)
        self.assertEqual(d2.job_id, job_norm)

        # Cancel low priority job
        self.queue.cancel_job(job_low)
        j_low_record = self.queue.get_job(job_low)
        self.assertEqual(j_low_record.status, JobStatus.CANCELLED)

    def test_04_colibri_client_generation_and_fallback(self):
        """Test 4: Verify ColibriClient generation and resilient fallback output."""
        client = ColibriClient(endpoint_url="http://127.0.0.1:8080/v1")
        # Should gracefully synthesize response even if Colibrì local daemon is not running
        res = client.generate(
            prompt="Analyze technical architecture for Contextual Retrieval chunk prepending",
            max_tokens=150
        )
        self.assertIsNotNone(res)
        self.assertTrue(len(res) > 10)
        self.assertIn("Context:", res)

    def test_05_contextual_chunk_prepending_task(self):
        """Test 5: Verify ContextualChunkPrependExecutor situates chunks in document context."""
        payload = {
            "doc_title": "Storage Engine Architecture Specification",
            "doc_full_text": "# Storage Engine\nThis specification details WAL checkpointing, page caches, and concurrency locks on Windows.",
            "chunk_content": "WAL autocheckpoint triggers flush when 1000 pages accumulate in the write-ahead log."
        }
        res = ContextualChunkPrependExecutor.execute(payload, client=self.colibri_client)
        self.assertIn("enriched_chunk", res)
        self.assertIn("context_prefix", res)
        self.assertTrue(res["enriched_length"] > res["original_length"])
        self.assertIn("WAL autocheckpoint", res["enriched_chunk"])

    def test_06_graphrag_community_summarization_task(self):
        """Test 6: Verify GraphRAGCommunitySummarizer extracts structured community summary."""
        payload = {
            "community_id": "comm_database_subsystem",
            "entities": ["SQLiteConnectionPool", "WALDaemon", "DenseVectorStore", "FTS5Index"],
            "relationships": [
                {"source": "SQLiteConnectionPool", "target": "WALDaemon", "relation": "flushes_wal"},
                {"source": "DenseVectorStore", "target": "SQLiteConnectionPool", "relation": "persists_embeddings"}
            ]
        }
        res = GraphRAGCommunitySummarizer.execute(payload, client=self.colibri_client)
        self.assertEqual(res["community_id"], "comm_database_subsystem")
        self.assertEqual(res["entity_count"], 4)
        self.assertIn("community_summary", res)
        self.assertTrue(len(res["community_summary"]) > 20)

    def test_07_mipro_eval_synthesizer_task(self):
        """Test 7: Verify MIPROEvalSynthesizer generates synthetic evaluation dataset."""
        payload = {
            "domain_name": "Distributed Storage & Concurrency",
            "sample_texts": [
                "SQLite WAL mode enables concurrent readers while maintaining strict single-writer transactional safety.",
                "Busy timeouts prevent database locking exceptions under multi-threaded load."
            ],
            "num_samples": 2
        }
        res = MIPROEvalSynthesizer.execute(payload, client=self.colibri_client)
        self.assertEqual(res["domain_name"], "Distributed Storage & Concurrency")
        self.assertIn("eval_output", res)
        self.assertTrue(len(res["eval_output"]) > 20)

    def test_08_cooperative_worker_daemon_zero_stutter(self):
        """Test 8: Verify CooperativeWorkerDaemon executes jobs with zero-stutter controls."""
        # Enqueue a test job
        job_id = self.queue.enqueue(
            job_type=JobType.CONTEXTUAL_CHUNK_PREPEND,
            payload={
                "doc_title": "Daemon Test",
                "doc_full_text": "Sample document for daemon verification.",
                "chunk_content": "Daemon chunk body."
            }
        )

        daemon = CooperativeWorkerDaemon(
            queue=self.queue,
            colibri_client=self.colibri_client,
            boot_grace_period_sec=0.1,  # Short boot grace for test
            cooling_interval_sec=0.1,
            poll_interval_sec=0.1
        )

        # Verify thread priority helper
        prio_ok = set_idle_thread_priority()
        self.assertIsInstance(prio_ok, bool)

        # Execute single step synchronously via run_once
        processed_job = daemon.run_once()
        self.assertIsNotNone(processed_job)
        self.assertEqual(processed_job.job_id, job_id)
        self.assertEqual(processed_job.status, JobStatus.COMPLETED)
        self.assertIn("enriched_chunk", processed_job.result)

        # Verify stats
        stats = self.queue.get_queue_stats()
        self.assertEqual(stats.get("COMPLETED", 0), 1)

    def test_09_fastapi_back_office_endpoints(self):
        """Test 9: Verify FastAPI /api/backoffice REST endpoints for job lifecycle."""
        enqueue_res = self.client.post("/api/backoffice/jobs", json={
            "job_type": "MULTI_DOC_AUDIT",
            "payload": {
                "doc_a_name": "API Spec v1",
                "doc_a_text": "GET /api/v1/search requires query parameter.",
                "doc_b_name": "API Spec v2",
                "doc_b_text": "GET /api/v2/search supports query and filter parameters."
            },
            "priority": 1
        })
        self.assertEqual(enqueue_res.status_code, 200)
        data = enqueue_res.json()
        self.assertEqual(data["status"], "enqueued")
        job_id = data["job_id"]

        # Poll job status
        get_res = self.client.get(f"/api/backoffice/jobs/{job_id}")
        self.assertEqual(get_res.status_code, 200)
        job_data = get_res.json()
        self.assertEqual(job_data["job_id"], job_id)
        self.assertEqual(job_data["status"], "PENDING")

        # List jobs
        list_res = self.client.get("/api/backoffice/jobs?status=PENDING")
        self.assertEqual(list_res.status_code, 200)
        self.assertTrue(any(j["job_id"] == job_id for j in list_res.json()))

        # Get stats
        stats_res = self.client.get("/api/backoffice/stats")
        self.assertEqual(stats_res.status_code, 200)
        self.assertIn("PENDING", stats_res.json())

        # Cancel job
        cancel_res = self.client.post(f"/api/backoffice/jobs/{job_id}/cancel")
        self.assertEqual(cancel_res.status_code, 200)
        self.assertEqual(cancel_res.json()["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()
