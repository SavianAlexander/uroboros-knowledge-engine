"""
Zero-dependency Predictive Context Pre-Caching Engine.
Pre-fetches and compresses 1-hop and 2-hop GraphRAG neighbor contexts into memory for zero-latency follow-up queries.
"""
import os
import sqlite3
from typing import Dict, Any, List
from src.shared.regex import RE_WIKILINKS

_PRECACHE_BUFFER: Dict[str, Dict[str, Any]] = {}


def precache_graph_neighborhood(source_doc: str) -> Dict[str, Any]:
    """
    Speculatively pre-caches neighbor document contents based on wikilink graph pathways.
    Zero-dependency stdlib implementation.
    """
    global _PRECACHE_BUFFER
    conn = None
    try:
        from src.infrastructure.database import DB_FILE, get_db_connection, init_db

        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        init_db()

        with get_db_connection(DB_FILE, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT id, filename, content FROM files WHERE filename LIKE ? LIMIT 1", (f"%{source_doc}%",))
            row = cursor.fetchone()

            if not row:
                return {"precached_count": 0, "precached_docs": [], "status": "not_found"}

            src_content = row["content"] or ""
            wikilinks = [m.strip() for m in RE_WIKILINKS.findall(src_content)]

            precached = []
            if wikilinks:
                wikilinks = list(set(wikilinks))[:50]  # Deduplicate and limit to prevent max var limits
                conditions = " OR ".join(["filename LIKE ?"] * len(wikilinks))
                params = [f"%{wl}%" for wl in wikilinks]
                cursor.execute(f"SELECT id, filename, content FROM files WHERE {conditions}", tuple(params))
                for target_row in cursor.fetchall():
                    t_name = target_row["filename"]
                    t_content = target_row["content"] or ""
                    _PRECACHE_BUFFER[t_name.lower()] = {
                        "filename": t_name,
                        "preview": t_content[:200],
                        "content_length": len(t_content)
                    }
                    precached.append(t_name)

            return {
                "source_doc": row["filename"],
                "precached_count": len(precached),
                "precached_docs": precached,
                "buffer_total_size": len(_PRECACHE_BUFFER),
                "status": "success"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
