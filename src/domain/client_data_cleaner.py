"""
Automated Client Data Cleanser, Normalizer & Deduplication Engine.
Zero-dependency, standard-library implementation for imputing missing values,
standardizing dates/currencies, and deduplicating rows across client datasets.
"""

import re
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from src.infrastructure.database import get_db
from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets


DATE_FORMATS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
    "%d-%b-%Y", "%d-%B-%Y", "%b %d, %Y", "%B %d, %Y",
    "%Y.%m.%d"
]


def standardize_date_string(val_str: str) -> Optional[str]:
    """Converts diverse date formats into standardized ISO-8601 (YYYY-MM-DD)."""
    if not val_str:
        return None
    s = val_str.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return s


def cleanse_client_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Executes automated data cleansing, missing value imputation, date standardization,
    and deduplication on a provisioned client dataset table.
    """
    datasets = list_orchestrated_datasets()
    target_ds = next((d for d in datasets if d["dataset_name"] == dataset_name), None)

    if not target_ds:
        return {
            "status": "not_found",
            "message": f"Dataset `{dataset_name}` not found in catalog"
        }

    table_name = target_ds["table_name"]
    cols_schema = target_ds.get("columns", {})

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(r) for r in cursor.fetchall()]

        if not rows:
            return {"status": "empty", "message": "Dataset table contains no rows"}

        total_original_rows = len(rows)

        # 1. Deduplication (Exact Row Hashes)
        seen_signatures = set()
        deduped_rows = []
        duplicates_removed = 0

        for r in rows:
            # Exclude auto-increment primary key ID from signature
            sig = tuple(str(r[c]) for c in cols_schema.keys() if c != "id")
            if sig in seen_signatures:
                duplicates_removed += 1
            else:
                seen_signatures.add(sig)
                deduped_rows.append(r)

        # 2. Imputation & Normalization
        imputed_count = 0
        normalized_dates_count = 0

        # Compute column means/modes
        col_stats = {}
        for col, col_type in cols_schema.items():
            if col == "id":
                continue
            if col_type in ("INTEGER", "REAL"):
                nums = [r[col] for r in deduped_rows if r.get(col) is not None and isinstance(r.get(col), (int, float))]
                col_stats[col] = sum(nums) / len(nums) if nums else 0.0
            else:
                vals = [str(r[col]) for r in deduped_rows if r.get(col) is not None and str(r.get(col)).strip() != ""]
                col_stats[col] = max(set(vals), key=vals.count) if vals else "N/A"

        # Apply transformations
        for r in deduped_rows:
            for col, col_type in cols_schema.items():
                if col == "id":
                    continue
                val = r.get(col)

                # Missing value imputation
                if val is None or str(val).strip() == "" or str(val).lower() in ("nan", "null", "none", "nil"):
                    r[col] = col_stats.get(col, None)
                    imputed_count += 1
                elif col_type == "TEXT" and any(d_kw in col for d_kw in ["date", "time", "created", "updated"]):
                    # Standardize dates
                    std_date = standardize_date_string(str(val))
                    if std_date != val:
                        r[col] = std_date
                        normalized_dates_count += 1

        # 3. Write back cleaned records
        cursor.execute(f"DELETE FROM {table_name}")

        cols_to_insert = [c for c in cols_schema.keys() if c != "id"]
        placeholders = ", ".join(["?"] * len(cols_to_insert))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(cols_to_insert)}) VALUES ({placeholders})"

        cleaned_payloads = [[r.get(c) for c in cols_to_insert] for r in deduped_rows]
        cursor.executemany(insert_sql, cleaned_payloads)

        # Update catalog count
        cursor.execute("UPDATE _client_datasets_catalog SET row_count = ?, updated_at = CURRENT_TIMESTAMP WHERE dataset_name = ?", (len(deduped_rows), dataset_name))
        conn.commit()

    return {
        "status": "success",
        "dataset_name": dataset_name,
        "table_name": table_name,
        "original_rows": total_original_rows,
        "cleaned_rows": len(deduped_rows),
        "duplicates_removed": duplicates_removed,
        "imputed_missing_values": imputed_count,
        "normalized_dates": normalized_dates_count
    }
