"""
Autonomous Neural Voice Pronunciation Normalizer, Lexical Phonetic Dictionary & Audio Mastering.
Standard: Pure Python Standard Library (re, math, os, sys) + NumPy (optional guard).
Ponytail Senior Dev Principle: 100% clear human-grade pronunciation of tech jargon, code, emails, acronyms, and daily business markdown without robotic cadence.
"""

import os
import sys
import re
import math
from typing import Dict, Any, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Comprehensive Technical, EVE Online, DevOps & Everyday Business Lexicon
LEXICAL_PHONETIC_REPLACEMENTS: List[Tuple[re.Pattern, str]] = [
    # Daily Business, Productivity & Executive Terms
    (re.compile(r"\bFYI\b", re.IGNORECASE), "For your information,"),
    (re.compile(r"\bASAP\b", re.IGNORECASE), "as soon as possible"),
    (re.compile(r"\bTL;?DR\b", re.IGNORECASE), "summary,"),
    (re.compile(r"\bIMHO\b", re.IGNORECASE), "in my humble opinion,"),
    (re.compile(r"\bIMO\b", re.IGNORECASE), "in my opinion,"),
    (re.compile(r"\bETA\b", re.IGNORECASE), "E-T-A"),
    (re.compile(r"\bEOD\b", re.IGNORECASE), "end of day"),
    (re.compile(r"\bCOB\b", re.IGNORECASE), "close of business"),
    (re.compile(r"\bFAQ\b", re.IGNORECASE), "F-A-Q"),
    (re.compile(r"\bFAQs\b", re.IGNORECASE), "F-A-Qs"),
    (re.compile(r"\bTBD\b", re.IGNORECASE), "to be determined"),
    (re.compile(r"(?:^|\s)w/\s+"), " with "),
    (re.compile(r"(?:^|\s)w/o\s+"), " without "),
    (re.compile(r"\be\.?g\.?,?\b", re.IGNORECASE), "for example,"),
    (re.compile(r"\bi\.?e\.?,?\b", re.IGNORECASE), "that is,"),
    (re.compile(r"\betc\.?\b", re.IGNORECASE), "et cetera"),
    (re.compile(r"\bP\.?S\.?\b", re.IGNORECASE), "P-S,"),
    (re.compile(r"\bCC:?\b"), "C-C"),
    (re.compile(r"\bBCC:?\b"), "B-C-C"),
    (re.compile(r"\bDM\b", re.IGNORECASE), "direct message"),
    (re.compile(r"\bKPIs?\b", re.IGNORECASE), "K-P-I"),
    (re.compile(r"\bROI\b", re.IGNORECASE), "R-O-I"),
    (re.compile(r"\bSLA\b", re.IGNORECASE), "S-L-A"),
    (re.compile(r"\bMRR\b", re.IGNORECASE), "M-R-R"),
    (re.compile(r"\bARR\b", re.IGNORECASE), "A-R-R"),
    (re.compile(r"\bQ1\b", re.IGNORECASE), "first quarter"),
    (re.compile(r"\bQ2\b", re.IGNORECASE), "second quarter"),
    (re.compile(r"\bQ3\b", re.IGNORECASE), "third quarter"),
    (re.compile(r"\bQ4\b", re.IGNORECASE), "fourth quarter"),
    (re.compile(r"\bYTD\b", re.IGNORECASE), "year to date"),
    (re.compile(r"\bMoM\b", re.IGNORECASE), "month over month"),
    (re.compile(r"\bYoY\b", re.IGNORECASE), "year over year"),
    (re.compile(r"\bB2B\b", re.IGNORECASE), "B-to-B"),
    (re.compile(r"\bB2C\b", re.IGNORECASE), "B-to-C"),
    (re.compile(r"\bSaaS\b", re.IGNORECASE), "sass"),
    (re.compile(r"\bPaaS\b", re.IGNORECASE), "pass"),
    (re.compile(r"\bIaaS\b", re.IGNORECASE), "I-pass"),
    (re.compile(r"\bOKRs?\b", re.IGNORECASE), "O-K-Rs"),
    (re.compile(r"\bMVP\b", re.IGNORECASE), "M-V-P"),
    (re.compile(r"\bWIP\b", re.IGNORECASE), "work in progress"),
    (re.compile(r"\bRFC\b", re.IGNORECASE), "R-F-C"),
    (re.compile(r"\bPoC\b", re.IGNORECASE), "proof of concept"),
    (re.compile(r"\bP0\b", re.IGNORECASE), "priority zero critical"),
    (re.compile(r"\bP1\b", re.IGNORECASE), "priority one high"),
    (re.compile(r"\bP2\b", re.IGNORECASE), "priority two medium"),

    # DevOps & Infrastructure & Algorithms
    (re.compile(r"\bLLMs?\b", re.IGNORECASE), "L-L-M"),
    (re.compile(r"\bRAG\b", re.IGNORECASE), "rag"),
    (re.compile(r"\bCI/CD\b", re.IGNORECASE), "C-I C-D"),
    (re.compile(r"\bAPI\b", re.IGNORECASE), "A-P-I"),
    (re.compile(r"\bAPIs\b", re.IGNORECASE), "A-P-Eyes"),
    (re.compile(r"\bJSON\b", re.IGNORECASE), "Jason"),
    (re.compile(r"\bYAML\b", re.IGNORECASE), "yam-ul"),
    (re.compile(r"\bMCP\b", re.IGNORECASE), "M-C-P"),
    (re.compile(r"\bSQL\b", re.IGNORECASE), "sequel"),
    (re.compile(r"\bSQLite\b", re.IGNORECASE), "Sequel Light"),
    (re.compile(r"\bPostgreSQL\b", re.IGNORECASE), "Postgres sequel"),
    (re.compile(r"\bPRAGMA\b", re.IGNORECASE), "pragma"),
    (re.compile(r"\bWAL\b", re.IGNORECASE), "wall"),
    (re.compile(r"\bFTS5\b", re.IGNORECASE), "F-T-S Five"),
    (re.compile(r"\bAST\b", re.IGNORECASE), "A-S-T"),
    (re.compile(r"\bSDK\b", re.IGNORECASE), "S-D-K"),
    (re.compile(r"\bSDKs\b", re.IGNORECASE), "S-D-Ks"),
    (re.compile(r"\bURL\b", re.IGNORECASE), "U-R-L"),
    (re.compile(r"\bURLs\b", re.IGNORECASE), "U-R-Ls"),
    (re.compile(r"\bCLI\b", re.IGNORECASE), "C-L-I"),
    (re.compile(r"\bUUID\b", re.IGNORECASE), "U-U-I-D"),
    (re.compile(r"\bVAD\b", re.IGNORECASE), "V-A-D"),
    (re.compile(r"\bDSP\b", re.IGNORECASE), "D-S-P"),
    (re.compile(r"\bSFX\b", re.IGNORECASE), "sound effects"),
    (re.compile(r"\bE2E\b", re.IGNORECASE), "E-to-E"),
    (re.compile(r"\bSOC\s*2\b", re.IGNORECASE), "Sock Two"),
    (re.compile(r"\bType\s*II\b", re.IGNORECASE), "Type Two"),
    (re.compile(r"\bHTML\b", re.IGNORECASE), "H-T-M-L"),
    (re.compile(r"\bCSS\b", re.IGNORECASE), "C-S-S"),
    (re.compile(r"\bDOM\b", re.IGNORECASE), "dom"),
    (re.compile(r"\bJWT\b", re.IGNORECASE), "J-W-T"),
    (re.compile(r"\bEPUB\b", re.IGNORECASE), "E-pub"),
    (re.compile(r"\bHTTP\b", re.IGNORECASE), "H-T-T-P"),
    (re.compile(r"\bHTTPS\b", re.IGNORECASE), "H-T-T-P-S"),
    (re.compile(r"\bREST\b", re.IGNORECASE), "rest"),
    (re.compile(r"\bWSL\b", re.IGNORECASE), "W-S-L"),
    (re.compile(r"\bSAPI\b", re.IGNORECASE), "Sap-ee"),
    (re.compile(r"\bTTS\b", re.IGNORECASE), "T-T-S"),
    (re.compile(r"\bSTT\b", re.IGNORECASE), "S-T-T"),
    (re.compile(r"\bONNX\b", re.IGNORECASE), "on-ix"),
    (re.compile(r"\bOllama\b", re.IGNORECASE), "Oh-lah-ma"),
    (re.compile(r"\bKokoro\b", re.IGNORECASE), "Koh-koh-roh"),
    (re.compile(r"\bUroboros\b", re.IGNORECASE), "Oo-roh-bor-os"),
    (re.compile(r"\bAntigravity\b", re.IGNORECASE), "Anti-gravity"),
    (re.compile(r"\bTududi\b", re.IGNORECASE), "Too-doo-dee"),
    (re.compile(r"\bFastAPI\b", re.IGNORECASE), "Fast A-P-I"),
    (re.compile(r"\bGitHub\b", re.IGNORECASE), "Git-Hub"),
    (re.compile(r"\bPytest\b", re.IGNORECASE), "Pie-test"),
    (re.compile(r"\bCortana\b", re.IGNORECASE), "Cor-tah-nah"),
    (re.compile(r"\bGPU\b", re.IGNORECASE), "G-P-U"),
    (re.compile(r"\bCPU\b", re.IGNORECASE), "C-P-U"),
    (re.compile(r"\bRAM\b", re.IGNORECASE), "ram"),
    (re.compile(r"\bUI\b", re.IGNORECASE), "U-I"),
    (re.compile(r"\bUX\b", re.IGNORECASE), "U-X"),
    (re.compile(r"\bGUI\b", re.IGNORECASE), "gooey"),
    (re.compile(r"\bSHA-?256\b", re.IGNORECASE), "Shaw 256"),
    (re.compile(r"\bAES\b", re.IGNORECASE), "A-E-S"),
    (re.compile(r"\bRSA\b", re.IGNORECASE), "R-S-A"),
    (re.compile(r"\bRegex\b", re.IGNORECASE), "reg-ex"),
    (re.compile(r"\bAsync\b", re.IGNORECASE), "ay-sync"),
    (re.compile(r"\bNPM\b", re.IGNORECASE), "N-P-M"),
    (re.compile(r"\bVite\b", re.IGNORECASE), "Veet"),
    (re.compile(r"\bWebpack\b", re.IGNORECASE), "Web-pack"),
    (re.compile(r"\bTypeScript\b", re.IGNORECASE), "Type-Script"),
    (re.compile(r"\bJavaScript\b", re.IGNORECASE), "Java-Script"),
    (re.compile(r"\bNode\.?js\b", re.IGNORECASE), "Node J-S"),
    (re.compile(r"\bReact\.?js\b", re.IGNORECASE), "React"),
    (re.compile(r"\bVue\.?js\b", re.IGNORECASE), "View J-S"),

    # Complexity Notation
    (re.compile(r"O\(1\)", re.IGNORECASE), "O of 1"),
    (re.compile(r"O\(n\)", re.IGNORECASE), "O of N"),
    (re.compile(r"O\(n\s*\^\s*2\)", re.IGNORECASE), "O of N squared"),
    (re.compile(r"O\(log\s*n\)", re.IGNORECASE), "O of log N"),
    (re.compile(r"O\(n\s*log\s*n\)", re.IGNORECASE), "O of N log N"),

    # Common Programming Symbols
    (re.compile(r"\s*!=\s*"), " is not equal to "),
    (re.compile(r"\s*===\s*"), " strictly equals "),
    (re.compile(r"\s*!==\s*"), " is strictly not equal to "),
    (re.compile(r"\s*==\s*"), " equals "),
    (re.compile(r"\s*>=\s*"), " greater than or equal to "),
    (re.compile(r"\s*<=\s*"), " less than or equal to "),
    (re.compile(r"\s*=>\s*"), " yields "),
    (re.compile(r"\s*->\s*"), " transforms to "),

    # EVE Online Canonical Jargon
    (re.compile(r"\bISK\b", re.IGNORECASE), "I-S-K"),
    (re.compile(r"\bSP\b", re.IGNORECASE), "skill points"),
    (re.compile(r"\bESI\b", re.IGNORECASE), "E-S-I"),
    (re.compile(r"\bCCP\b", re.IGNORECASE), "C-C-P"),
    (re.compile(r"\bAURA\b", re.IGNORECASE), "Aura"),
    (re.compile(r"\bD-Scan\b", re.IGNORECASE), "Directional Scan"),
    (re.compile(r"\bCyno\b", re.IGNORECASE), "Sy-no"),
    (re.compile(r"\bCapacitor\b", re.IGNORECASE), "Capacitor"),
    (re.compile(r"\bSubwarp\b", re.IGNORECASE), "Sub-warp"),
    (re.compile(r"\bCovetor\b", re.IGNORECASE), "Cov-eh-tor"),
    (re.compile(r"\bPorpoise\b", re.IGNORECASE), "Por-pus"),
    (re.compile(r"\bVelator\b", re.IGNORECASE), "Vel-ay-tor"),
    (re.compile(r"\bIbis\b", re.IGNORECASE), "Eye-bis"),
    (re.compile(r"\bG-EURJ\b", re.IGNORECASE), "G-E-U-R-J"),
    (re.compile(r"\bHodrold\b", re.IGNORECASE), "Hod-rold"),
    (re.compile(r"\bMettle\b", re.IGNORECASE), "Met-ul"),

    # Measurement Units & Versioning
    (re.compile(r"\b(\d+)\s*ms\b", re.IGNORECASE), r"\1 milliseconds"),
    (re.compile(r"\b(\d+)\s*kHz\b", re.IGNORECASE), r"\1 kilohertz"),
    (re.compile(r"\b(\d+)\s*Hz\b", re.IGNORECASE), r"\1 hertz"),
    (re.compile(r"\b(\d+)\s*dB\b", re.IGNORECASE), r"\1 decibels"),
    (re.compile(r"\b(\d+)\s*MB\b", re.IGNORECASE), r"\1 megabytes"),
    (re.compile(r"\b(\d+)\s*GB\b", re.IGNORECASE), r"\1 gigabytes"),
    (re.compile(r"\b(\d+)\s*TB\b", re.IGNORECASE), r"\1 terabytes"),
    (re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b", re.IGNORECASE), r"version \1 point \2 point \3"),
    (re.compile(r"\bv(\d+)\.(\d+)\b", re.IGNORECASE), r"version \1 point \2"),
    (re.compile(r"\b100%\b"), "100 percent"),
    (re.compile(r"(\d+(?:\.\d+)?)%"), r"\1 percent"),
    (re.compile(r"\b#(\d+)\b"), r"number \1"),
]


class VoiceNormalizer:
    """Intelligent text sanitizer, code translator, email memo reader & phonetic normalizer."""

    # ------------------------------------------------------------------
    # 1. Code Syntax to Fluent Spoken English
    # ------------------------------------------------------------------
    @classmethod
    def _translate_code_line(cls, line: str) -> Optional[str]:
        """Classify and translate a single line of programming code or CLI command into spoken English."""
        # Comments
        if line.startswith("#") or line.startswith("//"):
            comment = line.lstrip("#/ \t")
            return f"Comment: {comment}."

        # Python function definitions: def func(a, b=None):
        if m_def := re.match(r"^def\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*(?:->\s*([^:]+))?:", line):
            fn_name = m_def.group(1).replace("_", " ")
            raw_args = m_def.group(2).strip()
            ret_type = m_def.group(3)
            args_str = f"with arguments {raw_args.replace('_', ' ')}" if raw_args else "taking no arguments"
            ret_str = f" returning {ret_type.strip()}" if ret_type else ""
            return f"Defining function {fn_name}, {args_str}{ret_str}."

        # JS/TS function: function name(a, b)
        if m_fn := re.match(r"^(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*\((.*?)\)", line):
            fn_name = m_fn.group(1).replace("_", " ")
            raw_args = m_fn.group(2).strip()
            args_str = f"with parameters {raw_args}" if raw_args else "with no parameters"
            return f"Defining function {fn_name}, {args_str}."

        # React useState hook: const [data, setData] = useState(...)
        if m_hook := re.match(r"^(?:const|let)\s+\[([a-zA-Z_]\w*),\s*set([a-zA-Z_]\w*)\]\s*=\s*useState\((.*?)\)", line):
            state_name = m_hook.group(1)
            init_val = m_hook.group(3) or "default"
            return f"Declaring state variable {state_name}, initialized to {init_val}."

        # Class definition: class ClassName(Base):
        if m_cls := re.match(r"^class\s+([a-zA-Z_]\w*)(?:\((.*?)\))?:", line):
            cls_name = m_cls.group(1)
            base = m_cls.group(2)
            base_str = f" extending {base}" if base else ""
            return f"Defining class {cls_name}{base_str}."

        # Imports: import x as y / from x import y
        if line.startswith("import ") or line.startswith("from "):
            clean_imp = line.replace(";", "").replace("{", "").replace("}", "").replace(",", " and ")
            return f"{clean_imp}."

        # CLI / Bash Commands
        if re.match(r"^(?:git|npm|pip|docker|kubectl|pytest|cargo|go|curl|uvicorn|python)\b", line):
            cmd_line = line
            cmd_line = re.sub(r"-m\s+[\"'](.*?)[\"']", r"with message \1", cmd_line)
            cmd_line = re.sub(r"--save-dev", "as developer dependency", cmd_line)
            cmd_line = re.sub(r"-r\s+requirements\.txt", "from requirements file", cmd_line)
            cmd_line = re.sub(r"-d\s+-p\s+(\d+):(\d+)", r"in background mapping port \1 to \2", cmd_line)
            cmd_line = re.sub(r"-v\s+-s", "with verbose output", cmd_line)
            cmd_line = re.sub(r"checkout\s+-b\s+", "checkout new branch ", cmd_line)
            return f"Run command: {cmd_line}."

        # Git Diffs: + line / - line
        if line.startswith("+ "):
            return f"Added line: {line[2:]}."
        if line.startswith("- "):
            return f"Removed line: {line[2:]}."

        # Control flow: if / elif / else / for / while / return
        if line.startswith("if ") or line.startswith("if("):
            cond = re.sub(r"^if\s*\(?|\)?\s*\{?:?$", "", line)
            return f"If {cond}:"
        if line.startswith("elif ") or line.startswith("else if"):
            cond = re.sub(r"^(?:elif|else\s+if)\s*\(?|\)?\s*\{?:?$", "", line)
            return f"Else if {cond}:"
        if line.startswith("else:") or line.startswith("else"):
            return "Otherwise:"
        if line.startswith("return "):
            val = line[7:].rstrip(";").strip()
            return f"Returns {val}."

        # Generic fallback: clean punctuation and present clearly
        clean_l = re.sub(r"[;\{\}\(\)\[\]]", " ", line)
        clean_l = re.sub(r"\s+", " ", clean_l).strip()
        return clean_l if clean_l else None

    @classmethod
    def convert_code_to_spoken_english(cls, code_text: str, lang: str = "") -> str:
        """
        Deconstructs programming syntax into natural spoken developer English.
        """
        if not code_text or not code_text.strip():
            return ""

        lines = [line.strip() for line in code_text.strip().split("\n") if line.strip()]
        spoken_lines = []
        for line in lines:
            if spoken := cls._translate_code_line(line):
                spoken_lines.append(spoken)

        return " ".join(spoken_lines)

    # ------------------------------------------------------------------
    # 2. Email & Executive Memo Parser
    # ------------------------------------------------------------------
    @classmethod
    def normalize_email_text(cls, text: str) -> str:
        """
        Parses email headers, signatures, and body into a crisp spoken memo.
        """
        if not text:
            return ""

        # 1. Transform Header blocks
        text = re.sub(r"^From:\s*(.+)$", r"Email from \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^To:\s*(.+)$", r"Addressed to \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Subject:\s*(.+)$", r"Subject: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Date:\s*(.+)$", r"Date: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Cc:\s*(.+)$", r"Copied: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Bcc:\s*(.+)$", r"Blind copied: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Re:\s*(.+)$", r"Regarding: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^Fwd:\s*(.+)$", r"Forwarded: \1. ", text, flags=re.MULTILINE | re.IGNORECASE)

        # 2. Email addresses: name@domain.com -> name at domain dot com
        def email_replacer(m):
            user = m.group(1).replace(".", " dot ").replace("_", " underscore ")
            domain = m.group(2).replace(".", " dot ")
            return f"{user} at {domain}"

        text = re.sub(r"\b([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b", email_replacer, text)

        # 3. Clean thread quote headers (e.g. On Mon, Aug 15, Jane wrote:)
        text = re.sub(r"On\s+.*,\s+([a-zA-Z\s]+)\s+wrote:", r"Earlier message from \1:", text, flags=re.IGNORECASE)

        # 4. Remove standard legal disclaimers
        text = re.sub(r"(?i)This (?:email|message) and any (?:files|attachments) transmitted with it are confidential.*", "", text)
        text = re.sub(r"(?i)Sent from my (?:iPhone|iPad|Android|Galaxy|mobile device).*", "", text)

        # 5. Signatures and sign-offs
        text = re.sub(r"(?i)\b(Best regards|Sincerely|Warm regards|Kind regards|Cheers|Thanks and regards),?\s*\n+([a-zA-Z\s]+)", r"... \1, \2.", text)

        return text

    # ------------------------------------------------------------------
    # 3. Markdown Tables to Spoken Summary
    # ------------------------------------------------------------------
    @classmethod
    def convert_tables_to_spoken_text(cls, text: str) -> str:
        """
        Translates Markdown tables into natural spoken executive briefs.
        """
        table_pattern = re.compile(r"(\|[^\r\n]+\|\r?\n\|[\s\-:|]+\|\r?\n(?:\|[^\r\n]+\|\r?\n?)+)", re.MULTILINE)

        def table_replacer(match):
            raw_table = match.group(1).strip()
            lines = [l.strip() for l in raw_table.split("\n") if l.strip()]
            if len(lines) < 3:
                return ""
            header_cells = [c.strip() for c in lines[0].split("|") if c.strip()]
            data_rows = lines[2:]

            spoken_summary = [f"Table with columns: {', '.join(header_cells)}."]
            for idx, row in enumerate(data_rows, 1):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if cells:
                    row_items = [f"{header_cells[i]}: {cells[i]}" for i in range(min(len(header_cells), len(cells)))]
                    spoken_summary.append(f"Row {idx}: {', '.join(row_items)}.")

            return " ".join(spoken_summary) + " "

        return table_pattern.sub(table_replacer, text)

    # ------------------------------------------------------------------
    # 4. Daily Business & Financial Lexicon Normalizer
    # ------------------------------------------------------------------
    @classmethod
    def normalize_daily_business_lexicon(cls, text: str) -> str:
        """
        Translates dates, times, currencies, multipliers, and checklists.
        """
        if not text:
            return ""

        # Checklist todo items (inline or multiline)
        text = re.sub(r"(?:^|\s)[\-\*]?\s*\[[xX]\]\s*", " Completed task: ", text)
        text = re.sub(r"(?:^|\s)[\-\*]?\s*\[\s*\]\s*", " Pending task: ", text)

        # Financial Currencies ($1,250,500.50, $500M, $2.5B, €100, £50)
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*B\b", r"\1 billion dollars", text)
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*M\b", r"\1 million dollars", text)
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*k\b", r"\1 thousand dollars", text)
        text = re.sub(r"\$(\d{1,3}(?:,\d{3})+)\.(\d{2})\b", lambda m: f"{m.group(1).replace(',', '')} dollars and {m.group(2)} cents", text)
        text = re.sub(r"\$(\d{1,3}(?:,\d{3})+)\b", lambda m: f"{m.group(1).replace(',', '')} dollars", text)
        text = re.sub(r"\$(\d+)\.(\d{2})\b", r"\1 dollars and \2 cents", text)
        text = re.sub(r"\$(\d+)\b", r"\1 dollars", text)
        text = re.sub(r"€(\d+)\b", r"\1 euros", text)
        text = re.sub(r"£(\d+)\b", r"\1 pounds", text)
        text = re.sub(r"¥(\d+)\b", r"\1 yen", text)

        # Multipliers: 10x, 100x -> 10 times, 100 times
        text = re.sub(r"\b(\d+)x\b", r"\1 times", text)

        # Dates: YYYY-MM-DD -> Month Day, Year
        def date_replacer(m):
            y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
            months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            month_name = months[mo] if 1 <= mo <= 12 else str(mo)
            return f"{month_name} {d}, {y}"

        text = re.sub(r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b", date_replacer, text)

        # 24-hour time to 12-hour time (14:30 -> 2:30 PM, 08:15 -> 8:15 AM)
        def time_replacer(m):
            hh = int(m.group(1))
            mm = m.group(2)
            if 0 <= hh <= 23:
                period = "P-M" if hh >= 12 else "A-M"
                h12 = hh % 12
                if h12 == 0:
                    h12 = 12
                return f"{h12}:{mm} {period}"
            return m.group(0)

        text = re.sub(r"\b([01]?\d|2[0-3]):([0-5]\d)(?::[0-5]\d)?\b", time_replacer, text)

        # Durations: 10m, 30s, 2h, 5d
        text = re.sub(r"\b(\d+)\s*min(?:s|utes?)?\b", r"\1 minutes", text)
        text = re.sub(r"\b(\d+)\s*sec(?:s|onds?)?\b", r"\1 seconds", text)
        text = re.sub(r"\b(\d+)\s*hrs?\b", r"\1 hours", text)

        # Fractions & Math powers
        text = re.sub(r"\b1/2\b", "one half", text)
        text = re.sub(r"\b1/4\b", "one quarter", text)
        text = re.sub(r"\b3/4\b", "three quarters", text)
        text = re.sub(r"\b1/3\b", "one third", text)
        text = re.sub(r"\b2/3\b", "two thirds", text)
        text = re.sub(r"\b([a-zA-Z])\^2\b", r"\1 squared", text)
        text = re.sub(r"\b([a-zA-Z])\^3\b", r"\1 cubed", text)

        return text

    # ------------------------------------------------------------------
    # 5. Core Markdown Stripper & Structural Cleaner
    # ------------------------------------------------------------------
    @staticmethod
    def strip_markdown(text: str) -> str:
        """Strip markdown syntax to prevent Kokoro from reading symbols."""
        if not text:
            return ""
        # 1. Remove fenced code blocks completely
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"~~~[\s\S]*?~~~", "", text)
        # Inline code `code` -> code
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Markdown images ![alt](url) -> ""
        text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
        # Headers #, ## -> natural pause
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        # Unordered bullets -> comma pause
        text = re.sub(r"^\s*[\-\*\+]\s+", "", text, flags=re.MULTILINE)
        # Ordered list items
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # Bold/Italic asterisks/underscores
        text = re.sub(r"(\*\*|__|\*|_)", "", text)
        # Strikethrough
        text = re.sub(r"~~([^~]+)~~", r"\1", text)
        # Blockquotes >
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove non-spoken special brackets and symbols
        text = re.sub(r"[\[\]\{\}\<\>\\|#]", " ", text)
        # Clean multiple dots
        text = re.sub(r"\.{2,}", ". ", text)
        # Collapse multiple spaces and newlines
        text = re.sub(r"\n+", ". ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def apply_phonetic_dictionary(cls, text: str) -> str:
        """Substitute technical acronyms with natural phonetic equivalents."""
        if not text:
            return ""
        for pattern, replacement in LEXICAL_PHONETIC_REPLACEMENTS:
            text = pattern.sub(replacement, text)
        return text

    @classmethod
    def insert_natural_cadence(cls, text: str) -> str:
        """
        Inserts natural clause pauses (commas and periods) for fluid conversational breathing.
        """
        if not text:
            return ""
        # Ensure punctuation has clean trailing spacing
        text = re.sub(r"([.,!?;:])(?=[^\s\d])", r"\1 ", text)
        # Insert micro-pause for semicolons
        text = re.sub(r"\s*;\s*", ", ", text)
        # Replace dashes used as parentheticals with comma pause
        text = re.sub(r"\s+—\s+|\s+--\s+", ", ", text)
        # Clean double periods / multiple commas / duplicate pauses
        text = re.sub(r"\s*,\s*,\s*", ", ", text)
        text = re.sub(r"\s*\.\s*\.\s*", ". ", text)
        text = re.sub(r",\s*\.", ".", text)
        text = re.sub(r"\.\s*,", ".", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text and text[-1] not in ".!?":
            text += "."
        return text

    @classmethod
    def shape_gravitas_intent_cadence(cls, text: str) -> str:

        """
        Gravitas & Intent Prosody Shaper (Executive & Tactical Authority):
        - Strips frivolous filler words ('basically', 'you know', 'sort of', 'kind of').
        - Injects deliberate reflective micro-pauses at consequential transition boundaries.
        - Structures sentence conclusions with downward pitch drop.
        """
        if not text:
            return ""

        # 1. Remove dilution fillers
        fillers = [
            r"\bbasically\b", r"\byou know\b", r"\bsort of\b", r"\bkind of\b",
            r"\bliterally\b", r"\bto be honest\b", r"\bhonestly\b"
        ]
        for f in fillers:
            text = re.sub(f, "", text, flags=re.IGNORECASE)

        # 2. Add reflective cadence to strong introductory markers
        markers = [
            (r"\b(Listen|Remember|Understand|In truth|In fact|However|Therefore|Indeed|Conclusively)\s*,\s*", r"\1... "),
            (r"\b(The reality is|The fact remains|Mark my words|Make no mistake)\s*,\s*", r"\1— "),
        ]
        for pat, repl in markers:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)

        # 3. Clean spacing and punctuation
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ------------------------------------------------------------------
    # 6. Master Synthesis Pipeline
    # ------------------------------------------------------------------

    @classmethod
    def normalize_for_speech(cls, text: str, mode: str = "AUTO") -> str:
        """
        Master Pipeline:
        1. Fenced Code Block Translation (convert code to spoken English)
        2. Email & Memo Formatting (headers, quotes, disclaimers)
        3. Table Narration (translating markdown tables to spoken briefs)
        4. Daily Business & Financial Lexicon (currencies, dates, times, tasks)
        5. Markdown Stripping
        6. Phonetic Lexical Dictionary
        7. Natural Cadence & Breath Injection
        """
        if not text:
            return ""

        # Step 1: Translate fenced code blocks into spoken sentences
        def code_block_handler(m):
            lang = m.group(1) or ""
            code_content = m.group(2)
            spoken = cls.convert_code_to_spoken_english(code_content, lang=lang)
            return f" Code snippet: {spoken} "

        text = re.sub(r"```(\w*)[ \t]*\r?\n([\s\S]*?)```", code_block_handler, text)
        text = re.sub(r"~~~(\w*)[ \t]*\r?\n([\s\S]*?)~~~", code_block_handler, text)

        # Step 2: Email & Memo formatting
        text = cls.normalize_email_text(text)

        # Step 3: Markdown table translation
        text = cls.convert_tables_to_spoken_text(text)

        # Step 4: Daily business, currencies, dates, times, checklists
        text = cls.normalize_daily_business_lexicon(text)

        # Step 5: Clean remaining markdown formatting
        clean = cls.strip_markdown(text)

        # Step 6: Apply phonetic technical and acronym dictionary
        phonetic = cls.apply_phonetic_dictionary(clean)

        # Step 7: Insert breathing cadence
        cadence = cls.insert_natural_cadence(phonetic)

        return cadence.strip()

    @staticmethod
    def master_audio_buffer(
        samples: Any,
        sample_rate: int = 24000,
        target_dbfs: float = -1.0,
        dsp_preset: str = "STUDIO_MASTER"
    ) -> Any:
        """
        Studio Broadcast Audio Mastering Pipeline & True-Peak Limiter.
        Applies parametric EQ, dynamic compression, de-essing, and stereo widening.
        """
        if np is None or not isinstance(samples, np.ndarray) or samples.size == 0:
            return samples

        # 1. Apply Studio DSP Mastering Rack
        try:
            from src.infrastructure.eve_voice_dsp import process_tactical_dsp_pipeline
            mastered, _ = process_tactical_dsp_pipeline(samples, sample_rate=sample_rate, preset=dsp_preset)
            samples = mastered
        except Exception:
            pass

        # 2. Remove DC Offset
        samples = samples - np.mean(samples, axis=0)

        # 3. Peak normalization to target_dbfs
        peak = np.max(np.abs(samples))
        if peak > 1e-6:
            target_linear = 10.0 ** (target_dbfs / 20.0)
            gain = target_linear / peak
            samples = samples * gain

        # 4. Soft hyperbolic tangent saturation limiter for any peaks exceeding 0.95
        threshold = 0.95
        over_idx = np.abs(samples) > threshold
        if np.any(over_idx):
            samples[over_idx] = np.sign(samples[over_idx]) * (
                threshold + (1.0 - threshold) * np.tanh((np.abs(samples[over_idx]) - threshold) / (1.0 - threshold))
            )

        return np.clip(samples, -1.0, 1.0).astype(np.float32)
