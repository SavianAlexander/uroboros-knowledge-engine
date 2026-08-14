"""
Autonomous EVE Online Holding Corporation 0% Tax Optimization Engine.
Standard: Pure Python Standard Library (math, json, os, sys, time).
Ponytail Senior Dev Principle: Exact NPC 11% vs Player 0% tax savings calculus.
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


def calculate_tax_shield_savings(
    monthly_bounties_isk: float = 6000000000.0,  # 6 Billion ISK / mo (Ratting + Incursions + OFP)
    monthly_mission_rewards_isk: float = 1200000000.0,
    npc_corp_tax_percent: float = 11.0,
    player_holding_tax_percent: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate monthly and annual ISK shielded by establishing a private 0% player holding corporation.
    """
    gross_taxable_revenue = monthly_bounties_isk + monthly_mission_rewards_isk
    npc_tax_paid_monthly = gross_taxable_revenue * (npc_corp_tax_percent / 100.0)
    player_tax_paid_monthly = gross_taxable_revenue * (player_holding_tax_percent / 100.0)

    monthly_savings = npc_tax_paid_monthly - player_tax_paid_monthly
    annual_savings = monthly_savings * 12.0

    return {
        "monthly_taxable_revenue_m": round(gross_taxable_revenue / 1000000.0, 1),
        "npc_corp_tax_rate_percent": npc_corp_tax_percent,
        "player_corp_tax_rate_percent": player_holding_tax_percent,
        "npc_tax_loss_monthly_m": round(npc_tax_paid_monthly / 1000000.0, 1),
        "monthly_tax_shield_savings_m": round(monthly_savings / 1000000.0, 1),
        "annual_tax_shield_savings_m": round(annual_savings / 1000000.0, 1),
        "annual_tax_shield_savings_b": round(annual_savings / 1000000000.0, 2),
        "shield_recommendation": "CRITICAL_MANDATORY (Founds 0% Corp immediately)"
    }


def generate_corp_tax_markdown() -> List[str]:
    """Generate Holding Corporation Tax Shield reference document."""
    os.makedirs(VAULT_FLEET_DIR, exist_ok=True)
    out_file = os.path.join(VAULT_FLEET_DIR, "holding_corporation_tax_shield.md")

    tax_calc = calculate_tax_shield_savings()

    doc_md = f"""---
title: Autonomous EVE Online Private Holding Corporation 0% Tax Optimization
category: Fleet Economics
tags: [EVE, HoldingCorp, TaxShield, NPCTax, RattingBounties, Incursions, PassiveSavings, ISK]
last_updated: 2026-08-14
---

# 🏢 Autonomous Private Holding Corporation 0% Tax Optimization

This document outlines the corporate structure and tax shielding mathematics governing the migration of all 8 pilots from 11% NPC starter corporations into a private 0% tax entity.

---

## 📉 1. The 11% NPC Corporation Tax Bleed
- Default NPC Corporations (*Federal Navy Academy, Brutor Tribe, Republic Military School*) enforce a mandatory **11.0% flat tax** on all ratting bounties, mission rewards, and incursion payouts.
- For an active fleet grossing **{tax_calc['monthly_taxable_revenue_m']}M ISK/month**, the default NPC tax drains **-{tax_calc['npc_tax_loss_monthly_m']}M ISK / month**.

---

## 🛡️ 2. 0% Player Holding Corporation Balance Sheet
- **Player Corporation Tax Setting**: **`0.0%` Flat Rate**
- **Monthly Retained ISK**: **+{tax_calc['monthly_tax_shield_savings_m']}M ISK / Month**
- **Annual Retained Fleet Capital**: **+{tax_calc['annual_tax_shield_savings_b']} Billion ISK / Year ({tax_calc['annual_tax_shield_savings_m']}M ISK)**
- **Strategic Implementation**: **`{tax_calc['shield_recommendation']}`**
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc_md)

    return [out_file]


if __name__ == "__main__":
    files = generate_corp_tax_markdown()
    print(f"Generated corp tax document: {files}")
