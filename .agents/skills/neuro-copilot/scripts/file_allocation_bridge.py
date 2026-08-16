#!/usr/bin/env python3
"""
File Allocation & Repository Topology Bridge for Neuro Co-Pilot.
Enforces clean architecture directory allocation, identifies stray/orphaned files,
cleans temporary test artifacts, and ensures zero floating files in unauthorized directories.
Zero-dependency, pure Python standard library only.
"""

import os
import sys
import json
import re
import shutil
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Canonical Root Whitelist: Only these files are authorized to exist in the repository root
ALLOWED_ROOT_FILES = {
    # Core entry points & runners
    "know.py", "main.py", "batch_index.py", "desktop_app.py", "start_copilot.py",
    "run_domain_tests.py", "run_e2e_ui_tests.py",
    "run.bat", "run.ps1", "setup.ps1", "apply_system_hardening.bat",
    
    # Root UI bundles (100% bitwise parity with src/assets)
    "index.html", "index.html.gz", "style.css", "style.css.gz", "app.js", "app.js.gz",
    
    # Core Documentation & Project Governance
    "README.md", "README.es.md", "ARCHITECTURE.md", "AGENTS.md", "CHANGELOG.md",
    "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CITATION.cff", "LICENSE",
    "PROJECT.md", "ROADMAP.md", "SECURITY.md", "SUPPORT.md", "ORIGINAL_REQUEST.md",
    "TEST_INFRA.md", "TEST_READY.md",
    
    # Configurations & Build Manifests
    "docker-compose.yml", "docker-compose.test.yml",
    "Dockerfile", "Dockerfile.frontend", "Dockerfile.test",
    "nginx.conf", "pytest.ini", "requirements.txt", "uroboros_engine.spec",
    ".gitignore", ".gitattributes", ".editorconfig", ".env.example", ".dockerignore",
    
    # Canonical Knowledge & Vector Databases
    "knowledge.db", "vectors.db"
}

ALLOWED_ROOT_DIRS = {
    ".agents", ".git", ".github", ".pytest_cache", ".venv", "__pycache__",
    "assets", "backups", "build", "chunks", "data", "dist", "docs", "dumps",
    "frontend", "models", "scratch", "scripts", "skills", "src", "tests",
    "tools", "vault", "Triage (Support)"
}

# Orphan / Stray Pattern Signatures to Flag and Clean
ORPHAN_FILE_PATTERNS = [
    r"^adversarial_.*\.db$",             # Stray test databases in root
    r"^test_.*\.db$",                    # Stray unit test databases
    r".*\.db-journal$",                  # Dead rollback journals
    r".*\.tmp$",                         # Temporary files
    r".*~\$$",                           # Windows lock files
    r"^pytest\.log$",                    # Temporary test logs in root
]


def scan_repository_allocation(repo_root: str = BASE_DIR) -> Dict[str, Any]:
    """Scans repository structure and validates file allocation against architecture rules."""
    root_violations = []
    misplaced_tests = []
    misplaced_modules = []
    orphan_artifacts = []
    
    # 1. Audit Root Directory Files
    try:
        root_items = os.listdir(repo_root)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    for item in root_items:
        full_path = os.path.join(repo_root, item)
        if os.path.isfile(full_path):
            # Check against root whitelist
            if item not in ALLOWED_ROOT_FILES:
                # Check if it matches an orphan pattern
                if any(re.match(p, item, re.IGNORECASE) for p in ORPHAN_FILE_PATTERNS):
                    orphan_artifacts.append({
                        "file": item,
                        "path": full_path,
                        "reason": "Orphan/Temporary test artifact in root directory"
                    })
                elif item.startswith("test_") and item.endswith(".py"):
                    misplaced_tests.append({
                        "file": item,
                        "path": full_path,
                        "reason": "Test file located in root; must be in tests/ directory"
                    })
                else:
                    root_violations.append({
                        "file": item,
                        "path": full_path,
                        "reason": f"Unwhitelisted root file; must be relocated to scripts/, src/, or docs/"
                    })
        elif os.path.isdir(full_path):
            if item not in ALLOWED_ROOT_DIRS and not item.startswith("."):
                root_violations.append({
                    "directory": item,
                    "path": full_path,
                    "reason": f"Unrecognized root directory '{item}'"
                })

    # 2. Audit Misallocated Tests Across Subdirectories
    for root, dirs, files in os.walk(repo_root):
        # Exclude vendor and hidden directories
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "node_modules", ".gemini", "dist", "build", "__pycache__"}]
        norm_root = os.path.relpath(root, repo_root).replace("\\", "/")
        
        # Check if test files are outside tests/ and scratch/
        if norm_root != "." and not norm_root.startswith("tests") and not norm_root.startswith("scratch") and not norm_root.startswith(".agents"):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    misplaced_tests.append({
                        "file": file,
                        "directory": norm_root,
                        "path": os.path.join(root, file),
                        "reason": f"Test file located in '{norm_root}'; should be in 'tests/'"
                    })

    # 3. Check Stray Temporary Databases in Subdirectories
    for root, dirs, files in os.walk(os.path.join(repo_root, "scripts")):
        for file in files:
            if any(re.match(p, file, re.IGNORECASE) for p in ORPHAN_FILE_PATTERNS):
                orphan_artifacts.append({
                    "file": file,
                    "directory": "scripts",
                    "path": os.path.join(root, file),
                    "reason": "Stray temporary artifact in scripts/"
                })

    total_violations = len(root_violations) + len(misplaced_tests) + len(misplaced_modules) + len(orphan_artifacts)

    return {
        "status": "success",
        "clean": total_violations == 0,
        "total_violations": total_violations,
        "root_violations": root_violations,
        "misplaced_tests": misplaced_tests,
        "misplaced_modules": misplaced_modules,
        "orphan_artifacts": orphan_artifacts,
        "allowed_root_file_count": len(ALLOWED_ROOT_FILES),
        "allowed_root_dir_count": len(ALLOWED_ROOT_DIRS)
    }


