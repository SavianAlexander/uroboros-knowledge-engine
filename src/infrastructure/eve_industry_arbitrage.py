"""
Autonomous EVE Online Industry, Invention & Inter-Hub Market Arbitrage Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact CCP invention math, market tax formulas, and capital BOM calculators.
"""

import os
import sys
import math
import json
import time
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_IND_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Industry_Reactions")

DECRYPTORS = {
    "None": {"runs_modifier": 0, "me_modifier": 0, "prob_multiplier": 1.00},
    "Attainment Decryptor": {"runs_modifier": +4, "me_modifier": -1, "prob_multiplier": 1.80},
    "Augmentation Decryptor": {"runs_modifier": +9, "me_modifier": -2, "prob_multiplier": 1.60},
    "Parity Decryptor": {"runs_modifier": +3, "me_modifier": +1, "prob_multiplier": 1.50},
    "Process Decryptor": {"runs_modifier": 0, "me_modifier": +3, "prob_multiplier": 1.10},
    "Symmetry Decryptor": {"runs_modifier": +2, "me_modifier": +1, "prob_multiplier": 1.00},
    "Optimism Decryptor": {"runs_modifier": +5, "me_modifier": +2, "prob_multiplier": 1.40}
}


def calculate_invention_probability(
    base_chance: float = 0.34,
    encryption_skill: int = 5,
    datacore_skill_1: int = 5,
    datacore_skill_2: int = 5,
    decryptor_name: str = "Optimism Decryptor"
) -> Dict[str, Any]:
    """
    Calculate exact T2 invention probability using canonical CCP equation.
    """
    dec = DECRYPTORS.get(decryptor_name, DECRYPTORS["None"])
    skill_factor = 1.0 + (encryption_skill / 40.0) + ((datacore_skill_1 + datacore_skill_2) / 30.0)
    raw_chance = base_chance * skill_factor * dec["prob_multiplier"]
    final_chance = min(1.0, raw_chance)

    return {
        "base_chance_percent": round(base_chance * 100, 1),
        "encryption_skill_level": encryption_skill,
        "datacore_skills": [datacore_skill_1, datacore_skill_2],
        "decryptor_used": decryptor_name,
        "runs_modifier": dec["runs_modifier"],
        "me_modifier": dec["me_modifier"],
        "final_invention_probability_percent": round(final_chance * 100, 2),
        "expected_success_rate": f"{round(final_chance * 100, 1)}% ({round(1/final_chance, 1)} attempts per BPC)"
    }


def calculate_interhub_arbitrage_spread(
    item_name: str = "Tritanium (Packaged 100k)",
    buy_hub: str = "Jita 4-4 (The Forge)",
    buy_price_isk: float = 3.85,
    sell_hub: str = "Amarr VIII (Domain)",
    sell_price_isk: float = 4.45,
    quantity: int = 10000000,
    broker_relations_skill: int = 5,
    accounting_skill: int = 5,
    freight_cost_per_m3_isk: float = 12.0,
    unit_volume_m3: float = 0.01
) -> Dict[str, Any]:
    """
    Calculate net profit, tax deductions, and ROI for inter-hub hauling arbitrage.
    """
    # Sales Tax: 8% base - 0.88% per level of Accounting (3.6% at level 5)
    sales_tax_rate = 0.08 - (accounting_skill * 0.0088)
    # Broker Fee: 3% base - 0.4% per level of Broker Relations (1.0% at level 5 with faction standings)
    broker_fee_rate = 0.03 - (broker_relations_skill * 0.004)

    gross_investment = buy_price_isk * quantity
    gross_revenue = sell_price_isk * quantity

    total_broker_fees = gross_revenue * broker_fee_rate
    total_sales_tax = gross_revenue * sales_tax_rate
    total_freight_cost = (quantity * unit_volume_m3) * freight_cost_per_m3_isk

    net_revenue = gross_revenue - total_broker_fees - total_sales_tax - total_freight_cost
    net_profit = net_revenue - gross_investment
    roi_percent = (net_profit / gross_investment) * 100.0 if gross_investment > 0 else 0.0

    return {
        "item_name": item_name,
        "buy_hub": buy_hub,
        "sell_hub": sell_hub,
        "quantity": quantity,
        "gross_capital_invested_isk": round(gross_investment, 2),
        "gross_revenue_isk": round(gross_revenue, 2),
        "broker_fees_isk": round(total_broker_fees, 2),
        "sales_tax_isk": round(total_sales_tax, 2),
        "freight_cost_isk": round(total_freight_cost, 2),
        "net_profit_isk": round(net_profit, 2),
        "net_profit_millions": round(net_profit / 1000000.0, 2),
        "roi_percent": round(roi_percent, 2),
        "arbitrage_verdict": "HIGHLY_PROFITABLE" if roi_percent > 12.0 else "MARGINAL" if roi_percent > 4.0 else "UNPROFITABLE"
    }


def generate_industry_arbitrage_markdown() -> List[str]:
    """Generate Industry, Invention & Market Arbitrage reference document."""
    os.makedirs(VAULT_IND_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_IND_DIR, "blueprints_invention_market_arbitrage.md")

    inv_calc = calculate_invention_probability(base_chance=0.34, decryptor_name="Optimism Decryptor")
    arb_calc = calculate_interhub_arbitrage_spread()

    doc_md = f"""---
title: Autonomous EVE Online Industry, Invention & Inter-Hub Market Arbitrage Engine
category: Industrial Intelligence & Economics
tags: [EVE, Industry, Invention, BPO, BPC, Decryptors, MarketArbitrage, Jita44, AmarrVIII, Freight]
last_updated: 2026-08-14
---

# 🏭 Autonomous Industry, Invention & Inter-Hub Market Arbitrage Engine

This document outlines the T2 invention mathematical models, decryptor multipliers, and cross-regional inter-hub trade spread algorithms.

---

## 🔬 1. Canonical T2 Invention Mathematics
- **Base Invention Chance**: **{inv_calc['base_chance_percent']}%**
- **Skills**: Encryption V + Datacore Science V/V
- **Decryptor Applied**: **`{inv_calc['decryptor_used']}`** (Runs: `{inv_calc['runs_modifier']:+d}`, ME: `{inv_calc['me_modifier']:+d}`)
- **Final Invention Success Probability**: **{inv_calc['final_invention_probability_percent']}%**
- **Expected Success Benchmark**: **`{inv_calc['expected_success_rate']}`**

---

## 📈 2. Inter-Hub Market Arbitrage Ledger
- **Commodity**: `{arb_calc['item_name']}` (Volume: `{arb_calc['quantity']:,}` units)
- **Trade Route**: **`{arb_calc['buy_hub']}` $\\longrightarrow$ `{arb_calc['sell_hub']}`**
- **Gross Capital Invested**: **{arb_calc['gross_capital_invested_isk']:,.2f} ISK**
- **Broker Fees (1.0%)**: `{arb_calc['broker_fees_isk']:,.2f} ISK`
- **Sales Tax (3.6%)**: `{arb_calc['sales_tax_isk']:,.2f} ISK`
- **Hauling Freight Cost**: `{arb_calc['freight_cost_isk']:,.2f} ISK`
- **Net Liquid Profit**: **{arb_calc['net_profit_isk']:,.2f} ISK ({arb_calc['net_profit_millions']}M ISK)**
- **Net Return on Investment (ROI)**: **`{arb_calc['roi_percent']}%` ({arb_calc['arbitrage_verdict']})**
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_industry_arbitrage_markdown()
    print(f"Generated industry arbitrage document: {files}")
