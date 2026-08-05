"""
Pure domain services: RAG hybrid ranking math, wikilinks parsing, tag rules, term normalization, vector engine, summarization.
Zero dependencies on SQLite connection instances or FastAPI request objects.
"""

import re
import math
from collections import Counter
from functools import lru_cache
from typing import List, Dict, Tuple, Any, Optional

from src.shared.regex import (
    RE_NEAR_SYNTAX,
    RE_TOKEN_SPLIT,
    RE_SIZE_OP,
    RE_FTS_CLEAN,
    RE_WIKILINKS,
)

RE_VECTOR_TOKEN = re.compile(r'\b[a-zA-Z0-9]{2,}\b')
RE_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')

def reciprocal_rank_fusion(fts_results: List[Dict[str, Any]], vector_results: List[Dict[str, Any]], k: int = 60, limit: int = 10) -> List[Dict[str, Any]]:
    """RRF formula score(d) = sum(1 / (k + rank)) across ranking channels."""
    scores: Dict[str, float] = {}
    item_map: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(fts_results, start=1):
        key = item.get("filepath") or item.get("id") or str(item)
        scores[key] = scores.get(key, 0.0) + (1.0 / (k + rank))
        if key not in item_map:
            item_map[key] = dict(item)

    for rank, item in enumerate(vector_results, start=1):
        key = item.get("filepath") or item.get("id") or str(item)
        scores[key] = scores.get(key, 0.0) + (1.0 / (k + rank))
        if key not in item_map:
            item_map[key] = dict(item)

    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    fused_results = []
    for key in sorted_keys[:limit]:
        item = item_map[key]
        item["rrf_score"] = round(scores[key], 6)
        fused_results.append(item)
    return fused_results

def generate_hyde_expansion(query: str) -> str:
    """Generate hypothetical document snippet for vector query expansion."""
    try:
        from main import get_fallback_llm, is_testing
        if is_testing:
            return f"{query} - hypothetical answer context"
        llm = get_fallback_llm()
        if llm:
            prompt = (
                f"Write a concise 2-sentence technical excerpt answering this question: '{query}'. "
                "Do not explain, provide only the factual excerpt."
            )
            completion = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a concise technical excerpt generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.3
            )
            excerpt = completion["choices"][0]["message"]["content"].strip()
            if excerpt:
                return f"{query}\n{excerpt}"
    except Exception:
        pass
    return query

def generate_key_takeaways(text: str, num_bullets: int = 3) -> List[str]:
    """Generate key takeaways from text using sentence scoring."""
    if not text:
        return []
    sentences = RE_SENTENCE_SPLIT.split(text.strip())
    if not sentences:
        return []
    if len(sentences) <= num_bullets:
        return [f"• {s}" for s in sentences if s.strip()]
    
    words = re.findall(r"\b[a-z]{4,15}\b", text.lower())
    word_freq = Counter(words)
    scored_sentences = []
    for idx, s in enumerate(sentences):
        s_words = re.findall(r"\b[a-z]{4,15}\b", s.lower())
        score = sum(word_freq.get(w, 0) for w in s_words) / (len(s_words) or 1)
        scored_sentences.append((score, idx, s.strip()))
    
    top = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:num_bullets]
    top_sorted = sorted(top, key=lambda x: x[1])
    return [f"• {s[2]}" for s in top_sorted if s[2]]

RE_REDOS_NESTED_QUANTIFIERS = re.compile(r'(\+|\*|\{[\d,]+\})\s*\)')

def _safe_match(pat: str, text: str) -> bool:
    if not pat or not text:
        return False
    if "(" in pat and RE_REDOS_NESTED_QUANTIFIERS.search(pat):
        return pat.lower() in text.lower()
    try:
        return bool(re.search(pat, text, re.IGNORECASE))
    except re.error:
        import fnmatch
        try:
            regex_pat = fnmatch.translate(pat)
            return bool(re.search(regex_pat, text, re.IGNORECASE))
        except Exception:
            return pat.lower() in text.lower()

