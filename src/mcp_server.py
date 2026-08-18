import os
import sys
import json
import asyncio
from pathlib import Path
import httpx

# Add project root and neuro-copilot scripts directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / ".agents" / "skills" / "neuro-copilot" / "scripts"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from mcp.server.models import InitializationOptions
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    import mcp.server.stdio
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    
    class _MockTypes:
        class Tool:
            def __init__(self, name: str, description: str = "", inputSchema: dict | None = None):
                self.name = name
                self.description = description
                self.inputSchema = inputSchema or {}
        
        class TextContent:
            def __init__(self, type: str = "text", text: str = ""):
                self.type = type
                self.text = text
                
        class PromptArgument:
            def __init__(self, name: str, description: str = "", required: bool = False):
                self.name = name
                self.description = description
                self.required = required
                
        class Prompt:
            def __init__(self, name: str, description: str = "", arguments: list | None = None):
                self.name = name
                self.description = description
                self.arguments = arguments or []
                
        class PromptMessage:
            def __init__(self, role: str = "user", content: any = None):
                self.role = role
                self.content = content
                
        class GetPromptResult:
            def __init__(self, description: str = "", messages: list | None = None):
                self.description = description
                self.messages = messages or []
                
        class Resource:
            def __init__(self, uri: str, name: str = "", description: str = "", mimeType: str = ""):
                self.uri = uri
                self.name = name
                self.description = description
                self.mimeType = mimeType
                
        class ImageContent:
            def __init__(self, type: str = "image", data: str = "", mimeType: str = ""):
                self.type = type
                self.data = data
                self.mimeType = mimeType
                
        class EmbeddedResource:
            def __init__(self, type: str = "resource", resource: any = None):
                self.type = type
                self.resource = resource

    types = _MockTypes()

    class _MockServer:
        def __init__(self, name: str):
            self.name = name
        def list_tools(self):
            def decorator(f): return f
            return decorator
        def call_tool(self):
            def decorator(f): return f
            return decorator
        def list_resources(self):
            def decorator(f): return f
            return decorator
        def read_resource(self):
            def decorator(f): return f
            return decorator
        def list_prompts(self):
            def decorator(f): return f
            return decorator
        def get_prompt(self):
            def decorator(f): return f
            return decorator

    server = _MockServer("neuro-mcp")

if HAS_MCP:
    server = Server("neuro-mcp")

NEURO_API_URL = os.environ.get("NEURO_API_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("NEURO_API_KEY", "")

async def make_request(method: str, endpoint: str, **kwargs):
    url = f"{NEURO_API_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "The search query string"},
        "limit": {"type": "integer", "description": "Max results to return", "default": 5},
        "search_type": {"type": "string", "enum": ["hybrid", "vector", "fts"], "default": "hybrid"},
    },
    "required": ["query"],
}

INGEST_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "URL or local file path to index into vault"},
    },
    "required": ["url"],
}

TRIGGER_SCHEMA = {
    "type": "object",
    "properties": {
        "event_type": {"type": "string", "description": "Event type identifier"},
        "payload": {"type": "object", "description": "Optional payload data"},
    },
    "required": ["event_type"],
}

STATS_SCHEMA = {
    "type": "object",
    "properties": {},
}

HYDE_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query for hypothetical document expansion"},
    },
    "required": ["query"],
}

GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "entity": {"type": "string", "description": "Entity or concept name to traverse in Knowledge Graph"},
    },
    "required": ["entity"],
}

COMPRESS_AST_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File path to semantically compress for token budgeting"},
    },
    "required": ["path"],
}

SELF_PATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string", "description": "Stack trace or runtime error string to synthesize a fix for"},
        "file": {"type": "string", "description": "Optional target file path"},
    },
    "required": ["error"],
}

CALL_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "target": {"type": "string", "description": "Target Python module to build call graph for", "default": "know.py"},
    },
}

RELEASE_CERT_SCHEMA = {
    "type": "object",
    "properties": {},
}

SPEAK_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text message for neural voice synthesis"},
        "domain": {"type": "string", "description": "Domain profile (DEV_OPS, DAILY_BRIEF, EXECUTIVE_ASSISTANT, TACTICAL_COCKPIT, GENERAL)", "default": "GENERAL"},
        "priority": {"type": "string", "description": "Alert priority (CRITICAL, URGENT, NORMAL, INFO)", "default": "NORMAL"},
        "voice": {"type": "string", "description": "Kokoro voice persona (bf_emma, af_sarah, am_adam, af_bella, bm_george)"}
    },
    "required": ["text"],
}

