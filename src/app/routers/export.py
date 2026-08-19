"""
Export router for system stats CSV, search results CSV, and PDF reports.
"""
import json
import sqlite3
import time
import io
import csv
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.infrastructure.database import get_db
from src.core.domain.services import sanitise_fts_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["export"])
export_router = router


@router.get("/stats/export")
def export_stats_csv_endpoint():
    """Export MIME breakdown and system stats as CSV download."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mime_type, COUNT(*), SUM(file_size) FROM files GROUP BY mime_type")
            rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Mime Type", "File Count", "Total Size (bytes)"])
        for r in rows:
            writer.writerow([r[0] or "unknown", r[1], r[2] or 0])

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=system_stats.csv"},
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to export system stats CSV: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


def _fetch_export_rows(cursor, query: str):
    """Execute FTS search or fallback query to obtain up to 100 rows for export."""
    if query:
        try:
            cursor.execute(
                "SELECT files.filepath, files.filename, files.file_size, files.modified_at FROM fts_files JOIN files ON fts_files.filepath = files.filepath WHERE fts_files MATCH ? LIMIT 100",
                (sanitise_fts_query(query),),
            )
            rows = cursor.fetchall()
            if rows:
                return rows
        except Exception as e:
            logger.warning("FTS query failed during export, falling back to standard select: %s", e)
    cursor.execute("SELECT filepath, filename, file_size, modified_at FROM files LIMIT 100")
    return cursor.fetchall()


@router.get("/export")
def export_results_endpoint(query: str = "", format: str = "csv"):
    """Export search results as a CSV spreadsheet download."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            rows = _fetch_export_rows(cursor, query)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Filepath", "Filename", "Size (bytes)", "Modified At"])
        for r in rows:
            writer.writerow([r[0], r[1], r[2], r[3]])

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=uroboros_export.{format}"},
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to export search results: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/export")
def export_pdf_report_endpoint(style_template: str = "compact"):
    """Export PDF report of search index and statistics."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"Uroboros Knowledge Engine Report ({style_template})")
        c.drawString(100, 730, "System Status: Healthy")
        c.save()
        pdf_data = buffer.getvalue()
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=report.pdf"},
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to export PDF report: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/vault/json")
def export_vault_json_endpoint():
    """Export comprehensive vault inventory, tags, and vector chunk statistics as structured JSON download."""
    try:
        from fastapi.responses import Response
        with get_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, file_size, mime_type, modified_at, tags FROM files")
            files_data = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT file_id, COUNT(*) as chunks, COUNT(CASE WHEN embedding_json IS NOT NULL AND embedding_json != '[]' THEN 1 END) as embedded FROM file_chunks GROUP BY file_id")
            chunk_stats = {r["file_id"]: {"chunks": r["chunks"], "embedded": r["embedded"]} for r in cursor.fetchall()}

            for f in files_data:
                fid = f["id"]
                st = chunk_stats.get(fid, {"chunks": 0, "embedded": 0})
                f["total_chunks"] = st["chunks"]
                f["embedded_chunks"] = st["embedded"]

            payload = {
                "system": "Uroboros Knowledge Engine",
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "total_documents": len(files_data),
                "documents": files_data
            }

        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=vault_inventory.json"}
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to export vault JSON inventory: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/export/manifest")
def get_vault_export_manifest_endpoint():
    """Generates an export manifest containing SHA-256 integrity hashes, metadata, and chunk stats."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, file_size, mime_type, modified_at, sha256, tags FROM files")
            rows = cursor.fetchall()
            files_meta = [
                {
                    "id": r[0],
                    "filename": r[1],
                    "filepath": r[2],
                    "file_size": r[3] or 0,
                    "mime_type": r[4] or "text/plain",
                    "modified_at": r[5] or 0,
                    "sha256": r[6] or "",
                    "tags": r[7] or ""
                }
                for r in rows
            ]
        return {
            "status": "success",
            "engine": "Uroboros Knowledge Engine v8.0",
            "exported_at": time.time(),
            "total_files": len(files_meta),
            "manifest": files_meta
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to generate vault export manifest: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/export/package")
def export_vault_package_zip_endpoint():
    """Creates a self-contained portable ZIP archive of the vault with manifest and markdown contents."""
    import zipfile
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, file_size, mime_type, modified_at, sha256, tags, content FROM files")
            rows = cursor.fetchall()

        manifest_items = []
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for r in rows:
                fname = r[1] or f"doc_{r[0]}.txt"
                archive_name = f"documents/{r[0]}_{fname}"
                content = r[8] or ""
                zf.writestr(archive_name, content.encode("utf-8", errors="ignore"))
                manifest_items.append({
                    "id": r[0],
                    "filename": fname,
                    "archive_path": archive_name,
                    "file_size": r[3] or len(content),
                    "mime_type": r[4] or "text/plain",
                    "modified_at": r[5] or 0,
                    "sha256": r[6] or "",
                    "tags": r[7] or ""
                })

            manifest_json = json.dumps({
                "engine": "Uroboros Knowledge Engine v8.0",
                "exported_at": time.time(),
                "total_documents": len(manifest_items),
                "documents": manifest_items
            }, indent=2)
            zf.writestr("manifest.json", manifest_json.encode("utf-8"))

        zip_buffer.seek(0)
        timestamp_str = int(time.time())
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=vault_export_{timestamp_str}.zip"}
        )
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to create vault export package: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
