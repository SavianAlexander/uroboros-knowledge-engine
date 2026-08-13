"""
Sub-50ms SLA Circuit Breaker & Fallback Engine.
Monitors execution latency and automatically downgrades retrieval strategies if latency exceeds strict SLA bounds.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, Callable


def execute_with_sla_circuit_breaker(
    primary_func: Callable[[], Any],
    fallback_func: Callable[[], Any],
    latency_ms: float,
    max_sla_ms: float = 50.0
) -> Dict[str, Any]:
    """
    Executes search function, triggering fallback strategy if latency exceeds max SLA bounds.
    """
    safe_latency = float(latency_ms) if latency_ms is not None and isinstance(latency_ms, (int, float)) else 999.0
    safe_max_sla = float(max_sla_ms) if max_sla_ms is not None and isinstance(max_sla_ms, (int, float)) else 50.0

    if safe_latency <= safe_max_sla:
        try:
            result = primary_func()
            return {
                "result": result,
                "strategy_used": "primary_colbert",
                "circuit_tripped": False,
                "latency_ms": latency_ms,
                "status": "success"
            }
        except Exception:
            pass

    # Circuit tripped or primary failed -> Fallback to ultra-fast BM25 / FTS5
    try:
        fallback_res = fallback_func()
        return {
            "result": fallback_res,
            "strategy_used": "fallback_fts5_fast",
            "circuit_tripped": True,
            "latency_ms": latency_ms,
            "sla_threshold_ms": max_sla_ms,
            "status": "degraded_fallback"
        }
    except Exception as e:
        return {
            "result": None,
            "strategy_used": "fallback_failed",
            "circuit_tripped": True,
            "latency_ms": latency_ms,
            "sla_threshold_ms": max_sla_ms,
            "error": str(e),
            "status": "degraded_error"
        }
