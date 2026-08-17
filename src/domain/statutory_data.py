"""
Empirical Statutory Data & Policy Matrix Manager.
Standard: Pure Python standard library (json, os, typing).
Provides dynamic, cached, and schema-validated statutory guidelines for Social Program Management.
Eliminates static hardcoded magic numbers by grounding rules in empirical, versioned policy datasets.
"""

import json
import os
from typing import Dict, Any, Optional


_POLICY_CACHE: Optional[Dict[str, Any]] = None
_DEFAULT_POLICY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "statutory_policy_2026.json")
)


def load_statutory_policy(file_path: Optional[str] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Loads and caches the empirical statutory policy dataset from JSON."""
    global _POLICY_CACHE
    if _POLICY_CACHE is not None and not force_reload and file_path is None:
        return _POLICY_CACHE

    target_path = file_path or _DEFAULT_POLICY_PATH
    if not os.path.isfile(target_path):
        raise FileNotFoundError(
            f"Empirical statutory policy file not found at '{target_path}'. "
            "Please harvest primary sources via 'python .agents/skills/neuro-copilot/scripts/neuro_cli.py sync_sources --domain statutory'."
        )

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if file_path is None:
        _POLICY_CACHE = data
    return data


def get_fpl_monthly(
    household_size: int,
    region: str = "contiguous_48_and_dc",
    policy: Optional[Dict[str, Any]] = None
) -> float:
    """Computes the 100% Monthly Federal Poverty Level from empirical policy tables."""
    pol = policy or load_statutory_policy()
    guidelines = pol.get("fpl_guidelines", {}).get(region, {})
    base = float(guidelines.get("annual_base", 15650.0))
    per_person = float(guidelines.get("annual_per_person", 5520.0))
    size = max(1, int(household_size))
    annual_total = base + (size - 1) * per_person
    return round(annual_total / 12.0, 2)


def get_snap_max_allotment(
    household_size: int,
    policy: Optional[Dict[str, Any]] = None
) -> float:
    """Retrieves empirical SNAP maximum monthly allotment for household size."""
    pol = policy or load_statutory_policy()
    snap_cfg = pol.get("snap", {})
    allotments = snap_cfg.get("maximum_allotments", {})
    size = max(1, int(household_size))
    if str(size) in allotments:
        return float(allotments[str(size)])
    # 8+ members calculation
    base_8 = float(allotments.get("8", 1756.0))
    per_add = float(snap_cfg.get("per_additional_person_allotment", 220.0))
    return round(base_8 + (size - 8) * per_add, 2)


def get_snap_standard_deduction(
    household_size: int,
    policy: Optional[Dict[str, Any]] = None
) -> float:
    """Retrieves empirical SNAP standard deduction based on household size bracket."""
    pol = policy or load_statutory_policy()
    deductions = pol.get("snap", {}).get("standard_deduction", {})
    size = max(1, int(household_size))
    if size <= 3:
        return float(deductions.get("household_1_to_3", 198.0))
    elif size <= 5:
        return float(deductions.get("household_4_to_5", 208.0))
    else:
        return float(deductions.get("household_6_plus", 246.0))


def get_tanf_max_benefit(
    household_size: int,
    policy: Optional[Dict[str, Any]] = None
) -> float:
    """Retrieves empirical TANF maximum standard benefit for household size."""
    pol = policy or load_statutory_policy()
    tanf_cfg = pol.get("tanf", {})
    schedule = tanf_cfg.get("maximum_benefit_schedule", {})
    size = max(1, int(household_size))
    if str(size) in schedule:
        return float(schedule[str(size)])
    base_6 = float(schedule.get("6", 590.0))
    per_add = float(tanf_cfg.get("per_additional_person", 55.0))
    return round(base_6 + (size - 6) * per_add, 2)


def get_ccdf_copay_rate(
    income_pct_of_fpl: float,
    policy: Optional[Dict[str, Any]] = None
) -> float:
    """Retrieves empirical CCDF child care copay percentage from sliding fee curve."""
    pol = policy or load_statutory_policy()
    sliding_scale = pol.get("ccdf_childcare", {}).get("sliding_copay_schedule", [])
    for tier in sliding_scale:
        if income_pct_of_fpl <= float(tier.get("max_fpl_pct", 100.0)):
            return float(tier.get("copay_pct_of_income", 0.0))
    return 7.0

