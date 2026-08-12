from fastapi import APIRouter
from src.domain.daily_briefing import generate_daily_briefing

router = APIRouter()

@router.get("/api/briefing/daily")
@router.get("/api/briefing")
def get_daily_briefing_endpoint():
    """Daily Briefing API Endpoint."""
    return generate_daily_briefing()
