#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.deep_lexical_audit import audit_repository

findings = audit_repository(".")
filtered = []
for f in findings:
    norm_path = f["file"].replace("\\", "/")
    if "vault/Eve Online/" in norm_path:
        continue
    filtered.append(f)

print(f"Total Non-EVE Findings: {len(filtered)}\n")
for idx, f in enumerate(filtered, 1):
    print(f"{idx}. [{f['category']}] {f['file']}:{f['line']} ({f['term']})")
    print(f"   Context: {f['context']}\n")
