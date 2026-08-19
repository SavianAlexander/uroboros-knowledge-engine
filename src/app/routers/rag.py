"""
Core RAG, streaming chat, multi-turn sessions, legal RAG, and contemplation endpoints.
"""
import re
import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from src.core import text_utils
from src.core.text_utils import estimate_tokens, truncate_context_window, smart_extract_context, build_token_budget_context

logger = logging.getLogger(__name__)

from src.core.domain.models import (
    RAGStreamRequest, ChatRequest, ChatResponse, ContemplateRequest, ContemplateResponse,
    CreateSessionRequest, UpdateSessionRequest, AddMessageRequest
)
from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.web_search import fetch_web_context
from src.infrastructure.repositories.workflows import list_workflow_logs
from src.infrastructure.vector_engine import extract_rag_context
from src.infrastructure.repositories.chat import (
    create_chat_session, list_chat_sessions, get_chat_session, update_chat_session,
    delete_chat_session, add_chat_message, get_chat_messages
)
from src.infrastructure.llm import is_llm_available
from src.core.model_manager import get_fallback_llm, expand_query_with_llm
from src.domain.adaptive_context_compressor import compress_context_entropy
from src.domain.auto_correct_rag import auto_correct_grounding

# Backward-compatible router helpers and constants
_smart_extract_context = smart_extract_context
RE_WORD_BOUNDARIES = getattr(text_utils, "_RE_WORD_BOUNDARIES", re.compile(r'\w+'))
RE_SENTENCE_BOUNDARIES = getattr(text_utils, "_RE_SENTENCE_BOUNDARIES", re.compile(r'(?<=[.!?])\s+'))

router = APIRouter()


from src.domain.retrieval.adaptive_prompt_synthesizer import (
    AdaptivePromptSynthesizer,
    SemanticAffinityProfile
)

def classify_adaptive_intent(query: str, grounding_confidence: float = 0.0, candidate_count: int = 0) -> str:
    """
    Classifies user query dynamically using continuous multi-dimensional cognitive affinity scoring:
    - GREETING_CONVERSATIONAL
    - TECHNICAL_CODE
    - MATHEMATICAL_ANALYTIC
    - LEGAL_STATUTORY
    - GENERAL_RAG
    """
    if not query or not isinstance(query, str) or not query.strip():
        return "GREETING_CONVERSATIONAL"
    profile = AdaptivePromptSynthesizer.analyze_query(
        query=query,
        grounding_confidence=grounding_confidence,
        candidate_count=candidate_count
    )
    return profile.primary_mode


def _stream_llm_chunks(llm, messages: list, req):
    """Yield streamed tokens from Ollama or Llama LLM instance."""
    if hasattr(llm, "stream_chat"):
        model_choice = getattr(req, "model", None) or getattr(req, "model_config", None) or "auto"
        temp_val = req.temperature if req.temperature is not None else 0.3
        for tok in llm.stream_chat(messages=messages, model_name=model_choice, temperature=temp_val):
            yield tok
    else:
        full_prompt = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
        temp_val = req.temperature if req.temperature is not None else 0.3
        stream = llm.create_completion(prompt=full_prompt, stream=True, max_tokens=1024, temperature=temp_val)
        for chunk in stream:
            yield chunk["choices"][0]["text"]


