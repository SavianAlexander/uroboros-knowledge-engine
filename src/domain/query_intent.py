"""
Unified Semantic Query Intent Classifier & Thompson Sampling Bandit Router.
Consolidates query intent disambiguation, keyword matching heuristics,
and persistent SQLite-backed Beta distribution Thompson Sampling.
Standard: Pure Python standard library (sqlite3, random, time, unicodedata, typing, re).
"""

import re
import time
import random
import sqlite3
import unicodedata
from typing import Dict, Any, List, Optional, Tuple, Set

# Semantic Classification Keywords
CODE_KEYWORDS: Set[str] = {"def", "function", "class", "import", "api", "struct", "code", "method", "enum", "const", "let", "var"}
MATH_KEYWORDS: Set[str] = {"table", "revenue", "quarter", "profit", "percent", "sum", "average", "total", "margin", "count"}
SUMMARY_KEYWORDS: Set[str] = {"summary", "overview", "briefing", "report", "explain", "architecture"}
COMPARE_KEYWORDS: Set[str] = {"vs", "versus", "compare", "difference", "contrast", "compared"}
PATHFINDING_KEYWORDS: Set[str] = {"path", "connection", "relationship", "network", "connect", "links", "hop"}

_DEFAULT_ARMS: List[Tuple[str, float, float]] = [
    ("hybrid_rrf_pagerank", 1.0, 1.0),
    ("multihop_graph_bfs", 1.0, 1.0),
    ("contextual_hyde", 1.0, 1.0),
    ("parent_child_expand", 1.0, 1.0)
]


def classify_query_intent(query: str) -> Dict[str, Any]:
    """
    Classifies user query intent and provides recommended search parameter presets.
    """
    if not query or not isinstance(query, str):
        return {
            "query": "",
            "intent": "factual_lookup",
            "confidence": 1.0,
            "recommended_preset": {"top_k": 5, "rerank": True},
            "recommended_pipeline": "fts5_exact_search",
            "status": "success"
        }
    norm_query = unicodedata.normalize("NFC", query)
    words = set(re.findall(r'\b[\w-]+\b', norm_query.lower()))

    code_count = len(words.intersection(CODE_KEYWORDS))
    math_count = len(words.intersection(MATH_KEYWORDS))
    summary_count = len(words.intersection(SUMMARY_KEYWORDS))
    compare_count = len(words.intersection(COMPARE_KEYWORDS))
    path_count = len(words.intersection(PATHFINDING_KEYWORDS))

    if compare_count >= 1:
        intent = "comparative_analysis"
        confidence = min(0.95, 0.70 + compare_count * 0.1)
        preset = {"strategy": "subquery_table_diff", "top_k": 5, "side_by_side": True}
        pipeline = "multi_query_decomposition"
    elif path_count >= 1:
        intent = "exploratory_pathfinding"
        confidence = min(0.95, 0.70 + path_count * 0.1)
        preset = {"strategy": "graph_bfs", "top_k": 10, "multihop": True}
        pipeline = "graph_multihop_traversal"
    elif code_count >= 1:
        intent = "code_search"
        confidence = min(0.95, 0.70 + code_count * 0.1)
        preset = {"strategy": "cross_encoder", "top_k": 10, "entropy_chunking": True}
        pipeline = "fts5_code_symbols"
    elif math_count >= 1:
        intent = "tabular_math"
        confidence = min(0.95, 0.70 + math_count * 0.1)
        preset = {"strategy": "schema_rag", "top_k": 5, "table_header_inject": True}
        pipeline = "schema_rag_extractor"
    elif summary_count >= 1:
        intent = "analytical_summary"
        confidence = min(0.95, 0.70 + summary_count * 0.1)
        preset = {"strategy": "parent_child", "top_k": 8, "speculative_synthesis": True}
        pipeline = "contextual_hyde_expansion"
    else:
        intent = "factual_lookup"
        confidence = 0.85 if len(words) <= 3 else 0.75
        preset = {"strategy": "auto_unified", "top_k": 5, "colbert_rerank": True}
        pipeline = "fts5_exact_search"

    return {
        "query": query,
        "intent": intent,
        "confidence": round(confidence, 2),
        "recommended_preset": preset,
        "recommended_pipeline": pipeline,
        "status": "success"
    }


# Routing aliases
route_query_intent = classify_query_intent
route_intent = classify_query_intent


