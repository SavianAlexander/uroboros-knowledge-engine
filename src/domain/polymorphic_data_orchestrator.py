"""
Polymorphic Client Data Orchestrator & Autonomous Schema Discovery Engine.
Zero-dependency, standard-library implementation for ingesting arbitrary multi-format client data,
discovering dynamic schemas, auto-provisioning SQLite tables, and extracting relational linkages.
"""

import re
import csv
import io
import json
import sqlite3
import unicodedata
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from src.infrastructure.database import get_db

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
CURRENCY_REGEX = re.compile(r'^[\$\€\£\¥]?\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*[\$\€\£\¥]?$')
ISO_DATE_REGEX = re.compile(r'^\d{4}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])(?:[T\s]\d{2}:\d{2}(?::\d{2})?)?$')


def sanitize_identifier(name: str) -> str:
    """Sanitizes table and column names for safe SQL DDL execution."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', str(name).strip())
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean or clean[0].isdigit():
        clean = f"col_{clean}"
    return clean.lower()[:48]


def infer_value_type(val: Any) -> str:
    """Infers the data type of a single value."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "BOOLEAN"
    if isinstance(val, int):
        return "INTEGER"
    if isinstance(val, float):
        return "REAL"
    if isinstance(val, (dict, list)):
        return "JSON"

    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "none", "nan", "nil", ""):
        return "NULL"

    if val_str.lower() in ("true", "false", "yes", "no"):
        return "BOOLEAN"

    if re.match(r'^-?\d+$', val_str):
        return "INTEGER"

    if re.match(r'^-?\d*\.\d+$', val_str):
        return "REAL"

    if CURRENCY_REGEX.match(val_str) and any(c in val_str for c in "$€£¥,"):
        return "REAL"

    if ISO_DATE_REGEX.match(val_str):
        return "TEXT"  # SQLite stores dates as ISO TEXT

    if EMAIL_REGEX.match(val_str):
        return "TEXT"

    if (val_str.startswith("{") and val_str.endswith("}")) or (val_str.startswith("[") and val_str.endswith("]")):
        try:
            json.loads(val_str)
            return "JSON"
        except Exception:
            pass

    return "TEXT"


