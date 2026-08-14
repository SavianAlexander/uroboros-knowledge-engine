"""
Statistical Data Profiler, Correlation Engine & Automated EDA Generator.
Zero-dependency, standard-library implementation for calculating descriptive statistics,
Pearson correlation matrices, outlier distributions, and natural language executive summaries.
"""

import math
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from src.infrastructure.database import get_db
from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets


def calculate_numeric_stats(values: List[float]) -> Dict[str, Any]:
    """Calculates comprehensive descriptive statistics for a list of numbers."""
    if not values:
        return {"count": 0, "min": 0, "max": 0, "mean": 0, "median": 0, "stddev": 0, "iqr": 0}

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    mean = total / n

    median = sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[(n // 2) - 1] + sorted_vals[n // 2]) / 2.0
    p25 = sorted_vals[int(n * 0.25)]
    p75 = sorted_vals[int(n * 0.75)]
    iqr = p75 - p25

    variance = sum((x - mean) ** 2 for x in sorted_vals) / max(1, n - 1)
    stddev = math.sqrt(variance)

    # Outlier count (1.5 * IQR)
    lower_bound = p25 - 1.5 * iqr
    upper_bound = p75 + 1.5 * iqr
    outliers = [x for x in sorted_vals if x < lower_bound or x > upper_bound]

    return {
        "count": n,
        "min": round(sorted_vals[0], 2),
        "max": round(sorted_vals[-1], 2),
        "mean": round(mean, 2),
        "median": round(median, 2),
        "stddev": round(stddev, 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "iqr": round(iqr, 2),
        "outlier_count": len(outliers)
    }


def calculate_pearson_correlation(x: List[float], y: List[float]) -> float:
    """Calculates Pearson correlation coefficient between two numeric vectors."""
    n = min(len(x), len(y))
    if n < 2:
        return 0.0

    mean_x = sum(x[:n]) / n
    mean_y = sum(y[:n]) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    denom_y = sum((y[i] - mean_y) ** 2 for i in range(n))

    denominator = math.sqrt(denom_x * denom_y)
    if denominator == 0:
        return 0.0

    return round(max(-1.0, min(1.0, numerator / denominator)), 3)


def profile_client_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Computes an automated statistical profile, correlation matrix,
    and executive markdown summary for a provisioned client dataset.
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

    column_profiles = {}
    numeric_vectors: Dict[str, List[float]] = {}

    for col, col_type in cols_schema.items():
        if col == "id":
            continue

        raw_vals = [r.get(col) for r in rows if r.get(col) is not None]

        if col_type in ("INTEGER", "REAL"):
            num_vals = [float(v) for v in raw_vals if isinstance(v, (int, float))]
            column_profiles[col] = {
                "type": "NUMERIC",
                "stats": calculate_numeric_stats(num_vals)
            }
            numeric_vectors[col] = num_vals
        else:
            str_vals = [str(v).strip() for v in raw_vals if str(v).strip()]
            val_counts = {}
            for v in str_vals:
                val_counts[v] = val_counts.get(v, 0) + 1
            top_values = sorted(val_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            column_profiles[col] = {
                "type": "CATEGORICAL",
                "cardinality": len(val_counts),
                "top_frequent": [{"value": v, "count": c, "pct": round((c / max(1, len(str_vals))) * 100, 1)} for v, c in top_values]
            }

    # Compute correlation matrix
    correlation_matrix = {}
    num_cols = list(numeric_vectors.keys())
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            c1 = num_cols[i]
            c2 = num_cols[j]
            r_val = calculate_pearson_correlation(numeric_vectors[c1], numeric_vectors[c2])
            correlation_matrix[f"{c1} <-> {c2}"] = r_val

    # Synthesize Executive Natural Language Summary
    summary_lines = [
        f"### Executive Exploratory Data Analysis (EDA): `{dataset_name}`",
        f"- **Total Records**: `{len(rows):,}` across `{len(cols_schema)}` columns.",
        f"- **Numeric Columns**: `{len(num_cols)}` | **Categorical/Text Columns**: `{len(cols_schema) - len(num_cols)}`."
    ]
    if correlation_matrix:
        strong_corrs = [f"`{k}` (r={v})" for k, v in correlation_matrix.items() if abs(v) >= 0.5]
        if strong_corrs:
            summary_lines.append(f"- **Key Correlated Relationships**: {', '.join(strong_corrs)}.")

    return {
        "status": "success",
        "dataset_name": dataset_name,
        "table_name": table_name,
        "row_count": len(rows),
        "column_count": len(cols_schema),
        "column_profiles": column_profiles,
        "correlation_matrix": correlation_matrix,
        "executive_summary_markdown": "\n".join(summary_lines)
    }
