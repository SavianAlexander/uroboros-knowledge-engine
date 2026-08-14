import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_combat_anomalies import generate_anomalies_markdown
from src.infrastructure.eve_moon_reactions import generate_moon_reactions_markdown
from src.infrastructure.eve_exploration_lore import generate_exploration_lore_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 7: DED MATRIX, MOON REACTIONS, BURNERS & LORE")
print("=================================================================")

start_time = time.time()
indexed_count = 0

# 1. DED Combat Complexes & Burners
print("\n⚔️ Generating DED Combat Complex Matrix & Burner Mission Guides...")
ded_files = generate_anomalies_markdown()
for f in ded_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(ded_files)} Combat Anomaly documents.")

# 2. Moon Mining & T2 Composite Reactions
print("\n🌙 Generating Moon Ore Classifications & T2 Composite Reaction Chains...")
moon_files = generate_moon_reactions_markdown()
for f in moon_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(moon_files)} Moon Reaction documents.")

# 3. Exploration Signatures & Master Faction Lore
print("\n🔭 Generating Exploration Signatures & Master Faction Lore Compendium...")
exp_files = generate_exploration_lore_markdown()
for f in exp_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(exp_files)} Exploration & Lore documents.")

# 4. Database Maintenance
print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 7 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
