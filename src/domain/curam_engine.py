"""
IBM Cúram Social Program Management (SPM) & Cúram Express Rules (CER) Engine.
Standard: Pure Python Standard Library (json, hashlib, time, datetime, math).
Grounded in Empirical Policy Datasets (HHS, USDA, ACF, HUD).
Eliminates static magic numbers by consuming dynamic, versioned statutory data.
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.domain.statutory_data import (
    load_statutory_policy,
    get_fpl_monthly,
    get_snap_max_allotment,
    get_snap_standard_deduction,
    get_tanf_max_benefit,
    get_ccdf_copay_rate
)


# Empirical Statutory Constants for Backward Compatibility
FPL_ANNUAL_BASE_2026 = 15650.0
FPL_ANNUAL_PER_PERSON_2026 = 5520.0
SNAP_MAX_ALLOTMENTS_2026 = {1: 292.0, 2: 536.0, 3: 768.0, 4: 975.0, 5: 1158.0, 6: 1390.0, 7: 1536.0, 8: 1756.0}
TANF_MAX_BENEFITS_2026 = {1: 240.0, 2: 320.0, 3: 390.0, 4: 460.0, 5: 530.0, 6: 590.0}


def get_monthly_fpl(household_size: int, region: str = "contiguous_48_and_dc", policy: Optional[Dict[str, Any]] = None) -> float:
    """Calculate the 100% Monthly Federal Poverty Level for a given household size from empirical tables."""
    return get_fpl_monthly(household_size, region=region, policy=policy)


class CuramExpressRulesEngine:
    """
    Simulates the IBM Cúram Express Rules (CER) Engine.
    Evaluates citizen evidence against empirical statutory policy to determine Eligibility and Entitlement.
    """

    @staticmethod
    def evaluate_medicaid_magi(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Medicaid Modified Adjusted Gross Income (MAGI) Eligibility."""
        pol = policy or load_statutory_policy()
        med_cfg = pol.get("medicaid_magi", {})

        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income
        
        is_resident = bool(evidence.get("is_resident", True))
        has_qualified_status = bool(evidence.get("has_qualified_immigration_status", True))
        is_child = bool(evidence.get("is_child_under_19", False))
        is_pregnant = bool(evidence.get("is_pregnant", False))
        has_disability = bool(evidence.get("has_disability", False))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        disregard_5pct = monthly_100_fpl * 0.05 if med_cfg.get("statutory_5pct_disregard", True) else 0.0
        countable_income = max(0.0, gross_income - disregard_5pct)

        if is_child or is_pregnant:
            threshold_pct = float(med_cfg.get("children_pregnancy_fpl_pct", 200.0))
            category = "Medicaid Children & Pregnancy (CHIP/MAGI 200%)"
        elif has_disability:
            threshold_pct = float(med_cfg.get("abd_disability_fpl_pct", 150.0))
            category = "Medicaid Aged, Blind, and Disabled (ABD 150%)"
        else:
            threshold_pct = float(med_cfg.get("adult_expansion_fpl_pct", 138.0))
            category = "Medicaid MAGI Adult Expansion (138%)"

        max_allowed_income = round(monthly_100_fpl * (threshold_pct / 100.0), 2)
        income_pct_of_fpl = round((countable_income / monthly_100_fpl) * 100.0, 1) if monthly_100_fpl > 0 else 0.0

        income_eligible = countable_income <= max_allowed_income
        eligible = income_eligible and is_resident and has_qualified_status

        reason_codes = []
        if not income_eligible:
            reason_codes.append(f"Excess Countable Income (${countable_income:.2f} exceeds limit of ${max_allowed_income:.2f})")
        if not is_resident:
            reason_codes.append("Failed State Residency Verification")
        if not has_qualified_status:
            reason_codes.append("Citizenship or Immigration Status Not Verified")
        if eligible:
            reason_codes.append("Met all statutory MAGI financial and non-financial requirements")

        return {
            "program": "MEDICAID_MAGI",
            "category": category,
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "statutory_threshold_pct": threshold_pct,
            "countable_monthly_income": countable_income,
            "monthly_100_fpl": monthly_100_fpl,
            "max_allowed_income": max_allowed_income,
            "income_pct_of_fpl": income_pct_of_fpl,
            "disregard_applied": round(disregard_5pct, 2),
            "reason_codes": reason_codes,
            "evidence_snapshot": evidence
        }

    @staticmethod
    def evaluate_chip(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Children's Health Insurance Program (CHIP)."""
        pol = policy or load_statutory_policy()
        chip_cfg = pol.get("chip", {})
        
        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income
        
        is_child = bool(evidence.get("is_child_under_19", True))
        is_infant = bool(evidence.get("is_infant_under_1", False))
        is_uninsured = bool(evidence.get("is_uninsured", True))
        is_resident = bool(evidence.get("is_resident", True))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        disregard_5pct = monthly_100_fpl * 0.05
        countable_income = max(0.0, gross_income - disregard_5pct)

        threshold_pct = float(chip_cfg.get("infant_under_1_fpl_pct", 300.0)) if is_infant else float(chip_cfg.get("default_fpl_pct", 250.0))
        max_allowed_income = round(monthly_100_fpl * (threshold_pct / 100.0), 2)
        income_eligible = countable_income <= max_allowed_income

        eligible = is_child and is_uninsured and is_resident and income_eligible

        reason_codes = []
        if not is_child:
            reason_codes.append("Individual is not a child under age 19")
        if not is_uninsured:
            reason_codes.append("Individual has other creditable comprehensive health coverage")
        if not income_eligible:
            reason_codes.append(f"Income (${countable_income:.2f}) exceeds CHIP limit (${max_allowed_income:.2f})")
        if eligible:
            reason_codes.append(f"Approved for CHIP coverage at {threshold_pct}% FPL")

        return {
            "program": "CHIP",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "statutory_threshold_pct": threshold_pct,
            "countable_monthly_income": countable_income,
            "max_allowed_income": max_allowed_income,
            "monthly_100_fpl": monthly_100_fpl,
            "reason_codes": reason_codes
        }

    @staticmethod
    def evaluate_snap(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Supplemental Nutrition Assistance Program (SNAP)."""
        pol = policy or load_statutory_policy()
        snap_cfg = pol.get("snap", {})

        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income

        shelter_cost = float(evidence.get("shelter_cost_monthly", 0.0))
        utility_cost = float(evidence.get("utility_standard_monthly", snap_cfg.get("standard_utility_allowance", 150.0)))
        total_shelter = shelter_cost + utility_cost
        
        liquid_assets = float(evidence.get("liquid_assets", 0.0))
        has_elderly_or_disabled = bool(evidence.get("has_elderly_or_disabled_member", False))
        is_resident = bool(evidence.get("is_resident", True))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        gross_income_limit = round(monthly_100_fpl * (float(snap_cfg.get("gross_income_fpl_pct", 130.0)) / 100.0), 2)
        net_income_limit = round(monthly_100_fpl * (float(snap_cfg.get("net_income_fpl_pct", 100.0)) / 100.0), 2)

        # Asset test
        max_assets = float(snap_cfg.get("asset_limit_elderly_disabled", 4500.0)) if has_elderly_or_disabled else float(snap_cfg.get("asset_limit_standard", 3000.0))
        asset_eligible = liquid_assets <= max_assets

        # Deductions
        earned_disregard = earned_income * (float(snap_cfg.get("earned_income_disregard_pct", 20.0)) / 100.0)
        standard_ded = get_snap_standard_deduction(hh_size, policy=pol)
        adjusted_income = max(0.0, gross_income - earned_disregard - standard_ded)

        half_adjusted = adjusted_income * (float(snap_cfg.get("shelter_percentage_threshold", 50.0)) / 100.0)
        excess_shelter = max(0.0, total_shelter - half_adjusted)
        
        excess_shelter_cap = float(snap_cfg.get("excess_shelter_cap", 672.0))
        if not has_elderly_or_disabled:
            excess_shelter = min(excess_shelter, excess_shelter_cap)

        net_income = max(0.0, adjusted_income - excess_shelter)

        # Gross & Net test
        gross_passed = (gross_income <= gross_income_limit) or has_elderly_or_disabled
        net_passed = net_income <= net_income_limit
        eligible = gross_passed and net_passed and asset_eligible and is_resident

        # Allotment calculation
        max_allotment = get_snap_max_allotment(hh_size, policy=pol)
        expected_food_contrib = net_income * 0.30
        calculated_allotment = max(0.0, max_allotment - expected_food_contrib)
        
        min_allotment = float(snap_cfg.get("minimum_allotment_1_to_2", 23.0))
        if eligible and hh_size in (1, 2) and calculated_allotment < min_allotment:
            final_allotment = min_allotment
        else:
            final_allotment = round(calculated_allotment, 2) if eligible else 0.0

        reason_codes = []
        if not gross_passed:
            reason_codes.append(f"Gross income (${gross_income:.2f}) exceeds 130% FPL limit (${gross_income_limit:.2f})")
        if not net_passed:
            reason_codes.append(f"Net income (${net_income:.2f}) exceeds 100% FPL limit (${net_income_limit:.2f})")
        if not asset_eligible:
            reason_codes.append(f"Liquid assets (${liquid_assets:.2f}) exceed resource cap of ${max_assets:.2f}")
        if eligible:
            reason_codes.append(f"Eligible for Monthly SNAP Allotment of ${final_allotment:.2f}")

        return {
            "program": "SNAP",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "monthly_benefit_allotment": final_allotment,
            "max_possible_allotment": max_allotment,
            "gross_income": gross_income,
            "gross_limit_130_fpl": gross_income_limit,
            "net_countable_income": round(net_income, 2),
            "net_limit_100_fpl": net_income_limit,
            "deductions": {
                "standard_deduction": standard_ded,
                "earned_income_disregard": round(earned_disregard, 2),
                "excess_shelter_deduction": round(excess_shelter, 2)
            },
            "reason_codes": reason_codes
        }

    @staticmethod
    def evaluate_tanf(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Temporary Assistance for Needy Families (TANF) Cash Assistance."""
        pol = policy or load_statutory_policy()
        tanf_cfg = pol.get("tanf", {})

        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income

        liquid_assets = float(evidence.get("liquid_assets", 0.0))
        has_minor_child = bool(evidence.get("has_minor_child", False))
        is_pregnant = bool(evidence.get("is_pregnant", False))
        months_received = int(evidence.get("tanf_lifetime_months_received", 0))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        deprivation_met = has_minor_child or is_pregnant
        
        max_assets = float(tanf_cfg.get("asset_limit", 2500.0))
        asset_eligible = liquid_assets <= max_assets
        
        max_lifetime = int(tanf_cfg.get("lifetime_limit_months", 60))
        lifetime_limit_ok = months_received < max_lifetime

        initial_disregard = float(tanf_cfg.get("earned_income_disregard_initial", 90.0))
        ongoing_disregard_pct = float(tanf_cfg.get("earned_income_disregard_ongoing_pct", 30.0)) / 100.0
        countable_earned = max(0.0, earned_income - initial_disregard) * (1.0 - ongoing_disregard_pct)
        countable_income = countable_earned + unearned_income

        max_benefit = get_tanf_max_benefit(hh_size, policy=pol)
        income_eligible = countable_income < max_benefit
        eligible = deprivation_met and asset_eligible and lifetime_limit_ok and income_eligible

        cash_grant = max(0.0, round(max_benefit - countable_income, 2)) if eligible else 0.0

        reason_codes = []
        if not deprivation_met:
            reason_codes.append("Deprivation requirement not met (No qualifying minor child or pregnancy)")
        if not asset_eligible:
            reason_codes.append(f"Assets (${liquid_assets:.2f}) exceed TANF cap of ${max_assets:.2f}")
        if not lifetime_limit_ok:
            reason_codes.append(f"Exceeded {max_lifetime}-month TANF lifetime benefit limit")
        if not income_eligible:
            reason_codes.append(f"Countable income (${countable_income:.2f}) exceeds max grant (${max_benefit:.2f})")
        if eligible:
            reason_codes.append(f"Eligible for Monthly TANF Cash Assistance Grant of ${cash_grant:.2f}")

        return {
            "program": "TANF",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "monthly_cash_grant": cash_grant,
            "max_standard_grant": max_benefit,
            "countable_income": round(countable_income, 2),
            "lifetime_months_remaining": max(0, max_lifetime - months_received),
            "reason_codes": reason_codes
        }

    @staticmethod
    def evaluate_wic(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Special Supplemental Nutrition Program for Women, Infants, and Children (WIC)."""
        pol = policy or load_statutory_policy()
        wic_cfg = pol.get("wic", {})

        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income

        is_pregnant = bool(evidence.get("is_pregnant", False))
        is_postpartum = bool(evidence.get("is_postpartum", False))
        is_breastfeeding = bool(evidence.get("is_breastfeeding", False))
        is_infant = bool(evidence.get("is_infant_under_1", False))
        is_child_under_5 = bool(evidence.get("is_child_under_5", False))

        target_population = is_pregnant or is_postpartum or is_breastfeeding or is_infant or is_child_under_5

        # Adjunctive eligibility: Receiving Medicaid or SNAP makes client income-eligible for WIC automatically
        is_adjunctively_eligible = bool(evidence.get("receiving_medicaid", False) or evidence.get("receiving_snap", False) or evidence.get("receiving_tanf", False))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        threshold_pct = float(wic_cfg.get("income_limit_fpl_pct", 185.0))
        max_income = round(monthly_100_fpl * (threshold_pct / 100.0), 2)
        income_eligible = (gross_income <= max_income) or is_adjunctively_eligible

        nutritional_risk = bool(evidence.get("has_nutritional_risk", True)) # Standard presumptive clinic screening
        eligible = target_population and income_eligible and nutritional_risk

        priority_tier = "PRIORITY_I" if (is_pregnant or is_breastfeeding) else ("PRIORITY_II" if is_infant else "PRIORITY_III")

        reason_codes = []
        if not target_population:
            reason_codes.append("Individual is not within WIC categorical groups (Pregnant, Postpartum, Infant, Child < 5)")
        if not income_eligible:
            reason_codes.append(f"Gross income (${gross_income:.2f}) exceeds 185% FPL limit (${max_income:.2f})")
        if eligible:
            reason_codes.append(f"Approved for WIC Nutrition Package ({priority_tier}: {wic_cfg.get('priority_tiers', {}).get(priority_tier, 'Nutritional Support')})")

        return {
            "program": "WIC",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "target_population_verified": target_population,
            "adjunctively_eligible": is_adjunctively_eligible,
            "statutory_threshold_pct": threshold_pct,
            "priority_tier": priority_tier if eligible else None,
            "max_allowed_income": max_income,
            "reason_codes": reason_codes
        }

    @staticmethod
    def evaluate_ccdf(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: Child Care and Development Fund (CCDF) Subsidies."""
        pol = policy or load_statutory_policy()
        ccdf_cfg = pol.get("ccdf_childcare", {})

        hh_size = int(evidence.get("household_size", 1))
        region = str(evidence.get("region", "contiguous_48_and_dc"))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income

        has_child_under_13 = bool(evidence.get("has_child_under_13", True))
        is_working_or_training = bool(evidence.get("is_working_or_training", True))

        monthly_100_fpl = get_fpl_monthly(hh_size, region=region, policy=pol)
        smi_monthly = float(ccdf_cfg.get("state_median_income_monthly", 6800.0))
        smi_limit = smi_monthly * (float(ccdf_cfg.get("smi_limit_pct", 85.0)) / 100.0)
        fpl_limit = monthly_100_fpl * (float(ccdf_cfg.get("fpl_limit_pct", 200.0)) / 100.0)

        income_eligible = gross_income <= min(smi_limit, fpl_limit)
        eligible = has_child_under_13 and is_working_or_training and income_eligible

        income_pct_of_fpl = (gross_income / monthly_100_fpl) * 100.0 if monthly_100_fpl > 0 else 0.0
        copay_rate_pct = get_ccdf_copay_rate(income_pct_of_fpl, policy=pol)
        monthly_family_copay = round(gross_income * (copay_rate_pct / 100.0), 2) if eligible else 0.0

        reason_codes = []
        if not has_child_under_13:
            reason_codes.append("No qualifying child under age 13 residing in household")
        if not is_working_or_training:
            reason_codes.append("Parents/guardians do not meet work or educational activity requirements")
        if not income_eligible:
            reason_codes.append(f"Income (${gross_income:.2f}) exceeds CCDF 85% SMI limit (${smi_limit:.2f})")
        if eligible:
            reason_codes.append(f"Approved for Child Care Subsidy with {copay_rate_pct}% sliding copayment (${monthly_family_copay:.2f}/mo)")

        return {
            "program": "CCDF_CHILDCARE",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "copay_rate_percentage": copay_rate_pct,
            "monthly_family_copay": monthly_family_copay,
            "income_pct_of_fpl": round(income_pct_of_fpl, 1),
            "max_allowed_income": round(min(smi_limit, fpl_limit), 2),
            "reason_codes": reason_codes
        }

    @staticmethod
    def evaluate_section8(evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """CER RuleSet: HUD Section 8 Housing Choice Voucher & Tenant Rent Contribution."""
        pol = policy or load_statutory_policy()
        sec8_cfg = pol.get("section8_housing", {})

        hh_size = int(evidence.get("household_size", 1))
        earned_income = float(evidence.get("earned_income_monthly", 0.0))
        unearned_income = float(evidence.get("unearned_income_monthly", 0.0))
        gross_income = earned_income + unearned_income

        bedrooms = str(evidence.get("bedrooms", "2"))
        actual_rent = float(evidence.get("contract_rent_monthly", 1450.0))

        ami = float(sec8_cfg.get("area_median_income_monthly", 6500.0))
        very_low_income_limit = ami * (float(sec8_cfg.get("income_brackets_pct_of_ami", {}).get("very_low_income", 50.0)) / 100.0)

        income_eligible = gross_income <= very_low_income_limit
        is_resident = bool(evidence.get("is_resident", True))
        eligible = income_eligible and is_resident

        # Tenant contribution = 30% of monthly adjusted income
        tenant_contrib_pct = float(sec8_cfg.get("tenant_rent_contribution_pct", 30.0)) / 100.0
        min_tenant_pay = float(sec8_cfg.get("minimum_tenant_payment", 50.0))
        calculated_tenant_rent = max(min_tenant_pay, round(gross_income * tenant_contrib_pct, 2))
        
        payment_standard = float(sec8_cfg.get("payment_standard_by_bedrooms", {}).get(bedrooms, 1650.0))
        eligible_rent = min(actual_rent, payment_standard)
        housing_assistance_payment = max(0.0, round(eligible_rent - calculated_tenant_rent, 2)) if eligible else 0.0

        reason_codes = []
        if not income_eligible:
            reason_codes.append(f"Income (${gross_income:.2f}) exceeds HUD 50% AMI limit (${very_low_income_limit:.2f})")
        if eligible:
            reason_codes.append(f"Approved for Housing Choice Voucher (HAP: ${housing_assistance_payment:.2f}, Tenant Rent: ${calculated_tenant_rent:.2f})")

        return {
            "program": "SECTION8_HOUSING",
            "eligible": eligible,
            "decision_code": "APPROVED" if eligible else "DENIED",
            "housing_assistance_payment": housing_assistance_payment,
            "tenant_rent_contribution": calculated_tenant_rent if eligible else 0.0,
            "payment_standard": payment_standard,
            "ami_limit_50pct": very_low_income_limit,
            "reason_codes": reason_codes
        }

    @classmethod
    def evaluate_integrated_case(cls, evidence: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluates a single citizen integrated case across all 7 statutory social benefit programs.
        Simulates Cúram SPM Product Delivery Case (PDC) multi-program decisioning.
        """
        t0 = time.perf_counter()
        pol = policy or load_statutory_policy()

        medicaid = cls.evaluate_medicaid_magi(evidence, policy=pol)
        chip = cls.evaluate_chip(evidence, policy=pol)
        snap = cls.evaluate_snap(evidence, policy=pol)
        tanf = cls.evaluate_tanf(evidence, policy=pol)
        
        # Cross-program adjunctive evidence pass
        evidence_with_adjunct = dict(evidence)
        evidence_with_adjunct["receiving_medicaid"] = medicaid["eligible"]
        evidence_with_adjunct["receiving_snap"] = snap["eligible"]
        evidence_with_adjunct["receiving_tanf"] = tanf["eligible"]

        wic = cls.evaluate_wic(evidence_with_adjunct, policy=pol)
        ccdf = cls.evaluate_ccdf(evidence, policy=pol)
        sec8 = cls.evaluate_section8(evidence, policy=pol)

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        approved_programs = []
        if medicaid["eligible"]: approved_programs.append("MEDICAID_MAGI")
        if chip["eligible"]: approved_programs.append("CHIP")
        if snap["eligible"]: approved_programs.append("SNAP")
        if tanf["eligible"]: approved_programs.append("TANF")
        if wic["eligible"]: approved_programs.append("WIC")
        if ccdf["eligible"]: approved_programs.append("CCDF_CHILDCARE")
        if sec8["eligible"]: approved_programs.append("SECTION8_HOUSING")

        total_financial_value = (
            snap.get("monthly_benefit_allotment", 0.0) +
            tanf.get("monthly_cash_grant", 0.0) +
            sec8.get("housing_assistance_payment", 0.0)
        )

        return {
            "status": "success",
            "case_reference": evidence.get("case_reference", f"CURAM-IC-{int(time.time())}"),
            "applicant_name": evidence.get("applicant_name", "Anonymous Citizen"),
            "household_size": int(evidence.get("household_size", 1)),
            "evaluation_duration_ms": duration_ms,
            "policy_version": pol.get("metadata", {}).get("version", "2026.1"),
            "approved_programs_count": len(approved_programs),
            "approved_programs": approved_programs,
            "total_monthly_cash_and_nutrition_value": round(total_financial_value, 2),
            "programs": {
                "medicaid_magi": medicaid,
                "chip": chip,
                "snap": snap,
                "tanf": tanf,
                "wic": wic,
                "ccdf_childcare": ccdf,
                "section8_housing": sec8
            },
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
