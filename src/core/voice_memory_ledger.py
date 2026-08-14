"""
Autonomous Conversational Voice Memory Ledger & Ephemeral Transcript Engine.
Standard: Pure Python Standard Library (sqlite3, json, time, os, sys).
Ponytail Senior Dev Principle: Lightweight SQLite-backed conversational memory table preserving dialogue turns, transcripts, latency metrics, and semantic tags across reboots.
"""

import os
import sys
import sqlite3
import json
import time
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "knowledge.db")


class VoiceMemoryLedger:
    """Persistent SQLite conversational memory ledger for Antigravity neural voice engine."""

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_schema(cls):
        """Ensure voice_conversations table and indexes exist."""
        with cls._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS voice_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                speaker TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                normalized_text TEXT NOT NULL,
                persona TEXT NOT NULL,
                duration_ms REAL DEFAULT 0.0,
                domain TEXT DEFAULT 'GENERAL',
                metadata_json TEXT DEFAULT '{}'
            )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_voice_conv_session ON voice_conversations(session_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_voice_conv_ts ON voice_conversations(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_voice_conv_domain ON voice_conversations(domain);")
            conn.commit()

    @classmethod
    def log_turn(
        cls,
        speaker: str,
        raw_text: str,
        normalized_text: str,
        persona: str = "CALM_OPERATIONS",
        session_id: str = "default_session",
        duration_ms: float = 0.0,
        domain: str = "GENERAL",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record a single conversational turn in the ledger."""
        cls.init_schema()
        ts = time.time()
        meta_str = json.dumps(metadata or {})

        with cls._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO voice_conversations 
            (session_id, timestamp, speaker, raw_text, normalized_text, persona, duration_ms, domain, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, ts, speaker, raw_text, normalized_text, persona, duration_ms, domain, meta_str))
            turn_id = cur.lastrowid
            conn.commit()

        return {
            "turn_id": turn_id,
            "session_id": session_id,
            "timestamp": ts,
            "speaker": speaker,
            "persona": persona,
            "domain": domain
        }

    @classmethod
    def get_recent_turns(cls, limit: int = 10, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve recent conversational voice logs."""
        cls.init_schema()
        query = "SELECT * FROM voice_conversations"
        params = []
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with cls._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    @classmethod
    def get_voice_metrics(cls) -> Dict[str, Any]:
        """Compute aggregate voice dialogue metrics."""
        cls.init_schema()
        with cls._get_connection() as conn:
            total_turns = conn.execute("SELECT COUNT(*) FROM voice_conversations").fetchone()[0]
            avg_duration = conn.execute("SELECT AVG(duration_ms) FROM voice_conversations").fetchone()[0] or 0.0
            personas = conn.execute("SELECT persona, COUNT(*) as cnt FROM voice_conversations GROUP BY persona").fetchall()
            domains = conn.execute("SELECT domain, COUNT(*) as cnt FROM voice_conversations GROUP BY domain").fetchall()

            return {
                "total_recorded_turns": total_turns,
                "average_turn_duration_ms": round(avg_duration, 1),
                "persona_breakdown": {r["persona"]: r["cnt"] for r in personas},
                "domain_breakdown": {r["domain"]: r["cnt"] for r in domains}
            }