SFX_SCHEMA = {
    "type": "object",
    "properties": {
        "sfx_name": {"type": "string", "description": "Procedural UI sound effect (ready, confirm, complete, alert, dismiss, success, ping, warning)", "default": "complete"}
    },
    "required": ["sfx_name"],
}

ACT_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {"type": "string", "description": "High-level engineering task or question for autonomous ReAct agent to solve"},
        "steps": {"type": "integer", "description": "Maximum reasoning steps (default: 6)", "default": 6},
    },
    "required": ["task"],
}

SYMBOL_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string", "description": "Function, class, or method name to query in SQLite AST graph"},
    },
    "required": ["symbol"],
}

DOCTOR_SCHEMA = {
    "type": "object",
    "properties": {},
}

REAP_ZOMBIES_SCHEMA = {
    "type": "object",
    "properties": {},
}

CONSENSUS_DEBATE_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string", "description": "Architecture question or goal for Proposer / Red-Team / Arbiter multi-agent debate"}
    },
    "required": ["prompt"]
}

GRAPH_OF_THOUGHTS_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string", "description": "Goal or complex problem to decompose into a topological DAG of thoughts"}
    },
    "required": ["goal"]
}

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="neuro_search",
            description="Perform hybrid semantic search (ColBERT + FTS5) against Uroboros Knowledge Vault.",
            inputSchema=SEARCH_SCHEMA,
        ),
        types.Tool(
            name="neuro_act",
            description="Execute autonomous multi-step ReAct agent loop (Thought -> Action -> Observation -> Self-Correction) using local SLMs.",
            inputSchema=ACT_SCHEMA,
        ),
        types.Tool(
            name="neuro_symbol_graph",
            description="Look up symbol definition, line ranges, upstream callers, downstream callees, and database table references in SQLite AST graph.",
            inputSchema=SYMBOL_GRAPH_SCHEMA,
        ),
        types.Tool(
            name="neuro_doctor",
            description="Run unified 360° health diagnostic scorecard across OS RAM, process hygiene, SQLite invariants, Git Merkle, and Tududi burndown.",
            inputSchema=DOCTOR_SCHEMA,
        ),
        types.Tool(
            name="neuro_reap_zombies",
            description="Surgically terminate orphaned background Python test workers, hung processes, and duplicate servers, executing 6-phase OS optimization cascade.",
            inputSchema=REAP_ZOMBIES_SCHEMA,
        ),
        types.Tool(
            name="neuro_ingest",
            description="Ingest a URL or document into the Knowledge Engine vault.",
            inputSchema=INGEST_SCHEMA,
        ),
        types.Tool(
            name="neuro_trigger_workflow",
            description="Trigger an automated workflow rule in the Knowledge Engine.",
            inputSchema=TRIGGER_SCHEMA,
        ),
        types.Tool(
            name="neuro_stats",
            description="Retrieve knowledge vault statistics, database size, and indexed document count.",
            inputSchema=STATS_SCHEMA,
        ),
        types.Tool(
            name="neuro_hyde_query",
            description="Generate Hypothetical Document Embedding (HyDE) expansions for enhanced search retrieval.",
            inputSchema=HYDE_SCHEMA,
        ),
        types.Tool(
            name="neuro_graph_query",
            description="Traverse Wikilink Knowledge Graph entity relationships and connections.",
            inputSchema=GRAPH_SCHEMA,
        ),
        types.Tool(
            name="neuro_compress_ast",
            description="Semantically compress Python AST code to save up to 45% LLM prompt tokens.",
            inputSchema=COMPRESS_AST_SCHEMA,
        ),
        types.Tool(
            name="neuro_self_patch",
            description="Autonomous neural code self-patching engine synthesizing stdlib fixes from stack traces.",
            inputSchema=SELF_PATCH_SCHEMA,
        ),
        types.Tool(
            name="neuro_call_graph",
            description="Generate Unicode interactive function call graphs and import hierarchy trees.",
            inputSchema=CALL_GRAPH_SCHEMA,
        ),
        types.Tool(
            name="neuro_release_certificate",
            description="Generate immutable cryptographic SOC 2 Type II Merkle Release Certificate.",
            inputSchema=RELEASE_CERT_SCHEMA,
        ),
        types.Tool(
            name="neuro_speak",
            description="Speak message through Universal Kokoro-82M Neural Voice Bridge across multi-domain profiles.",
            inputSchema=SPEAK_SCHEMA,
        ),
        types.Tool(
            name="neuro_play_sfx",
            description="Play procedural UI earcon sound effect (chime, alert, confirmation, completion).",
            inputSchema=SFX_SCHEMA,
        ),
        types.Tool(
            name="neuro_consensus_debate",
            description="Execute multi-agent Proposer / Red-Team Critic / Arbiter consensus debate with quantitative verification scoring.",
            inputSchema=CONSENSUS_DEBATE_SCHEMA,
        ),
        types.Tool(
            name="neuro_graph_of_thoughts",
            description="Decompose complex engineering problems into a topological Directed Acyclic Graph (DAG) of thoughts using stdlib graphlib.",
            inputSchema=GRAPH_OF_THOUGHTS_SCHEMA,
        ),
    ]

