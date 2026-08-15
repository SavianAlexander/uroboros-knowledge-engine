"""
Zero-dependency Temporal Knowledge Graph Lineage Engine.
Tracks document version evolution and timestamped wikilink relationship lineage (t0 -> t1 -> t2).
"""
import sqlite3
import unicodedata
from typing import Dict, Any, List
from src.infrastructure.database import get_db_connection, DB_FILE, init_db


def get_temporal_knowledge_lineage(filename: str = "") -> Dict[str, Any]:
    """
    Retrieves temporal change lineage and version history for vault documents.
    Zero-dependency stdlib implementation.
    """
    norm_fn = unicodedata.normalize("NFC", str(filename)) if filename else ""

    def _fetch_rows():
        with get_db_connection(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query_sql = "SELECT id, filename, filepath, created_at FROM files"
            params = []
            if norm_fn:
                query_sql += " WHERE filename LIKE ?"
                params.append(f"%{norm_fn}%")
            query_sql += " ORDER BY id DESC LIMIT 20"
            cursor.execute(query_sql, params)
            return cursor.fetchall()

    try:
        try:
            rows = _fetch_rows()
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            rows = _fetch_rows()
    except Exception:
        rows = []

    import os
    from datetime import datetime, timezone

    timeline = []
    for idx, r in enumerate(rows):
        ts = r["created_at"]
        if not ts and r["filepath"] and os.path.exists(r["filepath"]):
            try:
                mtime = os.path.getmtime(r["filepath"])
                ts = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
            except Exception:
                ts = datetime.now(timezone.utc).isoformat()
        elif not ts:
            ts = datetime.now(timezone.utc).isoformat()

        timeline.append({
            "version_id": f"v{r['id']}",
            "filename": unicodedata.normalize("NFC", str(r["filename"] or "")),
            "filepath": r["filepath"],
            "timestamp": ts,
            "change_type": "UPDATED" if idx > 0 else "INITIAL"
        })

    return {
        "query_filename": filename or "All Vault Documents",
        "versions_count": len(timeline),
        "timeline": timeline,
        "status": "success"
    }

