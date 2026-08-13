"""
Automated Git Diff & Refactoring Patch Synthesizer.
Generates unified git diff patch strings for 1-click codebase refactoring.
Zero-dependency, stdlib difflib implementation.
"""

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
    orig_lines = original_code.splitlines(keepends=True)
    mod_lines = modified_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        n=3
    )
    patch_str = "".join(diff)

    return {
        "status": "success",
        "filepath": filepath,
        "has_changes": len(patch_str.strip()) > 0,
        "patch": patch_str
    }