def extract_ai_tags(content: str, filename: str, rule_matches: Optional[List[Tuple[str, str]]] = None) -> List[str]:
    """Extract AI/rule tags from document filename and content."""
    tags: List[str] = []
    if rule_matches:
        for pat, t_tag in rule_matches:
            if _safe_match(pat, filename) or _safe_match(pat, content):
                if t_tag not in tags:
                    tags.append(t_tag)

    fallback_rules = [
        ("astrophysics", "science"),
        ("physics", "science"),
        ("quantum", "science")
    ]
    for pat, tag in fallback_rules:
        if _safe_match(pat, filename) or _safe_match(pat, content):
            if tag not in tags:
                tags.append(tag)

    try:
        from main import is_testing, get_fallback_llm
        if is_testing:
            return tags
        llm = get_fallback_llm()
        if llm:
            prompt = (
                "Analyze the following document filename and text content.\n"
                "Extract exactly 2-3 concise keyword tags that best represent the topic or domain.\n"
                "Respond ONLY with a comma-separated list of lowercase tags. Do not explain anything.\n\n"
                f"Filename: {filename}\n"
                f"Content: {content[:800]}"
            )
            completion = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a database tag extractor. Respond only with comma-separated tags."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=0.2
            )
            tags_str = completion["choices"][0]["message"]["content"]
            ai_tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
            for t in ai_tags:
                if t not in tags:
                    tags.append(t)
    except Exception:
        pass
    return tags

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split text into chunks of specified size and overlap with 10MB memory safety ceiling."""
    if not text or not text.strip():
        return []
    if len(text) > 10_000_000:
        text = text[:10_000_000]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def parse_query_operators(q_str: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """Parse search operators (e.g. tag:foo, size:>1mb, -word, NEAR(...))."""
    if not q_str:
        return "", {}, {}

    operators: Dict[str, Any] = {}
    exclusions: Dict[str, Any] = {}
    cleaned_q = []

    near_exprs = re.findall(r'NEAR\([^)]+\)', q_str, re.IGNORECASE)
    for ne in near_exprs:
        cleaned_q.append(ne)
        q_str = q_str.replace(ne, "")

    tokens = q_str.split()
    for token in tokens:
        is_exclude = False
        t_val = token

        if t_val.startswith("-") and len(t_val) > 1:
            is_exclude = True
            t_val = t_val[1:]

        if ":" in t_val:
            key, val = t_val.split(":", 1)
            val = val.strip('"').strip("'")
            if is_exclude:
                exclusions[key.lower()] = val
            else:
                operators[key.lower()] = val
        elif ">" in t_val or "<" in t_val:
            match = RE_SIZE_OP.match(t_val)
            if match:
                op, num, unit = match.groups()
                bytes_val = int(num)
                if unit:
                    unit = unit.lower()
                    if unit == "kb":
                        bytes_val *= 1024
                    elif unit == "mb":
                        bytes_val *= 1024 * 1024
                if is_exclude:
                    exclusions["size"] = (op, bytes_val)
                else:
                    operators["size"] = (op, bytes_val)
            else:
                if is_exclude:
                    exclusions["word"] = exclusions.get("word", []) + [t_val]
                else:
                    cleaned_q.append(t_val)
        else:
            if is_exclude:
                exclusions["word"] = exclusions.get("word", []) + [t_val]
            else:
                cleaned_q.append(t_val)

    return " ".join(cleaned_q).strip(), operators, exclusions

@lru_cache(maxsize=1024)
def suggest_tags_from_text(text: str) -> List[str]:
    """Suggest top tags based on word frequency in text."""
    if not text:
        return []
    stopwords = {
        "the", "and", "of", "to", "is", "in", "that", "it", "for", "on", "with", "as",
        "this", "was", "at", "by", "an", "be", "are", "from", "or", "your", "have",
        "had", "has", "but", "not", "what", "all", "were", "when", "we"
    }
    words = re.findall(r"\b[a-z]{3,15}\b", text.lower())
    freq: Dict[str, int] = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:4]]

@lru_cache(maxsize=1024)
def generate_summary(text: str) -> str:
    """Generate extractive summary using TF-IDF sentence scoring."""
    if not text or len(text.strip()) < 100:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= 3:
        return text.strip()

    words = re.findall(r"\b[a-z]{4,15}\b", text.lower())
    word_freq = Counter(words)

    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        s_words = re.findall(r"\b[a-z]{4,15}\b", sentence.lower())
        for word in s_words:
            score += word_freq.get(word, 0)
        length = len(s_words)
        if length > 0:
            score = score / length
        sentence_scores.append((score, i, sentence))

    top_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:3]
    top_sentences = sorted(top_sentences, key=lambda x: x[1])
    return " ".join([s[2] for s in top_sentences]).strip()

_RE_CLEAN_FTS = re.compile(r'[\x00-\x1F\x7F<>]')
_RE_KEYWORD_OPERATORS = re.compile(r'\s*(\b(OR|NOT|AND)\b|NEAR\([^)]*\))\s*', re.IGNORECASE)

@lru_cache(maxsize=1024)
def sanitise_fts_query(query: str) -> str:
    """Sanitize search query for FTS5 syntax safety, HTML injection, and control characters."""
    if not query:
        return ""
    import unicodedata
    query = unicodedata.normalize("NFC", query)
    # Strip standalone or leading asterisks to prevent SQLite FTS5 unknown special query errors
    query = re.sub(r'(^|\s)\*+', ' ', query)
    # Strip dangerous FTS syntax symbols like /, =, <, >, ;, --, (, )
    cleaned = re.sub(r'[/<>=;~\\()|]|--', ' ', query)
    cleaned = _RE_CLEAN_FTS.sub('', cleaned)
    if '"' in cleaned:
        cleaned = cleaned.replace('"', ' ')
    cleaned = _RE_KEYWORD_OPERATORS.sub(' ', cleaned)
    words = [w for w in re.findall(r'\b[\w\-\*]+\b', cleaned) if w.lower() not in ('and', 'or', 'not', 'near')]
    if not words:
        return ""
    return " ".join(words)

@lru_cache(maxsize=1024)
def sanitize_tag(tag: str) -> str:
    """Sanitize and normalize tag string for query and storage."""
    if not tag:
        return ""
    return re.sub(r'[\s,#]+', '_', tag.strip().lower())

@lru_cache(maxsize=1024)
def lookup_tag_color(tag: str) -> str:
    """Read-only default tag color lookup by tag name hash."""
    if not tag:
        return "#3b82f6"
    colors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#6366f1"]
    idx = sum(ord(c) for c in tag.lower().strip()) % len(colors)
    return colors[idx]

@lru_cache(maxsize=1024)
def lookup_document_metadata_category(mime_type: str, ext: str) -> str:
    """Read-only pure document metadata lookup for mime and extension category."""
    mime = (mime_type or "").lower()
    extension = (ext or "").lstrip(".").lower()
    if mime.startswith("image/") or extension in ("png", "jpg", "jpeg", "gif", "svg", "webp"):
        return "image"
    if mime.startswith("audio/") or extension in ("wav", "mp3", "flac", "ogg", "m4a"):
        return "audio"
    if mime == "application/pdf" or extension == "pdf":
        return "pdf"
    if extension in ("doc", "docx", "rtf", "txt", "md"):
        return "document"
    if extension in ("xls", "xlsx", "csv"):
        return "spreadsheet"
    return "other"

def chunk_text_hierarchical(text: str, parent_size: int = 600, child_size: int = 150) -> List[Dict[str, Any]]:
    """
    Hierarchical Parent-Child Chunking.
    Splits text into larger Parent Sections (parent_size) and granular Child Snippets (child_size).
    Each child chunk holds a reference to its enclosing parent context block.
    """
    if not text or not text.strip():
        return []

    clean_text = text.strip()
    # Split into paragraphs or major sections
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', clean_text) if p.strip()]
    if not paragraphs:
        paragraphs = [clean_text]

    parent_blocks = []
    current_parent = []
    current_len = 0

    for p in paragraphs:
        if current_len + len(p) <= parent_size or not current_parent:
            current_parent.append(p)
            current_len += len(p)
        else:
            parent_blocks.append("\n\n".join(current_parent))
            current_parent = [p]
            current_len = len(p)
    if current_parent:
        parent_blocks.append("\n\n".join(current_parent))

    hierarchical_chunks = []
    child_idx = 0

    for parent_idx, parent_text in enumerate(parent_blocks):
        # Generate child chunks within this parent block
        sentences = [s.strip() for s in RE_SENTENCE_SPLIT.split(parent_text) if s.strip()]
        if not sentences:
            sentences = [parent_text]

        curr_child_sentences = []
        curr_child_len = 0

        for s in sentences:
            if curr_child_len + len(s) <= child_size or not curr_child_sentences:
                curr_child_sentences.append(s)
                curr_child_len += len(s)
            else:
                child_text = " ".join(curr_child_sentences)
                hierarchical_chunks.append({
                    "child_index": child_idx,
                    "parent_index": parent_idx,
                    "child_content": child_text,
                    "parent_content": parent_text,
                    "child_char_len": len(child_text),
                    "parent_char_len": len(parent_text)
                })
                child_idx += 1
                curr_child_sentences = [s]
                curr_child_len = len(s)

        if curr_child_sentences:
            child_text = " ".join(curr_child_sentences)
            hierarchical_chunks.append({
                "child_index": child_idx,
                "parent_index": parent_idx,
                "child_content": child_text,
                "parent_content": parent_text,
                "child_char_len": len(child_text),
                "parent_char_len": len(parent_text)
            })
            child_idx += 1

    return hierarchical_chunks

_SYNONYM_DICT = {
    "auth": "authentication",
    "authentication": "auth",
    "db": "database",
    "database": "db",
    "cfg": "configuration",
    "config": "configuration",
    "configuration": "config",
    "err": "error",
    "errors": "error",
    "req": "request",
    "requests": "request",
    "doc": "document",
    "docs": "document",
    "documents": "document",
    "func": "function",
    "functions": "function",
    "repo": "repository",
    "repositories": "repository",
}

@lru_cache(maxsize=2048)
def stem_word(word: str) -> str:
    """
    Lightweight rule-based Porter stemmer for English suffix reduction.
    Reduces plurals and common verbal suffixes without external dependencies.
    """
    if not word or len(word) <= 3:
        return word.lower()
    w = word.lower()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 3 and not w.endswith("ses") and not w.endswith("zes"):
        return w[:-1] if (w.endswith("les") or w.endswith("res") or w.endswith("des") or w.endswith("ves")) else w[:-2]
    if w.endswith("ing") and len(w) > 5:
        return w[:-3]
    if w.endswith("ed") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w

def expand_synonyms(query: str) -> str:
    """
    Expands query with technical domain synonyms and acronym equivalents.
    """
    if not query:
        return ""
    words = re.findall(r'\b[a-zA-Z0-9_\-]+\b', query)
    expanded = list(words)
    for w in words:
        low = w.lower()
        syn = _SYNONYM_DICT.get(low)
        if syn and syn not in expanded:
            expanded.append(syn)
    return " ".join(expanded)



