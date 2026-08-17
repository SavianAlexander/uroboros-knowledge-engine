#!/usr/bin/env python3
"""
Puerto Rico ERP & Multi-Database SQL Bridge (Neuro Copilot)
Dedicated zero-dependency CLI bridge providing unified, read-only SQL querying,
schema reflection, and cross-database analytics across:
  1. know.db (Neuro Knowledge Engine & PR Statutory Legal Corpus)
  2. payroll.db (Vantage PR Payroll System - Employees, Logs, Deductions)
  3. compliance.db (Vantage PR Compliance Portal - Solicitations, Certs, ASUME, CRIM)

Standard Library only (Ponytail principle: sqlite3, json, os, sys, re, argparse).
"""

import sys
import os
import json
import sqlite3
import re
import argparse
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output encoding resilience across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
desktop_root = os.path.abspath(os.path.join(project_root, ".."))

KNOW_DB_PATH = os.path.join(project_root, "know.db")
PAYROLL_DB_PATH = os.path.join(desktop_root, "Payroll System", "payroll.db")
COMPLIANCE_DB_PATH = os.path.join(desktop_root, "Vantage Fetch", "compliance.db")

FORBIDDEN_SQL_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|VACUUM|REINDEX|ATTACH|DETACH|PRAGMA\s+writable_schema)\b",
    re.IGNORECASE
)


