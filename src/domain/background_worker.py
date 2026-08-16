"""
Cooperative, Zero-Stutter Background Document Summarizer & Analysis Daemon.
Standard: Pure Python Standard Library (threading, ctypes, time, sqlite3, os)
Ponytail Senior Dev Principle: Idle OS thread priority + Boot grace period + 1-item throttled cool-off.
"""
import os
import sys
import time
import ctypes
import sqlite3
import threading
import logging
from typing import Optional
from src.infrastructure.database import get_db

logger = logging.getLogger(__name__)


def set_current_thread_idle_priority():
    """Lower current thread priority to IDLE so background work never lags desktop UI or audio."""
    if sys.platform == "win32":
        try:
            # -15 = THREAD_PRIORITY_IDLE on Windows NT/10/11
            THREAD_PRIORITY_IDLE = -15
            handle = ctypes.windll.kernel32.GetCurrentThread()
            ctypes.windll.kernel32.SetThreadPriority(handle, THREAD_PRIORITY_IDLE)
        except Exception as e:
            logger.debug(f"[BackgroundWorker] Windows thread priority note: {e}")
    else:
        try:
            os.nice(19)
        except Exception:
            pass


class DocumentSummarizerDaemon(threading.Thread):
    """
    Cooperative background daemon that generates document executive summaries:
    - 30-second boot grace period: allows application & browser to load at 0% background contention.
    - OS IDLE thread priority: yields CPU/GPU slices immediately when user interacts with PC.
    - Single-document throttled dispatch: processes 1 document per cycle with cooling intervals.
    """
    def __init__(self, boot_grace_seconds: int = 30, cooloff_seconds: int = 10, idle_interval_seconds: int = 60):
        super().__init__(daemon=True, name="CooperativeDocSummarizer")
        self.boot_grace_seconds = boot_grace_seconds
        self.cooloff_seconds = cooloff_seconds
        self.idle_interval_seconds = idle_interval_seconds
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        logger.info(f"[Summarizer Daemon] Started cooperative daemon (boot grace: {self.boot_grace_seconds}s).")
        
        # 1. Boot Grace Period: Keep CPU at 0% while app launches
        for _ in range(self.boot_grace_seconds):
            if not self._running:
                return
            time.sleep(1.0)

        # 2. Lower thread priority below normal desktop apps
        set_current_thread_idle_priority()

        # 3. Gentle throttled work loop
        while self._running:
            did_work = False
            try:
                did_work = self.process_single_unsummarized_document()
            except Exception as e:
                logger.warning(f"[Summarizer Daemon] Cycle error: {e}")

            # If work was processed, cool down for cooloff_seconds; otherwise sleep until idle_interval_seconds
            sleep_duration = self.cooloff_seconds if did_work else self.idle_interval_seconds
            for _ in range(sleep_duration):
                if not self._running:
                    return
                time.sleep(1.0)

    def process_single_unsummarized_document(self) -> bool:
        """Process exactly 1 document per step to prevent GPU/CPU spikes."""
        try:
            with get_db() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Find exactly 1 file missing an executive summary
                cursor.execute("""
                    SELECT id, filename, content FROM files 
                    WHERE content IS NOT NULL AND content != '' 
                      AND (metadata_json IS NULL OR json_extract(metadata_json, '$.summary') IS NULL)
                    ORDER BY id DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
                if not row:
                    return False

                from src.core.model_manager import get_fallback_llm
                llm = get_fallback_llm()
                if not llm:
                    return False

                fid = row["id"]
                content = row["content"][:1000]
                prompt = f"Summarize this document in 2 concise technical sentences:\n{content}"
                res = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=80)
                summary_text = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                if summary_text:
                    cursor.execute(
                        "UPDATE files SET metadata_json = json_set(COALESCE(metadata_json, '{}'), '$.summary', ?) WHERE id = ?",
                        (summary_text, fid)
                    )
                    conn.commit()
                    logger.info(f"[Summarizer Daemon] Gently summarized document #{fid} ({row['filename']})")
                    return True

                return False
        except Exception as e:
            logger.debug(f"[Summarizer Daemon] Worker iteration note: {e}")
            return False


_daemon: Optional[DocumentSummarizerDaemon] = None


def start_background_summarizer(boot_grace_seconds: int = 30, cooloff_seconds: int = 10):
    global _daemon
    if _daemon is None or not _daemon.is_alive():
        _daemon = DocumentSummarizerDaemon(
            boot_grace_seconds=boot_grace_seconds,
            cooloff_seconds=cooloff_seconds
        )
        _daemon.start()
    return _daemon
