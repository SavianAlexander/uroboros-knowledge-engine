"""
Intelligent Neural Speech Normalizer & Lexical Phonetic Engine.
Standard: Pure Python Standard Library (re, os, sys, math, unicodedata).
Ponytail Senior Dev Principle: 100% human-grade pronunciation of tech jargon, code blocks, acronyms, and markdown without robotic cadence or external dependencies.
"""

import os
import sys
import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def number_to_words(n: int) -> str:
    """Convert an integer to natural English words."""
    if n == 0:
        return "zero"
    if n < 0:
        return "minus " + number_to_words(abs(n))

    ones = [
        "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"
    ]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    thousands = ["", "thousand", "million", "billion", "trillion"]

    def helper(num: int) -> str:
        if num == 0:
            return ""
        elif num < 20:
            return ones[num] + " "
        elif num < 100:
            return tens[num // 10] + ("-" + ones[num % 10] if num % 10 != 0 else "") + " "
        else:
            return ones[num // 100] + " hundred " + (helper(num % 100) if num % 100 != 0 else "")

    parts = []
    i = 0
    while n > 0:
        rem = n % 1000
        if rem != 0:
            word = helper(rem).strip()
            if thousands[i]:
                word += " " + thousands[i]
            parts.insert(0, word)
        n //= 1000
        i += 1

    return " ".join(parts).replace("  ", " ").strip()


PHONETIC_ACRONYM_RULES: List[Tuple[re.Pattern, str]] = [
    # Required Canonical Phonetic Expansions
    (re.compile(r"\bSHA-?256\b", re.IGNORECASE), "S-H-A two fifty six"),
    (re.compile(r"\be-?CFR\b", re.IGNORECASE), "e-C-F-R"),
    (re.compile(r"\bFTS5\b", re.IGNORECASE), "F-T-S five"),
    (re.compile(r"\bSQLite\b", re.IGNORECASE), "sequel light"),
    (re.compile(r"\bSQL\b", re.IGNORECASE), "sequel"),
    (re.compile(r"\bAPIs\b"), "A-P-Is"),
    (re.compile(r"\bAPI\b"), "A-P-I"),
    (re.compile(r"\bJSON\b", re.IGNORECASE), "j-son"),
    (re.compile(r"\bPRAGMA\b", re.IGNORECASE), "pragma"),
    (re.compile(r"\bWAL\b"), "write ahead log"),
    
    # Infrastructure, Dev & Security Terms
    (re.compile(r"\bLLMs\b", re.IGNORECASE), "L-L-Ms"),
    (re.compile(r"\bLLM\b", re.IGNORECASE), "L-L-M"),
    (re.compile(r"\bRAG\b", re.IGNORECASE), "rag"),
    (re.compile(r"\bCI/CD\b", re.IGNORECASE), "C-I C-D"),
    (re.compile(r"\bYAML\b", re.IGNORECASE), "yam-ul"),
    (re.compile(r"\bMCP\b", re.IGNORECASE), "M-C-P"),
    (re.compile(r"\bAST\b", re.IGNORECASE), "A-S-T"),
    (re.compile(r"\bSDKs\b", re.IGNORECASE), "S-D-Ks"),
    (re.compile(r"\bSDK\b", re.IGNORECASE), "S-D-K"),
    (re.compile(r"\bURLs\b", re.IGNORECASE), "U-R-Ls"),
    (re.compile(r"\bURL\b", re.IGNORECASE), "U-R-L"),
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
    (re.compile(r"\bHTTP\b", re.IGNORECASE), "H-T-T-P"),
    (re.compile(r"\bHTTPS\b", re.IGNORECASE), "H-T-T-P-S"),
    (re.compile(r"\bREST\b", re.IGNORECASE), "rest"),
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
    (re.compile(r"\bGPU\b", re.IGNORECASE), "G-P-U"),
    (re.compile(r"\bCPU\b", re.IGNORECASE), "C-P-U"),
    (re.compile(r"\bRAM\b", re.IGNORECASE), "ram"),
    (re.compile(r"\bUI\b", re.IGNORECASE), "U-I"),
    (re.compile(r"\bUX\b", re.IGNORECASE), "U-X"),
    (re.compile(r"\bGUI\b", re.IGNORECASE), "gooey"),
    (re.compile(r"\bAES\b", re.IGNORECASE), "A-E-S"),
    (re.compile(r"\bRSA\b", re.IGNORECASE), "R-S-A"),
    (re.compile(r"\bDirectML\b", re.IGNORECASE), "Direct-M-L"),
    (re.compile(r"\bWASAPI\b", re.IGNORECASE), "Wah-sah-pee"),
    (re.compile(r"\bColBERT\b", re.IGNORECASE), "Coal-bear"),
    (re.compile(r"\bBM25\b", re.IGNORECASE), "B-M 25"),
    (re.compile(r"\bHNSW\b", re.IGNORECASE), "H-N-S-W"),
    (re.compile(r"\bTypeScript\b", re.IGNORECASE), "Type-Script"),
    (re.compile(r"\bJavaScript\b", re.IGNORECASE), "Java-Script"),
    (re.compile(r"\bNode\.?js\b", re.IGNORECASE), "Node J-S"),
    (re.compile(r"\bReact\.?js\b", re.IGNORECASE), "React"),
    (re.compile(r"\bNPM\b", re.IGNORECASE), "N-P-M"),
    (re.compile(r"\bVite\b", re.IGNORECASE), "Veet"),
    (re.compile(r"\b(\d+)\s*fps\b", re.IGNORECASE), r"\1 frames per second"),
    (re.compile(r"\bFPS\b"), "F-P-S"),
    
    # Business & Conversational Common Terms
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
    (re.compile(r"\be\.?g\.?,?\b", re.IGNORECASE), "for example,"),
    (re.compile(r"\bi\.?e\.?,?\b", re.IGNORECASE), "that is,"),
    (re.compile(r"\betc\.?\b", re.IGNORECASE), "et cetera"),
    (re.compile(r"\bKPIs?\b", re.IGNORECASE), "K-P-I"),
    (re.compile(r"\bROI\b", re.IGNORECASE), "R-O-I"),
    (re.compile(r"\bSLA\b", re.IGNORECASE), "S-L-A"),
    (re.compile(r"\bMRR\b", re.IGNORECASE), "M-R-R"),
    (re.compile(r"\bARR\b", re.IGNORECASE), "A-R-R"),
    (re.compile(r"\bSaaS\b", re.IGNORECASE), "sass"),
    (re.compile(r"\bMVP\b", re.IGNORECASE), "M-V-P"),
    (re.compile(r"\bPoC\b", re.IGNORECASE), "proof of concept"),
    (re.compile(r"\bRFC\b", re.IGNORECASE), "R-F-C"),
    (re.compile(r"\bWIP\b", re.IGNORECASE), "work in progress"),
    (re.compile(r"\bP0\b", re.IGNORECASE), "priority zero critical"),
    (re.compile(r"\bP1\b", re.IGNORECASE), "priority one high"),
    (re.compile(r"\bP2\b", re.IGNORECASE), "priority two medium"),
]


class SpeechNormalizer:
    """
    Intelligent Neural Speech Normalizer:
    - Pre-processes speech text: strips markdown syntax into natural breathing pauses.
    - Summarizes code blocks into natural developer descriptions.
    - Expands technical acronyms phonetically (SHA-256, SQL, eCFR, FTS5, API, JSON, PRAGMA, WAL, $15,000).
    """

    @classmethod
    def expand_currencies_and_numbers(cls, text: str) -> str:
        """
        Converts dollar/euro/pound amounts and formatted numbers into full spoken words.
        e.g. $15,000 -> 'fifteen thousand dollars'
             $1,250.50 -> 'one thousand two hundred fifty dollars and fifty cents'
             $500M -> '500 million dollars'
             $2.5B -> '2.5 billion dollars'
        """
        if not text:
            return ""

        # Billions / Millions / Thousands shorthand
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*[bB]\b", r"\1 billion dollars", text)
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*[mM]\b", r"\1 million dollars", text)
        text = re.sub(r"\$(\d+(?:\.\d+)?)\s*[kK]\b", r"\1 thousand dollars", text)

        # $15,000.50 or $15000.50
        def dollars_and_cents_repl(m):
            raw_num_str = m.group(1).replace(",", "")
            cents_str = m.group(2)
            try:
                dollars_val = int(raw_num_str)
                cents_val = int(cents_str)
                dollars_words = number_to_words(dollars_val)
                cents_words = number_to_words(cents_val)
                return f"{dollars_words} dollars and {cents_words} cents"
            except ValueError:
                return m.group(0)

        text = re.sub(r"\$(\d{1,3}(?:,\d{3})+|\d+)\.(\d{2})\b", dollars_and_cents_repl, text)

        # $15,000 or $15000
        def dollars_only_repl(m):
            raw_num_str = m.group(1).replace(",", "")
            try:
                dollars_val = int(raw_num_str)
                dollars_words = number_to_words(dollars_val)
                return f"{dollars_words} dollars"
            except ValueError:
                return m.group(0)

        text = re.sub(r"\$(\d{1,3}(?:,\d{3})+|\d+)\b", dollars_only_repl, text)

        # Euros, Pounds, Yen
        text = re.sub(r"€(\d+(?:,\d{3})*)\b", lambda m: f"{number_to_words(int(m.group(1).replace(',', '')))} euros", text)
        text = re.sub(r"£(\d+(?:,\d{3})*)\b", lambda m: f"{number_to_words(int(m.group(1).replace(',', '')))} pounds", text)
        text = re.sub(r"¥(\d+(?:,\d{3})*)\b", lambda m: f"{number_to_words(int(m.group(1).replace(',', '')))} yen", text)

        # Multipliers (10x -> 10 times)
        text = re.sub(r"\b(\d+)x\b", r"\1 times", text)
        # Percentages
        text = re.sub(r"(\d+(?:\.\d+)?)%", r"\1 percent", text)

        return text

    @classmethod
    def summarize_code_line(cls, line: str) -> Optional[str]:
        """Convert a single line of code into spoken developer English."""
        line = line.strip()
        if not line:
            return None

        # Comments
        if line.startswith("#") or line.startswith("//"):
            return f"Comment: {line.lstrip('#/ ')}."

        # Python function definition
        if m := re.match(r"^def\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*(?:->\s*([^:]+))?:", line):
            fn = m.group(1).replace("_", " ")
            args = m.group(2).strip()
            ret = m.group(3)
            arg_desc = f"with arguments {args.replace('_', ' ')}" if args else "taking no arguments"
            ret_desc = f" returning {ret.strip()}" if ret else ""
            return f"Defining function {fn}, {arg_desc}{ret_desc}."

        # JavaScript/TypeScript function definition
        if m := re.match(r"^(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*\((.*?)\)", line):
            fn = m.group(1).replace("_", " ")
            args = m.group(2).strip()
            arg_desc = f"with parameters {args}" if args else "with no parameters"
            return f"Defining function {fn}, {arg_desc}."

        # React hook / Variable declaration
        if m := re.match(r"^(?:const|let|var)\s+\[?([a-zA-Z_]\w*)(?:,\s*set\w+)?\]?\s*=\s*(?:useState\((.*?)\)|(.*))", line):
            var_name = m.group(1).replace("_", " ")
            return f"Declaring variable {var_name}."

        # Class definition
        if m := re.match(r"^class\s+([a-zA-Z_]\w*)(?:\((.*?)\))?:", line):
            cls_name = m.group(1)
            base = m.group(2)
            base_str = f" extending {base}" if base else ""
            return f"Defining class {cls_name}{base_str}."

        # Imports
        if line.startswith("import ") or line.startswith("from "):
            clean_imp = line.replace(";", "").replace("{", "").replace("}", "").replace(",", " and ")
            return f"{clean_imp}."

        # CLI command
        if re.match(r"^(?:git|npm|pip|docker|kubectl|pytest|cargo|go|curl|uvicorn|python)\b", line):
            return f"Run command: {line}."

        # Returns
        if line.startswith("return "):
            return f"Returns {line[7:].rstrip(';').strip()}."

        # Clean punctuation fallback
        clean = re.sub(r"[;\{\}\(\)\[\]]", " ", line)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean if clean else None

    @classmethod
    def summarize_code_blocks(cls, text: str) -> str:
        """
        Detects fenced code blocks (```lang ... ```) and transforms them into
        natural, concise spoken summaries (e.g. 'A code snippet defining...').
        """
        if not text:
            return ""

        def replacer(m: re.Match) -> str:
            lang = (m.group(1) or "").strip().lower()
            content = m.group(2).strip()

            # Plain text, log, or data dumps
            if lang in ["txt", "text", "log", "output", "csv", "json", "yaml", "yml"] or not lang:
                lines = [l.strip() for l in content.split("\n") if l.strip()]
                if len(lines) > 3:
                    return " Data output provided. "
                return " " + " ".join(lines) + " "

            # Analyze code lines
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            spoken_parts = []
            for l in lines:
                summary = cls.summarize_code_line(l)
                if summary:
                    spoken_parts.append(summary)

            if spoken_parts:
                first_item = spoken_parts[0]
                if first_item.startswith("Defining function"):
                    return f" A code snippet {first_item.lower()} "
                elif first_item.startswith("Defining class"):
                    return f" A code snippet {first_item.lower()} "
                elif first_item.startswith("Declaring variable"):
                    return f" A code snippet {first_item.lower()} "
                else:
                    return f" A code snippet: {' '.join(spoken_parts[:3])} "
            
            lang_label = lang.capitalize() if lang else "code"
            return f" A code snippet containing {lang_label} instructions. "

        text = re.sub(r"```(\w*)[ \t]*\r?\n([\s\S]*?)```", replacer, text)
        text = re.sub(r"~~~(\w*)[ \t]*\r?\n([\s\S]*?)~~~", replacer, text)
        return text

    @classmethod
    def strip_markdown(cls, text: str) -> str:
        """
        Strips markdown formatting into natural breathing pauses and smooth text:
        - Strips HTML / thought reasoning tags (<think>, <thought>, <details>)
        - Replaces headers (#, ##, ###) with pause delimiters
        - Replaces markdown links [text](url) -> text
        - Replaces images ![alt](url) -> ""
        - Replaces bold/italic (**text**, *text*, __text__, _text_) -> text
        - Replaces inline code `code` -> code
        - Converts list bullets and checkboxes into natural spoken phrases
        """
        if not text:
            return ""

        # 1. Strip reasoning and thoughts
        text = re.sub(r"(?is)<think>[\s\S]*?</think>", "", text)
        text = re.sub(r"(?is)<thought>[\s\S]*?</thought>", "", text)
        text = re.sub(r"(?is)<details[\s\S]*?</details>", "", text)
        text = re.sub(r"(?is)<style[\s\S]*?</style>", "", text)
        text = re.sub(r"(?is)<script[\s\S]*?</script>", "", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", " and ", text)
        text = re.sub(r"&lt;", " less than ", text)
        text = re.sub(r"&gt;", " greater than ", text)
        text = re.sub(r"&quot;", '"', text)

        # 2. Markdown tables
        table_pattern = re.compile(r"(\|[^\r\n]+\|\r?\n\|[\s\-:|]+\|\r?\n(?:\|[^\r\n]+\|\r?\n?)+)", re.MULTILINE)
        def table_sub(match):
            lines = [l.strip() for l in match.group(1).split("\n") if l.strip()]
            if len(lines) < 3:
                return ""
            header_cells = [c.strip() for c in lines[0].split("|") if c.strip()]
            data_rows = lines[2:]
            summary = [f"Table with columns: {', '.join(header_cells)}."]
            for idx, row in enumerate(data_rows, 1):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if cells:
                    row_items = [f"{header_cells[i]}: {cells[i]}" for i in range(min(len(header_cells), len(cells)))]
                    summary.append(f"Row {idx}: {', '.join(row_items)}.")
            return " " + " ".join(summary) + " "
        text = table_pattern.sub(table_sub, text)

        # 3. Checklists and bullets
        text = re.sub(r"(?:^|\s)[\-\*]?\s*\[[xX]\]\s*", " Completed task: ", text)
        text = re.sub(r"(?:^|\s)[\-\*]?\s*\[\s*\]\s*", " Pending task: ", text)
        text = re.sub(r"^\s*[\-\*\+]\s+", ", ", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*(\d+)\.\s+", r"Item \1: ", text, flags=re.MULTILINE)

        # 4. Links and images
        text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # 5. Headers (#, ##, ###) -> natural breathing pause
        text = re.sub(r"^#{1,6}\s*(.+)$", r", \1. ", text, flags=re.MULTILINE)

        # 6. Inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # 7. Intra-word underscores (snake_case) to spaces
        text = re.sub(r"(?<=\w)_(?=\w)", " ", text)

        # 8. Bold / Italic / Strikethrough
        text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
        text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
        text = re.sub(r"~~([^~]+)~~", r"\1", text)

        # 9. Blockquotes
        text = re.sub(r"^>\s*", ", ", text, flags=re.MULTILINE)

        # 10. URLs
        text = re.sub(r"https?://\S+", "", text)

        # 11. Unicode symbols & Glyphs
        text = unicodedata.normalize("NFKC", text)
        glyph_map = [
            (r"[•►▪▫★◆○●▶▷]", ", "),
            (r"[✓✔☑]", " completed, "),
            (r"[❌☒✖]", " failed, "),
            (r"⚠️\s*(?:Warning:?)?", " Warning: "),
            (r"∑", "sum of "),
            (r"√", "square root of "),
            (r"≈", " approximately "),
            (r"≠", " is not equal to "),
            (r"≤", " is less than or equal to "),
            (r"≥", " is greater than or equal to "),
            (r"±", " plus or minus "),
            (r"→|-->|==>", " leads to "),
            (r"←|<--|<==", " comes from "),
        ]
        for pat, rep in glyph_map:
            text = re.sub(pat, rep, text)

        # Strip remaining high range emoji
        text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
        text = re.sub(r"[\u2600-\u26ff\u2700-\u27bf]", "", text)

        # Clean remaining brackets
        text = re.sub(r"[\[\]\{\}\<\>\\|#]", " ", text)

        return text

    @classmethod
    def expand_technical_acronyms(cls, text: str) -> str:
        """Substitute technical acronyms with natural phonetic equivalents."""
        if not text:
            return ""
        for pattern, replacement in PHONETIC_ACRONYM_RULES:
            text = pattern.sub(replacement, text)
        return text

    @classmethod
    def insert_natural_cadence(cls, text: str) -> str:
        """
        Inserts natural breathing pauses, cleans double punctuation, and ensures smooth conversational cadence.
        """
        if not text:
            return ""

        # Insert space after punctuation when followed by letters (protecting 3.14)
        text = re.sub(r"([.,!?;:])(?=[A-Za-z])", r"\1 ", text)

        # Semicolons and dashes to commas
        text = re.sub(r"\s*;\s*", ", ", text)
        text = re.sub(r"\s+—\s+|\s+--\s+", ", ", text)

        # Clean repeated punctuation
        text = re.sub(r"\s*,\s*,+", ", ", text)
        text = re.sub(r"\s*\.\s*\.+", ". ", text)
        text = re.sub(r",\s*\.", ".", text)
        text = re.sub(r"\.\s*,", ".", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Remove leading punctuation artifacts
        text = re.sub(r"^[,\s]+", "", text)

        if text and text[-1] not in ".!?":
            text += "."
        return text

    @classmethod
    def normalize_for_speech(cls, text: str) -> str:
        """
        Master Speech Normalization Pipeline:
        1. Summarize and translate code blocks
        2. Expand currencies and numbers ($15,000 -> fifteen thousand dollars)
        3. Strip markdown syntax into natural pauses
        4. Phonetically expand technical acronyms (SHA-256, SQL, eCFR, FTS5, API, JSON, PRAGMA, WAL)
        5. Insert breathing cadence & clean pauses
        """
        if not text:
            return ""

        # Step 1: Code blocks
        text = cls.summarize_code_blocks(text)

        # Step 2: Currency & Numbers
        text = cls.expand_currencies_and_numbers(text)

        # Step 3: Markdown syntax
        text = cls.strip_markdown(text)

        # Step 4: Technical Acronyms
        text = cls.expand_technical_acronyms(text)

        # Step 5: Natural Cadence & Breathing
        text = cls.insert_natural_cadence(text)

        return text.strip()

    normalize = normalize_for_speech
