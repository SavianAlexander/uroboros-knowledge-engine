"""
Zero-dependency Multimodal Document Layout & Form Parser Engine.
Extracts structured tables, key-value form pairs, and checkbox states ([x] / [ ]) from document text.
"""
import re
from typing import Dict, Any, List

RE_TABLE_SEPARATOR = re.compile(r'^[|\s:-]+$')
RE_KEY_VALUE_PAIR = re.compile(r'^([A-Za-z0-9_\s#.\-]{2,30})\s*:\s*(.+)$', flags=re.MULTILINE)
RE_CHECKBOX_CHECKED = re.compile(r'^\s*[-*]\s*\[[xX]\]\s*(.+)$', flags=re.MULTILINE)
RE_CHECKBOX_UNCHECKED = re.compile(r'^\s*[-*]\s*\[\s*\]\s*(.+)$', flags=re.MULTILINE)


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
        "row_count": len(data_rows)
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
