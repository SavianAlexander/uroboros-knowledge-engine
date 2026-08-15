"""
Asyncio Stream Watchdog & Client Disconnection Reaper.
Standard: Pure Python Standard Library (asyncio, time, threading, logging).
Ponytail Senior Dev Principle: Prevent dangling coroutines and orphaned LLM/TTS streams
when a user closes the browser tab or cancels a streaming request.
"""

import time
import asyncio
import logging
import threading
from typing import Dict, Any, Optional, Set, Callable, AsyncGenerator

logger = logging.getLogger(__name__)

# Global registry of active async streaming sessions
_STREAMS_LOCK = threading.Lock()
_ACTIVE_STREAMS: Dict[str, Dict[str, Any]] = {}
_REAPED_STREAMS_COUNT = 0


class AsyncStreamReaper:
    """
    Manages and monitors lifecycle of async streaming responses (SSE / NDJSON).
    """

    @classmethod
    def register_stream(cls, stream_id: str, stream_type: str = "generic") -> str:
        now = time.time()
        with _STREAMS_LOCK:
            _ACTIVE_STREAMS[stream_id] = {
                "id": stream_id,
                "type": stream_type,
                "started_at": now,
                "last_chunk_at": now,
                "chunks_sent": 0,
                "status": "streaming"
            }
        return stream_id

    @classmethod
    def record_chunk(cls, stream_id: str):
        with _STREAMS_LOCK:
            if stream_id in _ACTIVE_STREAMS:
                _ACTIVE_STREAMS[stream_id]["last_chunk_at"] = time.time()
                _ACTIVE_STREAMS[stream_id]["chunks_sent"] += 1

    @classmethod
    def unregister_stream(cls, stream_id: str, status: str = "completed"):
        global _REAPED_STREAMS_COUNT
        with _STREAMS_LOCK:
            if stream_id in _ACTIVE_STREAMS:
                _ACTIVE_STREAMS[stream_id]["status"] = status
                del _ACTIVE_STREAMS[stream_id]
                _REAPED_STREAMS_COUNT += 1

    @classmethod
    def get_stream_stats(cls) -> Dict[str, Any]:
        with _STREAMS_LOCK:
            active_list = [
                {
                    "id": sid,
                    "type": s["type"],
                    "chunks_sent": s["chunks_sent"],
                    "duration_seconds": round(time.time() - s["started_at"], 2)
                }
                for sid, s in _ACTIVE_STREAMS.items()
            ]
            return {
                "active_streams_count": len(active_list),
                "active_streams": active_list,
                "lifetime_reaped_streams": _REAPED_STREAMS_COUNT
            }

    @classmethod
    async def wrap_disconnect_guard(
        cls,
        generator: AsyncGenerator[str, None],
        stream_id: str,
        stream_type: str = "generic",
        check_disconnect_fn: Optional[Callable[[], Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Wraps an asynchronous generator with client disconnection checks.
        If the client disconnects, aborts cleanly and unregisters the stream.
        """
        cls.register_stream(stream_id, stream_type)
        try:
            async for chunk in generator:
                if check_disconnect_fn:
                    is_disc = check_disconnect_fn()
                    if asyncio.iscoroutine(is_disc):
                        is_disc = await is_disc
                    if is_disc:
                        logger.info(f"Stream {stream_id} ({stream_type}) aborted: client disconnected.")
                        cls.unregister_stream(stream_id, status="client_disconnected")
                        break
                cls.record_chunk(stream_id)
                yield chunk
            cls.unregister_stream(stream_id, status="completed")
        except asyncio.CancelledError:
            logger.info(f"Stream {stream_id} cancelled.")
            cls.unregister_stream(stream_id, status="cancelled")
            raise
        except Exception as e:
            logger.warning(f"Stream {stream_id} error: {e}")
            cls.unregister_stream(stream_id, status="error")
            raise
