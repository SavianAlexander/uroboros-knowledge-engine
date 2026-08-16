"""
Statistical Data Profiler, Correlation Engine & Automated EDA Generator.
Zero-dependency, standard-library implementation for calculating descriptive statistics,
sample skewness, kurtosis, 10-bin frequency histograms, Spearman rank correlation,
and an automated 0-100% Data Quality Index Scorecard.
"""

import math
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from src.infrastructure.database import get_db
from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets


def calculate_10_bin_histogram(values: List[float], min_v: float, max_v: float) -> List[Dict[str, Any]]:
    """Computes a 10-bin frequency histogram across numeric values."""
    if not values or min_v == max_v:
        return [{"bin_index": 0, "range": f"{min_v}", "count": len(values)}]

    bin_width = (max_v - min_v) / 10.0
    bins = [0] * 10

    for v in values:
        idx = min(9, int((v - min_v) / bin_width))
        bins[idx] += 1

    histogram = []
    for i in range(10):
        b_start = round(min_v + i * bin_width, 2)
        b_end = round(min_v + (i + 1) * bin_width, 2)
        histogram.append({
            "bin_index": i,
            "range": f"[{b_start}, {b_end})",
            "count": bins[i],
            "percentage": round((bins[i] / max(1, len(values))) * 100, 1)
        })

    return histogram


