"""
Domain test suite for Extended Local OCR & Audio Transcription Engines.
Validates multi-tier OCR fallback (WinRT/Tesseract -> EXIF -> Metadata), word bounding coordinates,
WAV audio decoding, MP3 frame header parsing, 10-second timestamp chunking, and RMS energy calculation.
"""

import os
import sys
import math
import wave
import struct
import shutil
import tempfile
import unittest

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.domain.ocr_engine import extract_text_from_image
from src.domain.transcription_engine import transcribe_audio_memo, format_timestamp

class TestDomainOCRTranscription(unittest.TestCase):
    """Contract test suite for OCR and Audio Transcription domain engines."""

    def setUp(self):
        """Create an isolated temporary working directory for test fixtures."""
        self.temp_dir = tempfile.mkdtemp(prefix="test_ocr_transcription_")

    def tearDown(self):
        """Clean up temporary test artifacts."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_ocr_non_existent_file_handling(self):
        """Verify extract_text_from_image returns structured error response on missing files."""
        missing_path = os.path.join(self.temp_dir, "missing_image.png")
        res = extract_text_from_image(missing_path)

        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("error", res)
        self.assertEqual(res.get("text"), "")
        self.assertEqual(res.get("coords"), [])

    def test_02_ocr_image_extraction_and_coords(self):
        """Verify extract_text_from_image produces valid status, engine, text, coords, and metadata."""
        test_img_path = os.path.join(self.temp_dir, "sample_doc.png")

        try:
            from PIL import Image
            img = Image.new("RGB", (200, 100), color=(255, 255, 255))
            img.save(test_img_path)
        except Exception:
            with open(test_img_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

        res = extract_text_from_image(test_img_path)

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("filepath"), test_img_path)
        self.assertEqual(res.get("filename"), "sample_doc.png")
        self.assertIn(res.get("engine"), ["tesseract", "winrt", "pillow_exif", "metadata_fallback"])
        self.assertIsInstance(res.get("text"), str)
        self.assertGreater(len(res.get("text", "")), 0)
        self.assertIsInstance(res.get("coords"), list)
        self.assertIsInstance(res.get("metadata"), dict)

    def test_03_ocr_pillow_exif_and_metadata_fallback(self):
        """Verify fallback tiers extract image properties and stdlib metadata when OCR yields no text."""
        blank_img_path = os.path.join(self.temp_dir, "blank_image.png")
        try:
            from PIL import Image
            img = Image.new("RGB", (300, 200), color=(0, 0, 0))
            img.save(blank_img_path)
        except Exception:
            with open(blank_img_path, "wb") as f:
                f.write(b"NOT_A_VALID_IMAGE_HEADER_BYTES_12345")

        from unittest.mock import patch
        with patch("src.infrastructure.ocr.extract_ocr_text_structured", return_value=("", [])):
            res = extract_text_from_image(blank_img_path)

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("engine"), "pillow_exif")
        self.assertIn("blank_image.png", res.get("text", ""))
        self.assertEqual(res.get("coords"), [])
        self.assertIn("format", res.get("metadata", {}))


    def test_03b_ocr_stdlib_metadata_fallback(self):
        """Verify Tier 3 stdlib metadata fallback when WinRT and PIL fail or are unavailable."""
        corrupt_file = os.path.join(self.temp_dir, "corrupt_image.png")
        with open(corrupt_file, "wb") as f:
            f.write(b"CORRUPT_BYTES_98765")

        from unittest.mock import patch
        with patch("src.infrastructure.ocr.extract_ocr_text_structured", return_value=("", [])):
            with patch("PIL.Image.open", side_effect=Exception("PIL open error")):
                res = extract_text_from_image(corrupt_file)

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("engine"), "metadata_fallback")
        self.assertIn("corrupt_image.png", res.get("text", ""))
        self.assertEqual(res.get("coords"), [])
        self.assertIn("size_bytes", res.get("metadata", {}))



    def test_04_transcription_non_existent_file(self):
        """Verify transcribe_audio_memo handles missing files with structured error output."""
        missing_audio = os.path.join(self.temp_dir, "non_existent_memo.wav")
        res = transcribe_audio_memo(missing_audio)

        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("File not found", res.get("error", ""))
        self.assertEqual(res.get("transcript"), "")
        self.assertEqual(res.get("chunks"), [])

    def test_05_transcription_wav_chunking_and_energy(self):
        """Verify WAV audio processing generates 10-second timestamped chunks and RMS energy level."""
        wav_path = os.path.join(self.temp_dir, "test_audio_15s.wav")
        sample_rate = 16000
        duration_sec = 15.0
        num_frames = int(sample_rate * duration_sec)

        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            # Generate synthetic 440Hz sine wave tone
            raw_samples = []
            for i in range(num_frames):
                val = int(8000.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
                raw_samples.append(val)

            packed = struct.pack(f"<{num_frames}h", *raw_samples)
            wf.writeframes(packed)

        res = transcribe_audio_memo(wav_path, chunk_duration_sec=10.0)

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("format"), "wav")
        self.assertEqual(res.get("sample_rate"), 16000)
        self.assertEqual(res.get("channels"), 1)
        self.assertAlmostEqual(res.get("duration_seconds", 0.0), 15.0, delta=0.5)

        chunks = res.get("chunks", [])
        self.assertEqual(len(chunks), 2)

        # Chunk 1: [00:00 - 00:10]
        self.assertEqual(chunks[0]["chunk_index"], 1)
        self.assertEqual(chunks[0]["timestamp"], "[00:00 - 00:10]")
        self.assertGreater(chunks[0]["energy"], 1000.0)

        # Chunk 2: [00:10 - 00:15]
        self.assertEqual(chunks[1]["chunk_index"], 2)
        self.assertEqual(chunks[1]["timestamp"], "[00:10 - 00:15]")
        self.assertGreater(chunks[1]["energy"], 1000.0)

        self.assertIn("[00:00 - 00:10]", res.get("transcript", ""))
        self.assertIn("[00:10 - 00:15]", res.get("transcript", ""))
        self.assertGreater(res.get("avg_energy", 0.0), 1000.0)

    def test_06_transcription_mp3_frame_header_parsing(self):
        """Verify MP3 frame header parsing and chunking with timestamp markers."""
        mp3_path = os.path.join(self.temp_dir, "test_voice_memo.mp3")

        # Generate synthetic valid MP3 frames (MPEG-1 Layer III, 128 kbps, 44100 Hz, stereo)
        # Frame sync: 0xFF, 0xFB (1111 1111 1111 1011 -> MPEG-1, Layer III, no CRC)
        # Bitrate 128kbps (index 9), Sample rate 44100Hz (index 0) -> header bytes: 0xFF, 0xFB, 0x90, 0x64
        # Frame size = 144 * 128000 / 44100 = 417 bytes. Frame duration = 1152 / 44100 ~ 0.02612 sec.
        frame_header = bytes([0xFF, 0xFB, 0x90, 0x64])
        frame_size = 417
        payload = b"\x55" * (frame_size - 4)
        single_frame = frame_header + payload

        # Create ~12 seconds of MP3 audio frames (~460 frames)
        num_mp3_frames = 460
        with open(mp3_path, "wb") as f:
            for _ in range(num_mp3_frames):
                f.write(single_frame)

        res = transcribe_audio_memo(mp3_path, chunk_duration_sec=10.0)

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("format"), "mp3")
        self.assertEqual(res.get("sample_rate"), 44100)
        self.assertEqual(res.get("channels"), 2)
        self.assertGreater(res.get("duration_seconds", 0.0), 10.0)

        chunks = res.get("chunks", [])
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["timestamp"], "[00:00 - 00:10]")
        self.assertIn("[00:00 - 00:10]", res.get("transcript", ""))

    def test_07_transcription_corrupt_unknown_audio(self):
        """Verify corrupt/unknown audio file processing returns safe non-crashing response."""
        corrupt_path = os.path.join(self.temp_dir, "corrupt_file.unknown")
        with open(corrupt_path, "wb") as f:
            f.write(b"CORRUPT_AUDIO_HEADER_BYTES_12345")

        res = transcribe_audio_memo(corrupt_path)

        self.assertEqual(res.get("status"), "success")
        self.assertIn("filepath", res)
        self.assertIn("transcript", res)
        self.assertEqual(res.get("duration_seconds"), 0.0)

    def test_08_timestamp_formatter_utility(self):
        """Verify format_timestamp correctly converts seconds to MM:SS string."""
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(5.4), "00:05")
        self.assertEqual(format_timestamp(65), "01:05")
        self.assertEqual(format_timestamp(3599), "59:59")

if __name__ == "__main__":
    unittest.main()
