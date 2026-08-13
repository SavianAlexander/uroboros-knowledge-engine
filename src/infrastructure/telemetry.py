import time
import os
import threading
from typing import Dict, List, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class APMTelemetryExporter:
    """
    OpenTelemetry & Prometheus APM Exporter.
    Tracks latency percentiles (p50, p95, p99), endpoint throughput, and process memory.
    """
    def __init__(self):
        self.latencies: List[float] = []
        self.request_count = 0
        self.error_count = 0
        self._lock = threading.Lock()

    def record_request(self, duration_sec: float, status_code: int = 200):
        with self._lock:
            self.request_count += 1
            if status_code >= 400:
                self.error_count += 1
            self.latencies.append(duration_sec)
            if len(self.latencies) > 1000:
                self.latencies = self.latencies[-1000:]

    def get_metrics_summary(self) -> Dict[str, Any]:
        with self._lock:
            lats = sorted(self.latencies) if self.latencies else [0.0]
            n = len(lats)
            p50 = lats[int(n * 0.50)]
            p95 = lats[int(n * 0.95)] if n >= 20 else lats[-1]
            p99 = lats[int(n * 0.99)] if n >= 100 else lats[-1]

            mem_rss_mb = 0.0
            if HAS_PSUTIL:
                try:
                    process = psutil.Process(os.getpid())
                    mem_rss_mb = process.memory_info().rss / (1024 * 1024)
                except Exception:
                    mem_rss_mb = 0.0

            return {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "latency_p50_ms": round(p50 * 1000, 2),
                "latency_p95_ms": round(p95 * 1000, 2),
                "latency_p99_ms": round(p99 * 1000, 2),
                "memory_rss_mb": round(mem_rss_mb, 2)
            }

    def generate_prometheus_text(self) -> str:
        summary = self.get_metrics_summary()
        lines = [
            "# HELP uroboros_requests_total Total HTTP requests handled.",
            "# TYPE uroboros_requests_total counter",
            f"uroboros_requests_total {summary['total_requests']}",
            "# HELP uroboros_errors_total Total HTTP error responses.",
            "# TYPE uroboros_errors_total counter",
            f"uroboros_errors_total {summary['total_errors']}",
            "# HELP uroboros_latency_p50_ms HTTP request latency p50 in ms.",
            "# TYPE uroboros_latency_p50_ms gauge",
            f"uroboros_latency_p50_ms {summary['latency_p50_ms']}",
            "# HELP uroboros_memory_rss_mb Process resident memory in MB.",
            "# TYPE uroboros_memory_rss_mb gauge",
            f"uroboros_memory_rss_mb {summary['memory_rss_mb']}"
        ]
        return "\n".join(lines) + "\n"

GLOBAL_TELEMETRY = APMTelemetryExporter()
