"""
Persistent SQLite Job Queue for Back-Office Batch Processing.
Handles priority-based job scheduling, state transitions, retries, and result persistence.
"""

import os
import sys
import time
import json
import uuid
import sqlite3
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

from src.infrastructure.database import get_db_connection

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    CONTEXTUAL_CHUNK_PREPEND = "CONTEXTUAL_CHUNK_PREPEND"
    GRAPHRAG_COMMUNITY_SUMMARY = "GRAPHRAG_COMMUNITY_SUMMARY"
    MIPRO_EVAL_SYNTHESIS = "MIPRO_EVAL_SYNTHESIS"
    MULTI_DOC_AUDIT = "MULTI_DOC_AUDIT"
    CUSTOM_BATCH_INFERENCE = "CUSTOM_BATCH_INFERENCE"


class JobRecord(BaseModel):
    """Pydantic v2 schema for Back-Office job representation."""
    job_id: str
    job_type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: int = 2
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class BackOfficeJobQueue:
    """
    Persistent SQLite-backed job queue for deep offline Colibrì 744B batch operations.
    """

    def __init__(self, db_path: str = "know.db"):
        self.db_path = db_path
        self._init_queue_table()

    def _init_queue_table(self) -> None:
        """Provisions back_office_jobs table with WAL mode."""
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS back_office_jobs (
                    job_id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    priority INTEGER NOT NULL DEFAULT 2,
                    created_at REAL NOT NULL,
                    started_at REAL,
                    completed_at REAL,
                    result_json TEXT,
                    error_msg TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 3
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_back_office_status_prio ON back_office_jobs(status, priority, created_at)")
            conn.commit()

    def enqueue(
        self,
        job_type: Union[JobType, str],
        payload: Dict[str, Any],
        priority: int = 2,
        max_retries: int = 3,
        job_id: Optional[str] = None
    ) -> str:
        """
        Enqueues a new background job.
        """
        j_id = job_id or f"job_{uuid.uuid4().hex[:12]}"
        j_type = job_type.value if isinstance(job_type, JobType) else str(job_type)
        now = time.time()
        payload_str = json.dumps(payload)

        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO back_office_jobs (
                    job_id, job_type, payload_json, status, priority, created_at, retry_count, max_retries
                ) VALUES (?, ?, ?, 'PENDING', ?, ?, 0, ?)
            """, (j_id, j_type, payload_str, priority, now, max_retries))
            conn.commit()

        logger.info("Enqueued Back-Office job '%s' (type=%s, prio=%d)", j_id, j_type, priority)
        return j_id

    def dequeue(self) -> Optional[JobRecord]:
        """
        Dequeues next highest-priority pending job (LIMIT 1) and transitions it to PROCESSING.
        """
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM back_office_jobs
                WHERE status = 'PENDING'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if not row:
                return None

            job_id = row["job_id"]
            now = time.time()

            conn.execute("""
                UPDATE back_office_jobs
                SET status = 'PROCESSING', started_at = ?
                WHERE job_id = ?
            """, (now, job_id))
            conn.commit()

            return JobRecord(
                job_id=job_id,
                job_type=row["job_type"],
                payload=json.loads(row["payload_json"]) if row["payload_json"] else {},
                status=JobStatus.PROCESSING,
                priority=row["priority"],
                created_at=row["created_at"],
                started_at=now,
                retry_count=row["retry_count"],
                max_retries=row["max_retries"]
            )

    def complete_job(self, job_id: str, result: Dict[str, Any]) -> bool:
        """Marks a job as COMPLETED and stores its output payload."""
        now = time.time()
        res_str = json.dumps(result)
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("""
                UPDATE back_office_jobs
                SET status = 'COMPLETED', completed_at = ?, result_json = ?, error_msg = NULL
                WHERE job_id = ?
            """, (now, res_str, job_id))
            conn.commit()
        logger.info("Completed Back-Office job '%s'", job_id)
        return True

    def fail_job(self, job_id: str, error_msg: str) -> bool:
        """
        Handles job failure with automated retry backoff or terminal FAILED transition.
        """
        now = time.time()
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT retry_count, max_retries FROM back_office_jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return False

            retries = row["retry_count"] + 1
            max_r = row["max_retries"]

            if retries < max_r:
                new_status = "PENDING"  # Re-enqueue for retry
                logger.warning("Job '%s' failed (%s), re-enqueuing (attempt %d/%d)", job_id, error_msg, retries, max_r)
            else:
                new_status = "FAILED"
                logger.error("Job '%s' permanently failed after %d retries: %s", job_id, retries, error_msg)

            conn.execute("""
                UPDATE back_office_jobs
                SET status = ?, error_msg = ?, retry_count = ?, completed_at = ?
                WHERE job_id = ?
            """, (new_status, error_msg, retries, now if new_status == "FAILED" else None, job_id))
            conn.commit()
        return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancels a pending or processing job."""
        now = time.time()
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("""
                UPDATE back_office_jobs
                SET status = 'CANCELLED', completed_at = ?
                WHERE job_id = ? AND status IN ('PENDING', 'PROCESSING')
            """, (now, job_id))
            conn.commit()
        return True

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Retrieves single job state by ID."""
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM back_office_jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return JobRecord(
                job_id=row["job_id"],
                job_type=row["job_type"],
                payload=json.loads(row["payload_json"]) if row["payload_json"] else {},
                status=JobStatus(row["status"]),
                priority=row["priority"],
                created_at=row["created_at"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
                result=json.loads(row["result_json"]) if row["result_json"] else None,
                error_msg=row["error_msg"],
                retry_count=row["retry_count"],
                max_retries=row["max_retries"]
            )

    def list_jobs(self, status: Optional[Union[JobStatus, str]] = None, limit: int = 50) -> List[JobRecord]:
        """Lists recent jobs with optional status filter."""
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                st_str = status.value if isinstance(status, JobStatus) else str(status)
                cursor.execute("""
                    SELECT * FROM back_office_jobs
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (st_str, limit))
            else:
                cursor.execute("""
                    SELECT * FROM back_office_jobs
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [
                JobRecord(
                    job_id=r["job_id"],
                    job_type=r["job_type"],
                    payload=json.loads(r["payload_json"]) if r["payload_json"] else {},
                    status=JobStatus(r["status"]),
                    priority=r["priority"],
                    created_at=r["created_at"],
                    started_at=r["started_at"],
                    completed_at=r["completed_at"],
                    result=json.loads(r["result_json"]) if r["result_json"] else None,
                    error_msg=r["error_msg"],
                    retry_count=r["retry_count"],
                    max_retries=r["max_retries"]
                ) for r in rows
            ]

    def get_queue_stats(self) -> Dict[str, int]:
        """Returns aggregated counts of jobs across all statuses."""
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM back_office_jobs GROUP BY status")
            counts = {status.value: 0 for status in JobStatus}
            for st, cnt in cursor.fetchall():
                counts[st] = cnt
            return counts
