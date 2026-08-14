import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Neuro Alexander")

from src.infrastructure.eve_sde import generate_encyclopedia_markdown
from src.infrastructure.eve_zkill import generate_threat_intel_markdown
from src.infrastructure.eve_arbitrage import generate_market_arbitrage_markdown
from batch_index import index_single_file
from src.infrastructure.database import run_maintenance

print("=================================================================")
print("🌐 STARTING PHASE 4: SDE ENCYCLOPEDIA, ZKILL THREAT & ARBITRAGE")
print("=================================================================")

start_time = time.time()
indexed_count = 0

# 1. SDE Ship Encyclopedia
print("\n📘 Generating Master Ship Hull Encyclopedia & Theorycrafting Vault...")
enc_files = generate_encyclopedia_markdown()
for f in enc_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(enc_files)} Ship Encyclopedia documents.")

# 2. zKillboard Threat Intel
print("\n⚔️ Generating zKillboard Public Threat Intel & Combat Forensics...")
threat_files = generate_threat_intel_markdown()
for f in threat_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(threat_files)} Threat Intel documents.")

# 3. Market Arbitrage & Trade Routes
print("\n💎 Generating Regional Market Arbitrage & Trade Route Engine...")
arb_files = generate_market_arbitrage_markdown()
for f in arb_files:
    index_single_file(f)
    indexed_count += 1
print(f"  ✅ Generated & Indexed {len(arb_files)} Market Arbitrage documents.")

# 4. Database Maintenance
print("\n🔧 Running Uroboros Knowledge Vault Database Maintenance...")
try:
    run_maintenance()
    print("  ✅ Maintenance complete.")
except Exception as ex:
    print(f"  ⚠️ Maintenance warning: {ex}")

elapsed = time.time() - start_time
print("=================================================================")
print(f"🎉 PHASE 4 INTEGRATION COMPLETE in {elapsed:.2f}s!")
print(f"Total New Documents Indexed: {indexed_count}")
print("=================================================================")
