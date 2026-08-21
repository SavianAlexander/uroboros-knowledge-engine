"""
Cooperative Zero-Stutter Back-Office Worker Daemon.
Executes batch frontier-intelligence jobs for Colibrì 744B MoE while enforcing:
1. Windows THREAD_PRIORITY_IDLE OS priority.
2. 30-second cold boot grace period.
3. LIMIT 1 item rate-limiting.
4. 10-second inter-task cooling intervals.
"""

import os
import sys
import time
import ctypes
import threading
import logging
from typing import Dict, Any, Optional

from src.domain.back_office.job_queue import BackOfficeJobQueue, JobRecord, JobType, JobStatus
from src.domain.back_office.colibri_client import ColibriClient
from src.domain.back_office.tasks import (
    ContextualChunkPrependExecutor,
    GraphRAGCommunitySummarizer,
    MIPROEvalSynthesizer,
    MultiDocAuditExecutor
)

logger = logging.getLogger(__name__)

THREAD_PRIORITY_IDLE = -15
THREAD_PRIORITY_LOWEST = -2


def set_idle_thread_priority() -> bool:
    """
    Configures current thread priority to OS IDLE to guarantee zero UI/game stutter.
    """
    try:
        if sys.platform == "win32":
            handle = ctypes.windll.kernel32.GetCurrentThread()
            # Set thread priority to IDLE (-15)
            res = ctypes.windll.kernel32.SetThreadPriority(handle, THREAD_PRIORITY_IDLE)
            if res:
                logger.info("[ZERO_STUTTER] Configured Back-Office worker thread priority to THREAD_PRIORITY_IDLE (-15)")
                return True
        else:
            os.nice(19)
            logger.info("[ZERO_STUTTER] Configured Back-Office worker nice priority to 19")
            return True
    except Exception as e:
        logger.warning("[ZERO_STUTTER] Could not adjust thread priority: %s", e)
    return False


class CooperativeWorkerDaemon:
    """
    Background batch daemon running heavy Colibrì 744B jobs cooperatively.
    """

    def __init__(
        self,
        queue: Optional[BackOfficeJobQueue] = None,
        colibri_client: Optional[ColibriClient] = None,
        boot_grace_period_sec: float = 30.0,
        cooling_interval_sec: float = 10.0,
        poll_interval_sec: float = 5.0
    ):
        self.queue = queue or BackOfficeJobQueue()
        self.colibri_client = colibri_client or ColibriClient()
        self.boot_grace_period_sec = boot_grace_period_sec
        self.cooling_interval_sec = cooling_interval_sec
        self.poll_interval_sec = poll_interval_sec

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._is_active = False

    def start(self) -> None:
        """Starts the cooperative background worker daemon in a separate thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("CooperativeWorkerDaemon is already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="NeuroBackOfficeWorker", daemon=True)
        self._thread.start()
        self._is_active = True
        logger.info("CooperativeWorkerDaemon started successfully.")

    def stop(self, timeout: float = 5.0) -> None:
        """Signals worker daemon to stop gracefully."""
        self._stop_event.set()
        self._is_active = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        logger.info("CooperativeWorkerDaemon stopped.")

    def is_running(self) -> bool:
        """Returns True if the daemon thread is actively running."""
        return bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set())

    def run_once(self) -> Optional[JobRecord]:
        """
        Synchronously processes a single job from the queue.
        Useful for unit testing and manual triggers.
        """
        job = self.queue.dequeue()
        if not job:
            return None

        try:
            result = self._process_job(job)
            self.queue.complete_job(job.job_id, result)
            return self.queue.get_job(job.job_id)
        except Exception as e:
            logger.error("Job '%s' execution failed: %s", job.job_id, e)
            self.queue.fail_job(job.job_id, str(e))
            return self.queue.get_job(job.job_id)

    def _run_loop(self) -> None:
        """Main worker execution loop with zero-stutter safeguards."""
        set_idle_thread_priority()

        # 1. Cold boot grace period
        if self.boot_grace_period_sec > 0:
            logger.info("[ZERO_STUTTER] Waiting %.1fs cold-boot grace period before processing...", self.boot_grace_period_sec)
            self._stop_event.wait(timeout=self.boot_grace_period_sec)

        while not self._stop_event.is_set():
            job = None
            try:
                job = self.queue.dequeue()
            except Exception as e:
                logger.error("Queue dequeue error: %s", e)

            if not job:
                self._stop_event.wait(timeout=self.poll_interval_sec)
                continue

            # 2. Process Single Item (LIMIT 1)
            logger.info("Processing Back-Office job '%s' (type=%s, prio=%d)", job.job_id, job.job_type, job.priority)
            try:
                result = self._process_job(job)
                self.queue.complete_job(job.job_id, result)
            except Exception as e:
                logger.error("Error processing job '%s': %s", job.job_id, e)
                self.queue.fail_job(job.job_id, str(e))

            # 3. Inter-Task Cooling Interval (zero-stutter pause)
            if self.cooling_interval_sec > 0 and not self._stop_event.is_set():
                logger.info("[ZERO_STUTTER] Cooling interval (%.1fs) before next batch item...", self.cooling_interval_sec)
                self._stop_event.wait(timeout=self.cooling_interval_sec)

    def _process_job(self, job: JobRecord) -> Dict[str, Any]:
        """Routes job to its specialized task executor."""
        j_type = job.job_type

        if j_type == JobType.CONTEXTUAL_CHUNK_PREPEND.value or j_type == "CONTEXTUAL_CHUNK_PREPEND":
            return ContextualChunkPrependExecutor.execute(job.payload, client=self.colibri_client)

        elif j_type == JobType.GRAPHRAG_COMMUNITY_SUMMARY.value or j_type == "GRAPHRAG_COMMUNITY_SUMMARY":
            return GraphRAGCommunitySummarizer.execute(job.payload, client=self.colibri_client)

        elif j_type == JobType.MIPRO_EVAL_SYNTHESIS.value or j_type == "MIPRO_EVAL_SYNTHESIS":
            return MIPROEvalSynthesizer.execute(job.payload, client=self.colibri_client)

        elif j_type == JobType.MULTI_DOC_AUDIT.value or j_type == "MULTI_DOC_AUDIT":
            return MultiDocAuditExecutor.execute(job.payload, client=self.colibri_client)

        else:
            prompt = job.payload.get("prompt", "")
            out = self.colibri_client.generate(prompt)
            return {"output": out, "job_type": j_type}
