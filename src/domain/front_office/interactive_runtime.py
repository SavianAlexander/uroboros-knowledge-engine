"""
Front-Office Real-Time Interactive Runtime.
Provides ultra-low-latency (<1.5s) conversational answers using local VRAM SLMs
and dispatches compute-heavy tasks asynchronously to the Back-Office Colibrì queue.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

from src.core.gateway.gateway_router import ModelGatewayRouter
from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.back_office.job_queue import BackOfficeJobQueue, JobType

logger = logging.getLogger(__name__)


class InteractiveChatResponse(BaseModel):
    """Schema for Front-Office fast interactive chat response."""
    query: str
    answer: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: float
    model_used: str
    deep_job_id: Optional[str] = None


class FrontOfficeRuntime:
    """
    High-speed interactive conversational tier.
    """

    def __init__(
        self,
        gateway: Optional[ModelGatewayRouter] = None,
        job_queue: Optional[BackOfficeJobQueue] = None,
        default_model: str = "ollama/qwen2.5:7b"
    ):
        self.gateway = gateway or ModelGatewayRouter(default_model=default_model)
        self.job_queue = job_queue or BackOfficeJobQueue()
        self.default_model = default_model

    def fast_chat(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
        trigger_deep_job: bool = False,
        deep_job_type: Optional[JobType] = None
    ) -> InteractiveChatResponse:
        """
        Executes fast conversational retrieval + generation with strict sub-1.5s target.
        Optionally dispatches an asynchronous Back-Office background job.
        """
        start_time = time.perf_counter()

        # 1. Fast Hybrid Context Extraction
        context_text, citations = extract_advanced_rag_context(query, max_chunks=3)

        sys_prompt = system_prompt or (
            "You are a high-speed, direct technical assistant. Answer factually based on the provided context."
        )

        user_content = query
        if context_text:
            user_content = f"Context:\n{context_text}\n\nQuestion: {query}"

        # 2. Fast VRAM Model Generation
        resp = self.gateway.completion(
            prompt=user_content,
            system_prompt=sys_prompt,
            max_tokens=max_tokens,
            temperature=0.1
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # 3. Optional Non-Blocking Background Job Dispatch
        deep_job_id = None
        if trigger_deep_job:
            j_type = deep_job_type or JobType.CUSTOM_BATCH_INFERENCE
            deep_job_id = self.dispatch_deep_job(
                job_type=j_type,
                payload={"query": query, "context": context_text, "preliminary_answer": resp.text}
            )

        return InteractiveChatResponse(
            query=query,
            answer=resp.text,
            citations=citations,
            latency_ms=round(duration_ms, 2),
            model_used=resp.model,
            deep_job_id=deep_job_id
        )

    def dispatch_deep_job(
        self,
        job_type: Union[JobType, str],
        payload: Dict[str, Any],
        priority: int = 2
    ) -> str:
        """
        Asynchronously dispatches a heavy batch job to the Back-Office Colibrì 744B queue.
        Returns job_id instantly (<10ms).
        """
        return self.job_queue.enqueue(job_type=job_type, payload=payload, priority=priority)
