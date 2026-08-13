"""
Knowledge Graph Self-Healing & Wikilink Synthesizer.
Scans unlinked concept nodes across raw vault files and automatically inserts missing semantic [[wikilinks]].
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List, Set


def auto_synthesize_wikilinks(text_content: str, known_doc_titles: List[str]) -> Dict[str, Any]:
    """
    Scans text_content for unlinked occurrences of known_doc_titles and synthesizes [[wikilinks]].
    # ponytail: zero-dependency wikilink auto-synthesizer; ceiling: regex substring title match; upgrade: use Aho-Corasick automaton if vault document count exceeds 50,000 titles
    """
    if not text_content or not known_doc_titles:
        return {"status": "clean", "synthesized_text": text_content, "links_added": 0}

    synthesized = unicodedata.normalize("NFC", text_content)
    links_added = 0
    added_titles = []

    valid_titles = [str(t).strip() for t in (known_doc_titles or []) if t is not None and len(str(t).strip()) >= 3]
    # Sort titles by length descending so longer multi-word concepts (e.g. "Quantum Computing") match before sub-words ("Quantum")
    valid_titles.sort(key=len, reverse=True)
    for title in valid_titles:
        if title.lower() not in synthesized.lower():
            continue
        title_pattern = re.escape(title.strip())
        # Match title outside existing [[wikilinks]]
        pattern = re.compile(rf'(?<!\[\[)\b({title_pattern})\b(?!\]\])', re.IGNORECASE)
        
        matches = pattern.findall(synthesized)
        if matches:
            synthesized = pattern.sub(r'[[\1]]', synthesized)
            links_added += len(matches)
            added_titles.append(title)

    return {
        "status": "success",
        "original_char_count": len(text_content),
        "links_added": links_added,
        "synthesized_titles": added_titles,
        "synthesized_text": synthesized
    }
