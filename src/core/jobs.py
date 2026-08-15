import uuid
import time
import threading
import concurrent.futures
from typing import Dict, Any, Callable, Optional, List
import logging

logger = logging.getLogger(__name__)


class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.futures: Dict[str, concurrent.futures.Future] = {}
        self._jobs_lock = threading.Lock()
        self._reaped_jobs_count = 0

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def submit_job(
        self,
        task_func: Callable,
        *args,
        timeout_seconds: Optional[float] = None,
        description: str = "background_job",
        **kwargs
    ) -> str:
        job_id = str(uuid.uuid4())
        now = time.time()
        
        with self._jobs_lock:
            self.jobs[job_id] = {
                "id": job_id,
                "description": description,
                "status": "pending",
                "progress": 0.0,
                "result": None,
                "error": None,
                "started_at": now,
                "completed_at": None,
                "timeout_seconds": timeout_seconds,
            }
        
        # Inject job_id if the callable accepts it
        import inspect
        sig = inspect.signature(task_func)
        if 'job_id' in sig.parameters:
            kwargs['job_id'] = job_id

        import contextvars
        ctx = contextvars.copy_context()

        def wrapper(*w_args, **w_kwargs):
            try:
                return ctx.run(self._run_job, job_id, task_func, timeout_seconds, *w_args, **w_kwargs)
            except Exception as e:
                logger.error(f"Job {job_id} wrapper fatal error: {e}", exc_info=True)

        future = self.executor.submit(wrapper, *args, **kwargs)
        with self._jobs_lock:
            self.futures[job_id] = future
            
        return job_id

    def _run_job(self, job_id: str, task_func: Callable, timeout_seconds: Optional[float], *args, **kwargs):
        with self._jobs_lock:
            if job_id not in self.jobs:
                return
            if self.jobs[job_id]["status"] == "cancelled":
                return
            self.jobs[job_id]["status"] = "running"
            self.jobs[job_id]["started_at"] = time.time()

        try:
            result = task_func(*args, **kwargs)
            with self._jobs_lock:
                if self.jobs.get(job_id, {}).get("status") != "cancelled":
                    self.jobs[job_id]["status"] = "completed"
                    self.jobs[job_id]["progress"] = 100.0
                    self.jobs[job_id]["result"] = result
                    self.jobs[job_id]["completed_at"] = time.time()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.exception(f"Job {job_id} failed: {e}")
            with self._jobs_lock:
                if self.jobs.get(job_id, {}).get("status") != "cancelled":
                    self.jobs[job_id]["status"] = "failed"
                    self.jobs[job_id]["error"] = str(e)
                    self.jobs[job_id]["completed_at"] = time.time()

    def cancel_job(self, job_id: str) -> bool:
        """Attempts to cancel a pending or running job."""
        with self._jobs_lock:
            if job_id not in self.jobs:
                return False
            future = self.futures.get(job_id)
            if future and not future.done():
                future.cancel()
            self.jobs[job_id]["status"] = "cancelled"
            self.jobs[job_id]["completed_at"] = time.time()
            return True

    def update_progress(self, job_id: str, progress: float):
        with self._jobs_lock:
            if job_id in self.jobs and self.jobs[job_id]["status"] == "running":
                self.jobs[job_id]["progress"] = min(100.0, max(0.0, progress))

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._jobs_lock:
            job = self.jobs.get(job_id)
            return dict(job) if job else None

    def reap_stale_jobs(self, ttl_seconds: float = 3600.0, max_history: int = 500) -> int:
        """
        Evicts completed, failed, or cancelled jobs older than ttl_seconds.
        Caps total retained history at max_history to prevent unbounded RAM leakage.
        """
        now = time.time()
        reaped = 0
        with self._jobs_lock:
            terminal_jobs = [
                (jid, j) for jid, j in self.jobs.items()
                if j["status"] in ("completed", "failed", "cancelled")
            ]
            
            # 1. Evict by TTL
            for jid, j in terminal_jobs:
                comp_at = j.get("completed_at") or j.get("started_at", now)
                if now - comp_at > ttl_seconds:
                    del self.jobs[jid]
                    self.futures.pop(jid, None)
                    reaped += 1

            # 2. Evict by max history limit (oldest first)
            remaining_terminal = [
                (jid, j) for jid, j in self.jobs.items()
                if j["status"] in ("completed", "failed", "cancelled")
            ]
            if len(remaining_terminal) > max_history:
                remaining_terminal.sort(key=lambda x: x[1].get("completed_at") or 0)
                overflow_count = len(remaining_terminal) - max_history
                for i in range(overflow_count):
                    jid_to_del = remaining_terminal[i][0]
                    if jid_to_del in self.jobs:
                        del self.jobs[jid_to_del]
                        self.futures.pop(jid_to_del, None)
                        reaped += 1

            self._reaped_jobs_count += reaped

        return reaped

    def get_job_stats(self) -> Dict[str, Any]:
        """Returns real-time job queue vitals."""
        with self._jobs_lock:
            total = len(self.jobs)
            running = sum(1 for j in self.jobs.values() if j["status"] == "running")
            pending = sum(1 for j in self.jobs.values() if j["status"] == "pending")
            completed = sum(1 for j in self.jobs.values() if j["status"] == "completed")
            failed = sum(1 for j in self.jobs.values() if j["status"] == "failed")
            cancelled = sum(1 for j in self.jobs.values() if j["status"] == "cancelled")

        return {
            "total_tracked_jobs": total,
            "running": running,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "lifetime_reaped_jobs": self._reaped_jobs_count
        }

    def shutdown(self, wait: bool = False, timeout: float = 1.0):
        try:
            self.executor.shutdown(wait=wait, cancel_futures=True)
        except Exception:
            pass


def get_job_manager() -> JobManager:
    return JobManager.get_instance()