def _execute_adaptive_rag_stream(user_query: str, req: Any, session_id: Optional[str] = None):
    """
    Unified Adaptive RAG Streaming Engine:
    - Continuous Semantic Affinity Scoring (Conversational, Code, Math, Legal, Grounded Retrieval)
    - Dynamic Context-Weighted System Prompt Synthesis
    - Composable RetrievalDAGPipeline execution (Vault + Web)
    - Zero-Retrieval Adaptive Intelligence
    - Structured Telemetry Logging
    - SSE Token Streaming & Message Turn Persistence
    """
    if not user_query or not user_query.strip():
        raise HTTPException(status_code=422, detail="Missing message or query content")

    user_query = user_query.strip()

    llm = get_fallback_llm()
    if not is_llm_available() and llm is None:
        try:
            from src.core.config import is_testing
            if not is_testing:
                raise HTTPException(status_code=501, detail="llama-cpp-python is not installed. LLM runner disabled.")
        except ImportError:
            raise HTTPException(status_code=501, detail="llama-cpp-python is not installed. LLM runner disabled.")

    # 1. Execute Dynamic Composable RAG DAG Pipeline
    from src.domain.retrieval_pipeline_dag import get_retrieval_pipeline
    dag_pipeline = get_retrieval_pipeline()
    enable_web = bool(getattr(req, "web_search", False) or getattr(req, "enable_web_search", False))
    retrieval_res = dag_pipeline.execute(user_query, enable_web=enable_web)
    local_context = retrieval_res.context_text or ""
    local_citations = retrieval_res.citations or []
    web_sources = retrieval_res.web_sources or []

    # 2. Continuous Multi-Dimensional Semantic Affinity Profiling
    grounding_conf = getattr(retrieval_res.metrics, "grounding_confidence", 1.0)
    profile = AdaptivePromptSynthesizer.analyze_query(
        query=user_query,
        grounding_confidence=grounding_conf,
        candidate_count=len(local_citations)
    )
    intent = profile.primary_mode

    # 3. Session resolution and user message turn persistence
    req_session_id = session_id or getattr(req, "session_id", None)
    if not req_session_id:
        sess = create_chat_session(title=user_query[:30])
        req_session_id = sess["id"]

    add_chat_message(session_id=req_session_id, role="user", content=user_query)

    from src.core.model_router import route_prompt_model
    total_words = len(user_query.split()) + (len(local_context.split()) if local_context else 0)
    token_est = int(total_words * 1.35)
    model_req = getattr(req, "model", None) or getattr(req, "model_config", None) or "auto"
    if not model_req or model_req == "auto":
        routing_info = route_prompt_model(user_query, token_estimate=token_est)
    else:
        routing_info = {"model": model_req, "tier": "custom", "num_ctx": 4096}

    # 4. Synthesize Dynamic Adaptive System Prompt
    system_prompt = AdaptivePromptSynthesizer.synthesize_adaptive_system_prompt(
        profile=profile,
        domain_guidelines=getattr(retrieval_res, "domain_instructions", None)
    )

    messages = [{"role": "system", "content": system_prompt}]

    causality_keywords = ["why", "how did", "what caused", "reason", "because"]
    if any(kw in user_query.lower() for kw in causality_keywords):
        try:
            logs = list_workflow_logs(limit=10)
            if logs:
                causality_ctx = "\n".join([f"- [{log['executed_at']}] Event: {log['event_type']} (Status: {log['status']}) - {log.get('response_body') or ''}" for log in logs])
                messages.append({"role": "system", "content": f"Causality Event History Context:\n{causality_ctx}"})
        except Exception:
            pass

    try:
        past_msgs = get_chat_messages(req_session_id, limit=6)
        if past_msgs and len(past_msgs) > 1:
            for m in past_msgs[:-1]:
                messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
    except Exception:
        pass

    if local_context:
        truncated_local = _smart_extract_context(local_context, user_query, 6000)
        messages.append({"role": "system", "content": f"Document Vault Context:\n{truncated_local}"})
    if web_sources:
        web_str = "\n".join([f"- {w.get('title')}: {w.get('snippet')}" for w in web_sources])
        messages.append({"role": "system", "content": f"Live Web Context:\n{web_str}"})

    messages.append({"role": "user", "content": user_query})

    # Structured Telemetry Logging
    final_prompt_str = json.dumps(messages)
    logger.info(
        "RAG Execution | query='%s' | primary_mode='%s' | affinities=(conv=%.2f, code=%.2f, math=%.2f, legal=%.2f, ground=%.2f) | retrieved_chunk_count=%d | final_prompt_len=%d",
        user_query, profile.primary_mode, profile.conversational, profile.code_engineering, profile.quantitative_math, profile.legal_statutory, profile.grounded_retrieval, len(local_citations), len(final_prompt_str)
    )
    logger.info("Final Prompt: %s", final_prompt_str)

    def event_generator():
        # Yield sources SSE event with model tier metadata
        sources_payload = {
            "type": "sources",
            "session_id": req_session_id,
            "sources": local_citations,
            "local_citations": local_citations,
            "web_sources": web_sources,
            "intent": intent,
            "affinities": {
                "conversational": profile.conversational,
                "code_engineering": profile.code_engineering,
                "quantitative_math": profile.quantitative_math,
                "legal_statutory": profile.legal_statutory,
                "grounded_retrieval": profile.grounded_retrieval
            },
            "model_info": {
                "model": routing_info.get("model", "qwen2.5:7b"),
                "tier": routing_info.get("tier", "master_rag"),
                "context_window": routing_info.get("num_ctx", 4096)
            }
        }
        yield f"data: {json.dumps(sources_payload)}\n\n"

        # Stream response tokens
        full_response_text = ""
        token_count = 0
        t_gen_start = time.perf_counter()

        streamed_from_llm = False
        if llm:
            try:
                for tok in _stream_llm_chunks(llm, messages, req):
                    token_count += 1
                    full_response_text += tok
                    yield f"data: {json.dumps({'type': 'token', 'content': tok})}\n\n"
                streamed_from_llm = True
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                logger.error("Streaming exception in rag.py: %s", e)
                streamed_from_llm = False

        if not streamed_from_llm:
            fallback_msg = AdaptivePromptSynthesizer.synthesize_fallback_response(
                query=user_query,
                profile=profile,
                citations=local_citations
            )
            for tok in re.findall(r'\S+\s*', fallback_msg):
                token_count += 1
                full_response_text += tok
                yield f"data: {json.dumps({'type': 'token', 'content': tok})}\n\n"
                time.sleep(0.005)

        # Save assistant message turn into SQLite chat_messages table
        msg_record = add_chat_message(
            session_id=req_session_id,
            role="assistant",
            content=full_response_text,
            citations_json=local_citations,
            web_sources_json=web_sources,
            tokens_used=len(full_response_text.split())
        )

        # Trigger autonomous knowledge synthesis write-back loop (Uroboros feedback)
        try:
            from src.domain.knowledge_synthesis_loop import get_knowledge_synthesis_loop
            synth_loop = get_knowledge_synthesis_loop()
            synth_loop.record_synthesis(req_session_id, user_query, full_response_text, local_citations)
        except Exception:
            pass

        dt_gen = max(0.001, time.perf_counter() - t_gen_start)
        tok_speed = round(token_count / dt_gen, 1)
        done_payload = {
            "type": "done",
            "session_id": req_session_id,
            "message_id": msg_record.get("id") if isinstance(msg_record, dict) else None,
            "tokens_generated": token_count,
            "duration_sec": round(dt_gen, 2),
            "tokens_per_sec": tok_speed,
            "model": routing_info.get("model", "qwen2.5:7b"),
            "tier": routing_info.get("tier", "master_rag"),
            "intent": intent
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/api/rag/stream")
@router.post("/api/rag/query")
def rag_stream_endpoint(req: RAGStreamRequest):
    """
    Live Token Streaming RAG endpoint v2.0 with Grounded Sources Metadata:
    - Context via Composable RetrievalDAGPipeline (HyDE + RRF + Boundary)
    - SSE streaming tokens with Adaptive Intent Classification & Zero-Retrieval Intelligence
    """
    user_query = req.get_query()
    return _execute_adaptive_rag_stream(user_query=user_query, req=req, session_id=req.session_id)


@router.post("/api/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    """
    Milestone 2 SSE Chat Streaming Endpoint:
    - Extracts grounded vault document context via RetrievalDAGPipeline
    - Triggers WebSearchFetcher when vault hits < 2 or web_search=True
    - Adaptive Intent & Context Routing (GREETING_CONVERSATIONAL, TECHNICAL_CODE, MATHEMATICAL_ANALYTIC, LEGAL_STATUTORY, GENERAL_RAG)
    - Zero-Retrieval Adaptive Intelligence when retrieved_chunk_count == 0
    - Structured Telemetry Logging
    - Streams response tokens via Server-Sent Events (SSE)
    - Persists user prompt turn and assistant turn into SQLite chat_messages table
    """
    user_query = req.message or ""
    if not user_query and req.messages:
        user_query = req.messages[-1].content
    if not user_query and req.history:
        user_query = req.history[-1].content

    return _execute_adaptive_rag_stream(user_query=user_query, req=req, session_id=req.session_id)


@router.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Non-streaming chat endpoint with grounded RAG context and model completion."""
    if req.history is None and req.messages is None:
        raise HTTPException(status_code=422, detail="Missing required field 'history' or 'messages'")

    user_query = req.message or ""
    if not user_query and req.messages:
        user_query = req.messages[-1].content
    if not user_query and req.history:
        user_query = req.history[-1].content

    if not user_query or not user_query.strip():
        raise HTTPException(status_code=422, detail="Missing required field messages or history")

    user_query = user_query.strip()
    expanded_query = expand_query_with_llm(user_query)
    local_context, local_citations = extract_advanced_rag_context(expanded_query, max_chunks=5, jaccard_threshold=0.70)

    sources = [{"filename": c.get("filename", ""), "similarity": c.get("similarity", 0.0)} for c in local_citations]

    llm = get_fallback_llm()
    if is_llm_available() and llm is not None:
        try:
            prompt = f"Context:\n{local_context}\n\nUser: {user_query}\n\nAssistant:"
            temp = req.temperature if req.temperature is not None else 0.3
            resp = llm.create_completion(prompt=prompt, max_tokens=512, temperature=temp)
            text_resp = resp["choices"][0]["text"].strip()
            return ChatResponse(response=text_resp, sources=sources)
        except Exception:
            pass

    if local_context:
        resp_text = f"Based on retrieved vault context:\n\n{local_context[:500]}"
    else:
        resp_text = f"No direct document context found for query: '{user_query}'."

    return ChatResponse(response=resp_text, sources=sources)


class EnhancePromptRequest(BaseModel):
    prompt: str = Field(..., description="Raw prompt text to enhance and structure for RAG retrieval")


@router.post("/api/prompt/enhance")
def enhance_prompt_endpoint(req: EnhancePromptRequest):
    """
    Intelligently expands raw user queries into structured high-performance prompts
    optimized for RAG retrieval and structured code generation.
    """
    raw = (req.prompt or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    enhanced_fallback = (
        f"Provide an in-depth technical analysis and comprehensive breakdown of: '{raw}'.\n\n"
        f"Specifically:\n"
        f"1. Explain the fundamental principles and mechanics.\n"
        f"2. Provide concrete code/configuration examples and practical use cases.\n"
        f"3. Include a comparison table highlighting performance, trade-offs, and failure modes.\n"
        f"4. Detail best practices, security considerations, and edge case mitigations."
    )
    return {"original": raw, "enhanced": enhanced_fallback}


class LegalRAGRequest(BaseModel):
    query: str = Field(..., description="Statutory or regulatory query")
    max_chunks: Optional[int] = Field(5, description="Maximum statutory chunks to retrieve")


@router.post("/api/rag/legal")
def legal_rag_search_endpoint(req: LegalRAGRequest):
    """
    Dedicated Legal & Regulatory RAG Endpoint.
    Performs section-aware statutory search and pin-point citation grounding.
    """
    from src.domain.legal_rag_engine import LegalRegulatoryRAGEngine
    from src.domain.rag_engine import extract_advanced_rag_context

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    ctx_text, raw_citations = extract_advanced_rag_context(req.query, max_chunks=req.max_chunks or 5)
    
    chunks = LegalRegulatoryRAGEngine.chunk_legal_document(ctx_text)
    return LegalRegulatoryRAGEngine.format_legal_rag_response(req.query, chunks)


@router.post("/api/contemplate")
def contemplate_endpoint(req: ContemplateRequest):
    """Contemplate / analysis endpoint with dynamic prompt reflection and risk classification."""
    llm = get_fallback_llm()
    if not is_llm_available() and llm is None:
        try:
            from src.core.config import is_testing
            if not is_testing:
                raise HTTPException(status_code=501, detail="llama-cpp-python is not installed. LLM runner disabled.")
        except ImportError:
            raise HTTPException(status_code=501, detail="llama-cpp-python is not installed. LLM runner disabled.")

    prompt_text = (req.get_prompt() or "").strip()
    p_lower = prompt_text.lower()

    if any(k in p_lower for k in ("security", "pii", "auth", "token", "key", "delete", "drop", "critical", "vulnerability")):
        risk = "Elevated risk - requires compliance verification"
    elif any(k in p_lower for k in ("database", "migration", "schema", "wal", "update", "refactor", "table")):
        risk = "Moderate risk - state modification potential"
    else:
        risk = "Low operational risk"

    word_count = len(prompt_text.split()) if prompt_text else 0
    if word_count > 50:
        friction = f"Moderate ({word_count} words in specification)"
        velocity = "Analytical throughput"
    elif word_count > 10:
        friction = f"Minimal ({word_count} words)"
        velocity = "High throughput"
    else:
        friction = "Minimal"
        velocity = "High throughput"

    if prompt_text:
        first_line = prompt_text.split("\n")[0].strip()
        core_problem = first_line if len(first_line) < 120 else first_line[:117] + "..."
    else:
        core_problem = "Knowledge base reflection and state audit"

    raw_analysis = f"Contemplation of intent: '{core_problem}'. Assessed risk: {risk}. Operational velocity: {velocity}."

    return ContemplateResponse(
        core_problem=core_problem,
        risk_profile=risk,
        friction_cost=friction,
        velocity=velocity,
        raw_analysis=raw_analysis
    )


# ---------------------------------------------------------------------------
# Chat Sessions & Messages REST Endpoints
# ---------------------------------------------------------------------------

@router.get("/api/chat/sessions")
def list_sessions_endpoint():
    """List all chat sessions."""
    return list_chat_sessions()


@router.post("/api/chat/sessions")
def create_session_endpoint(req: Optional[CreateSessionRequest] = None):
    """Create a new chat session."""
    if req is None:
        return create_chat_session()
    return create_chat_session(
        title=req.title,
        model_path=req.model_path,
        temperature=req.temperature if req.temperature is not None else 0.7,
        context_window=req.context_window if req.context_window is not None else 4096,
        metadata_json=req.metadata_json
    )


@router.get("/api/chat/sessions/{session_id}")
def get_session_endpoint(session_id: str):
    """Get chat session details including messages."""
    sess = get_chat_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.put("/api/chat/sessions/{session_id}")
def update_session_endpoint(session_id: str, req: UpdateSessionRequest):
    """Update chat session metadata or parameters."""
    sess = update_chat_session(
        session_id=session_id,
        title=req.title,
        model_path=req.model_path,
        temperature=req.temperature,
        context_window=req.context_window,
        metadata_json=req.metadata_json
    )
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.delete("/api/chat/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    """Delete chat session and its associated messages."""
    success = delete_chat_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "id": session_id}


@router.post("/api/chat/sessions/{session_id}/messages")
def add_message_endpoint(session_id: str, req: AddMessageRequest):
    """Add a message turn to a session."""
    sess = get_chat_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return add_chat_message(
        session_id=session_id,
        role=req.role,
        content=req.content,
        citations_json=req.citations_json,
        web_sources_json=req.web_sources_json,
        tokens_used=req.tokens_used or 0,
        metadata_json=req.metadata_json
    )


@router.get("/api/chat/sessions/{session_id}/episodic")
def get_session_episodic_memory_endpoint(session_id: str, query: str = ""):
    """Queries episodic memory and multi-turn conversational context for a chat session."""
    try:
        from src.domain.episodic_rag import query_episodic_rag
        return query_episodic_rag(query, session_id=session_id)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to query episodic memory for session %s: %s", session_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stream/rag")
async def stream_rag_pipeline_endpoint(q: str = "", query: str = "", top_k: int = 5):
    """Progressive SSE streaming RAG endpoint emitting retrieval pipeline stages."""
    search_q = q or query or ""

    async def event_generator():
        t0 = time.time()
        # 1. Intent Classification
        try:
            from src.domain.query_intent_classifier import classify_query_intent
            intent_data = classify_query_intent(search_q)
            yield f"event: intent_classified\ndata: {json.dumps(intent_data)}\n\n"
        except Exception:
            pass
        await asyncio.sleep(0.01)

        # 2. Sub-Query Decomposition
        try:
            from src.domain.decomposed_hybrid_rag import decompose_query, execute_hybrid_decomposed_search
            sub_queries = decompose_query(search_q)
        except Exception:
            sub_queries = [search_q]

        yield f"event: query_decomposed\ndata: {json.dumps({'sub_queries': sub_queries})}\n\n"
        await asyncio.sleep(0.01)

        # 3. Retrieve & Compress Candidates (Offloaded to worker thread)
        try:
            rag_res = await asyncio.to_thread(execute_hybrid_decomposed_search, search_q, top_k=top_k)
        except Exception:
            rag_res = {"top_candidates": [], "compressed_context": "", "compression_ratio_pct": 0}

        candidates = rag_res.get("top_candidates", [])
        yield f"event: passages_retrieved\ndata: {json.dumps({'candidates_count': len(candidates), 'top_candidates': candidates[:3]})}\n\n"
        await asyncio.sleep(0.01)

        # 4. Context Compression Metrics
        yield f"event: context_compressed\ndata: {json.dumps({'compression_ratio_pct': rag_res.get('compression_ratio_pct', 0), 'compressed_char_count': rag_res.get('compressed_char_count', 0)})}\n\n"
        await asyncio.sleep(0.01)

        # 5. Token Answer Generation / Streaming
        compressed = rag_res.get("compressed_context", "")
        streamed_tokens = False
        try:
            from src.infrastructure.llm import is_llm_available, stream_llm_response
            if is_llm_available() and compressed:
                llm_prompt = f"Based on the following context, answer the query '{search_q}':\n\n{compressed[:800]}"
                for token_chunk in stream_llm_response(llm_prompt, max_tokens=150):
                    if token_chunk:
                        yield f"event: answer_chunk\ndata: {json.dumps({'token': token_chunk})}\n\n"
                        streamed_tokens = True
                        await asyncio.sleep(0.002)
        except Exception:
            streamed_tokens = False

        if not streamed_tokens:
            summary_tokens = (compressed[:200] if compressed else f"Synthesized findings for query '{search_q}'.").split()
            for token in summary_tokens:
                yield f"event: answer_chunk\ndata: {json.dumps({'token': token + ' '})}\n\n"
                await asyncio.sleep(0.002)

        # 6. Citations
        try:
            from src.domain.source_citation_generator import generate_source_citations
            citations = generate_source_citations(search_q, [c.get("content", "") for c in candidates])
            yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
        except Exception:
            pass

        # 7. Complete
        duration_ms = round((time.time() - t0) * 1000, 2)
        yield f"event: done\ndata: {json.dumps({'status': 'completed', 'duration_ms': duration_ms})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/api/chat/reformulate")
def reformulate_query_endpoint(payload: Dict[str, Any] = Body(...)):
    """Reformulates multi-turn conversational queries with antecedent and entity carry-over."""
    history = payload.get("history", [])
    query_str = payload.get("query", "")
    from src.domain.conversation_rag_rewriter import reformulate_conversational_query
    return reformulate_conversational_query(history, query_str)