async def _mcp_tool_search(args: dict) -> list[types.TextContent]:
    query = (args or {}).get("query", "")
    limit = (args or {}).get("limit", 6)
    search_type = (args or {}).get("search_type", "hybrid")

    # 1. Primary: Check if make_request API client is available or mocked
    try:
        res = await make_request("POST", "/api/search", json={"query": query, "limit": limit, "search_type": search_type})
        if isinstance(res, dict) and "results" in res:
            results = res.get("results", [])
            text_out = f"Search Results for '{query}':\n"
            for r in results:
                text_out += f"- [{r.get('score', 0.0)}] {r.get('filename')}: {r.get('content', '')}\n"
            return [types.TextContent(type="text", text=text_out)]
    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)) or "unreachable" in str(e).lower() or hasattr(e, "response"):
            return [types.TextContent(type="text", text=f"Error: {e}")]

    # 2. In-process Advanced RAG synthesis engine
    try:
        from src.domain.rag_engine import extract_advanced_rag_context
        context, citations = extract_advanced_rag_context(query, max_chunks=limit)
        if context or citations:
            text_out = f"## 📚 Empirical Knowledge Vault Hits for: '{query}'\n\n"
            if citations:
                text_out += "### 🏷️ Sources & Citations:\n"
                for c in citations:
                    fn = c.get("filename", "")
                    fp = c.get("filepath", "")
                    score = c.get("confidence_score", 0.0)
                    cite_label = c.get("citation", fn)
                    text_out += f"- **{cite_label}**\n  File: `{fp}` (Relevance: {score:.3f})\n"
                text_out += "\n"
            text_out += f"### 📄 Unredacted Vault Content:\n\n{context}\n"
            return [types.TextContent(type="text", text=text_out)]
    except Exception:
        pass

    # 3. Direct SQLite FTS5 file search
    try:
        from src.infrastructure.database import get_db
        from src.core.domain.services import sanitise_fts_query
        with get_db() as conn:
            cursor = conn.cursor()
            clean_q = sanitise_fts_query(query)
            try:
                cursor.execute(
                    "SELECT f.filepath, f.filename, f.content FROM fts_files fts JOIN files f ON fts.filepath = f.filepath WHERE fts_files MATCH ? LIMIT ?",
                    (clean_q, limit)
                )
                rows = cursor.fetchall()
            except Exception:
                rows = []

            if not rows:
                like_q = f"%{query}%"
                cursor.execute(
                    "SELECT filepath, filename, content FROM files WHERE filename LIKE ? OR content LIKE ? LIMIT ?",
                    (like_q, like_q, limit)
                )
                rows = cursor.fetchall()

            if rows:
                text_out = f"## 📚 Knowledge Vault FTS Hits for: '{query}'\n\n"
                for r in rows:
                    fname = r[1] if isinstance(r, (tuple, list)) else r.get("filename", "")
                    fpath = r[0] if isinstance(r, (tuple, list)) else r.get("filepath", "")
                    content = r[2] if isinstance(r, (tuple, list)) else r.get("content", "")
                    text_out += f"### File: `{fname}`\nPath: `{fpath}`\n```\n{content[:1500]}\n```\n\n"
                return [types.TextContent(type="text", text=text_out)]
    except Exception:
        pass

    return [types.TextContent(type="text", text=f"Search Results for '{query}':\nNo matching empirical documents found in knowledge vault.")]


async def _mcp_tool_ingest(args: dict) -> list[types.TextContent]:
    url = args.get("url", "")
    if url.startswith("http"):
        res = await make_request("POST", "/api/file/ingest-url", json={"url": url})
        return [types.TextContent(type="text", text=f"Successfully ingested: {url}\nResponse: {res}")]
    res = await make_request("POST", "/api/file/index", json={"directory": url})
    return [types.TextContent(type="text", text=f"Local file ingestion / Indexed directory {url}:\nResponse: {res}")]


