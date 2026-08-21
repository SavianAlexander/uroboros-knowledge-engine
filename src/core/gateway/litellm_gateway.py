"""
Production Universal Model Gateway.
Primary Engine: litellm (acompletion, completion, aembedding, embedding).
Supports provider-agnostic execution across Ollama, OpenAI, Anthropic, and Gemini.
Resilient Fallback: Built-in local HTTP client & fallback LLM adapter.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for LiteLLM
HAS_LITELLM = False
try:
    import litellm
    from litellm import completion, acompletion, embedding, aembedding
    litellm.suppress_debug_info = True
    HAS_LITELLM = True
except (ImportError, Exception) as e:
    HAS_LITELLM = False
    logger.info("LiteLLM library not available, using built-in model gateway fallback: %s", e)


class GatewayCompletionRequest(BaseModel):
    """Pydantic v2 schema for completion calls."""
    model: str = Field(default="ollama/qwen2.5:7b", description="LiteLLM model identifier")
    messages: List[Dict[str, str]] = Field(..., description="Chat message history")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    timeout: float = Field(default=30.0, ge=1.0)
    api_key: Optional[str] = None
    api_base: Optional[str] = None


class GatewayCompletionResponse(BaseModel):
    """Pydantic v2 schema for completion responses."""
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"
    gateway_engine: str = "litellm"


class UniversalModelGateway:
    """
    Universal model gateway executing LLM and embedding calls across heterogeneous backends.
    """

    @staticmethod
    def is_litellm_available() -> bool:
        """Checks if litellm gateway is available."""
        return HAS_LITELLM

    @staticmethod
    async def complete_async(request: GatewayCompletionRequest) -> GatewayCompletionResponse:
        """
        Executes an asynchronous chat completion call.
        """
        # 1. Primary Engine: LiteLLM
        if HAS_LITELLM:
            try:
                kwargs: Dict[str, Any] = {
                    "model": request.model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "timeout": request.timeout
                }
                if request.api_key:
                    kwargs["api_key"] = request.api_key
                if request.api_base:
                    kwargs["api_base"] = request.api_base

                resp = await acompletion(**kwargs)
                choices = getattr(resp, "choices", [])
                content = choices[0].message.content if choices else ""
                usage = getattr(resp, "usage", None)
                
                return GatewayCompletionResponse(
                    content=content,
                    model=request.model,
                    prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else len(str(request.messages).split()),
                    completion_tokens=getattr(usage, "completion_tokens", 0) if usage else len(content.split()),
                    total_tokens=getattr(usage, "total_tokens", 0) if usage else len(str(request.messages).split()) + len(content.split()),
                    gateway_engine="litellm"
                )
            except Exception as e:
                logger.warning("LiteLLM completion call failed, falling back to local provider: %s", e)

        # 2. Resilient Fallback Engine: Local provider / model manager
        return await UniversalModelGateway._fallback_completion(request)

    @staticmethod
    def complete_sync(request: GatewayCompletionRequest) -> GatewayCompletionResponse:
        """Synchronous wrapper for completion."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, UniversalModelGateway.complete_async(request)).result()
            return loop.run_until_complete(UniversalModelGateway.complete_async(request))
        except RuntimeError:
            return asyncio.run(UniversalModelGateway.complete_async(request))

    @staticmethod
    async def get_embedding_async(text: str, model: str = "ollama/nomic-embed-text") -> List[float]:
        """
        Asynchronously generates dense vector embeddings.
        """
        if HAS_LITELLM:
            try:
                resp = await aembedding(model=model, input=[text])
                data = getattr(resp, "data", [])
                if data and hasattr(data[0], "embedding"):
                    return list(data[0].embedding)
            except Exception as e:
                logger.warning("LiteLLM embedding call failed, falling back to local embedder: %s", e)

        from src.core.embeddings import generate_embedding
        return generate_embedding(text)

    @staticmethod
    async def _fallback_completion(request: GatewayCompletionRequest) -> GatewayCompletionResponse:
        """Fallback completion using internal model manager."""
        from src.core.model_manager import get_fallback_llm
        from src.core.config import is_testing

        if is_testing:
            # Deterministic test stub
            user_msg = next((m["content"] for m in reversed(request.messages) if m.get("role") == "user"), "query")
            return GatewayCompletionResponse(
                content=f"Synthesized response for: {user_msg}",
                model="test-fallback",
                prompt_tokens=10,
                completion_tokens=8,
                total_tokens=18,
                gateway_engine="test_fixture_gateway"
            )

        llm = get_fallback_llm()
        if llm:
            completion_dict = llm.create_chat_completion(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            content = completion_dict["choices"][0]["message"]["content"]
            usage = completion_dict.get("usage", {})
            return GatewayCompletionResponse(
                content=content,
                model="local-llm",
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                gateway_engine="local_model_manager"
            )

        # Fallback message
        return GatewayCompletionResponse(
            content="Standard gateway response (No active LLM weights configured).",
            model="null-gateway",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            gateway_engine="safe_fallback"
        )
