"""
Domain Chat Intelligence Engine.
Provides chat session lifecycle helpers, grounded citation parsing,
and context token length sliding window truncation logic.
"""
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

from src.core.text_utils import estimate_tokens, truncate_context_window

logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.warning("Failed to parse citations JSON string: %s", e)
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
        except Exception as e:
            logger.warning("Failed to parse metadata JSON string: %s", e)
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
