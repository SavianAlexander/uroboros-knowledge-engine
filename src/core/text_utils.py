import os
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from typing import List, Dict, Any, Optional

_RE_WORD_BOUNDARIES = re.compile(r'\w+')
_RE_SENTENCE_BOUNDARIES = re.compile(r'(?<=[.!?])\s+')
_RE_CLEAN_FTS = re.compile(r'[\x00-\x1f\x7f\x80-\x9f]')
_RE_KEYWORD_OPERATORS = re.compile(r'\b(AND|OR|NOT|NEAR)\b', re.IGNORECASE)
_STOPWORDS = frozenset({'the', 'and', 'for', 'with', 'that', 'this', 'from', 'about', 'have', 'been', 'were', 'will'})


def normalize_nfc(text: str) -> str:
    """Ensure consistent NFC Unicode normalization."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


@lru_cache(maxsize=1024)
def sanitise_fts_query(query: str) -> str:
    """
    Sanitize search query for SQLite FTS5 syntax safety, injection prevention, and control characters.
    Handles accent normalization (NFC), strips unbalanced quotes and rogue operators.
    """
    if not query:
        return ""
    query = unicodedata.normalize("NFC", query)
    # Strip standalone or leading asterisks to prevent SQLite FTS5 unknown special query errors
    query = re.sub(r'(^|\s)\*+', ' ', query)
    # Strip dangerous FTS syntax symbols like /, =, <, >, ;, --, (, )
    cleaned = re.sub(r'[/<>=;~\\()|]|--', ' ', query)
    cleaned = _RE_CLEAN_FTS.sub('', cleaned)
    if '"' in cleaned:
        cleaned = cleaned.replace('"', ' ')
    cleaned = _RE_KEYWORD_OPERATORS.sub(' ', cleaned)
    words = [w for w in re.findall(r'\b[\w\-\*]+\b', cleaned) if w.lower() not in ('and', 'or', 'not', 'near')]
    if not words:
        return ""
    return " ".join(words)


# Backward-compatible alias
sanitize_fts_query = sanitise_fts_query


@lru_cache(maxsize=1024)
def sanitize_tag(tag: str) -> str:
    """Sanitize and normalize tag string for query and storage."""
    if not tag:
        return ""
    return re.sub(r'[\s,#]+', '_', tag.strip().lower()).strip('_')


def estimate_tokens(text: str) -> int:
    """
    Estimates token count for a text string using word/character heuristics.
    Approx 1 token per 4 characters or 0.75 words, minimum 1 token for non-empty text.
    """
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(1, int(max(words * 1.3, chars / 4.0)))


def truncate_context_window(
    messages: List[Dict[str, Any]],
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Truncates turn history to fit within max_tokens budget:
    - Preserves system prompt at the top.
    - Applies a sliding window to retain the most recent user/assistant turns.
    - Maintains strict chronological sequence order.
    """
    if not messages or not isinstance(messages, list):
        if not system_prompt:
            return []
        messages = []

    result_messages: List[Dict[str, Any]] = []

    sys_msg = None
    turn_messages = list(messages) if messages else []

    if turn_messages and turn_messages[0].get("role") == "system":
        sys_msg = turn_messages.pop(0)
    elif system_prompt:
        sys_msg = {"role": "system", "content": system_prompt}

    sys_tokens = estimate_tokens(sys_msg.get("content", "")) if sys_msg else 0
    remaining_budget = max(0, max_tokens - sys_tokens)

    selected_turns: List[Dict[str, Any]] = []
    current_tokens = 0

    for msg in reversed(turn_messages):
        msg_content = msg.get("content", "")
        t_count = estimate_tokens(msg_content)
        if current_tokens + t_count <= remaining_budget:
            selected_turns.append(msg)
            current_tokens += t_count
        else:
            break

    selected_turns.reverse()

    if sys_msg:
        result_messages.append(sys_msg)
    result_messages.extend(selected_turns)

    return result_messages


def extract_top_keywords(text: str, top_k: int = 5, max_chars: int = 50000) -> List[str]:
    """Extract top common keywords from text payload for auto-tagging and suggestions."""
    if not text:
        return []
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text[:max_chars])]
    freq = Counter(w for w in words if w not in _STOPWORDS)
    return [w for w, _ in freq.most_common(top_k)]


def build_token_budget_context(chunks: List[str], max_tokens: int = 2000) -> str:
    """Packs text chunks into a single concatenated string strictly respecting token budget and protecting against table overflow."""
    if not chunks:
        return ""
    packed: List[str] = []
    budget = max_tokens
    for chunk in chunks:
        if not chunk or not chunk.strip():
            continue

        c_text = chunk.strip()
        # Tabular protection: if a table chunk is exceedingly long, cap data rows
        if "|" in c_text and c_text.count("\n") > 25:
            table_lines = c_text.splitlines()
            if len(table_lines) > 25:
                c_text = "\n".join(table_lines[:20]) + "\n| ... (remaining table rows truncated for context budget) |"

        c_tokens = estimate_tokens(c_text)
        if c_tokens <= budget:
            packed.append(c_text)
            budget -= c_tokens
        else:
            char_allowance = max(0, budget * 4)
            if char_allowance > 50:
                packed.append(c_text[:char_allowance].strip() + "...")
            break
    return "\n\n".join(packed)


def smart_extract_context(context: str, query: str, max_chars: int = 6000) -> str:
    """
    Extracts the highest relevance sentence blocks from a context payload
    based on query keyword density and token budgeting.
    """
    if not context or len(context) <= max_chars:
        return context or ""

    blocks = [b.strip() for b in context.split("\n\n") if b.strip()]
    if blocks and len(blocks) > 1:
        packed = build_token_budget_context(blocks, max_tokens=max_chars // 4)
        if packed:
            return packed

    keywords = {kw for kw in _RE_WORD_BOUNDARIES.findall(query.lower()) if len(kw) > 3 and kw not in _STOPWORDS}
    if not keywords:
        return context[:max_chars]

    sentences = _RE_SENTENCE_BOUNDARIES.split(context)
    scored = []
    for idx, s in enumerate(sentences):
        sentence_words = set(_RE_WORD_BOUNDARIES.findall(s.lower()))
        score = len(sentence_words & keywords)
        scored.append((score, idx, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected_indices = []
    current_len = 0
    for score, idx, s in scored:
        if current_len + len(s) > max_chars:
            continue
        selected_indices.append(idx)
        current_len += len(s)

    selected_indices.sort()
    selected_text = " ... ".join([sentences[i] for i in selected_indices])
    return selected_text if selected_text else context[:max_chars]

