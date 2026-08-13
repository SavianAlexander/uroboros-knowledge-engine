"""
Live SSE Event-Driven Knowledge Sync Engine.
Generates SSE event payloads for real-time document indexing, search progress, and telemetry updates.
Zero-dependency, stdlib implementation.
"""

import json
from typing import Dict, Any, Generator


def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    Formats a dictionary payload into standard Server-Sent Event (SSE) wire format.
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"


def generate_knowledge_sync_sse_stream(
    sync_job_id: str,
    total_steps: int = 3
) -> Generator[str, None, None]:
    """
    Simulates SSE stream events for knowledge sync background tasks.
    """
    yield format_sse_event("sync_start", {"job_id": sync_job_id, "status": "initializing"})
    for step in range(1, total_steps + 1):
        progress = round((step / float(total_steps)) * 100.0, 1)
        yield format_sse_event("sync_progress", {"job_id": sync_job_id, "step": step, "progress": progress})
    yield format_sse_event("sync_complete", {"job_id": sync_job_id, "status": "completed"})
