"""
Autonomous Knowledge Graph Synthesis and Write-Back Loop ("Uroboros Loop").
Extracts structured conceptual insights, definitions, and code solutions from AI completions
and dynamically persists them as atomic knowledge notes with HyperGraph Wikilink cross-references.
Standard: Python Standard Library (sqlite3, time, re, json, hashlib, typing).
"""

import os
import re
import time
import json
import sqlite3
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from src.infrastructure.database import get_db

logger = logging.getLogger(__name__)

RE_WIKILINKS = re.compile(r'\[\[(.*?)\]\]')
RE_MARKDOWN_HEADINGS = re.compile(r'^#{1,3}\s+(.+)$', re.MULTILINE)
RE_TAKEAWAYS = re.compile(r'(?:Key Takeaways?|Summary|Conclusion|Core Findings?):\s*(.*?)(?=\n#|\Z)', re.DOTALL | re.IGNORECASE)


class KnowledgeSynthesisLoop:
    """
    Closes the recursive knowledge loop:
    User Conversation -> Distillation -> Atomic Note Synthesis -> HyperGraph Linkage.
    """

    def __init__(self, min_token_length: int = 30):
        self.min_token_length = min_token_length

    def should_synthesize(self, user_query: str, assistant_response: str) -> bool:
        """Determine if an AI response contains durable, high-value knowledge."""
        if not assistant_response or len(assistant_response.split()) < self.min_token_length:
            return False
        
        synthesis_triggers = [
            "how to", "architecture", "design", "explain", "implement", "concept",
            "difference between", "protocol", "formula", "blueprint", "guide"
        ]
        q_lower = user_query.lower()
        has_trigger = any(t in q_lower for t in synthesis_triggers)
        has_structure = ("## " in assistant_response or "```" in assistant_response or "- " in assistant_response)
        return has_trigger and has_structure

    def extract_entities_and_wikilinks(self, text: str) -> List[str]:
        """Extract explicit [[wikilinks]] and prominent capitalized concept entities."""
        wikilinks = RE_WIKILINKS.findall(text)
        # Also discover capitalized multi-word entities (e.g., 'Clean Architecture', 'GraphRAG')
        words = re.findall(r'\b[A-Z][a-zA-Z0-9_]{2,}\b', text)
        stop_words = {"The", "This", "When", "What", "Here", "With", "From", "Your", "Based", "Note"}
        filtered_words = [w for w in set(words) if w not in stop_words and len(w) > 3]
        return list(set(wikilinks + filtered_words[:10]))

    def record_synthesis(
        self,
        session_id: int,
        user_query: str,
        assistant_response: str,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesize an atomic knowledge note from a chat turn and link into SQLite.
        """
        if not self.should_synthesize(user_query, assistant_response):
            return None

        t_now = time.time()
        title_match = RE_MARKDOWN_HEADINGS.search(assistant_response)
        title = title_match.group(1).strip() if title_match else user_query[:50].strip()
        safe_filename = re.sub(r'[^\w\-_]', '_', title.lower())[:60]
        filepath = f"synthesis/{safe_filename}.md"

        entities = self.extract_entities_and_wikilinks(assistant_response)
        wikilink_block = " ".join([f"[[{e}]]" for e in entities[:6]])

        note_content = (
            f"# {title}\n\n"
            f"> **Synthesized by Uroboros Knowledge Engine** | Origin Query: *{user_query}*\n"
            f"> **Connected Concepts:** {wikilink_block}\n\n"
            f"{assistant_response}\n\n"
            f"## Lineage Metadata\n"
            f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t_now))} UTC\n"
            f"- Chat Session ID: {session_id}\n"
        )

        content_hash = hashlib.sha256(note_content.encode("utf-8")).hexdigest()

        try:
            with get_db() as conn:
                conn.execute("PRAGMA busy_timeout = 5000")
                cursor = conn.cursor()

                # Insert or update synthesis record in files table
                insights_json = json.dumps({"origin": "uroboros_synthesis", "session_id": session_id, "entities": entities})
                cursor.execute("""
                    INSERT INTO files (filepath, filename, file_size, mime_type, modified_at, content, sha256, tags, insights)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(filepath) DO UPDATE SET
                        content = excluded.content,
                        file_size = excluded.file_size,
                        modified_at = excluded.modified_at,
                        sha256 = excluded.sha256,
                        tags = excluded.tags,
                        insights = excluded.insights
                """, (
                    filepath,
                    f"{safe_filename}.md",
                    len(note_content.encode("utf-8")),
                    "text/markdown",
                    t_now,
                    note_content,
                    content_hash,
                    "synthesis,ai_generated",
                    insights_json
                ))

                # Index in FTS table if present
                try:
                    cursor.execute("""
                        INSERT INTO fts_files (filepath, filename, content)
                        VALUES (?, ?, ?)
                        ON CONFLICT(filepath) DO UPDATE SET
                            content = excluded.content,
                            filename = excluded.filename
                    """, (filepath, f"{safe_filename}.md", note_content))
                except Exception:
                    pass

                conn.commit()

            logger.info(f"[KnowledgeSynthesis] Successfully synthesized atomic note: {filepath}")
            return {
                "filepath": filepath,
                "title": title,
                "sha256": content_hash,
                "entities": entities
            }
        except Exception as e:
            logger.warning(f"[KnowledgeSynthesis] Failed to persist synthesis: {e}")
            return None


# Global singleton instance
_synthesis_loop: Optional[KnowledgeSynthesisLoop] = None

def get_knowledge_synthesis_loop() -> KnowledgeSynthesisLoop:
    global _synthesis_loop
    if _synthesis_loop is None:
        _synthesis_loop = KnowledgeSynthesisLoop()
    return _synthesis_loop
