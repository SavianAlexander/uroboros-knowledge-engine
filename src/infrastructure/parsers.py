"""
Document parsing and content extraction modules (PDF, DOCX, RTF, XLSX, Audio, Images, Binary).
"""
import os
import re
import time
import hashlib
import functools
import wave
import zipfile
from typing import Tuple, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

import pypdf
import docx
from striprtf.striprtf import rtf_to_text
import openpyxl

logging.getLogger("pypdf").setLevel(logging.ERROR)

from src.infrastructure.ocr import extract_ocr_text_structured, extract_pdf_ocr
from src.domain.ocr_engine import extract_text_from_image

RE_PRINTABLE_BYTES = re.compile(b'[\x20-\x7E]{4,}')
RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_WHITESPACE_COLLAPSE = re.compile(r'\s+')

def calculate_sha256(filepath: str) -> Optional[str]:
    """Calculate SHA-256 hash of a file using C-level stdlib file_digest."""
    try:
        with open(filepath, 'rb') as f:
            if hasattr(hashlib, "file_digest"):
                return hashlib.file_digest(f, "sha256").hexdigest()
            sha256 = hashlib.sha256()
            while chunk := f.read(65536):
                sha256.update(chunk)
            return sha256.hexdigest()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in parsers.py: {e}")
        logger.warning(f"Error calculating SHA256 for {filepath}: {e}")
        return None

@functools.lru_cache(maxsize=4096)
def calculate_sha256_cached(filepath: str, mtime: float) -> Optional[str]:
    """LRU cached SHA-256 calculation based on mtime."""
    return calculate_sha256(filepath)

def safe_read_file(filepath: str, mode: str = "rb", attempts: int = 3) -> bytes:
    """Windows File Lock Resiliency: Retries file read operation if locked by antivirus scanner."""
    for attempt in range(attempts):
        try:
            with open(filepath, mode) as f:
                return f.read()
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.05 * (2 ** attempt))
    return b""

def safe_write_file(filepath: str, content: str, attempts: int = 3) -> bool:
    """Windows File Lock Resiliency: Retries file write operation if locked by antivirus scanner."""
    norm_path = os.path.abspath(filepath)
    for attempt in range(attempts):
        try:
            with open(norm_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.05 * (2 ** attempt))
    return False