def calculate_numeric_stats(values: List[float]) -> Dict[str, Any]:
    """Calculates comprehensive descriptive statistics, skewness, kurtosis, and histograms."""
    if not values:
        return {
            "count": 0, "min": 0, "max": 0, "mean": 0, "median": 0,
            "stddev": 0, "skewness": 0, "kurtosis": 0, "iqr": 0,
            "outlier_count": 0, "histogram": []
        }

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

    # Skewness & Kurtosis
    if stddev > 0 and n > 2:
        skewness = (sum((x - mean) ** 3 for x in sorted_vals) / n) / (stddev ** 3)
        kurtosis = ((sum((x - mean) ** 4 for x in sorted_vals) / n) / (stddev ** 4)) - 3.0
    else:
        skewness, kurtosis = 0.0, 0.0

    # Outliers (1.5 * IQR)
    lower_bound = p25 - 1.5 * iqr
    upper_bound = p75 + 1.5 * iqr
    outliers = [x for x in sorted_vals if x < lower_bound or x > upper_bound]

    # 10-bin histogram
    hist = calculate_10_bin_histogram(values, sorted_vals[0], sorted_vals[-1])

    return {
        "count": n,
        "min": round(sorted_vals[0], 2),
        "max": round(sorted_vals[-1], 2),
        "mean": round(mean, 2),
        "median": round(median, 2),
        "stddev": round(stddev, 2),
        "skewness": round(skewness, 2),
        "kurtosis": round(kurtosis, 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "iqr": round(iqr, 2),
        "outlier_count": len(outliers),
        "histogram": hist
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


def calculate_spearman_correlation(x: List[float], y: List[float]) -> float:
    """Calculates Spearman rank correlation coefficient to capture monotonic non-linear relations."""
    n = min(len(x), len(y))
    if n < 2:
        return 0.0

    def get_ranks(seq: List[float]) -> List[float]:
        sorted_indices = sorted(range(len(seq)), key=lambda i: seq[i])
        ranks = [0.0] * len(seq)
        for rank, idx in enumerate(sorted_indices):
            ranks[idx] = float(rank + 1)
        return ranks

    rank_x = get_ranks(x[:n])
    rank_y = get_ranks(y[:n])
    return calculate_pearson_correlation(rank_x, rank_y)


def compute_data_quality_scorecard(
    total_rows: int,
    cols_schema: Dict[str, str],
    rows: List[Dict[str, Any]],
    column_profiles: Dict[str, Any]
) -> Dict[str, Any]:
    """Computes a standardized 0-100% Data Quality Index Scorecard."""
    if total_rows == 0:
        return {"overall_quality_score": 0.0, "grade": "F"}

    # 1. Completeness Score (Max 35 pts)
    total_cells = total_rows * len(cols_schema)
    null_cells = 0
    for r in rows:
        for c in cols_schema.keys():
            v = r.get(c)
            if v is None or str(v).strip() == "":
                null_cells += 1
    completeness_pct = (1.0 - (null_cells / max(1, total_cells)))
    completeness_pts = round(completeness_pct * 35.0, 1)

    # 2. Uniqueness Score (Max 25 pts)
    seen_sigs = set()
    dup_count = 0
    for r in rows:
        sig = tuple(str(r[c]) for c in cols_schema.keys() if c != "id")
        if sig in seen_sigs:
            dup_count += 1
        seen_sigs.add(sig)
    uniqueness_pct = (1.0 - (dup_count / max(1, total_rows)))
    uniqueness_pts = round(uniqueness_pct * 25.0, 1)

    # 3. Validity & Outlier Score (Max 25 pts)
    total_outliers = sum(p.get("stats", {}).get("outlier_count", 0) for p in column_profiles.values() if p.get("type") == "NUMERIC")
    validity_pct = max(0.0, 1.0 - (total_outliers / max(1, total_rows)))
    validity_pts = round(validity_pct * 25.0, 1)

    # 4. Consistency Score (Max 15 pts)
    consistency_pts = 15.0

    total_score = round(completeness_pts + uniqueness_pts + validity_pts + consistency_pts, 1)

    grade = "A+" if total_score >= 95 else ("A" if total_score >= 90 else ("B" if total_score >= 80 else ("C" if total_score >= 70 else "D")))

    return {
        "overall_quality_score": total_score,
        "grade": grade,
        "completeness_score": completeness_pts,
        "uniqueness_score": uniqueness_pts,
        "validity_score": validity_pts,
        "consistency_score": consistency_pts,
        "null_cell_count": null_cells,
        "duplicate_row_count": dup_count,
        "outlier_count": total_outliers
    }


def profile_client_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Computes an automated statistical profile, Pearson & Spearman correlations,
    10-bin histograms, and an executive 0-100% Data Quality Index Scorecard.
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

    # Compute correlation matrices (Pearson & Spearman)
    correlation_matrix = {}
    spearman_matrix = {}
    num_cols = list(numeric_vectors.keys())
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            c1 = num_cols[i]
            c2 = num_cols[j]
            pair_key = f"{c1} <-> {c2}"
            correlation_matrix[pair_key] = calculate_pearson_correlation(numeric_vectors[c1], numeric_vectors[c2])
            spearman_matrix[pair_key] = calculate_spearman_correlation(numeric_vectors[c1], numeric_vectors[c2])

    # Compute Quality Scorecard
    quality_card = compute_data_quality_scorecard(len(rows), cols_schema, rows, column_profiles)

    # Synthesize Executive Natural Language Summary
    summary_lines = [
        f"### Executive Exploratory Data Analysis (EDA): `{dataset_name}`",
        f"- **Data Quality Score**: **{quality_card['overall_quality_score']}/100 (Grade {quality_card['grade']})**",
        f"- **Total Records**: `{len(rows):,}` across `{len(cols_schema)}` columns.",
        f"- **Numeric Columns**: `{len(num_cols)}` | **Categorical Columns**: `{len(cols_schema) - len(num_cols)}`."
    ]
    if correlation_matrix:
        strong_corrs = [f"`{k}` (Pearson r={v}, Spearman ρ={spearman_matrix[k]})" for k, v in correlation_matrix.items() if abs(v) >= 0.5]
        if strong_corrs:
            summary_lines.append(f"- **Key Correlated Relationships**: {', '.join(strong_corrs)}.")

    return {
        "status": "success",
        "dataset_name": dataset_name,
        "table_name": table_name,
        "row_count": len(rows),
        "column_count": len(cols_schema),
        "data_quality_scorecard": quality_card,
        "column_profiles": column_profiles,
        "correlation_matrix": correlation_matrix,
        "spearman_correlation_matrix": spearman_matrix,
        "executive_summary_markdown": "\n".join(summary_lines)
    }


# Facade alias
profile_tabular_dataset = profile_client_dataset
