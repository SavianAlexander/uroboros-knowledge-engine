"""
Adversarial Prompt Injection & Indirect Jailbreak Guard Engine.
Scans text input for indirect prompt injection, jailbreaks, and system override patterns.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List

INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?(previous\s+)?instructions', re.IGNORECASE),
    re.compile(r'system\s+override', re.IGNORECASE),
    re.compile(r'dan\s+mode', re.IGNORECASE),
    re.compile(r'developer\s+mode\s+enabled', re.IGNORECASE),
    re.compile(r'reveal\s+(system\s+)?prompt', re.IGNORECASE),
    re.compile(r'bypass\s+safety\s+filter', re.IGNORECASE),
    re.compile(r'disregard\s+(all\s+)?rules', re.IGNORECASE),
    re.compile(r'jailbreak\s+enabled', re.IGNORECASE)
]


def scan_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Scans text for adversarial prompt injection patterns.
    Returns safety status and flagged injection triggers.
    """
    if not text or not isinstance(text, str):
        return {"is_safe": True, "injection_triggers": [], "sanitized_text": "", "status": "success"}

    flagged_triggers = []
    sanitized = unicodedata.normalize("NFC", str(text))

    for pattern in INJECTION_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            flagged_triggers.append(pattern.pattern)
            sanitized = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", sanitized)

    is_safe = len(flagged_triggers) == 0

    return {
        "is_safe": is_safe,
        "injection_triggers": flagged_triggers,
        "sanitized_text": sanitized,
        "threat_level": "high" if not is_safe else "none",
        "status": "success"
    }

# Epistemic 4-Pillar and backward-compatible aliases
evaluate_prompt_safety = scan_prompt_injection

class PromptInjectionGuard:
    scan = staticmethod(scan_prompt_injection)
    evaluate_safety = staticmethod(scan_prompt_injection)

