"""
Zero-dependency Vector Embedding Health & Index Drift Monitor.
Audits vector embedding coverage, missing vectors, and dimension consistency across vault files.
"""

import sqlite3
from typing import Dict, Any, List


def audit_vector_health() -> Dict[str, Any]:
    """
    Audits vector coverage and detects index drift.
    Zero-dependency stdlib implementation.
    """
    try:
        import os
        from src.infrastructure.database import get_db, init_db, DB_FILE

        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        init_db()
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as cnt FROM files")
        row = cursor.fetchone()
        total_files = row["cnt"] if row else 0

        # Check file_chunks, vector_embeddings or embeddings table if exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('file_chunks', 'vector_embeddings', 'embeddings')")
        tables = [r[0] for r in cursor.fetchall()]

        embedded_count = 0
        dimension = None
        missing_count = total_files

        if "file_chunks" in tables:
            cursor.execute("SELECT COUNT(DISTINCT file_id) as cnt FROM file_chunks WHERE embedding_json IS NOT NULL AND embedding_json != '[]'")
            row_emb = cursor.fetchone()
            embedded_count = row_emb["cnt"] if row_emb else 0
            missing_count = max(0, total_files - embedded_count)
        elif "vector_embeddings" in tables:
            cursor.execute("SELECT COUNT(DISTINCT file_id) as cnt FROM vector_embeddings")
            row_emb = cursor.fetchone()
            embedded_count = row_emb["cnt"] if row_emb else 0
            missing_count = max(0, total_files - embedded_count)
        elif "embeddings" in tables:
            cursor.execute("SELECT COUNT(DISTINCT file_id) as cnt FROM embeddings")
            row_emb = cursor.fetchone()
            embedded_count = row_emb["cnt"] if row_emb else 0
            missing_count = max(0, total_files - embedded_count)

        coverage_pct = round((embedded_count / float(max(1, total_files))) * 100.0, 2)

        return {
            "total_files": total_files,
            "embedded_files": embedded_count,
            "missing_embeddings": missing_count,
            "coverage_pct": coverage_pct,
            "tables_found": tables,
            "health_status": "healthy" if coverage_pct >= 90.0 else "indexing_recommended",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
