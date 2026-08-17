"""
Universal Long-Form Document, Email & Briefing Audio Reader Engine.
Standard: Pure Python Standard Library (re, os, sys).
Ponytail Senior Dev Principle: Strips email boilerplates, quoted chains, tracking URLs, disclaimers, and footers into a crystal-clean, natural executive voice briefing.
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_normalizer import VoiceNormalizer


class DocumentVoiceReader:
    """Cleans and structures emails, markdown articles, and executive memos for voice narration."""

    DISCLAIMER_PATTERNS = [
        re.compile(r"this message (and any attachments )?is intended (only|solely) for.*", re.IGNORECASE),
        re.compile(r"confidentiality notice:.*", re.IGNORECASE),
        re.compile(r"if you are not the intended recipient.*", re.IGNORECASE),
        re.compile(r"click here to unsubscribe.*", re.IGNORECASE),
        re.compile(r"sent from my i(phone|pad).*", re.IGNORECASE),
        re.compile(r"get outlook for (ios|android).*", re.IGNORECASE),
    ]

    @classmethod
    def clean_email_for_speech(cls, raw_email: str) -> Dict[str, Any]:
        """
        Extract email headers (From, Subject, Date) and clean body into executive speech.
        """
        if not raw_email or not raw_email.strip():
            return {
                "sender": "Unknown Sender",
                "subject": "No Subject",
                "speech_text": "Empty email message."
            }

        lines = raw_email.splitlines()
        sender = "Unknown Sender"
        subject = "No Subject"
        date_str = ""
        body_lines = []
        in_headers = True

        for line in lines:
            if in_headers:
                m_from = re.match(r"^(From|Sender):\s*(.*)", line, re.IGNORECASE)
                if m_from:
                    # Clean display name from angle brackets
                    sender_raw = m_from.group(2).strip()
                    sender = re.sub(r"<.*?>", "", sender_raw).strip().strip('"\'') or sender_raw
                    continue

                m_subj = re.match(r"^(Subject):\s*(.*)", line, re.IGNORECASE)
                if m_subj:
                    subject = m_subj.group(2).strip()
                    continue

                m_date = re.match(r"^(Date):\s*(.*)", line, re.IGNORECASE)
                if m_date:
                    date_str = m_date.group(2).strip()
                    continue

                if not line.strip():
                    in_headers = False
                    continue
            else:
                body_lines.append(line)

        # If no RFC headers were detected, treat the whole text as body
        if not body_lines and in_headers:
            body_lines = lines

        # Clean body
        clean_body = cls._clean_body_content(body_lines)

        intro = f"Email from {sender}. Subject: {subject}."
        full_speech = f"{intro} {clean_body}".strip()
        normalized_speech = VoiceNormalizer.normalize_for_speech(full_speech)

        return {
            "sender": sender,
            "subject": subject,
            "date": date_str,
            "speech_text": normalized_speech,
            "word_count": len(normalized_speech.split())
        }

    @classmethod
    def _clean_body_content(cls, lines: List[str]) -> str:
        """Filter out quoted replies, disclaimers, and tracking links."""
        filtered = []
        for line in lines:
            stripped = line.strip()

            # Skip quoted lines (e.g. > On Fri, Aug 14...)
            if stripped.startswith(">") or stripped.startswith("|"):
                continue

            # Skip reply header line (e.g. On Aug 14, 2026, John Doe wrote:)
            if re.match(r"^On\s+.*wrote:\s*$", stripped, re.IGNORECASE):
                continue

            # Skip confidentiality notices & footers
            if any(p.search(stripped) for p in cls.DISCLAIMER_PATTERNS):
                break

            # Strip raw URLs to clean phrase
            line_no_urls = re.sub(r"https?://\S+", "link", stripped)

            # Strip email addresses
            line_clean = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "", line_no_urls)

            if line_clean.strip():
                filtered.append(line_clean.strip())

        return " ".join(filtered)
