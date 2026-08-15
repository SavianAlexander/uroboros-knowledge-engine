"""
Universal Code Syntax Deconstruction & Spoken Code Narrator Engine.
Standard: Pure Python Standard Library (re, ast, os, sys).
Ponytail Senior Dev Principle: Translates robotic programming syntax, git commands, SQL queries, stack traces, and diffs into elegant, conversational executive speech.
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_normalizer import VoiceNormalizer


class CodeSyntaxNarrator:
    """Deconstructs code snippets and syntax into spoken conversational explanations."""

    @classmethod
    def deconstruct_code_for_speech(cls, code_snippet: str, language: str = "python") -> str:
        """
        Main pipeline: takes raw code string and returns fluent narrative text.
        """
        if not code_snippet or not code_snippet.strip():
            return "No code provided."

        text = code_snippet.strip()
        lines = text.splitlines()

        # Check if it's a unified diff
        if any(line.startswith("diff --git") or line.startswith("@@ ") for line in lines):
            return cls._narrate_diff(lines)

        # Check if it's a SQL query
        if re.match(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\b", text, re.IGNORECASE):
            return cls._narrate_sql(text)

        # Check if it's a shell/CLI command
        if re.match(r"^\s*(git|docker|npm|npx|pip|python|pytest|cargo|curl|gh)\b", text):
            return cls._narrate_cli_command(text)

        # Python / Polyglot Code Narrative
        narrated_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Python Decorators
            m_dec = re.match(r"^@([\w\.\_]+)(\(.*\))?", stripped)
            if m_dec:
                dec_name = m_dec.group(1).replace("_", " ")
                narrated_lines.append(f"Decorator {dec_name}.")
                continue

            # Class definitions
            m_cls = re.match(r"^class\s+([A-Za-z0-9_]+)(\((.*)\))?:", stripped)
            if m_cls:
                cname = cls._clean_identifier(m_cls.group(1))
                parent = m_cls.group(3)
                if parent:
                    cparent = cls._clean_identifier(parent)
                    narrated_lines.append(f"Class {cname}, inheriting from {cparent}.")
                else:
                    narrated_lines.append(f"Class {cname}.")
                continue

            # Async / Def functions
            m_func = re.match(r"^(async\s+)?def\s+([A-Za-z0-9_]+)\s*\((.*?)\)(\s*->\s*(.*?))?:", stripped)
            if m_func:
                is_async = "Asynchronous function" if m_func.group(1) else "Function"
                fname = cls._clean_identifier(m_func.group(2))
                params = m_func.group(3).strip()
                ret = m_func.group(5)

                if fname == "init":
                    fname = "initialization constructor"

                narrative = f"{is_async} {fname}"
                if params and params != "self" and params != "cls":
                    clean_params = cls._clean_params(params)
                    narrative += f", accepting {clean_params}"
                if ret:
                    clean_ret = cls._clean_type_hint(ret)
                    narrative += f", returning {clean_ret}"
                narrated_lines.append(narrative + ".")
                continue

            # Return statements
            m_ret = re.match(r"^return\s+(.*)", stripped)
            if m_ret:
                ret_val = m_ret.group(1).rstrip(";")
                narrated_lines.append(f"Returns {cls._clean_expression(ret_val)}.")
                continue

            # Try / Except / Finally
            if stripped.startswith("try:"):
                narrated_lines.append("Try block.")
                continue
            m_exc = re.match(r"^except\s+([A-Za-z0-9_]+)(\s+as\s+[A-Za-z0-9_]+)?:", stripped)
            if m_exc:
                err_type = cls._clean_identifier(m_exc.group(1))
                narrated_lines.append(f"Catching {err_type}.")
                continue
            if stripped.startswith("finally:"):
                narrated_lines.append("Finally block.")
                continue

            # Variable Assignment
            m_assign = re.match(r"^([A-Za-z0-9_\,\s]+)\s*=\s*(.*)", stripped)
            if m_assign:
                var_name = cls._clean_identifier(m_assign.group(1))
                expr = cls._clean_expression(m_assign.group(2))
                narrated_lines.append(f"Sets {var_name} to {expr}.")
                continue

            # Fallback line
            clean_line = cls._clean_expression(stripped)
            narrated_lines.append(clean_line)

        raw_narrative = " ".join(narrated_lines)
        return VoiceNormalizer.normalize_for_speech(raw_narrative)

    @classmethod
    def _narrate_diff(cls, lines: List[str]) -> str:
        """Translate git diff hunks into spoken summary."""
        added = 0
        removed = 0
        modified_files = []

        for line in lines:
            if line.startswith("+++ b/"):
                modified_files.append(line.replace("+++ b/", "").strip())
            elif line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1

        file_str = ", ".join(modified_files) if modified_files else "codebase"
        summary = f"Diff for {file_str}: {added} lines added, and {removed} lines removed."
        return VoiceNormalizer.normalize_for_speech(summary)

    @classmethod
    def _narrate_sql(cls, sql_text: str) -> str:
        """Translate SQL statement into spoken English."""
        sql = sql_text.strip()
        m_sel = re.match(r"SELECT\s+(.*?)\s+FROM\s+([A-Za-z0-9_]+)(\s+WHERE\s+(.*?))?(\s+ORDER BY\s+(.*?))?(\s+LIMIT\s+(\d+))?;?$", sql, re.IGNORECASE)
        if m_sel:
            fields = m_sel.group(1).strip()
            table = cls._clean_identifier(m_sel.group(2).strip())
            where = m_sel.group(4)
            order = m_sel.group(6)
            limit = m_sel.group(8)

            fields_desc = "all columns" if fields == "*" else cls._clean_identifier(fields)
            res = f"SQL query selecting {fields_desc} from the {table} table"
            if where:
                res += f" where {cls._clean_expression(where.strip())}"
            if order:
                res += f", sorted by {cls._clean_expression(order.strip())}"
            if limit:
                res += f", limited to {limit} results"
            return VoiceNormalizer.normalize_for_speech(res + ".")

        return VoiceNormalizer.normalize_for_speech(f"SQL statement: {sql}.")

    @classmethod
    def _narrate_cli_command(cls, cmd: str) -> str:
        """Translate terminal / CLI commands into spoken description."""
        cmd = cmd.strip()
        if cmd.startswith("git commit -m"):
            m = re.search(r'-m\s+["\'](.*?)["\']', cmd)
            msg = m.group(1) if m else "changes"
            return VoiceNormalizer.normalize_for_speech(f"Git commit with message: {msg}.")
        if cmd.startswith("git push"):
            return VoiceNormalizer.normalize_for_speech("Git command pushing local commits to remote repository.")
        if cmd.startswith("pytest"):
            return VoiceNormalizer.normalize_for_speech(f"Running automated test suite with command {cmd}.")
        if cmd.startswith("npm run build"):
            return VoiceNormalizer.normalize_for_speech("Running production frontend build bundle.")

        return VoiceNormalizer.normalize_for_speech(f"Terminal command: {cmd}.")

    @classmethod
    def _clean_identifier(cls, name: str) -> str:
        """Convert snake_case and CamelCase to spaced natural words."""
        # Replace underscores
        s = name.replace("_", " ")
        # Insert space before CamelCase capitals
        s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
        return s.strip()

    @classmethod
    def _clean_params(cls, params: str) -> str:
        """Convert function parameters string to natural speech."""
        parts = [p.strip() for p in params.split(",") if p.strip() and p.strip() not in ("self", "cls")]
        cleaned = []
        for p in parts:
            if ":" in p:
                name, ptype = p.split(":", 1)
                cleaned.append(f"{cls._clean_type_hint(ptype.strip())} {cls._clean_identifier(name.strip())}")
            else:
                cleaned.append(cls._clean_identifier(p))
        return ", and ".join(cleaned) if len(cleaned) <= 2 else ", ".join(cleaned)

    @classmethod
    def _clean_type_hint(cls, hint: str) -> str:
        """Clean complex Python type hints for speech."""
        h = hint.replace("Optional[", "optional ").replace("List[", "list of ").replace("Dict[", "dictionary of ")
        h = h.replace("Tuple[", "tuple of ").replace("Any", "any value").replace("]", "")
        return cls._clean_identifier(h)

    @classmethod
    def _clean_expression(cls, expr: str) -> str:
        """Clean code expressions into readable text."""
        e = expr.replace("==", " equals ").replace("!=", " does not equal ")
        e = e.replace(">=", " is greater than or equal to ").replace("<=", " is less than or equal to ")
        e = e.replace(">", " is greater than ").replace("<", " is less than ")
        e = e.replace(" and ", " and ").replace(" or ", " or ")
        e = cls._clean_identifier(e)
        return e
