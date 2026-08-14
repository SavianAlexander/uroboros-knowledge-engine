"""
EVE Online Regional Market Arbitrage & Trade Route Engine.

Calculates price margins, mineral valuation spreads, and regional hauling profit opportunities
between major market hubs (Jita 4-4, Amarr VIII, Dodixie IX, Rens VI, Hek VIII, 1DQ1-A).

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time).
"""

import os
import sys
import json
import time

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
MARKET_DIR = os.path.join(VAULT_EVE_DIR, "Markets")

MINERAL_PRICES = {
    "Tritanium": {"jita": 4.12, "amarr": 4.35, "delve_1dq": 4.80, "volume_m3": 0.01},
    "Pyerite": {"jita": 12.80, "amarr": 13.40, "delve_1dq": 14.50, "volume_m3": 0.01},
    "Mexallon": {"jita": 74.50, "amarr": 78.20, "delve_1dq": 84.00, "volume_m3": 0.01},
    "Isogen": {"jita": 420.00, "amarr": 445.00, "delve_1dq": 490.00, "volume_m3": 0.01},
    "Nocxium": {"jita": 980.00, "amarr": 1020.00, "delve_1dq": 1150.00, "volume_m3": 0.01},
    "Zydrine": {"jita": 2450.00, "amarr": 2600.00, "delve_1dq": 2850.00, "volume_m3": 0.01},
    "Megacyte": {"jita": 3800.00, "amarr": 4100.00, "delve_1dq": 4600.00, "volume_m3": 0.01},
    "Morphite": {"jita": 14200.00, "amarr": 14900.00, "delve_1dq": 16500.00, "volume_m3": 0.01},
}

PI_COMMODITIES = {
    "Robotics (P3)": {"jita": 88000.0, "amarr": 94000.0, "delve_1dq": 115000.0, "volume_m3": 1.5},
    "Guidance Systems (P3)": {"jita": 78000.0, "amarr": 83000.0, "delve_1dq": 98000.0, "volume_m3": 1.5},
    "Broadcast Node (P4)": {"jita": 3800000.0, "amarr": 4100000.0, "delve_1dq": 4600000.0, "volume_m3": 100.0},
    "Integrity Response Drones (P4)": {"jita": 4100000.0, "amarr": 4350000.0, "delve_1dq": 4950000.0, "volume_m3": 100.0},
    "Nano-Factory (P4)": {"jita": 3950000.0, "amarr": 4200000.0, "delve_1dq": 4750000.0, "volume_m3": 100.0},
}


def generate_market_arbitrage_markdown(output_dir: str = MARKET_DIR) -> list:
    """Generate market arbitrage opportunities and trade route valuations."""
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. Mineral Arbitrage Matrix
    min_rows = []
    for mname, data in MINERAL_PRICES.items():
        j_p = data["jita"]
        d_p = data["delve_1dq"]
        spread = d_p - j_p
        margin_pct = (spread / j_p) * 100.0
        isk_per_m3 = spread / data["volume_m3"]
        min_rows.append(f"| **{mname}** | {j_p:,.2f} ISK | {d_p:,.2f} ISK | **+{spread:,.2f} ISK** | `+{margin_pct:.1f}%` | **{isk_per_m3:,.2f} ISK/m³** |")

    min_table = "\n".join(min_rows)

    # 2. PI Arbitrage Matrix
    pi_rows = []
    for pname, data in PI_COMMODITIES.items():
        j_p = data["jita"]
        d_p = data["delve_1dq"]
        spread = d_p - j_p
        margin_pct = (spread / j_p) * 100.0
        isk_per_m3 = spread / data["volume_m3"]
        pi_rows.append(f"| **{pname}** | {j_p:,.2f} ISK | {d_p:,.2f} ISK | **+{spread:,.2f} ISK** | `+{margin_pct:.1f}%` | **{isk_per_m3:,.2f} ISK/m³** |")

    pi_table = "\n".join(pi_rows)

    arb_file = os.path.join(output_dir, "market_arbitrage.md")
    arb_md = f"""# EVE Online: Regional Trade Hub Arbitrage & Margin Engine

Automated price spread analysis between **Jita 4-4 (Forge Core)**, **Amarr VIII (Domain)**, and **1DQ1-A (Goonswarm Sovereign Capital)**.

---

## 💎 Mineral Regional Price Spreads (Highsec $\rightarrow$ Nullsec Staging)
| Mineral | Jita 4-4 Price | 1DQ1-A Price | Absolute Spread | Margin % | Density (ISK/m³) |
| :--- | :--- | :--- | :--- | :--- | :--- |
{min_table}

---

## 🪐 Planetary Commodities Arbitrage (P3 / P4 High-Tech Goods)
| Commodity | Jita 4-4 Price | 1DQ1-A Price | Absolute Spread | Margin % | Density (ISK/m³) |
| :--- | :--- | :--- | :--- | :--- | :--- |
{pi_table}
"""
    with open(arb_file, "w", encoding="utf-8") as f:
        f.write(arb_md)
    created_files.append(arb_file)

    # 3. Trade & Hauling Routes Guide
    routes_file = os.path.join(output_dir, "trade_routes.md")
    routes_md = f"""# Strategic Hauling & Trade Routes: Jita to Delve

Optimized jump freighter and blockade runner corridors for fleet logistics.

---

### 🚀 Route 1: Jita 4-4 $\rightarrow$ 1DQ1-A (Jump Freighter Corridor)
- **Primary Carrier**: Nomad / Ark / Rhea (Jump Freighter)
- **Max Jump Fatigue**: 5.0 hours (managed via fatigue cooldowns)
- **Waypoints**: Jita $\rightarrow$ Highsec Staging $\rightarrow$ Lowsec Cyno Beacon $\rightarrow$ 1DQ1-A Keepstar
- **Average Profit per Full Cargo (350,000 m³)**: **1.2 Billion – 2.5 Billion ISK**

---

### ⚡ Route 2: High-Value Covert Hauling (Blockade Runner)
- **Primary Ship**: Prowler / Viator / Crane (Covert Ops Cloak)
- **Cargo**: P4 Commodities, Blueprints, Deadspace Modules, Skill Injectors
- **Safe Cargo Limit**: < 2.0 Billion ISK per run (Gank threshold avoidance)
"""
    with open(routes_file, "w", encoding="utf-8") as f:
        f.write(routes_md)
    created_files.append(routes_file)

    return created_files
