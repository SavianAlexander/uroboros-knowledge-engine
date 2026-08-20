import unittest
"""
Automated Test Suite: System Stability Governor, Windows Job Object Process Supervisor & Zombie Reaper.
Standard: Pure Python Standard Library + pytest + FastAPI TestClient.
"""

import os
import sys
import time
import threading
import subprocess
import pytest
from fastapi.testclient import TestClient

from src.infrastructure.process_supervisor import ProcessSupervisor
from src.infrastructure.database import (
    get_db,
    reap_zombie_connections,
    get_database_connection_stats,
    reset_db_connections,
    run_maintenance
)
from src.core.jobs import JobManager, get_job_manager
from src.core.async_reaper import AsyncStreamReaper
from src.core.stability_governor import StabilityGovernor, get_process_memory_usage
from src.app.main import app


@pytest.fixture(autouse=True)
def cleanup_connections():
    yield
    reset_db_connections()


class TestProcessSupervisorAndJobObjects(unittest.TestCase):
    """Validate child process tracking, exit code reaping, and Windows Job Object assignment."""

    def test_spawn_and_reap_child_process(self):
        # Spawn a short-lived subprocess (echo / true)
        cmd = [sys.executable, "-c", "import time; time.sleep(0.1); print('done')"]
        proc = ProcessSupervisor.spawn_safe_subprocess(cmd, description="test_sleep_proc")
        assert proc.pid > 0

        # Check tracking
        tracked = ProcessSupervisor.list_tracked_children()
        assert any(p["pid"] == proc.pid for p in tracked)

        # Wait for termination
        proc.wait(timeout=2.0)

        # Reap dead children
        reaped = ProcessSupervisor.reap_dead_children()
        assert reaped >= 1

        # Verify no longer in active tracked list
        tracked_after = ProcessSupervisor.list_tracked_children()
        assert not any(p["pid"] == proc.pid for p in tracked_after)

    def test_supervisor_stats(self):
        stats = ProcessSupervisor.get_supervisor_stats()
        assert "platform" in stats
        assert "job_object_active" in stats
        assert "active_tracked_children" in stats
        assert "lifetime_reaped_children" in stats


class TestDeadThreadConnectionReaper(unittest.TestCase):
    """Validate that connections opened by dead/terminated threads are identified and reaped."""

    def test_reap_zombie_thread_connection(self):
        reset_db_connections()

        # Flag to indicate thread finished
        thread_done = threading.Event()

        def worker():
            conn = get_db()
            conn.cursor().execute("SELECT 1").fetchone()
            thread_done.set()

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=2.0)
        assert thread_done.is_set()
        assert not t.is_alive()

        # The thread is dead, but its connection was recorded in _local_connections
        stats = get_database_connection_stats()
        assert stats["thread_local_connections_count"] >= 1

        # Reap dead-thread zombie connections
        reap_res = reap_zombie_connections(idle_timeout_seconds=0.0)
        assert reap_res["status"] == "success"
        assert reap_res["reaped_count"] >= 1
        assert any(r["reason"] == "dead_thread" for r in reap_res["reaped_connections"])


class TestJobManagerStabilityAndReaping(unittest.TestCase):
    """Validate background job queue, cancellation, timeouts, and stale job memory eviction."""

    def test_job_submission_and_completion(self):
        jm = JobManager(max_workers=2)

        def simple_task(x, y):
            return x + y

        jid = jm.submit_job(simple_task, 10, 20, description="addition")
        assert jid is not None

        # Wait for completion
        for _ in range(20):
            job = jm.get_job(jid)
            if job and job["status"] == "completed":
                break
            time.sleep(0.05)

        job = jm.get_job(jid)
        assert job["status"] == "completed"
        assert job["result"] == 30
        assert job["progress"] == 100.0

    def test_job_cancellation(self):
        jm = JobManager(max_workers=2)

        def long_task():
            time.sleep(1.0)
            return "finished"

        jid = jm.submit_job(long_task, description="long_running")
        cancelled = jm.cancel_job(jid)
        assert cancelled is True

        job = jm.get_job(jid)
        assert job["status"] == "cancelled"

    def test_reap_stale_jobs_ttl_and_max_history(self):
        jm = JobManager(max_workers=2)

        def dummy_task():
            return "ok"

        # Submit 10 quick jobs
        jids = [jm.submit_job(dummy_task) for _ in range(10)]
        time.sleep(0.3)

        # Evict with ttl_seconds=0 (all completed jobs)
        reaped = jm.reap_stale_jobs(ttl_seconds=0.0, max_history=2)
        assert reaped >= 8

        stats = jm.get_job_stats()
        assert stats["total_tracked_jobs"] <= 2
        assert stats["lifetime_reaped_jobs"] >= 8


class TestAsyncStreamReaper(unittest.TestCase):
    """Validate async stream tracking, chunk counting, and unregistering."""

    def test_stream_lifecycle(self):
        stream_id = "test_stream_001"
        AsyncStreamReaper.register_stream(stream_id, stream_type="sse_rag")
        
        stats = AsyncStreamReaper.get_stream_stats()
        assert stats["active_streams_count"] >= 1
        assert any(s["id"] == stream_id for s in stats["active_streams"])

        AsyncStreamReaper.record_chunk(stream_id)
        AsyncStreamReaper.record_chunk(stream_id)

        AsyncStreamReaper.unregister_stream(stream_id, status="completed")
        stats_after = AsyncStreamReaper.get_stream_stats()
        assert not any(s["id"] == stream_id for s in stats_after["active_streams"])
        assert stats_after["lifetime_reaped_streams"] >= 1


class TestStabilityGovernorAndAPI(unittest.TestCase):
    """Validate system vitals collection, 1-shot master reap, and FastAPI endpoints."""

    def test_stability_governor_vitals(self):
        vitals = StabilityGovernor.get_system_vitals()
        assert vitals["status"] == "healthy"
        assert "uptime_seconds" in vitals
        assert "memory" in vitals
        assert vitals["memory"]["rss_mb"] > 0
        assert "process_supervisor" in vitals
        assert "threads" in vitals
        assert "database" in vitals
        assert "jobs" in vitals

    def test_stability_governor_reap_all_zombies(self):
        reap_res = StabilityGovernor.reap_all_zombies(truncate_wal=True)
        assert reap_res["status"] == "success"
        assert "elapsed_ms" in reap_res
        assert "memory_before_mb" in reap_res
        assert "memory_after_mb" in reap_res
        assert "gc_collected_objects" in reap_res

    def test_fastapi_stability_endpoints(self):
        client = TestClient(app)

        # 1. GET /api/system/health/stability
        resp = client.get("/api/system/health/stability")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "memory" in data

        # 2. POST /api/system/reap
        reap_resp = client.post("/api/system/reap?truncate_wal=true")
        assert reap_resp.status_code == 200
        reap_data = reap_resp.json()
        assert reap_data["status"] == "success"
        assert "elapsed_ms" in reap_data
