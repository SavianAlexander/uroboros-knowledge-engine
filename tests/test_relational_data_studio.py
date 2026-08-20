"""
Unit test suite for Next-Gen Relational Schema Linker, Client Data Cleanser,
and Statistical Exploratory Profiler.
"""

import pytest
from src.domain.polymorphic_data_orchestrator import provision_dynamic_dataset
from src.domain.relational_schema_linker import (
    discover_foreign_key_relationships,
    generate_mermaid_er_diagram,
    synthesize_multi_table_join
)
from src.domain.client_data_cleaner import (
    standardize_date_string,
    cleanse_client_dataset
)
from src.domain.statistical_data_profiler import (
    calculate_numeric_stats,
    calculate_pearson_correlation,
    profile_client_dataset
)


import unittest


class TestRelationalDataStudio(unittest.TestCase):
    def test_date_standardization(self):
        assert standardize_date_string("08/14/2026") == "2026-08-14"
        assert standardize_date_string("2026-08-14") == "2026-08-14"
        assert standardize_date_string("14-Aug-2026") == "2026-08-14"
        assert standardize_date_string("2026.08.14") == "2026-08-14"


    def test_numeric_statistics_and_pearson_correlation(self):
        nums = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = calculate_numeric_stats(nums)
        assert stats["count"] == 5
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0

        # Perfect correlation
        r = calculate_pearson_correlation([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        assert r == 1.0

        # Negative correlation
        r_neg = calculate_pearson_correlation([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
        assert r_neg == -1.0


    def test_multi_table_relational_linking_and_joins(self):
        # 1. Ingest Dataset A: Customers
        customers_csv = """customer_id,name,state
    CUST-1,Acme Corp,CA
    CUST-2,Beta LLC,NY
    CUST-3,Gamma Inc,TX
    """
        provision_dynamic_dataset("studio_customers", customers_csv)

        # 2. Ingest Dataset B: Orders
        orders_csv = """order_id,customer_id,amount,status
    ORD-101,CUST-1,$1500.00,completed
    ORD-102,CUST-1,$2200.00,completed
    ORD-103,CUST-2,$850.00,pending
    """
        provision_dynamic_dataset("studio_orders", orders_csv)

        # Discover foreign keys
        fk_list = discover_foreign_key_relationships()
        assert len(fk_list) > 0
        assert any(rel["source_column"] == "customer_id" or rel["target_column"] == "customer_id" for rel in fk_list)

        # Generate Mermaid ER Diagram
        er = generate_mermaid_er_diagram()
        assert "erDiagram" in er
        assert "client_data_studio_customers" in er
        assert "client_data_studio_orders" in er

        # Synthesize Multi-Table JOIN
        join_res = synthesize_multi_table_join("Join customers and orders")
        assert join_res["status"] == "success"
        assert join_res["row_count"] > 0
        assert "JOIN" in join_res["generated_sql"]


    def test_data_cleansing_and_profiling(self):
        dirty_csv = """product_id,price,created_date,category
    P-101,$120.00,08/14/2026,Electronics
    P-101,$120.00,08/14/2026,Electronics
    P-102,,14-Aug-2026,Furniture
    """
        provision_dynamic_dataset("dirty_products", dirty_csv)

        # Run Cleansing
        clean_res = cleanse_client_dataset("dirty_products")
        assert clean_res["status"] == "success"
        assert clean_res["duplicates_removed"] == 1  # 1 duplicate removed
        assert clean_res["imputed_missing_values"] >= 1  # Missing price imputed

        # Run Profiling
        profile_res = profile_client_dataset("dirty_products")
        assert profile_res["status"] == "success"
        assert profile_res["row_count"] == 2
        assert "Executive Exploratory Data Analysis" in profile_res["executive_summary_markdown"]
