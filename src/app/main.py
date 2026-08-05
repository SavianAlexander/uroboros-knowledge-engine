"""
Main entrypoint module for src.app re-exporting FastAPI app and mounting export_router.
"""

from src.app.server import app
from src.app.routers.export import router as export_router, export_router as export_router_alias

__all__ = ["app", "export_router"]
