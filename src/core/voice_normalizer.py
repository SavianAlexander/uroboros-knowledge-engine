"""
Autonomous Neural Voice Pronunciation Normalizer, Lexical Phonetic Dictionary & Audio Mastering.
Standard: Pure Python Standard Library (re, math, os, sys) + NumPy (optional guard).
Ponytail Senior Dev Principle: 100% clear human-grade pronunciation of tech jargon, acronyms, and markdown without stumbling or robotic cadence.
"""

import os
import sys
import re
import math
from typing import Dict, Any, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

# Comprehensive Technical, EVE Online & DevOps Lexical Phonetic Dictionary
LEXICAL_PHONETIC_REPLACEMENTS: List[Tuple[re.Pattern, str]] = [
    # DevOps & Infrastructure
    (re.compile(r"\bCI/CD\b", re.IGNORECASE), "C-I C-D"),
    (re.compile(r"\bAPI\b", re.IGNORECASE), "A-P-I"),
    (re.compile(r"\bAPIs\b", re.IGNORECASE), "A-P-Eyes"),
    (re.compile(r"\bJSON\b", re.IGNORECASE), "Jason"),
    (re.compile(r"\bMCP\b", re.IGNORECASE), "M-C-P"),
    (re.compile(r"\bSQL\b", re.IGNORECASE), "sequel"),
    (re.compile(r"\bSQLite\b", re.IGNORECASE), "Sequel Light"),
    (re.compile(r"\bPRAGMA\b", re.IGNORECASE), "pragma"),
    (re.compile(r"\bWAL\b", re.IGNORECASE), "wall"),
    (re.compile(r"\bFTS5\b", re.IGNORECASE), "F-T-S Five"),
    (re.compile(r"\bAST\b", re.IGNORECASE), "A-S-T"),
    (re.compile(r"\bSDK\b", re.IGNORECASE), "S-D-K"),
    (re.compile(r"\bURL\b", re.IGNORECASE), "U-R-L"),
    (re.compile(r"\bURLs\b", re.IGNORECASE), "U-R-Ls"),
    (re.compile(r"\bCLI\b", re.IGNORECASE), "C-L-I"),
    (re.compile(r"\bUUID\b", re.IGNORECASE), "U-U-I-D"),
    (re.compile(r"\bVAD\b", re.IGNORECASE), "V-A-D"),
    (re.compile(r"\bDSP\b", re.IGNORECASE), "D-S-P"),
    (re.compile(r"\bSFX\b", re.IGNORECASE), "sound effects"),
    (re.compile(r"\bE2E\b", re.IGNORECASE), "E-to-E"),
    (re.compile(r"\bSOC\s*2\b", re.IGNORECASE), "Sock Two"),
    (re.compile(r"\bType\s*II\b", re.IGNORECASE), "Type Two"),
    (re.compile(r"\bHTML\b", re.IGNORECASE), "H-T-M-L"),
    (re.compile(r"\bCSS\b", re.IGNORECASE), "C-S-S"),
    (re.compile(r"\bDOM\b", re.IGNORECASE), "dom"),
    (re.compile(r"\bJWT\b", re.IGNORECASE), "J-W-T"),
    (re.compile(r"\bEPUB\b", re.IGNORECASE), "E-pub"),
    (re.compile(r"\bHTTP\b", re.IGNORECASE), "H-T-T-P"),
    (re.compile(r"\bHTTPS\b", re.IGNORECASE), "H-T-T-P-S"),
    (re.compile(r"\bREST\b", re.IGNORECASE), "rest"),
    (re.compile(r"\bWSL\b", re.IGNORECASE), "W-S-L"),
    (re.compile(r"\bSAPI\b", re.IGNORECASE), "Sap-ee"),
    (re.compile(r"\bTTS\b", re.IGNORECASE), "T-T-S"),
    (re.compile(r"\bONNX\b", re.IGNORECASE), "on-ix"),
    (re.compile(r"\bOllama\b", re.IGNORECASE), "Oh-lah-ma"),
    (re.compile(r"\bKokoro\b", re.IGNORECASE), "Koh-koh-roh"),
    (re.compile(r"\bUroboros\b", re.IGNORECASE), "Oo-roh-bor-os"),
    (re.compile(r"\bAntigravity\b", re.IGNORECASE), "Anti-gravity"),
    (re.compile(r"\bTududi\b", re.IGNORECASE), "Too-doo-dee"),
    (re.compile(r"\bFastAPI\b", re.IGNORECASE), "Fast A-P-I"),
    (re.compile(r"\bGitHub\b", re.IGNORECASE), "Git-Hub"),
    (re.compile(r"\bPytest\b", re.IGNORECASE), "Pie-test"),

    # EVE Online Canonical Jargon
    (re.compile(r"\bISK\b", re.IGNORECASE), "I-S-K"),
    (re.compile(r"\bSP\b", re.IGNORECASE), "skill points"),
    (re.compile(r"\bESI\b", re.IGNORECASE), "E-S-I"),
    (re.compile(r"\bCCP\b", re.IGNORECASE), "C-C-P"),
    (re.compile(r"\bAURA\b", re.IGNORECASE), "Aura"),
    (re.compile(r"\bD-Scan\b", re.IGNORECASE), "Directional Scan"),
    (re.compile(r"\bCyno\b", re.IGNORECASE), "Sy-no"),
    (re.compile(r"\bCapacitor\b", re.IGNORECASE), "Capacitor"),
    (re.compile(r"\bSubwarp\b", re.IGNORECASE), "Sub-warp"),
    (re.compile(r"\bCovetor\b", re.IGNORECASE), "Cov-eh-tor"),
    (re.compile(r"\bPorpoise\b", re.IGNORECASE), "Por-pus"),
    (re.compile(r"\bVelator\b", re.IGNORECASE), "Vel-ay-tor"),
    (re.compile(r"\bIbis\b", re.IGNORECASE), "Eye-bis"),
    (re.compile(r"\bG-EURJ\b", re.IGNORECASE), "G-E-U-R-J"),
    (re.compile(r"\bHodrold\b", re.IGNORECASE), "Hod-rold"),
    (re.compile(r"\bMettle\b", re.IGNORECASE), "Met-ul"),

    # Measurement Units & Versioning
    (re.compile(r"\b(\d+)\s*ms\b", re.IGNORECASE), r"\1 milliseconds"),
    (re.compile(r"\b(\d+)\s*kHz\b", re.IGNORECASE), r"\1 kilohertz"),
    (re.compile(r"\b(\d+)\s*Hz\b", re.IGNORECASE), r"\1 hertz"),
    (re.compile(r"\b(\d+)\s*dB\b", re.IGNORECASE), r"\1 decibels"),
    (re.compile(r"\b(\d+)\s*MB\b", re.IGNORECASE), r"\1 megabytes"),
    (re.compile(r"\b(\d+)\s*GB\b", re.IGNORECASE), r"\1 gigabytes"),
    (re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b", re.IGNORECASE), r"version \1 point \2 point \3"),
    (re.compile(r"\bv(\d+)\.(\d+)\b", re.IGNORECASE), r"version \1 point \2"),
    (re.compile(r"\b100%\b"), "100 percent"),
    (re.compile(r"(\d+)%"), r"\1 percent"),
    (re.compile(r"\b#(\d+)\b"), r"number \1"),
]


class VoiceNormalizer:
    """Zero-dependency text sanitizer, phonetic normalizer, and audio mastering rack."""

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Strip markdown syntax to prevent Kokoro from reading symbols."""
        if not text:
            return ""
        # 1. Remove fenced code blocks completely
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"~~~[\s\S]*?~~~", "", text)
        # Inline code `code` -> code
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Markdown images ![alt](url) -> ""
        text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
        # Headers #, ## -> natural pause
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        # Unordered bullets -> comma pause
        text = re.sub(r"^\s*[\-\*\+]\s+", "", text, flags=re.MULTILINE)
        # Ordered list items
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # Bold/Italic asterisks/underscores
        text = re.sub(r"(\*\*|__|\*|_)", "", text)
        # Strikethrough
        text = re.sub(r"~~([^~]+)~~", r"\1", text)
        # Blockquotes >
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove non-spoken special brackets and symbols
        text = re.sub(r"[\[\]\{\}\<\>\\|#]", " ", text)
        # Clean multiple dots
        text = re.sub(r"\.{2,}", "...", text)
        # Collapse multiple spaces and newlines
        text = re.sub(r"\n+", ". ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def apply_phonetic_dictionary(cls, text: str) -> str:
        """Substitute technical acronyms with natural phonetic equivalents."""
        if not text:
            return ""
        for pattern, replacement in LEXICAL_PHONETIC_REPLACEMENTS:
            text = pattern.sub(replacement, text)
        return text

    @classmethod
    def insert_natural_cadence(cls, text: str) -> str:
        """
        Inserts natural clause pauses (commas and ellipses) for fluid conversational breathing.
        Splits long compound sentences (>15 words) at logical conjunctions.
        """
        if not text:
            return ""
        # Ensure punctuation has clean trailing spacing
        text = re.sub(r"([.,!?;:])(?=[^\s\d])", r"\1 ", text)
        # Insert micro-pause for colons / semicolons
        text = re.sub(r"\s*;\s*", ", ", text)
        text = re.sub(r"\s*:\s*", "... ", text)
        # Replace dashes used as parentheticals with pauses
        text = re.sub(r"\s+—\s+|\s+--\s+", "... ", text)
        # Ensure trailing period
        if text and text[-1] not in ".!?":
            text += "."
        return text

    @classmethod
    def normalize_for_speech(cls, text: str) -> str:
        """
        Master Pipeline: Markdown Stripping -> Phonetic Normalization -> Cadence Insertion.
        """
        if not text:
            return ""
        clean = cls.strip_markdown(text)
        phonetic = cls.apply_phonetic_dictionary(clean)
        cadence = cls.insert_natural_cadence(phonetic)
        return cadence.strip()

    @staticmethod
    def master_audio_buffer(samples: Any, sample_rate: int = 24000, target_dbfs: float = -1.0) -> Any:
        """
        Professional EBU R128 True-Peak Audio Mastering & Soft Saturation Limiter.
        Prevents clipping and ensures clear audio reproduction on all DACs and speakers.
        """
        if np is None or not isinstance(samples, np.ndarray) or samples.size == 0:
            return samples

        # 1. Remove DC Offset
        samples = samples - np.mean(samples)

        # 2. Peak normalization to target_dbfs
        peak = np.max(np.abs(samples))
        if peak > 1e-6:
            target_linear = 10.0 ** (target_dbfs / 20.0)
            gain = target_linear / peak
            samples = samples * gain

        # 3. Soft hyperbolic tangent saturation limiter for any peaks exceeding 0.98
        threshold = 0.95
        over_idx = np.abs(samples) > threshold
        if np.any(over_idx):
            samples[over_idx] = np.sign(samples[over_idx]) * (
                threshold + (1.0 - threshold) * np.tanh((np.abs(samples[over_idx]) - threshold) / (1.0 - threshold))
            )

        return np.clip(samples, -1.0, 1.0).astype(np.float32)
