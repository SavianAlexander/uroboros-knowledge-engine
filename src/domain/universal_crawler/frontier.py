from urllib.parse import urlparse
from typing import List, Optional, Set
from src.domain.universal_crawler.models import CrawlConfig

"""
URL Frontier & Domain Policy Filter for Universal Crawler.
Controls crawl boundaries, domain containment, file extensions, and priority assignment.
"""

class UrlFrontier:
    """Manages URL filtering, depth checks, and priority calculation."""

    @staticmethod
    def extract_domain(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    @classmethod
    def is_allowed_domain(cls, url: str, allowed_domains: List[str]) -> bool:
        """Check if URL belongs to configured domains (or subdomain)."""
        if not allowed_domains:
            return True  # If no explicit domain restrictions, allow all
        url_domain = cls.extract_domain(url)
        for d in allowed_domains:
            clean_d = d.strip().lower()
            if url_domain == clean_d or url_domain.endswith(f".{clean_d}"):
                return True
        return False

    @staticmethod
    def is_target_file_asset(url: str, extensions: List[str]) -> bool:
        """Check if URL points to a downloadable file asset (e.g. .pdf, .docx)."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in extensions:
            if path.endswith(ext.lower()):
                return True
        return False

    @classmethod
    def should_crawl(cls, url: str, depth: int, config: CrawlConfig, visited_urls: Set[str]) -> bool:
        """Determine if a discovered URL should be enqueued."""
        if not url or url in visited_urls:
            return False
        if depth > config.max_depth:
            return False
        if not cls.is_allowed_domain(url, config.allowed_domains):
            return False
        return True

    @classmethod
    def calculate_priority(cls, url: str, depth: int, is_file: bool = False) -> int:
        """Calculate queue priority (Higher executes earlier)."""
        if is_file:
            return 8  # File downloads prioritized
        if depth == 0:
            return 10 # Seeds top priority
        if any(keyword in url.lower() for keyword in ["sitemap", "index", "leyes", "medidas", "docs", "api"]):
            return 7
        return max(1, 6 - depth)
