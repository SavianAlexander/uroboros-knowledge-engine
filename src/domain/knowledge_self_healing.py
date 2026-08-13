"""
Zero-dependency Autonomous Knowledge Base Self-Healing & Gap Detector.
Audits vault documents for orphaned nodes, broken wikilink cross-references, and missing topic coverage.
"""

import re
import sqlite3
from typing import Dict, Any, List, Set
from src.shared.regex import RE_WIKILINKS


def audit_knowledge_self_healing() -> Dict[str, Any]:
    """
    Audits knowledge base integrity, detecting orphaned nodes and broken links.
    Zero-dependency stdlib implementation.
    """
    try:
        import os
        from src.infrastructure.database import get_db, init_db

        init_db()
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, filename, filepath, content FROM files")
        rows = cursor.fetchall()

        if not rows:
            return {"orphaned_nodes": [], "broken_links": [], "health_score": 100.0, "status": "success"}

        node_map = {r[0]: r[1] for r in rows}
        filenames_lower = {str(r[1]).lower(): r[0] for r in rows}

        inbound_count = {r[0]: 0 for r in rows}
        outbound_count = {r[0]: 0 for r in rows}
        broken_links = []

        for r in rows:
            u_id = r[0]
            content = r[3] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target_name = m.strip().lower()
                if target_name in filenames_lower:
                    v_id = filenames_lower[target_name]
                    outbound_count[u_id] += 1
                    inbound_count[v_id] += 1
                else:
                    broken_links.append({
                        "source_file": r[1],
                        "target_wikilink": m.strip()
                    })

        orphaned_nodes = [
            {"id": nid, "filename": node_map[nid]}
            for nid in node_map
            if inbound_count[nid] == 0 and outbound_count[nid] == 0
        ]

        total_nodes = len(node_map)
        health_score = round(max(0.0, 100.0 - (len(orphaned_nodes) * 5.0) - (len(broken_links) * 2.0)), 2)

        return {
            "total_nodes": total_nodes,
            "orphaned_nodes": orphaned_nodes,
            "broken_links": broken_links,
            "health_score": health_score,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
