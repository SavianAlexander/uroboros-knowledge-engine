"""
Temporal Chronology & Topic Evolution Trajectory Engine.
Extracts chronological milestones, timestamped events, and conceptual trajectory across vault documents.
Zero-dependency standard-library implementation.
"""
import re
import time
import unicodedata
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.infrastructure.database import get_db

ISO_DATE_PATTERN = re.compile(r'\b(20\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01]))\b')
YEAR_MONTH_PATTERN = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(?:20\d{2})\b', re.IGNORECASE)
YEAR_PATTERN = re.compile(r'\b(202[0-9]|201[5-9])\b')


def extract_timeline_events_from_text(text: str, filename: str, fallback_timestamp: float) -> List[Dict[str, Any]]:
    """Extracts chronological events and context snippets from document text."""
    if not text:
        return []
    
    events = []
    lines = text.split("\n")
    seen_dates = set()

    for line in lines:
        clean_line = line.strip()
        if not clean_line or len(clean_line) < 15:
            continue

        # 1. Check ISO Dates (YYYY-MM-DD)
        for m in ISO_DATE_PATTERN.finditer(clean_line):
            d_str = m.group(1).replace("/", "-")
            if d_str not in seen_dates:
                seen_dates.add(d_str)
                try:
                    ts = datetime.strptime(d_str, "%Y-%m-%d").timestamp()
                except Exception:
                    ts = fallback_timestamp
                events.append({
                    "date_str": d_str,
                    "timestamp": ts,
                    "filename": filename,
                    "snippet": clean_line[:180],
                    "type": "explicit_iso_date"
                })

        # 2. Check Month Year (e.g. August 2026)
        for m in YEAR_MONTH_PATTERN.finditer(clean_line):
            d_str = m.group(0)
            if d_str.lower() not in seen_dates:
                seen_dates.add(d_str.lower())
                events.append({
                    "date_str": d_str,
                    "timestamp": fallback_timestamp,
                    "filename": filename,
                    "snippet": clean_line[:180],
                    "type": "month_year_mention"
                })

    if not events:
        # Fallback to document creation / modification milestone
        try:
            date_str = datetime.fromtimestamp(fallback_timestamp).strftime("%Y-%m-%d")
        except Exception:
            date_str = "2026-08-13"
        events.append({
            "date_str": date_str,
            "timestamp": fallback_timestamp,
            "filename": filename,
            "snippet": lines[0][:140] if lines else filename,
            "type": "document_mtime_milestone"
        })

    return events


def generate_vault_timeline(topic: str = "", limit: int = 25) -> Dict[str, Any]:
    """
    Generates a chronological knowledge trajectory across all matching vault documents.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            if topic and topic.strip():
                norm_topic = unicodedata.normalize("NFC", topic.strip())
                cursor.execute("""
                    SELECT id, filename, filepath, modified_at, content 
                    FROM files 
                    WHERE filename LIKE ? OR content LIKE ?
                    LIMIT 50
                """, (f"%{norm_topic}%", f"%{norm_topic}%"))
            else:
                cursor.execute("""
                    SELECT id, filename, filepath, modified_at, content 
                    FROM files 
                    ORDER BY modified_at DESC
                    LIMIT 50
                """)
            rows = cursor.fetchall()

        all_events = []
        for r in rows:
            fn = r[1] or "document"
            mtime = float(r[3] or time.time())
            content = r[4] or ""
            events = extract_timeline_events_from_text(content, fn, mtime)
            all_events.extend(events)

        # Sort events chronologically
        all_events.sort(key=lambda x: x["timestamp"])

        timeline = all_events[:limit]
        return {
            "status": "success",
            "topic": topic,
            "total_events": len(timeline),
            "timeline": timeline,
            "start_date": timeline[0]["date_str"] if timeline else None,
            "end_date": timeline[-1]["date_str"] if timeline else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "timeline": []}
