import time
import random
import ssl
import gzip
import http.cookiejar
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple, List

"""
Advanced Enterprise Stealth & Anti-Ban Subsystem.
Includes:
- Realistic Browser Profiles (Chrome, Safari, Firefox, Edge)
- Canonical Header Ordering & Client Hints (Sec-CH-UA, DNT, Sec-Fetch)
- Dynamic Proxy Pool with auto-failover
- WAF Challenge & Bot Detection Signature Analyzer
- Exponential Circuit Breaker & Adaptive Latency Pacing
"""

USER_AGENT_PROFILES = [
    {
        "name": "Chrome_Win11",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0"
    },
    {
        "name": "Safari_macOS",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "sec-ch-ua": None,
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-mobile": "?0"
    },
    {
        "name": "Firefox_Win11",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "sec-ch-ua": '"Firefox";v="123"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0"
    },
    {
        "name": "Edge_Win11",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "sec-ch-ua": '"Chromium";v="122", "Microsoft Edge";v="122"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0"
    }
]

STEALTH_PRESETS = {
    "ultra": {"min_delay": 2.0, "max_delay": 4.5, "burst_size": 12, "burst_pause": (8.0, 15.0)},
    "balanced": {"min_delay": 0.6, "max_delay": 1.8, "burst_size": 25, "burst_pause": (3.0, 7.0)},
    "fast": {"min_delay": 0.15, "max_delay": 0.45, "burst_size": 50, "burst_pause": (1.0, 2.5)}
}

# WAF and Challenge Signatures
WAF_SIGNATURES = [
    "cf-ray", "cloudflare", "cf-browser-verification", "turnstile",
    "datadome", "perimeterx", "akamai", "aws-waf", "shield-square",
    "incapsula", "captcha", "security check", "please verify you are human"
]

