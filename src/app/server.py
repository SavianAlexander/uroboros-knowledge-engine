"""
FastAPI application server instantiation, middleware, static asset mounts, and router registrations.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware

from src.infrastructure.database import init_db
from src.app.routers import health, search, rag, files, tags, export, analytics, workflows

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    beacon = None
    try:
        import uuid
        from src.infrastructure.p2p_sync import P2PPeerBeacon
        beacon = P2PPeerBeacon(node_id=str(uuid.uuid4())[:8], http_port=8092)
        beacon.start()
    except Exception:
        pass
    try:
        yield
    finally:
        if beacon:
            try:
                beacon.stop()
            except Exception:
                pass

app = FastAPI(title="Uroboros Knowledge Database", default_response_class=UJSONResponse, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)

if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
elif os.path.exists("src/assets"):
    app.mount("/assets", StaticFiles(directory="src/assets"), name="assets")

app.include_router(health.router)
app.include_router(search.router)
app.include_router(rag.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(export.router)
app.include_router(analytics.router)
app.include_router(workflows.router)


