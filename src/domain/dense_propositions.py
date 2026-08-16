"""
Dense Propositional Decomposition & Breadcrumb Scoping Engine (Milestone M2 / Feature F5).
Deconstructs complex documents into atomic, self-contained factual propositions while
preserving parent document hierarchical breadcrumb context (Document > Section > Subsection > Scope).
Zero-dependency, standard-library implementation with SQLite parent context expansion.
"""

import re
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Union

try:
    from src.infrastructure.database import get_db
except ImportError:
    get_db = None


def format_breadcrumb_scope(
    document_title: str = "",
    section_hierarchy: Optional[List[str]] = None
) -> str:
    """Formats document title and hierarchical section path into standard breadcrumb notation."""
    parts = []
    if document_title and document_title.strip():
        parts.append(document_title.strip())
    if section_hierarchy:
        for s in section_hierarchy:
            if s and str(s).strip():
                parts.append(str(s).strip())
    return " > ".join(parts)


DOT_PLACEHOLDER = "\uFF0E"
ELLIPSIS_PLACEHOLDER = "\u2026"
INTERROBANG_PLACEHOLDER = "\u203D"


def _split_into_atomic_clauses(raw_text: str) -> List[str]:
    """
    Decomposes raw passage text into clean atomic factual proposition statements.
    Handles Markdown headings, bullet points, numbered clauses, semi-colons, and compound sentences.
    Protects abbreviations, numbers, and technical symbols while filtering fragments < 12 characters.
    """
    if not raw_text or not isinstance(raw_text, str):
        return []

    text = raw_text.strip()
    if len(text) < 12:
        return []

    # 1. Protect numeric decimals (e.g. 3.14, 1.5, 1024.0)
    text = re.sub(r'(\d+)\.(\d+)', r'\g<1>' + DOT_PLACEHOLDER + r'\g<2>', text)

    # 2. Protect multi-dot abbreviations (e.g. e.g., i.e., a.m., p.m., U.S., U.S.C.)
    text = re.sub(r'\b((?:[A-Za-z]\.){2,})', lambda m: m.group(1).replace('.', DOT_PLACEHOLDER), text)

    # 3. Protect common Latin & English abbreviations
    abbr_pattern = r'\b(etc|vs|al|fig|ref|doc|dr|mr|mrs|ms|inc|ltd|corp|dept|sec|no|appx|vol|prof|gen|gov|sgt|capt|st|jr|sr|eq)\.'
    text = re.sub(abbr_pattern, r'\g<1>' + DOT_PLACEHOLDER, text, flags=re.IGNORECASE)

    # 4. Protect ellipsis (...) and interrobang (?!)
    text = text.replace('...', ELLIPSIS_PLACEHOLDER)
    text = text.replace('?!', INTERROBANG_PLACEHOLDER)
    text = text.replace('!?', INTERROBANG_PLACEHOLDER)

    # 5. Split by semicolons, newlines, and terminal sentence punctuation followed by whitespace
    raw_fragments = re.split(r'[;\n]+|(?<=[.!?\u2026\u203D])\s+', text)

    propositions = []
    for frag in raw_fragments:
        if not frag:
            continue
        
        # Restore protected characters
        frag_clean = frag.replace(DOT_PLACEHOLDER, '.').replace(ELLIPSIS_PLACEHOLDER, '...').replace(INTERROBANG_PLACEHOLDER, '?!').strip()

        # Clean leading list bullet markers (- , * , • , + ) or numbered lists (1. , (1) , (a) )
        frag_clean = re.sub(r'^[ \t]*[-*•+][ \t]+', '', frag_clean)
        frag_clean = re.sub(r'^[ \t]*(?:\d+\.|\(\d+\)|\([a-zA-Z]\))[ \t]+', '', frag_clean)
        frag_clean = frag_clean.strip()

        # Filter out empty or sub-minimal fragments (< 12 chars)
        if len(frag_clean) < 12:
            continue

        propositions.append(frag_clean)

    return propositions


