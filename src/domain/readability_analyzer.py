"""
Zero-dependency readability metrics & sentiment polarity analyzer engine.
Uses Flesch Reading Ease & Flesch-Kincaid Grade Level formulas.
"""

import functools
import re
from typing import Dict, Any

RE_SENTENCE = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')
RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]+\b')

POSITIVE_WORDS = {
    "good", "great", "excellent", "positive", "fortunate", "correct", "superior", "best",
    "awesome", "advantage", "growth", "effective", "valuable", "success", "innovative",
    "profit", "benefit", "efficient", "optimal", "clean", "robust", "pass", "passed"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "poor", "negative", "unfortunate", "wrong", "inferior", "worst",
    "awful", "disadvantage", "decline", "ineffective", "useless", "failure", "flaw",
    "loss", "risk", "bug", "error", "defect", "vulnerability", "fail", "failed"
}


@functools.lru_cache(maxsize=4096)
def count_syllables_in_word(word: str) -> int:
    """Estimates syllable count for an English word using stdlib regex rules."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]+', word))
    return max(1, syllables)


def analyze_readability(text: str) -> Dict[str, Any]:
    """
    Calculates Flesch Reading Ease, Flesch-Kincaid Grade Level, and Sentiment Polarity.
    Zero-dependency stdlib implementation.
    """
    if not text or not isinstance(text, (str, bytes)):
        return {
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade": 0.0,
            "reading_level": "Very Easy",
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "total_words": 0,
            "total_sentences": 0,
            "total_syllables": 0,
            "status": "empty"
        }

    import unicodedata
    raw_text = text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else str(text)
    str_text = unicodedata.normalize("NFC", raw_text)
    if not str_text.strip():
        return {
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade": 0.0,
            "reading_level": "Very Easy",
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "total_words": 0,
            "total_sentences": 0,
            "total_syllables": 0,
            "status": "empty"
        }

    sentences = [s.strip() for s in RE_SENTENCE.split(str_text.strip()) if s.strip()]
    words = RE_WORD.findall(str_text)
    if not words:
        return {
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade": 0.0,
            "reading_level": "Very Easy",
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "total_words": 0,
            "total_sentences": len(sentences),
            "total_syllables": 0,
            "status": "empty"
        }

    total_sentences = max(1, len(sentences))
    total_words = max(1, len(words))
    total_syllables = sum(count_syllables_in_word(w) for w in words)

    # Flesch Reading Ease: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    fre = 206.835 - 1.015 * (total_words / float(total_sentences)) - 84.6 * (total_syllables / float(total_words))
    fre = round(max(0.0, min(100.0, fre)), 2)

    # Flesch-Kincaid Grade Level: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    fkgl = 0.39 * (total_words / float(total_sentences)) + 11.8 * (total_syllables / float(total_words)) - 15.59
    fkgl = round(max(0.0, fkgl), 2)

    if fre >= 90:
        level = "Very Easy (5th Grade)"
    elif fre >= 70:
        level = "Fairly Easy (7th Grade)"
    elif fre >= 60:
        level = "Standard (8th-9th Grade)"
    elif fre >= 50:
        level = "Fairly Difficult (10th-12th Grade)"
    elif fre >= 30:
        level = "Difficult (College)"
    else:
        level = "Very Difficult (Graduate)"

    # Basic Sentiment Lexicon Analysis
    word_set = [w.lower() for w in words]
    pos_count = sum(1 for w in word_set if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in word_set if w in NEGATIVE_WORDS)
    
    total_sentiment_words = pos_count + neg_count
    if total_sentiment_words > 0:
        polarity = round((pos_count - neg_count) / float(total_sentiment_words), 2)
    else:
        polarity = 0.0

    if polarity > 0.1:
        sentiment_label = "Positive"
    elif polarity < -0.1:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    return {
        "flesch_reading_ease": fre,
        "flesch_kincaid_grade": fkgl,
        "reading_level": level,
        "sentiment_score": polarity,
        "sentiment_label": sentiment_label,
        "total_words": len(words),
        "total_sentences": len(sentences),
        "total_syllables": total_syllables,
        "avg_words_per_sentence": round(len(words) / float(total_sentences), 2),
        "avg_syllables_per_word": round(total_syllables / float(total_words), 2),
        "status": "success"
    }
