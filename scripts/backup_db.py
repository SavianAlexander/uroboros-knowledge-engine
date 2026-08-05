"""
Turnkey Online SQLite Database Backup & Restoration Utility for Uroboros Knowledge Engine.
Uses SQLite's native online C-API backup interface (conn.backup) for zero-downtime WAL backups.
"""

import os
import sys
import time
import sqlite3
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know


def backup_database(destination_path: str = None) -> str:
    """Perform live online backup of knowledge.db to destination_path."""
    know.init_db()
    source_db = know.DB_FILE

    if not destination_path:
        backup_dir = os.path.join(PROJECT_ROOT, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        destination_path = os.path.join(backup_dir, f"knowledge_backup_{timestamp}.db")

    os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)

    src_conn = sqlite3.connect(source_db)
    dst_conn = sqlite3.connect(destination_path)

    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=None)
        print(f"[SUCCESS] Database live backup saved to: {destination_path}")
        return destination_path
    finally:
        src_conn.close()
        dst_conn.close()


def restore_database(backup_path: str) -> bool:
    """Restore target database from specified backup file."""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    target_db = know.DB_FILE
    know.reset_db_connections()

    src_conn = sqlite3.connect(backup_path)
    dst_conn = sqlite3.connect(target_db)

    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=None)
        print(f"[SUCCESS] Database successfully restored from: {backup_path}")
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
