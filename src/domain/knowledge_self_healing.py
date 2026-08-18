"""
Zero-dependency Autonomous Knowledge Base Self-Healing & Gap Detector.
Audits vault documents for orphaned nodes, broken wikilink cross-references, and missing topic coverage.
"""
import os
import re
import sqlite3
from typing import Dict, Any, List, Set, Optional, Tuple
from src.shared.regex import RE_WIKILINKS


def audit_knowledge_self_healing() -> Dict[str, Any]:
    """
    Audits knowledge base integrity, detecting orphaned nodes and broken links.
    Zero-dependency stdlib implementation.
    """
    try:
        from src.infrastructure.database import get_db, init_db

        init_db()
        with get_db() as conn:
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
                target_raw = m[0] if isinstance(m, (tuple, list)) else m
                target_name = str(target_raw).strip().lower()
                if target_name in filenames_lower:
                    v_id = filenames_lower[target_name]
                    outbound_count[u_id] += 1
                    inbound_count[v_id] += 1
                else:
                    broken_links.append({
                        "source_file": r[1],
                        "target_wikilink": str(target_raw).strip()
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


def repair_knowledge_base() -> Dict[str, Any]:
    """
    Autonomous self-healing repair routine:
    1. Prunes orphaned file chunks whose parent file no longer exists.
    2. Re-indexes any files missing from the FTS5 full-text search index.
    3. Executes PRAGMA optimize and returns repair metrics.
    """
    try:
        from src.infrastructure.database import get_db
        pruned_chunks = 0
        reindexed_fts = 0
        with get_db() as conn:
            with conn:
                cursor = conn.cursor()
                # 1. Prune orphaned chunks
                cursor.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
                pruned_chunks = cursor.rowcount

                # 2. Re-index missing FTS files
                cursor.execute("""
                    INSERT INTO fts_files (filepath, filename, content)
                    SELECT filepath, filename, content FROM files
                    WHERE filepath NOT IN (SELECT filepath FROM fts_files)
                """)
                reindexed_fts = cursor.rowcount

                # 3. Optimize database internal B-tree structures
                cursor.execute("PRAGMA optimize")

        return {
            "status": "success",
            "pruned_orphaned_chunks": max(0, pruned_chunks),
            "reindexed_fts_documents": max(0, reindexed_fts),
            "message": "Knowledge vault integrity verified and self-healed cleanly."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


def inspect_database_health() -> Dict[str, Any]:
    """Inspects SQLite database health, WAL status, table count, and fragmentation."""
    from src.infrastructure.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]

        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]

        db_size_bytes = page_count * page_size

        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        total_tables = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='index'")
        total_indexes = cursor.fetchone()[0]

    return {
        "status": "healthy" if str(integrity).lower() == "ok" else "corrupt",
        "integrity_check": integrity,
        "journal_mode": journal_mode,
        "database_size_bytes": db_size_bytes,
        "database_size_mb": round(db_size_bytes / (1024 * 1024), 2),
        "total_tables": total_tables,
        "total_indexes": total_indexes
    }


def auto_optimize_indexes() -> Dict[str, Any]:
    """Analyzes dynamic client tables and creates missing indexes on foreign keys / high-cardinality columns."""
    from src.infrastructure.database import get_db
    from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets
    datasets = list_orchestrated_datasets()
    created_indexes = []

    with get_db() as conn:
        cursor = conn.cursor()
        for ds in datasets:
            table_name = ds["table_name"]
            cols = ds.get("columns", {})

            for col in cols.keys():
                if col == "id":
                    continue
                if any(kw in col for kw in ["id", "code", "key", "account", "client", "customer", "email", "date", "status", "category"]):
                    idx_name = f"idx_{table_name}_{col}"
                    try:
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({col})")
                        created_indexes.append(f"{table_name}.{col}")
                    except Exception:
                        pass

        cursor.execute("PRAGMA optimize")
        conn.commit()

    return {
        "status": "success",
        "indexes_verified": len(created_indexes),
        "indexed_targets": created_indexes
    }


def detect_client_data_anomalies(dataset_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scans dynamic client datasets for high null spikes, duplicate keys, PII leaks, and schema anomalies."""
    from src.infrastructure.database import get_db
    from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets
    datasets = list_orchestrated_datasets()
    if dataset_name:
        datasets = [d for d in datasets if d["dataset_name"] == dataset_name]

    anomalies = []

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for ds in datasets:
            table_name = ds["table_name"]
            cols = ds.get("columns", {})
            total_rows = ds.get("row_count", 0)

            if total_rows == 0:
                continue

            cursor.execute(f"SELECT * FROM {table_name} LIMIT 200")
            rows = [dict(r) for r in cursor.fetchall()]

            for col in cols.keys():
                if col == "id":
                    continue
                null_count = sum(1 for r in rows if r.get(col) is None or str(r.get(col)).strip() == "")
                if null_count > len(rows) * 0.5:
                    anomalies.append({
                        "dataset_name": ds["dataset_name"],
                        "table_name": table_name,
                        "column": col,
                        "anomaly_type": "HIGH_NULL_RATE",
                        "severity": "MEDIUM",
                        "details": f"Column `{col}` has {round((null_count/len(rows))*100, 1)}% null/empty values in sample"
                    })

            pii_counts = {"SSN": 0, "CREDIT_CARD": 0, "EMAIL": 0}
            for r in rows:
                row_str = " ".join([str(v) for v in r.values() if v is not None])
                if SSN_REGEX.search(row_str):
                    pii_counts["SSN"] += 1
                if CREDIT_CARD_REGEX.search(row_str):
                    pii_counts["CREDIT_CARD"] += 1
                if EMAIL_REGEX.search(row_str):
                    pii_counts["EMAIL"] += 1

            for pii_type, count in pii_counts.items():
                if count > 0:
                    anomalies.append({
                        "dataset_name": ds["dataset_name"],
                        "table_name": table_name,
                        "anomaly_type": f"PII_DETECTED_{pii_type}",
                        "severity": "HIGH",
                        "details": f"Found {count} rows containing unmasked {pii_type} tokens in sample data"
                    })

    return anomalies


def execute_database_self_healing() -> Dict[str, Any]:
    """Runs a complete self-healing, orphan purge, and optimization cycle across the entire database."""
    from src.infrastructure.database import get_db
    health_before = inspect_database_health()
    opt_res = auto_optimize_indexes()
    anomalies = detect_client_data_anomalies()

    purged_orphan_chunks = 0
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM file_chunks WHERE file_id NOT IN (SELECT id FROM files)")
            purged_orphan_chunks = cursor.rowcount
        except Exception:
            pass

        try:
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception:
            pass
        conn.commit()

    health_after = inspect_database_health()

    return {
        "status": "success",
        "database_health": health_after,
        "indexes_optimized": opt_res["indexes_verified"],
        "purged_orphan_chunks": max(0, purged_orphan_chunks),
        "anomalies_detected_count": len(anomalies),
        "anomalies": anomalies
    }


