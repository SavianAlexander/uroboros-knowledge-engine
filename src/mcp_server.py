import os
import json
import asyncio
import httpx
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
        "sfx_name": {"type": "string", "description": "Procedural SFX name (warp_spool, shield_critical, armor_bleed, hull_breach, target_lock, cockpit_ambient)", "default": "target_lock"}
    },
    "required": ["sfx_name"],
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
            description="Play procedural tactical cockpit sound effect (warp spool, shield siren, target lock).",
            inputSchema=SFX_SCHEMA,
        ),
    ]

async def _mcp_tool_search(args: dict) -> list[types.TextContent]:
    res = await make_request("POST", "/api/search", json={
        "query": args.get("query"),
        "limit": args.get("limit", 5),
        "search_type": args.get("search_type", "hybrid")
    })
    text_out = f"Search Results for '{args.get('query')}':\n\n"
    for doc in res.get("results", []):
        text_out += f"- [{doc.get('score', 0):.2f}] {doc.get('content', '')[:300]}...\n"
    return [types.TextContent(type="text", text=text_out)]


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
    from .agents.skills.neuro_copilot.scripts.neuro_bridge import compress_ast
    res = compress_ast(args.get("path"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_self_patch(args: dict) -> list[types.TextContent]:
    from .agents.skills.neuro_copilot.scripts.github_bridge import self_patch
    res = self_patch(args.get("error"), args.get("file"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_call_graph(args: dict) -> list[types.TextContent]:
    from .agents.skills.neuro_copilot.scripts.github_bridge import call_graph
    res = call_graph(args.get("target", "know.py"))
    return [types.TextContent(type="text", text=res)]


async def _mcp_tool_release_certificate(args: dict) -> list[types.TextContent]:
    from .agents.skills.neuro_copilot.scripts.github_bridge import generate_certificate
    res = generate_certificate()
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


_MCP_TOOL_HANDLERS = {
    "neuro_search": _mcp_tool_search,
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
        print("MCP library (mcp) is not installed on this system.")
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
