"""
Adversarial Context Sanitizer Engine.
Scans and neutralizes indirect prompt injections, system override directives,
markdown escape exploits, and raw execution vectors from retrieved text before prompt assembly.
Zero-dependency standard library implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional, Union

# Zero-width / hidden unicode characters used in adversarial stealth attacks
_ZERO_WIDTH_CHARS = re.compile(r'[\u200B\u200C\u200D\u200E\u200F\uFEFF\u2060\u202A-\u202E]')

# Adversarial prompt injection & system override vector patterns
INJECTION_VECTOR_PATTERNS = [
    # Explicit system overrides & pseudo-delimiters
    (re.compile(r'\[\s*SYSTEM\s+OVERRIDE\s*\]', re.IGNORECASE), "[SANITIZED_SYSTEM_OVERRIDE]"),
    (re.compile(r'\[\s*SYSTEM\s*\]', re.IGNORECASE), "[SANITIZED_SYSTEM]"),
    (re.compile(r'<<SYS>>[\s\S]*?<</SYS>>', re.IGNORECASE), "[SANITIZED_SYS_TAG]"),
    (re.compile(r'<\|(?:im_start|im_end|system|user|assistant)\|>', re.IGNORECASE), "[SANITIZED_CONTROL_TOKEN]"),
    (re.compile(r'(?:^|\n)\s*(?:SYSTEM\s*PROMPT|SYSTEM\s*INSTRUCTION)\s*:\s*', re.IGNORECASE), "\n[SANITIZED_PROMPT_HEADER]: "),
    
    # Instruction negation / jailbreak commands
    (re.compile(r'(?:ignore|disregard|forget|override)\s+(?:all\s+)?(?:previous\s+|prior\s+|existing\s+|above\s+)?(?:instructions|prompts|rules|constraints|directives|guidelines)', re.IGNORECASE), "[SANITIZED_INSTRUCTION_OVERRIDE]"),
    (re.compile(r'you\s+are\s+now\s+in\s+(?:developer\s+mode|dan\s+mode|unrestricted\s+mode|god\s+mode)', re.IGNORECASE), "[SANITIZED_JAILBREAK_MODE]"),
    (re.compile(r'(?:bypass|disable|turn\s+off)\s+(?:safety|content|guardrail|security)\s+(?:filter|filters|checks|protocol)', re.IGNORECASE), "[SANITIZED_FILTER_BYPASS]"),
    (re.compile(r'(?:reveal|print|output|display|show|dump)\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions|system\s+instructions|hidden\s+rules)', re.IGNORECASE), "[SANITIZED_PROMPT_LEAK_ATTEMPT]"),
    
    # Markdown & HTML stealth injections
    (re.compile(r'\[(?:comment|//)\]:\s*#\s*\((?:[^)]*(?:ignore|system|instruction|override|eval|curl)[^)]*)\)', re.IGNORECASE), "[SANITIZED_MARKDOWN_COMMENT]"),
    (re.compile(r'<!--[\s\S]*?(?:ignore|system|instruction|override|eval|curl|powershell)[\s\S]*?-->', re.IGNORECASE), "[SANITIZED_HTML_COMMENT]"),
    (re.compile(r'\[(?:[^\]]*)\]\(\s*javascript:[^)]*\)', re.IGNORECASE), "[SANITIZED_JS_LINK]"),
    (re.compile(r'\[(?:[^\]]*)\]\(\s*data:text/html[^)]*\)', re.IGNORECASE), "[SANITIZED_DATA_URI]"),
    
    # Raw dangerous script execution & shell piped execution patterns
    (re.compile(r'(?:curl|wget)\s+-[sSkL]*\s*https?://\S+\s*\|\s*(?:ba)?sh', re.IGNORECASE), "[SANITIZED_REMOTE_EXEC]"),
    (re.compile(r'powershell(?:\.exe)?\s+(?:-enc|-encodedcommand)\s+[A-Za-z0-9+/=]+', re.IGNORECASE), "[SANITIZED_ENCODED_POWERSHELL]"),
    (re.compile(r'(?:rm\s+-rf\s+/(?:\s|$)|format\s+[c-z]:)', re.IGNORECASE), "[SANITIZED_DESTRUCTIVE_COMMAND]"),
    (re.compile(r'\b(?:eval|exec)\s*\(\s*(?:compile\s*\(|base64\.b64decode|__import__|unescape)', re.IGNORECASE), "[SANITIZED_DYNAMIC_EVAL]")
]


class ContextSanitizer:
    """
    Adversarial Context Sanitizer.
    Inspects, strips, and neutralizes prompt injection vectors, hidden markdown exploits,
    and remote execution payloads from retrieved contexts before passing to LLM KV-cache.
    """

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Strips adversarial injection vectors and hidden characters from raw retrieved text.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Normalize Unicode and strip zero-width stealth characters
        norm = unicodedata.normalize("NFC", str(text))
        cleaned = _ZERO_WIDTH_CHARS.sub("", norm)

        # 2. Neutralize injection patterns
        for pattern, replacement in INJECTION_VECTOR_PATTERNS:
            cleaned = pattern.sub(replacement, cleaned)

        return cleaned

    @classmethod
    def scan_and_clean(cls, text: str) -> Dict[str, Any]:
        """
        Performs in-depth audit of text for prompt injection vectors.
        Returns safety telemetry, list of detected vectors, and sanitized text.
        """
        if not text or not isinstance(text, str):
            return {
                "is_clean": True,
                "sanitized_text": "",
                "vectors_detected": [],
                "vectors_count": 0,
                "original_length": 0,
                "sanitized_length": 0
            }

        norm = unicodedata.normalize("NFC", str(text))
        has_zero_width = bool(_ZERO_WIDTH_CHARS.search(norm))
        cleaned = _ZERO_WIDTH_CHARS.sub("", norm)

        vectors_detected = []
        if has_zero_width:
            vectors_detected.append("zero_width_unicode_stealth")

        for pattern, replacement in INJECTION_VECTOR_PATTERNS:
            matches = pattern.findall(cleaned)
            if matches:
                vectors_detected.append(pattern.pattern)
                cleaned = pattern.sub(replacement, cleaned)

        is_clean = len(vectors_detected) == 0

        return {
            "is_clean": is_clean,
            "sanitized_text": cleaned,
            "vectors_detected": vectors_detected,
            "vectors_count": len(vectors_detected),
            "original_length": len(text),
            "sanitized_length": len(cleaned)
        }

    @classmethod
    def sanitize_chunks(cls, chunks: List[Any]) -> List[Any]:
        """
        Sanitizes a list of strings or dictionary chunk representations.
        """
        if not chunks:
            return []

        sanitized_list = []
        for c in chunks:
            if isinstance(c, str):
                sanitized_list.append(cls.sanitize_text(c))
            elif isinstance(c, dict):
                item = dict(c)
                if "content" in item:
                    item["content"] = cls.sanitize_text(str(item["content"]))
                if "snippet" in item:
                    item["snippet"] = cls.sanitize_text(str(item["snippet"]))
                if "text" in item:
                    item["text"] = cls.sanitize_text(str(item["text"]))
                sanitized_list.append(item)
            else:
                sanitized_list.append(c)

        return sanitized_list


def sanitize_context_for_rag(context: str) -> str:
    """Helper functional wrapper for RAG context sanitization."""
    return ContextSanitizer.sanitize_text(context)
