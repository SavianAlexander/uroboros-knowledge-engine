"""
Unit test suite for Autonomous Database Orchestration, Polymorphic Ingestion,
Text-to-SQL Routing, and Self-Healing Database Index Management.
"""

import pytest
import json
from src.domain.polymorphic_data_orchestrator import (
    infer_value_type,
    infer_column_types,
    parse_polymorphic_content,
    provision_dynamic_dataset,
    list_orchestrated_datasets
)
from src.domain.autonomous_sql_router import (
    classify_analytical_intent,
    generate_safe_sql_query,
    execute_autonomous_sql_query
)
from src.domain.knowledge_self_healing import (
    inspect_database_health,
    auto_optimize_indexes,
    detect_client_data_anomalies,
    execute_database_self_healing
)


import unittest


class TestDatabaseOrchestration(unittest.TestCase):
    def test_type_inference(self):
        assert infer_value_type(100) == "INTEGER"
        assert infer_value_type(99.95) == "REAL"
        assert infer_value_type("$1,450.00") == "REAL"
        assert infer_value_type("2026-08-14") == "TEXT"
        assert infer_value_type("client@example.com") == "TEXT"
        assert infer_value_type(True) == "BOOLEAN"
        assert infer_value_type('{"key": "value"}') == "JSON"


    def test_polymorphic_parsing_and_provisioning(self):
        csv_sample = """client_name,account_id,revenue,signup_date
    Acme Corp,ACC-101,$12500.50,2026-01-15
    Beta LLC,ACC-102,$4800.00,2026-02-20
    Gamma Inc,ACC-103,$9200.75,2026-03-10
    """
        rows, fmt = parse_polymorphic_content(csv_sample)
        assert fmt == "csv"
        assert len(rows) == 3

        res = provision_dynamic_dataset("enterprise_clients", csv_sample)
        assert res["status"] == "success"
        assert res["table_name"] == "client_data_enterprise_clients"
        assert res["rows_ingested"] == 3
        assert "revenue" in res["columns"]

        datasets = list_orchestrated_datasets()
        assert any(d["dataset_name"] == "enterprise_clients" for d in datasets)


    def test_autonomous_text_to_sql_routing(self):
        # Ingest test dataset
        data = """employee,department,salary,active
    Alice,Engineering,150000,true
    Bob,Sales,120000,true
    Charlie,Engineering,165000,false
    """
        provision_dynamic_dataset("salaries", data)

        # 1. Test Aggregation: Count
        res_count = execute_autonomous_sql_query("What is the total count of records in salaries?")
        assert res_count["status"] == "success"
        assert "COUNT" in res_count["generated_sql"]

        # 2. Test Aggregation: Sum / Total
        res_sum = execute_autonomous_sql_query("What is the total salary in salaries?")
        assert res_sum["status"] == "success"
        assert "SUM" in res_sum["generated_sql"]


    def test_database_self_healing_and_anomaly_detection(self):
        # 1. Health inspection
        health = inspect_database_health()
        assert health["status"] == "healthy"
        assert health["total_tables"] > 0

        # 2. Auto-optimize indexes
        opt = auto_optimize_indexes()
        assert opt["status"] == "success"

        # 3. Anomaly detection (Null rates & PII)
        sample_with_pii = """customer,notes,ssn_code
    John Doe,Regular client,000-12-3456
    Jane Smith,VIP client,111-22-3333
    """
        provision_dynamic_dataset("pii_test_client", sample_with_pii)
        anomalies = detect_client_data_anomalies("pii_test_client")
        assert len(anomalies) > 0
        assert any("PII" in a["anomaly_type"] for a in anomalies)

        # 4. Full self-healing cycle
        cycle = execute_database_self_healing()
        assert cycle["status"] == "success"
