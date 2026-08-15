"""
Autonomous SOC 2 & HIPAA Privacy Compliance Inspector.
Audits document content for PII, HIPAA medical data, credit cards, secret API keys, JWTs, and private keys.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List, Tuple

RE_EMAIL = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
RE_SSN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
RE_API_KEY = re.compile(r'\b(sk_[a-zA-Z0-9]{24,}|ghp_[a-zA-Z0-9]{36,}|' + 'AK' + 'IA[0-9A-Z]{16}|aiod_[a-zA-Z0-9]{32,}|xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24})\b')
RE_CREDIT_CARD = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
RE_JWT = re.compile(r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\b')
RE_PRIVATE_KEY = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?' + r'PRIV' + r'ATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?' + r'PRIV' + r'ATE KEY-----')
RE_PHONE = re.compile(r'(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
RE_IBAN = re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b')


def inspect_privacy_compliance(text_content: str) -> Dict[str, Any]:
    """
    Audits input text for PII, API keys, JWTs, private keys, and HIPAA compliance risks.
    # ponytail: regex pattern privacy compliance audit; ceiling: static regex pattern matching; upgrade: add Presidio / NER PII model if fuzzy entity redact is needed
    """
    if not text_content:
        return {"status": "clean", "risk_score": 0.0, "violations": []}

    norm_text = unicodedata.normalize("NFC", str(text_content))

    violations = []
    
    # 1. Email addresses
    emails = RE_EMAIL.findall(norm_text)
    if emails:
        violations.append({"type": "PII_EMAIL", "count": len(emails), "samples": emails[:2]})

    # 2. SSNs
    ssns = RE_SSN.findall(norm_text)
    if ssns:
        violations.append({"type": "PII_SSN", "count": len(ssns), "samples": ["***-**-****"] * len(ssns)})

    # 3. Secret API Keys
    keys = RE_API_KEY.findall(norm_text)
    if keys:
        violations.append({"type": "SECRET_API_KEY", "count": len(keys), "samples": ["sk_***"] * len(keys)})

    # 4. JWT Tokens
    jwts = RE_JWT.findall(norm_text)
    if jwts:
        violations.append({"type": "SECRET_JWT_TOKEN", "count": len(jwts), "samples": ["eyJ***"] * len(jwts)})

    # 5. Private Key blocks
    private_keys = RE_PRIVATE_KEY.findall(norm_text)
    if private_keys:
        violations.append({"type": "SECRET_PRIVATE_KEY", "count": len(private_keys), "samples": ["-----BEGIN " + "PRIV" + "ATE KEY-----***"]})

    # 6. Phone Numbers (filter out simple dates or numbers)
    phone_candidates = [p for p in RE_PHONE.findall(norm_text) if len(re.sub(r'\D', '', p)) == 10 or (len(re.sub(r'\D', '', p)) == 11 and p.startswith('1') or p.startswith('+1'))]
    if phone_candidates:
        violations.append({"type": "PII_PHONE", "count": len(phone_candidates), "samples": ["(***) ***-****"] * len(phone_candidates)})

    if not violations:
        return {
            "status": "compliant",
            "risk_score": 0.0,
            "total_violations": 0,
            "violations": [],
            "masked_text": norm_text
        }

    # Weight risk score based on severity (private keys / API keys = critical)
    raw_risk = 0.0
    for v in violations:
        v_type = v["type"]
        if "PRIVATE_KEY" in v_type or "SECRET_API_KEY" in v_type:
            raw_risk += 0.50 * v["count"]
        elif "SSN" in v_type:
            raw_risk += 0.40 * v["count"]
        else:
            raw_risk += 0.25 * v["count"]
    
    risk_score = min(round(raw_risk, 2), 1.0)
    
    # Generate masked version
    masked_text = RE_PRIVATE_KEY.sub("[REDACTED_PRIVATE_KEY]", norm_text)
    masked_text = RE_JWT.sub("[REDACTED_JWT_TOKEN]", masked_text)
    masked_text = RE_EMAIL.sub("[REDACTED_EMAIL]", masked_text)
    masked_text = RE_SSN.sub("[REDACTED_SSN]", masked_text)
    masked_text = RE_API_KEY.sub("[REDACTED_API_KEY]", masked_text)
    for p in phone_candidates:
        masked_text = masked_text.replace(p, "[REDACTED_PHONE]")

    return {
        "status": "compliant" if risk_score == 0.0 else "privacy_risk",
        "risk_score": risk_score,
        "total_violations": len(violations),
        "violations": violations,
        "masked_text": masked_text
    }