async def _mcp_tool_trigger_workflow(args: dict) -> list[types.TextContent]:
    res = await make_request("POST", "/api/workflows/trigger", json={
        "event_type": args.get("event_type"),
        "payload": args.get("payload", {})
    })
    return [types.TextContent(type="text", text=f"Triggered {args.get('event_type')} workflow.\nResponse: {res}")]


async def _mcp_tool_stats(args: dict) -> list[types.TextContent]:
    from know import db_status
    stats = db_status()
    return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]


async def _mcp_tool_hyde_query(args: dict) -> list[types.TextContent]:
    from src.domain.services import generate_hyde
    hyde = generate_hyde(args.get("query"))
    return [types.TextContent(type="text", text=json.dumps({"query": args.get("query"), "hyde_expansion": hyde}, indent=2))]


async def _mcp_tool_graph_query(args: dict) -> list[types.TextContent]:
    from know import get_graph_data
    graph = get_graph_data()
    return [types.TextContent(type="text", text=json.dumps(graph, indent=2))]


async def _mcp_tool_compress_ast(args: dict) -> list[types.TextContent]:
    import neuro_bridge
    res = neuro_bridge.compress_ast(args.get("path"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_self_patch(args: dict) -> list[types.TextContent]:
    import github_bridge
    res = github_bridge.self_patch(args.get("error"), args.get("file"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_call_graph(args: dict) -> list[types.TextContent]:
    import github_bridge
    res = github_bridge.call_graph(args.get("target", "know.py"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_release_certificate(args: dict) -> list[types.TextContent]:
    import github_bridge
    res = github_bridge.generate_certificate()
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_speak(args: dict) -> list[types.TextContent]:
    from src.core.voice_bridge import VoiceBridge
    raw_text = args.get("text", "")
    try:
        from src.core.voice_normalizer import VoiceNormalizer
        clean_text = VoiceNormalizer.normalize_for_speech(raw_text)
    except Exception:
        clean_text = raw_text
    res = VoiceBridge.speak(
        text=clean_text,
        domain=args.get("domain", "GENERAL"),
        priority=args.get("priority", "NORMAL"),
        voice=args.get("voice")
    )
    return [types.TextContent(type="text", text=f"Spoken via VoiceBridge ({res.get('engine')}): '{clean_text}' [Dispatched: {res.get('dispatched')}]")]


async def _mcp_tool_play_sfx(args: dict) -> list[types.TextContent]:
    from src.core.voice_bridge import VoiceBridge
    sfx = args.get("sfx_name", "target_lock")
    wav_bytes = VoiceBridge.play_sfx(sfx)
    if wav_bytes:
        return [types.TextContent(type="text", text=f"Procedural SFX '{sfx}' synthesized successfully ({len(wav_bytes):,} bytes).")]
    return [types.TextContent(type="text", text=f"SFX '{sfx}' failed to generate.")]


async def _mcp_tool_act(args: dict) -> list[types.TextContent]:
    import react_agent_bridge
    res = react_agent_bridge.run_react_agent_loop(args.get("task", ""), max_steps=args.get("steps", 6))
    return [types.TextContent(type="text", text=json.dumps(res, indent=2))]


async def _mcp_tool_symbol_graph(args: dict) -> list[types.TextContent]:
    import ast_graph_bridge
    res = ast_graph_bridge.query_symbol_graph(args.get("symbol", ""))
    return [types.TextContent(type="text", text=json.dumps(res, indent=2))]


async def _mcp_tool_doctor(args: dict) -> list[types.TextContent]:
    import doctor_bridge
    res = doctor_bridge.generate_health_scorecard()
    return [types.TextContent(type="text", text=json.dumps(res, indent=2))]


async def _mcp_tool_reap_zombies(args: dict) -> list[types.TextContent]:
    import process_hygiene_bridge
    res = process_hygiene_bridge.clean_process_hygiene()
    return [types.TextContent(type="text", text=json.dumps(res, indent=2))]


async def _mcp_tool_consensus_debate(args: dict) -> list[types.TextContent]:
    prompt = (args or {}).get("prompt", "")
    try:
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "neuro-copilot", "scripts"))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from frontier_reasoning_bridge import ConsensusArbiter
        res = ConsensusArbiter.run_debate(prompt)
        out = (
            f"## 🏛️ Multi-Agent Consensus Debate Verdict\n\n"
            f"**Consensus Confidence Score**: `{res.consensus_score:.2f}`\n"
            f"**Passed**: `{'✅ True' if res.passed else '❌ False'}`\n\n"
            f"### 🛡️ Hardened Solution:\n{res.arbiter_verdict}\n\n"
            f"### ⚔️ Red-Team Critic Audit:\n{res.critic_critique}\n"
        )
        return [types.TextContent(type="text", text=out)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error in consensus debate: {e}")]


async def _mcp_tool_graph_of_thoughts(args: dict) -> list[types.TextContent]:
    goal = (args or {}).get("goal", "")
    try:
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "neuro-copilot", "scripts"))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from frontier_reasoning_bridge import GraphOfThoughtsEngine
        got = GraphOfThoughtsEngine(goal)
        got.build_standard_decomposition()
        nodes = got.execute_dag()
        out = f"## 🕸️ Graph-of-Thoughts DAG Execution ({len(nodes)} Nodes)\n\n"
        for nid, n in nodes.items():
            out += f"### Node `{nid}` ({n.thought_type})\n**Task**: {n.prompt}\n```\n{n.result}\n```\n\n"
        out += f"### 🎯 Final Synthesized Solution:\n{got.get_final_result()}\n"
        return [types.TextContent(type="text", text=out)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error in Graph of Thoughts: {e}")]


_MCP_TOOL_HANDLERS = {
    "neuro_search": _mcp_tool_search,
    "neuro_act": _mcp_tool_act,
    "neuro_symbol_graph": _mcp_tool_symbol_graph,
    "neuro_doctor": _mcp_tool_doctor,
    "neuro_reap_zombies": _mcp_tool_reap_zombies,
    "neuro_ingest": _mcp_tool_ingest,
    "neuro_trigger_workflow": _mcp_tool_trigger_workflow,
    "neuro_stats": _mcp_tool_stats,
    "neuro_hyde_query": _mcp_tool_hyde_query,
    "neuro_graph_query": _mcp_tool_graph_query,
    "neuro_compress_ast": _mcp_tool_compress_ast,
    "neuro_self_patch": _mcp_tool_self_patch,
    "neuro_call_graph": _mcp_tool_call_graph,
    "neuro_release_certificate": _mcp_tool_release_certificate,
    "neuro_speak": _mcp_tool_speak,
    "neuro_play_sfx": _mcp_tool_play_sfx,
    "neuro_consensus_debate": _mcp_tool_consensus_debate,
    "neuro_graph_of_thoughts": _mcp_tool_graph_of_thoughts,
}


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    try:
        handler = _MCP_TOOL_HANDLERS.get(name)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")
        return await handler(args)
    except httpx.HTTPStatusError as e:
        return [types.TextContent(type="text", text=f"HTTP Error: {e.response.text}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="neuro://vault/stats",
            name="Knowledge Vault Statistics",
            description="High-level indexing statistics, document count, and database size.",
            mimeType="application/json",
        ),
        types.Resource(
            uri="neuro://vault/recent",
            name="Recently Indexed Documents",
            description="List of recently ingested and modified documents in the vault.",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    if uri == "neuro://vault/stats":
        res = await make_request("GET", "/api/health")
        return json.dumps(res, indent=2)
    if uri == "neuro://vault/recent":
        res = await make_request("GET", "/api/file/tree")
        return json.dumps(res, indent=2)
    raise ValueError(f"Unknown resource URI: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="analyze_document",
            description="Deep technical analysis and summarization of a vault document.",
            arguments=[
                types.PromptArgument(
                    name="filepath",
                    description="Target file path to analyze",
                    required=True,
                )
            ],
        ),
        types.Prompt(
            name="search_and_synthesize",
            description="Search across vault and synthesize a cohesive research brief.",
            arguments=[
                types.PromptArgument(
                    name="topic",
                    description="Research topic to search and synthesize",
                    required=True,
                )
            ],
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    arguments = arguments or {}
    if name == "analyze_document":
        fp = arguments.get("filepath", "")
        return types.GetPromptResult(
            description=f"Analyze document {fp}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please analyze the following document thoroughly: {fp}"
                    ),
                )
            ],
        )
    if name == "search_and_synthesize":
        topic = arguments.get("topic", "")
        return types.GetPromptResult(
            description=f"Search and synthesize research brief on {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please search the knowledge vault and synthesize a comprehensive research brief on: {topic}"
                    ),
                )
            ],
        )
    raise ValueError(f"Unknown prompt: {name}")

async def main():
    if not HAS_MCP:
        sys.stderr.write("MCP library (mcp) is not installed on this system.\n")
        return
    capabilities = server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={},
    )
    init_options = InitializationOptions(
        server_name="neuro-mcp",
        server_version="1.0.0",
        capabilities=capabilities,
    )
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)

if __name__ == "__main__":
    asyncio.run(main())
