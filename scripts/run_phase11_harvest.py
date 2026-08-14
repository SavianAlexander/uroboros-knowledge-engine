import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_combat_mechanics import generate_combat_mechanics_markdown
from src.infrastructure.eve_doctrine_fits import generate_doctrines_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 11: IMPLANTS, COMBAT MATH, EWAR & DOCTRINES")
print("=================================================================")

start_time = time.time()
indexed_count = 0

# 1. Implants, Damage Math & EWAR
print("\n🧬 Generating Implants Matrix, Tracking/Missile Math & EWAR Guides...")
mech_files = generate_combat_mechanics_markdown()
for f in mech_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(mech_files)} Combat Mechanics documents.")

# 2. Doctrine Fitting Catalog
print("\n🛡️ Generating Master Fleet Doctrine Fitting Library (EFT / Pyfa)...")
doc_files = generate_doctrines_markdown()
for f in doc_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(doc_files)} Doctrine Fitting documents.")

# 3. Database Maintenance
print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 11 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
