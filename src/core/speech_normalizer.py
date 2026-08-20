"""
Intelligent Neural Speech Normalizer & Lexical Phonetic Engine.
Re-exports canonical implementation from src.core.voice_normalizer.
Standard: Pure Python Standard Library (re, os, sys, math, unicodedata).
Ponytail Senior Dev Principle: Single source of truth for phonetic normalization.
"""

from src.core.voice_normalizer import (
    VoiceNormalizer as SpeechNormalizer,
    number_to_words,
    normalize_speech_text,
    LEXICAL_PHONETIC_REPLACEMENTS,
    LEXICAL_PHONETIC_REPLACEMENTS as PHONETIC_ACRONYM_RULES,
)

__all__ = [
    "SpeechNormalizer",
    "number_to_words",
    "normalize_speech_text",
    "PHONETIC_ACRONYM_RULES",
    "LEXICAL_PHONETIC_REPLACEMENTS",
]

