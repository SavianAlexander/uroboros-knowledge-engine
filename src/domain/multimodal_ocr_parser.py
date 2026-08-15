"""
Zero-dependency Multimodal Document Layout & Form Parser Engine.
Extracts structured tables (Markdown & HTML), key-value form pairs, checkbox states ([x] / [ ]), and formats vision payloads for local Ollama VL models.
"""
import re
import json
import base64
from typing import Dict, Any, List, Optional

RE_TABLE_SEPARATOR = re.compile(r'^[|\s:-]+$')
RE_KEY_VALUE_PAIR = re.compile(r'^([A-Za-z0-9_\s#.\-]{2,30})\s*:\s*(.+)$', flags=re.MULTILINE)
RE_CHECKBOX_CHECKED = re.compile(r'^\s*[-*]\s*\[[xX]\]\s*(.+)$', flags=re.MULTILINE)
RE_CHECKBOX_UNCHECKED = re.compile(r'^\s*[-*]\s*\[\s*\]\s*(.+)$', flags=re.MULTILINE)
RE_HTML_TABLE = re.compile(r'<table[^>]*>(.*?)</table>', flags=re.DOTALL | re.IGNORECASE)
RE_HTML_ROW = re.compile(r'<tr[^>]*>(.*?)</tr>', flags=re.DOTALL | re.IGNORECASE)
RE_HTML_CELL = re.compile(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', flags=re.DOTALL | re.IGNORECASE)


def parse_markdown_tables(text: str) -> List[Dict[str, Any]]:
    """
    Parses Markdown tables into structured JSON schemas.
    Zero-dependency stdlib implementation.
    """
    if not text or not isinstance(text, str):
        return []
    lines = text.strip().split("\n")
    tables = []
    current_table_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current_table_lines.append(stripped)
        else:
            if len(current_table_lines) >= 2:
                tables.append(_build_table_structure(current_table_lines))
            current_table_lines = []

    if len(current_table_lines) >= 2:
        tables.append(_build_table_structure(current_table_lines))

    # Also parse HTML tables if present
    html_tables = parse_html_tables(text)
    tables.extend(html_tables)

    return tables


def parse_html_tables(html_text: str) -> List[Dict[str, Any]]:
    """
    Extracts structured rows and columns from raw HTML table markup.
    """
    if not html_text or "<table" not in html_text.lower():
        return []

    tables = []
    for table_match in RE_HTML_TABLE.finditer(html_text):
        table_html = table_match.group(1)
        row_matches = RE_HTML_ROW.findall(table_html)
        if not row_matches:
            continue

        raw_rows = []
        for r_html in row_matches:
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in RE_HTML_CELL.findall(r_html)]
            if cells:
                raw_rows.append(cells)

        if not raw_rows:
            continue

        headers = raw_rows[0]
        data_rows = []
        for r in raw_rows[1:]:
            row_dict = {}
            for idx, cell in enumerate(r):
                key = headers[idx] if idx < len(headers) else f"col_{idx}"
                row_dict[key] = cell
            data_rows.append(row_dict)

        tables.append({
            "headers": headers,
            "rows": data_rows,
            "row_count": len(data_rows),
            "format": "html"
        })

    return tables


def _build_table_structure(table_lines: List[str]) -> Dict[str, Any]:
    header_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
    data_rows = []

    for line in table_lines[1:]:
        if RE_TABLE_SEPARATOR.match(line):
            continue  # Separator line
        row_cells = [c.strip() for c in line.strip("|").split("|")]
        row_dict = {}
        for idx, cell in enumerate(row_cells):
            key = header_cells[idx] if idx < len(header_cells) else f"col_{idx}"
            row_dict[key] = cell
        data_rows.append(row_dict)

    return {
        "headers": header_cells,
        "rows": data_rows,
        "row_count": len(data_rows),
        "format": "markdown"
    }


def extract_key_value_pairs(text: str) -> Dict[str, str]:
    """
    Extracts key-value form fields (e.g., 'Invoice #: 12345', 'Total: $500.00').
    """
    if not text or not isinstance(text, str):
        return {}
    matches = RE_KEY_VALUE_PAIR.findall(text)
    kv_dict = {}
    for k, v in matches:
        kv_dict[k.strip()] = v.strip()
    return kv_dict


def parse_checkbox_states(text: str) -> Dict[str, List[str]]:
    """
    Extracts checked '[x]' and unchecked '[ ]' task list items.
    """
    if not text or not isinstance(text, str):
        return {"checked": [], "unchecked": []}
    checked = RE_CHECKBOX_CHECKED.findall(text)
    unchecked = RE_CHECKBOX_UNCHECKED.findall(text)
    return {
        "checked": [c.strip() for c in checked],
        "unchecked": [u.strip() for u in unchecked]
    }


def prepare_vision_model_payload(
    image_base64_or_path: str,
    prompt: str = "Extract all text, tables, and form fields accurately.",
    model: str = "qwen2-vl:7b"
) -> Dict[str, Any]:
    """
    Constructs an Ollama-compatible Vision Model JSON payload for local visual document analysis.
    """
    raw_img = str(image_base64_or_path or "").strip()
    # Strip data URI header if present
    if raw_img.startswith("data:image"):
        raw_img = raw_img.split(",", 1)[-1]

    return {
        "model": model,
        "prompt": prompt,
        "images": [raw_img] if raw_img else [],
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }


def parse_multimodal_document_layout(text: str) -> Dict[str, Any]:
    """
    Executes full multimodal document layout, form field, and table extraction.
    """
    tables = parse_markdown_tables(text)
    kv_pairs = extract_key_value_pairs(text)
    checkboxes = parse_checkbox_states(text)

    return {
        "tables": tables,
        "key_value_pairs": kv_pairs,
        "checkboxes": checkboxes,
        "table_count": len(tables),
        "kv_pair_count": len(kv_pairs),
        "status": "success"
    }

