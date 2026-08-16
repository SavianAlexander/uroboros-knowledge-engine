"""
Universal Web Crawler, Archival Harvester & Resilient Network Session Package.
Provides multi-strategy HTTP network sessions with:
- DNS-over-HTTPS (DoH) resolution (Cloudflare, Google DNS)
- Wayback Machine archival fallback resolution
- Human reading dwell models and typing flight dynamics
- Standards-compliant Client Hints and User-Agent header rotation
- Cookie jar state management and gzip/deflate decompression
"""

from src.domain.universal_crawler.browser_stealth import StealthSession
from src.domain.universal_crawler.ghost_stealth import GhostStealthSession, DoHResolver, CognitiveDwellModel
from src.domain.universal_crawler.neuromorphic_stealth import OmniStealthSession, NeuromorphicCognitiveEngine
from src.domain.universal_crawler.void_stealth import VoidStealthSession, WaybackFallbackResolver, BehavioralEntropyEngine
from src.domain.universal_crawler.phantom_stealth import PhantomStealthSession
from src.domain.universal_crawler.frontier import UrlFrontier
from src.domain.universal_crawler.models import (
    CrawlJob,
    CrawledDocument,
    CrawlConfig,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_PAUSED,
    JOB_STATUS_FAILED
)

__all__ = [
    "StealthSession",
    "GhostStealthSession",
    "OmniStealthSession",
    "VoidStealthSession",
    "PhantomStealthSession",
    "DoHResolver",
    "WaybackFallbackResolver",
    "CognitiveDwellModel",
    "NeuromorphicCognitiveEngine",
    "BehavioralEntropyEngine",
    "UrlFrontier",
    "CrawlJob",
    "CrawledDocument",
    "CrawlConfig",
    "JOB_STATUS_PENDING",
    "JOB_STATUS_RUNNING",
    "JOB_STATUS_COMPLETED",
    "JOB_STATUS_PAUSED",
    "JOB_STATUS_FAILED",
]
