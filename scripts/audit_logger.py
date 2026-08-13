#!/usr/bin/env python3
"""
Recurring System Audit Logger Script.
Executes skill health audits, security dependency scans, bloat detection, and self-tests,
appending structured findings to docs/system_audit_recurring.log.
"""

import sys
import os
import json
import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
scripts_dir = os.path.join(project_root, ".agents", "skills", "neuro-copilot", "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def log_system_audit():
    import subprocess
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = os.path.join(project_root, "docs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "system_audit_recurring.log")

    bridge_script = os.path.join(project_root, ".agents", "skills", "neuro-copilot", "scripts", "github_bridge.py")

    def run_sub(cmd_name):
        try:
            res = subprocess.run([sys.executable, bridge_script, cmd_name], capture_output=True, text=True, cwd=project_root)
            return json.loads(res.stdout) if res.stdout.strip().startswith("{") else {"status": "notice", "raw": res.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    bloat = run_sub("detect_bloat")
    sec = run_sub("audit_security_dependencies")
    skills = run_sub("audit_skills")

    is_healthy = "HEALTHY" if skills.get("healthy") else "UNHEALTHY"
    valid_cnt = skills.get("valid_skills_count", 0)
    iss_cnt = skills.get("issues_count", 0)
    sec_cnt = sec.get("total_findings", 0)
    bloat_cnt = bloat.get("total_bloat_warnings", 0)

    log_entry = f"=== RECURRING SYSTEM AUDIT LOG [{timestamp}] ===\n"
    log_entry += f"Skill Health: {is_healthy} ({valid_cnt} valid skills, {iss_cnt} issues)\n"
    log_entry += f"Security Vulnerabilities: {sec_cnt} findings\n"
    log_entry += f"Codebase Bloat Warnings: {bloat_cnt} warnings\n"
    if bloat.get("warnings"):
        log_entry += "Top Bloat Recommendations:\n"
        for w in bloat["warnings"][:5]:
            log_entry += f"  - [{w['file']}:{w['line']}] {w['issue']}\n"
    log_entry += "=====================================================\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Run exhaustive file-by-file AST/syntax scan
    try:
        from deep_file_scanner import run_exhaustive_file_scan
        run_exhaustive_file_scan()
    except Exception as e:
        print(f"File scanner notice: {e}")

    print(f"System audit logged successfully to {log_path}")

if __name__ == "__main__":
    log_system_audit()
