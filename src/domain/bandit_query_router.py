"""
Multi-Armed Bandit Query Router & Thompson Sampling Engine.
Dynamically optimizes retrieval pipeline selection (Hybrid RRF, HyDE, Graph BFS, Parent-Child)
using persistent SQLite-backed Beta distribution Thompson Sampling.
Standard: Pure Python standard library (sqlite3, random, time, unicodedata, typing).
"""
import time
import random
import sqlite3
import unicodedata
from typing import Dict, Any, List, Optional

_DEFAULT_ARMS = [
    ("hybrid_rrf_pagerank", 1.0, 1.0),
    ("multihop_graph_bfs", 1.0, 1.0),
    ("contextual_hyde", 1.0, 1.0),
    ("parent_child_expand", 1.0, 1.0)
]


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

    # Seed baseline arms for default FACTUAL intent if fresh
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
    Selects the optimal retrieval pipeline using Bayesian Thompson Sampling from SQLite.
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
                # Fall back to FACTUAL general arms if specific intent has no history
                cursor.execute(
                    "SELECT pipeline_name, trials, successes, alpha, beta, weight FROM bandit_pipeline_rewards WHERE intent = 'FACTUAL'"
                )
                rows = cursor.fetchall()

            for row in rows:
                p_name, trials, successes, alpha, beta, weight = row
                a = max(1.0, float(alpha))
                b = max(1.0, float(beta))
                # Real Thompson sampling from Beta distribution
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
        # Graceful fallback to deterministic default arm
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
    Updates the Bayesian reward distribution in SQLite for the selected pipeline.
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