def parse_audio_metadata(filepath: str) -> Dict[str, Any]:
    """Parse audio file metadata (WAV/MP3) with corrupt header validation."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) < 44:
        return {"duration": 0.0, "channels": 0, "samplerate": 0, "bitrate": "0 kbps"}
    try:
        with wave.open(filepath, 'rb') as w:
            params = w.getparams()
            if params.framerate <= 0 or params.nframes < 0 or params.nchannels <= 0:
                raise ValueError("Corrupt audio header params")
            # Verify file size matches expected wave payload length
            expected_min_bytes = 44 + (params.nframes * params.sampwidth * params.nchannels)
            if os.path.getsize(filepath) < expected_min_bytes:
                raise ValueError("Truncated or corrupt audio payload")
            duration = params.nframes / params.framerate
            return {
                "duration": round(duration, 2),
                "channels": params.nchannels,
                "samplerate": params.framerate,
                "bitrate": f"{params.framerate * params.sampwidth * 8 * params.nchannels // 1000} kbps"
            }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning(f"Error parsing audio metadata for {filepath}: {e}")
        return {"duration": 0.0, "channels": 0, "samplerate": 0, "bitrate": "0 kbps"}

def parse_jupyter_notebook(filepath: str) -> str:
    """
    Extracts structured Markdown narrative, Python code cells, LaTeX equations,
    and stdout / evaluation outputs from Jupyter Notebook (.ipynb) files.
    """
    import json
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            nb = json.load(f)

        cells = nb.get("cells", [])
        if not cells:
            return "[Empty Jupyter Notebook]"

        sections = []
        metadata = nb.get("metadata", {})
        kernel_name = metadata.get("kernelspec", {}).get("display_name") or metadata.get("language_info", {}).get("name") or "Python"
        sections.append(f"# Jupyter Notebook: {os.path.basename(filepath)} [Kernel: {kernel_name}]\n")

        for idx, cell in enumerate(cells, 1):
            cell_type = cell.get("cell_type", "code")
            source_lines = cell.get("source", [])
            source_text = "".join(source_lines) if isinstance(source_lines, list) else str(source_lines)

            if cell_type == "markdown":
                if source_text.strip():
                    sections.append(f"<!-- Cell {idx}: Markdown -->\n{source_text.strip()}\n")
            elif cell_type == "code":
                if source_text.strip():
                    sections.append(f"```python\n# [Cell {idx}: Code]\n{source_text.strip()}\n```")
                
                # Extract text outputs (stdout, stderr, text/plain)
                outputs = cell.get("outputs", [])
                out_texts = []
                for out in outputs:
                    out_type = out.get("output_type", "")
                    if out_type == "stream":
                        s_text = "".join(out.get("text", [])) if isinstance(out.get("text"), list) else str(out.get("text", ""))
                        if s_text.strip():
                            out_texts.append(f"[Stdout]:\n{s_text.strip()}")
                    elif out_type in ("execute_result", "display_data"):
                        data = out.get("data", {})
                        if "text/plain" in data:
                            res_txt = "".join(data["text/plain"]) if isinstance(data["text/plain"], list) else str(data["text/plain"])
                            if res_txt.strip():
                                out_texts.append(f"[Result]: {res_txt.strip()}")
                    elif out_type == "error":
                        ename = out.get("ename", "Error")
                        evalue = out.get("evalue", "")
                        out_texts.append(f"[Error: {ename}]: {evalue}")

                if out_texts:
                    sections.append("```text\n" + "\n".join(out_texts) + "\n```\n")
            elif cell_type == "raw":
                if source_text.strip():
                    sections.append(f"<!-- Cell {idx}: Raw Text -->\n{source_text.strip()}\n")

        return "\n".join(sections)
    except Exception as e:
        return f"[Jupyter Notebook Parsing Error: {str(e)}]"


def parse_obsidian_markdown(filepath: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parses Obsidian YAML frontmatter, Dataview key::value fields, and [[Wikilinks]].
    Extracts structured metadata (tags, aliases, dates, relations) into a searchable document header.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()

        metadata: Dict[str, Any] = {
            "tags": [],
            "aliases": [],
            "wikilinks": [],
            "dataview": {},
            "created": None,
            "modified": None
        }

        body = raw
        # 1. Parse YAML frontmatter bounded by ---
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            body = raw[fm_match.end():]
            
            for line in fm_text.splitlines():
                if ":" in line and not line.strip().startswith("-"):
                    k, v = line.split(":", 1)
                    key = k.strip().lower()
                    val = v.strip().strip("'\"")
                    
                    if key in ("tags", "tag"):
                        if val.startswith("[") and val.endswith("]"):
                            metadata["tags"].extend([t.strip().strip("'\"#") for t in val[1:-1].split(",") if t.strip()])
                        elif val:
                            metadata["tags"].append(val.strip("#"))
                    elif key in ("aliases", "alias"):
                        if val.startswith("[") and val.endswith("]"):
                            metadata["aliases"].extend([a.strip().strip("'\"") for a in val[1:-1].split(",") if a.strip()])
                        elif val:
                            metadata["aliases"].append(val)
                    elif key in ("created", "date"):
                        metadata["created"] = val
                    elif key in ("modified", "updated"):
                        metadata["modified"] = val
                    elif val:
                        metadata["dataview"][key] = val
                elif line.strip().startswith("-") and metadata["tags"] is not None:
                    item = line.strip().lstrip("-").strip().strip("'\"#")
                    if item:
                        metadata["tags"].append(item)

        # 2. Extract Obsidian [[Wikilinks]] (e.g. [[Target Page|Display Name]] or [[Target Page]])
        wikilink_matches = re.findall(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', body)
        for target, display in wikilink_matches:
            target_clean = target.strip()
            if target_clean:
                metadata["wikilinks"].append({
                    "target": target_clean,
                    "display": (display or target_clean).strip()
                })

        # 3. Extract Dataview inline fields [key:: value] or key:: value
        dv_bracketed = re.findall(r'\[([a-zA-Z0-9_\-]+)::\s*([^\]]+)\]', body)
        for k, v in dv_bracketed:
            metadata["dataview"][k.strip().lower()] = v.strip()

        # 4. Extract inline hashtags #topic/subtopic
        inline_tags = re.findall(r'(?:^|\s)#([a-zA-Z0-9_\-/]+)', body)
        for t in inline_tags:
            clean_t = t.strip()
            if clean_t and clean_t not in metadata["tags"] and not clean_t.isdigit():
                metadata["tags"].append(clean_t)

        # Build clean enriched content with structured metadata header for RAG indexing
        meta_header = []
        if metadata["tags"]:
            meta_header.append(f"**Tags**: {', '.join(metadata['tags'])}")
        if metadata["aliases"]:
            meta_header.append(f"**Aliases**: {', '.join(metadata['aliases'])}")
        if metadata["wikilinks"]:
            link_names = [w["target"] for w in metadata["wikilinks"]]
            meta_header.append(f"**Wikilinks**: {', '.join(link_names[:10])}")
        if metadata["dataview"]:
            dv_str = ", ".join([f"{k}={v}" for k, v in list(metadata["dataview"].items())[:6]])
            meta_header.append(f"**Dataview**: {dv_str}")

        header_block = "\n".join(meta_header) + "\n\n" if meta_header else ""
        return header_block + body.strip(), metadata
    except Exception as e:
        return f"[Obsidian Parsing Error: {str(e)}]", {}


def parse_pptx_presentation(filepath: str) -> str:
    """
    Extracts slide titles, body bullet points, shapes, and speaker notes from PowerPoint (.pptx) files
    using stdlib zipfile and XML parsing for zero-dependency portability.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    try:
        slides_text = []
        with zipfile.ZipFile(filepath, "r") as z:
            # 1. Discover all slide XML files
            slide_names = [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml', n)]
            # Sort slides numerically: slide1.xml, slide2.xml, slide10.xml
            slide_names.sort(key=lambda x: int(re.search(r'\d+', x).group()))

            for idx, sname in enumerate(slide_names, 1):
                raw_xml = z.read(sname)
                root = ET.fromstring(raw_xml)
                
                # Text runs in DrawingML: a:p (paragraph), a:r (run), a:t (text)
                paragraphs = []
                for p in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}p'):
                    p_texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t') if t.text]
                    line = "".join(p_texts).strip()
                    if line:
                        paragraphs.append(line)

                slide_title = paragraphs[0] if paragraphs else f"Slide {idx}"
                body_lines = paragraphs[1:] if len(paragraphs) > 1 else []

                slide_block = [f"## Slide {idx}: {slide_title}"]
                for b in body_lines:
                    slide_block.append(f"- {b}")

                # 2. Check for speaker notes in notesSlides
                notes_name = f"ppt/notesSlides/notesSlide{idx}.xml"
                if notes_name in z.namelist():
                    notes_xml = z.read(notes_name)
                    notes_root = ET.fromstring(notes_xml)
                    notes_paras = []
                    for np in notes_root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}p'):
                        np_texts = [t.text for t in np.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t') if t.text]
                        nline = "".join(np_texts).strip()
                        if nline and not nline.isdigit() and nline != slide_title:
                            notes_paras.append(nline)
                    if notes_paras:
                        slide_block.append(f"\n> **Speaker Notes**: {' '.join(notes_paras)}")

                slides_text.append("\n".join(slide_block))

        doc_header = f"# PowerPoint Presentation: {os.path.basename(filepath)} [Total Slides: {len(slides_text)}]\n\n"
        return doc_header + "\n\n".join(slides_text)
    except Exception as e:
        return f"[PPTX Parsing Error: {str(e)}]"


def parse_tabular_csv(filepath: str, max_preview_rows: int = 30) -> str:
    """
    Parses CSV and TSV tabular datasets, automatically detecting delimiters,
    inferring column data types, computing summary statistics, and generating markdown tables.
    """
    import csv
    try:
        sample_bytes = safe_read_file(filepath)[:8192]
        sample_text = sample_bytes.decode("utf-8", errors="replace")
        
        # Detect delimiter
        delim = ","
        if "\t" in sample_text and sample_text.count("\t") > sample_text.count(","):
            delim = "\t"
        elif ";" in sample_text and sample_text.count(";") > sample_text.count(","):
            delim = ";"
        elif "|" in sample_text and sample_text.count("|") > sample_text.count(","):
            delim = "|"

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter=delim)
            rows = []
            for r in reader:
                if r:
                    rows.append(r)

        if not rows:
            return "[Empty Tabular Dataset]"

        headers = rows[0]
        data_rows = rows[1:]
        total_rows = len(data_rows)
        total_cols = len(headers)

        # Infer column types
        type_summary = []
        for col_idx in range(total_cols):
            col_name = headers[col_idx] if col_idx < len(headers) else f"Col_{col_idx+1}"
            col_values = [r[col_idx] for r in data_rows if col_idx < len(r) and r[col_idx].strip()]
            
            is_int = True
            is_float = True
            for v in col_values[:100]:
                try:
                    int(v)
                except ValueError:
                    is_int = False
                try:
                    float(v)
                except ValueError:
                    is_float = False

            if is_int:
                inferred = "Integer"
            elif is_float:
                inferred = "Float"
            elif all(len(v) in (10, 19) and ("-" in v or "/" in v) for v in col_values[:50] if v):
                inferred = "Date/ISO"
            else:
                inferred = "String"
            type_summary.append(f"`{col_name}` ({inferred})")

        sections = [
            f"# Tabular Dataset: {os.path.basename(filepath)}",
            f"- **Dimensions**: {total_rows} rows x {total_cols} columns | **Delimiter**: `{repr(delim)[1:-1]}`",
            f"- **Schema**: {', '.join(type_summary)}\n",
            f"### Preview (First {min(total_rows, max_preview_rows)} rows):"
        ]

        # Format markdown table
        md_table = []
        header_row = "| " + " | ".join([h.replace("|", "/") for h in headers]) + " |"
        sep_row = "| " + " | ".join(["---"] * total_cols) + " |"
        md_table.append(header_row)
        md_table.append(sep_row)

        for row in data_rows[:max_preview_rows]:
            padded = row + [""] * (total_cols - len(row))
            row_str = "| " + " | ".join([str(val).replace("|", "/").replace("\n", " ") for val in padded[:total_cols]]) + " |"
            md_table.append(row_str)

        sections.append("\n".join(md_table))
        return "\n".join(sections)
    except Exception as e:
        return f"[CSV/Tabular Parsing Error: {str(e)}]"


