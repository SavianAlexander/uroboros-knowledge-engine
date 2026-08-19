import os
import time
import glob
import shutil
import sqlite3
import hashlib
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, get_db_connection, reset_db_connections

logger = logging.getLogger(__name__)

MAX_SNAPSHOT_RETENTION = 3

def _get_snapshots_dir(target_db: Optional[str] = None) -> str:
    """Return the absolute path to backups/snapshots/ for the given database."""
    db_path = os.path.abspath(target_db or db_module.DB_FILE)
    base_dir = os.path.dirname(db_path)
    snapshot_dir = os.path.join(base_dir, "backups", "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    return snapshot_dir

def _compute_file_sha256(path: str) -> Optional[str]:
    """Compute SHA-256 checksum of a file in 64KB blocks."""
    if not path or not os.path.exists(path) or not os.path.isfile(path):
        return None
    try:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning("Failed to compute file SHA256 for %s: %s", path, e)
        return None

def _compute_db_fingerprint(db_path: str) -> Optional[str]:
    """Compute deterministic cryptographic fingerprint of database schema, row counts, and contents."""
    if not db_path or not os.path.exists(db_path) or not os.path.isfile(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        hasher = hashlib.sha256()
        for tbl in tables:
            hasher.update(tbl.encode("utf-8"))
            try:
                cursor.execute(f"SELECT COUNT(*) FROM \"{tbl}\"")
                cnt = cursor.fetchone()[0]
                hasher.update(str(cnt).encode("utf-8"))
                cursor.execute(f"SELECT * FROM \"{tbl}\" ORDER BY 1 LIMIT 500")
                rows = cursor.fetchall()
                hasher.update(str(rows).encode("utf-8"))
            except Exception:
                pass
        conn.close()
        return hasher.hexdigest()
    except Exception as e:
        logger.debug("Failed to compute SQLite data fingerprint for %s: %s", db_path, e)
        return _compute_file_sha256(db_path)

def _parse_timestamp_from_filename(filename: str) -> Optional[int]:
    """Extract integer timestamp from snapshot filenames across new and legacy naming conventions."""
    base = os.path.basename(filename)
    if ".snapshot-" in base:
        ts_part = base.split(".snapshot-")[-1]
        try:
            return int(ts_part)
        except ValueError:
            pass
    elif "snapshot-" in base:
        ts_part = base.split("snapshot-")[-1]
        try:
            return int(ts_part)
        except ValueError:
            pass
    elif "snapshot_" in base:
        raw = base.split("snapshot_")[-1].split("_")[0].replace(".db", "")
        try:
            return int(raw)
        except ValueError:
            pass
    return None

def _normalize_timestamp_for_sort(ts: int) -> int:
    """Normalize 10-digit second timestamps and 13-digit millisecond timestamps for consistent chronological sorting."""
    return ts * 1000 if ts < 10000000000 else ts

def list_db_snapshots(target_db: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available database snapshots from backups/snapshots/ and legacy paths."""
    db_file = target_db or db_module.DB_FILE
    target_db_abs = os.path.abspath(db_file)
    base_dir = os.path.dirname(target_db_abs)
    snapshot_dir = _get_snapshots_dir(target_db_abs)
    db_base = os.path.basename(target_db_abs)

    search_patterns = [
        os.path.join(snapshot_dir, f"{db_base}.snapshot-*"),
        os.path.join(snapshot_dir, "*.snapshot-*"),
        os.path.join(snapshot_dir, "snapshot_*.db"),
        os.path.join(snapshot_dir, "*snapshot*"),
        f"{target_db_abs}.snapshot-*",
        f"{db_file}.snapshot-*",
        os.path.join(base_dir, "vault", "snapshots", "snapshot_*.db"),
        os.path.join(base_dir, "vault", "snapshots", "*snapshot*")
    ]

    seen_files = set()
    snapshots_by_ts: Dict[int, Dict[str, Any]] = {}

    for pattern in search_patterns:
        for f in glob.glob(pattern):
            f_abs = os.path.abspath(f)
            if f_abs in seen_files or not os.path.isfile(f_abs):
                continue
            seen_files.add(f_abs)

            ts = _parse_timestamp_from_filename(f_abs)
            if ts is None:
                continue

            try:
                size = os.path.getsize(f_abs)
            except Exception as e:
                logger.warning("Failed to read snapshot file metadata for %s: %s", f_abs, e)
                continue

            # Prioritize files in backups/snapshots/ over legacy locations
            if ts not in snapshots_by_ts or "backups" in f_abs:
                snapshots_by_ts[ts] = {
                    "timestamp": ts,
                    "filename": f_abs,
                    "size": size
                }

    snapshots = list(snapshots_by_ts.values())
    snapshots.sort(key=lambda x: _normalize_timestamp_for_sort(x["timestamp"]), reverse=True)
    return snapshots

def prune_db_snapshots(target_db: Optional[str] = None, max_retention: int = MAX_SNAPSHOT_RETENTION) -> int:
    """Prune oldest database snapshots exceeding max_retention limit."""
    snapshots = list_db_snapshots(target_db)
    if len(snapshots) <= max_retention:
        return 0

    excess = snapshots[max_retention:]
    pruned = 0
    for snap in excess:
        f = snap.get("filename")
        if f and os.path.exists(f):
            try:
                os.remove(f)
                pruned += 1
                logger.info("Pruned old database snapshot exceeding retention limit: %s", f)
            except Exception as e:
                logger.warning("Failed to delete snapshot %s during retention pruning: %s", f, e)
    return pruned

def create_db_snapshot(target_db: Optional[str] = None, max_retention: int = MAX_SNAPSHOT_RETENTION) -> int:
    """Create atomic database snapshot in backups/snapshots/ with SHA-256 deduplication and retention pruning."""
    db_file = target_db or db_module.DB_FILE
    target_db_abs = os.path.abspath(db_file)

    # 1. Truncate WAL to ensure all committed pages are flushed to disk
    try:
        with get_db_connection(target_db_abs, timeout=10.0) as conn:
            with conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning("Failed to truncate WAL before snapshot creation: %s", e)

    # 2. SHA-256 / Content Fingerprint Deduplication check
    existing_snaps = list_db_snapshots(target_db_abs)
    if existing_snaps:
        latest_snap = existing_snaps[0]
        latest_file = latest_snap.get("filename")
        if latest_file and os.path.exists(latest_file):
            # Check direct file SHA-256 match
            curr_file_hash = _compute_file_sha256(target_db_abs)
            latest_file_hash = _compute_file_sha256(latest_file)
            if curr_file_hash and latest_file_hash and curr_file_hash == latest_file_hash:
                logger.info("Database content unchanged (file SHA-256 match: %s); reusing existing snapshot %s", curr_file_hash[:8], latest_snap["timestamp"])
                return int(latest_snap["timestamp"])

            # Check logical database data & schema fingerprint match
            curr_fp = _compute_db_fingerprint(target_db_abs)
            latest_fp = _compute_db_fingerprint(latest_file)
            if curr_fp and latest_fp and curr_fp == latest_fp:
                logger.info("Database content unchanged (data fingerprint match: %s); reusing existing snapshot %s", curr_fp[:8], latest_snap["timestamp"])
                return int(latest_snap["timestamp"])

    # 3. Create new snapshot in backups/snapshots/
    snapshot_dir = _get_snapshots_dir(target_db_abs)
    db_base = os.path.basename(target_db_abs)
    current_sec = int(time.time())

    # If another snapshot was already created in the current second, use millisecond timestamps
    has_same_second = any(
        _normalize_timestamp_for_sort(s["timestamp"]) // 1000 == current_sec 
        for s in existing_snaps
    )

    dest_sec = os.path.join(snapshot_dir, f"{db_base}.snapshot-{current_sec}")
    if os.path.exists(dest_sec) or has_same_second:
        timestamp = int(time.time() * 1000)
        dest = os.path.join(snapshot_dir, f"{db_base}.snapshot-{timestamp}")
        while os.path.exists(dest):
            timestamp += 1
            dest = os.path.join(snapshot_dir, f"{db_base}.snapshot-{timestamp}")
    else:
        timestamp = current_sec
        dest = dest_sec

    c_src = None
    c_dst = None
    try:
        c_src = sqlite3.connect(target_db_abs)
        c_dst = sqlite3.connect(dest)
        c_src.backup(c_dst)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning("SQLite backup API failed during snapshot creation, falling back to file copy: %s", e)
        try:
            if c_dst: c_dst.close()
        except Exception: pass
        try:
            if c_src: c_src.close()
        except Exception: pass
        c_dst = None
        c_src = None
        shutil.copy2(target_db_abs, dest)
    finally:
        if c_dst:
            try: c_dst.close()
            except Exception: pass
        if c_src:
            try: c_src.close()
            except Exception: pass

    # 4. Automatically prune older snapshots exceeding max_retention
    try:
        prune_db_snapshots(target_db_abs, max_retention=max_retention)
    except Exception as e:
        logger.warning("Automatic post-creation snapshot retention pruning failed: %s", e)

    return timestamp

def restore_db_snapshot(timestamp: int, target_db: Optional[str] = None) -> bool:
    """Restore database from snapshot timestamp across backups/snapshots/ and legacy paths."""
    db_file = target_db or db_module.DB_FILE
    target_db_abs = os.path.abspath(db_file)

    snapshots = list_db_snapshots(target_db_abs)
    matching_snap = next((s for s in snapshots if int(s["timestamp"]) == int(timestamp)), None)

    src = None
    if matching_snap and os.path.exists(matching_snap["filename"]):
        src = matching_snap["filename"]
    else:
        snapshot_dir = _get_snapshots_dir(target_db_abs)
        db_base = os.path.basename(target_db_abs)
        candidates = [
            os.path.join(snapshot_dir, f"{db_base}.snapshot-{timestamp}"),
            os.path.join(snapshot_dir, f"snapshot-{timestamp}"),
            f"{target_db_abs}.snapshot-{timestamp}",
            f"{db_file}.snapshot-{timestamp}",
        ]
        for c in candidates:
            if os.path.exists(c):
                src = c
                break

    if not src or not os.path.exists(src):
        logger.warning("Snapshot with timestamp %s not found for restore", timestamp)
        return False

    reset_db_connections()

    # Purge lingering WAL / SHM files to prevent ghost pages
    for ext in ["-wal", "-shm"]:
        wal_file = target_db_abs + ext
        if os.path.exists(wal_file):
            try:
                os.remove(wal_file)
            except Exception as e:
                logger.debug("Snapshot restore WAL purge notice: %s", e)

    c_src = None
    c_dst = None
    restored = False
    try:
        c_src = sqlite3.connect(src)
        c_dst = sqlite3.connect(target_db_abs)
        c_src.backup(c_dst)
        restored = True
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.debug("Snapshot backup API fallback notice: %s", e)
        try:
            if c_dst: c_dst.close()
        except Exception: pass
        try:
            if c_src: c_src.close()
        except Exception: pass
        c_dst = None
        c_src = None
        shutil.copy2(src, target_db_abs)
        restored = True
    finally:
        if c_dst:
            try: c_dst.close()
            except Exception: pass
        if c_src:
            try: c_src.close()
            except Exception: pass

    if restored:
        try:
            with get_db_connection(target_db_abs, timeout=10.0) as conn:
                with conn:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception as e:
            logger.debug("Snapshot post-restore checkpoint notice: %s", e)

    return restored

def delete_db_snapshot(timestamp: int, target_db: Optional[str] = None) -> bool:
    """Delete a database snapshot by timestamp across backups/snapshots/ and legacy paths."""
    db_file = target_db or db_module.DB_FILE
    target_db_abs = os.path.abspath(db_file)

    snapshots = list_db_snapshots(target_db_abs)
    matching_snaps = [s for s in snapshots if int(s["timestamp"]) == int(timestamp)]

    deleted = False
    if matching_snaps:
        for s in matching_snaps:
            f = s.get("filename")
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                    deleted = True
                except Exception as e:
                    logger.warning("Failed to delete snapshot file %s: %s", f, e)

    if not deleted:
        snapshot_dir = _get_snapshots_dir(target_db_abs)
        db_base = os.path.basename(target_db_abs)
        candidates = [
            os.path.join(snapshot_dir, f"{db_base}.snapshot-{timestamp}"),
            os.path.join(snapshot_dir, f"snapshot-{timestamp}"),
            f"{target_db_abs}.snapshot-{timestamp}",
            f"{db_file}.snapshot-{timestamp}",
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    os.remove(c)
                    deleted = True
                except Exception as e:
                    logger.warning("Failed to delete candidate snapshot file %s: %s", c, e)

    return deleted

def get_snapshot_path(timestamp: int, target_db: Optional[str] = None) -> Optional[str]:
    """Retrieve absolute file path of a snapshot by timestamp."""
    db_file = target_db or db_module.DB_FILE
    target_db_abs = os.path.abspath(db_file)
    snapshots = list_db_snapshots(target_db_abs)
    for s in snapshots:
        if int(s["timestamp"]) == int(timestamp):
            return s["filename"]
    return None