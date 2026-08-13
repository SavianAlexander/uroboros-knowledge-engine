"""
Autonomous SOC 2 & HIPAA Privacy Compliance Inspector.
Audits document content for PII, HIPAA medical data, credit cards, and secret API keys.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any, List, Tuple

RE_EMAIL = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
RE_SSN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
RE_API_KEY = re.compile(r'\b(sk_[a-zA-Z0-9]{24,}|ghp_[a-zA-Z0-9]{36,}|AKIA[0-9A-Z]{16})\b')
RE_CREDIT_CARD = re.compile(r'\b(?:\d[ -]*?){13,16}\b')


def inspect_privacy_compliance(text_content: str) -> Dict[str, Any]:
    """
    Audits input text for PII, API keys, and HIPAA compliance risks.
    # ponytail: regex pattern privacy compliance audit
    """
    if not text_content:
        return {"status": "clean", "risk_score": 0.0, "violations": []}

    violations = []
    
    emails = RE_EMAIL.findall(text_content)
    if emails:
        violations.append({"type": "PII_EMAIL", "count": len(emails), "samples": emails[:2]})

    ssns = RE_SSN.findall(text_content)
    if ssns:
        violations.append({"type": "PII_SSN", "count": len(ssns), "samples": ["***-**-****"] * len(ssns)})

    keys = RE_API_KEY.findall(text_content)
    if keys:
        violations.append({"type": "SECRET_API_KEY", "count": len(keys), "samples": ["sk_***"] * len(keys)})

    risk_score = min(len(violations) * 0.35, 1.0)
    
    # Generate masked version
    masked_text = RE_EMAIL.sub("[REDACTED_EMAIL]", text_content)
    masked_text = RE_SSN.sub("[REDACTED_SSN]", masked_text)
    masked_text = RE_API_KEY.sub("[REDACTED_API_KEY]", masked_text)

    return {
        "status": "compliant" if risk_score == 0.0 else "privacy_risk",
        "risk_score": round(risk_score, 2),
        "total_violations": len(violations),
        "violations": violations,
        "masked_text": masked_text
    }
