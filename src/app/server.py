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
        port = int(os.environ.get("PORT", 8000))
        beacon = P2PPeerBeacon(node_id=str(uuid.uuid4())[:8], http_port=port)
        beacon.start()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in server.py: {e}")
    try:
        yield
    finally:
        if beacon:
            try:
                beacon.stop()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in server.py: {e}")

app = FastAPI(title="Uroboros Knowledge Database", default_response_class=UJSONResponse, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)

if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
elif os.path.exists("src/assets"):
    app.mount("/assets", StaticFiles(directory="src/assets"), name="assets")

from fastapi.responses import FileResponse

@app.get("/")
def get_index():
    asset_path = Path("src/assets/index.html")
    if not asset_path.exists():
        asset_path = Path("index.html")
    return FileResponse(str(asset_path))

@app.get("/style.css")
def get_css():
    asset_path = Path("src/assets/style.css")
    if not asset_path.exists():
        asset_path = Path("style.css")
    return FileResponse(str(asset_path), media_type="text/css")

@app.get("/app.js")
def get_js():
    asset_path = Path("src/assets/app.js")
    if not asset_path.exists():
        asset_path = Path("app.js")
    return FileResponse(str(asset_path), media_type="application/javascript")

from fastapi import Depends
from src.app.auth import verify_api_key

app.include_router(health.router) # Health remains unprotected
app.include_router(search.router, dependencies=[Depends(verify_api_key)])
app.include_router(rag.router, dependencies=[Depends(verify_api_key)])
app.include_router(files.router, dependencies=[Depends(verify_api_key)])
app.include_router(tags.router, dependencies=[Depends(verify_api_key)])
app.include_router(export.router, dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, dependencies=[Depends(verify_api_key)])
app.include_router(workflows.router, dependencies=[Depends(verify_api_key)])
from src.app import auth
app.include_router(auth.router)


