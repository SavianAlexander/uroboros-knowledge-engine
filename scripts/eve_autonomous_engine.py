"""
EVE Online Autonomous Telemetry Engine & Multi-Tier Background Daemon.

Provides continuous, dynamic, self-healing synchronization for the entire fleet:
- Tier 1 Tactical Stream (5m interval): Server status, hourly kills/jumps heatmaps, incursions, sov campaigns, online/location tracking.
- Tier 2 Deep Fleet Sync (15m interval): Wallet journals, live assets/pricing, skill queues, mail, notifications, PI, omni-tables.
- Self-Healing OAuth: Automatically refreshes expiring tokens in tokens.json.
- Differential Indexer: Computes SHA-256 diffs against knowledge.db to re-index only modified files.

Ponytail: Zero-dependency stdlib implementation (os, sys, time, json, hashlib, threading).
"""

import os
import sys
import time
import json
import hashlib
import signal

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.infrastructure.eve_sso import token_manager
from src.infrastructure.eve_realtime import generate_realtime_markdown
from src.infrastructure.eve_vault_sync import sync_and_index_all_characters
from src.infrastructure.eve_omni_tables import generate_omni_tables_markdown
from src.infrastructure.eve_alpha_omega import generate_clone_status_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance, get_db

RUNNING = True


def handle_stop_signal(signum, frame):
    global RUNNING
    print("\n🛑 Stop signal received. Shutting down Autonomous EVE Engine gracefully...")
    RUNNING = False


signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)


def get_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def index_if_modified(filepath: str) -> bool:
    """Index file into knowledge.db only if content has changed (SHA256 diff)."""
    if not os.path.exists(filepath):
        return False
    current_sha = get_file_sha256(filepath)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT sha256 FROM files WHERE filepath = ?", (filepath,))
        row = cur.fetchone()
        if row and row[0] == current_sha:
            return False  # Unchanged, skip re-embedding

    index_single_file(filepath)
    return True


class AutonomousEveEngine:
    def __init__(self, tactical_interval: int = 300, deep_interval: int = 900):
        self.tactical_interval = tactical_interval
        self.deep_interval = deep_interval
        self.last_tactical_time = 0
        self.last_deep_time = 0
        self.cycle_count = 0

    def run_tactical_cycle(self):
        """Execute Fast Tactical Stream (Server status, danger/traffic heatmaps, incursions, sov)."""
        print(f"\n📡 [{time.strftime('%H:%M:%S UTC', time.gmtime())}] Running Tier 1 Tactical Universe Stream...")
        try:
            rt_files = generate_realtime_markdown()
            updated = 0
            for f in rt_files:
                if index_if_modified(f):
                    updated += 1
            print(f"  ✅ Tactical Stream updated: {len(rt_files)} files evaluated ({updated} modified & re-indexed).")
        except Exception as ex:
            print(f"  ⚠️ Tactical Stream warning: {ex}")
        self.last_tactical_time = time.time()

    def run_deep_fleet_cycle(self):
        """Execute Deep Fleet Sync (Wallet, Assets, Skills, Mail, PI, Omni Tables, Clone Status)."""
        print(f"\n🚀 [{time.strftime('%H:%M:%S UTC', time.gmtime())}] Running Tier 2 Full-Spectrum Fleet Synchronization...")
        try:
            # 1. Full Character Profile Sync & Master Matrices
            results = sync_and_index_all_characters()
            print(f"  ✅ Fleet Telemetry synced: {results.get('total_characters', 0)} pilots.")

            # 2. Dynamic Clone Status
            clone_files = generate_clone_status_markdown()
            for f in clone_files:
                index_if_modified(f)

            # 3. Omni-State Correlation Tables
            omni_files = generate_omni_tables_markdown()
            for f in omni_files:
                index_if_modified(f)

            # 4. Database Maintenance
            run_maintenance()
            print(f"  ✅ Deep Fleet Synchronization & DB Maintenance complete.")
        except Exception as ex:
            print(f"  ❌ Deep Fleet Sync error: {ex}")
        self.last_deep_time = time.time()

    def run_once(self):
        """Execute a full tactical + deep synchronization once."""
        print("=================================================================")
        print("🌐 AUTONOMOUS EVE ENGINE: EXECUTING FULL ON-DEMAND SYNC")
        print("=================================================================")
        start = time.time()
        self.run_tactical_cycle()
        self.run_deep_fleet_cycle()
        elapsed = time.time() - start
        print("=================================================================")
        print(f"🎉 FULL SYNCHRONIZATION CYCLE COMPLETE in {elapsed:.2f}s!")
        print("=================================================================")

    def start_daemon(self):
        """Run infinite autonomous daemon loop."""
        print("=================================================================")
        print("🌐 AUTONOMOUS EVE TELEMETRY ENGINE DAEMON STARTED")
        print(f"  • Tier 1 Tactical Stream Interval: {self.tactical_interval}s ({self.tactical_interval//60} min)")
        print(f"  • Tier 2 Deep Fleet Sync Interval: {self.deep_interval}s ({self.deep_interval//60} min)")
        print("=================================================================")
        global RUNNING
        while RUNNING:
            now = time.time()
            # Check tactical interval
            if (now - self.last_tactical_time) >= self.tactical_interval:
                self.run_tactical_cycle()

            # Check deep interval
            if (now - self.last_deep_time) >= self.deep_interval:
                self.run_deep_fleet_cycle()

            self.cycle_count += 1
            # Sleep in short increments for responsive interrupt handling
            for _ in range(10):
                if not RUNNING:
                    break
                time.sleep(1)

        print("🛑 Autonomous EVE Engine Daemon terminated.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVE Online Autonomous Telemetry Daemon")
    parser.add_argument("--once", action="store_true", help="Run one full cycle and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in the background")
    parser.add_argument("--tactical-interval", type=int, default=300, help="Tactical stream interval in seconds (default: 300)")
    parser.add_argument("--deep-interval", type=int, default=900, help="Deep fleet sync interval in seconds (default: 900)")

    args = parser.parse_args()
    engine = AutonomousEveEngine(tactical_interval=args.tactical_interval, deep_interval=args.deep_interval)

    if args.daemon:
        engine.start_daemon()
    else:
        engine.run_once()
