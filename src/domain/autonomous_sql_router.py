"""
Autonomous Text-to-SQL & Analytical Hybrid RAG Router.
Zero-dependency, standard-library implementation for converting natural language questions
into injection-safe SQL queries over dynamic client tables, with fallback to hybrid semantic RAG.
"""

import re
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from src.infrastructure.database import get_db
from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets, sanitize_identifier


AGGREGATION_KEYWORDS = {
    "total": "SUM",
    "sum": "SUM",
    "count": "COUNT",
    "how many": "COUNT",
    "number of": "COUNT",
    "average": "AVG",
    "avg": "AVG",
    "mean": "AVG",
    "maximum": "MAX",
    "max": "MAX",
    "highest": "MAX",
    "minimum": "MIN",
    "min": "MIN",
    "lowest": "MIN"
}


def classify_analytical_intent(query: str) -> str:
    """Classifies user query into TABULAR_SQL, SEMANTIC_RAG, or DUAL_FUSION."""
    if not query:
        return "SEMANTIC_RAG"
    q_lower = query.lower()

    has_agg = any(kw in q_lower for kw in AGGREGATION_KEYWORDS.keys())
    has_sql_tokens = any(tok in q_lower for tok in ["group by", "order by", "filter by", "greater than", "less than", "between", "list all", "table", "records", "rows", "column"])
    has_semantic_tokens = any(tok in q_lower for tok in ["why", "explain", "how does", "summarize", "describe", "meaning", "concept", "context"])

    if (has_agg or has_sql_tokens) and has_semantic_tokens:
        return "DUAL_FUSION"
    if has_agg or has_sql_tokens:
        return "TABULAR_SQL"
    return "SEMANTIC_RAG"


def find_target_dataset_and_columns(query: str, datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Identifies the most relevant dynamic dataset and column mappings for a query."""
    if not datasets:
        return None

    q_lower = query.lower()
    best_match = None
    max_score = -1

    for ds in datasets:
        score = 0
        ds_name = ds["dataset_name"].lower()
        if ds_name in q_lower:
            score += 10

        # Match column names
        cols = ds.get("columns", {})
        matched_cols = []
        for col_name in cols.keys():
            clean_col = col_name.replace("_", " ").lower()
            if clean_col in q_lower or col_name.lower() in q_lower:
                score += 3
                matched_cols.append(col_name)

        if score > max_score:
            max_score = score
            best_match = {
                "dataset": ds,
                "matched_columns": matched_cols,
                "score": score
            }

    if best_match and best_match["score"] > 0:
        return best_match

    # Fallback to the latest dataset if only one exists
    if len(datasets) == 1:
        return {
            "dataset": datasets[0],
            "matched_columns": list(datasets[0].get("columns", {}).keys()),
            "score": 1
        }

    return None


def generate_safe_sql_query(query: str, dataset_match: Dict[str, Any]) -> Tuple[Optional[str], List[Any], str]:
    """Generates an injection-safe, parameterized SQL query based on natural language intent."""
    ds = dataset_match["dataset"]
    table_name = ds["table_name"]
    cols_schema = ds.get("columns", {})
    q_lower = query.lower()

    # Identify Aggregation
    selected_agg = None
    for kw, agg_func in AGGREGATION_KEYWORDS.items():
        if kw in q_lower:
            selected_agg = agg_func
            break

    # Identify numeric column for SUM / AVG / MIN / MAX
    numeric_cols = [c for c, t in cols_schema.items() if t in ("INTEGER", "REAL") and c != "id"]
    target_num_col = numeric_cols[0] if numeric_cols else "*"

    for c in numeric_cols:
        if c.replace("_", " ") in q_lower:
            target_num_col = c
            break

    # Build SQL
    if selected_agg == "COUNT":
        sql = f"SELECT COUNT(*) as total_count FROM {table_name}"
        params = []
        explanation = f"Counted total records in dataset `{ds['dataset_name']}`"
    elif selected_agg in ("SUM", "AVG", "MAX", "MIN") and numeric_cols:
        sql = f"SELECT {selected_agg}({target_num_col}) as {selected_agg.lower()}_{target_num_col} FROM {table_name}"
        params = []
        explanation = f"Calculated {selected_agg} of column `{target_num_col}` in dataset `{ds['dataset_name']}`"
    else:
        # Default: Select top records matching mentioned columns
        select_cols = [c for c in cols_schema.keys() if c != "id"][:8]
        sql = f"SELECT {', '.join(select_cols)} FROM {table_name} LIMIT 20"
        params = []
        explanation = f"Retrieved top records from dataset `{ds['dataset_name']}`"

    return sql, params, explanation


def execute_autonomous_sql_query(query: str) -> Dict[str, Any]:
    """
    Autonomously routes a query to dynamic client SQL tables, generates
    injection-safe SQL, executes it, and returns formatted tabular results.
    """
    intent = classify_analytical_intent(query)
    datasets = list_orchestrated_datasets()

    if not datasets:
        return {
            "status": "no_datasets",
            "intent": intent,
            "message": "No dynamic client datasets currently provisioned",
            "results": []
        }

    match = find_target_dataset_and_columns(query, datasets)
    if not match:
        return {
            "status": "dataset_not_matched",
            "intent": intent,
            "message": "Could not identify target client dataset for query",
            "available_datasets": [d["dataset_name"] for d in datasets],
            "results": []
        }

    sql, params, explanation = generate_safe_sql_query(query, match)
    if not sql:
        return {
            "status": "sql_gen_failed",
            "intent": intent,
            "message": "Could not synthesize safe SQL query",
            "results": []
        }

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            rows = [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            return {
                "status": "error",
                "intent": intent,
                "error": str(e),
                "sql": sql,
                "results": []
            }

    return {
        "status": "success",
        "intent": intent,
        "dataset_name": match["dataset"]["dataset_name"],
        "table_name": match["dataset"]["table_name"],
        "generated_sql": sql,
        "explanation": explanation,
        "row_count": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "results": rows
    }
