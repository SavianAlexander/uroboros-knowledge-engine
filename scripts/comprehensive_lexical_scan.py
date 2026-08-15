#!/usr/bin/env python3
"""
Comprehensive Lexical Scanner for Uroboros Knowledge Engine
Categorizes findings into:
1. Valid Domain Terminology (e.g. data sovereignty, superior, god-object anti-pattern, magic bytes, superficial, super())
2. Actionable Ostentatious Terms to Normalize
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

ACTIONABLE_PATTERNS = [
    (r"\bApex Fusion\b", "High-Throughput Fusion"),
    (r"\bApex Harvester\b", "Deep Harvester"),
    (r"\bApex Extraction\b", "Deep Extraction"),
    (r"\bApex\b", "Peak"),
    (r"\bSovereign Crawler\b", "Crawler"),
    (r"\bSovereign Harvester\b", "Deep Harvester"),
    (r"\bSovereign Engine\b", "Core Engine"),
    (r"\bSovereign Architecture\b", "Core Architecture"),
    (r"\bSovereign Voice\b", "Executive Voice"),
    (r"\bSovereign Studio\b", "Voice Studio"),
    (r"\bSovereign Tri-Engine\b", "Tri-Engine"),
    (r"\bSovereign Presence\b", "Executive Presence"),
    (r"\bSovereign Awe\b", "Executive Precision"),
    (r"\bSOVEREIGN_PRESENCE\b", "EXECUTIVE_PRESENCE"),
    (r"\bSOVEREIGN_AWE\b", "EXECUTIVE_PRECISION"),
    (r"\bTRANSCENDENTAL_AURA\b", "HOLOGRAPHIC_AURA"),
    (r"\bTranscendent Aura\b", "Holographic Aura"),
    (r"\bTranscendent Architecture\b", "Distributed Architecture"),
    (r"\bTranscendent\b", "Advanced"),
    (r"\bTranscendental\b", "Advanced"),
    (r"\bTranscendence\b", "Advancement"),
    (r"\bOmniscient\b", "Comprehensive"),
    (r"\bOmni-Sovereign\b", "Universal"),
    (r"\bomni-sovereign\b", "universal"),
    (r"\bOMNI_SOVEREIGN\b", "UNIVERSAL"),
    (r"\bSupremacy\b", "Benchmark Lead"),
    (r"\bIncomparable\b", "High-Performance"),
    (r"\bUnrivaled\b", "High-Performance"),
    (r"\bUnmatched\b", "Optimized"),
    (r"\bGod-Tier\b", "Enterprise-Grade"),
    (r"\bgod-tier\b", "enterprise-grade"),
    (r"\bGOD_TIER\b", "ENTERPRISE_GRADE"),
    (r"\bMagic Wand\b", "Prompt Optimizer"),
    (r"\bmagic wand\b", "prompt optimizer"),
    (r"\bSuper-Upgrades\b", "System Upgrades"),
    (r"\bsuper-upgrades\b", "system upgrades"),
    (r"\bSupercharged\b", "Accelerated"),
    (r"\bsupercharged\b", "accelerated"),
    (r"\bFlawless\b", "Deterministic"),
    (r"\bflawless\b", "deterministic"),
    (r"\bPerfection Engine\b", "System Hygiene Engine"),
    (r"\bperfection engine\b", "system hygiene engine"),
    (r"\bRevolutionary\b", "Modern"),
    (r"\brevolutionary\b", "modern"),
    (r"\bGroundbreaking\b", "Modern"),
    (r"\bgroundbreaking\b", "modern"),
    (r"\bUnprecedented\b", "High-Performance"),
    (r"\bunprecedented\b", "high-performance"),
    (r"\bMiracle\b", "Optimization"),
    (r"\bmiracle\b", "optimization"),
]

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", "coverage", ".pytest_cache", ".gemini", "Triage (Support)"}

EXCLUDE_PATTERNS = [
    r"vault[\\/]Eve Online[\\/]News",
    r"data sovereignty",
    r"sovereignty warfare",
    r"sov warfare",
    r"sov nullsec",
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
    r"Enterprise Naming & Technical Clarity Guard",
    r"TERM_RULES",
    r"ACTIONABLE_PATTERNS",
]


def scan_actionable():
    findings = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".md", ".json", ".yaml", ".yml"}:
                filepath = os.path.join(root, file)
                norm_path = filepath.replace("\\", "/")
                if "vault/Eve Online/News/" in norm_path or "comprehensive_lexical_scan.py" in norm_path:
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for idx, line in enumerate(lines, 1):
                    if any(re.search(ep, line, re.IGNORECASE) for ep in EXCLUDE_PATTERNS):
                        continue
                    for pat, rep in ACTIONABLE_PATTERNS:
                        m = re.search(pat, line)
                        if m:
                            findings.append({
                                "file": filepath,
                                "line": idx,
                                "match": m.group(0),
                                "replacement": rep,
                                "context": line.strip()[:140]
                            })
                            break
    return findings


def auto_fix_all(findings):
    files_to_fix = set(f["file"] for f in findings)
    fixed_count = 0
    for filepath in files_to_fix:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        original_content = content
        for pat, rep in ACTIONABLE_PATTERNS:
            # Check line by line to avoid whitelisted phrases
            lines = content.splitlines(keepends=True)
            new_lines = []
            for line in lines:
                if any(re.search(ep, line, re.IGNORECASE) for ep in EXCLUDE_PATTERNS):
                    new_lines.append(line)
                else:
                    new_lines.append(re.sub(pat, rep, line))
            content = "".join(new_lines)

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            fixed_count += 1
    return fixed_count


def main():
    findings = scan_actionable()
    print(f"Actionable Ostentatious Findings: {len(findings)}")
    for f in findings:
        print(f"  - {f['file']}:{f['line']} [{f['match']}] -> {f['replacement']}")
        print(f"    {f['context']}")

    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fixed = auto_fix_all(findings)
        print(f"\nSuccessfully auto-normalized {fixed} files!")


if __name__ == "__main__":
    main()
