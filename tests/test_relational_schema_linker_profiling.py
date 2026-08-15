"""
Unit test suite for Frontier Data Studio: Multi-Hop BFS Relational Linker,
Inclusion Dependency (IND), Deep Cleansing, and 0-100% Data Quality Scorecard.
"""

import pytest
from src.domain.polymorphic_data_orchestrator import provision_dynamic_dataset
from src.domain.relational_schema_linker import (
    normalize_column_name,
    calculate_inclusion_dependency,
    classify_cardinality,
    plan_multi_hop_join_path,
    synthesize_multi_table_join,
    discover_foreign_key_relationships
)
from src.domain.client_data_cleaner import (
    standardize_phone_number,
    standardize_state_or_zip,
    standardize_boolean_value,
    levenshtein_similarity,
    cleanse_client_dataset
)
from src.domain.statistical_data_profiler import (
    calculate_10_bin_histogram,
    calculate_spearman_correlation,
    compute_data_quality_scorecard,
    profile_client_dataset
)


def test_phone_state_boolean_standardization():
    assert standardize_phone_number("(555) 234-5678") == "+15552345678"
    assert standardize_phone_number("555.234.5678") == "+15552345678"
    assert standardize_phone_number("+1 555-234-5678") == "+15552345678"

    assert standardize_state_or_zip("customer_state", "california") == "CA"
    assert standardize_state_or_zip("postal_zip", "1234") == "01234"

    assert standardize_boolean_value("yes") == 1
    assert standardize_boolean_value("ACTIVE") == 1
    assert standardize_boolean_value("no") == 0


def test_levenshtein_and_fuzzy_similarity():
    sim_exact = levenshtein_similarity("Acme Corp", "Acme Corp")
    assert sim_exact == 1.0

    sim_typo = levenshtein_similarity("Acme Corporation", "Acme Corporaton")
    assert sim_typo > 0.90


def test_inclusion_dependency_and_multi_hop_join():
    # 1. Ingest Table 1: Divisions
    div_csv = """dept_code,division_name
ENG,Engineering
SALES,Sales & Growth
"""
    provision_dynamic_dataset("frontier_divisions", div_csv)

    # 2. Ingest Table 2: Employees (with different column name 'dept_id')
    emp_csv = """emp_id,name,dept_id,phone
E-101,Alice,ENG,(555) 111-2222
E-102,Bob,SALES,555.333.4444
"""
    provision_dynamic_dataset("frontier_employees", emp_csv)

    # Calculate Inclusion Dependency
    cont, jacc = calculate_inclusion_dependency(
        "client_data_frontier_divisions", "dept_code",
        "client_data_frontier_employees", "dept_id"
    )
    assert cont == 1.0  # All division codes exist in employees

    # Discover foreign keys
    rels = discover_foreign_key_relationships()
    assert len(rels) > 0

    # Multi-hop join synthesis
    join_res = synthesize_multi_table_join("Join divisions and employees", ["frontier_divisions", "frontier_employees"])
    assert join_res["status"] == "success"
    assert join_res["row_count"] == 2


def test_group_conditioned_cleansing():
    dirty_data = """employee,department,salary,active
Alice,Engineering,$150000,yes
Bob,Engineering,,true
Charlie,Sales,$80000,1
Dave,Sales,,y
"""
    provision_dynamic_dataset("dept_salaries", dirty_data)

    clean_res = cleanse_client_dataset("dept_salaries")
    assert clean_res["status"] == "success"
    assert clean_res["imputed_missing_values"] == 2
    assert clean_res["conditioned_imputation_group"] == "department"


def test_histograms_spearman_and_quality_scorecard():
    hist = calculate_10_bin_histogram([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 10, 100)
    assert len(hist) == 10

    # Spearman rank correlation
    spearman_r = calculate_spearman_correlation([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])
    assert spearman_r == 1.0

    profile_res = profile_client_dataset("dept_salaries")
    assert profile_res["status"] == "success"
    scorecard = profile_res["data_quality_scorecard"]
    assert scorecard["overall_quality_score"] > 80.0
    assert scorecard["grade"] in ("A+", "A", "B")
