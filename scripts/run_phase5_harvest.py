import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_realtime import generate_realtime_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 5: REAL-TIME UNIVERSE TELEMETRY & TACTICAL RADAR")
print("=================================================================")

start_time = time.time()
indexed_count = 0

print("\n📡 Fetching Live Real-Time Universe Streams from CCP ESI...")
rt_files = generate_realtime_markdown()

for f in rt_files:
    index_single_file(f)
    indexed_count += 1
    print(f"  ✅ Indexed Real-Time Stream: {os.path.basename(f)}")

print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 5 REAL-TIME TELEMETRY COMPLETE in {elapsed:.2f}s!")
print(f"Total Live Stream Documents Indexed: {indexed_count}")
print("=================================================================")
