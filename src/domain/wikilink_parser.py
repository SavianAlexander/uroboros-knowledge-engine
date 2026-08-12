"""
Wikilink Content Parser Domain Module.
Provides zero-dependency parsing of markdown wikilink syntax:
  [[target]], [[target|label]], [[target#anchor]], [[target#anchor|label]]
"""

import re
from functools import lru_cache
from dataclasses import dataclass
from typing import Optional, List


@dataclass(slots=True)
class WikilinkMatch:
    """Dataclass representing a parsed wikilink."""
    raw_text: str
    target_title: str
    anchor: Optional[str] = None
    alias: Optional[str] = None
    slug: str = ""


# Regex matching double square bracket wikilink expressions: [[...]]
RE_WIKILINK_BRACKETS = re.compile(r'\[\[([^\]]+)\]\]')
RE_NON_WORD = re.compile(r'[^\w\s\-]', re.UNICODE)
RE_SLUG_SEP = re.compile(r'[\s\-_]+', re.UNICODE)

ASCII_SLUG_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_-")


@lru_cache(maxsize=4096)
def normalize_target_title(title: str) -> str:
    """
    Normalizes target document title by trimming whitespace and
    stripping trailing .md or .txt extensions.
    """
    if not title:
        return ""
    
    cleaned = title.strip() if (title[0] <= ' ' or title[-1] <= ' ') else title
    if not cleaned:
        return ""

    if '.' in cleaned:
        low = cleaned.lower()
        if low.endswith(".md"):
            cleaned = cleaned[:-3]
            if cleaned and (cleaned[0] <= ' ' or cleaned[-1] <= ' '):
                cleaned = cleaned.strip()
        elif low.endswith(".txt"):
            cleaned = cleaned[:-4]
            if cleaned and (cleaned[0] <= ' ' or cleaned[-1] <= ' '):
                cleaned = cleaned.strip()
    
    return cleaned


@lru_cache(maxsize=4096)
def slugify_title(title: str) -> str:
    """
    Converts a title into a normalized URL/filename slug.
    Example: "My Document.md" -> "my_document"
    """
    if not title:
        return ""
    normalized = normalize_target_title(title) if ("." in title or title[0] <= ' ' or title[-1] <= ' ') else title
    if not normalized:
        return ""
    
    # Ultra-fast path for standard ASCII titles
    if normalized.isascii():
        if normalized.islower() and set(normalized) <= ASCII_SLUG_CHARS:
            return normalized if (normalized[0] != '_' and normalized[-1] != '_') else normalized.strip('_')
        if normalized.isalnum():
            return normalized.lower()
        s = normalized.replace(' ', '_').replace('-', '_')
        if s.replace('_', '').isalnum():
            s = s.strip('_')
            return s if s.islower() else s.lower()

    # Fallback for complex non-ASCII or punctuation titles
    cleaned = RE_NON_WORD.sub('', normalized)
    slug = RE_SLUG_SEP.sub('_', cleaned).strip('_').lower()
    return slug




@lru_cache(maxsize=8192)
def parse_wikilinks(content: str) -> List[WikilinkMatch]:
    """
    Parses content for all wikilinks in syntax:
    - [[target]]
    - [[target|label]]
    - [[target#anchor]]
    - [[target#anchor|label]]
    
    Returns a list of WikilinkMatch objects.
    """
    if not content or '[[' not in content:
        return []
    
    matches: List[WikilinkMatch] = []
    
    for match in RE_WIKILINK_BRACKETS.finditer(content):
        raw_text = match.group(0)
        inner = match.group(1)
        if inner[0] <= ' ' or inner[-1] <= ' ':
            inner = inner.strip()
        if not inner:
            continue
        
        # Fast-path simple target without alias or anchor
        if '|' not in inner and '#' not in inner:
            raw_title = inner
            alias = None
            anchor = None
        else:
            # Split on '|' to separate target/anchor from alias
            if '|' in inner:
                target_part, alias_part = inner.split('|', 1)
                alias = (alias_part.strip() if (alias_part and (alias_part[0] <= ' ' or alias_part[-1] <= ' ')) else alias_part) or None
            else:
                target_part = inner
                alias = None
            
            # Split target_part on '#' to separate target document title from anchor
            if '#' in target_part:
                raw_title, anchor_part = target_part.split('#', 1)
                anchor = (anchor_part.strip() if (anchor_part and (anchor_part[0] <= ' ' or anchor_part[-1] <= ' ')) else anchor_part) or None
            else:
                raw_title = target_part
                anchor = None
        
        target_title = normalize_target_title(raw_title)
        if not target_title:
            continue
        
        slug = slugify_title(target_title)
        
        matches.append(
            WikilinkMatch(
                raw_text=raw_text,
                target_title=target_title,
                anchor=anchor,
                alias=alias,
                slug=slug
            )
        )
    
    return matches


def extract_target_titles(content: str) -> List[str]:
    """
    Extracts a list of unique normalized target titles from content.
    Preserves original order of appearance.
    """
    if not content or '[[' not in content:
        return []
    parsed = parse_wikilinks(content)
    seen = set()
    titles = []
    for match in parsed:
        if match.target_title not in seen:
            seen.add(match.target_title)
            titles.append(match.target_title)
    return titles

RE_IMPLICIT_ENTITY = re.compile(r'\b(?:[A-Z][a-z0-9]+\s){1,2}[A-Z][a-z0-9]+\b')

@lru_cache(maxsize=8192)
def extract_implicit_entities(content: str) -> List[str]:
    """
    Extracts implicit entities (capitalized proper nouns, e.g. 'Project Uroboros')
    to establish implicit graph edges without manual wikilinks.
    """
    if not content:
        return []
    
    seen = set()
    entities = []
    for match in RE_IMPLICIT_ENTITY.finditer(content):
        entity = match.group(0)
        # Avoid common sentence starters if possible, but keep it mechanically simple
        if entity not in seen:
            seen.add(entity)
            entities.append(entity)
            
    return entities

