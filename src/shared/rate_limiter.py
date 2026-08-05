import time
import threading
from typing import Dict, List, Tuple

class SlidingWindowRateLimiter:
    """
    Thread-safe IP sliding window rate limiter.
    Allows up to max_requests per window_seconds per IP.
    """
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, ip_address: str) -> Tuple[bool, int]:
        """
        Check if IP address is within rate limit budget.
        Returns (is_allowed, remaining_requests).
        """
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            timestamps = self.requests.get(ip_address, [])
            valid_timestamps = [t for t in timestamps if t > cutoff]

            if len(valid_timestamps) >= self.max_requests:
                self.requests[ip_address] = valid_timestamps
                return False, 0

            valid_timestamps.append(now)
            self.requests[ip_address] = valid_timestamps
            remaining = self.max_requests - len(valid_timestamps)
            return True, remaining

    def reset(self):
        with self._lock:
            self.requests.clear()
