import time
import threading
from urllib.parse import urlparse
from typing import Dict, Optional

"""
Per-Domain Polite Token-Bucket Rate Limiter.
Allows high-throughput cross-domain crawling while strictly enforcing
polite rate-limits and jitter per individual target domain.
"""

class DomainRateLimiter:
    """Thread-safe per-domain token bucket rate limiter."""

    def __init__(self, default_interval: float = 1.0):
        self.default_interval = default_interval
        self._domain_locks: Dict[str, threading.Lock] = {}
        self._last_request_time: Dict[str, float] = {}
        self._master_lock = threading.Lock()

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return "default"

    def acquire(self, url: str, min_delay: Optional[float] = None):
        """Block until the target domain is ready for another request."""
        domain = self._get_domain(url)
        interval = min_delay if min_delay is not None else self.default_interval

        with self._master_lock:
            if domain not in self._domain_locks:
                self._domain_locks[domain] = threading.Lock()
                self._last_request_time[domain] = 0.0
            domain_lock = self._domain_locks[domain]

        with domain_lock:
            now = time.time()
            elapsed = now - self._last_request_time[domain]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            self._last_request_time[domain] = time.time()
