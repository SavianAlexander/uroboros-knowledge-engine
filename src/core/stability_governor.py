"""
Global System Stability Governor & Master Zombie Reaper.
Standard: Pure Python Standard Library (os, sys, gc, time, ctypes, threading).
Ponytail Senior Dev Principle: One unified interface for system diagnostics,
memory telemetry, process supervision, thread liveness, and atomic zombie reclamation.
"""

import os
import gc
import sys
import time
import ctypes
import logging
import threading
from typing import Dict, Any, List, Optional

from src.infrastructure.process_supervisor import ProcessSupervisor
from src.domain.thread_watchdog import list_active_workers, shutdown_all_workers
from src.core.jobs import get_job_manager
from src.core.async_reaper import AsyncStreamReaper

logger = logging.getLogger(__name__)

# Track server boot timestamp
_SERVER_BOOT_TIME = time.time()


def get_process_memory_usage() -> Dict[str, Any]:
    """Retrieves current process working set (RSS) and peak memory in MB without third-party deps."""
    pid = os.getpid()
    rss_mb = 0.0
    peak_mb = 0.0

    if sys.platform == "win32":
        try:
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            psapi = ctypes.windll.psapi
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
                rss_mb = round(pmc.WorkingSetSize / (1024 * 1024), 2)
                peak_mb = round(pmc.PeakWorkingSetSize / (1024 * 1024), 2)
        except Exception:
            pass

    else:
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            rss_mb = round(usage.ru_maxrss / 1024, 2)
            peak_mb = rss_mb
        except Exception:
            pass

    return {
        "pid": pid,
        "rss_mb": rss_mb,
        "peak_mb": peak_mb,
    }


class StabilityGovernor:
    """
    Unified stability monitor and zero-dependency zombie reclamation engine.
    """

    @classmethod
    def get_system_vitals(cls) -> Dict[str, Any]:
        """Collects complete real-time diagnostics on process, threads, DB, jobs, and memory."""
        now = time.time()
        uptime_seconds = round(now - _SERVER_BOOT_TIME, 1)

        # 1. Process & Memory Vitals
        mem = get_process_memory_usage()
        proc_stats = ProcessSupervisor.get_supervisor_stats()

        # 2. Thread Workers Vitals
        active_threads = list_active_workers()
        all_threads_count = threading.active_count()

        # 3. Database & WAL Vitals
        try:
            from src.infrastructure.database import get_database_connection_stats, db_status
            db_conn_stats = get_database_connection_stats()
            db_metrics = db_status()
        except Exception as e:
            db_conn_stats = {"error": str(e)}
            db_metrics = {}

        # 4. Job Manager Vitals
        job_stats = get_job_manager().get_job_stats()

        # 5. Async Streams Vitals
        stream_stats = AsyncStreamReaper.get_stream_stats()

        return {
            "status": "healthy",
            "uptime_seconds": uptime_seconds,
            "platform": sys.platform,
            "memory": mem,
            "process_supervisor": proc_stats,
            "threads": {
                "total_python_threads": all_threads_count,
                "registered_workers": active_threads
            },
            "database": {
                "connections": db_conn_stats,
                "metrics": db_metrics
            },
            "jobs": job_stats,
            "async_streams": stream_stats,
            "timestamp": now
        }

    @classmethod
    def reap_all_zombies(cls, truncate_wal: bool = True) -> Dict[str, Any]:
        """
        Master 1-Shot Zombie Reclamation Protocol:
        1. Reaps dead child subprocesses and closes pipe handles.
        2. Closes orphan SQLite connections from dead Python threads.
        3. Evicts stale/completed background jobs from RAM.
        4. Checkpoints SQLite WAL log.
        5. Triggers Python garbage collection (gc.collect).
        """
        start_time = time.time()
        mem_before = get_process_memory_usage()

        # 1. Reap child subprocesses
        reaped_children = ProcessSupervisor.reap_dead_children()

        # 2. Reap dead-thread database connections & truncate WAL
        try:
            from src.infrastructure.database import reap_zombie_connections, run_maintenance
            db_reap = reap_zombie_connections(idle_timeout_seconds=60.0)
            run_maintenance(truncate_wal=truncate_wal)
        except Exception as e:
            db_reap = {"status": "error", "error": str(e)}

        # 3. Reap stale background jobs (older than 10 minutes)
        reaped_jobs = get_job_manager().reap_stale_jobs(ttl_seconds=600.0, max_history=100)

        # 4. Force Python garbage collection
        gc_collected = gc.collect()

        mem_after = get_process_memory_usage()
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "success",
            "elapsed_ms": elapsed_ms,
            "reaped_children_count": reaped_children,
            "reaped_db_connections": db_reap.get("reaped_count", 0),
            "reaped_jobs_count": reaped_jobs,
            "gc_collected_objects": gc_collected,
            "memory_before_mb": mem_before["rss_mb"],
            "memory_after_mb": mem_after["rss_mb"],
            "memory_freed_mb": max(0.0, round(mem_before["rss_mb"] - mem_after["rss_mb"], 2))
        }
