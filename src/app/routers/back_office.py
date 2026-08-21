"""
FastAPI Router for Back-Office Batch Queue Management.
Exposes endpoints to enqueue, monitor, list, and cancel Colibrì 744B jobs.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.domain.back_office.job_queue import BackOfficeJobQueue, JobRecord, JobStatus, JobType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/backoffice", tags=["BackOffice"])
queue = BackOfficeJobQueue()


class EnqueueJobRequest(BaseModel):
    job_type: str
    payload: Dict[str, Any]
    priority: int = Field(default=2, ge=1, le=3)
    max_retries: int = Field(default=3, ge=1, le=10)


class JobResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    priority: int
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None
    retry_count: int


@router.post("/jobs", response_model=Dict[str, Any])
def enqueue_job(req: EnqueueJobRequest):
    """Enqueues a new background job for Colibrì 744B batch processing."""
    try:
        job_id = queue.enqueue(
            job_type=req.job_type,
            payload=req.payload,
            priority=req.priority,
            max_retries=req.max_retries
        )
        return {"status": "enqueued", "job_id": job_id, "job_type": req.job_type}
    except Exception as e:
        logger.error("Failed to enqueue job: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
def get_job(job_id: str):
    """Retrieves status and output of a specific job."""
    job = queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job.model_dump()


@router.get("/jobs", response_model=List[Dict[str, Any]])
def list_jobs(status: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200)):
    """Lists recent jobs with optional status filtering."""
    jobs = queue.list_jobs(status=status, limit=limit)
    return [j.model_dump() for j in jobs]


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    """Cancels a pending or processing job."""
    success = queue.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found or already finished")
    return {"status": "cancelled", "job_id": job_id}


@router.get("/stats")
def get_stats():
    """Retrieves queue load metrics across all statuses."""
    return queue.get_queue_stats()
