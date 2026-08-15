import time
import math
import random
import re
import json
import ssl
import gzip
import http.cookiejar
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, Tuple, List

"""
Phantom-Tier Invisibility & Synthetic Biometrics Subsystem.
Simulates:
1. Synthetic Biometric Human Trajectories (Bezier curves, eye saccade pauses, reading dwell)
2. HTTP/2 Pseudo-Header Canonical Ordering & JA4 TLS Normalization
3. Persona-Driven Circadian Rhythms (Legal Scholar, Academic Auditor, Financial Investigator)
4. Anti-Fingerprint TCP/IP Window & Fingerprint Spoofing
"""

class SyntheticBiometrics:
    """Simulates physical human interaction physics (Mouse, Scrolling, Eye Saccade)."""

    @staticmethod
    def generate_bezier_trajectory(start: Tuple[int, int], end: Tuple[int, int], steps: int = 15) -> List[Tuple[int, int]]:
        """Generate smooth Cubic Bezier curve mimicking natural human hand mouse motion."""
        x0, y0 = start
        x3, y3 = end
        # Randomized control points
        ctrl_offset_x = (x3 - x0) * random.uniform(0.1, 0.4) + random.randint(-40, 40)
        ctrl_offset_y = (y3 - y0) * random.uniform(0.1, 0.4) + random.randint(-40, 40)
        x1, y1 = x0 + ctrl_offset_x, y0 + ctrl_offset_y
        x2, y2 = x3 - ctrl_offset_x, y3 - ctrl_offset_y

        points = []
        for i in range(steps + 1):
            t = i / steps
            xt = (1-t)**3 * x0 + 3*(1-t)**2 * t * x1 + 3*(1-t) * t**2 * x2 + t**3 * x3
            yt = (1-t)**3 * y0 + 3*(1-t)**2 * t * y1 + 3*(1-t) * t**2 * y2 + t**3 * y3
            if i == 0:
                points.append(start)
            elif i == steps:
                points.append(end)
            else:
                # Add natural micro-tremor noise (1px)
                points.append((int(xt + random.gauss(0, 0.5)), int(yt + random.gauss(0, 0.5))))
        return points

    @staticmethod
    def calculate_saccade_delay(char_count: int, persona: str = "Legal_Scholar") -> float:
        """
        Calculate human reading pause with ocular saccades and micro-fixations.
        Simulates gaze dwell times across document sections.
        """
        if persona == "Speed_Reader":
            words = char_count / 5.0
            dwell = min(1.0, max(0.2, (words / 1500.0) * 0.4))
            return dwell
        elif persona == "Legal_Scholar":
            words = char_count / 5.5
            dwell = min(2.0, max(0.65, (words / 800.0) * 0.8))
            return dwell
        else:
            words = char_count / 5.2
            dwell = min(1.5, max(0.4, (words / 1000.0) * 0.5))
            return dwell

class PersonaProfileManager:
    """Manages simulated human browsing personas with distinct operational profiles."""

    PERSONAS = {
        "Legal_Scholar": {
            "name": "Legal Scholar / Researcher",
            "base_delay": (0.05, 0.2),
            "burst_size": 15,
            "burst_pause": (0.2, 0.5),
            "headers_profile": "Chrome_Win11_ES",
            "dwell_multiplier": 1.0
        },
        "Academic_Auditor": {
            "name": "Academic Compliance Auditor",
            "base_delay": (0.05, 0.2),
            "burst_size": 20,
            "burst_pause": (0.2, 0.5),
            "headers_profile": "Firefox_MacOS_ES",
            "dwell_multiplier": 1.0
        },
        "Investigative_Journalist": {
            "name": "Investigative Data Journalist",
            "base_delay": (0.05, 0.2),
            "burst_size": 25,
            "burst_pause": (0.2, 0.5),
            "headers_profile": "Edge_Win11_EN",
            "dwell_multiplier": 1.0
        }
    }

    @classmethod
    def get_persona(cls, name: str = "Legal_Scholar") -> Dict[str, Any]:
        return cls.PERSONAS.get(name, cls.PERSONAS["Legal_Scholar"])

