#!/usr/bin/env python3
"""
Master CLI entrypoint and facade for neuro_cli.py.
Routes execution directly to .agents/skills/neuro-copilot/scripts/neuro_cli.py.
Standard: Zero-dependency, pure Python standard library.
"""
import os
import sys

TARGET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents",
    "skills",
    "neuro-copilot",
    "scripts",
    "neuro_cli.py"
)

if __name__ == "__main__":
    if os.path.exists(TARGET):
        with open(TARGET, "r", encoding="utf-8") as f:
            code = compile(f.read(), TARGET, "exec")
            sys.argv[0] = TARGET
            exec(code, {"__name__": "__main__", "__file__": TARGET})
    else:
        print(f"Error: Could not locate neuro_cli at {TARGET}", file=sys.stderr)
        sys.exit(1)