def decompose_into_propositions(
    text: str,
    document_title: str = "",
    section_hierarchy: Optional[List[str]] = None,
    file_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Deconstructs complex document text into atomic self-contained factual propositions
    with hierarchical breadcrumb scope:
    [{
        'proposition_id': str,
        'file_id': int | None,
        'breadcrumb_scope': 'Doc > Section > Subsection > Scope',
        'statement': str,
        'contextual_statement': '[Doc > Section] statement',
        'char_length': int,
        'token_estimate': int,
        'section_hierarchy': list[str]
    }]
    """
    if not text or not isinstance(text, str):
        return []

    doc_prefix = str(file_id) if file_id is not None else (document_title or "doc")
    base_hierarchy = list(section_hierarchy) if section_hierarchy else []

    # Check if text contains markdown headings
    has_markdown_headings = bool(re.search(r'^(#{1,6})\s+(.+)$', text, flags=re.MULTILINE))

    propositions: List[Dict[str, Any]] = []
    global_idx = 0

    if not has_markdown_headings:
        # Standard flat text or pre-scoped text block
        breadcrumb = format_breadcrumb_scope(document_title, base_hierarchy)
        statements = _split_into_atomic_clauses(text)

        for stmt in statements:
            contextual = f"[{breadcrumb}] {stmt}" if breadcrumb else stmt
            prop = {
                "proposition_id": f"{doc_prefix}#prop_{global_idx}",
                "file_id": file_id,
                "breadcrumb_scope": breadcrumb,
                "statement": stmt,
                "contextual_statement": contextual,
                "char_length": len(stmt),
                "token_estimate": max(1, len(stmt) // 4),
                "section_hierarchy": list(base_hierarchy)
            }
            propositions.append(prop)
            global_idx += 1

        return propositions

    # Markdown structured document parsing: track heading stack
    lines = text.splitlines()
    current_heading_stack: List[Tuple[int, str]] = []
    current_block_lines: List[str] = []

    def flush_block():
        nonlocal global_idx
        if not current_block_lines:
            return
        block_text = "\n".join(current_block_lines).strip()
        current_block_lines.clear()
        if not block_text:
            return

        # Combine base hierarchy with dynamic markdown heading stack
        combined_hierarchy = list(base_hierarchy) + [h[1] for h in current_heading_stack]
        breadcrumb = format_breadcrumb_scope(document_title, combined_hierarchy)
        statements = _split_into_atomic_clauses(block_text)

        for stmt in statements:
            contextual = f"[{breadcrumb}] {stmt}" if breadcrumb else stmt
            prop = {
                "proposition_id": f"{doc_prefix}#prop_{global_idx}",
                "file_id": file_id,
                "breadcrumb_scope": breadcrumb,
                "statement": stmt,
                "contextual_statement": contextual,
                "char_length": len(stmt),
                "token_estimate": max(1, len(stmt) // 4),
                "section_hierarchy": combined_hierarchy
            }
            propositions.append(prop)
            global_idx += 1

    for line in lines:
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if header_match:
            flush_block()
            level = len(header_match.group(1))
            header_text = header_match.group(2).strip().rstrip('#').strip()
            # Pop stack to maintain strict heading tree depth
            current_heading_stack = [item for item in current_heading_stack if item[0] < level]
            current_heading_stack.append((level, header_text))
        else:
            current_block_lines.append(line)

    flush_block()
    return propositions


def expand_propositions_to_parent_context(
    propositions: List[Dict[str, Any]],
    max_parent_chars: int = 1500,
    db_connection: Any = None
) -> List[Dict[str, Any]]:
    """
    Expands atomic propositions with surrounding parent document context.
    Fetches source document content from SQLite files table or cached metadata,
    extracting a window of up to max_parent_chars around the proposition statement.
    """
    if not propositions:
        return []

    # Cache for fetched file contents in this batch
    content_cache: Dict[Union[int, str], Optional[str]] = {}

    for prop in propositions:
        file_id = prop.get("file_id")
        statement = prop.get("statement", "")
        breadcrumb = prop.get("breadcrumb_scope", "")
        doc_id_key = file_id if file_id is not None else breadcrumb.split(" > ")[0] if breadcrumb else None

        content = None
        if doc_id_key in content_cache:
            content = content_cache[doc_id_key]
        else:
            try:
                conn = db_connection or (get_db() if get_db is not None else None)
                if conn is not None:
                    cursor = conn.cursor()
                    if file_id is not None:
                        cursor.execute("SELECT content FROM files WHERE id = ?", (file_id,))
                        row = cursor.fetchone()
                        if row:
                            content = row[0] if isinstance(row, (tuple, list)) else row["content"]
                    
                    if not content and doc_id_key and file_id is None and isinstance(doc_id_key, str) and not str(doc_id_key).isdigit():
                        cursor.execute("SELECT content FROM files WHERE filename = ? OR filepath = ?", (str(doc_id_key), str(doc_id_key)))
                        row = cursor.fetchone()
                        if not row:
                            cursor.execute("SELECT content FROM files WHERE filename LIKE ? OR filepath LIKE ?", (f"%{doc_id_key}%", f"%{doc_id_key}%"))
                            row = cursor.fetchone()
                        if row:
                            content = row[0] if isinstance(row, (tuple, list)) else row["content"]
            except Exception:
                content = None
            
            content_cache[doc_id_key] = content

        parent_snippet = ""
        if content and isinstance(content, str):
            pos = content.find(statement)
            if pos != -1:
                half_window = (max_parent_chars - len(statement)) // 2
                start_idx = max(0, pos - max(0, half_window))
                end_idx = min(len(content), start_idx + max_parent_chars)
                if (end_idx - start_idx) < max_parent_chars and start_idx > 0:
                    start_idx = max(0, end_idx - max_parent_chars)
                parent_snippet = content[start_idx:end_idx].strip()
            else:
                # Case-insensitive fallback search
                lower_pos = content.lower().find(statement.lower()) if statement else -1
                if lower_pos != -1:
                    half_window = (max_parent_chars - len(statement)) // 2
                    start_idx = max(0, lower_pos - max(0, half_window))
                    end_idx = min(len(content), start_idx + max_parent_chars)
                    parent_snippet = content[start_idx:end_idx].strip()
                else:
                    parent_snippet = content[:max_parent_chars].strip()
        else:
            # Fallback when database is unavailable or document content not indexed
            parent_snippet = prop.get("contextual_statement") or statement

        prop["parent_context"] = parent_snippet
        prop["parent_context_chars"] = len(parent_snippet)
        prop["has_parent_context"] = bool(parent_snippet)

    return propositions


# Facade alias
extract_dense_propositions = decompose_into_propositions
