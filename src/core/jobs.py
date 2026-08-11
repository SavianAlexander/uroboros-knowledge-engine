import uuid
import time
import threading
import concurrent.futures
from typing import Dict, Any, Callable, Optional
import logging

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def submit_job(self, task_func: Callable, *args, **kwargs) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "progress": 0.0,
            "result": None,
            "error": None,
            "started_at": time.time(),
        }
        
        # We need a way to pass the job_id into the task so it can update its own progress
        import inspect
        sig = inspect.signature(task_func)
        if 'job_id' in sig.parameters:
            kwargs['job_id'] = job_id

        import contextvars
        ctx = contextvars.copy_context()

        def wrapper(*args, **kwargs):
            import sys; print(f"WRAPPER ARGS: {args} KWARGS: {kwargs} outer_job_id: {job_id}", file=sys.stderr); sys.stderr.flush()
            try:
                return ctx.run(self._run_job, job_id, task_func, *args, **kwargs)
            except Exception as e:
                print(f"FATAL WRAPPER ERROR: {e}")
                import traceback; traceback.print_exc()

        future = self.executor.submit(wrapper, *args, **kwargs)
        return job_id

    def _run_job(self, _job_id: str, task_func: Callable, *args, **kwargs):
        self.jobs[_job_id]["status"] = "running"
        try:
            result = task_func(*args, **kwargs)
            self.jobs[_job_id]["status"] = "completed"
            self.jobs[_job_id]["progress"] = 100.0
            self.jobs[_job_id]["result"] = result
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.getLogger(__name__).exception(f"Swallowed error in jobs.py: {e}")
            logging.exception(f"Job {_job_id} failed: {e}")
            self.jobs[_job_id]["status"] = "failed"
            self.jobs[_job_id]["error"] = str(e)
            
        # Optional: Sync to SQLite here if we want persistence across reboots, 
        # but for a fast async queue, in-memory is fine for the lifetime of the process.

    def update_progress(self, job_id: str, progress: float):
        if job_id in self.jobs:
            self.jobs[job_id]["progress"] = progress

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def shutdown(self):
        self.executor.shutdown(wait=False)

def get_job_manager() -> JobManager:
    return JobManager.get_instance()
