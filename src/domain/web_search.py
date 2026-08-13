"""
Zero-dependency Web Search Fetcher using Python standard library modules only.
Provides WebSearchFetcher class and fetch_web_context function.
"""
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional

class HTMLSnippetParser(HTMLParser):
    """Simple HTML tag stripper for web search snippet text parsing."""
    def __init__(self):
        super().__init__()
        self.text_chunks: List[str] = []

    def handle_data(self, data: str):
        cleaned = data.strip()
        if cleaned:
            self.text_chunks.append(cleaned)

    def get_text(self) -> str:
        return " ".join(self.text_chunks)

def strip_html_tags(html_str: str) -> str:
    """Strips HTML tags from text string using standard library HTMLParser."""
    if not html_str:
        return ""
    parser = HTMLSnippetParser()
    try:
        parser.feed(html_str)
        return parser.get_text()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in web_search.py")
        return html_str

def fetch_web_context(query: str, max_results: int = 3, timeout: float = 4.0) -> List[Dict[str, Any]]:
    """
    Fetches external web context snippets with title, url, snippet using standard library only.
    Handles network errors, socket timeouts, and offline mode gracefully by returning [].
    """
    if not query or not str(query).strip():
        return []

    raw_query = str(query).strip()
    encoded_query = urllib.parse.quote_plus(raw_query)
    api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&no_redirect=1"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UroborosEngine/2.0"}

    results: List[Dict[str, Any]] = []

    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                raw_payload = response.read().decode('utf-8', errors='ignore')
                try:
                    data = json.loads(raw_payload) if raw_payload else {}
                except (json.JSONDecodeError, ValueError):
                    data = {}

                abstract = data.get("AbstractText", "").strip()
                heading = data.get("Heading", "").strip() or raw_query
                abstract_url = data.get("AbstractURL", "").strip()

                if abstract:
                    results.append({
                        "title": heading,
                        "url": abstract_url or f"https://duckduckgo.com/?q={encoded_query}",
                        "snippet": abstract,
                        "source": "web"
                    })

                related_topics = data.get("RelatedTopics") or []
                for topic in related_topics:
                    if len(results) >= max_results:
                        break
                    if isinstance(topic, dict):
                        text = topic.get("Text", "").strip()
                        first_url = topic.get("FirstURL", "").strip()
                        if text:
                            results.append({
                                "title": text[:60] + ("..." if len(text) > 60 else ""),
                                "url": first_url or f"https://duckduckgo.com/?q={encoded_query}",
                                "snippet": text,
                                "source": "web"
                            })
    except Exception:
        # Silently catch network errors, socket timeouts, connection failures, offline mode
        import logging; logging.getLogger(__name__).exception("Swallowed error in web_search.py")
        return []

    return results[:max_results]

class WebSearchFetcher:
    """Zero-dependency web search fetcher using standard library modules only."""

    @staticmethod
    def search(query: str, max_results: int = 3, timeout: float = 4.0) -> List[Dict[str, Any]]:
        return fetch_web_context(query, max_results=max_results, timeout=timeout)

    @staticmethod
    def fetch(query: str, max_results: int = 3, timeout: float = 4.0) -> List[Dict[str, Any]]:
        return fetch_web_context(query, max_results=max_results, timeout=timeout)
