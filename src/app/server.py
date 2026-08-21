"""
FastAPI application server instantiation, middleware, static asset mounts, and router registrations.
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
try:
    import orjson
    from fastapi.responses import ORJSONResponse as FastJSONResponse
except (ImportError, ModuleNotFoundError):
    from fastapi.responses import JSONResponse as FastJSONResponse
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from src.infrastructure.database import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from src.core.shutdown import register_shutdown_handlers, execute_clean_shutdown
    from src.domain.thread_watchdog import list_active_workers, shutdown_all_workers
    register_shutdown_handlers()
    beacon = None
    worker = None
    
    # Opt-in P2P Sync Beacon (Disabled by default for instant lightweight startup)
    if os.environ.get("ENABLE_P2P_BEACON", "").lower() in ("1", "true", "yes"):
        try:
            import uuid
            from src.infrastructure.p2p_sync import P2PPeerBeacon
            port = int(os.environ.get("PORT", 8085))
            beacon = P2PPeerBeacon(node_id=str(uuid.uuid4())[:8], http_port=port)
            beacon.start()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning("Failed to start P2P peer beacon: %s", e)

    # Opt-in GPU/CPU Background Summarizer (Disabled by default to prevent hardware lag)
    if os.environ.get("ENABLE_BACKGROUND_SUMMARIZER", "").lower() in ("1", "true", "yes"):
        try:
            from src.domain.background_worker import start_background_summarizer
            worker = start_background_summarizer()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning("Failed to start background summarizer: %s", e)

    # Cooperative Zero-Stutter SQLite WAL Daemon
    wal_worker = None
    if os.environ.get("ENABLE_WAL_DAEMON", "1").lower() in ("1", "true", "yes"):
        try:
            from src.infrastructure.database import start_wal_daemon
            wal_worker = start_wal_daemon()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning("Failed to start WAL daemon: %s", e)

    try:
        yield
    finally:
        if wal_worker and hasattr(wal_worker, 'stop'):
            try:
                wal_worker.stop()
            except Exception:
                pass
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
                logger.warning("Failed to cleanly stop P2P beacon: %s", e)
        execute_clean_shutdown()

app = FastAPI(
    title="Uroboros Knowledge Engine API",
    description="Enterprise-grade Knowledge Engine with Hybrid RRF RAG, Graph Traversal, Neural Voice, and Autonomous Swarm Intelligence.",
    version="2.0.0",
    default_response_class=FastJSONResponse,
    lifespan=lifespan
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi import Request
from src.shared.exceptions import UroborosError

@app.exception_handler(UroborosError)
async def uroboros_exception_handler(request: Request, exc: UroborosError):
    return FastJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

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
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    if not asset_path.exists():
        return FileResponse("index.html", headers=headers) if os.path.exists("index.html") else JSONResponse({"error": "UI build not found. Run npm run build in frontend/."})
    return FileResponse(str(asset_path), headers=headers)

@app.get("/app.js")
def get_app_bundle():
    p = os.path.join(FRONTEND_DIST, "app.js")
    headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=604800"}
    if os.path.exists(p):
        return FileResponse(p, media_type="application/javascript", headers=headers)
    # If React build is active, Vite bundles assets in /assets/
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        raise HTTPException(status_code=404, detail="Legacy bundle app.js deprecated in React SPA. Use assets/index-*.js.")
    return FileResponse("app.js", headers=headers) if os.path.exists("app.js") else JSONResponse({"error": "Bundle not found"}, status_code=404)

@app.get("/style.css")
def get_style_bundle():
    p = os.path.join(FRONTEND_DIST, "style.css")
    headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=604800"}
    if os.path.exists(p):
        return FileResponse(p, media_type="text/css", headers=headers)
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        raise HTTPException(status_code=404, detail="Legacy bundle style.css deprecated in React SPA. Use assets/index-*.css.")
    return FileResponse("style.css", headers=headers) if os.path.exists("style.css") else JSONResponse({"error": "Style not found"}, status_code=404)


from fastapi import Depends
from src.app.auth import verify_api_key

from src.app.routers import health, search, rag, retrieval_ops, files, datasets, tags, export, analytics, workflows, briefing, ocr, voice, voice_ws, crawler, back_office

app.include_router(health.router) # Health remains unprotected
app.include_router(voice.router) # Voice and OpenAI audio API
app.include_router(voice_ws.router) # Real-Time Audio Spectrum & Call WebSocket
app.include_router(crawler.router, dependencies=[Depends(verify_api_key)])
app.include_router(search.router, dependencies=[Depends(verify_api_key)])
app.include_router(rag.router, dependencies=[Depends(verify_api_key)])
app.include_router(retrieval_ops.router, dependencies=[Depends(verify_api_key)])
app.include_router(files.router, dependencies=[Depends(verify_api_key)])
app.include_router(datasets.router, dependencies=[Depends(verify_api_key)])
app.include_router(tags.router, dependencies=[Depends(verify_api_key)])
app.include_router(export.router, dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, dependencies=[Depends(verify_api_key)])
app.include_router(workflows.router, dependencies=[Depends(verify_api_key)])
app.include_router(briefing.router, dependencies=[Depends(verify_api_key)])
app.include_router(ocr.router, dependencies=[Depends(verify_api_key)])
app.include_router(back_office.router, dependencies=[Depends(verify_api_key)])
from src.app import auth
app.include_router(auth.router)


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


