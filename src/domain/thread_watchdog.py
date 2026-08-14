"""
Global Thread Liveness Watchdog & Daemon Lifecycle Manager.
Tracks background threads, ensures strict daemon enforcement, and provides graceful shutdown joins.
Zero-dependency standard-library implementation.
"""
import threading
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

_REGISTERED_THREADS: List[Dict[str, Any]] = []
_REGISTRY_LOCK = threading.Lock()


def register_worker_thread(thread: threading.Thread, name: str = "worker") -> threading.Thread:
    """Ensures thread is marked daemon=True and tracks it in the global lifecycle registry."""
    thread.daemon = True
    with _REGISTRY_LOCK:
        _REGISTERED_THREADS.append({
            "name": name,
            "thread": thread
        })
    return thread


def list_active_workers() -> List[Dict[str, Any]]:
    """Returns a snapshot of all active registered background workers."""
    with _REGISTRY_LOCK:
        active = []
        for item in _REGISTERED_THREADS:
            t = item["thread"]
            active.append({
                "name": item["name"],
                "is_alive": t.is_alive(),
                "is_daemon": t.daemon,
                "ident": t.ident
            })
        return active


def shutdown_all_workers(timeout: float = 1.0) -> Dict[str, Any]:
    """Attempts cooperative shutdown and joins all active registered background workers."""
    with _REGISTRY_LOCK:
        joined = []
        for item in _REGISTERED_THREADS:
            t = item["thread"]
            if t.is_alive() and t != threading.current_thread():
                try:
                    t.join(timeout=timeout)
                    joined.append({"name": item["name"], "status": "stopped" if not t.is_alive() else "still_running"})
                except Exception as e:
                    joined.append({"name": item["name"], "status": f"error: {e}"})
        return {"status": "success", "workers": joined}
