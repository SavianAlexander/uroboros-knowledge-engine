import re
from typing import Dict, Any

_RE_EXT = re.compile(r'\b(pdf|docx|md|txt|png|jpg|mp3|csv|json)\b', re.IGNORECASE)
_RE_TAG = re.compile(r'\btagged\s+([a-zA-Z0-9_-]+)', re.IGNORECASE)
_RE_SIZE = re.compile(r'\bsize\s*(>|<|=)\s*(\d+)\s*(mb|kb|b)?\b', re.IGNORECASE)

def parse_natural_language_filter(query: str) -> Dict[str, Any]:
    """
    Parses natural language query strings into structured SQLite search parameters and filters.
    Example: "pdf files tagged architecture size > 1mb" ->
    {'fts_term': 'files', 'filters': {'ext': 'pdf', 'tag': 'architecture', 'size_op': '>', 'size_bytes': 1048576}}
    """
    if not query or not str(query).strip():
        return {"fts_term": "", "filters": {}}

    raw = str(query).strip()
    filters: Dict[str, Any] = {}

    # Extract extension
    ext_match = _RE_EXT.search(raw)
    if ext_match:
        filters["ext"] = ext_match.group(1).lower()

    # Extract tag
    tag_match = _RE_TAG.search(raw)
    if tag_match:
        filters["tag"] = tag_match.group(1).lower()

    # Extract size constraint
    size_match = _RE_SIZE.search(raw)
    if size_match:
        try:
            op, val, unit = size_match.groups()
            val_int = int(val)
            unit_str = (unit or "b").lower()
            multiplier = 1048576 if unit_str == "mb" else (1024 if unit_str == "kb" else 1)
            filters["size_op"] = op
            filters["size_bytes"] = val_int * multiplier
        except (ValueError, OverflowError, TypeError):
            pass

    # Clean FTS keywords
    cleaned_fts = _RE_TAG.sub('', raw)
    cleaned_fts = _RE_SIZE.sub('', cleaned_fts)
    cleaned_fts = re.sub(r'\b(files|documents|notes|from|last|week|month)\b', '', cleaned_fts, flags=re.IGNORECASE).strip()

    return {
        "fts_term": cleaned_fts or raw,
        "filters": filters
    }
