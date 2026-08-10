"""
Domain Chat Intelligence Engine.
Provides chat session lifecycle helpers, grounded citation parsing,
and context token length sliding window truncation logic.
"""

import json
from typing import List, Dict, Any, Tuple, Optional

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
    if not messages and not system_prompt:
        return []

    result_messages: List[Dict[str, Any]] = []

    # Handle system prompt
    sys_msg = None
    turn_messages = list(messages) if messages else []

    if turn_messages and turn_messages[0].get("role") == "system":
        sys_msg = turn_messages.pop(0)
    elif system_prompt:
        sys_msg = {"role": "system", "content": system_prompt}

    sys_tokens = estimate_tokens(sys_msg.get("content", "")) if sys_msg else 0
    remaining_budget = max(0, max_tokens - sys_tokens)

    # Collect turns from newest to oldest within remaining budget
    selected_turns: List[Dict[str, Any]] = []
    current_tokens = 0

    for msg in reversed(turn_messages):
        msg_content = msg.get("content", "")
        t_count = estimate_tokens(msg_content)
        if current_tokens + t_count <= remaining_budget:
            selected_turns.append(msg)
            current_tokens += t_count
        else:
            # Token budget reached
            break

    # Restore chronological order
    selected_turns.reverse()

    if sys_msg:
        result_messages.append(sys_msg)
    result_messages.extend(selected_turns)

    return result_messages

def parse_citations_and_metadata(
    citations_raw: Any,
    metadata_raw: Any
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses citations and metadata robustly, supporting JSON strings, dicts, lists,
    deep nested structures, unicode/emoji strings, and fallback empty structures.
    """
    citations: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

    # Parse citations
    if isinstance(citations_raw, str):
        try:
            parsed = json.loads(citations_raw)
            if isinstance(parsed, list):
                citations = parsed
            elif isinstance(parsed, dict):
                citations = [parsed]
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in chat_intelligence.py")
            citations = []
    elif isinstance(citations_raw, list):
        citations = citations_raw
    elif isinstance(citations_raw, dict):
        citations = [citations_raw]

    # Parse metadata
    if isinstance(metadata_raw, str):
        try:
            parsed = json.loads(metadata_raw)
            if isinstance(parsed, dict):
                metadata = parsed
            else:
                metadata = {"raw": parsed}
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in chat_intelligence.py")
            metadata = {"raw_string": metadata_raw}
    elif isinstance(metadata_raw, dict):
        metadata = metadata_raw
    elif metadata_raw is not None:
        metadata = {"value": metadata_raw}

    return citations, metadata

def format_message_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensures message list is properly sorted, role-validated,
    and returns formatted turns with parsed citations and metadata.
    """
    if not messages:
        return []

    formatted = []
    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        if role not in ("system", "user", "assistant"):
            role = "user"

        citations, metadata = parse_citations_and_metadata(
            msg.get("citations_json"),
            msg.get("metadata_json")
        )

        formatted.append({
            "id": msg.get("id"),
            "session_id": msg.get("session_id"),
            "sequence_index": idx,
            "role": role,
            "content": msg.get("content", ""),
            "citations": citations,
            "metadata": metadata,
            "tokens_used": msg.get("tokens_used", estimate_tokens(msg.get("content", ""))),
            "created_at": msg.get("created_at")
        })

    return formatted