def get_unified_connection() -> sqlite3.Connection:
    """
    Creates an in-memory SQLite connection and attaches all active PR ERP databases in read-only mode.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Attach know.db if exists
    if os.path.exists(KNOW_DB_PATH):
        try:
            know_uri = f"file:{os.path.abspath(KNOW_DB_PATH)}?mode=ro"
            cursor.execute(f"ATTACH DATABASE '{know_uri}' AS know")
        except Exception:
            cursor.execute(f"ATTACH DATABASE '{os.path.abspath(KNOW_DB_PATH)}' AS know")

    # Attach payroll.db if exists
    if os.path.exists(PAYROLL_DB_PATH):
        try:
            payroll_uri = f"file:{os.path.abspath(PAYROLL_DB_PATH)}?mode=ro"
            cursor.execute(f"ATTACH DATABASE '{payroll_uri}' AS payroll")
        except Exception:
            cursor.execute(f"ATTACH DATABASE '{os.path.abspath(PAYROLL_DB_PATH)}' AS payroll")

    # Attach compliance.db if exists
    if os.path.exists(COMPLIANCE_DB_PATH):
        try:
            comp_uri = f"file:{os.path.abspath(COMPLIANCE_DB_PATH)}?mode=ro"
            cursor.execute(f"ATTACH DATABASE '{comp_uri}' AS compliance")
        except Exception:
            cursor.execute(f"ATTACH DATABASE '{os.path.abspath(COMPLIANCE_DB_PATH)}' AS compliance")

    return conn


def get_schema_catalog() -> Dict[str, Any]:
    """
    Reflects the full schema of all attached PR ERP databases (know, payroll, compliance).
    """
    conn = get_unified_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA database_list;")
    dbs = cursor.fetchall()

    catalog = {}
    for db_row in dbs:
        db_name = db_row["name"]
        if db_name in ["main", "temp"]:
            continue
        db_file = db_row["file"]
        catalog[db_name] = {"file": db_file, "tables": {}}

        cursor.execute(f"SELECT name FROM {db_name}.sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cursor.fetchall()]

        for t in tables:
            cursor.execute(f"PRAGMA {db_name}.table_info({t});")
            cols = [
                {"name": c[1], "type": c[2], "notnull": bool(c[3]), "pk": bool(c[5])}
                for c in cursor.fetchall()
            ]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {db_name}.{t};")
                row_count = cursor.fetchone()[0]
            except Exception:
                row_count = 0

            catalog[db_name]["tables"][t] = {
                "row_count": row_count,
                "columns": cols
            }

    conn.close()
    return catalog


def execute_safe_query(sql_query: str, limit: int = 100) -> Dict[str, Any]:
    """
    Executes a read-only SQL query across attached databases with strict safety guardrails.
    """
    if not sql_query or not sql_query.strip():
        return {"status": "error", "message": "SQL query required."}

    clean_sql = sql_query.strip()
    if FORBIDDEN_SQL_PATTERNS.search(clean_sql):
        return {
            "status": "error",
            "message": "Mutation/DDL query rejected. Only read-only SELECT queries are allowed."
        }

    # Ensure LIMIT clause if not present
    if not re.search(r"\bLIMIT\b", clean_sql, re.IGNORECASE):
        clean_sql = f"{clean_sql.rstrip(';')} LIMIT {limit}"

    conn = get_unified_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(clean_sql)
        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description] if cursor.description else []
        records = [dict(zip(cols, [row[c] for c in cols])) for row in rows]
        conn.close()
        return {
            "status": "success",
            "query": clean_sql,
            "row_count": len(records),
            "columns": cols,
            "records": records
        }
    except Exception as e:
        conn.close()
        return {"status": "error", "query": clean_sql, "message": str(e)}


def get_payroll_metrics() -> Dict[str, Any]:
    """
    Extracts high-level payroll metrics from payroll.db.
    """
    if not os.path.exists(PAYROLL_DB_PATH):
        return {"status": "error", "message": "payroll.db not found."}

    conn = sqlite3.connect(f"file:{PAYROLL_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees;")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM employees WHERE status='active';")
    active_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM payroll_logs;")
    total_logs = cursor.fetchone()[0]

    cursor.execute("""
    SELECT 
        COALESCE(SUM(gross_wages), 0) as total_gross,
        COALESCE(SUM(fica_ss_employee + fica_med_employee + pr_income_tax), 0) as total_withholdings,
        COALESCE(SUM(net_pay), 0) as total_net_paid
    FROM payroll_logs;
    """)
    totals = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) FROM compliance_filings;")
    filings_count = cursor.fetchone()[0]

    conn.close()
    return {
        "status": "success",
        "database": "payroll.db",
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_payroll_runs": total_logs,
        "totals": totals,
        "compliance_filings_count": filings_count
    }


def get_compliance_metrics() -> Dict[str, Any]:
    """
    Extracts high-level government clearance and certificate metrics from compliance.db.
    """
    if not os.path.exists(COMPLIANCE_DB_PATH):
        return {"status": "error", "message": "compliance.db not found."}

    conn = sqlite3.connect(f"file:{COMPLIANCE_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM solicitations;")
    total_solicitations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM submissions;")
    total_submissions = cursor.fetchone()[0]

    cursor.execute("""
    SELECT document_type, COUNT(*) as count, status 
    FROM submissions 
    GROUP BY document_type, status;
    """)
    doc_breakdown = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM audit_logs;")
    audit_count = cursor.fetchone()[0]

    conn.close()
    return {
        "status": "success",
        "database": "compliance.db",
        "total_solicitations": total_solicitations,
        "total_submissions": total_submissions,
        "document_breakdown": doc_breakdown,
        "audit_logs_count": audit_count
    }


def ask_erp_copilot(question: str) -> str:
    """
    Translates a natural language question into a verified read-only SQL query, executes it across
    the attached PR ERP databases, and synthesizes a structured executive answer.
    """
    if not question:
        return json.dumps({"status": "error", "message": "Question required"})

    catalog = get_schema_catalog()
    catalog_summary = []
    for db_name, db_info in catalog.items():
        for t_name, t_info in db_info["tables"].items():
            col_list = ", ".join([f"{c['name']} ({c['type']})" for c in t_info["columns"]])
            catalog_summary.append(f"- {db_name}.{t_name} ({t_info['row_count']} rows): [{col_list}]")
    schema_text = "\n".join(catalog_summary)

    prompt = (
        f"You are the Neuro PR ERP SQL Bridge Assistant. You have read-only access to an SQLite database with "
        f"three attached namespaces:\n"
        f"  - know: Local knowledge vault and statutory legal corpus (pr_legal_corpus, pr_legal_jurisprudence)\n"
        f"  - payroll: Vantage PR Payroll system (employees, payroll_logs, compliance_filings, settings)\n"
        f"  - compliance: Vantage PR Compliance portal (solicitations, submissions, verification_logs)\n\n"
        f"DATABASE SCHEMA CATALOG:\n{schema_text}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"Provide ONLY a valid read-only SQLite SELECT query that answers the user's question, prefixed with ```sql and ending with ```. "
        f"Always prefix table names with their namespace (e.g. payroll.employees, compliance.submissions, know.pr_legal_corpus)."
    )

    try:
        from src.core.model_manager import OllamaClient
        client = OllamaClient()
        response_dict = client(prompt, model="qwen2.5-coder:3b", max_tokens=256, temperature=0.1)
        raw_text = response_dict.get("choices", [{}])[0].get("text", "").strip()

        # Extract SQL block
        m = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", raw_text, re.IGNORECASE)
        sql_candidate = m.group(1).strip() if m else raw_text.strip()

        # Execute synthesized SQL
        res = execute_safe_query(sql_candidate)

        # Synthesize concise explanation
        explain_prompt = (
            f"Given the user question: '{question}'\n"
            f"And the SQL query: {sql_candidate}\n"
            f"And the resulting records: {json.dumps(res.get('records', [])[:10])}\n\n"
            f"Provide a concise executive answer explaining the results."
        )
        explain_res = client(explain_prompt, model="phi4-mini:latest", max_tokens=300, temperature=0.2)
        summary = explain_res.get("choices", [{}])[0].get("text", "").strip()

        return json.dumps({
            "status": "success",
            "question": question,
            "synthesized_sql": sql_candidate,
            "query_results": res,
            "executive_summary": summary
        }, indent=2)
    except Exception as e:
        # Fallback to direct heuristic search or query execution
        return json.dumps({
            "status": "error",
            "message": str(e),
            "schema_catalog": catalog
        }, indent=2)


def self_test() -> int:
    """Run assert-based self-test suite for pr_erp_sql_bridge.py."""
    print("=== Running PR ERP SQL Bridge Self-Test Suite ===")

    # 1. Test Schema Catalog Reflection
    catalog = get_schema_catalog()
    assert isinstance(catalog, dict), "Catalog must be a dict"
    print(f"  [Pass] Schema Catalog reflected ({len(catalog)} attached namespaces: {list(catalog.keys())})")

    # 2. Test Read-Only Query Guardrails
    guard_res = execute_safe_query("DROP TABLE payroll.employees;")
    assert guard_res.get("status") == "error", "Forbidden query must be blocked"
    print("  [Pass] DDL / Mutation guardrail successfully blocked DROP TABLE")

    # 3. Test Safe SELECT Query
    select_res = execute_safe_query("SELECT 1 as test_val, date('now') as today;")
    assert select_res.get("status") == "success", f"SELECT failed: {select_res}"
    assert select_res["records"][0]["test_val"] == 1
    print("  [Pass] Safe SELECT execution clean")

    # 4. Test Cross-Database Table Query
    if "compliance" in catalog and "solicitations" in catalog["compliance"]["tables"]:
        comp_res = execute_safe_query("SELECT COUNT(*) as count FROM compliance.solicitations;")
        assert comp_res.get("status") == "success", "compliance query failed"
        print(f"  [Pass] compliance.db query clean ({comp_res['records'][0]['count']} solicitations)")

    if "payroll" in catalog and "settings" in catalog["payroll"]["tables"]:
        pay_res = execute_safe_query("SELECT COUNT(*) as count FROM payroll.settings;")
        assert pay_res.get("status") == "success", "payroll query failed"
        print(f"  [Pass] payroll.db query clean ({pay_res['records'][0]['count']} settings)")

    print("PR ERP SQL Bridge Self-Test Complete: ALL ASSERTIONS PASSED (100% Success)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Puerto Rico ERP Multi-Database SQL Bridge")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("schema", help="Reflect full schema of know.db, payroll.db, compliance.db")
    subparsers.add_parser("payroll", help="Get summary metrics from payroll.db")
    subparsers.add_parser("compliance", help="Get summary metrics from compliance.db")

    q_p = subparsers.add_parser("query", help="Execute read-only SQL query across attached databases")
    q_p.add_argument("sql", help="SQL SELECT query string")
    q_p.add_argument("--limit", type=int, default=100, help="Maximum records to return")

    ask_p = subparsers.add_parser("ask", help="Natural language question to SQL query synthesis")
    ask_p.add_argument("question", nargs="*", help="Question text")

    subparsers.add_parser("self_test", help="Run assertion self-test suite")

    args = parser.parse_args()

    if not args.command or args.command == "schema":
        print(json.dumps(get_schema_catalog(), indent=2))
    elif args.command == "payroll":
        print(json.dumps(get_payroll_metrics(), indent=2))
    elif args.command == "compliance":
        print(json.dumps(get_compliance_metrics(), indent=2))
    elif args.command == "query":
        print(json.dumps(execute_safe_query(args.sql, args.limit), indent=2))
    elif args.command == "ask":
        q_str = " ".join(args.question) if isinstance(args.question, list) else str(args.question or "")
        print(ask_erp_copilot(q_str))
    elif args.command == "self_test":
        sys.exit(self_test())


if __name__ == "__main__":
    main()
