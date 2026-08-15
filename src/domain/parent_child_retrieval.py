"""
Zero-dependency Hierarchical Parent-Child Context Retrieval Engine.
Matches small child chunks for speed/precision, but expands to full parent document context.
"""
import os
import sqlite3
from typing import Dict, Any, List


def expand_child_chunks_to_parents(file_ids: List[int], max_chars_per_parent: int = 1500) -> List[Dict[str, Any]]:
    """
    Expands matched child file IDs into full parent document contexts.
    Zero-dependency stdlib implementation.
    """
    if not file_ids or not isinstance(file_ids, list):
        return []

    safe_max_chars = max(100, int(max_chars_per_parent)) if max_chars_per_parent is not None and isinstance(max_chars_per_parent, (int, float)) else 1500

    try:
        from src.infrastructure.database import get_db, init_db, DB_FILE

        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        safe_ids = [fid for fid in file_ids if isinstance(fid, (int, str))][:500]
        if not safe_ids:
            return []

        def _fetch_parents():
            with get_db() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in safe_ids)
                cursor.execute(f"SELECT id, filename, filepath, content FROM files WHERE id IN ({placeholders})", safe_ids)
                return cursor.fetchall()

        try:
            rows = _fetch_parents()
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            rows = _fetch_parents()

        parent_contexts = []
        for r in rows:
            content = r["content"] or ""
            truncated_content = content[:safe_max_chars] if len(content) > safe_max_chars else content
            parent_contexts.append({
                "parent_id": r["id"],
                "filename": r["filename"],
                "filepath": r["filepath"],
                "full_parent_context": truncated_content,
                "total_chars": len(content),
                "is_truncated": len(content) > safe_max_chars
            })

        return parent_contexts
    except Exception as e:
        return []
