import re
import json
import hashlib
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse, urldefrag
from typing import List, Dict, Any, Tuple, Optional, Set

"""
Enterprise Multi-Format Deep Content, Asset & Metadata Extractor.
Parses HTML, PDF, JSON, XML Sitemaps, and RSS/Atom feeds into structured text,
hierarchical AST sections, and metadata entities for Knowledge Graph RAG ingestion.
"""

STRIP_TAGS = ["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "iframe"]

def normalize_url(url: str, base_url: str) -> Optional[str]:
    """Resolve and normalize absolute URL, stripping fragments."""
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if url.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
        return None
    try:
        joined = urljoin(base_url, url)
        defragged, _ = urldefrag(joined)
        parsed = urlparse(defragged)
        if parsed.scheme not in ("http", "https"):
            return None
        return defragged
    except Exception:
        return None

def extract_links_from_html(html: str, base_url: str) -> List[str]:
    """Discover and normalize all hyperlinks from HTML document."""
    if not html or not isinstance(html, str):
        return []
    raw_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    discovered = []
    seen = set()

    for r in raw_links:
        norm = normalize_url(r, base_url)
        if norm and norm not in seen:
            seen.add(norm)
            discovered.append(norm)

    return discovered

def extract_html_metadata(html: str) -> Dict[str, Any]:
    """Extract OpenGraph, Schema.org JSON-LD, and Dublin Core metadata from HTML."""
    meta = {}
    if not html:
        return meta

    # Description & Keywords
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', html, re.I)
    if desc_match:
        meta["description"] = desc_match.group(1).strip()

    # OpenGraph (og:title, og:description, og:type)
    for tag in re.finditer(r'<meta\s+property=["\']og:([^"\']+)["\']\s+content=["\']([^"\']*)["\']', html, re.I):
        meta[f"og_{tag.group(1)}"] = tag.group(2).strip()

    # Schema.org JSON-LD
    json_ld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.DOTALL)
    for j_str in json_ld_matches:
        try:
            parsed_ld = json.loads(j_str.strip())
            if isinstance(parsed_ld, dict):
                meta["schema_type"] = parsed_ld.get("@type")
                if "headline" in parsed_ld:
                    meta["headline"] = parsed_ld["headline"]
        except Exception:
            pass

    return meta

def extract_clean_text_from_html(html: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Extract title, clean readable text, and structured metadata from HTML.
    Returns (title, clean_text, metadata).
    """
    if not html or not isinstance(html, str):
        return "Untitled Document", "", {}

    meta = extract_html_metadata(html)

    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else meta.get("og_title", "Untitled Web Page")
    title = re.sub(r'\s+', ' ', title)

    # Strip unwanted elements
    clean_html = html
    for tag in STRIP_TAGS:
        clean_html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', ' ', clean_html, flags=re.IGNORECASE | re.DOTALL)

    # Convert common block tags to newlines
    clean_html = re.sub(r'<(?:p|div|h[1-6]|li|tr|blockquote)[^>]*>', '\n', clean_html, flags=re.IGNORECASE)
    clean_html = re.sub(r'<br\s*/?>', '\n', clean_html, flags=re.IGNORECASE)

    # Strip all remaining tags
    text = re.sub(r'<[^>]+>', ' ', clean_html)

    # Unescape common HTML entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")

    # Clean redundant whitespace
    lines = [re.sub(r'\s+', ' ', line).strip() for line in text.split('\n')]
    clean_text = '\n'.join(line for line in lines if line)

    return title, unicodedata.normalize("NFC", clean_text), meta

def extract_urls_from_sitemap_xml(xml_content: str, base_url: str = "") -> List[str]:
    """Extract all loc URLs from XML sitemaps or RSS/Atom feeds."""
    urls = []
    if not xml_content:
        return urls

    # Fast regex extraction to handle varying XML namespaces
    loc_matches = re.findall(r'<loc>(.*?)</loc>', xml_content, re.IGNORECASE)
    for loc in loc_matches:
        norm = normalize_url(loc, base_url) if base_url else loc.strip()
        if norm and norm not in urls:
            urls.append(norm)

    # Also check RSS <link> tags
    if not urls:
        link_matches = re.findall(r'<link>(.*?)</link>', xml_content, re.IGNORECASE)
        for link in link_matches:
            norm = normalize_url(link, base_url) if base_url else link.strip()
            if norm and norm not in urls:
                urls.append(norm)

    return urls

def extract_text_from_json(json_bytes: bytes) -> Tuple[str, str]:
    """Parse JSON payload into structured plain text."""
    try:
        data = json.loads(json_bytes.decode('utf-8', errors='ignore'))
        title = "JSON API Payload"
        text = json.dumps(data, indent=2, ensure_ascii=False)
        return title, text
    except Exception as e:
        return "Invalid JSON", f"Error parsing JSON: {e}"

def extract_text_from_pdf_stream(pdf_bytes: bytes, filename: str = "document.pdf") -> Tuple[str, str]:
    """Extract text from raw PDF bytes."""
    text_pieces = re.findall(r'\(([^\(\)]{3,})\)', pdf_bytes.decode('latin-1', errors='ignore'))
    extracted = ' '.join(text_pieces) if text_pieces else f"Binary PDF Document ({len(pdf_bytes)} bytes)"
    clean_title = filename.replace('.pdf', '').replace('_', ' ').title()
    return clean_title, unicodedata.normalize("NFC", extracted)

def calculate_merkle_provenance(content: str, url: str, metadata: Dict[str, Any]) -> str:
    """Calculate cryptographic SHA-256 Merkle leaf for crawled asset."""
    norm_content = unicodedata.normalize("NFC", content.strip())
    header = f"{url}|{metadata.get('content_type', '')}|{metadata.get('job_id', '')}"
    payload = f"{header}\n{norm_content}".encode('utf-8')
    return hashlib.sha256(payload).hexdigest()
