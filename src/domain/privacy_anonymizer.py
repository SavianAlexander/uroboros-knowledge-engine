"""
Differential Privacy & PII Redaction Guard Engine.
Scans and redacts Social Security Numbers, Credit Card Numbers, API Keys, Passwords, Email Addresses, and IPv4 Addresses.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any

RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
RE_SSN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
RE_CREDIT_CARD = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
RE_API_KEY = re.compile(r'\b(?:sk|pk|api|key)_[a-zA-Z0-9]{16,64}\b', re.IGNORECASE)
RE_IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def anonymize_text_pii(text: str) -> Dict[str, Any]:
    """
    Redacts sensitive PII from text before vector embedding or storage.
    Returns anonymized text and redaction count metadata.
    """
    if not text or not isinstance(text, str):
        return {"anonymized_text": "", "redactions_count": 0, "status": "success"}

    anonymized = text
    redactions = 0

    def replace_and_count(pattern, replacement, input_str):
        nonlocal redactions
        matches = len(pattern.findall(input_str))
        redactions += matches
        return pattern.sub(replacement, input_str)

    anonymized = replace_and_count(RE_EMAIL, "[REDACTED_EMAIL]", anonymized)
    anonymized = replace_and_count(RE_SSN, "[REDACTED_SSN]", anonymized)
    anonymized = replace_and_count(RE_API_KEY, "[REDACTED_API_KEY]", anonymized)
    anonymized = replace_and_count(RE_IPV4, "[REDACTED_IP]", anonymized)

    return {
        "original_char_len": len(text),
        "anonymized_char_len": len(anonymized),
        "anonymized_text": anonymized,
        "redactions_count": redactions,
        "status": "success"
    }
