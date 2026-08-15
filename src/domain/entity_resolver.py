"""
Knowledge Graph Entity Disambiguation & Alias Resolver.
Maps entity variations (e.g. 'PostgreSQL', 'Postgres', 'pg_db') to canonical graph nodes.
Zero-dependency, stdlib implementation.
"""
import unicodedata

from typing import Dict, Any, List, Set, Tuple

DEFAULT_ALIAS_MAP = {
    "postgres": "PostgreSQL",
    "pg_db": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "py": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "fastapi_app": "FastAPI",
    "sqlite_db": "SQLite",
    "fts": "FTS5"
}


def resolve_canonical_entity(entity_name: str, custom_map: Dict[str, str] = None) -> str:
    """Returns the canonical entity name for a given raw entity or alias string."""
    if not entity_name:
        return ""
    norm_name = unicodedata.normalize("NFC", str(entity_name))
    clean = norm_name.strip().lower()
    mapping = {**DEFAULT_ALIAS_MAP, **(custom_map or {})}
    if clean in mapping:
        return mapping[clean]

    import os
    import sqlite3
    from src.infrastructure.database import DB_FILE, get_db_connection
    if os.path.exists(DB_FILE):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT target_tag FROM tag_aliases WHERE alias = ? LIMIT 1", (clean,))
                row = cursor.fetchone()
                if row:
                    return str(row[0])
                cursor.execute("SELECT synonym FROM synonyms WHERE word = ? LIMIT 1", (clean,))
                row2 = cursor.fetchone()
                if row2:
                    return str(row2[0])
        except Exception:
            pass

    return norm_name.strip()


def batch_resolve_entities(entities: List[str]) -> Dict[str, Any]:
    """Batch resolves entity aliases into canonical node clusters."""
    if not entities or not isinstance(entities, list):
        entities = []
    resolved_map = {}
    canonical_clusters: Dict[str, List[str]] = {}

    for e in entities:
        canonical = resolve_canonical_entity(e)
        resolved_map[e] = canonical
        if canonical not in canonical_clusters:
            canonical_clusters[canonical] = []
        if e not in canonical_clusters[canonical]:
            canonical_clusters[canonical].append(e)

    return {
        "status": "success",
        "total_input_entities": len(entities),
        "total_canonical_entities": len(canonical_clusters),
        "resolved_mapping": resolved_map,
        "clusters": canonical_clusters
    }
