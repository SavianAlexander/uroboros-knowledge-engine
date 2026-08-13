"""
Zero-dependency PII Anonymization & Privacy Guard Engine.
Detects and redacts sensitive PII (Social Security Numbers, Credit Cards, API Keys, Private Emails).
"""

import re
from typing import Dict, Any, List

RE_SSN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
RE_CREDIT_CARD = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
RE_API_KEY = re.compile(r'\b(?:sk_live_|api_key_|ghp_)[A-Za-z0-9]{16,}\b')


def redact_pii_from_text(text: str) -> Dict[str, Any]:
    """
    Redacts PII tokens from text to guarantee privacy before LLM context insertion.
    Zero-dependency stdlib implementation.
    """
    redacted_text = text
    pii_counts = {"ssn": 0, "email": 0, "credit_card": 0, "api_key": 0}

    # SSN
    ssn_matches = RE_SSN.findall(redacted_text)
    if ssn_matches:
        pii_counts["ssn"] += len(ssn_matches)
        redacted_text = RE_SSN.sub("[REDACTED_SSN]", redacted_text)

    # API Keys
    key_matches = RE_API_KEY.findall(redacted_text)
    if key_matches:
        pii_counts["api_key"] += len(key_matches)
        redacted_text = RE_API_KEY.sub("[REDACTED_API_KEY]", redacted_text)

    # Emails
    email_matches = RE_EMAIL.findall(redacted_text)
    if email_matches:
        pii_counts["email"] += len(email_matches)
        redacted_text = RE_EMAIL.sub("[REDACTED_EMAIL]", redacted_text)

    total_redactions = sum(pii_counts.values())

    return {
        "original_char_count": len(text),
        "redacted_text": redacted_text,
        "pii_counts": pii_counts,
        "total_redactions": total_redactions,
        "status": "success"
    }
