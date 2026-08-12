import sqlite3
from typing import Dict, Any, List
from src.infrastructure.database import get_db
from src.shared.regex import RE_WIKILINKS

def discover_knowledge_gaps() -> Dict[str, Any]:
    """
    Knowledge Graph Reasoning & Gap Finder Engine.
    Identifies 'Orphan Nodes' (unlinked documents) and 'Missing Concepts'
    (wikilinks referencing non-existent documents in vault).
    """
    try:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT id, filename, filepath, content FROM files")
        rows = cursor.fetchall()

        file_titles = set(r["filename"].lower() for r in rows)
        unlinked_wikilinks = set()
        orphan_files = []

        for r in rows:
            content = r["content"] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target = m.strip().lower()
                if target and not any(target in ft for ft in file_titles):
                    unlinked_wikilinks.add(m.strip())

        # Find orphan files (zero tags and zero wikilinks)
        cursor.execute("SELECT f.id, f.filename, f.filepath FROM files f WHERE f.id NOT IN (SELECT file_id FROM tags)")
        orphan_rows = cursor.fetchall()
        orphan_files = [{"id": r["id"], "filename": r["filename"]} for r in orphan_rows[:5]]

        return {
            "missing_concepts": sorted(list(unlinked_wikilinks))[:10],
            "orphan_documents": orphan_files,
            "gap_count": len(unlinked_wikilinks),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
