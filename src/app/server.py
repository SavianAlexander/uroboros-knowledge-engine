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
    from src.core.shutdown import register_shutdown_handlers, execute_clean_shutdown
    from src.domain.thread_watchdog import list_active_workers, shutdown_all_workers
    register_shutdown_handlers()
    beacon = None
    worker = None
    try:
        import uuid
        from src.infrastructure.p2p_sync import P2PPeerBeacon
        port = int(os.environ.get("PORT", 8085))
        beacon = P2PPeerBeacon(node_id=str(uuid.uuid4())[:8], http_port=port)
        beacon.start()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in server.py beacon: {e}")

    try:
        from src.domain.background_worker import start_background_summarizer
        worker = start_background_summarizer()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error starting background summarizer: {e}")

    try:
        yield
    finally:
        if worker and hasattr(worker, 'stop'):
            try:
                worker.stop()
            except Exception:
                pass
        if beacon:
            try:
                beacon.stop()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in server.py beacon stop: {e}")
        execute_clean_shutdown()

app = FastAPI(title="Uroboros Knowledge Database", default_response_class=JSONResponse, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
elif os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

if os.path.exists(os.path.join(FRONTEND_DIST, "chunks")):
    app.mount("/chunks", StaticFiles(directory=os.path.join(FRONTEND_DIST, "chunks")), name="chunks")

from fastapi.responses import FileResponse

@app.get("/")
def get_index():
    asset_path = Path(FRONTEND_DIST) / "index.html"
    if not asset_path.exists():
        return FileResponse("index.html") if os.path.exists("index.html") else JSONResponse({"error": "UI build not found. Run npm run build in frontend/."})
    return FileResponse(str(asset_path))

@app.get("/app.js")
def get_app_bundle():
    p = os.path.join(FRONTEND_DIST, "app.js")
    return FileResponse(p, media_type="application/javascript") if os.path.exists(p) else FileResponse("app.js")

@app.get("/style.css")
def get_style_bundle():
    p = os.path.join(FRONTEND_DIST, "style.css")
    return FileResponse(p, media_type="text/css") if os.path.exists(p) else FileResponse("style.css")


from fastapi import Depends
from src.app.auth import verify_api_key

from src.app.routers import health, search, rag, files, tags, export, analytics, workflows, briefing, ocr, eve, voice, voice_ws, crawler

app.include_router(health.router) # Health remains unprotected
app.include_router(voice.router) # Voice and OpenAI audio API
app.include_router(voice_ws.router) # Real-Time Audio Spectrum & Call WebSocket
app.include_router(crawler.router, dependencies=[Depends(verify_api_key)])
app.include_router(search.router, dependencies=[Depends(verify_api_key)])
app.include_router(rag.router, dependencies=[Depends(verify_api_key)])
app.include_router(files.router, dependencies=[Depends(verify_api_key)])
app.include_router(tags.router, dependencies=[Depends(verify_api_key)])
app.include_router(export.router, dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, dependencies=[Depends(verify_api_key)])
app.include_router(workflows.router, dependencies=[Depends(verify_api_key)])
app.include_router(briefing.router, dependencies=[Depends(verify_api_key)])
app.include_router(ocr.router, dependencies=[Depends(verify_api_key)])
app.include_router(eve.router, dependencies=[Depends(verify_api_key)])
from src.app import auth
app.include_router(auth.router)


from fastapi import HTTPException

@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("health") or full_path.startswith("metrics"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Check frontend/dist first, then src/assets, then local root
    for candidate_dir in [Path("frontend/dist"), Path("src/assets"), Path(".")]:
        target = candidate_dir / full_path
        if target.is_file():
            return FileResponse(str(target))

    asset_path = Path("frontend/dist/index.html")
    if asset_path.exists():
        return FileResponse(str(asset_path))
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return JSONResponse({"error": "UI build not found. Run npm run build in frontend/."})