def _init_bandit_table(conn: sqlite3.Connection):
    """Initializes the persistent bandit pipeline rewards table in SQLite."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bandit_pipeline_rewards (
            pipeline_name TEXT NOT NULL,
            intent TEXT NOT NULL DEFAULT 'FACTUAL',
            trials INTEGER NOT NULL DEFAULT 0,
            successes INTEGER NOT NULL DEFAULT 0,
            alpha REAL NOT NULL DEFAULT 1.0,
            beta REAL NOT NULL DEFAULT 1.0,
            weight REAL NOT NULL DEFAULT 0.5,
            updated_at REAL,
            PRIMARY KEY (pipeline_name, intent)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bandit_intent ON bandit_pipeline_rewards(intent, weight DESC)")

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bandit_pipeline_rewards")
    if (cursor.fetchone() or [0])[0] == 0:
        now = time.time()
        for arm_name, a, b in _DEFAULT_ARMS:
            cursor.execute("""
                INSERT INTO bandit_pipeline_rewards (pipeline_name, intent, trials, successes, alpha, beta, weight, updated_at)
                VALUES (?, 'FACTUAL', 0, 0, ?, ?, 0.5, ?)
            """, (arm_name, a, b, now))
        conn.commit()


def bandit_select_pipeline(intent: str = "FACTUAL") -> Dict[str, Any]:
    """
    Selects optimal retrieval pipeline using Bayesian Thompson Sampling from SQLite.
    Draws a random sample from Beta(alpha, beta) for each active pipeline arm.
    """
    safe_intent = unicodedata.normalize("NFC", str(intent or "FACTUAL")).strip().upper()
    best_arm = "hybrid_rrf_pagerank"
    best_score = -1.0
    arms_state: Dict[str, Dict[str, Any]] = {}

    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_bandit_table(conn)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT pipeline_name, trials, successes, alpha, beta, weight FROM bandit_pipeline_rewards WHERE intent = ?",
                (safe_intent,)
            )
            rows = cursor.fetchall()

            if not rows and safe_intent != "FACTUAL":
                cursor.execute(
                    "SELECT pipeline_name, trials, successes, alpha, beta, weight FROM bandit_pipeline_rewards WHERE intent = 'FACTUAL'"
                )
                rows = cursor.fetchall()

            for row in rows:
                p_name, trials, successes, alpha, beta, weight = row
                a = max(1.0, float(alpha))
                b = max(1.0, float(beta))
                sample = random.betavariate(a, b)
                arms_state[p_name] = {
                    "trials": trials,
                    "successes": successes,
                    "alpha": a,
                    "beta": b,
                    "sample": round(sample, 4),
                    "weight": round(weight, 4)
                }

                if sample > best_score:
                    best_score = sample
                    best_arm = p_name

    except Exception as e:
        arms_state["hybrid_rrf_pagerank"] = {"sample": 0.85, "error": str(e)}
        best_arm = "hybrid_rrf_pagerank"
        best_score = 0.85

    return {
        "intent": safe_intent,
        "selected_pipeline": best_arm,
        "bandit_confidence": round(best_score if best_score >= 0 else 0.80, 4),
        "arms_state": arms_state,
        "status": "success"
    }


def record_bandit_feedback(
    pipeline_name: str,
    is_successful: bool,
    intent: str = "FACTUAL"
) -> Dict[str, Any]:
    """
    Updates Bayesian reward distribution in SQLite for the selected pipeline.
    Success increments alpha; failure increments beta.
    """
    if not pipeline_name:
        return {"status": "error", "message": "pipeline_name is required"}

    p_str = str(pipeline_name).strip()
    safe_intent = unicodedata.normalize("NFC", str(intent or "FACTUAL")).strip().upper()
    now = time.time()

    try:
        from src.infrastructure.database import get_db
        with get_db() as conn:
            _init_bandit_table(conn)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT trials, successes, alpha, beta FROM bandit_pipeline_rewards WHERE pipeline_name = ? AND intent = ?",
                (p_str, safe_intent)
            )
            row = cursor.fetchone()

            if row:
                t = row[0] + 1
                s = row[1] + (1 if is_successful else 0)
                a = row[2] + (1.0 if is_successful else 0.0)
                b = row[3] + (0.0 if is_successful else 1.0)
            else:
                t = 1
                s = 1 if is_successful else 0
                a = 2.0 if is_successful else 1.0
                b = 1.0 if is_successful else 2.0

            w = round(s / float(max(1, t)), 4)

            cursor.execute("""
                INSERT INTO bandit_pipeline_rewards (pipeline_name, intent, trials, successes, alpha, beta, weight, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(pipeline_name, intent) DO UPDATE SET
                    trials = excluded.trials,
                    successes = excluded.successes,
                    alpha = excluded.alpha,
                    beta = excluded.beta,
                    weight = excluded.weight,
                    updated_at = excluded.updated_at
            """, (p_str, safe_intent, t, s, a, b, w, now))
            conn.commit()

            return {
                "pipeline": p_str,
                "intent": safe_intent,
                "updated_arm": {
                    "trials": t,
                    "successes": s,
                    "alpha": a,
                    "beta": b,
                    "weight": w
                },
                "status": "success"
            }
    except Exception as e:
        return {
            "pipeline": p_str,
            "status": "error",
            "error": str(e)
        }


class BanditQueryRouter:
    """Facade for Thompson Sampling retrieval pipeline selection."""

    @staticmethod
    def select(intent: str = "FACTUAL") -> Dict[str, Any]:
        return bandit_select_pipeline(intent)

    @staticmethod
    def record(pipeline_name: str, is_successful: bool, intent: str = "FACTUAL") -> Dict[str, Any]:
        return record_bandit_feedback(pipeline_name, is_successful, intent)
