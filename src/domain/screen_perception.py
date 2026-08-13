"""
Real-Time Screen Perception & Ambient Workspace Awareness Engine.
Extracts active screen OCR text and editor layout context for zero-cloud RAG perception.
"""
import unicodedata
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def capture_screen_context(sample_ocr: bool = True) -> Dict[str, Any]:
    """
    Captures ambient screen context and OCR text for workspace perception.
    Includes zero-dependency fallback for headless / background execution environments.
    # ponytail: lightweight fallback for non-GUI / headless execution environments; ceiling: PIL ImageGrab + pytesseract desktop capture; upgrade: bind WinRT GraphicsCapture API if 60fps real-time screen perception stream is needed
    """
    now = datetime.now(timezone.utc).isoformat()
    try:
        from PIL import ImageGrab
        import pytesseract

        screenshot = ImageGrab.grab()
        if sample_ocr:
            ocr_text = pytesseract.image_to_string(screenshot)
        else:
            ocr_text = ""
        norm_ocr = unicodedata.normalize("NFC", ocr_text) if ocr_text else ""
        return {
            "status": "active",
            "timestamp": now,
            "resolution": f"{screenshot.width}x{screenshot.height}",
            "ocr_text_snippet": norm_ocr[:500] if norm_ocr else "",
            "has_active_display": True
        }
    except Exception as e:
        return {
            "status": "fallback",
            "timestamp": now,
            "resolution": "headless",
            "ocr_text_snippet": "",
            "has_active_display": False,
            "info": str(e)
        }
