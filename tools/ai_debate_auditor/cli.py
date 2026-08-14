"""
Command-Line Interface (CLI) for Adversarial AI Debate Auditor & Counter-Argument Engine.
Zero external dependencies - 100% Python Standard Library.
"""

import argparse
import sys
import os
from typing import Optional

try:
    from .engine import DebateAuditorEngine
    from .models import EpistemicVerdict
except (ImportError, ValueError):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from tools.ai_debate_auditor.engine import DebateAuditorEngine
    from tools.ai_debate_auditor.models import EpistemicVerdict



def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai_debate_auditor",
        description="Adversarial AI Debate Auditor & Counter-Argument Engine (Zero-Dependency Epistemic Verification)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python -m tools.ai_debate_auditor.cli --input "You are brilliantly correct! Free energy is real."
  python -m tools.ai_debate_auditor.cli --file transcript.txt --output audit_report.md
  python -m tools.ai_debate_auditor.cli --file paper.txt --format json --strict
"""
    )
    
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "-i", "--input",
        type=str,
        help="Raw text string or debate assertion to audit."
    )
    input_group.add_argument(
        "-f", "--file",
        type=str,
        help="Path to file containing debate text, transcript, or research document."
    )
    
    parser.add_argument(
        "-c", "--context",
        type=str,
        default=None,
        help="Optional leading user prompt or question context for sycophancy echo detection."
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to write the output report (Markdown or JSON)."
    )
    
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format: 'markdown' (default) or 'json'."
    )
    
    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Strict mode: exit with code 1 if verdict is DEBUNKED or HRS >= 0.60."
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-essential console outputs and banners."
    )

    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Optional path to custom SQLite knowledge vault."
    )
    
    return parser.parse_args(args)


def main(args: Optional[list] = None) -> int:
    # Ensure stdout/stderr handles UTF-8 on Windows
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parsed = parse_args(args)
    
    # Resolve input text
    input_text = None
    file_path = None
    
    if parsed.file:
        file_path = parsed.file
        if not os.path.isfile(file_path):
            sys.stderr.write(f"Error: Target input file not found: {file_path}\n")
            return 1
    elif parsed.input:
        input_text = parsed.input
    else:
        # Check if piped via stdin
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            sys.stderr.write("Error: Please provide --input or --file, or pipe text via stdin.\n")
            return 1

    engine = DebateAuditorEngine(default_db_path=parsed.db)
    
    try:
        if file_path:
            report = engine.audit_file(
                file_path=file_path,
                prompt_context=parsed.context,
                strict=parsed.strict
            )
        else:
            report = engine.audit_text(
                text=input_text or "",
                prompt_context=parsed.context,
                strict=parsed.strict
            )
    except Exception as exc:
        sys.stderr.write(f"Audit Engine Error: {str(exc)}\n")
        return 1

    # Format output
    if parsed.format == "json":
        output_content = report.to_json(indent=2)
    else:
        output_content = report.markdown_report

    # Handle output target
    if parsed.output:
        try:
            output_dir = os.path.dirname(parsed.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(parsed.output, "w", encoding="utf-8") as out_f:
                out_f.write(output_content)
            if not parsed.quiet:
                sys.stderr.write(f"[ai_debate_auditor] Report written to: {parsed.output}\n")
        except Exception as write_err:
            sys.stderr.write(f"Error writing output file: {str(write_err)}\n")
            return 1
    else:
        sys.stdout.write(output_content + "\n")

    # Strict mode exit code evaluation
    if parsed.strict:
        if report.verdict == EpistemicVerdict.DEBUNKED or report.metrics.hallucination_risk_score >= 0.60:
            if not parsed.quiet:
                sys.stderr.write("[ai_debate_auditor] Strict Mode: Audit FAILED (Verdict: DEBUNKED / High Risk)\n")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
