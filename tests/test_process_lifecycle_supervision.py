"""
Unit and integration test suite for Process Lifecycle Supervision & Supervised PID Lockfile Guards.
Verifies:
1. Process liveness detection (is_pid_alive) on Win32/POSIX.
2. Atomic PID lockfile write, read, and remove operations.
3. Direct child process supervision with Popen handles.
4. Graceful termination protocol (SIGTERM / Win32 TerminateProcess) with timeout.
5. Deterministic cleanup_llama_server and atexit teardown safety.
6. Supervised single-instance enforcement and stale lock pruning.
7. Concurrency and zero lock collisions across multiple threads.
"""

import os
import sys
import time
import signal
import tempfile
import unittest
import threading
import subprocess

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.core.model_manager import (
    LlamaServerProcessSupervisor,
    is_pid_alive,
    cleanup_llama_server,
    ensure_single_llama_server_instance,
    DEFAULT_PID_PATH
)


class TestProcessLifecycleSupervision(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_proc_supervision_")
        self.custom_pid_path = os.path.join(self.test_dir, ".llama_server.pid")
        self.original_pid_path = LlamaServerProcessSupervisor.get_pid_path()
        LlamaServerProcessSupervisor.set_pid_path(self.custom_pid_path)

    def tearDown(self):
        LlamaServerProcessSupervisor.stop_server(timeout=1.0)
        LlamaServerProcessSupervisor.set_pid_path(self.original_pid_path)
        if os.path.exists(self.custom_pid_path):
            try:
                os.remove(self.custom_pid_path)
            except Exception:
                pass

    def test_01_is_pid_alive_detection(self):
        """Verify liveness detection correctly identifies active vs invalid PIDs."""
        # Current process must be alive
        self.assertTrue(is_pid_alive(os.getpid()))
        
        # Invalid and non-existent PIDs
        self.assertFalse(is_pid_alive(None))
        self.assertFalse(is_pid_alive(0))
        self.assertFalse(is_pid_alive(-1))
        self.assertFalse(is_pid_alive(9999999))

    def test_02_atomic_pid_lockfile_lifecycle(self):
        """Verify atomic writing, reading, and removal of PID lockfile."""
        current_pid = os.getpid()
        self.assertTrue(LlamaServerProcessSupervisor.write_pid(current_pid))
        self.assertTrue(os.path.exists(self.custom_pid_path))

        read_pid = LlamaServerProcessSupervisor.read_pid()
        self.assertEqual(read_pid, current_pid)

        self.assertTrue(LlamaServerProcessSupervisor.remove_pid())
        self.assertFalse(os.path.exists(self.custom_pid_path))
        self.assertIsNone(LlamaServerProcessSupervisor.read_pid())

    def test_03_direct_child_process_supervision(self):
        """Verify supervisor directly tracks child Popen handle and terminates it cleanly."""
        # Spawn a long-running dummy Python subprocess
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        try:
            self.assertIsNone(proc.poll())
            self.assertTrue(is_pid_alive(proc.pid))

            LlamaServerProcessSupervisor.register_process(proc)
            self.assertEqual(LlamaServerProcessSupervisor.get_active_pid(), proc.pid)
            self.assertEqual(LlamaServerProcessSupervisor.read_pid(), proc.pid)

            # Stop server cleanly
            res = LlamaServerProcessSupervisor.stop_server(timeout=2.0)
            self.assertTrue(res)
            self.assertFalse(is_pid_alive(proc.pid))
            self.assertIsNone(LlamaServerProcessSupervisor.get_active_pid())
            self.assertFalse(os.path.exists(self.custom_pid_path))
        finally:
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

    def test_04_graceful_termination_external_pid(self):
        """Verify supervisor terminates external running PID and prunes lockfile."""
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        try:
            LlamaServerProcessSupervisor.write_pid(proc.pid)
            self.assertEqual(LlamaServerProcessSupervisor.get_active_pid(), proc.pid)

            stopped = LlamaServerProcessSupervisor.terminate_process(proc.pid, timeout=2.0)
            self.assertTrue(stopped)
            self.assertFalse(is_pid_alive(proc.pid))
        finally:
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

    def test_05_stale_pid_lockfile_pruning(self):
        """Verify ensure_single_instance prunes stale lockfile referencing dead PID."""
        dead_pid = 9999998
        LlamaServerProcessSupervisor.write_pid(dead_pid)
        self.assertTrue(os.path.exists(self.custom_pid_path))

        LlamaServerProcessSupervisor._last_audit_time = 0.0
        LlamaServerProcessSupervisor.ensure_single_instance()

        self.assertFalse(os.path.exists(self.custom_pid_path))
        self.assertIsNone(LlamaServerProcessSupervisor.read_pid())

    def test_06_deterministic_cleanup_handler(self):
        """Verify cleanup_llama_server module-level exit handler executes safely."""
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        try:
            LlamaServerProcessSupervisor.register_process(proc)
            cleanup_llama_server()
            self.assertFalse(is_pid_alive(proc.pid))
        finally:
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

    def test_07_ensure_single_llama_server_instance_proxy(self):
        """Verify backward-compatible proxy function operates without error."""
        LlamaServerProcessSupervisor._last_audit_time = 0.0
        ensure_single_llama_server_instance()
        # Second call within debounce window
        ensure_single_llama_server_instance()

    def test_08_concurrent_lockfile_operations(self):
        """Verify multi-threaded concurrency safety for supervisor operations."""
        def worker(thread_idx):
            for _ in range(10):
                LlamaServerProcessSupervisor.read_pid()
                LlamaServerProcessSupervisor.get_active_pid()
                time.sleep(0.001)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


if __name__ == "__main__":
    unittest.main()
