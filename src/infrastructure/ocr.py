"""
Windows WinRT OCR and pytesseract / EXIF fallback text extraction.
"""
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

# Windows Native OCR setup (WinRT)
HAS_WINRT = False
try:
    if os.name == 'nt':
        from winrt.windows.storage import StorageFile
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.graphics.imaging import BitmapDecoder
        HAS_WINRT = True
except ImportError:
    HAS_WINRT = False

async def _async_ocr_structured(filepath):
    if not HAS_WINRT:
        return "[OCR not supported on this platform]", []
    try:
        abs_path = os.path.abspath(filepath)
        file = await StorageFile.get_file_from_path_async(abs_path)
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = OcrEngine.try_create_from_user_profile_languages()
        if not engine:
            return "[OCR Error: Failed to create WinRT OcrEngine]", []
        result = await engine.recognize_async(bitmap)

        coords = []
        for line in result.lines:
            for word in line.words:
                rect = word.bounding_rect
                coords.append({
                    "word": word.text,
                    "x": rect.x,
                    "y": rect.y,
                    "w": rect.width,
                    "h": rect.height
                })
        return result.text, coords
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.debug(f"WinRT OCR failed for {filepath}: {e}")
        return f"[OCR Error: {str(e)}]", []

def extract_ocr_text_structured(filepath):
    """Extract OCR text and word bounding box coordinates."""
    abs_path = os.path.abspath(filepath)
    if HAS_WINRT:
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)


            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    def _run_in_thread():
                        new_loop = asyncio.new_event_loop()
                        try:
                            return new_loop.run_until_complete(_async_ocr_structured(abs_path))
                        finally:
                            new_loop.close()
                    res_text, res_coords = pool.submit(_run_in_thread).result()
            else:
                res_text, res_coords = loop.run_until_complete(_async_ocr_structured(abs_path))

            if res_text and not res_text.startswith("[OCR Error"):
                return res_text, res_coords
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.debug(f"Error in WinRT OCR structured: {e}")

    # Try pytesseract OCR fallback
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(abs_path)
        text = pytesseract.image_to_string(img)
        if text.strip():
            return text.strip(), []
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except BaseException as e:
        logger.debug(f"pytesseract OCR fallback unavailable: {e}")

    # Try EXIF / Metadata extraction fallback
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(filepath)
        exif_data = img._getexif()
        metadata = []
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if isinstance(value, (str, int, float)):
                    metadata.append(f"{tag_name}: {value}")

        metadata.append(f"Format: {img.format}")
        metadata.append(f"Size: {img.size[0]}x{img.size[1]} px")
        metadata.append(f"Mode: {img.mode}")

        return f"[OCR Fallback - Image Metadata Extraction]\n" + "\n".join(metadata), []
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.debug("Image EXIF parsing fallback notice in ocr.py: %s", e)
        return f"[Image Parsing Error: {str(e)}]", []

def extract_pdf_ocr(filepath):
    """Extract OCR text from scanned PDF pages."""
    try:
        import fitz
        doc = fitz.open(filepath)
        text_parts = []
        all_coords = []
        for page in list(doc)[:10]:
            try:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")

                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    temp_path = f.name
                    f.write(img_bytes)

                try:
                    page_text, page_coords = extract_ocr_text_structured(temp_path)
                    if page_text and not page_text.startswith("[OCR Error") and not page_text.startswith("[OCR Setup"):
                        text_parts.append(page_text)
                        all_coords.extend(page_coords)
                finally:
                    try:
                        os.unlink(temp_path)
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception as e:
                        logger.debug(f"Error unlinking temp file: {e}")
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                logger.debug(f"Error processing PDF page: {e}")
        return "\n\n".join(text_parts), all_coords
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.debug(f"Scanned PDF OCR Error: {e}")
        return f"[Scanned PDF OCR Error: {str(e)}]", []
