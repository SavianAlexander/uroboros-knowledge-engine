import os
import time
import hashlib
import sqlite3
from typing import Dict, List, Any, Optional
from src.infrastructure.database import get_db, get_db_connection, get_db_write_connection, DB_FILE, DB_TIMEOUT

from pathlib import Path

def save_file_revision(filepath: str, content: str):
    """Save a snapshot of file content into file_revisions with safe connection management."""
    norm_path = str(Path(filepath).resolve())
    abs_path = os.path.abspath(filepath)
    content_hash = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT,
                content TEXT,
                sha256 TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO file_revisions (filepath, content, sha256)
            VALUES (?, ?, ?)
        """, (norm_path, content, content_hash))
        if norm_path != abs_path:
            cursor.execute("""
                INSERT INTO file_revisions (filepath, content, sha256)
                VALUES (?, ?, ?)
            """, (abs_path, content, content_hash))
        
        cursor.execute("""
            DELETE FROM file_revisions
            WHERE filepath = ? AND id NOT IN (
                SELECT id FROM file_revisions WHERE filepath = ? ORDER BY id DESC LIMIT 5
            )
        """, (norm_path, norm_path))
        conn.commit()

def get_file_revisions(filepath: str) -> List[Dict[str, Any]]:
    """Retrieve last 5 revision snapshots for a file with safe connection management."""
    norm_path = str(Path(filepath).resolve())
    abs_path = os.path.abspath(filepath)
    with get_db_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT,
                content TEXT,
                sha256 TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            SELECT id, filepath, sha256, saved_at, LENGTH(content) as content_length
            FROM file_revisions
            WHERE filepath = ? OR filepath = ?
            ORDER BY id DESC LIMIT 5
        """, (norm_path, abs_path))
        return [dict(row) for row in cursor.fetchall()]

def revert_file_revision(filepath: str, revision_id: int) -> bool:
    """Revert a file to a specific revision ID with correct column name."""
    norm_path = str(Path(filepath).resolve())
    abs_path = os.path.abspath(filepath)
    with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT filepath, content FROM file_revisions WHERE id = ?", (revision_id,))
        row = cursor.fetchone()
        if not row:
            return False
        row_path = str(Path(row["filepath"]).resolve())
        if row_path != norm_path and row["filepath"] != abs_path and row["filepath"] != filepath:
            return False
        
        rev_content = row["content"]
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(rev_content)
        if norm_path != abs_path and os.path.exists(norm_path):
            try:
                with open(norm_path, "w", encoding="utf-8") as f:
                    f.write(rev_content)
            except Exception:
                pass
        
        sha256 = hashlib.sha256(rev_content.encode("utf-8")).hexdigest()
        cursor.execute("UPDATE files SET content = ?, file_size = ?, modified_at = ? WHERE filepath = ? OR filepath = ?", (rev_content, len(rev_content), os.path.getmtime(abs_path), abs_path, norm_path))
        try:
            cursor.execute("DELETE FROM fts_files WHERE filepath = ? OR filepath = ?", (abs_path, norm_path))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content) VALUES (?, ?, ?)", (abs_path, os.path.basename(abs_path), rev_content))
        except Exception:
            pass
        conn.commit()
        return True