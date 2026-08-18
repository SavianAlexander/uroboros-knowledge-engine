"""
Automated Git Diff & Refactoring Patch Synthesizer.
Generates unified git diff patch strings for 1-click codebase refactoring.
Zero-dependency, stdlib difflib implementation.
"""
import unicodedata

import difflib
from typing import Dict, Any, List, Optional


def generate_refactoring_patch(
    original_code: str,
    modified_code: str,
    filepath: str = "src/module.py"
) -> Dict[str, Any]:
    """
    Generates a unified git diff patch string between original and modified code versions.
    """
    orig_lines = unicodedata.normalize("NFC", str(original_code or "")).splitlines(keepends=True)
    mod_lines = unicodedata.normalize("NFC", str(modified_code or "")).splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        n=3
    )
    diff_list = list(diff)
    patch_str = "".join(diff_list)

    additions = sum(1 for line in diff_list if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff_list if line.startswith("-") and not line.startswith("---"))

    return {
        "status": "success",
        "filepath": filepath,
        "has_changes": len(patch_str.strip()) > 0,
        "additions_count": additions,
        "deletions_count": deletions,
        "total_changes": additions + deletions,
        "patch": patch_str
    }


def generate_html_diff_view(
    original_code: str,
    modified_code: str,
    filepath: str = "src/module.py"
) -> str:
    """
    Generates side-by-side HTML diff visualization string.
    Zero-dependency stdlib difflib.HtmlDiff implementation.
    """
    orig_lines = str(original_code or "").splitlines()
    mod_lines = str(modified_code or "").splitlines()

    html_diff = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    return html_diff.make_file(
        orig_lines,
        mod_lines,
        fromdesc=f"Original ({filepath})",
        todesc=f"Modified ({filepath})",
        context=True,
        numlines=3
    )

# Epistemic 4-Pillar alias
synthesize_code_diff = generate_refactoring_patch

