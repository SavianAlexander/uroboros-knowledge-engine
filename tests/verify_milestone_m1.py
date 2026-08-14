"""
Empirical Verification & Stress Test Harness for Milestone M1.
Challenger 2 Verification Protocol.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import math
import random
from datetime import datetime, date, timedelta

from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    compute_authority_weighted_rrf,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)
from src.domain.temporal_validity import (
    detect_temporal_validity,
    compute_temporal_decay,
    DOMAIN_HALF_LIVES,
    STATUS_PENALTY_CAPS,
    SUPERSEDING_PATTERNS
)
from src.domain.grounded_retrieval_engine import GroundedRetrievalEngine


def test_monotonicity_of_temporal_decay():
    print("\n--- [TEST 1] Monotonicity of Temporal Decay (Phi_temporal) ---")
    domains = list(DOMAIN_HALF_LIVES.keys()) + ["unknown_domain", None]
    statuses = list(STATUS_PENALTY_CAPS.keys()) + ["UNKNOWN_STATUS", None]
    
    total_checks = 0
    monotonicity_violations = 0
    bound_violations = 0
    
    now = datetime.now()
    
    for dom in domains:
        for stat in statuses:
            cap = STATUS_PENALTY_CAPS.get((stat or "ACTIVE").upper(), 1.00)
            floor = 0.05
            
            prev_decay = 1.05
            
            # Dense grid: 0 to 50 years at 0.05 year increments (1000 points)
            for i in range(1001):
                dt_years = i * 0.05
                # Create date corresponding to dt_years ago
                past_date = now.date() - timedelta(days=int(dt_years * 365.25))
                
                decay = compute_temporal_decay(
                    document_year_or_date=past_date,
                    domain=dom,
                    status=stat
                )
                
                total_checks += 1
                
                # Check bounds
                if not (floor - 1e-6 <= decay <= cap + 1e-6):
                    print(f"FAILED BOUND: dom={dom}, stat={stat}, dt={dt_years}, decay={decay}, cap={cap}, floor={floor}")
                    bound_violations += 1
                
                # Check monotonicity: as dt increases, decay must NOT increase (must be <= prev_decay)
                if decay > prev_decay + 1e-6:
                    print(f"FAILED MONOTONICITY: dom={dom}, stat={stat}, dt={dt_years}: decay={decay} > prev_decay={prev_decay}")
                    monotonicity_violations += 1
                    
                prev_decay = decay

            # Test extreme long range: 50 to 5000 years
            for dt_years in [100, 200, 500, 1000, 5000]:
                decay = compute_temporal_decay(
                    document_year_or_date=now.year - dt_years,
                    domain=dom,
                    status=stat
                )
                total_checks += 1
                if decay > prev_decay + 1e-6:
                    print(f"FAILED MONOTONICITY (EXTREME): dom={dom}, stat={stat}, dt={dt_years}")
                    monotonicity_violations += 1
                if decay < floor - 1e-6:
                    print(f"FAILED FLOOR: decay={decay} < floor={floor}")
                    bound_violations += 1
                prev_decay = decay
                
    print(f"Total Monotonicity & Bound checks performed: {total_checks}")
    print(f"Monotonicity violations: {monotonicity_violations}")
    print(f"Bound violations: {bound_violations}")
    assert monotonicity_violations == 0, f"{monotonicity_violations} monotonicity violations found!"
    assert bound_violations == 0, f"{bound_violations} bound violations found!"
    print(">>> PASS: Temporal decay is strictly non-increasing across all tested parameter spaces.")


def test_epistemic_tier_dominance():
    print("\n--- [TEST 2] Epistemic Tier 1 Dominance over Tier 4 under Identical RRF Ranks ---")
    ranks_to_test = [1, 2, 5, 10, 20, 50, 100, 200, 500]
    k_values = [1, 10, 60, 100]
    weight_combos = [
        {"lexical": 0.5, "dense": 0.5},
        {"lexical": 1.0, "dense": 0.0},
        {"lexical": 0.0, "dense": 1.0},
        {"lexical": 0.7, "dense": 0.3}
    ]
    staleness_values = [1.0, 0.8, 0.5, 0.4, 0.1, 0.05]
    
    total_checks = 0
    dominance_violations = 0
    hierarchy_violations = 0
    
    for r in ranks_to_test:
        for k in k_values:
            for w in weight_combos:
                for phi in staleness_values:
                    # Construct 4 candidates with identical ranks and identical staleness
                    c1 = {
                        "id": "t1_doc",
                        "filename": "statute.txt",
                        "epistemic_tier": TIER_1_PRIMARY,
                        "epistemic_weight": TIER_WEIGHTS[TIER_1_PRIMARY],
                        "staleness_coefficient": phi,
                        "rank": r
                    }
                    c2 = {
                        "id": "t2_doc",
                        "filename": "spec.md",
                        "epistemic_tier": TIER_2_TECH_SPEC,
                        "epistemic_weight": TIER_WEIGHTS[TIER_2_TECH_SPEC],
                        "staleness_coefficient": phi,
                        "rank": r
                    }
                    c3 = {
                        "id": "t3_doc",
                        "filename": "textbook.pdf",
                        "epistemic_tier": TIER_3_SECONDARY,
                        "epistemic_weight": TIER_WEIGHTS[TIER_3_SECONDARY],
                        "staleness_coefficient": phi,
                        "rank": r
                    }
                    c4 = {
                        "id": "t4_doc",
                        "filename": "scratchpad.txt",
                        "epistemic_tier": TIER_4_COMMENTARY,
                        "epistemic_weight": TIER_WEIGHTS[TIER_4_COMMENTARY],
                        "staleness_coefficient": phi,
                        "rank": r
                    }
                    
                    lexical = [c4, c3, c2, c1]  # inserted in inverse order to test sorting stability
                    dense = [c4, c3, c2, c1]
                    
                    fused = compute_authority_weighted_rrf(
                        lexical_ranks=lexical,
                        dense_ranks=dense,
                        k=k,
                        intent_weights=w
                    )
                    
                    total_checks += 1
                    
                    # 1. Tier 1 must strictly outrank Tier 4
                    t1_res = next(x for x in fused if x["id"] == "t1_doc")
                    t4_res = next(x for x in fused if x["id"] == "t4_doc")
                    
                    if t1_res["grounded_score"] <= t4_res["grounded_score"] or t1_res["final_rank"] >= t4_res["final_rank"]:
                        print(f"FAILED TIER 1 > TIER 4: r={r}, k={k}, w={w}, phi={phi}: t1={t1_res['grounded_score']} (rank {t1_res['final_rank']}) vs t4={t4_res['grounded_score']} (rank {t4_res['final_rank']})")
                        dominance_violations += 1
                    
                    # 2. Strict Full Hierarchy: Tier 1 > Tier 2 > Tier 3 > Tier 4
                    t2_res = next(x for x in fused if x["id"] == "t2_doc")
                    t3_res = next(x for x in fused if x["id"] == "t3_doc")
                    
                    is_monotonic_hierarchy = (
                        t1_res["grounded_score"] > t2_res["grounded_score"] > t3_res["grounded_score"] > t4_res["grounded_score"] and
                        t1_res["final_rank"] < t2_res["final_rank"] < t3_res["final_rank"] < t4_res["final_rank"]
                    )
                    if not is_monotonic_hierarchy:
                        print(f"FAILED FULL HIERARCHY: r={r}, k={k}, w={w}, phi={phi}")
                        hierarchy_violations += 1

    print(f"Total Tier Dominance checks performed: {total_checks}")
    print(f"Tier 1 vs Tier 4 violations: {dominance_violations}")
    print(f"Full Hierarchy (T1 > T2 > T3 > T4) violations: {hierarchy_violations}")
    assert dominance_violations == 0, f"{dominance_violations} Tier 1 dominance violations found!"
    assert hierarchy_violations == 0, f"{hierarchy_violations} Hierarchy violations found!"
    print(">>> PASS: Epistemic Tier 1 strictly and unconditionally outranks Tier 4 given identical RRF ordinal ranks.")


def test_superseded_hard_cap_enforcement():
    print("\n--- [TEST 3] Superseded Document Hard Cap (<= 0.40) Enforcement ---")
    
    total_checks = 0
    cap_violations = 0
    
    now = datetime.now()
    
    # 1. Direct compute_temporal_decay checks across all domains and years
    domains = list(DOMAIN_HALF_LIVES.keys()) + [None, "arbitrary"]
    years = [now.year, now.year + 1, now.year - 1, 2020, 2010, 2000, 1990, 1970, 1900]
    half_lives = [0.1, 1.0, 5.0, 10.0, 365.25, 1000.0, None]
    
    for dom in domains:
        for yr in years:
            for hl in half_lives:
                decay = compute_temporal_decay(
                    document_year_or_date=yr,
                    domain=dom,
                    status="SUPERSEDED",
                    half_life_days=hl
                )
                total_checks += 1
                if decay > 0.400001:
                    print(f"FAILED SUPERSEDED CAP: dom={dom}, yr={yr}, hl={hl}, decay={decay}")
                    cap_violations += 1

    # 2. Text marker superseding parsing checks
    test_snippets = [
        "This standard is superseded by ISO 27001:2022.",
        "Obsoletes: RFC 7230, RFC 7231",
        "This implementation is obsoleted by kernel v6.1.",
        "Module replaced by new crypto engine v2.",
        "Rendered obsolete by executive order 14028.",
        "Deprecated in v2.0 and superseded by v3.0.",
    ]
    
    for snip in test_snippets:
        res = detect_temporal_validity(snip, publication_year=now.year)
        total_checks += 1
        if not res["is_superseded"]:
            print(f"FAILED SUPERSEDED DETECTION: snippet='{snip}'")
            cap_violations += 1
        if res["temporal_status"] != "SUPERSEDED":
            print(f"FAILED STATUS: expected SUPERSEDED, got {res['temporal_status']}")
            cap_violations += 1
        if res["staleness_coefficient"] > 0.400001:
            print(f"FAILED CAP: staleness={res['staleness_coefficient']} > 0.40")
            cap_violations += 1

    print(f"Total Superseded Cap checks performed: {total_checks}")
    print(f"Superseded Cap violations: {cap_violations}")
    assert cap_violations == 0, f"{cap_violations} Superseded hard cap violations found!"
    print(">>> PASS: Superseded documents never exceed the hard cap <= 0.40 under any conditions.")


def test_extreme_boundary_and_stress_cases():
    print("\n--- [TEST 4] Extreme Boundary and Stress Cases ---")
    
    # Negative time delta (future dates)
    decay_future = compute_temporal_decay(datetime.now().year + 5, status="ACTIVE")
    assert decay_future == 1.0, f"Future date decay should be capped at 1.0, got {decay_future}"
    
    decay_future_superseded = compute_temporal_decay(datetime.now().year + 5, status="SUPERSEDED")
    assert decay_future_superseded <= 0.40, f"Future superseded date should be capped at 0.40, got {decay_future_superseded}"
    
    # Empty inputs
    t_empty, w_empty = classify_source_epistemic_tier("")
    assert t_empty == TIER_4_COMMENTARY
    assert w_empty == 0.35
    
    # GroundedRetrievalEngine evaluation on empty and low-authority candidates
    engine = GroundedRetrievalEngine(top_k=5, refusal_threshold=0.65)
    
    # 1. Zero evidence -> refusal
    r0 = engine.evaluate_grounding("test query", [])
    assert r0["status"] == "refusal"
    assert r0["overall_grounded_confidence"] == 0.0
    
    # 2. Only Tier 4 commentary -> confidence should be below 0.65 -> refusal
    t4_candidates = [
        {"id": f"t4_{i}", "filename": f"scratchpad_{i}.txt", "content": "random notes", "rank": i+1}
        for i in range(3)
    ]
    r_t4 = engine.evaluate_grounding("test query", t4_candidates)
    assert r_t4["status"] == "refusal"
    assert r_t4["overall_grounded_confidence"] < 0.65
    
    # 3. High quality Tier 1 active candidates -> success
    t1_candidates = [
        {"id": f"t1_{i}", "filename": f"rfc911{i}_spec.pdf", "content": "Standard specifications 100tps", "rank": i+1}
        for i in range(3)
    ]
    r_t1 = engine.evaluate_grounding("test query", t1_candidates)
    assert r_t1["status"] == "success"
    assert r_t1["overall_grounded_confidence"] >= 0.65
    
    print(">>> PASS: All boundary and stress conditions behaved as specified.")


if __name__ == "__main__":
    print("================================================================================")
    print("RUNNING CHALLENGER 2 EMPIRICAL VERIFICATION HARNESS FOR MILESTONE M1")
    print("================================================================================")
    test_monotonicity_of_temporal_decay()
    test_epistemic_tier_dominance()
    test_superseded_hard_cap_enforcement()
    test_extreme_boundary_and_stress_cases()
    print("================================================================================")
    print("ALL EMPIRICAL VERIFICATIONS PASSED WITH 0 FAILURES.")
    print("================================================================================")
