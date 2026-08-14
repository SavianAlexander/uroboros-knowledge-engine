import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_ore_reprocessing import generate_ore_reprocessing_markdown
from src.infrastructure.eve_blueprints_vault import generate_blueprints_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 8: MASTER ORES, REPROCESSING & BLUEPRINT VAULT")
print("=================================================================")

start_time = time.time()
indexed_count = 0

# 1. Master Ore Encyclopedia & Reprocessing
print("\n💎 Generating Master Ore Encyclopedia, Reprocessing Math & Ice/Gas Compendium...")
ore_files = generate_ore_reprocessing_markdown()
for f in ore_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(ore_files)} Ore & Reprocessing documents.")

# 2. Universal Blueprints & Invention Guide
print("\n📜 Generating Master Blueprint Tech Tree, Invention Guide & Fleet Portfolio...")
bp_files = generate_blueprints_markdown()
for f in bp_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(bp_files)} Blueprint Vault documents.")

# 3. Database Maintenance
print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 8 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
