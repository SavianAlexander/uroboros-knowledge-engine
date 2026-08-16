#!/usr/bin/env python3
"""
Deep Lexical Auditor & Exhaustive Scan Script
Scans all workspace files for any non-transparent, hyperbolic, sensationalist, or ostentatious terms.
"""

import os
import re
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Broad regex search patterns for exhaustive auditing
SEARCH_PATTERNS = [
    (r"\bapex\b", "apex"),
    (r"\bsovereign\b", "sovereign"),
    (r"\bsovereignty\b", "sovereignty"),
    (r"\btranscendent\b", "transcendent"),
    (r"\btranscendental\b", "transcendental"),
    (r"\btranscendence\b", "transcendence"),
    (r"\bomniscient\b", "omniscient"),
    (r"\bomnipresent\b", "omnipresent"),
    (r"\bomnipotent\b", "omnipotent"),
    (r"\bomni-[a-z]+\b", "omni-"),
    (r"\bsupremacy\b", "supremacy"),
    (r"\bsupreme\b", "supreme"),
    (r"\bincomparable\b", "incomparable"),
    (r"\bunrivaled\b", "unrivaled"),
    (r"\bunmatched\b", "unmatched"),
    (r"\blegendary\b", "legendary"),
    (r"\bmagic\b", "magic"),
    (r"\bmagical\b", "magical"),
    (r"\bwizard\b", "wizard"),
    (r"\bgod-?tier\b", "god-tier"),
    (r"\bgodlike\b", "godlike"),
    (r"\bgod-?like\b", "god-like"),
    (r"\bgod-?mode\b", "god-mode"),
    (r"\bsupercharged\b", "supercharged"),
    (r"\bsuper-?[a-z]+\b", "super-"),
    (r"\bultimate\b", "ultimate"),
    (r"\bflawless\b", "flawless"),
    (r"\bperfection\b", "perfection"),
    (r"\brevolutionary\b", "revolutionary"),
    (r"\bgroundbreaking\b", "groundbreaking"),
    (r"\bunprecedented\b", "unprecedented"),
    (r"\bmiracle\b", "miracle"),
    (r"\bawe\b", "awe"),
    (r"\bawe-inspiring\b", "awe-inspiring"),
    (r"\bmonstrous\b", "monstrous"),
    (r"\bbeast\b", "beast"),
    (r"\bhyper-?[a-z]+\b", "hyper-"),
]

EXCLUDE_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", "build",
    "coverage", ".pytest_cache", ".gemini", "Triage (Support)"
}

EXCLUDE_PATTERNS = [
    r"vault[\\/]Eve Online[\\/]News",
    r"data sovereignty",
    r"sovereignty warfare",
    r"sov warfare",
    r"sov nullsec",
    r"Sovereign staging",
    r"Sovereign Capital",
    r"Sovereignty Upgrades",
    r"Singularity test server",
    r"Max Singularity",
    r"Zenith Quadrant",
    r"Quantum Cores",
    r"god object",
    r"god-object",
    r"superuser",
    r"superclass",
    r"super\(\)",
    r"super\.",
    r"__init__",
    r"supervisor",
    r"magic byte",
    r"magic number",
    r"magic string",
    r"magic header",
    r"magic signature",
    r"magic cookie",
    r"Unmatched double quotes",
    r"Unmatched quotes",
    r"Unmatched prefix",
    r"Unmatched search",
    r"\+15% Flawless",
    r"Flawless Jaspet",
    r"Flawless Arkonor",
    r"HyperGraph",
    r"hyperlink",
    r"hyperparameter",
    r"hyperbolic",
    r"hypertext",
    r"SEARCH_PATTERNS",
    r"TERM_RULES",
    r"ACTIONABLE_PATTERNS",
    r"Enterprise Naming & Technical Clarity Guard",
    r"Never use informal, hype-y",
]


def audit_repository(repo_root="."):
    findings = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".md", ".json", ".yaml", ".yml"}:
                filepath = os.path.join(root, file)
                norm_path = filepath.replace("\\", "/")
                if "vault/Eve Online/News/" in norm_path or "deep_lexical_audit.py" in norm_path or "comprehensive_lexical_scan.py" in norm_path:
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for idx, line in enumerate(lines, 1):
                    if any(re.search(ep, line, re.IGNORECASE) for ep in EXCLUDE_PATTERNS):
                        continue
                    for pat, term_cat in SEARCH_PATTERNS:
                        m = re.search(pat, line, re.IGNORECASE)
                        if m:
                            findings.append({
                                "file": filepath,
                                "line": idx,
                                "term": m.group(0),
                                "category": term_cat,
                                "context": line.strip()[:140]
                            })
    return findings


if __name__ == "__main__":
    results = audit_repository(".")
    print(f"Total Broad Audit Findings: {len(results)}\n")
    for r in results:
        print(f"[{r['category']}] {r['file']}:{r['line']} -> {r['term']}")
        print(f"   Context: {r['context']}")
