"""
Automated Client Data Cleanser, Normalizer & Deduplication Engine.
Zero-dependency, standard-library implementation for group-conditioned imputation,
E.164 phone standardization, state/postal harmonization, boolean normalization,
and fuzzy string deduplication (Levenshtein distance).
"""

import re
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from src.infrastructure.database import get_db
from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets


DATE_FORMATS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
    "%d-%b-%Y", "%d-%B-%Y", "%b %d, %Y", "%B %d, %Y",
    "%Y.%m.%d"
]

US_STATE_MAP = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY"
}


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


def standardize_phone_number(val_str: str) -> str:
    """Standardizes phone numbers into E.164 format (+1XXXXXXXXXX)."""
    digits = re.sub(r'\D', '', val_str)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    return val_str.strip()


def standardize_state_or_zip(col_name: str, val_str: str) -> str:
    """Standardizes US states and 5-digit zip codes."""
    s = val_str.strip()
    c_lower = col_name.lower()
    if any(k in c_lower for k in ["state", "province"]):
        return US_STATE_MAP.get(s.lower(), s.upper())
    elif any(k in c_lower for k in ["zip", "postal"]) and s.isdigit() and len(s) < 5:
        return s.zfill(5)
    return s


def standardize_boolean_value(val: Any) -> Any:
    """Harmonizes boolean-like values into standard boolean."""
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s in ("true", "1", "yes", "y", "t", "active"):
        return 1
    elif s in ("false", "0", "no", "n", "f", "inactive"):
        return 0
    return val


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Computes normalized Levenshtein similarity [0.0 to 1.0]."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    dist = dp[m][n]
    max_len = max(m, n)
    return 1.0 - (dist / max_len)


def cleanse_client_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Executes deep automated cleansing: group-conditioned imputation,
    E.164 phone normalization, postal/state standardization, boolean harmonization,
    and exact + fuzzy deduplication.
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

        # 1. Exact & Fuzzy Deduplication
        deduped_rows: List[Dict[str, Any]] = []
        duplicates_removed = 0
        seen_exact = set()

        for r in rows:
            sig = tuple(str(r[c]) for c in cols_schema.keys() if c != "id")
            if sig in seen_exact:
                duplicates_removed += 1
                continue

            # Fuzzy check against existing deduped rows
            is_fuzzy_dup = False
            for existing in deduped_rows:
                sims = []
                name_mismatch = False
                for c, c_type in cols_schema.items():
                    if c != "id" and c_type == "TEXT":
                        v1 = str(r.get(c, "")).strip().lower()
                        v2 = str(existing.get(c, "")).strip().lower()
                        if any(k in c.lower() for k in ["name", "emp", "user", "client", "customer", "email", "person"]):
                            if v1 and v2 and levenshtein_similarity(v1, v2) < 0.80:
                                name_mismatch = True
                                break
                        if len(v1) > 2 and len(v2) > 2 and not any(k in c.lower() for k in ["dept", "category", "status", "role", "group"]):
                            sims.append(levenshtein_similarity(v1, v2))
                if not name_mismatch and sims and sum(sims) / len(sims) >= 0.90:
                    is_fuzzy_dup = True
                    break

            if is_fuzzy_dup:
                duplicates_removed += 1
            else:
                seen_exact.add(sig)
                deduped_rows.append(r)

        # 2. Identify Categorical Grouping Column for Conditioned Imputation
        group_col = next((c for c, t in cols_schema.items() if c != "id" and t == "TEXT" and any(k in c.lower() for k in ["dept", "category", "status", "role", "group"])), None)

        group_means: Dict[Tuple[str, Any], float] = {}
        global_stats: Dict[str, Any] = {}

        for col, col_type in cols_schema.items():
            if col == "id":
                continue
            if col_type in ("INTEGER", "REAL"):
                nums = [r[col] for r in deduped_rows if r.get(col) is not None and isinstance(r.get(col), (int, float))]
                global_stats[col] = sum(nums) / len(nums) if nums else 0.0

                if group_col:
                    for r in deduped_rows:
                        g_val = r.get(group_col)
                        val = r.get(col)
                        if g_val is not None and isinstance(val, (int, float)):
                            key = (col, g_val)
                            group_means.setdefault(key, []).append(val)
            else:
                vals = [str(r[col]) for r in deduped_rows if r.get(col) is not None and str(r.get(col)).strip() != ""]
                global_stats[col] = max(set(vals), key=vals.count) if vals else "N/A"

        # Compute average per group
        final_group_means = {k: sum(v) / len(v) for k, v in group_means.items() if v}

        # 3. Apply Transformations & Imputation
        imputed_count = 0
        normalized_dates_count = 0
        normalized_phones_count = 0

        for r in deduped_rows:
            for col, col_type in cols_schema.items():
                if col == "id":
                    continue
                val = r.get(col)

                # Missing value imputation
                if val is None or str(val).strip() == "" or str(val).lower() in ("nan", "null", "none", "nil"):
                    if col_type in ("INTEGER", "REAL") and group_col:
                        g_val = r.get(group_col)
                        imputed_val = final_group_means.get((col, g_val), global_stats.get(col, 0.0))
                    else:
                        imputed_val = global_stats.get(col, None)
                    r[col] = imputed_val
                    imputed_count += 1
                elif col_type == "TEXT":
                    val_str = str(val).strip()
                    # Phone normalization
                    if any(p_kw in col.lower() for p_kw in ["phone", "tel", "mobile", "cell"]):
                        std_phone = standardize_phone_number(val_str)
                        if std_phone != val:
                            r[col] = std_phone
                            normalized_phones_count += 1
                    # Date normalization
                    elif any(d_kw in col.lower() for d_kw in ["date", "time", "created", "updated"]):
                        std_date = standardize_date_string(val_str)
                        if std_date != val:
                            r[col] = std_date
                            normalized_dates_count += 1
                    # State / Zip normalization
                    elif any(s_kw in col.lower() for s_kw in ["state", "zip", "postal"]):
                        r[col] = standardize_state_or_zip(col, val_str)
                elif col_type == "BOOLEAN":
                    r[col] = standardize_boolean_value(val)

        # 4. Write back cleaned records
        cursor.execute(f"DELETE FROM {table_name}")

        cols_to_insert = [c for c in cols_schema.keys() if c != "id"]
        placeholders = ", ".join(["?"] * len(cols_to_insert))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(cols_to_insert)}) VALUES ({placeholders})"

        cleaned_payloads = [[r.get(c) for c in cols_to_insert] for r in deduped_rows]
        cursor.executemany(insert_sql, cleaned_payloads)

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
        "normalized_dates": normalized_dates_count,
        "normalized_phones": normalized_phones_count,
        "conditioned_imputation_group": group_col
    }