def extract_content(filepath: str, suffix: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text content and coordinates based on file extension/type."""
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > 50 * 1024 * 1024:
            return f"[File Size Exceeds 50MB - Extraction Skipped: {os.path.basename(filepath)}]", []
        
        # 1. Specialized Parsers
        if suffix == '.ipynb':
            return parse_jupyter_notebook(filepath), []
        elif suffix in ('.md', '.markdown'):
            content, _ = parse_obsidian_markdown(filepath)
            return content, []
        elif suffix == '.pptx':
            return parse_pptx_presentation(filepath), []
        elif suffix in ('.csv', '.tsv', '.tab'):
            return parse_tabular_csv(filepath), []
        elif suffix == '.epub':
            try:
                epub_texts = []
                with zipfile.ZipFile(filepath, 'r') as z:
                    for name in z.namelist():
                        if name.endswith(('.html', '.xhtml', '.xml', '.htm')):
                            raw = z.read(name).decode('utf-8', errors='ignore')
                            clean_text = RE_HTML_TAGS.sub(' ', raw)
                            clean_text = RE_WHITESPACE_COLLAPSE.sub(' ', clean_text).strip()
                            if len(clean_text) > 30:
                                epub_texts.append(clean_text)
                return "\n\n".join(epub_texts), []
            except Exception as e:
                return f"[EPUB Extraction Error: {str(e)}]", []
        elif suffix == '.pdf':
            try:
                # Primary high-performance engine: PyMuPDF (fitz)
                try:
                    import fitz
                    doc = fitz.open(filepath)
                    page_texts = [page.get_text() for page in doc]
                    extracted = "\n".join(page_texts)
                    doc.close()
                    if len(extracted.strip()) >= 50:
                        return extracted, []
                except Exception:
                    pass

                # Fallback engine: pypdf
                reader = pypdf.PdfReader(filepath)
                page_texts = []
                for page in reader.pages:
                    try:
                        txt = page.extract_text() or ""
                        page_texts.append(txt)
                    except Exception:
                        pass
                extracted = "\n".join(page_texts)
                if len(extracted.strip()) < 50:
                    ocr_res, ocr_coords = extract_pdf_ocr(filepath)
                    if ocr_res and ocr_res.strip():
                        return ocr_res, ocr_coords
                    return f"[Parsing Error: Unreadable PDF content]", []
                return extracted, []
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in parsers.py: {e}")
                return f"[Parsing Error: {str(e)}]", []
        elif suffix == '.docx':
            try:
                doc = docx.Document(filepath)
                return "\n".join([para.text for para in doc.paragraphs]), []
            except Exception as e:
                return f"[DOCX Parsing Error: {str(e)}]", []
        elif suffix == '.rtf':
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return rtf_to_text(f.read()), []
            except Exception as e:
                return f"[RTF Parsing Error: {str(e)}]", []
        elif suffix == '.xlsx':
            try:
                wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
                text_lines = []
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows(values_only=True):
                        row_str = " ".join([str(v) for v in row if v is not None])
                        if row_str.strip():
                            text_lines.append(row_str)
                try:
                    wb.close()
                except Exception:
                    pass
                return "\n".join(text_lines), []
            except Exception as e:
                return f"[XLSX Parsing Error: {str(e)}]", []
        elif suffix in ['.png', '.jpg', '.jpeg', '.bmp']:
            return extract_ocr_text_structured(filepath)
        elif suffix in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
            meta = parse_audio_metadata(filepath)
            dur = meta.get("duration", 0.0)
            ch = meta.get("channels", 0)
            sr = meta.get("samplerate", 0)
            transcript = ""
            if dur > 0 and sr > 0:
                try:
                    # ponytail: safe import guard for whisper/torch DLL loads on valid audio headers
                    import whisper
                    model = whisper.load_model("tiny")
                    res = model.transcribe(filepath)
                    transcript = res.get("text", "").strip()
                except (Exception, BaseException, OSError, AttributeError):
                    pass
            
            header = f"[Audio Voice Memo | Duration: {dur}s | Channels: {ch} | SampleRate: {sr} Hz]"
            content_str = f"{header}\n{transcript}" if transcript else header
            return content_str, []
        elif suffix == '.zip':
            import zipfile
            with zipfile.ZipFile(filepath, 'r') as z:
                file_list = z.namelist()
                return "Zip Contents:\n" + "\n".join(file_list), []
        else:
            raw_bytes = safe_read_file(filepath)[:1024 * 1024]
            for enc in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'utf-16'):
                try:
                    return raw_bytes.decode(enc), []
                except (UnicodeDecodeError, UnicodeError):
                    continue

            strings = RE_PRINTABLE_BYTES.findall(raw_bytes[:1024 * 512])
            decoded = " ".join([s.decode('ascii') for s in strings])
            return f"[Extracted Binary Strings]\n{decoded}", []
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in parsers.py: {e}")
        return f"[Parsing Error: {str(e)}]", []


def extract_raptor_hierarchical_summaries(text: str, filename: str = "") -> Dict[str, Any]:
    """Generates 3-tier semantic cluster and executive abstraction tree for document text."""
    try:
        from src.domain.raptor_tree_indexer import build_raptor_tree
        from src.core.domain.services import chunk_text
        raw_chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
        chunks = [{"text": c, "source": filename} for c in raw_chunks]
        if len(chunks) < 2:
            return {"status": "skipped", "reason": "insufficient_chunks"}
        return build_raptor_tree(chunks)
    except Exception as e:
        return {"status": "error", "message": str(e)}
