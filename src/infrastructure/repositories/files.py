import os
import time
import hashlib
import sqlite3
from typing import Dict, List, Any, Optional
import src.infrastructure.database as db_infra
from src.infrastructure.database import get_db, get_db_connection, get_db_write_connection

from pathlib import Path

def save_file_revision(filepath: str, content: str):
    """Save a snapshot of file content into file_revisions with safe connection management."""
    norm_path = os.path.abspath(filepath)
    content_hash = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()
    with get_db_write_connection(db_infra.DB_FILE, timeout=db_infra.DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO file_revisions (filepath, content, sha256)
            VALUES (?, ?, ?)
        """, (norm_path, content, content_hash))
        
        cursor.execute("""
            DELETE FROM file_revisions
            WHERE filepath = ? AND id NOT IN (
                SELECT id FROM file_revisions WHERE filepath = ? ORDER BY id DESC LIMIT 5
            )
        """, (norm_path, norm_path))
        conn.commit()

def get_file_revisions(filepath: str) -> List[Dict[str, Any]]:
    """Retrieve last 5 revision snapshots for a file with safe connection management."""
    norm_path = os.path.abspath(filepath)
    fname = os.path.basename(norm_path)
    with get_db_connection(db_infra.DB_FILE, timeout=db_infra.DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filepath, sha256, saved_at, LENGTH(content) as content_length
            FROM file_revisions
            WHERE filepath = ? OR filepath LIKE ?
            ORDER BY id DESC LIMIT 5
        """, (norm_path, f"%{fname}"))
        return [dict(row) for row in cursor.fetchall()]

def revert_file_revision(filepath: str, revision_id: int) -> bool:
    """Revert a file to a specific revision ID snapshot."""
    norm_path = os.path.abspath(filepath)
    with get_db_write_connection(db_infra.DB_FILE, timeout=db_infra.DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM file_revisions WHERE id = ?", (revision_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        rev_content = row["content"]
        with open(norm_path, "w", encoding="utf-8") as f:
            f.write(rev_content)
        
        sha256 = hashlib.sha256(rev_content.encode("utf-8")).hexdigest()
        cursor.execute("UPDATE files SET content = ?, file_size = ?, modified_at = ? WHERE filepath = ? OR filename = ?", (rev_content, len(rev_content), os.path.getmtime(norm_path), norm_path, os.path.basename(norm_path)))
        try:
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (norm_path,))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content) VALUES (?, ?, ?)", (norm_path, os.path.basename(norm_path), rev_content))
        except Exception:
            pass
        conn.commit()
        return True