"""
Zero-dependency extractive document summarization & TF-IDF sentence ranking engine.
"""

import re
from collections import Counter
from typing import Dict, Any, List

RE_SENTENCE = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')
RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he",
    "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}


def summarize_text(text: str, max_sentences: int = 3) -> Dict[str, Any]:
    """
    Ranks sentences by TF-IDF keyword density to generate a high-density extractive summary.
    Zero-dependency stdlib implementation.
    """
    if not text or not isinstance(text, (str, bytes)):
        return {
            "summary": "",
            "key_sentences": [],
            "total_sentences": 0,
            "compression_ratio": 0.0,
            "status": "empty"
        }

    import unicodedata
    raw_str = text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else str(text)
    str_text = unicodedata.normalize("NFC", raw_str)
    if not str_text.strip():
        return {
            "summary": "",
            "key_sentences": [],
            "total_sentences": 0,
            "compression_ratio": 0.0,
            "status": "empty"
        }

    # Split into sentences
    raw_sentences = RE_SENTENCE.split(str_text.strip())
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 15]

    if not sentences:
        return {
            "summary": str_text[:200],
            "key_sentences": [str_text[:200]],
            "total_sentences": 1,
            "compression_ratio": 1.0,
            "status": "success"
        }

    # Calculate word frequency scores across document
    all_words = RE_WORD.findall(str_text.lower())
    content_words = [w for w in all_words if w not in STOP_WORDS]
    word_counts = Counter(content_words)

    # Rank sentences based on accumulated word frequency weights
    sentence_scores = []
    for idx, sentence in enumerate(sentences):
        words = RE_WORD.findall(sentence.lower())
        if not words:
            continue
        score = sum(word_counts[w] for w in words if w not in STOP_WORDS) / float(len(words))
        sentence_scores.append((score, idx, sentence))

    # Pick top N sentences maintaining original narrative order
    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    safe_max = max(1, int(max_sentences)) if max_sentences is not None and isinstance(max_sentences, (int, float)) else 3
    top_ranked = sentence_scores[:safe_max]
    top_ranked.sort(key=lambda x: x[1])  # Re-sort by original index

    extracted_sentences = [s[2] for s in top_ranked]
    summary = " ".join(extracted_sentences)
    ratio = round(len(summary) / float(max(1, len(str_text))), 4)

    return {
        "summary": summary,
        "key_sentences": extracted_sentences,
        "total_sentences": len(sentences),
        "extracted_sentences_count": len(extracted_sentences),
        "compression_ratio": ratio,
        "status": "success"
    }
