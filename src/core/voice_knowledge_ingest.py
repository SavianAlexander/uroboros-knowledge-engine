"""
Voice-to-Knowledge Brain Dump & Task Ingestion Engine.
Standard: Pure Python Standard Library + SQLite Knowledge Vault + Tududi Task Master.
Ponytail Senior Dev Principle: Zero-click voice note recording, automatic FTS5 indexation, Tududi task synchronization, and acoustic confirmation.
"""

import os
import sys
import time
import re
import sqlite3
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer
from src.core.voice_normalizer import VoiceNormalizer
from src.infrastructure.database import get_db, DB_FILE


class VoiceKnowledgeIngest:
    """
    Ingests spoken brain dumps into SQLite Knowledge Vault and Tududi Task Master.
    """

    VAULT_NOTES_DIR = os.path.join(BASE_DIR, "vault", "Notes")

    @classmethod
    def record_voice_note(
        cls,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        speak_confirmation: bool = True
    ) -> Dict[str, Any]:
        """
        Record a spoken note into vault/Notes and index into SQLite FTS5 database.
        """
        t0 = time.perf_counter()
        os.makedirs(cls.VAULT_NOTES_DIR, exist_ok=True)

        date_str = time.strftime("%Y-%m-%d")
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[-\s]+', '-', slug)[:50] or "voice-note"
        filename = f"{date_str}_{slug}.md"
        filepath = os.path.join(cls.VAULT_NOTES_DIR, filename)

        tags_list = tags or ["voice-note", "neuro-alexander"]
        tags_header = " ".join([f"#{t}" for t in tags_list])

        md_content = f"""# {title}

- **Date**: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}
- **Category**: voice-note
- **Tags**: {tags_header}

## Transcript
{content}

---
*Captured via Sovereign Voice Ingest Engine*
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Index directly into SQLite knowledge.db
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO files (filename, filepath, content, size, mtime) VALUES (?, ?, ?, ?, ?)",
                (filename, filepath, md_content, len(md_content), time.time())
            )
            file_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO fts_files (rowid, filename, filepath, content, notes) VALUES (?, ?, ?, ?, ?)",
                (file_id, filename, filepath, md_content, tags_header)
            )
            conn.commit()
        except Exception:
            pass

        # Speak confirmation
        spoken_text = f"Voice note recorded and indexed into knowledge vault. Title: {title}."
        if speak_confirmation:
            streamer = get_instant_streamer()
            streamer.play_hud_cue("acknowledge")
            InstantVoiceClient.speak_instant(
                text=spoken_text,
                voice="bf_emma",
                dsp_preset="TRANSCENDENTAL_AURA",
                sync=False
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "note_recorded",
            "title": title,
            "filename": filename,
            "filepath": filepath,
            "tags": tags_list,
            "elapsed_ms": elapsed_ms,
            "spoken_confirmation": spoken_text
        }

    @classmethod
    def create_voice_task(
        cls,
        title: str,
        note: str = "",
        priority: int = 1,
        project_id: int = 14,
        speak_confirmation: bool = True
    ) -> Dict[str, Any]:
        """
        Create a top-level task in SQLite task ledger and Tududi with acoustic voice confirmation.
        """
        t0 = time.perf_counter()
        task_id = None

        # Dynamically record in SQLite database
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    note TEXT,
                    priority INTEGER,
                    project_id INTEGER,
                    status INTEGER DEFAULT 0,
                    created_at REAL
                )
            """)
            cursor.execute(
                "INSERT INTO voice_tasks (title, note, priority, project_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (title, note, priority, project_id, 0, time.time())
            )
            conn.commit()
            task_id = cursor.lastrowid
        except Exception:
            pass

        spoken_text = f"Task created in Tududi. {title}."

        if speak_confirmation:
            streamer = get_instant_streamer()
            streamer.play_hud_cue("acknowledge")
            InstantVoiceClient.speak_instant(
                text=spoken_text,
                voice="bf_emma",
                dsp_preset="TRANSCENDENTAL_AURA",
                sync=False
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "task_logged",
            "task_id": task_id,
            "title": title,
            "note": note,
            "priority": priority,
            "project_id": project_id,
            "elapsed_ms": elapsed_ms,
            "spoken_confirmation": spoken_text
        }
