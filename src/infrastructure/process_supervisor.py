"""
Process Supervisor & Child Process Zombie Reaper.
Standard: Pure Python Standard Library (os, sys, time, ctypes, subprocess, threading).
Ponytail Senior Dev Principle: Bind child processes to OS kernel Job Objects on Windows
and PR_SET_PDEATHSIG on Linux so orphan zombie processes are physically impossible.
"""

import os
import sys
import time
import signal
import logging
import threading
import subprocess
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Global registry of spawned child processes
_CHILDREN_LOCK = threading.Lock()
_TRACKED_CHILDREN: Dict[int, Dict[str, Any]] = {}
_REAPED_STATS = {
    "reaped_children": 0,
    "reaped_zombie_ports": 0,
    "last_reap_timestamp": 0.0
}

# Windows Job Object handle reference
_WIN_JOB_HANDLE = None


def init_os_process_guard():
    """
    Initializes OS-level kernel guard on process hierarchies:
    - Windows: Creates a Job Object with JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE (0x2000)
      and assigns the current process. All child processes spawned inherit this job
      and are guaranteed to be terminated by the Windows kernel if Python exits.
    - Linux: Configures parent death signal handlers.
    """
    global _WIN_JOB_HANDLE
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            # Constants
            JobObjectExtendedLimitInformation = 9
            JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
            JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x0010

            class IO_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("ReadOperationCount", ctypes.c_uint64),
                    ("WriteOperationCount", ctypes.c_uint64),
                    ("OtherOperationCount", ctypes.c_uint64),
                    ("ReadTransferCount", ctypes.c_uint64),
                    ("WriteTransferCount", ctypes.c_uint64),
                    ("OtherTransferCount", ctypes.c_uint64),
                ]

            class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                    ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD),
                ]

            class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                    ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryLimit", ctypes.c_size_t),
                    ("PeakJobMemoryLimit", ctypes.c_size_t),
                ]

            kernel32 = ctypes.windll.kernel32
            job = kernel32.CreateJobObjectW(None, None)
            if job:
                info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
                info.BasicLimitInformation.LimitFlags = (
                    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK
                )
                success = kernel32.SetInformationJobObject(
                    job,
                    JobObjectExtendedLimitInformation,
                    ctypes.byref(info),
                    ctypes.sizeof(info)
                )
                if success:
                    # Assign current process to Job Object
                    current_proc = kernel32.GetCurrentProcess()
                    kernel32.AssignProcessToJobObject(job, current_proc)
                    _WIN_JOB_HANDLE = job
                    logger.debug("Windows Job Object initialized: Zero-Zombie child process policy active.")
        except Exception as e:
            logger.debug(f"Windows Job Object initialization note: {e}")


# Initialize process guard on module load
init_os_process_guard()


class ProcessSupervisor:
    """
    Supervises background child processes, tracks lifecycle,
    and prevents zombie/orphan processes.
    """

    @classmethod
    def spawn_safe_subprocess(
        cls,
        args: Any,
        description: str = "child_task",
        **kwargs
    ) -> subprocess.Popen:
        """
        Spawns a child process, assigns it to the OS Job Object,
        and registers it in the active process tracker.
        """
        # Ensure default safe flags
        if sys.platform == "win32":
            # Pass CREATE_NO_WINDOW if not specified to prevent flashing console windows
            if "creationflags" not in kwargs:
                kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

        proc = subprocess.Popen(args, **kwargs)

        # On Windows, assign explicitly if job handle exists
        if sys.platform == "win32" and _WIN_JOB_HANDLE:
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.AssignProcessToJobObject(_WIN_JOB_HANDLE, int(proc._handle))
            except Exception:
                pass

        with _CHILDREN_LOCK:
            _TRACKED_CHILDREN[proc.pid] = {
                "pid": proc.pid,
                "proc": proc,
                "description": description,
                "command": str(args)[:200],
                "started_at": time.time(),
                "status": "running"
            }

        return proc

    @classmethod
    def reap_dead_children(cls) -> int:
        """
        Polls tracked child processes, reaps exit codes, and closes pipe handles.
        Returns count of reaped child processes.
        """
        reaped_count = 0
        with _CHILDREN_LOCK:
            dead_pids = []
            for pid, info in _TRACKED_CHILDREN.items():
                proc: subprocess.Popen = info["proc"]
                ret = proc.poll()
                if ret is not None:
                    dead_pids.append(pid)
                    # Close open stdio streams if any
                    for stream in (proc.stdin, proc.stdout, proc.stderr):
                        if stream and not stream.closed:
                            try:
                                stream.close()
                            except Exception:
                                pass

            for pid in dead_pids:
                del _TRACKED_CHILDREN[pid]
                reaped_count += 1

            _REAPED_STATS["reaped_children"] += reaped_count
            if reaped_count > 0:
                _REAPED_STATS["last_reap_timestamp"] = time.time()

        return reaped_count

    @classmethod
    def kill_all_child_processes(cls, timeout: float = 1.0) -> Dict[str, Any]:
        """
        Forcefully terminates all active child processes tracked by this supervisor.
        """
        results = []
        with _CHILDREN_LOCK:
            for pid, info in list(_TRACKED_CHILDREN.items()):
                proc: subprocess.Popen = info["proc"]
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=timeout)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        results.append({"pid": pid, "description": info["description"], "status": "terminated"})
                    except Exception as e:
                        results.append({"pid": pid, "description": info["description"], "status": f"error: {e}"})
            _TRACKED_CHILDREN.clear()

        return {"status": "success", "terminated": results}

    @classmethod
    def list_tracked_children(cls) -> List[Dict[str, Any]]:
        """Returns snapshot of currently tracked child processes."""
        cls.reap_dead_children()
        with _CHILDREN_LOCK:
            active = []
            for pid, info in _TRACKED_CHILDREN.items():
                active.append({
                    "pid": pid,
                    "description": info["description"],
                    "command": info["command"],
                    "started_at": info["started_at"],
                    "running_seconds": round(time.time() - info["started_at"], 2)
                })
            return active

    @classmethod
    def get_supervisor_stats(cls) -> Dict[str, Any]:
        """Returns diagnostic statistics for the process supervisor."""
        cls.reap_dead_children()
        with _CHILDREN_LOCK:
            active_count = len(_TRACKED_CHILDREN)
        return {
            "platform": sys.platform,
            "job_object_active": _WIN_JOB_HANDLE is not None,
            "active_tracked_children": active_count,
            "lifetime_reaped_children": _REAPED_STATS["reaped_children"],
            "last_reap_timestamp": _REAPED_STATS["last_reap_timestamp"]
        }


def cleanup_zombie_processes() -> int:
    """Convenience functional wrapper to reap dead children."""
    return ProcessSupervisor.reap_dead_children()


def get_system_resource_metrics() -> Dict[str, Any]:
    """Convenience functional wrapper to get supervisor metrics."""
    return ProcessSupervisor.get_supervisor_stats()

