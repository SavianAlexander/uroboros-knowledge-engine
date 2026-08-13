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

def create_chat_session(
    title: Optional[str] = None,
    model_path: Optional[str] = None,
    temperature: float = 0.7,
    context_window: int = 4096,
    metadata_json: Optional[Any] = None
) -> Dict[str, Any]:
    """Create a new chat session in SQLite database."""
    session_id = uuid.uuid4().hex
    now_iso = datetime.now(timezone.utc).isoformat()
    session_title = title if title is not None else "New Chat"
    meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json
    
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at, model_path, temperature, context_window, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, session_title, time.time(), time.time(), model_path, temperature, context_window, meta_str))
        conn.commit()

    return {
        "id": session_id,
        "user_id": user_id,
        "title": session_title,
        "created_at": now_iso,
        "updated_at": now_iso,
        "model_path": model_path,
        "temperature": temperature,
        "context_window": context_window,
        "metadata_json": metadata_json
    }

def list_chat_sessions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """List most recent chat sessions."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at, model_path, temperature, context_window, metadata_json
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        rows = cursor.fetchall()
        
    sessions = []
    for r in rows:
        d = dict(r)
        if d.get("metadata_json"):
            try:
                d["metadata_json"] = json.loads(d["metadata_json"])
            except (ValueError, TypeError, json.JSONDecodeError):
                pass
        sessions.append(d)
    return sessions

def get_chat_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get full chat session including ordered messages."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None
        session_dict = dict(row)
        session_dict["messages"] = get_chat_messages(session_id)
        return session_dict

def update_chat_session(
    session_id: str,
    title: Optional[str] = None,
    model_path: Optional[str] = None,
    temperature: Optional[float] = None,
    context_window: Optional[int] = None,
    metadata_json: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """Update metadata and parameters for a chat session."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        if not cursor.fetchone():
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        updates = ["updated_at = ?"]
        params: List[Any] = [now_iso]

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if model_path is not None:
            updates.append("model_path = ?")
            params.append(model_path)
        if temperature is not None:
            updates.append("temperature = ?")
            params.append(temperature)
        if context_window is not None:
            updates.append("context_window = ?")
            params.append(context_window)
        if metadata_json is not None:
            meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json
            updates.append("metadata_json = ?")
            params.append(meta_str)

        params.extend([session_id, user_id])
        sql = f"UPDATE chat_sessions SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        cursor.execute(sql, params)
        conn.commit()

    return get_chat_session(session_id)

def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session and cascade delete all associated messages."""
    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def add_chat_message(
    session_id: str,
    role: str,
    content: str,
    citations_json: Optional[Any] = None,
    web_sources_json: Optional[Any] = None,
    tokens_used: int = 0,
    metadata_json: Optional[Any] = None
) -> Dict[str, Any]:
    """Add a message turn to a chat session."""
    msg_id = uuid.uuid4().hex
    now_iso = datetime.now(timezone.utc).isoformat()
    cit_str = json.dumps(citations_json) if isinstance(citations_json, (dict, list)) else citations_json
    web_str = json.dumps(web_sources_json) if isinstance(web_sources_json, (dict, list)) else web_sources_json
    meta_str = json.dumps(metadata_json) if isinstance(metadata_json, (dict, list)) else metadata_json

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, content, cit_str, web_str, tokens_used or 0, now_iso, meta_str))
        cursor.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now_iso, session_id))
        conn.commit()

    return {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "citations_json": cit_str,
        "web_sources_json": web_str,
        "tokens_used": tokens_used or 0,
        "created_at": now_iso,
        "metadata_json": meta_str
    }

def get_chat_messages(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all messages for a session ordered by created_at ASC."""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]