"""
Autonomous EVE Online Skill Farm Extraction & Passive PLEX Arbitrage Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact 500k SP extraction thresholds and PLEX subscription ROI calculus.
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

VAULT_FLEET_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Fleet_Operations")


def calculate_sp_farming_roi(
    primary_attr: int = 27,
    secondary_attr: int = 21,
    implant_bonus: int = 5,
    extractor_cost_isk: float = 510000000.0,
    injector_sell_price_isk: float = 980000000.0,
    plex_500_cost_isk: float = 2650000000.0,
    sales_tax_percent: float = 3.6,
    broker_fee_percent: float = 1.0
) -> Dict[str, Any]:
    """
    Calculate exact monthly ISK yield, extractor costs, and net PLEX profit per skill farm character.
    """
    eff_primary = primary_attr + implant_bonus
    eff_secondary = secondary_attr + implant_bonus
    sp_per_hour = (eff_primary * 60) + (eff_secondary * 30)
    monthly_sp_produced = sp_per_hour * 24 * 30.0  # 30-day month

    # Extractors usable per month (500k SP per extractor, character must have >5.5M SP)
    extractors_per_month = monthly_sp_produced / 500000.0
    gross_extractor_cost = extractors_per_month * extractor_cost_isk

    # Gross Injector Revenue after taxes
    gross_injector_sales = extractors_per_month * injector_sell_price_isk
    tax_rate = (sales_tax_percent + broker_fee_percent) / 100.0
    net_injector_revenue = gross_injector_sales * (1.0 - tax_rate)

    # Net ISK Generation before & after PLEXing account
    net_isk_before_plex = net_injector_revenue - gross_extractor_cost
    net_profit_after_plex = net_isk_before_plex - plex_500_cost_isk

    return {
        "monthly_sp_produced": round(monthly_sp_produced, 0),
        "injectors_generated_per_month": round(extractors_per_month, 2),
        "gross_extractor_cost_m": round(gross_extractor_cost / 1000000.0, 1),
        "gross_injector_revenue_m": round(gross_injector_sales / 1000000.0, 1),
        "net_injector_revenue_m": round(net_injector_revenue / 1000000.0, 1),
        "net_isk_yield_before_plex_m": round(net_isk_before_plex / 1000000.0, 1),
        "plex_500_cost_m": round(plex_500_cost_isk / 1000000.0, 1),
        "net_profit_after_plex_m": round(net_profit_after_plex / 1000000.0, 1),
        "farm_status": "PROFITABLE_FARM (Free Omega + Liquid Profit)" if net_profit_after_plex >= 0 else "PARTIAL_SUBSIDY (Reduces Omega Cost)"
    }


def generate_sp_farming_markdown() -> List[str]:
    """Generate Skill Farming & PLEX Arbitrage reference document."""
    os.makedirs(VAULT_FLEET_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_FLEET_DIR, "skill_farming_plex_arbitrage.md")

    farm_calc = calculate_sp_farming_roi()

    doc_md = f"""---
title: Autonomous EVE Online Skill Farm Extraction & Passive PLEX Arbitrage Matrix
category: Fleet Economics
tags: [EVE, SkillFarming, SPInjector, SPExtractor, PLEX, PassiveIncome, NeuralRemap, Implants]
last_updated: 2026-08-14
---

# 💉 Autonomous Skill Farm Extraction & Passive PLEX Arbitrage Matrix

This document provides the financial and mathematical equations governing 500,000 SP skill extraction cycles and passive PLEX account maintenance.

---

## 📊 1. Monthly Skill Point Harvest & Extraction Metrics
- **Optimal Attributes**: Primary 32 / Secondary 26 (with +5 Learning Implants)
- **Monthly SP Output**: **{farm_calc['monthly_sp_produced']:,} SP / Month**
- **Large Skill Injectors Produced**: **{farm_calc['injectors_generated_per_month']} Injectors / Month**

---

## 💰 2. Monthly Financial Balance Sheet (Per Character)
- **Gross Injector Sales Value**: **{farm_calc['gross_injector_revenue_m']}M ISK**
- **Net Injector Revenue (After 4.6% Taxes)**: **{farm_calc['net_injector_revenue_m']}M ISK**
- **Cost of Skill Extractors**: **-{farm_calc['gross_extractor_cost_m']}M ISK**
- **Net Extraction Profit (Before PLEX)**: **+{farm_calc['net_isk_yield_before_plex_m']}M ISK (~1.70 Billion ISK)**
- **500 PLEX Omega Subscription Cost**: **-{farm_calc['plex_500_cost_m']}M ISK**
- **Net Balance**: **{farm_calc['net_profit_after_plex_m']}M ISK ({farm_calc['farm_status']})**
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_sp_farming_markdown()
    print(f"Generated SP farming document: {files}")
