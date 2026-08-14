"""
Graceful Shutdown Handlers & Windows OS Control Signal Interceptor.
Captures SIGINT, SIGTERM, atexit, and Windows CTRL_CLOSE_EVENT to cleanly flush SQLite WAL
and terminate sockets without [WinError 32] file locking or zombie processes.
"""
import os
import sys
import atexit
import signal
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)
_SHUTDOWN_EXECUTED = False


def execute_clean_shutdown():
    """Executes atomic database checkpoint, closes sockets, and stops background threads."""
    global _SHUTDOWN_EXECUTED
    if _SHUTDOWN_EXECUTED:
        return
    _SHUTDOWN_EXECUTED = True

    # 1. Close database connections and checkpoint WAL
    try:
        from src.infrastructure.database import reset_db_connections, run_maintenance
        reset_db_connections()
        run_maintenance(truncate_wal=True)
    except Exception as e:
        logger.debug(f"Shutdown db maintenance note: {e}")

    # 2. Stop thread workers
    try:
        from src.domain.thread_watchdog import shutdown_all_workers
        shutdown_all_workers(timeout=0.5)
    except Exception as e:
        logger.debug(f"Shutdown worker note: {e}")


def register_shutdown_handlers():
    """Registers cross-platform signal handlers, atexit hook, and Windows console handlers."""
    # 1. Python atexit
    atexit.register(execute_clean_shutdown)

    # 2. POSIX / Standard signals
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, lambda s, f: (execute_clean_shutdown(), sys.exit(0)))
        except (ValueError, AttributeError):
            pass

    # 3. Windows Kernel32 SetConsoleCtrlHandler
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            PHANDLER_ROUTINE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

            def win_ctrl_handler(ctrl_type):
                # 0: CTRL_C, 1: CTRL_BREAK, 2: CTRL_CLOSE, 5: CTRL_LOGOFF, 6: CTRL_SHUTDOWN
                execute_clean_shutdown()
                return False  # Pass to next handler / let OS close cleanly

            # Retain reference to prevent garbage collection
            global _WIN_HANDLER_REF
            _WIN_HANDLER_REF = PHANDLER_ROUTINE(win_ctrl_handler)
            ctypes.windll.kernel32.SetConsoleCtrlHandler(_WIN_HANDLER_REF, True)
        except Exception as e:
            logger.debug(f"Note on Windows SetConsoleCtrlHandler: {e}")
