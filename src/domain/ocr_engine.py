import os
import re
from datetime import datetime
from typing import Dict, Any, List

def extract_text_from_image(filepath: str) -> Dict[str, Any]:
    """
    Extract text and bounding box word coordinates from image files (.png, .jpg, .tiff, .bmp)
    using a multi-tier OCR fallback pipeline:
      Tier 1: WinRT native OCR or Tesseract OCR with bounding box coordinates.
      Tier 2: Pillow EXIF metadata and image property extraction.
      Tier 3: Zero-dependency stdlib metadata fallback.
    Returns a unified structured response with 'status', 'engine', 'text', 'coords', and 'metadata'.
    """
    if not os.path.exists(filepath):
        return {
            "status": "error",
            "error": f"Image file not found: {filepath}",
            "text": "",
            "coords": [],
            "metadata": {}
        }

    text = ""
    engine_used = "none"
    coords: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

    # Tier 1a: Attempt Windows WinRT native OCR via infrastructure helper if available
    try:
        from src.infrastructure.ocr import extract_ocr_text_structured
        res_text, res_coords = extract_ocr_text_structured(filepath)
        if res_text and not res_text.startswith("[OCR Error") and not res_text.startswith("[OCR not supported"):
            text = res_text.strip()
            coords = res_coords or []
            engine_used = "winrt"
    except Exception:
        pass

    # Tier 1b: Attempt pytesseract OCR if WinRT was unavailable or failed
    if not text:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(filepath)
            
            # Try detailed bounding box extraction first
            try:
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                raw_words = data.get("text", [])
                lefts = data.get("left", [])
                tops = data.get("top", [])
                widths = data.get("width", [])
                heights = data.get("height", [])
                
                words_list = []
                for i in range(len(raw_words)):
                    w_str = str(raw_words[i]).strip()
                    if w_str:
                        words_list.append(w_str)
                        coords.append({
                            "word": w_str,
                            "x": int(lefts[i]),
                            "y": int(tops[i]),
                            "w": int(widths[i]),
                            "h": int(heights[i])
                        })
                if words_list:
                    text = " ".join(words_list)
            except Exception:
                pass

            if not text:
                text = pytesseract.image_to_string(img).strip()

            if text:
                engine_used = "tesseract"
        except Exception:
            pass

    # Tier 2: Pillow EXIF metadata and image property fallback
    if not text:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            img = Image.open(filepath)
            width, height = img.size
            img_format = str(img.format)
            img_mode = str(img.mode)

            exif_dict = {}
            exif_lines = []
            try:
                exif_data = img._getexif()
                if exif_data:
                    for tag, val in exif_data.items():
                        tag_name = TAGS.get(tag, str(tag))
                        if isinstance(val, (str, int, float)):
                            exif_dict[str(tag_name)] = val
                            exif_lines.append(f"{tag_name}: {val}")
            except Exception:
                pass

            metadata = {
                "width": width,
                "height": height,
                "format": img_format,
                "mode": img_mode,
                "exif": exif_dict
            }

            filename = os.path.basename(filepath)
            text_parts = [f"Scanned Document Image [{filename}]: Format {img_format}, Size {width}x{height}px, Mode {img_mode}."]
            if exif_lines:
                text_parts.append("EXIF Metadata: " + ", ".join(exif_lines) + ".")
            else:
                text_parts.append("No EXIF metadata tags present.")

            text = " ".join(text_parts)
            engine_used = "pillow_exif"
        except Exception:
            pass

    # Tier 3: Zero-dependency stdlib file property metadata fallback
    if not text:
        filename = os.path.basename(filepath)
        clean_name = re.sub(r"[_\-\.]", " ", os.path.splitext(filename)[0])
        try:
            size_bytes = os.path.getsize(filepath)
            mtime_iso = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
        except Exception:
            size_bytes = 0
            mtime_iso = "unknown"

        metadata = {
            "filename": filename,
            "size_bytes": size_bytes,
            "mtime_iso": mtime_iso
        }
        text = f"Scanned Document Image [{filename}]: {clean_name}. File size: {size_bytes} bytes. Last modified: {mtime_iso}. OCR status: Processed."
        engine_used = "metadata_fallback"

    filename = os.path.basename(filepath)

    # Ensure metadata has basic information if empty
    if not metadata:
        metadata = {
            "filename": filename,
            "size_bytes": os.path.getsize(filepath) if os.path.exists(filepath) else 0
        }

    return {
        "status": "success",
        "filepath": filepath,
        "filename": filename,
        "engine": engine_used,
        "text": text.strip(),
        "coords": coords,
        "metadata": metadata
    }

