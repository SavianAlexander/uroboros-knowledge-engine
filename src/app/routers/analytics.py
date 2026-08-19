"""
FastAPI REST Router for Document Intelligence & Vault Analytics endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from src.core.domain.models import (
    AnalyticsOverviewResponse,
    StorageBreakdownResponse,
    TagDistributionResponse,
    SearchActivityResponse
)
from src.domain.analytics_engine import (
    get_indexing_overview,
    get_storage_breakdown,
    get_tag_distribution,
    get_search_activity
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])


@router.get("/api/analytics/summary", response_model=AnalyticsOverviewResponse)
@router.get("/api/analytics/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview_endpoint():
    try:
        return get_indexing_overview()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to retrieve analytics overview: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics overview: {str(e)}"
        )


@router.get("/api/analytics/storage", response_model=StorageBreakdownResponse)
def get_analytics_storage_endpoint():
    try:
        return get_storage_breakdown()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to retrieve storage breakdown: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve storage breakdown: {str(e)}"
        )


@router.get("/api/analytics/tags", response_model=TagDistributionResponse)
def get_analytics_tags_endpoint():
    try:
        return get_tag_distribution()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to retrieve tag distribution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tag distribution: {str(e)}"
        )


@router.get("/api/analytics/search-activity", response_model=SearchActivityResponse)
def get_analytics_search_activity_endpoint():
    try:
        return get_search_activity()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to retrieve search activity telemetry: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve search activity telemetry: {str(e)}"
        )


@router.get("/api/sync/events/stream")
def get_sync_events_stream_endpoint(
    job_id: str = "default_sync",
    total_steps: int = 3,
    delay_ms: float = 0.0
):
    """Streams live SSE events for background knowledge synchronization."""
    try:
        from fastapi.responses import StreamingResponse
        from src.domain.sse_sync_stream import generate_knowledge_sync_sse_stream
        return StreamingResponse(
            generate_knowledge_sync_sse_stream(sync_job_id=job_id, total_steps=total_steps, delay_ms=delay_ms),
            media_type="text/event-stream"
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to stream sync events: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream sync events: {str(e)}"
        )
