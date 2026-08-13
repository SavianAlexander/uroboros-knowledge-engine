"""
FastAPI application server instantiation, middleware, static asset mounts, and router registrations.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse
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
        port = int(os.environ.get("PORT", 8085))
        beacon = P2PPeerBeacon(node_id=str(uuid.uuid4())[:8], http_port=port)
        beacon.start()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in server.py: {e}")
    try:
        yield
    finally:
        if beacon:
            try:
                beacon.stop()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in server.py: {e}")

app = FastAPI(title="Uroboros Knowledge Database", default_response_class=JSONResponse, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)

if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

from fastapi.responses import FileResponse

@app.get("/")
def get_index():
    asset_path = Path("frontend/dist/index.html")
    if not asset_path.exists():
        # Fallback for dev mode
        return FileResponse("index.html") if os.path.exists("index.html") else JSONResponse({"error": "UI build not found. Run npm run build in frontend/."})
    return FileResponse(str(asset_path))


from fastapi import Depends
from src.app.auth import verify_api_key

from src.app.routers import health, search, rag, files, tags, export, analytics, workflows, briefing, ocr

app.include_router(health.router) # Health remains unprotected
app.include_router(search.router, dependencies=[Depends(verify_api_key)])
app.include_router(rag.router, dependencies=[Depends(verify_api_key)])
app.include_router(files.router, dependencies=[Depends(verify_api_key)])
app.include_router(tags.router, dependencies=[Depends(verify_api_key)])
app.include_router(export.router, dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, dependencies=[Depends(verify_api_key)])
app.include_router(workflows.router, dependencies=[Depends(verify_api_key)])
app.include_router(briefing.router, dependencies=[Depends(verify_api_key)])
app.include_router(ocr.router, dependencies=[Depends(verify_api_key)])
from src.app import auth
app.include_router(auth.router)


from fastapi import HTTPException

@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("assets/") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("health") or full_path.startswith("metrics"):
        raise HTTPException(status_code=404, detail="Not Found")
    asset_path = Path("frontend/dist/index.html")
    if asset_path.exists():
        return FileResponse(str(asset_path))
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return JSONResponse({"error": "UI build not found. Run npm run build in frontend/."})


