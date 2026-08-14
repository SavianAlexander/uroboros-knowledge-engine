"""
Turnkey Online SQLite Database Backup, Restoration & Rotation Utility for Uroboros Knowledge Engine & Tududi Task Master.
Uses SQLite's native online C-API backup interface (conn.backup) for zero-downtime WAL backups.
"""

import os
import sys
import time
import sqlite3
import glob
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know


def backup_database(destination_path: str = None, max_backups: int = 7) -> dict:
    """Perform live online backup of knowledge.db and tududi_db/production.sqlite3 to backups/ directory."""
    know.init_db()
    backup_dir = os.path.join(PROJECT_ROOT, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    results = {}

    # 1. Backup knowledge.db
    source_know = know.DB_FILE
    target_know = destination_path or os.path.join(backup_dir, f"knowledge_backup_{timestamp}.db")
    
    if os.path.exists(source_know):
        # Truncate WAL first
        with sqlite3.connect(source_know) as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            
        src_conn = sqlite3.connect(source_know)
        dst_conn = sqlite3.connect(target_know)
        try:
            with dst_conn:
                src_conn.backup(dst_conn, pages=100, progress=None)
            results["knowledge_db"] = target_know
            print(f"[SUCCESS] Knowledge DB live backup saved to: {target_know}")
        finally:
            src_conn.close()
            dst_conn.close()

    # 2. Backup tududi production.sqlite3
    tududi_db_candidates = [
        os.path.join(PROJECT_ROOT, "tududi_db", "production.sqlite3"),
        r"C:\Users\Administrator\Desktop\Task Master\tududi_db\production.sqlite3"
    ]
    tududi_db = next((p for p in tududi_db_candidates if os.path.exists(p)), None)

    if tududi_db:
        target_tududi = os.path.join(backup_dir, f"tududi_backup_{timestamp}.sqlite3")
        with sqlite3.connect(tududi_db) as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")

        src_conn = sqlite3.connect(tududi_db)
        dst_conn = sqlite3.connect(target_tududi)
        try:
            with dst_conn:
                src_conn.backup(dst_conn, pages=100, progress=None)
            results["tududi_db"] = target_tududi
            print(f"[SUCCESS] Tududi DB live backup saved to: {target_tududi}")
        finally:
            src_conn.close()
            dst_conn.close()

    # 3. Rotate and prune old backups (keep last max_backups)
    for pattern in ["knowledge_backup_*.db", "tududi_backup_*.sqlite3"]:
        existing = sorted(glob.glob(os.path.join(backup_dir, pattern)))
        if len(existing) > max_backups:
            for old_file in existing[:-max_backups]:
                try:
                    os.remove(old_file)
                    print(f"[ROTATION] Pruned old backup snapshot: {os.path.basename(old_file)}")
                except Exception:
                    pass

    return results


def restore_database(backup_path: str) -> bool:
    """Restore target database from specified backup file."""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    is_tududi = "tududi" in os.path.basename(backup_path).lower()
    target_db = os.path.join(PROJECT_ROOT, "tududi_db", "production.sqlite3") if is_tududi else know.DB_FILE
    
    if not is_tududi:
        know.reset_db_connections()

    src_conn = sqlite3.connect(backup_path)
    dst_conn = sqlite3.connect(target_db)

    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=None)
        print(f"[SUCCESS] Database successfully restored to {target_db} from: {backup_path}")
        return True
    finally:
        src_conn.close()
        dst_conn.close()


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "backup"
    target = sys.argv[2] if len(sys.argv) > 2 else None

    if action == "backup":
        backup_database(target)
    elif action == "restore":
        if not target:
            print("Error: Restore requires backup file path argument.")
            sys.exit(1)
        restore_database(target)
    else:
        print("Usage: python scripts/backup_db.py [backup|restore] [path]")
        sys.exit(1)
