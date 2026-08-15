#!/usr/bin/env python3
"""
Neuro Co-Pilot Nomenclature & Lexical Clarity Bridge
Dedicated zero-dependency CLI bridge for:
1. Scanning codebases, UI assets, test suites, and documentation for ostentatious, sensationalist, or non-transparent words
2. Context-aware filtering (preserving canonical EVE Online news/lore and standard CS anti-pattern terms)
3. Automated deterministic normalization and batch rewriting
4. Continuous verification gate integration with Neuro Co-Pilot and GitHub CI
"""

import sys
import os
import re
import json
import argparse
import time

# Ensure UTF-8 console output resilience across Windows platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", "build",
    "coverage", ".pytest_cache", "Triage (Support)", ".gemini"
}

# Explicit terms to normalize: (Pattern, Replacement, Description)
TERM_RULES = [
    (r"\bOmni-Sovereign\b", "Universal", "Replace Omni-Sovereign with Universal"),
    (r"\bomni-sovereign\b", "universal", "Replace omni-sovereign with universal"),
    (r"\bOMNI_SOVEREIGN\b", "UNIVERSAL", "Replace OMNI_SOVEREIGN with UNIVERSAL"),
    (r"\bGod-Tier\b", "Enterprise-Grade", "Replace God-Tier with Enterprise-Grade"),
    (r"\bgod-tier\b", "enterprise-grade", "Replace god-tier with enterprise-grade"),
    (r"\bGOD_TIER\b", "ENTERPRISE_GRADE", "Replace GOD_TIER with ENTERPRISE_GRADE"),
    (r"\bMagic Wand\b", "Prompt Optimizer", "Replace Magic Wand with Prompt Optimizer"),
    (r"\bmagic wand\b", "prompt optimizer", "Replace magic wand with prompt optimizer"),
    (r"\bTranscendent Aura\b", "Holographic Aura", "Replace Transcendent Aura with Holographic Aura"),
    (r"\bTRANSCENDENTAL_AURA\b", "HOLOGRAPHIC_AURA", "Replace TRANSCENDENTAL_AURA with HOLOGRAPHIC_AURA"),
    (r"\bTranscendent Architecture\b", "Distributed Architecture", "Replace Transcendent Architecture with Distributed Architecture"),
    (r"\bSovereign Awe\b", "Executive Precision", "Replace Sovereign Awe with Executive Precision"),
    (r"\bSOVEREIGN_AWE\b", "EXECUTIVE_PRECISION", "Replace SOVEREIGN_AWE with EXECUTIVE_PRECISION"),
    (r"\bSovereign Presence\b", "Executive Presence", "Replace Sovereign Presence with Executive Presence"),
    (r"\bSOVEREIGN_PRESENCE\b", "EXECUTIVE_PRESENCE", "Replace SOVEREIGN_PRESENCE with EXECUTIVE_PRESENCE"),
    (r"\bSovereign Voice\b", "Executive Voice", "Replace Sovereign Voice with Executive Voice"),
    (r"\bSovereign Studio\b", "Voice Studio", "Replace Sovereign Studio with Voice Studio"),
    (r"\bSovereign Architecture\b", "Core Architecture", "Replace Sovereign Architecture with Core Architecture"),
    (r"\bSuper-Upgrades\b", "System Upgrades", "Replace Super-Upgrades with System Upgrades"),
    (r"\bsuper-upgrades\b", "system upgrades", "Replace super-upgrades with system upgrades"),
    (r"\bApex Phantom\b", "Phantom Stealth", "Replace Apex Phantom with Phantom Stealth"),
    (r"\bAPEX_PHANTOM\b", "BROWSER_AUTOMATION", "Replace APEX_PHANTOM with BROWSER_AUTOMATION"),
    (r"\bApex Yield\b", "Max-Yield", "Replace Apex Yield with Max-Yield"),
    (r"\bApex Farm\b", "High-Yield Farm", "Replace Apex Farm with High-Yield Farm"),
]

# Canonical patterns to protect (do NOT replace)
WHITELIST_CONTEXT_PATTERNS = [
    r"vault[\\/]Eve Online[\\/]News",    # Historical CCP EVE news chronicles
    r"god object",                        # Standard CS anti-pattern
    r"god-object",
    r"sovereignty warfare",               # EVE nullsec game mechanic
    r"sov warfare",
    r"sov nullsec",
    r"Singularity test server",           # EVE test server
    r"Max Singularity",                   # EVE character lore
    r"Zenith Quadrant",                   # EVE Quadrant lore
    r"Quantum Cores",                     # EVE structure mechanic
]


def is_whitelisted_file(filepath: str) -> bool:
    """Check if file is exempt from lexical scanning (e.g. historical game news)."""
    norm_path = filepath.replace("\\", "/")
    if "vault/Eve Online/News/" in norm_path:
        return True
    return False


