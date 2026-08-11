from src.infrastructure.database import get_db, get_db_connection, get_db_write_connection, get_pool
import src.infrastructure.database as db
import os
import re
import time
import glob
import shutil
import sqlite3
import hashlib
import threading
from typing import Dict, List, Any, Tuple, Optional, Callable
import mimetypes
import concurrent.futures
import uuid
import json
import contextlib
import logging
from datetime import datetime, timezone
import queue
from datetime import datetime, timezone
from pathlib import Path
from src.shared.security import get_file_acl
from src.core.domain.services import (
    extract_ai_tags,
    chunk_text,
)
from src.infrastructure.parsers import extract_content, parse_audio_metadata, calculate_sha256, calculate_sha256_cached

def create_workflow_trigger(
    name: str,
    event_type: str,
    webhook_url: str,
    condition_pattern: Optional[str] = "",
    secret_header: Optional[str] = "",
    is_active: bool = True
) -> Dict[str, Any]:
    """Create a new workflow trigger rule."""
    now = datetime.now(timezone.utc).isoformat()
    active_int = 1 if is_active else 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO workflow_triggers (name, event_type, condition_pattern, webhook_url, secret_header, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, event_type, condition_pattern or "", webhook_url, secret_header or "", active_int, now, now)
        )
        conn.commit()
        trigger_id = cursor.lastrowid
        return get_workflow_trigger(trigger_id)

def list_workflow_triggers(
    event_type: Optional[str] = None,
    active_only: bool = False
) -> List[Dict[str, Any]]:
    """List registered workflow trigger rules."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM workflow_triggers WHERE 1=1"
        params = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_workflow_trigger(trigger_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single workflow trigger by ID."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflow_triggers WHERE id = ?", (trigger_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_workflow_trigger(trigger_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update fields of an existing workflow trigger rule."""
    allowed_fields = {"name", "event_type", "condition_pattern", "webhook_url", "secret_header", "is_active"}
    updates = []
    params = []
    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            if key == "is_active":
                value = 1 if value else 0
            updates.append(f"{key} = ?")
            params.append(value)
    if not updates:
        return get_workflow_trigger(trigger_id)
    
    now = datetime.now(timezone.utc).isoformat()
    updates.append("updated_at = ?")
    params.append(now)
    params.append(trigger_id)
    
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE workflow_triggers SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
    return get_workflow_trigger(trigger_id)

def delete_workflow_trigger(trigger_id: int) -> bool:
    """Delete a workflow trigger rule by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workflow_triggers WHERE id = ?", (trigger_id,))
        conn.commit()
        return cursor.rowcount > 0

def log_workflow_execution(
    trigger_id: Optional[int],
    event_type: str,
    payload_json: str,
    status: str,
    response_status_code: Optional[int] = None,
    response_body: str = "",
    execution_time_ms: float = 0.0,
    retry_count: int = 0
) -> int:
    """Log an evaluation or HTTP POST delivery attempt to workflow_logs."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        real_trigger_id = trigger_id
        if real_trigger_id is not None:
            cursor.execute("SELECT 1 FROM workflow_triggers WHERE id = ?", (real_trigger_id,))
            if not cursor.fetchone():
                real_trigger_id = None
        cursor.execute(
            """
            INSERT INTO workflow_logs (
                trigger_id, event_type, payload_json, status,
                response_status_code, response_body, execution_time_ms,
                retry_count, executed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                real_trigger_id, event_type, payload_json, status,
                response_status_code, response_body[:2000] if response_body else "", execution_time_ms,
                retry_count, now
            )
        )
        conn.commit()
        return cursor.lastrowid

def list_workflow_logs(
    trigger_id: Optional[int] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """List recent workflow execution logs."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if trigger_id is not None:
            cursor.execute(
                "SELECT * FROM workflow_logs WHERE trigger_id = ? ORDER BY executed_at DESC, id DESC LIMIT ?",
                (trigger_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM workflow_logs ORDER BY executed_at DESC, id DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]