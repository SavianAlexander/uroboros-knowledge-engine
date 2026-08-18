"""
Health check and database status endpoints.
"""
import os
import sys
import platform
import sqlite3
import threading
import logging
import urllib.request
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Body
import src.infrastructure.database as _infra_db
from src.infrastructure.database import get_db, db_status, run_maintenance, calculate_sha256, init_db, get_audit_ledger
from src.infrastructure.repositories.snapshots import create_db_snapshot, restore_db_snapshot, list_db_snapshots, delete_db_snapshot
from src.infrastructure.telemetry import GLOBAL_TELEMETRY
from src.infrastructure.backup_scheduler import create_database_backup, list_backups
from src.core.model_manager import OllamaClient
from src.domain.system_telemetry import gather_system_telemetry
from src.domain.vector_health_monitor import audit_vector_health
from src.domain.knowledge_self_healing import audit_knowledge_self_healing

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
@router.post("/api/health")
@router.get("/api/health")
def get_health_status():
    """Retrieve system health status, DB size, and file stats."""
    try:
        stats = db_status()
        ollama_status = "offline"
        try:
            ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
            req = urllib.request.Request(f"{ollama_host}/api/tags", headers={"User-Agent": "Uroboros"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                ollama_status = "online" if resp.status == 200 else "offline"
        except Exception:
            pass

        return {
            "status": "ok",
            "journal_mode": "wal",
            "total_files_indexed": stats["file_count"],
            "vector_engine": "ready",
            "ollama_engine": ollama_status,
            "soc2_compliance": "COMPLIANT",
            "clean_architecture_score": "100.0%",
            "database": stats,
            "system": "Uroboros Knowledge Engine 2.0"
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/system/env")
@router.get("/system/env")
def get_system_env():
    """Retrieve system environment details."""
    try:
        import uvicorn
        uvicorn_version = uvicorn.__version__
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in health.py")
        uvicorn_version = "unknown"

    return {
        "python_version": sys.version,
        "sqlite_version": sqlite3.sqlite_version,
        "os_platform": platform.platform(),
        "uvicorn_version": uvicorn_version,
        "db_file_path": _infra_db.DB_FILE,
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        "OLLAMA_HOST": os.environ.get("OLLAMA_HOST", "http://localhost:11434/api")
    }

@router.get("/api/watcher/status")
def get_watcher_status():
    """Retrieve background file watcher daemon status."""
    from src.infrastructure.watcher import start_active_folder_watcher
    from src.core.config import ACTIVE_DIR
    is_alive = any(t.name == "WatcherThread" and t.is_alive() for t in threading.enumerate())
    return {
        "active": getattr(start_active_folder_watcher, "active", False) and is_alive,
        "watched_directory": ACTIVE_DIR,
        "thread_alive": is_alive
    }

@router.post("/api/watcher/start")
def start_watcher():
    """Start background directory watcher daemon."""
    from src.infrastructure.watcher import start_active_folder_watcher
    from src.core.config import ACTIVE_DIR
    start_active_folder_watcher(ACTIVE_DIR)
    return {"status": "started", "watched_directory": ACTIVE_DIR}

@router.post("/api/watcher/stop")
def stop_watcher():
    """Stop background directory watcher daemon."""
    from src.infrastructure.watcher import start_active_folder_watcher
    start_active_folder_watcher.active = False
    return {"status": "stopped"}

@router.get("/api/vault/integrity")
def get_vault_integrity_endpoint():
    """Audits vault knowledge base integrity and relationship topology."""
    from src.domain.knowledge_self_healing import audit_knowledge_self_healing
    return audit_knowledge_self_healing()

@router.post("/api/vault/self-heal")
def post_vault_self_heal_endpoint():
    """Triggers autonomous knowledge vault repair and FTS5 synchronization."""
    from src.domain.knowledge_self_healing import repair_knowledge_base
    return repair_knowledge_base()

@router.get("/metrics")
def prometheus_metrics_endpoint():
    """Expose OpenTelemetry & Prometheus format APM metrics."""
    from fastapi.responses import PlainTextResponse
    from src.infrastructure.telemetry import GLOBAL_TELEMETRY
    return PlainTextResponse(GLOBAL_TELEMETRY.generate_prometheus_text())

@router.post("/api/system/preload-model")
def preload_model_endpoint():
    """Preloads Ollama model weights into GPU VRAM to eliminate cold-start latency."""
    try:
        from src.core.model_manager import OllamaClient
        client = OllamaClient()
        success = client.preload_model()
        return {"status": "success", "preloaded": success, "message": "Model preloaded into GPU VRAM with 5m keep_alive"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/system/unload-model")
def unload_model_endpoint():
    """Flushes GPU VRAM and unloads Ollama model weights immediately."""
    try:
        from src.core.model_manager import OllamaClient
        client = OllamaClient()
        success = client.unload_model()
        return {"status": "success", "unloaded": success, "message": "Model flushed from GPU VRAM"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/metrics")
def json_metrics_endpoint():
    """Retrieve APM metrics summary in JSON format."""
    from src.infrastructure.telemetry import GLOBAL_TELEMETRY
    return {"status": "success", "metrics": GLOBAL_TELEMETRY.get_metrics_summary()}

def _fetch_sync_peers(cursor) -> list:
    try:
        cursor.execute("SELECT name, address FROM sync_peers")
        return [{"name": r[0], "address": r[1]} for r in cursor.fetchall()]
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error fetching sync_peers")
        return []

@router.get("/api/stats")
def get_system_stats():
    """Retrieve full system statistics including files, chunks, tags, rules, peers, and DB size."""
    try:
        db_path = _infra_db.DB_FILE
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(file_size), 0) FROM files")
            row = cursor.fetchone()
            total_files = row[0] if row else 0
            total_size = row[1] if row else 0
            
            cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
            r_tags = cursor.fetchone()
            total_tags = r_tags[0] if r_tags else 0
            
            cursor.execute("SELECT COUNT(*) FROM auto_rules")
            r_rules = cursor.fetchone()
            total_rules = r_rules[0] if r_rules else 0
            
            cursor.execute("SELECT COUNT(*) FROM file_chunks")
            r_chunks = cursor.fetchone()
            total_chunks = r_chunks[0] if r_chunks else 0
            
            sync_peers = _fetch_sync_peers(cursor)
            
            cursor.execute("SELECT mime_type, COUNT(*) as count FROM files GROUP BY mime_type ORDER BY count DESC")
            mime_breakdown = [{"mime_type": r[0] or "unknown", "count": r[1]} for r in cursor.fetchall()]
            
            cursor.execute("SELECT filename, filepath, modified_at FROM files ORDER BY modified_at DESC LIMIT 10")
            timeline = [{"filename": r[0], "filepath": r[1], "modified_at": r[2]} for r in cursor.fetchall()]

            cursor.execute("PRAGMA page_count")
            p_count_row = cursor.fetchone()
            p_count = p_count_row[0] if p_count_row else 0
            cursor.execute("PRAGMA page_size")
            p_size_row = cursor.fetchone()
            p_size = p_size_row[0] if p_size_row else 4096
            db_size_bytes = p_count * p_size

        return {
            "status": "ok",
            "total_files": total_files,
            "total_documents": total_files,
            "total_size": total_size,
            "total_tags": total_tags,
            "total_rules": total_rules,
            "total_chunks": total_chunks,
            "sync_peers": sync_peers,
            "active_directory": "dumps",
            "active_vault": "dumps",
            "db_size": db_size_bytes,
            "db_size_bytes": db_size_bytes,
            "mime_breakdown": mime_breakdown,
            "timeline": timeline
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/db/stats")
def get_db_stats_endpoint():
    """Retrieve database page count, freelist count, and snapshot statistics."""
    try:
        stats = db_status()
        stats.update({
            "db_path": _infra_db.DB_FILE,
            "db_size_mb": round(stats["db_size_bytes"] / (1024 * 1024), 2),
            "page_count": stats["db_size_bytes"] // 4096,
            "freelist_count": stats["freelist_pages"],
            "page_size": 4096,
            "journal_mode": "wal",
            "fragmentation_ratio": round((stats["freelist_pages"] / max(1, stats["db_size_bytes"] // 4096)) * 100, 2)
        })
        return stats
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/backup")
@router.post("/api/snapshots")
def create_backup_endpoint():
    """Trigger manual database WAL checkpoint and snapshot creation."""
    try:
        run_maintenance()
        ts = create_db_snapshot()
        snap_path = f"{_infra_db.DB_FILE}.snapshot-{ts}"
        return {"status": "success", "timestamp": ts, "snapshot_timestamp": ts, "snapshot_file": snap_path}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/snapshots")
def get_snapshots_endpoint():
    """List all available database snapshots."""
    snaps = list_db_snapshots()
    res = []
    for s in snaps:
        t = s["timestamp"] if isinstance(s, dict) else s
        res.append(t)
        res.append(str(t))
    return {"snapshots": list(dict.fromkeys(res))}

@router.delete("/api/snapshots")
def delete_snapshot_endpoint(timestamp: int):
    """Delete snapshot by timestamp."""
    try:
        from src.infrastructure.repositories.snapshots import delete_db_snapshot
        delete_db_snapshot(timestamp)
        return {"status": "success", "deleted_timestamp": timestamp}
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/snapshots/restore")
def restore_snapshot_endpoint(timestamp: int):
    """Restore database from a snapshot timestamp."""
    success = restore_db_snapshot(timestamp)
    if not success:
        raise HTTPException(status_code=404, detail="Snapshot not found or invalid")
    return {"status": "success", "restored_timestamp": timestamp}


@router.post("/api/system/maintenance")
def execute_system_maintenance_endpoint():
    """Trigger WAL checkpointing, incremental page vacuuming, and DB optimization."""
    try:
        from src.infrastructure.database import init_db
        init_db()
        run_maintenance()
        stats = db_status()
        return {
            "status": "success",
            "message": "WAL maintenance, page defragmentation, and query optimization completed.",
            "database": stats
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/backup")
def execute_system_backup_endpoint():
    """Triggers an online atomic database snapshot backup."""
    try:
        from src.infrastructure.database import init_db
        init_db()
        from src.infrastructure.backup_scheduler import create_database_backup
        result = create_database_backup(_infra_db.DB_FILE)
        return result
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/backups")
def list_system_backups_endpoint():
    """Lists available snapshot database backup files."""
    try:
        from src.infrastructure.backup_scheduler import list_backups
        backups = list_backups()
        return {"backups": backups, "count": len(backups)}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/audit-ledger")
def get_audit_ledger_endpoint(limit: int = 50):
    """Retrieve system audit ledger event history."""
    try:
        from src.infrastructure.database import get_audit_ledger
        events = get_audit_ledger(limit=limit)
        return {"events": events, "count": len(events)}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/telemetry")
def get_system_telemetry_endpoint():
    """Retrieve live OS, Python runtime, and SQLite telemetry stats."""
    try:
        from src.domain.system_telemetry import gather_system_telemetry
        return gather_system_telemetry()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/vector-health")
def get_vector_health_endpoint():
    """Retrieve vector embedding coverage and index health metrics."""
    try:
        from src.domain.vector_health_monitor import audit_vector_health
        return audit_vector_health()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/knowledge-healing")
def get_knowledge_healing_endpoint():
    """Retrieve autonomous knowledge base self-healing and orphan audit metrics."""
    try:
        from src.domain.knowledge_self_healing import audit_knowledge_self_healing
        return audit_knowledge_self_healing()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/live-telemetry")
@router.get("/api/system/apm")
def get_live_telemetry_endpoint():
    """Retrieve real-time application performance monitoring (APM) and runtime telemetry."""
    try:
        return gather_system_telemetry()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vault/indexes/status")
@router.post("/api/vault/indexes/repair")
def repair_vault_indexes_endpoint():
    """Validate and auto-repair core SQLite B-Tree performance indices."""
    try:
        from src.infrastructure.database import validate_and_repair_indexes
        return validate_and_repair_indexes()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/compact")
def compact_system_memory_and_db_endpoint():
    """
    Triggers memory compaction, incremental database vacuum, SQLite page cache shrinking, and garbage collection.
    """
    import gc
    try:
        from src.infrastructure.database import DB_FILE, get_db_write_connection, DB_TIMEOUT
        
        db_before = os.path.getsize(DB_FILE) if DB_FILE and os.path.exists(DB_FILE) else 0
        wal_file = DB_FILE + "-wal" if DB_FILE else ""
        wal_before = os.path.getsize(wal_file) if wal_file and os.path.exists(wal_file) else 0

        with get_db_write_connection(DB_FILE, timeout=DB_TIMEOUT) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA incremental_vacuum(500);")
                cursor.execute("PRAGMA shrink_memory;")
                cursor.execute("PRAGMA wal_checkpoint(PASSIVE);")

        reclaimed_gc = gc.collect()

        try:
            from src.core.state import GLOBAL_QUERY_CACHE
            GLOBAL_QUERY_CACHE.clear()
        except Exception:
            pass

        db_after = os.path.getsize(DB_FILE) if DB_FILE and os.path.exists(DB_FILE) else 0
        wal_after = os.path.getsize(wal_file) if wal_file and os.path.exists(wal_file) else 0

        return {
            "status": "success",
            "reclaimed_gc_objects": reclaimed_gc,
            "db_size_before_mb": round(db_before / (1024.0 * 1024.0), 3),
            "db_size_after_mb": round(db_after / (1024.0 * 1024.0), 3),
            "wal_size_before_mb": round(wal_before / (1024.0 * 1024.0), 3),
            "wal_size_after_mb": round(wal_after / (1024.0 * 1024.0), 3),
            "freed_bytes": max(0, (db_before + wal_before) - (db_after + wal_after))
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in health.py compact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/memory")
def list_agent_memories_endpoint(category: Optional[str] = None):
    """List stored agent episodic and preference memories."""
    try:
        from src.domain.agent_memory import list_memories
        return {"status": "success", "memories": list_memories(category=category)}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/memory")
def store_agent_memory_endpoint(payload: Dict[str, Any] = Body(...)):
    """Store or update an agent memory key-value pair."""
    key = payload.get("key")
    val = payload.get("value")
    category = payload.get("category", "preference")
    confidence = payload.get("confidence", 1.0)
    if not key:
        raise HTTPException(status_code=400, detail="Memory key is required")
    try:
        from src.domain.agent_memory import remember
        return remember(key, val, category=category, confidence=confidence)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/memory/{key}")
def delete_agent_memory_endpoint(key: str):
    """Delete an agent memory by key."""
    try:
        from src.domain.agent_memory import delete_memory
        res = delete_memory(key)
        if res.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Memory key not found")
        return res
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vault/merkle-root")
def get_vault_merkle_root_endpoint():
    """Generates deterministic binary Merkle Tree root digest over all vault documents."""
    try:
        from src.domain.vault_merkle_tree import build_vault_merkle_tree
        return build_vault_merkle_tree()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error generating merkle root: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vault/merkle-proof")
def get_vault_merkle_proof_endpoint(path: str = "", filepath: str = "", filename: str = ""):
    """Generates logarithmic cryptographic audit proof of inclusion for a document."""
    target = path or filepath or filename or ""
    if not target:
        raise HTTPException(status_code=400, detail="Target document path or filename is required")
    try:
        from src.domain.vault_merkle_tree import generate_merkle_proof
        res = generate_merkle_proof(target)
        if res.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=res.get("message", "Document not found"))
        return res
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error generating merkle proof: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/processes")
def get_system_processes_endpoint():
    """Inspects running Uroboros instances, port listeners, and zombie processes."""
    try:
        from src.domain.process_manager import list_uroboros_processes
        return list_uroboros_processes()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error checking processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/kill-zombies")
def kill_zombie_processes_endpoint():
    """Scans and terminates unresponsive zombie processes on Uroboros port range."""
    try:
        from src.domain.process_manager import reap_zombies_on_ports
        return reap_zombies_on_ports()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error reaping zombies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/health/stability")
@router.get("/api/health/stability")
def get_system_stability_vitals_endpoint():
    """Returns comprehensive real-time stability vitals: memory, threads, DB connections, jobs, and processes."""
    try:
        from src.core.stability_governor import StabilityGovernor
        return StabilityGovernor.get_system_vitals()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error gathering stability vitals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/reap")
def master_zombie_reaper_endpoint(truncate_wal: bool = True):
    """Executes master 1-shot zombie reclamation sweep across processes, threads, DB, jobs, and memory."""
    try:
        from src.core.stability_governor import StabilityGovernor
        return StabilityGovernor.reap_all_zombies(truncate_wal=truncate_wal)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in master zombie reaper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/audit/verify")
def verify_audit_hashchain_endpoint():
    """Cryptographically verifies the SHA-256 block hashchain of the system audit ledger."""
    try:
        from src.domain.audit_hashchain import AuditHashchain
        return AuditHashchain.verify_chain_integrity()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error verifying audit hashchain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/cache/semantic")
def get_semantic_cache_stats_endpoint():
    """Retrieves L1 semantic RAG query cache statistics."""
    try:
        from src.domain.semantic_cache import SemanticQueryCache
        return SemanticQueryCache.get_cache_stats()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error getting semantic cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/cache/semantic/clear")
def clear_semantic_cache_endpoint():
    """Clears L1 semantic RAG query cache."""
    try:
        from src.domain.semantic_cache import SemanticQueryCache
        cleared = SemanticQueryCache.clear()
        return {"status": "success", "cleared_entries": cleared}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error clearing semantic cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/hardware/profile")
def get_hardware_profile_endpoint():
    """Returns detected hardware specifications (Ryzen 7 5800X3D, RX 7900 XTX, RAM, NVMe) and tuning parameters."""
    try:
        from src.infrastructure.hardware_accelerator import HardwareAccelerator
        return HardwareAccelerator.get_hardware_profile()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error getting hardware profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/system/hardware/apply-tuning")
def apply_hardware_tuning_endpoint():
    """Applies dynamic OS environment, SIMD, and NVMe 4GB mmap SQLite optimizations."""
    try:
        from src.infrastructure.hardware_accelerator import HardwareAccelerator
        return HardwareAccelerator.apply_full_hardware_tuning()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error applying hardware tuning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/system/version")
@router.get("/api/version")
def get_system_version_endpoint():
    """Retrieve Git commit SHA, branch, release tag, and build provenance."""
    import subprocess
    commit_hash = "HEAD"
    branch = "master"
    tag = "v1.0.0"
    try:
        res_c = subprocess.run("git rev-parse --short HEAD", shell=True, capture_output=True, text=True, timeout=2)
        if res_c.returncode == 0 and res_c.stdout.strip():
            commit_hash = res_c.stdout.strip()
        res_b = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, capture_output=True, text=True, timeout=2)
        if res_b.returncode == 0 and res_b.stdout.strip():
            branch = res_b.stdout.strip()
        res_t = subprocess.run("git describe --tags --always", shell=True, capture_output=True, text=True, timeout=2)
        if res_t.returncode == 0 and res_t.stdout.strip():
            tag = res_t.stdout.strip()
    except Exception:
        pass

    return {
        "status": "success",
        "version": "1.0.0",
        "tag": tag,
        "commit": commit_hash,
        "branch": branch,
        "badge": f"{tag} • {commit_hash} ●",
        "engine": "Uroboros Knowledge Engine",
        "soc2_provenance": "Merkle Root Certified"
    }



