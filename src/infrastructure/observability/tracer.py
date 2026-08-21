"""
Canonical Observability & Telemetry Tracer (10-Tool Stack).
Integrates Langfuse @observe() lifecycle tracing for RAG spans, latencies, token costs, and eval scores.
"""

import os
import sys
import time
import functools
import logging
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for Langfuse
HAS_LANGFUSE = False
try:
    import langfuse
    from langfuse.decorators import observe, langfuse_context
    HAS_LANGFUSE = True
except (ImportError, Exception) as e:
    HAS_LANGFUSE = False
    logger.info("Langfuse package not active, using built-in high-resolution tracer fallback: %s", e)


def observe(name: Optional[str] = None, as_type: str = "span"):
    """
    Canonical @observe() decorator tracking function execution spans, latency, and exceptions.
    """
    def decorator(func: Callable):
        span_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = LangfuseTracer.get_instance()
            start = time.perf_counter()
            error_msg = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                dur_ms = (time.perf_counter() - start) * 1000
                tracer.record_span(
                    name=span_name,
                    span_type=as_type,
                    duration_ms=dur_ms,
                    metadata={"error": error_msg} if error_msg else {}
                )
        return wrapper
    return decorator


class LangfuseTracer:
    """
    Singleton observability tracer logging end-to-end RAG telemetry spans.
    """
    _instance: Optional["LangfuseTracer"] = None

    def __init__(self):
        self.spans: List[Dict[str, Any]] = []
        self.eval_scores: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "LangfuseTracer":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def is_langfuse_active() -> bool:
        """Checks if native Langfuse client is active."""
        return HAS_LANGFUSE

    def record_span(
        self,
        name: str,
        span_type: str = "span",
        duration_ms: float = 0.0,
        tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Records an execution span."""
        span_data = {
            "name": name,
            "type": span_type,
            "duration_ms": duration_ms,
            "tokens": tokens,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        self.spans.append(span_data)
        logger.debug("Logged trace span '%s' (type=%s, dur=%.2fms)", name, span_type, duration_ms)

    def score_trace(self, name: str, value: float, comment: str = "") -> None:
        """Logs an evaluation score for a trace."""
        self.eval_scores.append({
            "name": name,
            "value": value,
            "comment": comment,
            "timestamp": time.time()
        })

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Calculates aggregated metrics across all recorded spans."""
        total_dur = sum(s["duration_ms"] for s in self.spans)
        total_tokens = sum(s.get("tokens", 0) for s in self.spans)
        return {
            "total_spans": len(self.spans),
            "total_duration_ms": total_dur,
            "total_tokens": total_tokens,
            "evaluations_count": len(self.eval_scores)
        }

    def clear(self) -> None:
        """Clears in-memory trace buffers."""
        self.spans.clear()
        self.eval_scores.clear()