class StealthNetworkSession:
    """Enterprise Human-Emulation Session Manager with WAF Detection & Proxy Support."""

    def __init__(self, mode: str = "balanced", proxy_list: Optional[List[str]] = None):
        self.mode = mode
        self.config = STEALTH_PRESETS.get(mode, STEALTH_PRESETS["balanced"])
        self.proxy_list = proxy_list or []
        self.cookie_jar = http.cookiejar.CookieJar()
        self.ssl_context = self._create_stealth_ssl_context()

        self.opener = self._build_opener()
        self.profile = random.choice(USER_AGENT_PROFILES)
        self.request_count = 0
        self.backoff_factor = 1.0
        self.last_latency_ms = 0.0

    def _create_stealth_ssl_context(self) -> ssl.SSLContext:
        """Create high-compatibility TLS context mimicking modern browsers."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            # Prefer modern ECDHE ciphers
            ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384')
        except Exception:
            pass
        return ctx

    def _build_opener(self) -> urllib.request.OpenerDirector:
        """Construct opener with cookies, SSL, and optional proxy rotation."""
        handlers = [
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPSHandler(context=self.ssl_context)
        ]
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            handlers.append(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}))

        return urllib.request.build_opener(*handlers)

    def rotate_proxy(self):
        """Rotate to another proxy if proxy pool is present."""
        if self.proxy_list:
            self.opener = self._build_opener()

    def get_headers(self, referer: Optional[str] = None, is_json: bool = False) -> Dict[str, str]:
        """Construct ordered, realistic browser headers."""
        headers = {
            "User-Agent": self.profile["User-Agent"],
            "Accept-Language": "es-PR,es;q=0.9,es-419;q=0.8,en-US;q=0.7,en;q=0.6",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1" if not is_json else "0",
            "Sec-Fetch-Dest": "empty" if is_json else "document",
            "Sec-Fetch-Mode": "cors" if is_json else "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        if self.profile.get("sec-ch-ua"):
            headers["sec-ch-ua"] = self.profile["sec-ch-ua"]
            headers["sec-ch-ua-platform"] = self.profile["sec-ch-ua-platform"]
            headers["sec-ch-ua-mobile"] = self.profile["sec-ch-ua-mobile"]

        if is_json:
            headers["Accept"] = "application/json, text/plain, */*"
        else:
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"

        if referer:
            headers["Referer"] = referer

        return headers

    def jitter_delay(self):
        """Adaptive Gaussian jitter delay with reading pauses."""
        self.request_count += 1
        cfg = self.config

        # Check reading pause
        if self.request_count % cfg["burst_size"] == 0:
            pause_time = random.uniform(*cfg["burst_pause"])
            time.sleep(pause_time)
            self.profile = random.choice(USER_AGENT_PROFILES)
            self.rotate_proxy()
            return

        mean = (cfg["min_delay"] + cfg["max_delay"]) / 2.0
        std_dev = (cfg["max_delay"] - cfg["min_delay"]) / 4.0
        delay = max(cfg["min_delay"], random.gauss(mean, std_dev)) * self.backoff_factor
        time.sleep(delay)

    def detect_waf_challenge(self, status_code: int, headers: Dict[str, str], body_sample: str) -> Optional[str]:
        """Detect WAF challenge or Bot detection signatures in response."""
        body_lower = body_sample.lower()
        header_str = " ".join([f"{k}:{v}" for k, v in headers.items()]).lower()

        for sig in WAF_SIGNATURES:
            if sig in header_str or sig in body_lower:
                if status_code in (403, 429, 503):
                    return f"WAF Challenge Detected: {sig}"
        return None

    def fetch(
        self,
        url: str,
        referer: Optional[str] = None,
        timeout: int = 25,
        max_retries: int = 4
    ) -> Tuple[Optional[bytes], Optional[str], int, Optional[str], Dict[str, Any]]:
        """
        Fetch URL with WAF detection, decompression, and latency tracking.
        Returns (content_bytes, content_type, status_code, error_message, telemetry).
        """
        for attempt in range(max_retries):
            self.jitter_delay()
            t_start = time.time()
            try:
                is_json = url.endswith(".json") or "/api/" in url
                headers = self.get_headers(referer=referer, is_json=is_json)
                req = urllib.request.Request(url, headers=headers)

                with self.opener.open(req, timeout=timeout) as res:
                    self.last_latency_ms = (time.time() - t_start) * 1000.0
                    self.backoff_factor = 1.0
                    status_code = res.status
                    content_type = res.headers.get("Content-Type", "").split(";")[0].strip()
                    res_headers = dict(res.headers.items())
                    raw_data = res.read()

                    # Gzip decompression
                    if res.headers.get("Content-Encoding") == "gzip":
                        try:
                            raw_data = gzip.decompress(raw_data)
                        except Exception:
                            pass

                    telemetry = {
                        "latency_ms": self.last_latency_ms,
                        "server": res.headers.get("Server", "Unknown"),
                        "cf_ray": res.headers.get("CF-RAY"),
                        "profile": self.profile["name"]
                    }
                    return raw_data, content_type, status_code, None, telemetry

            except urllib.error.HTTPError as e:
                self.last_latency_ms = (time.time() - t_start) * 1000.0
                status_code = e.code
                err_body = ""
                try:
                    err_body = e.read().decode('utf-8', errors='ignore')[:500]
                except Exception:
                    pass

                waf_alert = self.detect_waf_challenge(status_code, dict(e.headers.items()), err_body)
                if waf_alert:
                    print(f"  [!] {waf_alert}. Rotating identity and backing off...")
                    self.profile = random.choice(USER_AGENT_PROFILES)
                    self.rotate_proxy()

                if status_code in (429, 503):
                    retry_after = e.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after and retry_after.isdigit() else (4.0 * (2 ** attempt)) + random.uniform(1.0, 3.0)
                    self.backoff_factor = min(self.backoff_factor * 1.5, 4.0)
                    time.sleep(wait_time)
                elif status_code in (403, 404):
                    return None, "", status_code, f"HTTP Error {status_code}: {e.reason}", {"latency_ms": self.last_latency_ms}
                else:
                    time.sleep(2.0)
            except Exception as ex:
                self.last_latency_ms = (time.time() - t_start) * 1000.0
                if attempt == max_retries - 1:
                    return None, "", 0, str(ex), {"latency_ms": self.last_latency_ms}
                time.sleep(2.0 * (attempt + 1))

        return None, "", 0, "Max retries exceeded", {"latency_ms": self.last_latency_ms}