def clean_orphan_artifacts(repo_root: str = BASE_DIR) -> Dict[str, Any]:
    """Removes orphan test databases, dead temporary files, and cleans stray scratch artifacts."""
    scan = scan_repository_allocation(repo_root)
    removed = []
    errors = []

    # Clean orphan artifacts identified
    for item in scan.get("orphan_artifacts", []):
        path = item.get("path")
        if path and os.path.exists(path):
            try:
                os.remove(path)
                removed.append(path)
            except Exception as e:
                errors.append({"path": path, "error": str(e)})

    # Also clean transient WAL/SHM locks on orphan databases if found
    for item in ["adversarial_i3.db-wal", "adversarial_i3.db-shm"]:
        full_p = os.path.join(repo_root, item)
        if os.path.exists(full_p):
            try:
                os.remove(full_p)
                removed.append(full_p)
            except Exception as e:
                errors.append({"path": full_p, "error": str(e)})

    return {
        "status": "success" if not errors else "partial_success",
        "removed_count": len(removed),
        "removed_files": removed,
        "errors": errors
    }


def check_topology_gate(repo_root: str = BASE_DIR) -> int:
    """Continuous verification gate for repository file allocation (exits 0 if clean, 1 if violations)."""
    scan = scan_repository_allocation(repo_root)
    if scan.get("clean", False):
        print("✅ [PASS] Repository file allocation is 100% compliant with Clean Architecture topology.")
        return 0
    else:
        print(f"❌ [FAIL] Repository file allocation check failed with {scan.get('total_violations')} violations:")
        for v in scan.get("root_violations", []):
            print(f"   - Root Violation: {v.get('file', v.get('directory'))} -> {v.get('reason')}")
        for t in scan.get("misplaced_tests", []):
            print(f"   - Misplaced Test: {t.get('file')} in {t.get('directory')} -> {t.get('reason')}")
        for o in scan.get("orphan_artifacts", []):
            print(f"   - Orphan Artifact: {o.get('file')} -> {o.get('reason')}")
        return 1


def self_test() -> bool:
    """Automated bridge contract verification."""
    print("Executing file_allocation_bridge self_test...")
    scan = scan_repository_allocation(BASE_DIR)
    assert scan.get("status") == "success", "Scan status must be success"
    assert "total_violations" in scan, "Scan must return total_violations count"
    assert "allowed_root_file_count" in scan, "Scan must include root whitelist count"
    print(f"file_allocation_bridge self_test PASSED [100%] (Audit found {scan.get('total_violations')} violations)")
    return True


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print("Usage: file_allocation_bridge.py [scan|clean|check|self_test]")
        sys.exit(0)

    cmd = args[0].lower()
    if cmd == "scan":
        res = scan_repository_allocation(BASE_DIR)
        print(json.dumps(res, indent=2))
    elif cmd in ("clean", "cleanup", "fix"):
        res = clean_orphan_artifacts(BASE_DIR)
        print(json.dumps(res, indent=2))
    elif cmd == "check":
        code = check_topology_gate(BASE_DIR)
        sys.exit(code)
    elif cmd == "self_test":
        success = self_test()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
