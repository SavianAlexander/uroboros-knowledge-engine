"""
Zero-dependency document line comparison and similarity calculation engine using stdlib difflib.
"""

import difflib
from typing import Dict, Any, List


def compare_text_content(text_a: str, text_b: str, label_a: str = "Version A", label_b: str = "Version B") -> Dict[str, Any]:
    """
    Compares two text strings line-by-line using stdlib difflib.
    Returns unified diff lines, additions count, deletions count, and similarity ratio.
    """
    lines_a = str(text_a or "").splitlines()
    lines_b = str(text_b or "").splitlines()

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    similarity_ratio = round(matcher.ratio(), 4)

    diff_generator = difflib.unified_diff(
        lines_a, lines_b,
        fromfile=label_a,
        tofile=label_b,
        lineterm=""
    )
    diff_lines = list(diff_generator)

    additions = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    return {
        "similarity_ratio": similarity_ratio,
        "similarity_pct": round(similarity_ratio * 100, 2),
        "additions": additions,
        "deletions": deletions,
        "total_changes": additions + deletions,
        "diff_lines": diff_lines
    }
