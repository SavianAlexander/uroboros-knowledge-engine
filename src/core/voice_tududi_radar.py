"""
Autonomous Tududi Task Master Voice Radar & Proactive Voice Notification Daemon.
Standard: Pure Python Standard Library (threading, time, json, os, sys).
Ponytail Senior Dev Principle: Non-blocking background radar polling task deadlines and speaking concise verbal summaries when action items require attention.
"""

import os
import sys
import json
import sqlite3
import threading
import time
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge


class TududiVoiceRadarDaemon:
    """Background voice radar monitoring Tududi task master metrics."""

    _running = False
    _thread = None
    _last_sweep_time = 0.0
    _poll_interval_seconds = 300  # 5 minutes

    @classmethod
    def _query_tududi_sqlite(cls, path: str, project_id: int, today_prefix: str) -> Optional[Dict[str, int]]:
        """Query live SQLite database for task metrics."""
        if not (path and os.path.isfile(path)):
            return None
        try:
            with sqlite3.connect(path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE (project_id=? OR ? IS NULL) AND status IN (0, 1)",
                    (project_id, project_id)
                )
                pending = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE (project_id=? OR ? IS NULL) AND status=2 AND (completed_at LIKE ? OR updated_at LIKE ?)",
                    (project_id, project_id, f"{today_prefix}%", f"{today_prefix}%")
                )
                completed_today = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE (project_id=? OR ? IS NULL) AND status IN (0, 1) AND due_date IS NOT NULL AND due_date != '' AND due_date < ?",
                    (project_id, project_id, today_prefix)
                )
                overdue = cursor.fetchone()[0]

                return {
                    "pending_tasks": int(pending),
                    "completed_today": int(completed_today),
                    "overdue_tasks": int(overdue)
                }
        except Exception:
            return None

    @classmethod
    def _query_tududi_cache(cls, cache_path: str, today_prefix: str) -> Optional[Dict[str, int]]:
        """Query fallback JSON cache snapshot for task metrics."""
        if not (cache_path and os.path.isfile(cache_path)):
            return None
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tasks = data.get("tasks", [])
            pending = sum(1 for t in tasks if t.get("status") in (0, 1))
            completed_today = sum(1 for t in tasks if t.get("status") == 2 and str(t.get("completed_at", "")).startswith(today_prefix))
            overdue = sum(1 for t in tasks if t.get("status") in (0, 1) and t.get("due_date") and str(t.get("due_date")) < today_prefix)
            return {
                "pending_tasks": pending,
                "completed_today": completed_today,
                "overdue_tasks": overdue
            }
        except Exception:
            return None

    @classmethod
    def _fetch_live_metrics(cls, project_id: int = 13) -> Dict[str, int]:
        """Query live Tududi SQLite database or cached snapshot for real task counts."""
        candidates = [
            os.environ.get("TUDUDI_DB_PATH", ""),
            "tududi.sqlite",
            os.path.expanduser("~/.tududi/tududi.sqlite"),
            os.path.join(BASE_DIR, "tududi.sqlite"),
            os.path.join(BASE_DIR, "..", "tududi.sqlite")
        ]

        today_prefix = time.strftime("%Y-%m-%d")

        for path in candidates:
            if metrics := cls._query_tududi_sqlite(path, project_id, today_prefix):
                return metrics

        cache_path = os.path.join(BASE_DIR, "vault", "roadmap", "tududi_cache.json")
        if metrics := cls._query_tududi_cache(cache_path, today_prefix):
            return metrics

        return {"pending_tasks": 0, "completed_today": 0, "overdue_tasks": 0}

    @classmethod
    def execute_radar_sweep(cls) -> Dict[str, Any]:
        """
        Execute an immediate Tududi task radar sweep and synthesize voice alert.
        """
        cls._last_sweep_time = time.time()
        metrics = cls._fetch_live_metrics()
        pending_tasks = metrics["pending_tasks"]
        completed_today = metrics["completed_today"]
        overdue_tasks = metrics["overdue_tasks"]

        # Speak announcement if pending items exist
        if overdue_tasks > 0:
            msg = f"Tududi Radar Alert: You have {overdue_tasks} overdue tasks requiring immediate attention."
            VoiceBridge.speak(msg, domain="DAILY_BRIEF", priority="CRITICAL", sfx_intro="shield_critical")
        elif pending_tasks > 0 or completed_today > 0:
            msg = f"Tududi Task Master report: {completed_today} tasks completed today with {pending_tasks} pending action items."
            VoiceBridge.speak(msg, domain="DAILY_BRIEF", priority="NORMAL")
        else:
            msg = "Tududi Task Master report: All task master action items and milestones are fully synchronized."
            VoiceBridge.speak(msg, domain="DAILY_BRIEF", priority="NORMAL")

        return {
            "status": "sweep_completed",
            "timestamp": cls._last_sweep_time,
            "pending_tasks": pending_tasks,
            "completed_today": completed_today,
            "overdue_tasks": overdue_tasks,
            "spoken": True
        }

    @classmethod
    def start_daemon(cls, interval_seconds: int = 300):
        """Start non-blocking radar monitoring thread."""
        if cls._running:
            return
        cls._poll_interval_seconds = interval_seconds
        cls._running = True
        cls._thread = threading.Thread(target=cls._radar_loop, daemon=True)
        cls._thread.start()

    @classmethod
    def stop_daemon(cls):
        """Stop background radar thread."""
        cls._running = False

    @classmethod
    def _radar_loop(cls):
        while cls._running:
            time.sleep(cls._poll_interval_seconds)
            if not cls._running:
                break
            try:
                cls.execute_radar_sweep()
            except Exception:
                pass
