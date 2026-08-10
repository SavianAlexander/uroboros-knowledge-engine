"""
Document parsing and content extraction modules (PDF, DOCX, RTF, XLSX, Audio, Images, Binary).
"""

import os
import re
import time
import hashlib
import functools
import wave
from typing import Tuple, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

import pypdf
import docx
from striprtf.striprtf import rtf_to_text
import openpyxl

from src.infrastructure.ocr import extract_ocr_text_structured, extract_pdf_ocr

RE_PRINTABLE_BYTES = re.compile(b'[\x20-\x7E]{4,}')

def calculate_sha256(filepath: str) -> Optional[str]:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
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
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in parsers.py: {e}")
        logger.warning(f"Error parsing audio metadata for {filepath}: {e}")
        return {"duration": 0.0, "channels": 0, "samplerate": 0, "bitrate": "0 kbps"}

def extract_content(filepath: str, suffix: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text content and coordinates based on file extension/type."""
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > 50 * 1024 * 1024:
            return f"[File Size Exceeds 50MB - Extraction Skipped: {os.path.basename(filepath)}]", []
        if suffix == '.pdf':
            try:
                reader = pypdf.PdfReader(filepath)
                extracted = "\n".join([page.extract_text() or "" for page in reader.pages])
                if len(extracted.strip()) < 50:
                    ocr_res, ocr_coords = extract_pdf_ocr(filepath)
                    if ocr_res and ocr_res.strip():
                        return ocr_res, ocr_coords
                    return f"[Parsing Error: Unreadable PDF content]", []
                return extracted, []
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in parsers.py: {e}")
                return f"[Parsing Error: {str(e)}]", []
        elif suffix == '.docx':
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs]), []
        elif suffix == '.rtf':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return rtf_to_text(f.read()), []
        elif suffix == '.xlsx':
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            text_lines = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_str = " ".join([str(v) for v in row if v is not None])
                    if row_str.strip():
                        text_lines.append(row_str)
            return "\n".join(text_lines), []
        elif suffix in ['.png', '.jpg', '.jpeg', '.bmp']:
            return extract_ocr_text_structured(filepath)
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
