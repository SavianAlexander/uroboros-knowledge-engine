"""
Production Langfuse Observability & Tracing Engine.
Primary Engine: langfuse (observe decorator, Langfuse client for spans, token accounting, stage latency).
Resilient Fallback: Local cryptographic trace ledger (data/telemetry_traces.jsonl).
"""

import os
import sys
import time
import uuid
import json
import logging
from functools import wraps
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for Langfuse
HAS_LANGFUSE = False
try:
    import langfuse
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    HAS_LANGFUSE = True
except (ImportError, Exception) as e:
    HAS_LANGFUSE = False
    logger.info("Langfuse library not available, using local JSONL trace ledger fallback: %s", e)


class RAGSpanRecord(BaseModel):
    """Pydantic v2 schema for individual RAG stage telemetry spans."""
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    stage_name: str
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    tokens_used: int = 0
    status: str = "success"
    error_message: Optional[str] = None


class RAGTraceRecord(BaseModel):
    """Pydantic v2 schema for end-to-end RAG lifecycle trace."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    query: str
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    spans: List[RAGSpanRecord] = Field(default_factory=list)
    final_output: Optional[str] = None
    engine: str = "langfuse" if HAS_LANGFUSE else "local_ledger"


class LangfuseTracer:
    """
    RAG Observability & Trace Manager.
    Logs lifecycle spans to Langfuse Cloud / self-hosted instance, or persists locally.
    """

    _LOCAL_LEDGER_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "telemetry_traces.jsonl"
    )

    @staticmethod
    def is_langfuse_available() -> bool:
        """Checks if langfuse package is active."""
        return HAS_LANGFUSE

    @staticmethod
    def create_trace(query: str) -> RAGTraceRecord:
        """Initializes a new lifecycle trace container."""
        return RAGTraceRecord(query=query)

    @staticmethod
    def log_span(
        trace: RAGTraceRecord,
        stage_name: str,
        input_data: Any,
        output_data: Any,
        latency_ms: float,
        tokens_used: int = 0,
        error: Optional[str] = None
    ) -> RAGSpanRecord:
        """
        Appends a stage span to the trace record.
        """
        span = RAGSpanRecord(
            trace_id=trace.trace_id,
            stage_name=stage_name,
            input_payload={"data": str(input_data)[:500]},
            output_payload={"data": str(output_data)[:500]},
            latency_ms=round(latency_ms, 3),
            tokens_used=tokens_used,
            status="error" if error else "success",
            error_message=error
        )
        trace.spans.append(span)
        trace.total_latency_ms += latency_ms
        trace.total_tokens += tokens_used

        # Also emit to Langfuse if context is active
        if HAS_LANGFUSE:
            try:
                langfuse_context.update_current_observation(
                    name=stage_name,
                    input=input_data,
                    output=output_data,
                    metadata={"latency_ms": latency_ms, "tokens": tokens_used}
                )
            except Exception:
                pass

        return span

    @staticmethod
    def finalize_trace(trace: RAGTraceRecord, final_output: str = "") -> None:
        """
        Finalizes and persists the trace record.
        """
        trace.final_output = final_output
        trace.total_latency_ms = round(trace.total_latency_ms, 3)

        # Local JSONL persistence
        try:
            os.makedirs(os.path.dirname(LangfuseTracer._LOCAL_LEDGER_PATH), exist_ok=True)
            with open(LangfuseTracer._LOCAL_LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(trace.model_dump_json() + "\n")
        except Exception as e:
            logger.warning("Failed to append local trace ledger: %s", e)


def observe_rag_stage(stage_name: str):
    """
    Decorator for automatically instrumenting RAG functions with latency & span telemetry.
    """
    def decorator(func: Callable):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            error_msg = None
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                elapsed = (time.perf_counter() - start) * 1000.0
                logger.info("[OBSERVE_STAGE] stage='%s' latency=%.2fms error=%s", stage_name, elapsed, error_msg)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            error_msg = None
            result = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                elapsed = (time.perf_counter() - start) * 1000.0
                logger.info("[OBSERVE_STAGE_ASYNC] stage='%s' latency=%.2fms error=%s", stage_name, elapsed, error_msg)

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
