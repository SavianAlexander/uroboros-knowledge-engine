"""
File management, uploading, editing, raw inspection, and revision endpoints.
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import logging

logger = logging.getLogger(__name__)

from src.shared.security import verify_path_containment
from src.core.domain.models import (
    FileSaveRequest,
    FileEditRequest,
    DeleteFileRequest,
    BulkDeleteRequest,
    IndexRequest,
    RevertRequest,
    OpenFileRequest,
    FileInsightsRequest,
    RenameRequest,
)
from src.core.domain.services import generate_summary, generate_key_takeaways
from src.infrastructure.database import (
    get_file_revisions,
    revert_file_revision,
    index_directory,
    save_file_revision,
    get_db,
)
from src.infrastructure.llm import is_llm_available, get_fallback_llm

router = APIRouter()

ACTIVE_DIR = "dumps"

def get_active_dir():
    try:
        from main import ACTIVE_DIR as m_dir
        return m_dir
    except Exception:
        return ACTIVE_DIR

@router.get("/")
def get_index():
    asset_path = Path("src/assets/index.html")
    if not asset_path.exists():
        asset_path = Path("index.html")
    return FileResponse(str(asset_path))

@router.get("/style.css")
def get_css():
    asset_path = Path("src/assets/style.css")
    if not asset_path.exists():
        asset_path = Path("style.css")
    return FileResponse(str(asset_path), media_type="text/css")

@router.get("/app.js")
def get_js():
    asset_path = Path("src/assets/app.js")
    if not asset_path.exists():
        asset_path = Path("app.js")
    return FileResponse(str(asset_path), media_type="application/javascript")

@router.get("/api/file/raw")
@router.get("/api/file")
def get_raw_file(path: str):
    """Retrieve raw file content and metadata."""
    verify_path_containment(path)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        norm_path = os.path.abspath(path)
        tags = []
        file_id = None
        db_content = None
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content FROM files WHERE filepath = ? OR filepath = ?", (path, norm_path))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="File not found")
            file_id = row[0]
            db_content = row[1]
            cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (file_id,))
            tags = [r[0] for r in cursor.fetchall()]

        ext = os.path.splitext(path)[1].lower()
        if ext in ('.pdf', '.docx', '.xlsx', '.rtf') and db_content:
            content = db_content
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        import re
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', content)]
        freq = {}
        for w in words:
            if w not in ('the', 'and', 'for', 'with', 'that', 'this', 'from'):
                freq[w] = freq.get(w, 0) + 1
        top_words = [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]]
        suggested_tags = list(set(top_words))

        res = {
            "id": file_id,
            "path": path,
            "filepath": path,
            "filename": os.path.basename(path),
            "content": content,
            "tags": tags,
            "suggested_tags": suggested_tags
        }
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.wav', '.mp3', '.flac', '.ogg', '.m4a'):
            from src.infrastructure.parsers import parse_audio_metadata
            res["audio_metadata"] = parse_audio_metadata(path)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/file/save")
@router.post("/api/file/edit")
def save_file_endpoint(req: FileSaveRequest):
    """Save updated content to file with revision history tracking."""
    fp = req.get_path()
    verify_path_containment(fp)
    norm_path = os.path.abspath(fp)
    if not os.path.exists(norm_path):
        raise HTTPException(status_code=404, detail="File does not exist")
    if os.path.isdir(norm_path):
        raise HTTPException(status_code=500, detail="Is a directory")

    try:
        with open(norm_path, "r", encoding="utf-8", errors="ignore") as f:
            old_content = f.read()
        save_file_revision(norm_path, old_content)

        from src.infrastructure.parsers import safe_write_file
        safe_write_file(norm_path, req.content)

        with get_db() as conn:
            cursor = conn.cursor()
            mtime = os.path.getmtime(norm_path)
            fsize = os.path.getsize(norm_path)
            cursor.execute("UPDATE files SET content = ?, file_size = ?, modified_at = ? WHERE filepath = ?", (req.content, fsize, mtime, norm_path))
            try:
                cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (norm_path,))
                fn = os.path.basename(norm_path)
                cursor.execute("INSERT INTO fts_files (filepath, filename, content) VALUES (?, ?, ?)", (norm_path, fn, req.content))
            except Exception:
                pass
            conn.commit()

        try:
            import sys
            if "main" in sys.modules and hasattr(sys.modules["main"], "GLOBAL_QUERY_CACHE"):
                c = getattr(sys.modules["main"], "GLOBAL_QUERY_CACHE", None)
                if c and hasattr(c, "clear"):
                    c.clear()
        except Exception:
            pass

        index_directory(os.path.dirname(norm_path))
        return {"status": "success", "filepath": norm_path, "path": norm_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/file/tree")
@router.get("/api/tree")
def get_file_tree():
    """Retrieve file tree directory structure of active workspace."""
    base = get_active_dir()
    if not os.path.exists(base):
        os.makedirs(base, exist_ok=True)
    tree = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, base)
            tree.append({"filepath": fp, "relative_path": rel, "size": os.path.getsize(fp)})
    return {"base": base, "tree": tree}

@router.post("/api/file/delete")
def delete_file_endpoint(req: DeleteFileRequest):
    """Securely delete file from disk and database."""
    fp = req.get_path()
    verify_path_containment(fp)
    if not os.path.exists(fp):
        raise HTTPException(status_code=404, detail="File does not exist")
    try:
        norm_path = os.path.abspath(fp)
        os.remove(norm_path)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE filepath = ?", (norm_path,))
            row = cursor.fetchone()
            file_id = row[0] if row else None
            cursor.execute("DELETE FROM files WHERE filepath = ?", (norm_path,))
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (norm_path,))
            cursor.execute("DELETE FROM file_revisions WHERE filepath = ?", (norm_path,))
            if file_id:
                cursor.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM ocr_coords WHERE file_id = ?", (file_id,))
            conn.commit()
        return {"status": "success", "deleted": norm_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/file/rename")
def rename_file_endpoint(req: RenameRequest):
    """Rename file on disk and update database references."""
    old_fp = req.get_path()
    verify_path_containment(old_fp)
    real_old = os.path.abspath(old_fp)
    if not os.path.exists(old_fp) and not os.path.exists(real_old):
        raise HTTPException(status_code=404, detail="File does not exist")
    
    real_old = real_old if os.path.exists(real_old) else os.path.abspath(old_fp)
    parent_dir = os.path.dirname(real_old)
    norm_new = os.path.abspath(os.path.join(parent_dir, req.new_name))
    verify_path_containment(norm_new)
    
    if os.path.exists(norm_new) and norm_new != real_old and not req.overwrite:
        raise HTTPException(status_code=400, detail="Target file already exists")
    
    try:
        if os.path.exists(norm_new) and norm_new != real_old:
            try:
                os.remove(norm_new)
            except Exception:
                pass
        os.rename(real_old, norm_new)
        with get_db() as conn:
            cursor = conn.cursor()
            if norm_new != real_old:
                cursor.execute("DELETE FROM files WHERE filepath = ?", (norm_new,))
            cursor.execute("UPDATE files SET filepath = ?, filename = ? WHERE filepath = ? OR filepath = ?", (norm_new, req.new_name, real_old, old_fp))
            try:
                cursor.execute("DELETE FROM fts_files WHERE filepath = ? OR filepath = ?", (real_old, old_fp))
            except Exception:
                pass
            try:
                cursor.execute("UPDATE file_revisions SET filepath = ? WHERE filepath = ? OR filepath = ?", (norm_new, real_old, old_fp))
            except Exception as e:
                logger.warning(f'Failed to update revision history for rename: {e}')
            conn.commit()
        index_directory(parent_dir)
        return {"status": "success", "old_filepath": real_old, "new_filepath": norm_new, "filepath": norm_new}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/bulk_delete")
@router.post("/api/file/bulk-delete")
def bulk_delete_endpoint(req: BulkDeleteRequest):
    """Bulk delete files from workspace and database."""
    deleted = []
    for fp in req.filepaths:
        try:
            verify_path_containment(fp)
            if os.path.exists(fp):
                os.remove(fp)
                deleted.append(fp)
        except Exception:
            pass
    return {"status": "success", "deleted": deleted}

@router.post("/api/upload")
def upload_file_endpoint(file: UploadFile = File(...)):
    """Upload new file into workspace active directory."""
    base = get_active_dir()
    if file.filename and file.filename.startswith("voice-memo-"):
        base = os.path.join(base, "voice_memos")
    os.makedirs(base, exist_ok=True)
    dest_path = os.path.join(base, file.filename)
    verify_path_containment(dest_path)
    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        index_directory(base)
        return {"status": "success", "filename": file.filename, "filepath": dest_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TranscribeRequest(BaseModel):
    filepath: str

@router.post("/api/transcribe")
def transcribe_audio_endpoint(req: TranscribeRequest):
    """Transcribe audio voice memo and auto-index transcript document."""
    from src.domain.transcription_engine import transcribe_audio_memo
    verify_path_containment(req.filepath)
    result = transcribe_audio_memo(req.filepath)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Auto-index transcript into SQLite database
    transcript_file = req.filepath + ".txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(result["transcript"])

    parent_dir = os.path.dirname(req.filepath)
    index_directory(parent_dir)
    return {"status": "success", "transcription": result, "transcript_file": transcript_file}

@router.post("/api/index")
def trigger_index_endpoint(req: IndexRequest):
    """Trigger directory indexing task with disk space check."""
    dir_p = req.get_dir()
    try:
        total, used, free = shutil.disk_usage(dir_p if (dir_p and os.path.exists(dir_p)) else ".")
        if free < 10 * 1024 * 1024:
            raise HTTPException(status_code=507, detail="Insufficient storage space to complete index operation")
    except HTTPException:
        raise
    except Exception:
        pass
    try:
        index_directory(dir_p)
        return {"status": "success", "indexed_dir": dir_p}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/file/summary")
def get_file_summary_endpoint(path: str):
    """Retrieve or generate concise document summary."""
    verify_path_containment(path)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        summary = generate_summary(text)
        takeaways = generate_key_takeaways(text)
        return {"filepath": path, "summary": summary, "takeaways": takeaways}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/file/revisions")
def get_file_revisions_endpoint(path: str):
    """Retrieve last 5 revision snapshots for a file."""
    verify_path_containment(path)
    return {"path": path, "revisions": get_file_revisions(path)}

@router.post("/api/file/revert")
def revert_file_revision_endpoint(req: RevertRequest):
    """Revert a file to a specific revision ID."""
    fp = req.get_path()
    verify_path_containment(fp)
    success = revert_file_revision(fp, req.revision_id)
    if not success:
        raise HTTPException(status_code=400, detail="Revision ID not found or path mismatch")
    return {"status": "success", "reverted_to": req.revision_id}

@router.get("/api/file/insights")
@router.post("/api/file/insights")
def get_file_insights_endpoint(req: Optional[FileInsightsRequest] = None, path: Optional[str] = None):
    """
    Generate deep AI document insights.
    Truncation boundary: content > 4000 characters -> content[:2000] + content[-2000:]
    Prompt format: Document Content:\n{truncated_text}\n\nProvide the summary and 3 key insights.
    """
    fp = path
    if req and req.get_path():
        fp = req.get_path()

    verify_path_containment(fp)

    db_content = None
    if fp:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT content FROM files WHERE filepath = ?", (fp,))
                row = cursor.fetchone()
                if row:
                    db_content = row[0]
        except Exception:
            pass

    content = db_content
    if content is None and fp and os.path.exists(fp):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = None

    error_prefixes = (
        "[Parsing Error:",
        "[OCR Error:",
        "[OCR Setup Error:",
        "[OCR not supported",
        "[ThreadPool Error:",
        "[File Size Exceeds",
        "[Image Parsing Error:"
    )

    if content is None or not content.strip() or any(content.strip().startswith(prefix) for prefix in error_prefixes):
        return {"filepath": fp or "", "path": fp or "", "insights": "*This document contains no readable text content to extract insights.*"}

    try:
        from main import get_fallback_llm as main_get_fallback_llm
        llm = main_get_fallback_llm()
    except Exception:
        llm = get_fallback_llm()

    if not is_llm_available() and llm is None:
        raise HTTPException(status_code=501, detail="Local LLM inference module (llama_cpp) is not available on this system.")

    try:
        if len(content) > 4000:
            truncated_text = content[:2000] + content[-2000:]
        else:
            truncated_text = content

        prompt = f"Document Content:\n{truncated_text}\n\nProvide the summary and 3 key insights."
        if llm:
            completion = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a document analyzer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.3
            )
            insights = completion["choices"][0]["message"]["content"]
        else:
            insights = "Extractive Insights Summary:\n" + generate_summary(truncated_text)

        return {"filepath": fp, "path": fp, "insights": insights}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/open")
@router.post("/api/file/open")
def open_file_endpoint(req: OpenFileRequest):
    """Open file in native operating system default app."""
    fp = req.get_path()
    verify_path_containment(fp)
    if not os.path.exists(fp):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.startfile(fp)
        return {"status": "opened", "filepath": fp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
