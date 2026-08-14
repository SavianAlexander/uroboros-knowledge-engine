"""
Conversational Query Reformulator & Multi-Turn Context Carry-Over.
Resolves conversational antecedents, pronouns, and implicit entity references into standalone search queries.
Zero-dependency, standard-library implementation.
"""
import re
import unicodedata
from typing import List, Dict, Any, Optional

PRONOUN_PATTERN = re.compile(r'\b(it|this|that|these|those|they|them|the second one|the first one|the previous|the latter|the former)\b', re.IGNORECASE)
ENTITY_PATTERN = re.compile(r'\b[A-Z][a-zA-Z0-9_-]{2,}\b|\b[a-z]{4,}(?:-[a-z0-9]+)+\b')


def extract_salient_entities(text: str) -> List[str]:
    """Extracts key entity tokens from prior conversational turns."""
    if not text:
        return []
    norm = unicodedata.normalize("NFC", text)
    stopwords = {
        "the", "this", "that", "what", "which", "when", "where", "with", "from", "have", "been",
        "about", "would", "could", "should", "there", "their", "here", "also", "into", "more"
    }
    words = re.findall(r'\b[a-zA-Z0-9_\-\.]{3,}\b', norm)
    salient = []
    for w in words:
        w_lower = w.lower()
        if w_lower not in stopwords and not w.isdigit():
            if w not in salient:
                salient.append(w)
    return salient[:8]


def reformulate_conversational_query(
    conversation_history: List[Dict[str, str]],
    current_query: str
) -> Dict[str, Any]:
    """
    Reformulates a multi-turn conversational query into a self-contained retrieval query.
    """
    safe_q = str(current_query or "").strip()
    if not conversation_history or not safe_q:
        return {
            "original_query": safe_q,
            "reformulated_query": safe_q,
            "has_pronouns": False,
            "injected_entities": [],
            "status": "success"
        }

    has_pronoun_match = bool(PRONOUN_PATTERN.search(safe_q))
    words = safe_q.split()
    is_short_followup = len(words) <= 5 and any(w.lower() in ["why", "how", "compare", "difference", "explain", "details", "more"] for w in words)

    if not has_pronoun_match and not is_short_followup:
        return {
            "original_query": safe_q,
            "reformulated_query": safe_q,
            "has_pronouns": False,
            "injected_entities": [],
            "status": "success"
        }

    # Extract entities from recent conversation turns (latest 3)
    recent_turns = conversation_history[-3:]
    candidate_entities = []
    for turn in reversed(recent_turns):
        user_text = turn.get("user") or turn.get("query") or turn.get("content") or ""
        asst_text = turn.get("assistant") or turn.get("response") or ""
        salient = extract_salient_entities(user_text) + extract_salient_entities(asst_text[:200])
        for ent in salient:
            if ent.lower() not in [e.lower() for e in candidate_entities]:
                candidate_entities.append(ent)

    injected = candidate_entities[:3]
    if injected:
        reformulated = f"{safe_q} ({' '.join(injected)})"
    else:
        reformulated = safe_q

    return {
        "original_query": safe_q,
        "reformulated_query": reformulated,
        "has_pronouns": has_pronoun_match,
        "injected_entities": injected,
        "status": "success"
    }
