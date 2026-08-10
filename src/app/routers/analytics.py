"""
FastAPI REST Router for Document Intelligence & Vault Analytics endpoints.
"""

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

router = APIRouter(tags=["analytics"])


@router.get("/api/analytics/summary", response_model=AnalyticsOverviewResponse)
@router.get("/api/analytics/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview_endpoint():
    try:
        return get_indexing_overview()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in analytics.py: {e}")
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
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in analytics.py: {e}")
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
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in analytics.py: {e}")
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
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in analytics.py: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve search activity telemetry: {str(e)}"
        )
