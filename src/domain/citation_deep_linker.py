"""
Sentence-Level Deep Citation Linking Engine.
Generates exact target sentence character offsets and highlight snippets for UI deep-linking when clicking citations.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List


def create_deep_citation_link(
    citation_id: int,
    source_document_text: str,
    target_sentence: str
) -> Dict[str, Any]:
    """
    Finds exact character start/end offsets for a target sentence in a source document.
    """
    if not source_document_text or not isinstance(source_document_text, str):
        return {"citation_id": citation_id, "start_char": 0, "end_char": 0, "found": False}

    if not target_sentence or not isinstance(target_sentence, str):
        return {"citation_id": citation_id, "start_char": 0, "end_char": 0, "found": False}

    clean_target = target_sentence.strip()
    if not clean_target or len(clean_target) > len(source_document_text):
        return {"citation_id": citation_id, "start_char": 0, "end_char": 0, "found": False}

    start_pos = source_document_text.find(clean_target)
    if start_pos == -1:
        start_pos = source_document_text.lower().find(clean_target.lower())

    if start_pos != -1:
        end_pos = start_pos + len(clean_target)
        return {
            "citation_id": citation_id,
            "target_sentence": clean_target,
            "start_char": start_pos,
            "end_char": end_pos,
            "highlight_snippet": source_document_text[start_pos:end_pos],
            "found": True,
            "status": "success"
        }

    return {
        "citation_id": citation_id,
        "target_sentence": target_sentence.strip(),
        "start_char": 0,
        "end_char": 0,
        "highlight_snippet": target_sentence.strip(),
        "found": False,
        "status": "not_found"
    }
