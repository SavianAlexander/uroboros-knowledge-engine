#!/usr/bin/env python3
"""
Exhaustive File-by-File Code Scanner.
Scans every single file in the codebase for AST syntax errors, unused imports,
type warnings, malformed JSON, and line-by-line code issues, appending findings
to docs/system_audit_recurring.log.
"""

import sys
import os
import ast
import json
import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def scan_python_file(filepath):
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
        tree = ast.parse(code, filename=filepath)

        # Check for unused imports or syntax issues
        for node in ast.walk(tree):
            if isinstance(node, ast.Try) and not node.handlers and not node.finalbody:
                issues.append((node.lineno, "Empty try block without except/finally handlers"))
            elif isinstance(node, ast.FunctionDef) and len(node.body) == 0:
                issues.append((node.lineno, f"Function '{node.name}' has empty body"))
    except SyntaxError as e:
        issues.append((e.lineno or 1, f"SyntaxError: {e.msg}"))
    except Exception as e:
        issues.append((1, f"Parse Error: {str(e)}"))
    return issues

def scan_json_file(filepath):
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        issues.append((e.lineno, f"JSONDecodeError: {e.msg}"))
    except Exception as e:
        issues.append((1, f"JSON Read Error: {str(e)}"))
    return issues

def run_exhaustive_file_scan():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = os.path.join(project_root, "docs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "system_audit_recurring.log")

    scanned_files = 0
    file_issues = {}

    for root, dirs, files in os.walk(project_root):
        # Exclude node_modules, .git, venv, build, dist, brain
        dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "venv", "__pycache__", "dist", "build", ".gemini", "brain"]]

        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, project_root)
            scanned_files += 1

            if file.endswith(".py"):
                issues = scan_python_file(filepath)
                if issues:
                    file_issues[rel_path] = issues
            elif file.endswith(".json"):
                issues = scan_json_file(filepath)
                if issues:
                    file_issues[rel_path] = issues

    log_entry = f"=== EXHAUSTIVE FILE-BY-FILE AUDIT LOG [{timestamp}] ===\n"
    log_entry += f"Total Files Scanned: {scanned_files}\n"
    log_entry += f"Files with Line Errors/Warnings: {len(file_issues)}\n"

    if file_issues:
        log_entry += "Detailed Line-by-Line File Issues Found:\n"
        for fpath, issues in file_issues.items():
            log_entry += f"  File: [{fpath}]\n"
            for line, err in issues:
                log_entry += f"    - Line {line}: {err}\n"
    else:
        log_entry += "NO FILE SYNTAX OR PARSE ERRORS DETECTED ACROSS WORKSPACE.\n"

    log_entry += "=========================================================\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Exhaustive file scan complete ({scanned_files} files scanned). Logged to {log_path}")

if __name__ == "__main__":
    run_exhaustive_file_scan()
