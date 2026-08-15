import unittest
import sqlite3
import json
import time
from src.domain.universal_crawler.models import (
    CrawlJob,
    CrawlConfig,
    CrawlUrlItem,
    CrawledDocument,
    JOB_STATUS_PENDING,
    JOB_STATUS_COMPLETED
)
from src.domain.universal_crawler.frontier import UrlFrontier
from src.domain.universal_crawler.rate_limiter import DomainRateLimiter
from src.domain.universal_crawler.ghost_stealth import (
    CognitiveDwellModel,
    HumanJourneyTracker,
    GhostStealthSession
)
from src.domain.universal_crawler.extractor import (
    extract_clean_text_from_html,
    extract_links_from_html,
    extract_html_metadata,
    extract_urls_from_sitemap_xml,
    calculate_merkle_provenance,
    normalize_url
)
from src.domain.universal_crawler.stealth_engine import StealthNetworkSession
from src.infrastructure.crawler_repository import (
    init_crawler_schema,
    create_job,
    get_job,
    list_jobs,
    enqueue_urls,
    pop_next_url,
    save_crawled_document,
    get_job_documents
)

class TestUniversalCrawlerEnterprise(unittest.TestCase):
    """
    Comprehensive test suite for the Enterprise Ghost-Tier Stealth Crawler & Swarm.
    """

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_crawler_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_job_lifecycle_persistence(self):
        """Verify persistent job creation and state retrieval."""
        config = CrawlConfig(max_pages=50, stealth_mode="ghost", allowed_domains=["example.com"])
        job = CrawlJob(
            name="Test Legal Scrape",
            seed_urls=["https://example.com/legal"],
            config=config
        )
        job_id = create_job(self.conn, job)
        self.assertGreater(job_id, 0)

        retrieved = get_job(self.conn, job_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Legal Scrape")
        self.assertEqual(retrieved.config.max_pages, 50)
        self.assertEqual(retrieved.config.stealth_mode, "ghost")
        self.assertEqual(retrieved.seed_urls, ["https://example.com/legal"])

    def test_url_frontier_queue_and_deduplication(self):
        """Verify priority queueing and deduplication in URL frontier."""
        job = CrawlJob(name="Queue Test", seed_urls=["https://site.org/index"])
        job_id = create_job(self.conn, job)

        item1 = pop_next_url(self.conn, job_id)
        self.assertIsNotNone(item1)
        self.assertEqual(item1.url, "https://site.org/index")

        new_urls = [
            ("https://site.org/page1", 1, 5),
            ("https://site.org/page2", 1, 6),
            ("https://site.org/page1", 1, 5),  # Duplicate
        ]
        added = enqueue_urls(self.conn, job_id, new_urls)
        self.assertEqual(added, 2)

        next_item = pop_next_url(self.conn, job_id)
        self.assertIsNotNone(next_item)
        self.assertEqual(next_item.url, "https://site.org/page2")

    def test_domain_rate_limiter(self):
        """Verify per-domain polite rate limiter delays consecutive requests to same domain."""
        limiter = DomainRateLimiter(default_interval=0.1)
        t0 = time.time()
        limiter.acquire("https://oslpr.org/medida1")
        limiter.acquire("https://oslpr.org/medida2")
        elapsed = time.time() - t0
        self.assertGreaterEqual(elapsed, 0.08)

    def test_cognitive_dwell_model(self):
        """Verify human cognitive dwell calculation scales with content density."""
        short_dwell = CognitiveDwellModel.calculate_dwell_seconds(300, stealth_level="fast")
        long_dwell = CognitiveDwellModel.calculate_dwell_seconds(8000, stealth_level="fast")
        self.assertGreater(long_dwell, short_dwell)
        self.assertGreater(short_dwell, 0.1)

    def test_human_journey_tracker_and_csrf(self):
        """Verify natural human referer continuity and CSRF token extraction."""
        journey = HumanJourneyTracker()
        sample_page = '<form><input type="hidden" name="__RequestVerificationToken" value="xyz_secure_token_123" /></form>'
        journey.record_visit("https://sutra.oslpr.org/medidas", sample_page)

        # Subsequent detail page should have the listing page as natural referer
        referer = journey.get_natural_referer("https://sutra.oslpr.org/medidas/136624")
        self.assertEqual(referer, "https://sutra.oslpr.org/medidas")

        # CSRF token harvested
        csrf = journey.get_csrf_token("https://sutra.oslpr.org/medidas/136624")
        self.assertEqual(csrf, "xyz_secure_token_123")

    def test_ghost_stealth_headers(self):
        """Verify ghost headers contain client hints, referer, and host."""
        session = GhostStealthSession(mode="ghost")
        session.journey.record_visit("https://sutra.oslpr.org/index.html")
        headers = session.get_ghost_headers("https://sutra.oslpr.org/medidas/100")

        self.assertEqual(headers["Host"], "sutra.oslpr.org")
        self.assertIn("es-PR", headers["Accept-Language"])
        self.assertEqual(headers["Referer"], "https://sutra.oslpr.org/index.html")
        self.assertEqual(headers["Sec-Fetch-Site"], "same-origin")
        self.assertIn("Chromium", headers["sec-ch-ua"])

    def test_xml_sitemap_extraction(self):
        """Verify extraction of URLs from XML sitemap format."""
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/leyes/codigo-civil</loc></url>
            <url><loc>https://example.com/leyes/codigo-penal</loc></url>
        </urlset>
        """
        urls = extract_urls_from_sitemap_xml(sitemap_xml)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://example.com/leyes/codigo-civil", urls)
        self.assertIn("https://example.com/leyes/codigo-penal", urls)

    def test_html_metadata_and_json_ld(self):
        """Verify extraction of OpenGraph and Schema.org metadata."""
        html = """
        <html>
        <head>
            <title>Ley 55 de 2020</title>
            <meta name="description" content="Código Civil de Puerto Rico">
            <meta property="og:title" content="Código Civil 2020">
            <script type="application/ld+json">
            {"@type": "Legislation", "headline": "Ley Núm. 55-2020"}
            </script>
        </head>
        <body><p>Texto legal</p></body>
        </html>
        """
        title, text, meta = extract_clean_text_from_html(html)
        self.assertEqual(title, "Ley 55 de 2020")
        self.assertEqual(meta.get("description"), "Código Civil de Puerto Rico")
        self.assertEqual(meta.get("og_title"), "Código Civil 2020")
        self.assertEqual(meta.get("schema_type"), "Legislation")

    def test_waf_signature_detection(self):
        """Verify detection of WAF challenges."""
        session = StealthNetworkSession(mode="fast")
        sig = session.detect_waf_challenge(
            status_code=403,
            headers={"Server": "cloudflare", "CF-RAY": "85a12b3c4d5e"},
            body_sample="Please enable cookies and turnstile to continue"
        )
        self.assertIsNotNone(sig)
        self.assertIn("WAF Challenge Detected", sig)

    def test_merkle_provenance(self):
        """Verify cryptographic SHA-256 Merkle leaf integrity."""
        text = "Ley Núm. 55-2020. Nuevo Código Civil de Puerto Rico."
        url = "https://sutra.oslpr.org/ley55.html"
        meta = {"job_id": 1, "content_type": "text/html"}

        merkle = calculate_merkle_provenance(text, url, meta)
        self.assertEqual(len(merkle), 64)

if __name__ == "__main__":
    unittest.main()
