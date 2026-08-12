"""
FastAPI router for High-Throughput PDF/OCR Document Ingestion and Live Queue Telemetry.
"""

import os
import tempfile
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, UJSONResponse
from src.domain.ocr_pipeline import HybridPDFIngestionEngine

router = APIRouter(prefix="/api/ingest", tags=["Ingestion & OCR"])
engine = HybridPDFIngestionEngine()

_ingestion_queue: List[Dict[str, Any]] = []


@router.post("/pdf", response_class=UJSONResponse)
async def ingest_pdf_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Ingest a PDF document, extract layout/text, calculate OCR confidence, and enqueue for RAG indexing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    result = engine.process_pdf(temp_path)

    queue_item = {
        "id": len(_ingestion_queue) + 1,
        "filename": file.filename,
        "status": "processed",
        "confidence": result["confidence_score"],
        "pages": result["num_pages"],
        "words": result["total_words"],
        "requires_ocr_review": result["requires_ocr_review"]
    }
    _ingestion_queue.append(queue_item)

    return UJSONResponse(content={
        "status": "success",
        "data": result,
        "queue_item": queue_item
    })


@router.get("/queue", response_class=UJSONResponse)
def get_ingestion_queue():
    """
    Retrieve live in-memory PDF/OCR ingestion queue items.
    """
    return UJSONResponse(content={
        "total_queued": len(_ingestion_queue),
        "queue": _ingestion_queue
    })


@router.get("/stream")
async def stream_ingestion_progress():
    """
    Real-time SSE event stream broadcasting PDF/OCR ingestion queue status updates.
    """
    async def event_generator():
        import json
        while True:
            payload = json.dumps({
                "type": "queue_telemetry",
                "count": len(_ingestion_queue),
                "items": _ingestion_queue[-10:]
            })
            yield f"data: {payload}\n\n"
            await asyncio.sleep(2.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
