"""
Live SSE Event-Driven Knowledge Sync Engine.
Generates SSE event payloads for real-time document indexing, search progress, and telemetry updates.
Zero-dependency, stdlib implementation.
"""
import json
from typing import Dict, Any, Generator


import time
from typing import Dict, Any, Generator, Optional, List


def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    Formats a dictionary payload into standard Server-Sent Event (SSE) wire format.
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"


def generate_knowledge_sync_sse_stream(
    sync_job_id: str,
    total_steps: int = 3,
    delay_ms: float = 0.0,
    step_descriptions: Optional[List[str]] = None
) -> Generator[str, None, None]:
    """
    Simulates SSE stream events for knowledge sync background tasks.
    Zero-dependency stdlib implementation.
    """
    steps_cnt = max(1, min(50, int(total_steps))) if total_steps else 3
    yield format_sse_event("sync_start", {"job_id": sync_job_id, "status": "initializing", "total_steps": steps_cnt})
    
    for step in range(1, steps_cnt + 1):
        if delay_ms > 0:
            time.sleep(min(1.0, delay_ms / 1000.0))
        progress = round((step / float(steps_cnt)) * 100.0, 1)
        desc = step_descriptions[step - 1] if step_descriptions and len(step_descriptions) >= step else f"Processing step {step}/{steps_cnt}"
        yield format_sse_event("sync_progress", {
            "job_id": sync_job_id,
            "step": step,
            "total_steps": steps_cnt,
            "progress": progress,
            "description": desc
        })

    yield format_sse_event("sync_complete", {"job_id": sync_job_id, "status": "completed", "total_steps_executed": steps_cnt})
