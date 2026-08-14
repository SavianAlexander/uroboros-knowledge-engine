import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_university import generate_eve_university_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 15: EVE UNIVERSITY (UNIWIKI) & DEEP MECHANICS")
print("=================================================================")

start_time = time.time()
indexed_count = 0

print("\n🎓 Generating EVE University Fleet Curriculum, Deep Physics & Playbooks...")
uni_files = generate_eve_university_markdown()
for f in uni_files:
    index_single_file(f)
    indexed_count += 1
    print(f"  ✅ Generated & Indexed: {os.path.basename(f)}")

print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 15 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
