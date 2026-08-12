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

        # Generate Executive Highlight
        highlights = [
            f"Vault contains {total_files} active documents across your workspaces.",
            f"Top active knowledge categories: {', '.join([t['tag'] for t in top_tags]) or 'General'}.",
            f"Latest file activity: {recent_files[0]['filename'] if recent_files else 'None'}."
        ]

        return {
            "date": time.strftime("%Y-%m-%d"),
            "total_documents": total_files,
            "top_tags": top_tags,
            "recent_files": recent_files,
            "executive_summary": " ".join(highlights),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
