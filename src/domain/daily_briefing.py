import time
import sqlite3
from typing import Dict, Any, List
from src.infrastructure.database import get_db

def generate_daily_briefing() -> Dict[str, Any]:
    """
    Synthesizes an Executive Daily Briefing across workspace documents.
    Aggregates recent files, top active tags, document count metrics, and AI summary insights.
    """
    try:
        from src.infrastructure.database import get_db, init_db
        init_db()
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Document Metrics
        cursor.execute("SELECT COUNT(*) as cnt FROM files")
        total_files = cursor.fetchone()["cnt"]

        cursor.execute("SELECT tag, COUNT(*) as cnt FROM tags GROUP BY tag ORDER BY cnt DESC LIMIT 5")
        top_tags = [{"tag": r["tag"], "count": r["cnt"]} for r in cursor.fetchall()]

        cursor.execute("SELECT filename, modified_at, filepath FROM files ORDER BY modified_at DESC LIMIT 5")
        recent_files = [{"filename": r["filename"], "filepath": r["filepath"]} for r in cursor.fetchall()]

        # Vector & Chunk Metrics
        cursor.execute("SELECT COUNT(*) as cnt FROM file_chunks")
        total_chunks = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM file_chunks WHERE embedding_json IS NOT NULL AND embedding_json != '[]'")
        total_embedded = cursor.fetchone()["cnt"]

        coverage_pct = round((total_embedded / total_chunks * 100), 1) if total_chunks > 0 else 0.0

        # Knowledge Gaps
        from src.domain.graph_reasoning import discover_knowledge_gaps
        gaps = discover_knowledge_gaps()
        missing_concepts = gaps.get("missing_concepts", [])

        # Generate Executive Highlight
        highlights = [
            f"Vault contains {total_files} active documents and {total_chunks:,} vector chunks across your workspaces.",
            f"Dense vector embedding coverage: {coverage_pct}% ({total_embedded:,}/{total_chunks:,} chunks).",
            f"Top active knowledge categories: {', '.join([t['tag'] for t in top_tags]) or 'General'}.",
            f"Latest file activity: {recent_files[0]['filename'] if recent_files else 'None'}."
        ]

        return {
            "date": time.strftime("%Y-%m-%d"),
            "total_documents": total_files,
            "total_chunks": total_chunks,
            "total_embedded": total_embedded,
            "embedding_coverage_pct": coverage_pct,
            "top_tags": top_tags,
            "recent_files": recent_files,
            "missing_concepts": missing_concepts,
            "executive_summary": " ".join(highlights),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