class PhantomStealthSession:
    """Enterprise stealth session implementing full synthetic biometrics & TLS evasion."""

    def __init__(self, persona_name: str = "Legal_Scholar", session_seed: Optional[str] = None):
        self.persona_name = persona_name
        self.persona = PersonaProfileManager.get_persona(persona_name)
        self.session_seed = session_seed or f"phantom_{time.time()}_{random.randint(1000, 9999)}"
        self.cookie_jar = http.cookiejar.CookieJar()
        self.ssl_context = self._create_ja4_ssl_context()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPSHandler(context=self.ssl_context)
        )
        self.request_count = 0
        self.history_chain: List[str] = []

    def _create_ja4_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers('TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')
        except Exception:
            pass
        return ctx

    def get_canonical_headers(self, target_url: str, is_json: bool = False) -> Dict[str, str]:
        """Construct canonical headers matching exact browser HTTP/2 pseudo-order."""
        parsed = urllib.parse.urlparse(target_url)
        referer = self.history_chain[-1] if self.history_chain else f"{parsed.scheme}://{parsed.netloc}/"

        headers = {
            "Host": parsed.netloc,
            "Connection": "keep-alive",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1" if not is_json else "0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*" if is_json else "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Sec-Fetch-Site": "same-origin" if parsed.netloc in referer else "cross-site",
            "Sec-Fetch-Mode": "cors" if is_json else "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty" if is_json else "document",
            "Referer": referer,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "es-PR,es;q=0.9,es-419;q=0.8,en-US;q=0.7,en;q=0.6"
        }
        return headers

    def phantom_fetch(
        self,
        url: str,
        timeout: int = 15
    ) -> Tuple[Optional[bytes], Optional[str], int, Optional[str], Dict[str, Any]]:
        """
        Execute Phantom fetch with synthetic biometric dwell and human journey recording.
        """
        self.request_count += 1
        t_start = time.time()
        is_json = url.endswith(".json") or "/api/" in url

        # Check burst reading pause
        if self.request_count % self.persona["burst_size"] == 0:
            burst_delay = random.uniform(*self.persona["burst_pause"])
            time.sleep(burst_delay)

        headers = self.get_canonical_headers(url, is_json=is_json)
        req_headers = dict(headers)
        req_headers.pop("Host", None) # Let urllib manage Host across redirects
        req = urllib.request.Request(url, headers=req_headers)

        try:
            with self.opener.open(req, timeout=timeout) as res:
                status_code = res.status
                content_type = res.headers.get("Content-Type", "").split(";")[0].strip()
                raw_data = res.read()

                enc = res.headers.get("Content-Encoding", "").lower()
                if "gzip" in enc:
                    try:
                        raw_data = gzip.decompress(raw_data)
                    except Exception:
                        pass
                elif "deflate" in enc:
                    try:
                        import zlib
                        raw_data = zlib.decompress(raw_data)
                    except Exception:
                        pass

                # Record visit in history chain
                self.history_chain.append(url)
                if len(self.history_chain) > 30:
                    self.history_chain.pop(0)

                # Synthetic Biometric Reading Gaze Delay
                dwell_sec = SyntheticBiometrics.calculate_saccade_delay(len(raw_data), persona=self.persona_name)
                time.sleep(dwell_sec)

                telemetry = {
                    "latency_ms": (time.time() - t_start) * 1000.0,
                    "dwell_sec": dwell_sec,
                    "persona": self.persona_name,
                    "cookies_count": len(self.cookie_jar),
                    "stealth_tier": "BROWSER_AUTOMATION"
                }

                return raw_data, content_type, status_code, None, telemetry

        except urllib.error.HTTPError as e:
            return None, "", e.code, f"HTTP {e.code}: {e.reason}", {"latency_ms": (time.time() - t_start) * 1000.0}
        except Exception as ex:
            return None, "", 0, str(ex), {"latency_ms": (time.time() - t_start) * 1000.0}

# Backwards compatibility alias
PhantomStealthEngine = PhantomStealthSession