def scan_file_for_terms(filepath: str) -> list:
    """Scans a single file for ostentatious or non-transparent words."""
    if is_whitelisted_file(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    findings = []
    for line_idx, line in enumerate(lines, 1):
        # Check against whitelist patterns
        if any(re.search(pat, line, re.IGNORECASE) for pat in WHITELIST_CONTEXT_PATTERNS):
            continue

        for pattern, replacement, desc in TERM_RULES:
            matches = list(re.finditer(pattern, line))
            if matches:
                for match in matches:
                    findings.append({
                        "file": filepath,
                        "line": line_idx,
                        "match": match.group(0),
                        "suggested_replacement": replacement,
                        "description": desc,
                        "context": line.strip()[:120]
                    })
    return findings


def scan_repository(search_root=".") -> list:
    """Scans the repository for non-transparent nomenclature."""
    all_findings = []
    for root, dirs, files in os.walk(search_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".md", ".json", ".yaml", ".yml"}:
                full_path = os.path.join(root, file)
                findings = scan_file_for_terms(full_path)
                all_findings.extend(findings)
    return all_findings


def auto_fix_file(filepath: str) -> int:
    """Automatically applies replacements to a file. Returns number of replacements made."""
    if is_whitelisted_file(filepath):
        return 0

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return 0

    original_content = content
    for pattern, replacement, _ in TERM_RULES:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return 1
    return 0


def auto_fix_repository(search_root=".") -> dict:
    """Batch-fixes all files in search_root."""
    fixed_files = []
    for root, dirs, files in os.walk(search_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".md", ".json", ".yaml", ".yml"}:
                full_path = os.path.join(root, file)
                if auto_fix_file(full_path):
                    fixed_files.append(full_path)
    return {
        "status": "success",
        "fixed_files_count": len(fixed_files),
        "fixed_files": fixed_files
    }


def normalize_readme_files(repo_root=".") -> dict:
    """Explicitly builds and normalizes master README and README.es files."""
    build_script = os.path.join(repo_root, "scripts", "build_master_readme.py")
    build_es_script = os.path.join(repo_root, "scripts", "build_master_readme_es.py")

    results = []
    if os.path.exists(build_script):
        auto_fix_file(build_script)
        import subprocess
        subprocess.run([sys.executable, build_script], cwd=repo_root, check=True)
        results.append("README.md regenerated")

    if os.path.exists(build_es_script):
        auto_fix_file(build_es_script)
        import subprocess
        subprocess.run([sys.executable, build_es_script], cwd=repo_root, check=True)
        results.append("README.es.md regenerated")

    return {"status": "success", "results": results}


def self_test():
    """Runs automated verification assertions for nomenclature bridge."""
    test_text = "This is an Omni-Sovereign system with God-Tier performance and Magic Wand tuning."
    fixed = test_text
    for pattern, rep, _ in TERM_RULES:
        fixed = re.sub(pattern, rep, fixed)

    assert "Omni-Sovereign" not in fixed
    assert "God-Tier" not in fixed
    assert "Magic Wand" not in fixed
    assert "Universal" in fixed
    assert "Enterprise-Grade" in fixed
    assert "Prompt Optimizer" in fixed
    print("✅ [PASS] Nomenclature Bridge self-tests passed 100%!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot Nomenclature & Lexical Clarity Bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan files for non-transparent nomenclature")
    p_scan.add_argument("--path", default=".", help="Directory or file path to scan")
    p_scan.add_argument("--json", action="store_true", help="Output findings in JSON format")

    # auto_fix
    p_fix = subparsers.add_parser("auto_fix", help="Batch-normalize non-transparent words")
    p_fix.add_argument("--path", default=".", help="Directory or file path to normalize")

    # check
    p_check = subparsers.add_parser("check", help="Verification gate check (exit code 1 if findings)")
    p_check.add_argument("--path", default=".", help="Directory or file path to check")

    # normalize_readme
    subparsers.add_parser("normalize_readme", help="Regenerate and normalize master READMEs")

    # self_test
    subparsers.add_parser("self_test", help="Run automated self-tests")

    args = parser.parse_args()

    if args.command == "scan":
        findings = scan_repository(args.path)
        if args.json:
            print(json.dumps(findings, indent=2, ensure_ascii=False))
        else:
            print(f"\n🔍 Nomenclature Scan Results for '{args.path}':")
            print(f"   Total Findings: {len(findings)}\n")
            for f in findings:
                print(f"   - {f['file']}:{f['line']} | Found: '{f['match']}' -> Replace with: '{f['suggested_replacement']}'")
                print(f"     Context: {f['context']}")
            if not findings:
                print("   ✨ 100% Clean! Zero non-transparent terms detected.")

    elif args.command == "auto_fix":
        res = auto_fix_repository(args.path)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "check":
        findings = scan_repository(args.path)
        if findings:
            print(f"❌ [FAIL] Nomenclature check failed with {len(findings)} violations:")
            for f in findings[:10]:
                print(f"   - {f['file']}:{f['line']} '{f['match']}' -> '{f['suggested_replacement']}'")
            sys.exit(1)
        else:
            print("✅ [PASS] Nomenclature verification passed! 100% clean.")
            sys.exit(0)

    elif args.command == "normalize_readme":
        res = normalize_readme_files(".")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "self_test":
        self_test()


if __name__ == "__main__":
    main()
