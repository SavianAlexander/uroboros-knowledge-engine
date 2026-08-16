"""
Conversation Context Compression & Memory Summarization Engine.
Extracts salient topics, user intents, and system decisions from conversation history to fit context budgets.
Standard: Pure Python standard library (unicodedata, re, typing).
"""
import re
import unicodedata
from typing import Dict, Any, List


def compress_context_memory(
    chat_history: List[Dict[str, str]],
    target_summary_len: int = 250
) -> Dict[str, Any]:
    """
    Compresses chat history into a dense semantic context memory summary.
    Extracts key queries and responses while stripping conversational filler.
    """
    if not chat_history:
        return {
            "compressed_memory_summary": "",
            "summary": "",
            "original_char_length": 0,
            "compressed_char_length": 0,
            "compression_ratio": 0.0,
            "status": "empty_history"
        }

    user_turns = []
    assistant_turns = []

    for msg in chat_history:
        role = msg.get("role")
        content = unicodedata.normalize("NFC", str(msg.get("content", ""))).strip()
        if not content:
            continue
        if role == "user":
            user_turns.append(content)
        elif role == "assistant":
            assistant_turns.append(content)

    # Extract distinct topics
    user_topics = [re.sub(r'[\r\n]+', ' ', turn)[:80] for turn in user_turns[-4:]]
    asst_conclusions = [re.sub(r'[\r\n]+', ' ', turn)[:80] for turn in assistant_turns[-3:]]

    summary_parts = []
    if user_topics:
        summary_parts.append(f"User inquired: {'; '.join(user_topics)}")
    if asst_conclusions:
        summary_parts.append(f"System resolved: {'; '.join(asst_conclusions)}")

    summary_text = " | ".join(summary_parts)[:target_summary_len]
    original_length = sum(len(m.get("content", "")) for m in chat_history)
    summary_length = len(summary_text)

    compression_ratio = round(1.0 - (summary_length / float(max(1, original_length))), 4) if original_length > 0 else 0.0

    return {
        "compressed_memory_summary": summary_text,
        "summary": summary_text,
        "original_char_length": original_length,
        "compressed_char_length": summary_length,
        "compression_ratio": compression_ratio,
        "turns_processed": len(chat_history),
        "status": "success"
    }