def infer_column_types(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """Infers predominant SQL types for all columns across sample rows."""
    if not rows:
        return {}

    type_counts: Dict[str, Dict[str, int]] = {}

    for row in rows[:500]:
        for col, val in row.items():
            s_col = sanitize_identifier(col)
            if s_col not in type_counts:
                type_counts[s_col] = {"INTEGER": 0, "REAL": 0, "BOOLEAN": 0, "JSON": 0, "TEXT": 0}
            
            v_type = infer_value_type(val)
            if v_type in type_counts[s_col]:
                type_counts[s_col][v_type] += 1

    inferred_types = {}
    for col, counts in type_counts.items():
        total = sum(counts.values())
        if total == 0:
            inferred_types[col] = "TEXT"
            continue

        if counts["JSON"] > total * 0.3:
            inferred_types[col] = "TEXT"  # Store JSON as TEXT in SQLite
        elif counts["TEXT"] > total * 0.2:
            inferred_types[col] = "TEXT"
        elif counts["REAL"] > 0 or (counts["REAL"] + counts["INTEGER"] == total and counts["REAL"] > 0):
            inferred_types[col] = "REAL"
        elif counts["INTEGER"] > total * 0.7:
            inferred_types[col] = "INTEGER"
        elif counts["BOOLEAN"] > total * 0.7:
            inferred_types[col] = "INTEGER"
        else:
            inferred_types[col] = "TEXT"

    return inferred_types


def clean_cell_value(val: Any, target_type: str) -> Any:
    """Cleans and coerces a cell value according to target SQL type."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "none", "nan", "nil", ""):
        return None

    if target_type == "INTEGER":
        try:
            # Handle float strings like '12.0' or currency
            cleaned = re.sub(r'[\$,€£¥]', '', val_str)
            return int(float(cleaned))
        except Exception:
            return None

    if target_type == "REAL":
        try:
            cleaned = re.sub(r'[\$,€£¥]', '', val_str)
            return float(cleaned)
        except Exception:
            return None

    if target_type == "JSON" or isinstance(val, (dict, list)):
        if isinstance(val, (dict, list)):
            return json.dumps(val)
        return val_str

    return val_str


def parse_polymorphic_content(content: str, format_hint: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
    """Parses arbitrary string content into tabular records and identifies source format."""
    trimmed = content.strip()
    if not trimmed:
        return [], "empty"

    # 1. Try JSON Array
    if trimmed.startswith("[") and trimmed.endswith("]"):
        try:
            data = json.loads(trimmed)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return data, "json_array"
        except Exception:
            pass

    # 2. Try JSONL (JSON Lines)
    if "\n" in trimmed:
        lines = trimmed.splitlines()
        jsonl_rows = []
        is_jsonl = True
        for line in lines[:20]:
            s_line = line.strip()
            if not s_line:
                continue
            if s_line.startswith("{") and s_line.endswith("}"):
                try:
                    obj = json.loads(s_line)
                    if isinstance(obj, dict):
                        jsonl_rows.append(obj)
                    else:
                        is_jsonl = False
                        break
                except Exception:
                    is_jsonl = False
                    break
            else:
                is_jsonl = False
                break

        if is_jsonl and len(jsonl_rows) > 0:
            full_rows = []
            for line in lines:
                s_line = line.strip()
                if s_line:
                    try:
                        full_rows.append(json.loads(s_line))
                    except Exception:
                        pass
            return full_rows, "jsonl"

    # 3. Try CSV / TSV
    delimiter = '\t' if (format_hint == 'tsv' or '\t' in trimmed.splitlines()[0]) else ','
    try:
        reader = csv.DictReader(io.StringIO(trimmed), delimiter=delimiter)
        rows = [row for row in reader if any(row.values())]
        if rows and len(rows[0]) > 1:
            return rows, "csv" if delimiter == ',' else "tsv"
    except Exception:
        pass

    # 4. Fallback: Key-Value Log Parser
    kv_rows = []
    current_record = {}
    for line in trimmed.splitlines():
        clean_l = line.strip()
        if not clean_l:
            if current_record:
                kv_rows.append(current_record)
                current_record = {}
            continue
        if ":" in clean_l or "=" in clean_l:
            sep = ":" if ":" in clean_l else "="
            k, v = clean_l.split(sep, 1)
            current_record[k.strip()] = v.strip()
    if current_record:
        kv_rows.append(current_record)

    if kv_rows:
        return kv_rows, "key_value_logs"

    return [], "unknown"


def provision_dynamic_dataset(
    dataset_name: str,
    raw_content: str,
    format_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Autonomously provisions a dynamic SQLite table for arbitrary client data,
    discovers column types, inserts rows atomically, and registers metadata.
    """
    rows, detected_format = parse_polymorphic_content(raw_content, format_hint)
    if not rows:
        return {
            "status": "error",
            "message": "No structured tabular records could be extracted from payload",
            "table_name": None,
            "rows_ingested": 0
        }

    inferred_types = infer_column_types(rows)
    safe_table = f"client_data_{sanitize_identifier(dataset_name)}"

    # Ensure catalog table exists
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _client_datasets_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT UNIQUE,
                table_name TEXT UNIQUE,
                source_format TEXT,
                row_count INTEGER,
                columns_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Construct DDL
        col_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        sanitized_col_map = {}
        for original_col in rows[0].keys():
            s_col = sanitize_identifier(original_col)
            sanitized_col_map[original_col] = s_col
            col_type = inferred_types.get(s_col, "TEXT")
            col_defs.append(f"{s_col} {col_type}")

        ddl = f"CREATE TABLE IF NOT EXISTS {safe_table} (\n  " + ",\n  ".join(col_defs) + "\n)"
        cursor.execute(ddl)

        # Clear existing rows if re-ingesting
        cursor.execute(f"DELETE FROM {safe_table}")

        # Insert rows
        cols_to_insert = [sanitized_col_map[k] for k in rows[0].keys()]
        placeholders = ", ".join(["?"] * len(cols_to_insert))
        insert_sql = f"INSERT INTO {safe_table} ({', '.join(cols_to_insert)}) VALUES ({placeholders})"

        cleaned_records = []
        for r in rows:
            record_vals = []
            for k in rows[0].keys():
                s_col = sanitized_col_map[k]
                t_type = inferred_types.get(s_col, "TEXT")
                record_vals.append(clean_cell_value(r.get(k), t_type))
            cleaned_records.append(record_vals)

        cursor.executemany(insert_sql, cleaned_records)

        # Auto-create indexes on potential ID/foreign key columns
        for s_col in cols_to_insert:
            if any(id_kw in s_col for id_kw in ["id", "code", "key", "account", "client", "customer", "email", "date"]):
                idx_name = f"idx_{safe_table}_{s_col}"
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {safe_table} ({s_col})")

        # Register in catalog
        cursor.execute("""
            INSERT INTO _client_datasets_catalog (dataset_name, table_name, source_format, row_count, columns_json, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(dataset_name) DO UPDATE SET
                table_name=excluded.table_name,
                source_format=excluded.source_format,
                row_count=excluded.row_count,
                columns_json=excluded.columns_json,
                updated_at=CURRENT_TIMESTAMP
        """, (dataset_name, safe_table, detected_format, len(cleaned_records), json.dumps(inferred_types)))

        conn.commit()

    return {
        "status": "success",
        "dataset_name": dataset_name,
        "table_name": safe_table,
        "source_format": detected_format,
        "rows_ingested": len(cleaned_records),
        "columns": inferred_types,
        "sample_columns": list(inferred_types.keys())[:10]
    }


def list_orchestrated_datasets() -> List[Dict[str, Any]]:
    """Returns all dynamically orchestrated client datasets and their schemas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _client_datasets_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT UNIQUE,
                table_name TEXT UNIQUE,
                source_format TEXT,
                row_count INTEGER,
                columns_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("SELECT dataset_name, table_name, source_format, row_count, columns_json, created_at, updated_at FROM _client_datasets_catalog ORDER BY updated_at DESC")
        rows = cursor.fetchall()

    result = []
    for r in rows:
        try:
            cols = json.loads(r[4])
        except Exception:
            cols = {}
        result.append({
            "dataset_name": r[0],
            "table_name": r[1],
            "source_format": r[2],
            "row_count": r[3],
            "columns": cols,
            "created_at": r[5],
            "updated_at": r[6]
        })
    return result
