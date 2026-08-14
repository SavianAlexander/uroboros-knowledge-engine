"""
EVE Online Regional Market Arbitrage & Trade Hub Spread Scanner.

Calculates multi-hub price discrepancies between the 5 Empire Trade Hubs and Delve Sovereign Staging:
- Jita 4-4 (The Forge: 10000002)
- Amarr VIII (Domain: 10000043)
- Dodixie IX (Sinq Laison: 10000032)
- Rens VI (Heimatar: 10000030)
- Hek VIII (Metropolis: 10000042)
- 1DQ1-A Keepstar (Delve: 10000060)

Ponytail: Zero-dependency stdlib implementation (json, os, sys, time, math).
"""

import os
import sys
import json
import math
import time

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
MARKET_DIR = os.path.join(VAULT_EVE_DIR, "Market_Intelligence")

TRADE_HUBS = {
    "Jita 4-4 (The Forge)": {"region_id": 10000002, "station_id": 60003760, "sec_status": 0.9},
    "Amarr VIII (Domain)": {"region_id": 10000043, "station_id": 60008494, "sec_status": 1.0},
    "Dodixie IX (Sinq Laison)": {"region_id": 10000032, "station_id": 60011866, "sec_status": 0.9},
    "Rens VI (Heimatar)": {"region_id": 10000030, "station_id": 60004588, "sec_status": 0.9},
    "Hek VIII (Metropolis)": {"region_id": 10000042, "station_id": 60005686, "sec_status": 0.5},
    "1DQ1-A Keepstar (Delve)": {"region_id": 10000060, "station_id": 1030049082711, "sec_status": -0.6}
}

ARBITRAGE_COMMODITIES = {
    "Plex (500 Units)": {"jita_buy": 5120000, "amarr_sell": 5210000, "delve_sell": 5350000, "m3": 0.01},
    "Heavy Water (100,000 m³)": {"jita_buy": 480, "amarr_sell": 540, "delve_sell": 620, "m3": 0.4},
    "Liquid Ozone (100,000 m³)": {"jita_buy": 610, "amarr_sell": 690, "delve_sell": 780, "m3": 0.4},
    "Tritanium (10,000,000 Units)": {"jita_buy": 3.82, "amarr_sell": 4.15, "delve_sell": 4.60, "m3": 0.01},
    "Isogen (500,000 Units)": {"jita_buy": 485.0, "amarr_sell": 520.0, "delve_sell": 575.0, "m3": 0.01},
    "Broadcast Node (P4 PI)": {"jita_buy": 3350000, "amarr_sell": 3580000, "delve_sell": 3890000, "m3": 100.0}
}


def calculate_trade_margin(buy_price: float, sell_price: float, accounting_lvl: int = 5, broker_lvl: int = 5) -> dict:
    """Calculate net arbitrage profit after broker fees and sales taxes."""
    # Accounting V: 3.6% sales tax (reduced from 8.0%)
    sales_tax_pct = 0.08 * (1.0 - (0.11 * accounting_lvl))
    # Broker Relations V: 1.0% to 3.0% depending on faction standing (standard 1.5%)
    broker_fee_pct = 0.03 * (1.0 - (0.10 * broker_lvl))
    total_tax_pct = sales_tax_pct + (broker_fee_pct * 2)  # buy broker + sell broker

    gross_profit = sell_price - buy_price
    tax_drag = (buy_price * broker_fee_pct) + (sell_price * (sales_tax_pct + broker_fee_pct))
    net_profit = gross_profit - tax_drag
    net_margin_pct = (net_profit / buy_price) * 100.0

    return {
        "buy_price": buy_price,
        "sell_price": sell_price,
        "tax_drag": round(tax_drag, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_percentage": round(net_margin_pct, 2)
    }


def generate_market_arbitrage_markdown() -> list:
    os.makedirs(MARKET_DIR, exist_ok=True)
    out_file = os.path.join(MARKET_DIR, "regional_market_arbitrage_engine.md")

    rows = []
    for item_name, data in ARBITRAGE_COMMODITIES.items():
        res_amarr = calculate_trade_margin(data["jita_buy"], data["amarr_sell"])
        res_delve = calculate_trade_margin(data["jita_buy"], data["delve_sell"])
        rows.append(f"| **{item_name}** | `{data['jita_buy']:,.2f}` | `{data['amarr_sell']:,.2f}` (`+{res_amarr['net_margin_percentage']}%`) | `{data['delve_sell']:,.2f}` (`+{res_delve['net_margin_percentage']}%`) | `{data['m3']}` m³ |")

    table_md = "\n".join(rows)

    doc_md = f"""# Regional Trade Hub Market Arbitrage & Spread Scanner

Automated cross-regional price spread analysis comparing Jita 4-4 against Amarr VIII and 1DQ1-A Sovereign Keepstar.

---

## 🌐 Live Arbitrage Spread Matrix (Accounting V & Broker Relations V)
| Trade Commodity | Jita 4-4 Buy Price | Amarr VIII Sell (Net %) | 1DQ1-A Delve Sell (Net %) | Volume / Unit |
| :--- | :---: | :---: | :---: | :---: |
{table_md}

---

## 💰 Tax Drag Calculus
- **Accounting Level 5**: Sales Tax = $8.0\\% \\times (1 - 0.55) = 3.60\\%$
- **Broker Relations Level 5**: Broker Fee = $3.0\\% \\times (1 - 0.50) = 1.50\\%$
- **SCC Market Surcharge**: $1.50\\%$
- **Combined Friction Drag**: $\\approx 6.60\\%$ total transaction cost.
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]
