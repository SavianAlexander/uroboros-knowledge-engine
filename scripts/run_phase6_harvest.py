import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_faction_warfare import generate_fw_markdown
from src.infrastructure.eve_sovereignty import generate_sovereignty_markdown
from src.infrastructure.eve_deep_space import generate_deep_space_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 6: FW WARZONES, SOV MAP, J-SPACE & POCHVEN")
print("=================================================================")

start_time = time.time()
indexed_count = 0

# 1. Faction Warfare
print("\n⚔️ Generating Faction Warfare Warzone & Contestation Matrix...")
fw_files = generate_fw_markdown()
for f in fw_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(fw_files)} Faction Warfare documents.")

# 2. Nullsec Sovereignty Map
print("\n👑 Generating Null-Sec Sovereignty & Coalition Territory Matrix...")
sov_files = generate_sovereignty_markdown()
for f in sov_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(sov_files)} Sovereignty documents.")

# 3. Deep Space, Wormholes, Pochven, Abyssal & PI Schematics
print("\n🌌 Generating Deep Space, J-Space, Pochven, Abyssal & PI Schematics...")
ds_files = generate_deep_space_markdown()
for f in ds_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(ds_files)} Deep Space documents.")

# 4. Database Maintenance
print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 6 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
