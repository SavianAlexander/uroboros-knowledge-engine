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
from src.infrastructure.repositories.files import get_file_revisions, revert_file_revision, save_file_revision
from src.infrastructure.vector_engine import index_directory
from src.infrastructure.database import get_db
from src.infrastructure.llm import is_llm_available, get_fallback_llm

router = APIRouter()

ACTIVE_DIR = "dumps"

def get_active_dir():
    try:
        from src.core.config import ACTIVE_DIR as m_dir
        return m_dir
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in files.py")
        return ACTIVE_DIR


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
        from collections import Counter
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', content)]
        freq = Counter(w for w in words if w not in ('the', 'and', 'for', 'with', 'that', 'this', 'from'))
        # ponytail: shortest diff wins
        suggested_tags = [w for w, _ in freq.most_common(5)]

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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in files.py: {e}")
            conn.commit()

        try:
            from src.core.state import GLOBAL_QUERY_CACHE
            if GLOBAL_QUERY_CACHE is not None:
                GLOBAL_QUERY_CACHE.invalidate()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in files.py: {e}")
        index_directory(os.path.dirname(norm_path))
        return {"status": "success", "filepath": norm_path, "path": norm_path}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in files.py: {e}")
        os.rename(real_old, norm_new)
        with get_db() as conn:
            cursor = conn.cursor()
            if norm_new != real_old:
                cursor.execute("DELETE FROM files WHERE filepath = ?", (norm_new,))
            cursor.execute("UPDATE files SET filepath = ?, filename = ? WHERE filepath = ? OR filepath = ?", (norm_new, req.new_name, real_old, old_fp))
            try:
                cursor.execute("DELETE FROM fts_files WHERE filepath = ? OR filepath = ?", (real_old, old_fp))
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in files.py: {e}")
            try:
                cursor.execute("UPDATE file_revisions SET filepath = ? WHERE filepath = ? OR filepath = ?", (norm_new, real_old, old_fp))
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
                logger.exception("Failed to update revision history for rename") # ponytail: remove redundant format
            conn.commit()
        index_directory(parent_dir)
        return {"status": "success", "old_filepath": real_old, "new_filepath": norm_new, "filepath": norm_new}
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in files.py: {e}")
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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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

from src.core.jobs import get_job_manager

@router.post("/api/file/index")
def index_directory_endpoint(req: IndexRequest):
    """Trigger background indexing and extraction across all supported files in active directory."""
    # ponytail: shortest diff wins
    dir_p = req.directory if req.directory else get_active_dir()

    if req.directory:
        verify_path_containment(req.directory)

    if not os.path.exists(dir_p):
        os.makedirs(dir_p, exist_ok=True)
        
    try:
        disk_usage = shutil.disk_usage(dir_p)
        if disk_usage.free < 100 * 1024 * 1024:
            raise HTTPException(status_code=507, detail="Insufficient storage space to complete index operation")
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in files.py: {e}")
        
    jm = get_job_manager()
    job_id = jm.submit_job(index_directory, dir_p)
    return {"status": "queued", "job_id": job_id, "indexed_dir": dir_p}

@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    jm = get_job_manager()
    job = jm.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in files.py: {e}")

    content = db_content
    if content is None and fp and os.path.exists(fp):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in files.py")
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
        from src.core.model_manager import get_fallback_llm as main_get_fallback_llm
        llm = main_get_fallback_llm()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in files.py")
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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
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
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in files.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))
