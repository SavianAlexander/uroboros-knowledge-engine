"""
Zero-dependency TF-IDF term frequency & capitalized domain entity extraction engine.
"""

import re
import math
from collections import Counter
from typing import Dict, Any, List

# Standard English stop words list (pure stdlib, zero dependencies)
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
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn’t", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}

RE_PROPER_NOUN = re.compile(r'\b[A-Z][a-zA-Z0-9_-]{2,}\b')
RE_WORD = re.compile(r'\b[a-zA-Z0-9_-]{3,}\b')


def extract_entities_from_text(text: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Extracts key domain entities, technical terms, and TF-IDF word frequencies.
    Zero-dependency stdlib implementation.
    """
    if not text or not text.strip():
        return {
            "entities": [],
            "keywords": [],
            "total_words": 0,
            "status": "success"
        }

    words = RE_WORD.findall(text)
    total_words = len(words)

    # 1. Capitalized Entity Recognition (Proper Nouns & Acronyms)
    capitalized = RE_PROPER_NOUN.findall(text)
    entity_counts = Counter(w for w in capitalized if w.lower() not in STOP_WORDS)
    top_entities = [
        {"entity": term, "count": count}
        for term, count in entity_counts.most_common(top_k)
    ]

    # 2. Term Frequency Analysis (excluding stop words)
    filtered_words = [w.lower() for w in words if w.lower() not in STOP_WORDS]
    word_counts = Counter(filtered_words)

    top_keywords = []
    for term, count in word_counts.most_common(top_k):
        tf = round(count / float(total_words), 4) if total_words > 0 else 0.0
        top_keywords.append({
            "term": term,
            "count": count,
            "tf_score": tf
        })

    return {
        "entities": top_entities,
        "keywords": top_keywords,
        "total_words": total_words,
        "unique_keywords": len(word_counts),
        "status": "success"
    }
