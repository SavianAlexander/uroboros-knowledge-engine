from typing import Optional
from fastapi import APIRouter, Query
from src.domain.daily_briefing import generate_daily_briefing

router = APIRouter(tags=["briefing"])


@router.get("/api/briefing/daily")
@router.get("/api/briefing")
def get_daily_briefing_endpoint(
    limit: int = Query(5, ge=1, le=50, description="Max recent files and tags to return"),
    tag_filter: Optional[str] = Query(None, description="Optional tag filter for briefing synthesis"),
    include_audio_script: bool = Query(False, description="Include multi-speaker audio debrief dialogue"),
    user_id: Optional[str] = Query(None, description="Optional user context ID")
):
    """
    Daily Briefing API Endpoint.
    Dynamically configurable via request query parameters with optional podcast script synthesis.
    """
    briefing = generate_daily_briefing()
    
    if limit != 5:
        if "top_tags" in briefing and isinstance(briefing["top_tags"], list):
            briefing["top_tags"] = briefing["top_tags"][:limit]
        if "recent_files" in briefing and isinstance(briefing["recent_files"], list):
            briefing["recent_files"] = briefing["recent_files"][:limit]

    if tag_filter and "top_tags" in briefing:
        norm_filter = tag_filter.strip().lower()
        briefing["filtered_by_tag"] = tag_filter
        briefing["top_tags"] = [t for t in briefing["top_tags"] if norm_filter in str(t.get("tag", "")).lower()]

    if user_id:
        briefing["user_id"] = user_id

    if include_audio_script:
        from src.domain.audio_briefing import generate_audio_briefing_script
        audio_data = generate_audio_briefing_script(briefing)
        briefing["audio_briefing"] = audio_data

    return briefing
