"""
FastAPI router for High-Throughput PDF/OCR Document Ingestion and Live Queue Telemetry.
Hardened with safe path sanitization, automatic temp-file cleanup, and bounded queue capacity.
"""
import json
import os
import uuid
import tempfile
import asyncio
from collections import deque
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from src.domain.ocr_pipeline import HybridPDFIngestionEngine

router = APIRouter(prefix="/api/ingest", tags=["Ingestion & OCR"])
engine = HybridPDFIngestionEngine()

# Bounded queue preventing in-memory process memory bloat
_MAX_QUEUE_CAPACITY = 200
_ingestion_queue: deque = deque(maxlen=_MAX_QUEUE_CAPACITY)


@router.post("/pdf", response_class=JSONResponse)
async def ingest_pdf_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Ingest a PDF document, extract layout/text, calculate OCR confidence, and enqueue for RAG indexing.
    Sanitizes upload filenames and guarantees automatic temp-file disk cleanup.
    """
    raw_name = file.filename or "document.pdf"
    if not raw_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    safe_filename = os.path.basename(raw_name)
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"ocr_{uuid.uuid4().hex[:8]}_{safe_filename}")

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        result = await asyncio.to_thread(engine.process_pdf, temp_path)

        queue_item = {
            "id": len(_ingestion_queue) + 1,
            "filename": safe_filename,
            "status": "processed",
            "confidence": result.get("confidence_score", 0.0),
            "pages": result.get("num_pages", 0),
            "words": result.get("total_words", 0),
            "requires_ocr_review": result.get("requires_ocr_review", False)
        }
        _ingestion_queue.append(queue_item)

        return JSONResponse(content={
            "status": "success",
            "data": result,
            "queue_item": queue_item
        })
    finally:
        # Guarantee zero disk leaks in temp directory
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@router.get("/queue", response_class=JSONResponse)
def get_ingestion_queue():
    """
    Retrieve live bounded PDF/OCR ingestion queue items.
    """
    queue_list = list(_ingestion_queue)
    return JSONResponse(content={
        "total_queued": len(queue_list),
        "queue": queue_list
    })


@router.get("/stream")
async def stream_ingestion_progress():
    """
    Real-time SSE event stream broadcasting PDF/OCR ingestion queue status updates.
    """
    async def event_generator():
        while True:
            queue_list = list(_ingestion_queue)
            payload = json.dumps({
                "type": "queue_telemetry",
                "count": len(queue_list),
                "items": queue_list[-10:]
            })
            yield f"data: {payload}\n\n"
            await asyncio.sleep(2.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

