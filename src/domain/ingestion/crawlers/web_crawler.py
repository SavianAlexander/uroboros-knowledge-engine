"""
Production Asynchronous Web Ingestion Engine.
Primary Engine: crawl4ai (AsyncWebCrawler with CrawlerRunConfig for clean Markdown extraction).
Resilient Fallback: Async HTTPX + HTML-to-Markdown cleaner.
"""

import os
import sys
import re
import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Safe Import Guard for Crawl4AI
HAS_CRAWL4AI = False
try:
    import crawl4ai
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    HAS_CRAWL4AI = True
except (ImportError, Exception) as e:
    HAS_CRAWL4AI = False
    logger.info("Crawl4AI library not available, using built-in asynchronous HTTPX crawler fallback: %s", e)


class ProductionWebCrawler:
    """
    Production-grade asynchronous web crawler converting live web pages into LLM-ready clean Markdown.
    Strips navigation menus, scripts, advertisements, and modal overlays.
    """

    @staticmethod
    def is_crawl4ai_available() -> bool:
        """Checks if crawl4ai engine is available."""
        return HAS_CRAWL4AI

    @staticmethod
    async def crawl_url(
        url: str,
        word_count_threshold: int = 10,
        remove_overlay_elements: bool = True,
        timeout_seconds: float = 15.0
    ) -> Dict[str, Any]:
        """
        Asynchronously fetches and converts a web page into structured Markdown.
        
        Args:
            url: HTTP/HTTPS web address to crawl.
            word_count_threshold: Minimum word threshold to discard noise blocks.
            remove_overlay_elements: Whether to remove popups and cookie banners.
            timeout_seconds: Request timeout in seconds.
            
        Returns:
            Dictionary containing 'markdown', 'title', 'url', 'status_code', 'engine', and 'links'.
        """
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL supplied: '{url}'")

        # 1. Primary Engine: crawl4ai AsyncWebCrawler
        if HAS_CRAWL4AI:
            try:
                run_cfg = CrawlerRunConfig(
                    word_count_threshold=word_count_threshold,
                    remove_overlay_elements=remove_overlay_elements,
                    exclude_external_links=False
                )
                async with AsyncWebCrawler() as crawler:
                    res = await crawler.arun(url=url, config=run_cfg)
                    if res.success:
                        return {
                            "markdown": res.markdown or "",
                            "title": getattr(res, "title", parsed.netloc),
                            "url": url,
                            "status_code": getattr(res, "status_code", 200),
                            "engine": "crawl4ai",
                            "links": getattr(res, "links", [])
                        }
            except Exception as e:
                logger.warning("Crawl4AI execution failed for '%s', falling back to async HTTPX parser: %s", url, e)

        # 2. Resilient Fallback Engine: Async HTTPX + HTML2Markdown sanitizer
        return await ProductionWebCrawler._fallback_crawl(url, timeout_seconds=timeout_seconds)

    @staticmethod
    def crawl_url_sync(url: str, **kwargs) -> Dict[str, Any]:
        """Synchronous wrapper for crawl_url."""
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, ProductionWebCrawler.crawl_url(url, **kwargs)).result()
            return asyncio.run(ProductionWebCrawler.crawl_url(url, **kwargs))
        except Exception as e:
            if "invalid" in str(e).lower() or not url.startswith("http"):
                raise ValueError(f"Invalid URL supplied: '{url}'") from e
            raise

    @staticmethod
    async def _fallback_crawl(url: str, timeout_seconds: float = 15.0) -> Dict[str, Any]:
        """
        Async HTTPX crawler with zero-dependency HTML-to-Markdown cleaner.
        """
        import httpx
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 NeuroCrawler/2.0"
        }
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            html_text = resp.text
            status = resp.status_code

        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else urlparse(url).netloc

        # Strip scripts, styles, head, nav, footer, noscript
        cleaned_html = re.sub(r'<(script|style|head|nav|footer|noscript|svg)[^>]*>.*?</\1>', '', html_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert headings
        for h_level in range(6, 0, -1):
            h_prefix = "#" * h_level
            cleaned_html = re.sub(
                rf'<h{h_level}[^>]*>(.*?)</h{h_level}>',
                rf'\n\n{h_prefix} \1\n\n',
                cleaned_html,
                flags=re.IGNORECASE | re.DOTALL
            )

        # Convert links
        cleaned_html = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

        # Convert bold / strong / em
        cleaned_html = re.sub(r'<(strong|b)>(.*?)</\1>', r'**\2**', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        cleaned_html = re.sub(r'<(em|i)>(.*?)</\1>', r'*\2*', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

        # Convert list items
        cleaned_html = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

        # Convert paragraphs and breaks
        cleaned_html = re.sub(r'<br\s*/?>', '\n', cleaned_html, flags=re.IGNORECASE)
        cleaned_html = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1\n\n', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

        # Strip remaining HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', cleaned_html)

        # Clean excessive whitespace
        lines = [line.strip() for line in clean_text.splitlines()]
        compact_lines = []
        for line in lines:
            if line:
                compact_lines.append(line)
            elif compact_lines and compact_lines[-1] != "":
                compact_lines.append("")

        markdown_body = f"# {title}\n\n" + "\n".join(compact_lines).strip()

        # Extract internal/external links
        links = []
        for match in re.finditer(r'\[(.*?)\]\((https?://[^\s\)]+)\)', markdown_body):
            links.append({"text": match.group(1).strip(), "url": match.group(2).strip()})

        return {
            "markdown": markdown_body,
            "title": title,
            "url": url,
            "status_code": status,
            "engine": "httpx_html2markdown",
            "links": links
        }
