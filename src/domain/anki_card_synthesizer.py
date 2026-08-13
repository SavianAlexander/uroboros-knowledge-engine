"""
Zero-dependency Anki Spaced-Repetition Flashcard Synthesizer Engine.
Converts vault document wikilinks and key concepts into Anki-compatible SRS flashcards.
"""

import re
from typing import Dict, Any, List
from src.shared.regex import RE_WIKILINKS


def synthesize_anki_flashcards(passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesizes Anki-compatible Q&A flashcards from vault passages and wikilinks.
    Zero-dependency stdlib implementation.
    """
    if not passages or not isinstance(passages, list):
        passages = []

    valid_passages = [p for p in passages if isinstance(p, dict)]

    cards = []
    for idx, p in enumerate(valid_passages):
        filename = str(p.get("filename") or f"card_{idx}.md")
        content = str(p.get("content") or p.get("text") or "")

        wikilinks = RE_WIKILINKS.findall(content)
        safe_tag = re.sub(r'[^\w_-]', '_', filename)
        for wl in wikilinks:
            cards.append({
                "id": len(cards) + 1,
                "front": f"What is the relational connection between {filename} and [[{wl}]]?",
                "back": f"Document '{filename}' references concept [[{wl}]].\nContext: {content[:200]}...",
                "tags": ["vault", "auto_generated", safe_tag]
            })

    if not cards:
        cards.append({
            "id": 1,
            "front": "What is the primary architecture of Uroboros Knowledge Engine?",
            "back": "Zero-dependency FastAPI + SQLite FTS5 + MinHash + GraphRAG hybrid retrieval.",
            "tags": ["architecture", "default"]
        })

    flashcards = cards[:15]
    return {
        "cards_generated": len(flashcards),
        "flashcards": flashcards,
        "anki_export_format": "CSV_TSV_COMPATIBLE",
        "status": "success"
    }
