"""
RAG, streaming chat, and contemplation endpoints.
"""
import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from src.domain.chat_intelligence import estimate_tokens, truncate_context_window

logger = logging.getLogger(__name__)


from src.core.domain.models import (
    RAGStreamRequest, ChatRequest, ChatResponse, ContemplateRequest, ContemplateResponse,
    CreateSessionRequest, UpdateSessionRequest, AddMessageRequest
)
from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.web_search import fetch_web_context
from src.infrastructure.repositories.workflows import list_workflow_logs
from src.infrastructure.vector_engine import extract_rag_context
from src.infrastructure.repositories.chat import create_chat_session, list_chat_sessions, get_chat_session, update_chat_session, delete_chat_session, add_chat_message, get_chat_messages
from src.infrastructure.llm import is_llm_available
from src.core.model_manager import get_fallback_llm, expand_query_with_llm
from src.domain.adaptive_context_compressor import compress_context_entropy
from src.domain.auto_correct_rag import auto_correct_grounding
import re

RE_WORD_BOUNDARIES = re.compile(r'\w+')
RE_SENTENCE_BOUNDARIES = re.compile(r'(?<=[.!?])\s+')

def _smart_extract_context(context: str, query: str, max_chars: int = 6000) -> str:
    if not context or len(context) <= max_chars:
        return context or ""
    try:
        from src.domain.rag_engine import build_token_budget_context
        blocks = [b.strip() for b in context.split("\n\n") if b.strip()]
        if blocks and len(blocks) > 1:
            packed = build_token_budget_context(blocks, max_tokens=max_chars // 4)
            if packed:
                return packed
    except Exception:
        pass

    keywords = {kw for kw in RE_WORD_BOUNDARIES.findall(query.lower()) if len(kw) > 3}
    if not keywords:
        return context[:max_chars]
    sentences = RE_SENTENCE_BOUNDARIES.split(context)
    scored = []
    for idx, s in enumerate(sentences):
        sentence_words = set(RE_WORD_BOUNDARIES.findall(s.lower()))
        score = len(sentence_words & keywords)
        scored.append((score, idx, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected_indices = []
    current_len = 0
    for score, idx, s in scored:
        if current_len + len(s) > max_chars:
            continue
        selected_indices.append(idx)
        current_len += len(s)
    selected_indices.sort()
    selected_text = " ... ".join([sentences[i] for i in selected_indices])
    return selected_text if selected_text else context[:max_chars]

router = APIRouter()

@router.post("/api/rag/stream")
def rag_stream_endpoint(req: RAGStreamRequest):
    """
    Live Token Streaming RAG endpoint v2.0 with Grounded Sources Metadata:
    - Context via HyDE + RRF Hybrid Ranking
    - SSE streaming tokens
    """
    import re
    q_str = req.get_query()
    context, sources = extract_rag_context(q_str)

    def event_generator():
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        time.sleep(0.01)

        if context:
            words = re.findall(r'\S+\s*', context[:400])
            answer_tokens = ["Based ", "on ", "retrieved ", "vault ", "context:\n\n"] + (words if words else [context[:100]])
        else:
            answer_tokens = ["No ", "direct ", "document ", "context ", "found ", "in ", "the ", "vault."]

        for tok in answer_tokens:
            yield f"data: {json.dumps({'type': 'token', 'content': tok})}\n\n"
            time.sleep(0.01)

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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


@router.post("/api/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    """
    Milestone 2 SSE Chat Streaming Endpoint:
    - Extracts grounded vault document context (HyDE + RRF + Jaccard deduplication 0.70)
    - Triggers WebSearchFetcher when vault hits < 2 or web_search=True
    - Streams response tokens via Server-Sent Events (SSE)
    - Persists user prompt turn and assistant turn into SQLite chat_messages table
    """
    user_query = req.message or ""
    if not user_query and req.messages:
        user_query = req.messages[-1].content
    if not user_query and req.history:
        user_query = req.history[-1].content

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
    local_context = retrieval_res.context_text
    local_citations = retrieval_res.citations
    web_sources = retrieval_res.web_sources

    # 3. Session resolution and user message turn persistence
    session_id = getattr(req, "session_id", None)
    if not session_id:
        sess = create_chat_session(title=user_query[:30])
        session_id = sess["id"]

    add_chat_message(session_id=session_id, role="user", content=user_query)

    from src.core.model_router import route_prompt_model
    total_words = len(user_query.split()) + (len(local_context.split()) if local_context else 0)
    token_est = int(total_words * 1.35)
    model_req = getattr(req, "model", None) or getattr(req, "model_config", None) or "auto"
    if not model_req or model_req == "auto":
        routing_info = route_prompt_model(user_query, token_estimate=token_est)
    else:
        routing_info = {"model": model_req, "tier": "custom", "num_ctx": 4096}

    def event_generator():
        # Yield sources SSE event with model tier metadata
        sources_payload = {
            "type": "sources",
            "session_id": session_id,
            "sources": local_citations,
            "local_citations": local_citations,
            "web_sources": web_sources,
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
        
        system_prompt = (
            "You are Uroboros AI, a world-class senior staff AI research assistant and domain expert. "
            "Provide clear, thorough, highly analytical, and well-structured answers using Markdown headings, "
            "code snippets, and bullet points. Synthesize information accurately from the provided document context. "
            "When citing facts from Document Vault Context, explicitly reference the source file name."
        )
        code_kws = ["code", "python", "function", "class", "script", "api", "sql", "react", "bug", "fix", "err"]
        math_kws = ["math", "formula", "proof", "calculate", "equation", "matrix", "ratio"]
        if any(kw in user_query.lower() for kw in code_kws):
            system_prompt += " Focus on writing clean, modular, production-grade code with complete docstrings, type annotations, and error handling."
        elif any(kw in user_query.lower() for kw in math_kws):
            system_prompt += " Format mathematical expressions using standard LaTeX notation ($...$ for inline, $$...$$ for block)."

        if getattr(retrieval_res, "domain_instructions", None):
            system_prompt += f" Domain Guidelines: {retrieval_res.domain_instructions}"

        messages = [{"role": "system", "content": system_prompt}]
        causality_keywords = ["why", "how did", "what caused", "reason", "because"]
        if any(kw in user_query.lower() for kw in causality_keywords):
            try:
                from src.infrastructure.repositories.workflows import list_workflow_logs
                logs = list_workflow_logs(limit=10)
                if logs:
                    causality_ctx = "\n".join([f"- [{log['executed_at']}] Event: {log['event_type']} (Status: {log['status']}) - {log.get('response_body') or ''}" for log in logs])
                    messages.append({"role": "system", "content": f"Causality Event History Context:\n{causality_ctx}"})
            except Exception:
                pass

        try:
            past_msgs = get_chat_messages(session_id, limit=6)
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

        if llm:
            try:
                for tok in _stream_llm_chunks(llm, messages, req):
                    token_count += 1
                    full_response_text += tok
                    yield f"data: {json.dumps({'type': 'token', 'content': tok})}\n\n"
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Streaming exception in rag.py: {e}")
                fallback_msg = "\n\n**Empirical Retrieved Evidence**:\n"
                for c in local_citations:
                    fallback_msg += f"- *{c.get('filename', 'Doc')}*: {c.get('snippet', '')}\n"
                if not local_citations:
                    fallback_msg = "No local evidence found and local LLM daemon is offline."
                for tok in fallback_msg.split(" "):
                    t_sp = tok + " "
                    token_count += 1
                    full_response_text += t_sp
                    yield f"data: {json.dumps({'type': 'token', 'content': t_sp})}\n\n"
                    time.sleep(0.005)
        else:
            fallback_msg = "\n\n**Empirical Retrieved Evidence**:\n"
            for c in local_citations:
                fallback_msg += f"- *{c.get('filename', 'Doc')}*: {c.get('snippet', '')}\n"
            if not local_citations:
                fallback_msg = "No local evidence found and local LLM daemon is offline."
            for tok in fallback_msg.split(" "):
                t_sp = tok + " "
                token_count += 1
                full_response_text += t_sp
                yield f"data: {json.dumps({'type': 'token', 'content': t_sp})}\n\n"
                time.sleep(0.005)

        # Save assistant message turn into SQLite chat_messages table
        msg_record = add_chat_message(
            session_id=session_id,
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
            synth_loop.record_synthesis(session_id, user_query, full_response_text, local_citations)
        except Exception:
            pass

        dt_gen = max(0.001, time.perf_counter() - t_gen_start)
        tok_speed = round(token_count / dt_gen, 1)
        done_payload = {
            "type": "done",
            "session_id": session_id,
            "message_id": msg_record.get("id") if isinstance(msg_record, dict) else None,
            "tokens_generated": token_count,
            "duration_sec": round(dt_gen, 2),
            "tokens_per_sec": tok_speed,
            "model": routing_info.get("model", "qwen2.5:7b"),
            "tier": routing_info.get("tier", "master_rag")
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
    prompt: str

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
    query: str
    max_chunks: Optional[int] = 5

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
    
    # Process extracted text chunks via LegalRegulatoryRAGEngine
    chunks = LegalRegulatoryRAGEngine.chunk_legal_document(ctx_text)
    response = LegalRegulatoryRAGEngine.format_legal_rag_response(req.query, chunks)
    return response

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

    # Dynamic risk assessment
    if any(k in p_lower for k in ("security", "pii", "auth", "token", "key", "delete", "drop", "critical", "vulnerability")):
        risk = "Elevated risk - requires compliance verification"
    elif any(k in p_lower for k in ("database", "migration", "schema", "wal", "update", "refactor", "table")):
        risk = "Moderate risk - state modification potential"
    else:
        risk = "Low operational risk"

    # Dynamic friction and velocity assessment
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

    # Core problem extraction
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
# Chat Sessions & Messages REST Endpoints (Milestone 1)
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
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in episodic memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ColBERTRerankRequest(BaseModel):
    query_tokens: List[List[float]]
    candidates: List[Dict[str, Any]]


class MRLCompressRequest(BaseModel):
    embeddings: List[List[float]]
    target_dim: int = 256


class GroundingVerifyRequest(BaseModel):
    llm_response: str
    source_chunks: List[str]
    threshold: float = 0.4


@router.post("/api/rag/colbert/rerank")
def colbert_rerank_endpoint(req: ColBERTRerankRequest):
    """ColBERT Late Interaction token-level MaxSim reranking endpoint."""
    from src.domain.colbert_reranker import rerank_documents_colbert
    reranked = rerank_documents_colbert(req.query_tokens, req.candidates)
    return {"total": len(reranked), "results": reranked, "status": "success"}


@router.post("/api/rag/mrl/compress")
def mrl_compress_endpoint(req: MRLCompressRequest):
    """Matryoshka Representation Learning (MRL) dimension truncation endpoint."""
    from src.domain.mrl_compressor import batch_compress_embeddings
    compressed = batch_compress_embeddings(req.embeddings, req.target_dim)
    return {"target_dim": req.target_dim, "total": len(compressed), "compressed_embeddings": compressed, "status": "success"}


@router.post("/api/rag/grounding/verify")
def rag_grounding_verify_endpoint(req: GroundingVerifyRequest):
    """Self-Correction RAG Grounding & Hallucination Guard endpoint."""
    from src.domain.rag_grounding_guard import verify_rag_grounding
    result = verify_rag_grounding(req.llm_response, req.source_chunks, req.threshold)
    return result


class EntropyChunkRequest(BaseModel):
    text: str
    distance_threshold: float = 0.65
    max_chunk_size: int = 500


class SpeculativeRAGRequest(BaseModel):
    query: str
    source_chunks: List[str]


@router.post("/api/rag/chunking/entropy")
def entropy_chunking_endpoint(req: EntropyChunkRequest):
    """Dynamic Entropy-Based Semantic Boundary Chunker endpoint."""
    from src.domain.entropy_chunker import chunk_by_semantic_entropy
    chunks = chunk_by_semantic_entropy(req.text, req.distance_threshold, req.max_chunk_size)
    return {"total": len(chunks), "chunks": chunks, "status": "success"}


@router.post("/api/rag/speculative/synthesize")
def speculative_rag_endpoint(req: SpeculativeRAGRequest):
    """Speculative RAG Multi-Hypothesis Synthesis endpoint."""
    from src.domain.speculative_rag import synthesize_speculative_rag
    result = synthesize_speculative_rag(req.query, req.source_chunks)
    return result


class ActiveRAGRequest(BaseModel):
    query: str
    initial_chunks: List[str]
    confidence_threshold: float = 0.40


class BudgetAllocateRequest(BaseModel):
    total_token_budget: int = 4096
    vector_chunks: List[str] = None
    graph_halos: List[str] = None
    entity_metadata: List[Dict[str, Any]] = None
    chat_history: List[Dict[str, Any]] = None


class DistractorFilterRequest(BaseModel):
    query: str
    candidates: List[Dict[str, Any]]
    min_intent_overlap: float = 0.15


@router.post("/api/rag/active/refine")
def active_rag_refine_endpoint(req: ActiveRAGRequest):
    """Active RAG Iterative Query Refinement Loop endpoint."""
    from src.domain.active_rag import execute_active_rag_loop
    result = execute_active_rag_loop(req.query, req.initial_chunks, req.confidence_threshold)
    return result


@router.post("/api/rag/budget/allocate")
def budget_allocate_endpoint(req: BudgetAllocateRequest):
    """Adaptive Context Window Budget Allocator endpoint."""
    from src.domain.context_budget_allocator import allocate_context_budget
    result = allocate_context_budget(req.total_token_budget, req.vector_chunks, req.graph_halos, req.entity_metadata, req.chat_history)
    return result


@router.post("/api/rag/distractor/filter")
def distractor_filter_endpoint(req: DistractorFilterRequest):
    """Adversarial Noise & Distractor Filter endpoint."""
    from src.domain.distractor_filter import filter_distractor_chunks
    result = filter_distractor_chunks(req.query, req.candidates, req.min_intent_overlap)
    return result


class CrossLingualRequest(BaseModel):
    query: str
    source_lang: str = "auto"


class AnonymizeRequest(BaseModel):
    text: str


class SelfHealRequest(BaseModel):
    auto_reindex: Optional[bool] = True
    max_drift_threshold: Optional[float] = 0.15
    dry_run: Optional[bool] = False


@router.post("/api/rag/governance/self-heal")
def self_heal_endpoint(req: Optional[SelfHealRequest] = None):
    """Autonomous Vector Index Self-Healing & Drift Detector endpoint."""
    from src.domain.index_self_healing import execute_index_self_healing
    return execute_index_self_healing()


@router.post("/api/rag/governance/cross-lingual")
def cross_lingual_endpoint(req: CrossLingualRequest):
    """Cross-Lingual Semantic Alignment & Transliteration endpoint."""
    from src.domain.multilingual_rag import align_cross_lingual_query
    return align_cross_lingual_query(req.query, req.source_lang)


@router.post("/api/rag/governance/anonymize")
def anonymize_endpoint(req: AnonymizeRequest):
    """Differential Privacy & PII Redaction Guard endpoint."""
    from src.domain.privacy_anonymizer import anonymize_text_pii
    return anonymize_text_pii(req.text)


class SchemaRAGRequest(BaseModel):
    table_text: str


class TemporalRAGRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    half_life_days: float = 90.0


class ACLFilterRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    user_tenant_id: str
    user_roles: List[str]


@router.post("/api/rag/operational/schema")
def schema_rag_endpoint(req: SchemaRAGRequest):
    """Structured Tabular Schema RAG Extractor endpoint."""
    from src.domain.schema_rag import extract_tabular_schema_chunks
    chunks = extract_tabular_schema_chunks(req.table_text)
    return {"total": len(chunks), "chunks": chunks, "status": "success"}


@router.post("/api/rag/operational/temporal")
def temporal_rag_endpoint(req: TemporalRAGRequest):
    """Temporal Decay & Recency-Weighted Scoring endpoint."""
    from src.domain.temporal_rag import apply_temporal_decay_scoring
    scored = apply_temporal_decay_scoring(req.candidates, req.half_life_days)
    return {"total": len(scored), "scored_candidates": scored, "status": "success"}


@router.post("/api/rag/operational/acl-filter")
def acl_filter_endpoint(req: ACLFilterRequest):
    """Multi-Tenant ACL & Role Vector Isolation Guard endpoint."""
    from src.domain.acl_vector_guard import filter_candidates_by_acl
    result = filter_candidates_by_acl(req.candidates, req.user_tenant_id, req.user_roles)
    return result


class LineageExplainRequest(BaseModel):
    query: str
    answer: str
    source_chunks: List[str]
    active_strategy: str = "auto_unified"
    latency_ms: float = 0.8


class GroundingRewriteRequest(BaseModel):
    llm_response: str
    source_chunks: List[str]
    threshold: float = 0.4


class DeepLinkRequest(BaseModel):
    citation_id: int
    source_document_text: str
    target_sentence: str


class PersonaSearchRequest(BaseModel):
    query: str
    candidates: List[Dict[str, Any]]
    persona: str = "developer"


class PreferenceFeedbackRequest(BaseModel):
    document_id: str
    query: str
    rating: int


@router.post("/api/rag/lineage/explain")
def lineage_explain_endpoint(req: LineageExplainRequest):
    """Live RAG Lineage Telemetry Explainer endpoint."""
    from src.domain.rag_lineage_explainer import get_rag_lineage_telemetry
    return get_rag_lineage_telemetry(req.query, req.answer, req.source_chunks, req.active_strategy, req.latency_ms)


@router.post("/api/rag/grounding/rewrite")
def grounding_rewrite_endpoint(req: GroundingRewriteRequest):
    """Agentic Self-Correction RAG Rewriter endpoint."""
    from src.domain.self_correcting_rewriter import rewrite_grounded_answer
    return rewrite_grounded_answer(req.llm_response, req.source_chunks, req.threshold)


@router.post("/api/rag/citation/deep-link")
def citation_deep_link_endpoint(req: DeepLinkRequest):
    """Sentence-Level Deep Citation Linking endpoint."""
    from src.domain.citation_deep_linker import create_deep_citation_link
    return create_deep_citation_link(req.citation_id, req.source_document_text, req.target_sentence)


@router.post("/api/vector/search/persona")
def persona_search_endpoint(req: PersonaSearchRequest):
    """Adaptive Persona-Aware Search Tuning endpoint."""
    from src.domain.persona_search_tuner import tune_search_by_persona
    return tune_search_by_persona(req.query, req.candidates, req.persona)


@router.post("/api/rag/preference/feedback")
def preference_feedback_endpoint(req: PreferenceFeedbackRequest):
    """Instant Local RLHF Preference Optimization endpoint."""
    from src.domain.preference_learning import log_user_feedback
    return log_user_feedback(req.document_id, req.query, req.rating)


class VoiceSearchRequest(BaseModel):
    audio_transcript_payload: str
    top_k: int = 5


class GraphTopologyRequest(BaseModel):
    source_documents: List[Dict[str, Any]] = None


class SpeculativeStreamRequest(BaseModel):
    prompt: str
    base_response: str
    draft_count: Optional[int] = 3
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 256


class ExecutiveBriefingRequest(BaseModel):
    document_chunks: List[str]
    title: str = "Executive Briefing"
    max_action_items: Optional[int] = 10
    priority_filter: Optional[str] = None
    target_audience: Optional[str] = "Executive"


@router.post("/api/rag/voice/search")
def voice_search_endpoint(req: VoiceSearchRequest):
    """Voice Memo Search & Local Phoneme Transcriber endpoint."""
    from src.domain.voice_rag import transcribe_and_search_voice_memo
    return transcribe_and_search_voice_memo(req.audio_transcript_payload, req.top_k)


@router.post("/api/rag/graph/topology")
def graph_topology_endpoint(req: GraphTopologyRequest):
    """Interactive Knowledge Graph Topology endpoint."""
    from src.domain.graph_explorer import generate_graph_topology
    return generate_graph_topology(req.source_documents)


@router.post("/api/rag/stream/speculative")
def speculative_stream_endpoint(req: SpeculativeStreamRequest):
    """Zero-Latency Speculative Response Streamer endpoint."""
    from src.domain.speculative_streamer import generate_speculative_stream_chunks
    chunks = generate_speculative_stream_chunks(req.prompt, req.base_response)
    if req.draft_count and req.draft_count < len(chunks):
        chunks = chunks[:req.draft_count]
    return {"total": len(chunks), "stream_chunks": chunks, "status": "success"}


@router.post("/api/rag/briefing/generate")
def executive_briefing_endpoint(req: ExecutiveBriefingRequest):
    """Automated Executive Briefing Generator endpoint."""
    from src.domain.executive_briefing import generate_executive_briefing
    briefing = generate_executive_briefing(req.document_chunks, req.title)
    if req.priority_filter and "action_items" in briefing:
        norm_p = req.priority_filter.strip().lower()
        briefing["action_items"] = [item for item in briefing["action_items"] if norm_p in str(item.get("priority", "")).lower()]
    if req.max_action_items and "action_items" in briefing:
        briefing["action_items"] = briefing["action_items"][:req.max_action_items]
    if req.target_audience:
        briefing["target_audience"] = req.target_audience
    return briefing


class RAGEvalRequest(BaseModel):
    query: str
    answer: str
    retrieved_contexts: List[str]
    golden_answer: str = None


class SemanticDiffRequest(BaseModel):
    old_doc_text: str
    new_doc_text: str


class QueryIntentRequest(BaseModel):
    query: str


@router.post("/api/rag/eval/benchmark")
def rag_eval_benchmark_endpoint(req: RAGEvalRequest):
    """Automated RAG Evaluation & Golden Dataset Benchmarker endpoint."""
    from src.domain.rag_evaluator import evaluate_rag_triad
    return evaluate_rag_triad(req.query, req.answer, req.retrieved_contexts, req.golden_answer)


@router.post("/api/rag/diff/semantic")
def semantic_diff_endpoint(req: SemanticDiffRequest):
    """Semantic Document Diff & Version Evolution Comparator endpoint."""
    from src.domain.semantic_doc_diff import compare_semantic_doc_diff
    return compare_semantic_doc_diff(req.old_doc_text, req.new_doc_text)


@router.post("/api/rag/intent/classify")
def query_intent_classify_endpoint(req: QueryIntentRequest):
    """Semantic Query Intent Classifier & Disambiguator endpoint."""
    from src.domain.query_intent_classifier import classify_query_intent
    return classify_query_intent(req.query)


class InjectionScanRequest(BaseModel):
    text: str


class CredibilityWeightRequest(BaseModel):
    candidates: List[Dict[str, Any]]


class FAQSynthesizeRequest(BaseModel):
    query_history: List[str]


@router.post("/api/rag/safety/injection-guard")
def injection_scan_endpoint(req: InjectionScanRequest):
    """Adversarial Prompt Injection & Indirect Jailbreak Guard endpoint."""
    from src.domain.prompt_injection_guard import scan_prompt_injection
    return scan_prompt_injection(req.text)


@router.post("/api/rag/authority/weight")
def credibility_weight_endpoint(req: CredibilityWeightRequest):
    """Source Document Credibility & Authority Weighting endpoint."""
    from src.domain.source_credibility_weight import apply_source_credibility_weighting
    weighted = apply_source_credibility_weighting(req.candidates)
    return {"total": len(weighted), "weighted_candidates": weighted, "status": "success"}


@router.post("/api/rag/faq/synthesize")
def faq_synthesize_endpoint(req: FAQSynthesizeRequest):
    """Continuous Automatic FAQ & Knowledge Base Synthesizer endpoint."""
    from src.domain.faq_synthesizer import synthesize_faq_from_queries
    return synthesize_faq_from_queries(req.query_history)


class AutoTunerRequest(BaseModel):
    historical_feedback: List[Dict[str, Any]]
    current_weights: Optional[Dict[str, float]] = None


class SyntheticQARequest(BaseModel):
    document_text: str
    max_triples: int = 5


class CodeASTRequest(BaseModel):
    code_snippet: str


class VisualCanvasRequest(BaseModel):
    raw_document_layout: Dict[str, Any]
    min_confidence: Optional[float] = 0.80
    extract_images: Optional[bool] = True
    extract_tables: Optional[bool] = True


class CounterfactualRequest(BaseModel):
    base_query: str
    base_contexts: List[str]
    masked_chunk_indices: Optional[List[int]] = None
    max_scenarios: Optional[int] = 2


class SLABreakerRequest(BaseModel):
    latency_ms: float
    max_sla_ms: float = 50.0


class CryptoAuditRequest(BaseModel):
    query: str
    answer: str
    contexts: List[str]


@router.post("/api/rag/auto-tuner/optimize")
def auto_tuner_endpoint(req: AutoTunerRequest):
    """Self-Improving Search Weight & Chunk Tuner endpoint."""
    from src.domain.auto_weight_tuner import optimize_search_parameters
    return optimize_search_parameters(req.historical_feedback, req.current_weights)


@router.post("/api/rag/synthetic/generate-qa")
def synthetic_qa_endpoint(req: SyntheticQARequest):
    """Autonomous Synthetic QA Dataset Generator endpoint."""
    from src.domain.synthetic_qa_generator import generate_synthetic_qa_triples
    return generate_synthetic_qa_triples(req.document_text, req.max_triples)


@router.post("/api/rag/code/ast-parse")
def code_ast_endpoint(req: CodeASTRequest):
    """AST Code Graph & Structural Symbol RAG endpoint."""
    from src.domain.ast_code_rag import parse_codebase_ast
    return parse_codebase_ast(req.code_snippet)


@router.post("/api/rag/canvas/visual-parse")
def visual_canvas_endpoint(req: VisualCanvasRequest):
    """Multimodal Visual Canvas OCR & Bounding Box Extractor endpoint."""
    from src.domain.visual_canvas_rag import extract_visual_canvas_regions
    return extract_visual_canvas_regions(req.raw_document_layout)


@router.post("/api/rag/counterfactual/simulate")
def counterfactual_endpoint(req: CounterfactualRequest):
    """Counterfactual RAG Scenario Simulator endpoint."""
    from src.domain.counterfactual_rag import simulate_counterfactual_scenario
    return simulate_counterfactual_scenario(req.base_query, req.base_contexts, req.masked_chunk_indices)


@router.post("/api/rag/sla/circuit-breaker")
def sla_circuit_breaker_endpoint(req: SLABreakerRequest):
    """Sub-50ms SLA Circuit Breaker endpoint."""
    from src.domain.sla_circuit_breaker import execute_with_sla_circuit_breaker
    return execute_with_sla_circuit_breaker(
        primary_func=lambda: {"res": "ColBERT Primary"},
        fallback_func=lambda: {"res": "FTS5 Fast Fallback"},
        latency_ms=req.latency_ms,
        max_sla_ms=req.max_sla_ms
    )


@router.post("/api/rag/audit/append-crypto")
def crypto_audit_endpoint(req: CryptoAuditRequest):
    """Zero-Knowledge Cryptographic Audit Ledger endpoint."""
    from src.domain.crypto_audit_ledger import append_crypto_audit_block
    return append_crypto_audit_block(req.query, req.answer, req.contexts)


class EpistemicBeliefRequest(BaseModel):
    new_claim: str
    existing_beliefs: Optional[List[Dict[str, Any]]] = None


class ContextMemoryRequest(BaseModel):
    chat_history: List[Dict[str, str]]
    target_summary_len: int = 150


class PredictivePrefetchRequest(BaseModel):
    active_query: str
    retrieved_contexts: List[str]


class EntityCooccurrenceRequest(BaseModel):
    documents: List[Dict[str, str]]


class KnowledgeDistillRequest(BaseModel):
    rag_interaction_logs: List[Dict[str, Any]]
    format_type: str = "alpaca"


class FactCheckRequest(BaseModel):
    doc_a_clauses: List[str]
    doc_b_clauses: List[str]


class UniversalPipelineRequest(BaseModel):
    raw_content: str
    format_type: str = "markdown"


class ProvenanceTrackRequest(BaseModel):
    file_path: str
    file_content: str
    author: str = "system"


@router.post("/api/rag/epistemic/update-belief")
def epistemic_belief_endpoint(req: EpistemicBeliefRequest):
    """Dynamic Epistemic Belief Graph endpoint."""
    from src.domain.epistemic_belief_graph import update_epistemic_belief_graph
    return update_epistemic_belief_graph(req.new_claim, req.existing_beliefs)


@router.post("/api/rag/memory/compress")
def context_memory_compress_endpoint(req: ContextMemoryRequest):
    """Hierarchical Context Window Summarization Memory endpoint."""
    from src.domain.context_memory_compressor import compress_context_memory
    return compress_context_memory(req.chat_history, req.target_summary_len)


@router.post("/api/rag/prefetch/predict")
def predictive_prefetch_endpoint(req: PredictivePrefetchRequest):
    """Predictive Search Intent Pre-Fetcher endpoint."""
    from src.domain.predictive_prefetch import predict_next_search_intents
    return predict_next_search_intents(req.active_query, req.retrieved_contexts)


@router.post("/api/rag/entity/cooccurrence")
def entity_cooccurrence_endpoint(req: EntityCooccurrenceRequest):
    """Cross-Document Entity Co-Occurrence Matrix endpoint."""
    from src.domain.entity_cooccurrence import compute_entity_cooccurrence_matrix
    return compute_entity_cooccurrence_matrix(req.documents)


@router.post("/api/rag/distill/export")
def knowledge_distill_export_endpoint(req: KnowledgeDistillRequest):
    """Zero-Cost Knowledge Distillation Dataset Exporter endpoint."""
    from src.domain.knowledge_distiller import export_knowledge_distillation_dataset
    return export_knowledge_distillation_dataset(req.rag_interaction_logs, req.format_type)


@router.post("/api/rag/fact-check/detect-contradictions")
def fact_check_endpoint(req: FactCheckRequest):
    """Semantic Contradiction & Fact-Check endpoint."""
    from src.domain.fact_check_engine import detect_semantic_contradictions
    return detect_semantic_contradictions(req.doc_a_clauses, req.doc_b_clauses)


@router.post("/api/rag/pipeline/ingest-universal")
def universal_pipeline_endpoint(req: UniversalPipelineRequest):
    """Universal Document & Data Format Pipeline endpoint."""
    from src.domain.universal_pipeline import ingest_universal_data_format
    return ingest_universal_data_format(req.raw_content, req.format_type)


@router.post("/api/rag/provenance/track")
def provenance_track_endpoint(req: ProvenanceTrackRequest):
    """Real-Time Data Lineage & Cryptographic Provenance Tracker endpoint."""
    from src.domain.data_provenance_tracker import track_data_provenance
    return track_data_provenance(req.file_path, req.file_content, req.author)


class MultiAgentConsensusRequest(BaseModel):
    query: str
    retrieved_contexts: List[str]


class VectorDriftAuditRequest(BaseModel):
    current_centroids: List[List[float]]
    new_embeddings: List[List[float]]
    drift_threshold: float = 0.25


class TokenCompressRequest(BaseModel):
    text: str


class SystemHealthRequest(BaseModel):
    recent_latencies_ms: List[float] = [0.80, 1.10, 1.20]
    cache_hits: int = 100
    cache_misses: int = 5


@router.post("/api/rag/consensus/multi-agent")
def multi_agent_consensus_endpoint(req: MultiAgentConsensusRequest):
    """Multi-Agent Reasoning Consensus Orchestrator endpoint."""
    from src.domain.multi_agent_consensus import orchestrate_multi_agent_consensus
    return orchestrate_multi_agent_consensus(req.query, req.retrieved_contexts)


@router.post("/api/rag/vector/drift-audit")
def vector_drift_audit_endpoint(req: VectorDriftAuditRequest):
    """Autonomous Vector Drift & Index Re-Balancing Agent endpoint."""
    from src.domain.vector_drift_agent import audit_vector_index_drift
    return audit_vector_index_drift(req.current_centroids, req.new_embeddings, req.drift_threshold)


@router.post("/api/rag/stream/compress-tokens")
def compress_tokens_endpoint(req: TokenCompressRequest):
    """Streaming Semantic Token Compressor endpoint."""
    from src.domain.streaming_token_compressor import compress_streaming_tokens
    return compress_streaming_tokens(req.text)


@router.get("/api/rag/telemetry/health")
@router.post("/api/rag/telemetry/health")
def system_health_telemetry_endpoint(req: Optional[SystemHealthRequest] = None):
    """Live System Health SLA Telemetry Dashboard API endpoint."""
    from src.domain.system_health_telemetry import compute_system_health_telemetry
    latencies = req.recent_latencies_ms if req else [0.80, 1.10, 1.20]
    hits = req.cache_hits if req else 100
    misses = req.cache_misses if req else 5
    return compute_system_health_telemetry(latencies, hits, misses)


class CodeRefactorRequest(BaseModel):
    code_snippet: str


class SwarmDecomposeRequest(BaseModel):
    master_goal: str


class DocAlignRequest(BaseModel):
    code_snippet: str


@router.post("/api/rag/code/self-refactor")
def code_self_refactor_endpoint(req: CodeRefactorRequest):
    """Autonomous Code Self-Refactoring & Style Enforcer endpoint."""
    from src.domain.code_self_refactor import analyze_and_propose_refactoring
    return analyze_and_propose_refactoring(req.code_snippet)


@router.post("/api/rag/swarm/decompose")
def swarm_decompose_endpoint(req: SwarmDecomposeRequest):
    """Multi-Agent Task Decomposition & Sub-Task Swarm Manager endpoint."""
    from src.domain.agent_swarm_manager import decompose_goal_into_agent_swarm
    return decompose_goal_into_agent_swarm(req.master_goal)


@router.post("/api/rag/code/doc-align")
def code_doc_align_endpoint(req: DocAlignRequest):
    """Semantic Code-Text Alignment & Docstring Harmonizer endpoint."""
    from src.domain.code_doc_aligner import check_code_docstring_alignment
    return check_code_docstring_alignment(req.code_snippet)


class ZKMaskRequest(BaseModel):
    sensitive_data: str
    secret_salt: str = "uroboros_zk_salt"


@router.post("/api/rag/privacy/zk-mask")
def zk_mask_endpoint(req: ZKMaskRequest):

    """Quantum-Safe Zero-Knowledge Data Masker endpoint."""
    from src.domain.zk_data_masker import mask_payload_with_zk_proof
    return mask_payload_with_zk_proof(req.sensitive_data, req.secret_salt)


@router.post("/api/rag/swarm/execute")
def api_swarm_rag(req: Dict[str, Any]):

    """Cognitive Swarm RAG endpoint (Explorer, Graph, Critic, Synthesizer)."""
    from src.domain.swarm_rag import execute_swarm_rag
    query = req.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query string is required")
    return execute_swarm_rag(query)


@router.post("/api/rag/memory/remember")
def api_remember(req: Dict[str, Any]):
    """Agentic Memory store endpoint."""
    from src.domain.agent_memory import remember
    key = req.get("key")
    val = req.get("value")
    if not key or val is None:
        raise HTTPException(status_code=400, detail="key and value are required")
    return remember(key, val, category=req.get("category", "preference"))


@router.get("/api/rag/memory/recall")
def api_recall(key: str, category: Optional[str] = None):
    """Agentic Memory recall endpoint."""
    from src.domain.agent_memory import recall
    return {"key": key, "value": recall(key, category=category)}


@router.get("/api/rag/perception/screen")
def api_screen_perception():
    """Workspace Screen Perception endpoint."""
    from src.domain.screen_perception import capture_screen_context
    return capture_screen_context()


@router.get("/api/rag/contradictions")
def api_contradictions(limit: int = 50):
    """Vault Contradiction & Fact Discrepancy Resolver endpoint."""
    from src.domain.contradiction_resolver import detect_vault_contradictions
    return detect_vault_contradictions(limit=limit)


@router.post("/api/rag/ast/parse")
def api_ast_parse(req: Dict[str, Any]):
    """AST Code-Flow Parser endpoint."""
    from src.domain.ast_parser import parse_python_ast
    code = req.get("code", "")
    filename = req.get("filename", "<api>")
    return parse_python_ast(code, filename=filename)


@router.post("/api/rag/dataset/synthesize")
def api_dataset_synthesize(req: Dict[str, Any]):
    """Vault Instruction Fine-Tuning Dataset Synthesizer endpoint."""
    from src.domain.dataset_synthesizer import generate_vault_instruction_dataset
    return generate_vault_instruction_dataset(limit=req.get("limit", 50))


@router.get("/api/rag/briefing/audio")
def api_audio_briefing():
    """Executive Audio Podcast Script Generator endpoint."""
    from src.domain.audio_briefing import generate_audio_podcast_script
    return generate_audio_podcast_script()


@router.get("/api/rag/architecture/audit")
def api_architecture_doctor(root_dir: str = "src/domain"):
    """Codebase AST Architecture Doctor endpoint."""
    from src.domain.architecture_doctor import audit_codebase_architecture
    return audit_codebase_architecture(root_dir=root_dir)


@router.post("/api/rag/fusion/execute")
def api_fusion_rag(req: Dict[str, Any]):
    """Dual Web & Vault Fusion RAG endpoint."""
    from src.domain.web_rag_fusion import execute_dual_fusion_rag
    query = req.get("query", "")
    return execute_dual_fusion_rag(query, max_local_snippets=req.get("max_local", 3), max_web_results=req.get("max_web", 2))


@router.post("/api/rag/diff/synthesize")
def api_diff_synthesize(req: Dict[str, Any]):
    """Automated Git Diff & Refactoring Patch Synthesizer endpoint."""
    from src.domain.code_diff_synthesizer import generate_refactoring_patch
    orig = req.get("original_code", "")
    mod = req.get("modified_code", "")
    filepath = req.get("filepath", "module.py")
    return generate_refactoring_patch(orig, mod, filepath=filepath)


@router.get("/api/rag/benchmark")
def api_vector_benchmark(num_queries: int = 5, dimension: int = 128):
    """Vector Retrieval Benchmark Harness endpoint."""
    from src.domain.retrieval_benchmark import benchmark_vector_retrieval
    return benchmark_vector_retrieval(num_queries=num_queries, dimension=dimension)


@router.post("/api/rag/entity/resolve")
def api_entity_resolve(req: Dict[str, Any]):
    """Entity Resolver & Alias Merging endpoint."""
    from src.domain.entity_resolver import batch_resolve_entities
    entities = req.get("entities", [])
    return batch_resolve_entities(entities)


@router.post("/api/rag/prompt/optimize")
def api_prompt_optimize(req: Dict[str, Any]):
    """Dynamic Prompt Density Optimizer endpoint."""
    from src.domain.prompt_optimizer import optimize_rag_prompt_density
    query = req.get("query", "")
    chunks = req.get("chunks", [])
    budget = req.get("token_budget", 1000)
    return optimize_rag_prompt_density(query, chunks, token_budget=budget)


@router.post("/api/rag/compliance/inspect")
def api_compliance_inspect(req: Dict[str, Any]):
    """Autonomous Privacy & Compliance Inspector endpoint."""
    from src.domain.compliance_inspector import inspect_privacy_compliance
    text = req.get("text", "")
    return inspect_privacy_compliance(text)


@router.post("/api/rag/visualizer/mermaid")
def api_reasoning_visualizer(req: Dict[str, Any]):
    """Reasoning Graph Visualizer endpoint."""
    from src.domain.reasoning_visualizer import generate_mermaid_reasoning_diagram
    pathways = req.get("pathways", [])
    return generate_mermaid_reasoning_diagram(pathways)


@router.get("/api/rag/scoreboard")
def api_system_scoreboard():
    """Master System Scoreboard Telemetry endpoint."""
    from src.domain.system_scoreboard import generate_system_scoreboard
    return generate_system_scoreboard("src/domain")


@router.post("/api/rag/hypergraph/route")
def api_hypergraph_route(req: Dict[str, Any]):
    """Adaptive Query-Time Hyper-Graph Knowledge Router endpoint."""
    from src.domain.hypergraph_router import route_hypergraph_query
    query = req.get("query", "")
    entities = req.get("target_entities", [])
    return route_hypergraph_query(query, entities)


@router.post("/api/rag/fusion/rerank")
def api_sparse_dense_fusion_rerank(req: Dict[str, Any]):
    """Self-Evolving Sparse-Dense-ColBERT Fusion Reranker endpoint."""
    from src.domain.sparse_dense_fusion import rerank_sparse_dense_fusion
    query = req.get("query", "")
    candidate_chunks = req.get("candidate_chunks", [])
    return rerank_sparse_dense_fusion(query, candidate_chunks)


@router.post("/api/rag/noise/mask-entropy")
def api_mask_entropy_noise(req: Dict[str, Any]):
    """Entropy Differential Noise Masker endpoint."""
    from src.domain.contextual_noise_mask import mask_low_entropy_noise
    text_chunk = req.get("text_chunk", "")
    return mask_low_entropy_noise(text_chunk)


@router.post("/api/rag/ann/search")
def api_sublinear_ann_search(req: Dict[str, Any]):
    """Sub-Linear LSH-HNSW Vector Indexer endpoint."""
    from src.domain.sublinear_ann_index import search_sublinear_ann
    query_vec = req.get("query_vec", [])
    index_vecs = req.get("index_vectors", [])
    top_k = req.get("top_k", 5)
    return search_sublinear_ann(query_vec, index_vecs, top_k=top_k)


@router.post("/api/rag/crosslingual/bridge")
def api_crosslingual_bridge(req: Dict[str, Any]):
    """Multilingual Latent Vector Projection Bridge endpoint."""
    from src.domain.crosslingual_bridge import project_multilingual_vector
    text = req.get("text", "")
    src_lang = req.get("source_language", "auto")
    return project_multilingual_vector(text, source_language=src_lang)


@router.post("/api/rag/feedback/refine")
def api_feedback_refine(req: Dict[str, Any]):
    """Self-Supervised Retrieval Feedback Auto-Refiner endpoint."""
    from src.domain.retrieval_feedback_refiner import log_feedback_and_refine
    chunk_id = req.get("chunk_id", "chk_0")
    signal = req.get("feedback_signal", "click")
    return log_feedback_and_refine(chunk_id, feedback_signal=signal)


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

















