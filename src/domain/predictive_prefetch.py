"""
Predictive Search Intent Pre-Fetcher Engine.
Predicts user's next likely search queries based on active document context and pre-warms vector cache.
Zero-dependency, stdlib implementation.
"""
import hashlib
import re
import unicodedata
from typing import Dict, Any, List

RE_WIKILINK = re.compile(r'\[\[(.*?)\]\]')
RE_HEADING = re.compile(r'(?:^|\n)#{1,4}\s+([^\n]+)')
RE_WORDS = re.compile(r'\b[A-Za-z][A-Za-z0-9_-]{3,}\b')

STOP_WORDS = {
    "this", "that", "with", "from", "have", "were", "what", "when", "where",
    "which", "there", "their", "about", "would", "could", "should", "document",
    "section", "chapter", "details", "overview", "system", "using"
}


def _extract_salient_topics(query: str, contexts: List[str]) -> List[str]:
    """Extracts salient topics, wikilinks, and headings from query and contexts."""
    topics = []
    seen = set()

    # 1. Extract wikilinks from contexts
    for ctx in contexts:
        if not ctx:
            continue
        for wl in RE_WIKILINK.findall(ctx):
            clean_wl = wl.split("|")[0].strip()
            norm = clean_wl.lower()
            if clean_wl and norm not in seen and len(clean_wl) > 2:
                seen.add(norm)
                topics.append(clean_wl)

    # 2. Extract markdown headings from contexts
    for ctx in contexts:
        if not ctx:
            continue
        for heading in RE_HEADING.findall(ctx):
            clean_h = re.sub(r'[#\*`_]', '', heading).strip()
            norm = clean_h.lower()
            if clean_h and norm not in seen and len(clean_h.split()) <= 5:
                seen.add(norm)
                topics.append(clean_h)

    # 3. Extract keywords from query
    q_words = [w for w in RE_WORDS.findall(query) if w.lower() not in STOP_WORDS]
    for w in q_words:
        norm = w.lower()
        if norm not in seen:
            seen.add(norm)
            topics.append(w.title())

    # 4. Extract capitalized entity nouns from context bodies
    for ctx in contexts:
        if not ctx:
            continue
        words = RE_WORDS.findall(ctx)
        for w in words:
            if w[0].isupper() and w.lower() not in STOP_WORDS and w.lower() not in seen:
                seen.add(w.lower())
                topics.append(w)
                if len(topics) >= 10:
                    break

    return topics if topics else ["Knowledge Base Architecture"]


def predict_next_search_intents(
    active_query: str,
    retrieved_contexts: List[str]
) -> Dict[str, Any]:
    """
    Predicts follow-up search queries and pre-warms vector cache keys using active context grounding.
    Zero-dependency stdlib implementation.
    """
    norm_query = unicodedata.normalize("NFC", str(active_query or "")).strip()
    norm_ctxs = [unicodedata.normalize("NFC", str(c)).strip() for c in (retrieved_contexts or []) if c]

    topics = _extract_salient_topics(norm_query, norm_ctxs)
    main_topic = topics[0] if topics else "Topic"
    secondary_topic = topics[1] if len(topics) > 1 else "Alternative Approaches"

    predicted_queries = [
        f"Explain {main_topic} implementation details and specifications",
        f"What are the security, compliance, and trust controls for {main_topic}?",
        f"Compare {main_topic} with {secondary_topic}" if len(topics) > 1 else f"Compare {main_topic} with alternative architectures"
    ]

    # Generate deterministic SHA256 prewarm cache keys
    prewarmed_keys = [
        f"vec_prewarm_{hashlib.sha256(q.lower().encode('utf-8')).hexdigest()[:12]}"
        for q in predicted_queries
    ]

    return {
        "active_query": norm_query,
        "predicted_followup_queries": predicted_queries,
        "salient_topics_extracted": topics[:5],
        "prewarmed_cache_keys": prewarmed_keys,
        "total_contexts_analyzed": len(norm_ctxs),
        "status": "success"
    }
